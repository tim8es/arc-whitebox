from __future__ import annotations

import gc
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from methods.e093_v29_adapter import DEPTH, EXPECTED_BLOB, WIDTH, git_blob_sha1, load_exact_v29

BUDGET = 2**41
SEED = 93093
E051_FLOPS = 587262754287
TARGET_UTIL = 0.135
TARGET_FLOPS = TARGET_UTIL * BUDGET
DEPTH_BELOW_32 = 5


def synthetic_mlp():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = np.sqrt(2.0 / WIDTH)
    weights = [
        fnp.asarray(rng.normal(0.0, scale, size=(WIDTH, WIDTH)).astype(np.float32), dtype=fnp.float32)
        for _ in range(DEPTH)
    ]
    return SimpleNamespace(width=WIDTH, depth=DEPTH, weights=weights)


def setup_estimator(estimator) -> None:
    estimator.setup(
        SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET, api_version="1", seed=SEED)
    )


def _matmul_estimate(a, b) -> tuple[int, tuple[int, int, int] | None]:
    ashape = tuple(int(x) for x in getattr(a, "shape", ()))
    bshape = tuple(int(x) for x in getattr(b, "shape", ()))
    if len(ashape) < 2 or len(bshape) < 2:
        return 0, None
    m, k = ashape[-2], ashape[-1]
    kb, n = bshape[-2], bshape[-1]
    if k != kb:
        return 0, None
    try:
        batch_shape = np.broadcast_shapes(ashape[:-2], bshape[:-2])
    except ValueError:
        return 0, None
    batch = math.prod(batch_shape) if batch_shape else 1
    # Conventional multiply+accumulate count; intentionally independent of flopscope internals.
    est = int(batch * m * n * max(1, 2 * k - 1))
    return est, (m, k, n)


class MatmulProfiler:
    def __init__(self) -> None:
        self.original = fnp.matmul
        self.calls = 0
        self.estimated_flops = 0
        self.square32_flops = 0
        self.small_le32_flops = 0
        self.square32_calls = 0

    def wrapped(self, a, b, *args, **kwargs):
        est, dims = _matmul_estimate(a, b)
        self.calls += 1
        self.estimated_flops += est
        if dims is not None:
            m, k, n = dims
            if max(m, k, n) <= 32:
                self.small_le32_flops += est
            if (m, k, n) == (32, 32, 32):
                self.square32_flops += est
                self.square32_calls += 1
        return self.original(a, b, *args, **kwargs)

    def install(self) -> None:
        fnp.matmul = self.wrapped

    def restore(self) -> None:
        fnp.matmul = self.original


def run_predict(mod, mlp):
    estimator = mod.Estimator()
    setup_estimator(estimator)
    profiler = MatmulProfiler()
    profiler.install()
    started = time.perf_counter()
    try:
        with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
            prediction = estimator.predict(mlp, BUDGET)
    finally:
        profiler.restore()
    wall_s = time.perf_counter() - started
    estimator.teardown()
    result = {
        "prediction": prediction,
        "predict_flops": int(ctx.flops_used),
        "residual_s": float(ctx.residual_wall_time_s),
        "wall_s": float(wall_s),
        "matmul_calls": profiler.calls,
        "matmul_estimated_flops": profiler.estimated_flops,
        "square32_flops": profiler.square32_flops,
        "small_le32_flops": profiler.small_le32_flops,
        "square32_calls": profiler.square32_calls,
    }
    del estimator
    gc.collect()
    return result


def strassen_cost(n: int, depth: int) -> int:
    if depth == 0:
        return 2 * n**3
    half = n // 2
    return 7 * strassen_cost(half, depth - 1) + 18 * half**2


