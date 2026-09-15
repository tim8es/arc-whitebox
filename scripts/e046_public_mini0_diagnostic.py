from __future__ import annotations

import json
import time

import flopscope as flops
import numpy as np
import whestbench
from whestbench import SetupContext

from methods.e046_harmonic_defect_control import (
    DEPTH_EXPECTED,
    GH_ORDER,
    HARMONIC_DEGREE,
    HARMONIC_RANK,
    WIDTH_EXPECTED,
    Estimator,
)

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 1.89e-8
UTIL_GATE = 0.125
ADJUSTED_GATE = 2.5e-9
RESIDUAL_GATE_S = 0.4


def _emit(result: dict[str, object]) -> None:
    print("E046_DIAGNOSTIC_JSON=" + json.dumps(result, sort_keys=True))


def _setup(estimator: Estimator) -> None:
    estimator.setup(
        SetupContext(
            width=WIDTH_EXPECTED,
            depth=DEPTH_EXPECTED,
            flop_budget=BUDGET,
            api_version="1",
            seed=0,
        )
    )


def main() -> None:
    result: dict[str, object] = {
        "experiment": "E046",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "index": INDEX,
        "budget": BUDGET,
        "harmonic_rank": HARMONIC_RANK,
        "harmonic_degree": HARMONIC_DEGREE,
        "gh_order": GH_ORDER,
        "failures": 1,
        "local_go": False,
    }
    try:
        dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
        row = dataset[INDEX]
        mlp = whestbench.mlp_at(dataset, INDEX)
        target = np.asarray(row["final_means"], dtype=np.float64)
        result["width"] = int(mlp.width)
        result["depth"] = int(mlp.depth)
        if int(mlp.width) != WIDTH_EXPECTED or int(mlp.depth) != DEPTH_EXPECTED:
            raise RuntimeError(
                f"unexpected frozen mini0 architecture width={mlp.width} depth={mlp.depth}"
            )
        if target.shape != (WIDTH_EXPECTED,):
            raise RuntimeError(f"unexpected final target shape {target.shape}")

        estimator = Estimator()
        _setup(estimator)
        started = time.perf_counter()
        with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
            prediction = estimator.predict(mlp, BUDGET)
        wall_s = time.perf_counter() - started
        estimator.teardown()

        prediction_np = np.asarray(prediction, dtype=np.float64)
        if prediction_np.shape != (DEPTH_EXPECTED, WIDTH_EXPECTED):
            raise RuntimeError(f"unexpected prediction shape {prediction_np.shape}")
        finite = bool(np.isfinite(prediction_np).all())
        delta = prediction_np[-1] - target
        raw_mse = float(np.mean(delta * delta))
        flops_used = int(budget.flops_used)
        utilization = float(flops_used / BUDGET)
        adjusted = float(raw_mse * max(0.1, utilization))
        residual_s = float(budget.residual_wall_time_s)

        counts_ok = bool(
            estimator._e046_rank_counts == [HARMONIC_RANK] * (DEPTH_EXPECTED - 1)
            and estimator._e046_degree_counts == [HARMONIC_DEGREE] * (DEPTH_EXPECTED - 1)
            and estimator._e046_gh_orders == [GH_ORDER] * (DEPTH_EXPECTED - 1)
        )

        repeat_estimator = Estimator()
        _setup(repeat_estimator)
        with flops.BudgetContext(flop_budget=BUDGET, quiet=True):
            repeat_prediction = repeat_estimator.predict(mlp, BUDGET)
        repeat_estimator.teardown()
        repeat_np = np.asarray(repeat_prediction, dtype=np.float64)
        deterministic_diff = float(np.max(np.abs(repeat_np - prediction_np)))
        deterministic = bool(deterministic_diff == 0.0)

        result.update(
            {
                "failures": 0,
                "finite": finite,
                "raw_final_mse": raw_mse,
                "flops_used": flops_used,
                "utilization": utilization,
                "adjusted_proxy": adjusted,
                "wall_s": wall_s,
                "residual_s": residual_s,
                "backend_s": float(budget.flopscope_backend_time_s),
                "overhead_s": float(budget.flopscope_overhead_time_s),
                "max_abs_defect": float(estimator._e046_max_abs_defect),
                "rank_counts": list(estimator._e046_rank_counts),
                "degree_counts": list(estimator._e046_degree_counts),
                "gh_orders": list(estimator._e046_gh_orders),
                "counts_ok": counts_ok,
                "determinism_max_abs_diff": deterministic_diff,
                "deterministic": deterministic,
                "raw_gate": raw_mse <= RAW_GATE,
                "util_gate": utilization <= UTIL_GATE,
                "adjusted_gate": adjusted < ADJUSTED_GATE,
                "residual_gate": residual_s < RESIDUAL_GATE_S,
            }
        )
        result["local_go"] = bool(
            finite
            and counts_ok
            and deterministic
            and result["raw_gate"]
            and result["util_gate"]
            and result["adjusted_gate"]
            and result["residual_gate"]
            and result["failures"] == 0
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    _emit(result)


if __name__ == "__main__":
    main()
