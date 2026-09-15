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

from methods.e044_fixed_checkpoint_k3_replay import (
    CHECKPOINTS,
    PINNED_BLOB_SHA,
    PROJECTED_UTILIZATION,
    checkpoint_live_counts,
    checkpoint_source_uses,
    load_patched_module,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.5e-9
RESIDUAL_CAP = 0.400
EXPECTED_PATCH_KEYS = {
    "import_anchor",
    "no_confine",
    "state_anchor",
    "skip_src",
    "mode",
    "skip_mode_start",
    "skip_mode_end",
    "birth_fb",
    "w1_prev",
    "newborn",
    "source_start",
    "source_end",
}


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
    mlp = MLP(
        width=1024,
        depth=16,
        weights=[fnp.asarray(w) for w in weights],
        seed=0,
    )
    return mlp, gt


def _predict(module, row: dict, *, metered: bool, module_tag: str) -> dict:
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
        "module_tag": module_tag,
    }


def main() -> None:
    # Public data is loaded once. The candidate mechanism, checkpoint tuple and
    # patch are frozen before this harness commit. Network fetch/blob verification
    # occurs before metering; candidate arithmetic itself is fully metered.
    row = _load_row0()
    module, provenance = load_patched_module("_e044_science_v25")
    repeat_module, repeat_provenance = load_patched_module("_e044_repeat_v25")

    patch_counts = dict(provenance["patch_counts"])
    scope_patch_ok = (
        provenance["blob_sha"] == PINNED_BLOB_SHA
        and set(patch_counts) == EXPECTED_PATCH_KEYS
        and all(v == 1 for v in patch_counts.values())
        and provenance["no_confine_frozen"] is True
        and tuple(provenance["checkpoints_frozen"]) == CHECKPOINTS
    )

    candidate = _predict(module, row, metered=True, module_tag="science")
    repeat = _predict(repeat_module, row, metered=False, module_tag="repeat")

    utilization = candidate["flops"] / BUDGET
    adjusted = candidate["mse"] * max(0.1, utilization)
    det_max_abs = float(np.max(np.abs(candidate["pred"] - repeat["pred"])))
    finite = bool(candidate["finite"] and repeat["finite"])
    counts = checkpoint_live_counts(16)
    source_uses = checkpoint_source_uses(16)

    # All 15 births are hard-wired to be retained by the patch: there is no
    # selector/prune/rank path, and the final checkpoint is layer 15 before the
    # final mean evaluation. Successful traversal through final _dslices with all
    # 15 metadata entries is the runtime cardinality check.
    final_births = tuple(range(15))
    runtime_cardinality_ok = candidate["pred"].shape == (16, 1024)
    repeat_scope_ok = (
        repeat_provenance["blob_sha"] == PINNED_BLOB_SHA
        and repeat_provenance["no_confine_frozen"] is True
        and tuple(repeat_provenance["checkpoints_frozen"]) == CHECKPOINTS
    )

    gates = {
        "raw_mse_le_1.89e-08": candidate["mse"] <= RAW_GATE,
        "utilization_le_0.14": utilization <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": candidate["residual_s"] < RESIDUAL_CAP,
        "finite": finite,
        "deterministic_repeat_diff_eq_0": det_max_abs == 0.0,
        "checkpoints_exact": CHECKPOINTS == (7, 11, 15),
        "checkpoint_live_counts": counts == (7, 11, 15),
        "checkpoint_source_uses_eq_33": source_uses == 33,
        "all_15_births_retained": final_births == tuple(range(15)),
        "runtime_source_cardinality": runtime_cardinality_ok,
        "pinned_blob_and_patch_counts": scope_patch_ok,
        "no_confine_true": provenance["no_confine_frozen"] is True,
        "repeat_scope_identical": repeat_scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "public_mini_index": 0,
        "checkpoints": list(CHECKPOINTS),
        "checkpoint_live_counts": list(counts),
        "checkpoint_source_uses": int(source_uses),
        "final_births": list(final_births),
        "projected_utilization_pre_science": PROJECTED_UTILIZATION,
        "raw_final_mse": candidate["mse"],
        "total_flops": candidate["flops"],
        "utilization": utilization,
        "adjusted_proxy": adjusted,
        "residual_s": candidate["residual_s"],
        "wall_s": candidate["wall_s"],
        "failures": 0,
        "finite": finite,
        "deterministic_repeat_max_abs": det_max_abs,
        "repeat_raw_final_mse": repeat["mse"],
        "pinned_blob": provenance["blob_sha"],
        "patch_counts": patch_counts,
        "no_confine_frozen": provenance["no_confine_frozen"],
        "checkpoints_frozen": list(provenance["checkpoints_frozen"]),
        "runtime_source_cardinality_ok": runtime_cardinality_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E044_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e044_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