def main() -> None:
    out = {
        "experiment": "E093",
        "stage": "A",
        "seed": SEED,
        "width": WIDTH,
        "depth": DEPTH,
        "budget": BUDGET,
        "target_util": TARGET_UTIL,
        "target_flops": TARGET_FLOPS,
        "reference_e051_flops": E051_FLOPS,
        "protocol_go": False,
    }
    try:
        mod, source = load_exact_v29()
        source_blob = git_blob_sha1(source)
        out["source_blob"] = source_blob
        if source_blob != EXPECTED_BLOB:
            raise RuntimeError("source hash mismatch")

        mlp = synthetic_mlp()
        first = run_predict(mod, mlp)
        repeat = run_predict(mod, mlp)

        first_np = np.asarray(first.pop("prediction"))
        repeat_np = np.asarray(repeat.pop("prediction"))
        finite = bool(np.isfinite(first_np).all() and np.isfinite(repeat_np).all())
        det_max = float(np.max(np.abs(first_np - repeat_np)))
        deterministic = bool(det_max == 0.0)

        measured_flops = int(first["predict_flops"])
        square32 = int(first["square32_flops"])
        small32 = int(first["small_le32_flops"])
        reference_drift = abs(measured_flops - E051_FLOPS) / E051_FLOPS

        # Absolute fantasy lower bound: ignore *all* Strassen additions and apply only the
        # multiplication-count factor to identified square-32 dense work.
        zero_add_factor = (7.0 / 8.0) ** DEPTH_BELOW_32
        zero_add_total = measured_flops - square32 + square32 * zero_add_factor
        zero_add_util = zero_add_total / BUDGET

        costs = {str(d): strassen_cost(32, d) for d in range(DEPTH_BELOW_32 + 1)}
        dense32_cost = strassen_cost(32, 0)
        depth5_ratio_with_adds = costs[str(DEPTH_BELOW_32)] / dense32_cost
        best_depth = min(range(DEPTH_BELOW_32 + 1), key=lambda d: costs[str(d)])
        best_ratio = costs[str(best_depth)] / dense32_cost
        conservative_total = measured_flops - square32 + square32 * depth5_ratio_with_adds
        conservative_util = conservative_total / BUDGET
        best_depth_total = measured_flops - square32 + square32 * best_ratio
        best_depth_util = best_depth_total / BUDGET

        # Even stronger global impossibility bound: pretend 100% of V29 FLOPs were eligible
        # square-32 leaf work and pretend recursive Strassen additions were free.
        global_fantasy_util = measured_flops * zero_add_factor / BUDGET

        out.update(
            {
                "finite": finite,
                "deterministic": deterministic,
                "determinism_max_abs": det_max,
                "first": first,
                "repeat": repeat,
                "reference_flop_drift_fraction": reference_drift,
                "square32_fraction_of_predict": square32 / measured_flops if measured_flops else 0.0,
                "small_le32_fraction_of_predict": small32 / measured_flops if measured_flops else 0.0,
                "zero_add_factor_depth5": zero_add_factor,
                "zero_add_total_lower_bound_flops": zero_add_total,
                "zero_add_total_lower_bound_util": zero_add_util,
                "strassen32_cost_by_depth": costs,
                "depth5_ratio_with_adds": depth5_ratio_with_adds,
                "depth5_conservative_total_flops": conservative_total,
                "depth5_conservative_util": conservative_util,
                "best_recursive_depth_for_32_with_adds": best_depth,
                "best_recursive_ratio_for_32_with_adds": best_ratio,
                "best_recursive_total_flops": best_depth_total,
                "best_recursive_util": best_depth_util,
                "global_fantasy_zero_add_util": global_fantasy_util,
            }
        )

        gates = {
            "finite": finite,
            "deterministic": deterministic,
            "source_hash": source_blob == EXPECTED_BLOB,
            "reference_flops": reference_drift <= 0.005,
            "leaf32_present": square32 > 0,
            "optimistic_util": zero_add_util <= TARGET_UTIL,
        }
        out["gates"] = gates
        out["protocol_go"] = bool(all(gates.values()))
        out["terminal"] = "GO_STAGE_B" if out["protocol_go"] else "NO-GO/DROP"
    except Exception as exc:
        out["error_type"] = type(exc).__name__
        out["error"] = str(exc)
        out["terminal"] = "NO-GO/DROP"

    print("E093_STAGE_A_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    Path("e093-stage-a.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    if not out.get("protocol_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
