from __future__ import annotations

import gc
import hashlib
import json
import math
import types
import urllib.request
from pathlib import Path

import flopscope as flops
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP

from methods.e091_production_bridge import (
    FEATURE_P,
    PHASE2_BUDGET,
    final_layer_coordinate_features,
    production_cost_ceiling,
)
from methods.e091_production_shape_exact import (
    exact_layer_means,
    fit_shared_ridge,
    generate_exact_family_weights,
)

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research" / "E091_PRODUCTION_SHAPE_EXACT_FAMILY_FREEZE.json"
E043_COMMIT = "d0108f7faccaa656d3908f5afeaa90e056881c71"
E043_ADAPTER_BLOB = "8777dde2b848dd8ae855f9040ca27b4c6f235989"
E043_UPSTREAM_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
E043_ADAPTER_URL = (
    "https://raw.githubusercontent.com/tim8es/arc-whitebox/"
    + E043_COMMIT
    + "/methods/e043_terminal_adjoint_k3.py"
)
RAW_GATE = 1.89e-8
UTIL_GATE = 0.135


def canonical_payload_sha256(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def load_freeze() -> tuple[dict, str]:
    record = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    payload = record["payload"]
    observed = canonical_payload_sha256(payload)
    declared = str(record["payload_sha256"])
    if observed != declared:
        raise AssertionError(f"freeze payload hash mismatch: {observed} != {declared}")
    if payload["base"]["commit"] != E043_COMMIT:
        raise AssertionError("E043 commit identity drift")
    if payload["base"]["adapter_blob_sha"] != E043_ADAPTER_BLOB:
        raise AssertionError("E043 adapter blob identity drift")
    return payload, observed


def load_frozen_e043_module():
    with urllib.request.urlopen(E043_ADAPTER_URL, timeout=30) as response:
        adapter_raw = response.read()
    adapter_blob = git_blob_sha(adapter_raw)
    if adapter_blob != E043_ADAPTER_BLOB:
        raise AssertionError(f"E043 adapter blob mismatch: {adapter_blob}")
    adapter = types.ModuleType("e091_frozen_e043_adapter")
    exec(compile(adapter_raw.decode("utf-8"), "<e091_frozen_e043_adapter>", "exec"), adapter.__dict__)
    patched, provenance = adapter.fetch_and_patch_pinned_source()
    if provenance["blob_sha"] != E043_UPSTREAM_BLOB:
        raise AssertionError("E043 upstream pinned blob mismatch")
    if not all(int(v) == 1 for v in provenance["patch_counts"].values()):
        raise AssertionError(f"E043 patch count drift: {provenance['patch_counts']}")
    module = types.ModuleType("e091_frozen_e043_estimator")
    exec(compile(patched, "<e091_frozen_e043_estimator>", "exec"), module.__dict__)
    return module, {
        "adapter_blob_sha": adapter_blob,
        "upstream_blob_sha": provenance["blob_sha"],
        "patch_counts": provenance["patch_counts"],
    }


def run_base(module, seed: int, width: int, depth: int) -> dict[str, object]:
    weights = generate_exact_family_weights(seed=seed, width=width, depth=depth)
    truth = exact_layer_means(weights)
    mlp = MLP(width=width, depth=depth, weights=weights, seed=seed, name=f"e091-exact-{seed}")
    mlp.validate()
    estimator = module.Estimator()
    estimator.setup(
        SetupContext(width=width, depth=depth, flop_budget=PHASE2_BUDGET, api_version="1", seed=0)
    )
    with flops.BudgetContext(flop_budget=PHASE2_BUDGET, quiet=True) as budget:
        prediction = estimator.predict(mlp, PHASE2_BUDGET)
    estimator.teardown()
    pred = np.asarray(prediction, dtype=np.float64)
    if pred.shape != (depth, width):
        raise AssertionError(f"unexpected E043 output shape {pred.shape}")
    finite = bool(np.isfinite(pred).all() and np.isfinite(truth).all())
    replay = {
        "stored_births": int(estimator._e043_stored_births),
        "replayed_births": int(estimator._e043_replayed_births),
        "nonterminal_replays": int(estimator._e043_nonterminal_replays),
    }
    replay["ok"] = bool(
        replay["stored_births"] == depth - 1
        and replay["replayed_births"] == depth - 1
        and replay["nonterminal_replays"] == 0
    )
    features = final_layer_coordinate_features(pred, weights[-1])
    result = {
        "seed": int(seed),
        "base_prediction": pred,
        "truth": truth,
        "features": features,
        "last_weight": weights[-1],
        "base_flops": int(budget.flops_used),
        "base_utilization": float(budget.flops_used / PHASE2_BUDGET),
        "finite": finite,
        "terminal_replay": replay,
    }
    del mlp, estimator, prediction, weights
    gc.collect()
    return result


def mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def main() -> None:
    payload, freeze_hash = load_freeze()
    width = int(payload["shape"]["width"])
    depth = int(payload["shape"]["depth"])
    calibration_seeds = [int(v) for v in payload["split"]["calibration_seeds"]]
    evaluation_seeds = [int(v) for v in payload["split"]["evaluation_seeds"]]
    if set(calibration_seeds) & set(evaluation_seeds):
        raise AssertionError("calibration/evaluation network overlap")
    if width != 1024 or depth != 16 or FEATURE_P != 16:
        raise AssertionError("production-shape identity drift")

    base_module, base_provenance = load_frozen_e043_module()

    cal_X: list[np.ndarray] = []
    cal_z: list[np.ndarray] = []
    calibration_metrics: list[dict[str, object]] = []
    for seed in calibration_seeds:
        row = run_base(base_module, seed, width, depth)
        final_base = np.asarray(row["base_prediction"][-1], dtype=np.float64)
        final_truth = np.asarray(row["truth"][-1], dtype=np.float64)
        cal_X.append(np.asarray(row["features"], dtype=np.float64))
        cal_z.append(final_truth - final_base)
        calibration_metrics.append(
            {
                "seed": seed,
                "base_raw_mse": mse(final_base, final_truth),
                "base_flops": int(row["base_flops"]),
                "finite": bool(row["finite"]),
                "terminal_replay": row["terminal_replay"],
            }
        )
        del row
        gc.collect()

    design = np.vstack(cal_X)
    residual = np.concatenate(cal_z)
    beta = fit_shared_ridge(design, residual, lam=float(payload["ridge"]["lambda"]))
    calibration_corrected_mse = float(np.mean((design @ beta - residual) ** 2))
    del cal_X, cal_z, design, residual
    gc.collect()

    eval_metrics: list[dict[str, object]] = []
    base_sse = 0.0
    corrected_sse = 0.0
    count = 0
    max_utilization_upper = 0.0
    all_finite = True
    all_replay_ok = True
    frozen_cost = production_cost_ceiling(width)
    bridge_ceiling = int(frozen_cost["feature_flops_ceiling"]) + int(
        frozen_cost["correction_flops_ceiling"]
    )

    for seed in evaluation_seeds:
        row = run_base(base_module, seed, width, depth)
        final_base = np.asarray(row["base_prediction"][-1], dtype=np.float64)
        final_truth = np.asarray(row["truth"][-1], dtype=np.float64)
        features = np.asarray(row["features"], dtype=np.float64)
        correction = features @ beta
        corrected = final_base + correction
        base_err = final_base - final_truth
        corrected_err = corrected - final_truth
        base_mse = float(np.mean(base_err * base_err))
        corrected_mse = float(np.mean(corrected_err * corrected_err))
        base_sse += float(np.sum(base_err * base_err))
        corrected_sse += float(np.sum(corrected_err * corrected_err))
        count += width
        all_in_flops_upper = int(row["base_flops"]) + bridge_ceiling
        util_upper = float(all_in_flops_upper / PHASE2_BUDGET)
        max_utilization_upper = max(max_utilization_upper, util_upper)
        all_finite = all_finite and bool(row["finite"]) and bool(np.isfinite(corrected).all())
        all_replay_ok = all_replay_ok and bool(row["terminal_replay"]["ok"])
        eval_metrics.append(
            {
                "seed": seed,
                "base_raw_mse": base_mse,
                "corrected_raw_mse": corrected_mse,
                "relative_mse_improvement": float(1.0 - corrected_mse / base_mse)
                if base_mse > 0.0
                else 0.0,
                "base_flops": int(row["base_flops"]),
                "bridge_flops_ceiling": bridge_ceiling,
                "whole_candidate_flops_upper": all_in_flops_upper,
                "whole_candidate_utilization_upper": util_upper,
                "finite": bool(row["finite"]) and bool(np.isfinite(corrected).all()),
                "terminal_replay": row["terminal_replay"],
                "truth_final_mean_abs_max": float(np.max(np.abs(final_truth))),
                "correction_abs_max": float(np.max(np.abs(correction))),
            }
        )
        del row, final_base, final_truth, features, correction, corrected
        gc.collect()

    heldout_base_mse = float(base_sse / count)
    heldout_corrected_mse = float(corrected_sse / count)
    raw_gate = bool(heldout_corrected_mse <= RAW_GATE)
    util_gate = bool(max_utilization_upper <= UTIL_GATE)
    execution_gate = bool(all_finite and all_replay_ok)
    falsifier_pass = bool(raw_gate and util_gate and execution_gate)

    result = {
        "schema": "arc.whitebox.e091.production_shape_exact_family_result.v1",
        "experiment": "E091",
        "freeze_payload_sha256": freeze_hash,
        "identity": {
            "base_experiment": "E043",
            "base_commit": E043_COMMIT,
            "base_adapter_blob": E043_ADAPTER_BLOB,
            "feature_map": "final_layer_coordinate_features_v1",
            "p": FEATURE_P,
            "lambda": float(payload["ridge"]["lambda"]),
            "calibration_unit": "whole synthetic network",
            "width": width,
            "depth": depth,
        },
        "base_provenance": base_provenance,
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "benchmark_holdout": False,
            "full_suite": False,
            "benchmark_targets_read": False,
        },
        "calibration": {
            "seeds": calibration_seeds,
            "rows": len(calibration_seeds) * width,
            "metrics": calibration_metrics,
            "ridge_training_residual_mse": calibration_corrected_mse,
            "beta": beta.tolist(),
            "beta_l2": float(np.linalg.norm(beta)),
        },
        "evaluation": {
            "seeds": evaluation_seeds,
            "network_metrics": eval_metrics,
            "heldout_base_raw_mse": heldout_base_mse,
            "heldout_corrected_raw_mse": heldout_corrected_mse,
            "relative_mse_improvement": float(1.0 - heldout_corrected_mse / heldout_base_mse)
            if heldout_base_mse > 0.0
            else 0.0,
            "max_whole_candidate_utilization_upper": max_utilization_upper,
        },
        "gates": {
            "finite_and_terminal_replay": execution_gate,
            "raw_le_1_89e_8": raw_gate,
            "utilization_le_0_135": util_gate,
        },
        "falsifier_pass": falsifier_pass,
        "scientific_go": False,
        "decision": "PRODUCTION_SHAPE_FALSIFIER_PASS_ONLY" if falsifier_pass else "SCIENTIFIC_NO_GO",
        "terminal_blocker": None
        if falsifier_pass
        else {
            "raw_gate_failed": not raw_gate,
            "utilization_gate_failed": not util_gate,
            "execution_gate_failed": not execution_gate,
            "note": "Frozen production-shape exact-ground-truth falsifier failed; E091 terminal rule forbids seed/feature/lambda rescue or a second family under E091.",
        },
    }
    out = ROOT / "e091-production-shape-exact-result.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("E091_PRODUCTION_SHAPE_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
