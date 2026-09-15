from __future__ import annotations

import json
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq
from whestbench.domain import MLP

from methods.e040_late_source_exact_window import (
    PINNED_BLOB_SHA,
    PROJECTED_UTILIZATION,
    birth_schedule,
    load_patched_module,
    source_layer_pairs,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.5e-9
RESIDUAL_CAP = 0.400


class _Ctx:
    seed = 0


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _make_mlp(row: dict) -> tuple[MLP, np.ndarray]:
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(16, 1024, 1024)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(1024)
    return MLP(width=1024, depth=16, weights=[fnp.asarray(w) for w in weights], seed=0), gt


def _run(module, row: dict, *, metered: bool) -> dict:
    mlp, gt = _make_mlp(row)
    est = module.Estimator()
    est.setup(_Ctx())
    t0 = time.perf_counter()
    if metered:
        with flops.BudgetContext(
            flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
        ) as ctx:
            pred = est.predict(mlp, BUDGET)
            used = float(ctx.flops_used)
        residual = float(ctx.residual_wall_time_s)
    else:
        pred = est.predict(mlp, BUDGET)
        used = float("nan")
        residual = float("nan")
    wall = time.perf_counter() - t0
    arr = np.asarray(pred, dtype=np.float64)
    return {
        "pred": arr,
        "mse": float(np.mean((arr[-1] - gt) ** 2)),
        "flops": used,
        "residual_s": residual,
        "wall_s": wall,
        "finite": bool(np.isfinite(arr).all()),
    }


def main() -> None:
    module, provenance = load_patched_module()
    births, insertions = birth_schedule(16)
    pairs = source_layer_pairs(16)
    row = _load_row0()
    candidate = _run(module, row, metered=True)
    repeat = _run(module, row, metered=False)

    util = candidate["flops"] / BUDGET
    adjusted = candidate["mse"] * max(0.1, util)
    det_max_abs = float(np.max(np.abs(candidate["pred"] - repeat["pred"])))
    scope_ok = (
        provenance["blob_sha"] == PINNED_BLOB_SHA
        and provenance["patch_target_count"] == 1
        and provenance["no_confine_frozen"] is True
        and births == tuple(range(7, 15))
        and insertions == tuple(range(8, 16))
        and pairs == 36
    )
    gates = {
        "raw_mse_le_1.89e-08": candidate["mse"] <= RAW_GATE,
        "utilization_le_0.14": util <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": candidate["residual_s"] < RESIDUAL_CAP,
        "finite": candidate["finite"] and repeat["finite"],
        "deterministic": det_max_abs == 0.0,
        "pinned_blob": provenance["blob_sha"] == PINNED_BLOB_SHA,
        "patch_target_count_eq_1": provenance["patch_target_count"] == 1,
        "no_confine_frozen": provenance["no_confine_frozen"] is True,
        "birth_schedule": births == tuple(range(7, 15)) and insertions == tuple(range(8, 16)),
        "source_pairs_eq_36": pairs == 36,
        "scope": scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "public_mini_index": 0,
        "final_mse": candidate["mse"],
        "flops": candidate["flops"],
        "utilization": util,
        "adjusted_proxy": adjusted,
        "residual_s": candidate["residual_s"],
        "wall_s": candidate["wall_s"],
        "deterministic_repeat_max_abs": det_max_abs,
        "finite": candidate["finite"] and repeat["finite"],
        "failures": 0,
        "pinned_blob": provenance["blob_sha"],
        "patch_target_count": provenance["patch_target_count"],
        "no_confine_frozen": provenance["no_confine_frozen"],
        "birth_layers": list(births),
        "insertion_layers": list(insertions),
        "source_layer_pairs": pairs,
        "projected_utilization_pre_science": PROJECTED_UTILIZATION,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E040_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e040_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
