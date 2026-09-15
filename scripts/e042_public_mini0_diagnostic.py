from __future__ import annotations

import json
import time
import types

import flopscope as flops
import numpy as np
import whestbench
from whestbench import SetupContext

from methods.e042_source_column_cubature import (
    PINNED_BLOB_SHA,
    Q_SUITE,
    fetch_and_patch_pinned_source,
    quadrature_weight,
    source_nodes,
)

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.5e-9


def _emit(result: dict[str, object]) -> None:
    print("E042_DIAGNOSTIC_JSON=" + json.dumps(result, sort_keys=True))


def main() -> None:
    result: dict[str, object] = {
        "experiment": "E042",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "index": INDEX,
        "budget": BUDGET,
        "q": Q_SUITE,
        "failures": 1,
        "local_go": False,
    }

    try:
        patched, provenance = fetch_and_patch_pinned_source()
        result["pinned_blob"] = provenance["blob_sha"]
        result["pinned_blob_ok"] = provenance["blob_sha"] == PINNED_BLOB_SHA
        result["patch_counts"] = provenance["patch_counts"]
        counts = provenance["patch_counts"]
        result["patch_counts_ok"] = (
            counts.get("carrier_pools") == 2
            and all(v == 1 for k, v in counts.items() if k != "carrier_pools")
        )

        module = types.ModuleType("e042_patched_v25_public_mini0")
        exec(compile(patched, "<e042_patched_v25_public_mini0>", "exec"), module.__dict__)

        dataset = whestbench.load_dataset(
            DATASET,
            revision=REVISION,
            split=SPLIT,
        )
        row = dataset[INDEX]
        mlp = whestbench.mlp_at(dataset, INDEX)
        target = np.asarray(row["final_means"], dtype=np.float64)

        result["width"] = int(mlp.width)
        result["depth"] = int(mlp.depth)
        if int(mlp.width) != 1024 or int(mlp.depth) != 16:
            raise RuntimeError(
                f"unexpected frozen mini0 architecture width={mlp.width} depth={mlp.depth}"
            )
        if target.shape != (mlp.width,):
            raise RuntimeError(f"unexpected final target shape {target.shape}")

        birth_cards = [len(source_nodes(mlp.width, b)) for b in range(mlp.depth)]
        birth_unique = [len(np.unique(source_nodes(mlp.width, b))) for b in range(mlp.depth)]
        result["birth_cardinality_min"] = min(birth_cards)
        result["birth_cardinality_max"] = max(birth_cards)
        result["birth_unique_min"] = min(birth_unique)
        result["birth_unique_max"] = max(birth_unique)
        result["omega"] = quadrature_weight(mlp.width)
        result["nodes_ok"] = (
            min(birth_cards) == Q_SUITE
            and max(birth_cards) == Q_SUITE
            and min(birth_unique) == Q_SUITE
            and max(birth_unique) == Q_SUITE
        )

        estimator = module.Estimator()
        estimator.setup(
            SetupContext(
                width=mlp.width,
                depth=mlp.depth,
                flop_budget=BUDGET,
                api_version="1",
                seed=0,
            )
        )

        started = time.perf_counter()
        with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
            prediction = estimator.predict(mlp, BUDGET)
        wall_s = time.perf_counter() - started
        estimator.teardown()

        prediction_np = np.asarray(prediction, dtype=np.float64)
        finite = bool(np.isfinite(prediction_np).all())
        if prediction_np.shape != (mlp.depth, mlp.width):
            raise RuntimeError(f"unexpected prediction shape {prediction_np.shape}")

        delta = prediction_np[-1] - target
        raw_mse = float(np.mean(delta * delta))
        flops_used = int(budget.flops_used)
        utilization = float(flops_used / BUDGET)
        adjusted = float(raw_mse * max(0.1, utilization))

        result.update(
            {
                "failures": 0,
                "finite": finite,
                "raw_final_mse": raw_mse,
                "flops_used": flops_used,
                "utilization": utilization,
                "adjusted_proxy": adjusted,
                "wall_s": wall_s,
                "raw_gate": raw_mse <= RAW_GATE,
                "util_gate": utilization <= UTIL_GATE,
                "adjusted_gate": adjusted < ADJUSTED_GATE,
            }
        )
        result["local_go"] = bool(
            finite
            and result["pinned_blob_ok"]
            and result["patch_counts_ok"]
            and result["nodes_ok"]
            and result["raw_gate"]
            and result["util_gate"]
            and result["adjusted_gate"]
            and result["failures"] == 0
        )
    except Exception as exc:  # One-shot scientific diagnostic: record failure, never retry.
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    _emit(result)


if __name__ == "__main__":
    main()
