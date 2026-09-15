from __future__ import annotations

import json
import time

import flopscope as flops
import numpy as np
import whestbench
from whestbench import SetupContext

from methods.e047_connected_diagram_dp import DTYPE, Estimator, KMAX, PROBE_COUNT

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 1.89e-8
ADJUSTED_GATE = 2.5e-9
FINAL_UTIL_GATE = 0.125
CORE_UTIL_GATE = 0.100
RESIDUAL_GATE_S = 0.400


def _emit(result: dict[str, object]) -> None:
    print("E047_DIAGNOSTIC_JSON=" + json.dumps(result, sort_keys=True))


def _setup(estimator: Estimator, width: int, depth: int) -> None:
    estimator.setup(
        SetupContext(
            width=width,
            depth=depth,
            flop_budget=BUDGET,
            api_version="1",
            seed=0,
        )
    )


def main() -> None:
    result: dict[str, object] = {
        "experiment": "E047",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "index": INDEX,
        "budget": BUDGET,
        "kmax": KMAX,
        "probe_count": PROBE_COUNT,
        "dtype": str(np.dtype(DTYPE)),
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
        if int(mlp.width) != 1024 or int(mlp.depth) != 16:
            raise RuntimeError(f"unexpected frozen mini0 architecture width={mlp.width} depth={mlp.depth}")
        if target.shape != (mlp.width,):
            raise RuntimeError(f"unexpected final target shape {target.shape}")

        estimator = Estimator()
        _setup(estimator, mlp.width, mlp.depth)
        started = time.perf_counter()
        with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
            prediction = estimator.predict(mlp, BUDGET)
        wall_s = time.perf_counter() - started
        estimator.teardown()

        prediction_np = np.asarray(prediction, dtype=np.float64)
        if prediction_np.shape != (mlp.depth, mlp.width):
            raise RuntimeError(f"unexpected prediction shape {prediction_np.shape}")
        finite = bool(np.isfinite(prediction_np).all())
        delta = prediction_np[-1] - target
        raw_mse = float(np.mean(delta * delta))
        flops_used = int(budget.flops_used)
        utilization = float(flops_used / BUDGET)
        core_projected_utilization = utilization
        adjusted = float(raw_mse * max(0.1, utilization))
        residual_s = float(budget.residual_wall_time_s)
        state_rank_max = int(max(max(ranks) for ranks in estimator._e047_state_ranks))
        representation_ok = bool(
            state_rank_max <= 2
            and estimator._e047_order_counts == [KMAX - 2] * mlp.depth
            and estimator._e047_probe_counts == [PROBE_COUNT] * mlp.depth
        )

        repeat_estimator = Estimator()
        _setup(repeat_estimator, mlp.width, mlp.depth)
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
                "core_projected_utilization": core_projected_utilization,
                "adjusted_proxy": adjusted,
                "wall_s": wall_s,
                "residual_s": residual_s,
                "backend_s": float(budget.flopscope_backend_time_s),
                "overhead_s": float(budget.flopscope_overhead_time_s),
                "state_rank_max": state_rank_max,
                "representation_ok": representation_ok,
                "max_abs_connected": float(estimator._e047_max_abs_connected),
                "determinism_max_abs_diff": deterministic_diff,
                "deterministic": deterministic,
                "raw_gate": raw_mse <= RAW_GATE,
                "adjusted_gate": adjusted < ADJUSTED_GATE,
                "final_util_gate": utilization <= FINAL_UTIL_GATE,
                "core_util_gate": core_projected_utilization <= CORE_UTIL_GATE,
                "residual_gate": residual_s < RESIDUAL_GATE_S,
            }
        )
        result["local_go"] = bool(
            finite
            and representation_ok
            and deterministic
            and result["raw_gate"]
            and result["adjusted_gate"]
            and result["final_util_gate"]
            and result["core_util_gate"]
            and result["residual_gate"]
            and result["failures"] == 0
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    _emit(result)


if __name__ == "__main__":
    main()
