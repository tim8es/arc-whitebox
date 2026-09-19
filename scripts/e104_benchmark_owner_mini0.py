from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
POSITIVE_DIRECTIONS = TRAJECTORIES // 2
DIRECTION_SEED = 104105
BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 1.89e-8
UTIL_GATE = 0.135
OUT = Path("e104-benchmark-owner-mini0.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def build_inputs_billed():
    rng = fnp.random.default_rng(DIRECTION_SEED)
    blocks = []
    if POSITIVE_DIRECTIONS % WIDTH:
        raise RuntimeError("positive direction count must be divisible by width")
    mu_r = mean_chi_radius(WIDTH)
    for _ in range(POSITIVE_DIRECTIONS // WIDTH):
        g = rng.standard_normal((WIDTH, WIDTH))
        q, r = fnp.linalg.qr(g)
        diag = fnp.diag(r)
        signs = fnp.where(diag < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        blocks.append(fnp.multiply(q, mu_r).astype(fnp.float32))
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def run_predict(mlp):
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        h = build_inputs_billed()
        input_np = np.asarray(h, dtype=np.float32).copy()
        rows = []
        for w in mlp.weights:
            h = fnp.matmul(h, w)
            h = fnp.maximum(h, fnp.float32(0.0))
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
        prediction = fnp.stack(rows, axis=0)
        predict_flops = int(ctx.flops_used)
        residual_s = float(ctx.residual_wall_time_s)
    wall_s = time.perf_counter() - started

    pred = np.asarray(prediction, dtype=np.float64).copy()
    half = TRAJECTORIES // 2
    pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))
    return pred, predict_flops, residual_s, wall_s, pair_max_abs


def metric_flops_and_mse(prediction: np.ndarray, target: np.ndarray) -> tuple[float, int]:
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        p = fnp.asarray(prediction)
        t = fnp.asarray(target)
        delta = p[-1] - t
        raw = fnp.mean(delta * delta)
    return float(raw), int(ctx.flops_used)


def main() -> None:
    result = {
        "schema": "arc.whitebox.e104.benchmark_owner_mini0.v1",
        "experiment": "E104",
        "idempotency_key": "ARC-E104-BENCHMARK-OWNER-MINI0-20260919",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "index": INDEX,
        "budget": BUDGET,
        "direction_seed": DIRECTION_SEED,
        "trajectories": TRAJECTORIES,
        "failures": 1,
        "benchmark_go": False,
    }
    try:
        dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
        row = dataset[INDEX]
        mlp = whestbench.mlp_at(dataset, INDEX)
        target = np.asarray(row["final_means"], dtype=np.float64)

        result["width"] = int(mlp.width)
        result["depth"] = int(mlp.depth)
        result["target_shape"] = list(target.shape)
        if int(mlp.width) != WIDTH or int(mlp.depth) != DEPTH:
            raise RuntimeError(
                f"unexpected mini0 shape width={mlp.width} depth={mlp.depth}"
            )
        if target.shape != (WIDTH,):
            raise RuntimeError(f"unexpected final target shape {target.shape}")

        prediction, predict_flops, residual_s, wall_s, pair_max_abs = run_predict(mlp)
        finite = bool(np.isfinite(prediction).all())
        raw_mse, metric_flops = metric_flops_and_mse(prediction, target)
        all_in_flops = int(predict_flops + metric_flops)
        utilization = float(all_in_flops / BUDGET)
        prediction_sha256 = hashlib.sha256(prediction.tobytes()).hexdigest()

        gates = {
            "shape_16x1024": list(prediction.shape) == [DEPTH, WIDTH],
            "finite": finite,
            "antithetic_pair_exact": pair_max_abs == 0.0,
            "failures_eq_0": True,
            "raw_final_mse_le_1_89e_8": raw_mse <= RAW_GATE,
            "utilization_le_0_135": utilization <= UTIL_GATE,
        }
        result.update(
            {
                "failures": 0,
                "finite": finite,
                "prediction_shape": list(prediction.shape),
                "prediction_sha256": prediction_sha256,
                "antithetic_input_pair_max_abs": pair_max_abs,
                "raw_final_mse": raw_mse,
                "predict_flops": predict_flops,
                "metric_flops": metric_flops,
                "all_in_flops": all_in_flops,
                "utilization": utilization,
                "residual_s": residual_s,
                "wall_s": wall_s,
                "gates": gates,
                "benchmark_go": bool(all(gates.values())),
                "scope": {
                    "direct_metric_only": True,
                    "official_scorer": False,
                    "holdout": False,
                    "full_suite": False,
                    "tuning": False,
                    "rerun": False,
                },
            }
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_BENCHMARK_OWNER_MINI0=" + json.dumps(result, sort_keys=True), flush=True)
    if not result.get("benchmark_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
