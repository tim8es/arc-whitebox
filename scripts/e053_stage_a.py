from __future__ import annotations

import gc
import json
import time
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from methods.e053_v29_adapter import (
    AGE_OLD2,
    DEPTH,
    EXPECTED_BLOB,
    R_OLD2,
    WIDTH,
    git_blob_sha1,
    load_e053,
    load_v29,
)

BUDGET = 2**41
SEED = 53053
UTIL_GATE = 0.2670561845802695
DELTA_GATE = 0.02
DET_GATE = 1e-12


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


def run_predict(mod, mlp):
    estimator = mod.Estimator()
    setup_estimator(estimator)
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        prediction = estimator.predict(mlp, BUDGET)
    wall_s = time.perf_counter() - started
    estimator.teardown()
    flops_used = int(ctx.flops_used)
    residual_s = float(ctx.residual_wall_time_s)
    del estimator
    gc.collect()
    return prediction, flops_used, residual_s, wall_s


def comparison_metrics(base_pred, cand_pred, repeat_pred):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        base = fnp.asarray(base_pred)
        cand = fnp.asarray(cand_pred)
        repeat = fnp.asarray(repeat_pred)
        diff = cand - base
        repeat_diff = cand - repeat
        max_abs_delta = fnp.max(fnp.abs(diff))
        det_max = fnp.max(fnp.abs(repeat_diff))
        all_num = fnp.sqrt(fnp.mean(diff * diff))
        all_den = fnp.sqrt(fnp.mean(base * base))
        final_diff = cand[-1] - base[-1]
        final_num = fnp.sqrt(fnp.mean(final_diff * final_diff))
        final_den = fnp.sqrt(fnp.mean(base[-1] * base[-1]))
    all_rel = float(all_num) / max(float(all_den), 1e-30)
    final_rel = float(final_num) / max(float(final_den), 1e-30)
    return {
        "comparison_flops": int(ctx.flops_used),
        "max_abs_delta": float(max_abs_delta),
        "determinism_max_abs_diff": float(det_max),
        "all_layer_rel_rms_delta": all_rel,
        "final_layer_rel_rms_delta": final_rel,
    }


def main() -> None:
    result = {
        "experiment": "E053",
        "width": WIDTH,
        "depth": DEPTH,
        "seed": SEED,
        "budget": BUDGET,
        "upstream_blob": EXPECTED_BLOB,
        "age_old2": AGE_OLD2,
        "r_old2": R_OLD2,
        "stage_a_go": False,
    }
    try:
        base_mod, base_bytes = load_v29()
        cand_mod, cand_bytes = load_e053()
        result["baseline_blob"] = git_blob_sha1(base_bytes)
        result["candidate_source_blob"] = git_blob_sha1(cand_bytes)
        if result["baseline_blob"] != EXPECTED_BLOB or result["candidate_source_blob"] != EXPECTED_BLOB:
            raise RuntimeError("source hash mismatch")
        if (base_mod.Estimator.AGE_OLD2, base_mod.Estimator.R_OLD2) != (7, 224):
            raise RuntimeError("baseline constants changed")
        if (cand_mod.Estimator.AGE_OLD2, cand_mod.Estimator.R_OLD2) != (6, 256):
            raise RuntimeError("candidate constants changed")

        mlp = synthetic_mlp()
        base_pred, base_flops, base_residual, base_wall = run_predict(base_mod, mlp)
        cand_pred, cand_flops, cand_residual, cand_wall = run_predict(cand_mod, mlp)
        repeat_pred, repeat_flops, repeat_residual, repeat_wall = run_predict(cand_mod, mlp)

        base_np = np.asarray(base_pred)
        cand_np = np.asarray(cand_pred)
        repeat_np = np.asarray(repeat_pred)
        base_finite = bool(np.isfinite(base_np).all())
        cand_finite = bool(np.isfinite(cand_np).all())
        repeat_finite = bool(np.isfinite(repeat_np).all())
        metrics = comparison_metrics(base_pred, cand_pred, repeat_pred)
        all_in_flops = int(cand_flops + metrics["comparison_flops"])
        utilization = float(all_in_flops / BUDGET)

        finite_gate = bool(base_finite and cand_finite and repeat_finite)
        determinism_gate = bool(metrics["determinism_max_abs_diff"] <= DET_GATE)
        util_gate = bool(utilization <= UTIL_GATE)
        cost_gate = bool(cand_flops < base_flops)
        active_gate = bool(metrics["max_abs_delta"] > 0.0)
        bounded_gate = bool(
            metrics["all_layer_rel_rms_delta"] <= DELTA_GATE
            and metrics["final_layer_rel_rms_delta"] <= DELTA_GATE
        )
        result.update(
            {
                "baseline_finite": base_finite,
                "candidate_finite": cand_finite,
                "repeat_finite": repeat_finite,
                "baseline_predict_flops": base_flops,
                "candidate_predict_flops": cand_flops,
                "repeat_predict_flops": repeat_flops,
                "baseline_residual_s": base_residual,
                "candidate_residual_s": cand_residual,
                "repeat_residual_s": repeat_residual,
                "baseline_wall_s": base_wall,
                "candidate_wall_s": cand_wall,
                "repeat_wall_s": repeat_wall,
                "all_in_flops": all_in_flops,
                "utilization": utilization,
                **metrics,
                "finite_gate": finite_gate,
                "determinism_gate": determinism_gate,
                "util_gate": util_gate,
                "cost_gate": cost_gate,
                "active_gate": active_gate,
                "bounded_delta_gate": bounded_gate,
            }
        )
        result["stage_a_go"] = bool(
            finite_gate and determinism_gate and util_gate and cost_gate and active_gate and bounded_gate
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    print("E053_STAGE_A_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    Path("e053-stage-a.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if not result.get("stage_a_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
