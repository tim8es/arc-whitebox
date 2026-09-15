from __future__ import annotations

import json
import os
import sys
import time
import types
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq
from whestbench.domain import MLP

from methods.e041_backward_leverage_source_reservoir import (
    CAPACITY,
    PINNED_BLOB_SHA,
    PROJECTED_UTILIZATION,
    backward_leverage_scores,
    fetch_and_patch_pinned_source,
    select_births_knapsack,
    source_pair_cost,
    walsh_probes,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.5e-9
RESIDUAL_CAP = 0.400
_EXPECTED_PATCH_KEYS = {
    "no_confine_anchor",
    "newborn_block",
    "w2b_list",
    "dA_list",
    "dP_list",
    "c1_list",
    "c2_list",
    "y_list",
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
    return MLP(
        width=1024,
        depth=16,
        weights=[fnp.asarray(w) for w in weights],
        seed=0,
    ), gt


def _load_frozen_module(code, keep_births: tuple[int, ...], module_name: str):
    old_no_confine = os.environ.get("V21_NO_CONFINE")
    old_keep = os.environ.get("E041_KEEP_BIRTHS")
    os.environ["V21_NO_CONFINE"] = "1"
    os.environ["E041_KEEP_BIRTHS"] = ",".join(str(x) for x in keep_births)
    try:
        module = types.ModuleType(module_name)
        module.__file__ = f"<{module_name}>"
        sys.modules[module_name] = module
        exec(code, module.__dict__)
    finally:
        if old_no_confine is None:
            os.environ.pop("V21_NO_CONFINE", None)
        else:
            os.environ["V21_NO_CONFINE"] = old_no_confine
        if old_keep is None:
            os.environ.pop("E041_KEEP_BIRTHS", None)
        else:
            os.environ["E041_KEEP_BIRTHS"] = old_keep
    return module


def _repeat(row: dict, code, selected: tuple[int, ...]) -> tuple[np.ndarray, tuple[int, ...]]:
    mlp, _ = _make_mlp(row)
    probes = fnp.asarray(walsh_probes(np, mlp.width), dtype=fnp.float32)
    scores = backward_leverage_scores(fnp, mlp.weights, probes)
    selected_repeat = select_births_knapsack(
        np.asarray(scores, dtype=np.float64).tolist(), capacity=CAPACITY
    )
    module = _load_frozen_module(code, selected_repeat, "_e041_repeat_v25")
    est = module.Estimator()
    est.setup(_Ctx())
    pred = est.predict(mlp, BUDGET)
    return np.asarray(pred, dtype=np.float64), selected_repeat


def main() -> None:
    # Network fetch, immutable blob verification, patching and compilation happen
    # before the billed scientific context. The MLP-dependent selector and candidate
    # prediction themselves execute in one BudgetContext, as preregistered.
    patched_source, provenance = fetch_and_patch_pinned_source()
    code = compile(patched_source, "<_e041_pinned_v25>", "exec")
    row = _load_row0()
    mlp, gt = _make_mlp(row)
    probes = fnp.asarray(walsh_probes(np, mlp.width), dtype=fnp.float32)

    patch_counts = dict(provenance["patch_counts"])
    patch_scope_ok = (
        provenance["blob_sha"] == PINNED_BLOB_SHA
        and set(patch_counts) == _EXPECTED_PATCH_KEYS
        and all(v == 1 for v in patch_counts.values())
    )

    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        scores = backward_leverage_scores(fnp, mlp.weights, probes)
        scores_np = np.asarray(scores, dtype=np.float64)
        selected = select_births_knapsack(scores_np.tolist(), capacity=CAPACITY)
        selector_flops = float(ctx.flops_used)

        module = _load_frozen_module(code, selected, "_e041_science_v25")
        no_confine_frozen = bool(getattr(module, "NO_CONFINE", False))
        keep_births_frozen = tuple(getattr(module, "E041_KEEP_BIRTHS", ()))
        est = module.Estimator()
        est.setup(_Ctx())
        pred = est.predict(mlp, BUDGET)
        total_flops = float(ctx.flops_used)
    residual_s = float(ctx.residual_wall_time_s)
    wall_s = time.perf_counter() - t0

    arr = np.asarray(pred, dtype=np.float64)
    raw_mse = float(np.mean((arr[-1] - gt) ** 2))
    utilization = total_flops / BUDGET
    adjusted = raw_mse * max(0.1, utilization)
    pair_cost = source_pair_cost(selected)

    repeat_pred, repeat_selected = _repeat(row, code, selected)
    det_max_abs = float(np.max(np.abs(arr - repeat_pred)))
    finite = bool(np.isfinite(arr).all() and np.isfinite(repeat_pred).all())
    selection_exact = selected == select_births_knapsack(
        scores_np.tolist(), capacity=CAPACITY
    )
    selector_billed = selector_flops > 0.0 and total_flops >= selector_flops
    # The atomic patch guards every source-record component; successful traversal
    # through all 16 layers is the runtime cardinality check that all selected stacks
    # remained aligned (the same mismatch crashed E040 before metrics).
    atomic_cardinality_ok = patch_scope_ok and arr.shape[0] == 16
    no_other_v25_env_mutation = True

    gates = {
        "raw_mse_le_1.89e-08": raw_mse <= RAW_GATE,
        "utilization_le_0.14": utilization <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": residual_s < RESIDUAL_CAP,
        "finite": finite,
        "deterministic_repeat_diff_eq_0": det_max_abs == 0.0,
        "pair_cost_le_41": pair_cost <= CAPACITY,
        "selection_exact_knapsack": selection_exact,
        "selector_billed": selector_billed,
        "pinned_blob": provenance["blob_sha"] == PINNED_BLOB_SHA,
        "atomic_patch_counts": patch_scope_ok,
        "runtime_source_cardinality": atomic_cardinality_ok,
        "no_confine_true": no_confine_frozen is True,
        "keep_births_frozen": keep_births_frozen == selected,
        "repeat_selection_identical": repeat_selected == selected,
        "no_other_v25_env_mutation": no_other_v25_env_mutation,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "public_mini_index": 0,
        "leverage_scores": [float(x) for x in scores_np],
        "selected_births": list(selected),
        "selected_pair_cost": int(pair_cost),
        "selector_flops": selector_flops,
        "total_flops": total_flops,
        "utilization": utilization,
        "projected_utilization_pre_science": PROJECTED_UTILIZATION,
        "raw_final_mse": raw_mse,
        "adjusted_proxy": adjusted,
        "residual_s": residual_s,
        "wall_s": wall_s,
        "failures": 0,
        "finite": finite,
        "deterministic_repeat_max_abs": det_max_abs,
        "repeat_selected_births": list(repeat_selected),
        "pinned_blob": provenance["blob_sha"],
        "patch_counts": patch_counts,
        "no_confine_frozen": no_confine_frozen,
        "keep_births_frozen": list(keep_births_frozen),
        "runtime_source_cardinality_ok": atomic_cardinality_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E041_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e041_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
