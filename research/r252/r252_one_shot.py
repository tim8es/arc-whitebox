#!/usr/bin/env python3
"""One-shot R252 target-free parent/candidate harness.

The candidate file is created only after the unchanged parent gate passes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp
from whestbench.domain import MLP

from r252_fixture import (
    DEPTH,
    WIDTH,
    EXPECTED_TRUTH_SHA256,
    EXPECTED_WEIGHTS_SHA256,
    build_manifest,
    build_weights,
    exact_truth,
)

BUDGET = 2**41
EXPECTED_PARENT_SHA256 = "c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20"

OLD_DA = "dA_list.append(9.0 + w2 * w2 + 9.0 * e_b * e_b)"
OLD_DP = "dP_list.append(1.0 + S3c * S3c)"
NEW_DA = "dA_list.append(w2 * w2 + e_b * e_b)"
NEW_DP = "dP_list.append(w2 * w2 + S3c * S3c)"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def import_estimator(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Estimator


def covariance_trace_lines(path: Path) -> set[int]:
    lines = path.read_text().splitlines()
    hits = [
        i + 1
        for i, line in enumerate(lines)
        if "C = flops.as_symmetric(C, symmetry=(0, 1))" in line
    ]
    if len(hits) != 2:
        raise RuntimeError(f"expected two C as_symmetric sites, got {hits}")
    # Trace fires before a line. The next line sees the post-as_symmetric C.
    return {hits[-1] + 1}


def run_estimator(path: Path, weights: list[np.ndarray], label: str) -> dict:
    Estimator = import_estimator(path, f"r252_{label}")
    mlp = MLP(
        width=WIDTH,
        depth=DEPTH,
        weights=[fnp.asarray(w, dtype=fnp.float32) for w in weights],
        seed=252001,
        name="r252-block2-252001",
    )
    mlp.validate()
    target_lines = covariance_trace_lines(path)
    checkpoints = []
    abs_path = str(path.resolve())

    def tracer(frame, event, arg):
        if event == "line" and frame.f_code.co_filename == abs_path and frame.f_lineno in target_lines:
            C = frame.f_locals.get("C")
            li = frame.f_locals.get("li")
            if C is not None and li is not None:
                arr = np.asarray(C)
                finite = bool(np.isfinite(arr).all())
                max_abs = float(np.max(np.abs(arr))) if arr.size else 0.0
                sym = float(np.max(np.abs(arr - arr.T))) if arr.size else 0.0
                checkpoints.append(
                    {
                        "layer": int(li),
                        "finite": finite,
                        "max_abs": max_abs,
                        "max_symmetry_residual": sym,
                    }
                )
        return tracer

    result = {
        "label": label,
        "source_sha256": sha256_bytes(path.read_bytes()),
        "exception": None,
        "covariance_checkpoints": checkpoints,
    }
    oldtrace = sys.gettrace()
    try:
        sys.settrace(tracer)
        with flops.BudgetContext(
            flop_budget=BUDGET,
            wall_time_limit_s=120.0,
            quiet=True,
        ) as ctx:
            pred = Estimator().predict(mlp, budget=BUDGET)
        arr = np.asarray(pred, dtype=np.float64)
        summary = ctx.summary()
        result.update(
            {
                "shape": list(arr.shape),
                "prediction_sha256": sha256_bytes(
                    np.asarray(pred, dtype="<f4").tobytes(order="C")
                ),
                "flops_used": int(ctx.flops_used),
                "budget_summary": summary,
                "prediction_finite_by_layer": [
                    bool(np.isfinite(arr[i]).all()) for i in range(arr.shape[0])
                ],
                "prediction_max_abs_by_layer": [
                    float(np.max(np.abs(arr[i]))) for i in range(arr.shape[0])
                ],
                "_prediction": arr,
            }
        )
    except Exception as exc:
        result["exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        sys.settrace(oldtrace)
    return result


def add_truth_metrics(result: dict, truth: np.ndarray) -> None:
    if result.get("exception") is not None or "_prediction" not in result:
        return
    pred = result["_prediction"]
    if pred.shape != truth.shape:
        return
    per = np.mean((pred - truth) ** 2, axis=1)
    result["per_layer_mse"] = [float(x) for x in per]
    result["all_layer_mse"] = float(np.mean(per))
    result["final_layer_mse"] = float(per[-1])


def parent_gate(result: dict) -> tuple[bool, list[str]]:
    failures = []
    if result.get("source_sha256") != EXPECTED_PARENT_SHA256:
        failures.append("parent_source_hash")
    if result.get("exception") is not None:
        failures.append("parent_exception")
    if result.get("shape") != [DEPTH, WIDTH]:
        failures.append("parent_shape")
    if not all(result.get("prediction_finite_by_layer", [])):
        failures.append("parent_nonfinite_prediction")
    cps = result.get("covariance_checkpoints", [])
    if len(cps) != DEPTH:
        failures.append(f"parent_covariance_checkpoint_count:{len(cps)}")
    for cp in cps:
        if not cp["finite"]:
            failures.append(f"parent_cov_nonfinite_L{cp['layer']}")
        tol = 1.0e-5 * max(1.0, cp["max_abs"])
        if cp["max_symmetry_residual"] > tol:
            failures.append(f"parent_cov_symmetry_L{cp['layer']}")
    return (not failures), failures


def construct_candidate(parent_path: Path, candidate_path: Path) -> dict:
    src = parent_path.read_text()
    counts = {OLD_DA: src.count(OLD_DA), OLD_DP: src.count(OLD_DP)}
    if counts[OLD_DA] != 1 or counts[OLD_DP] != 1:
        raise RuntimeError(f"patch anchor count mismatch: {counts}")
    candidate = src.replace(OLD_DA, NEW_DA).replace(OLD_DP, NEW_DP)
    # R252 delta itself may contain only fnp-array arithmetic and shipped literals.
    delta = NEW_DA + "\n" + NEW_DP
    if "math." in delta or "/" in delta or "float(" in delta:
        raise RuntimeError("R252 delta source-compliance gate failed")
    candidate_path.write_text(candidate)
    return {
        "anchor_counts": counts,
        "parent_sha256": sha256_bytes(src.encode()),
        "candidate_sha256": sha256_bytes(candidate.encode()),
        "old_lines": [OLD_DA, OLD_DP],
        "new_lines": [NEW_DA, NEW_DP],
        "delta_math_star": False,
        "delta_python_division": False,
        "delta_scalar_materialization": False,
    }


def candidate_gate(parent: dict, cand: dict) -> tuple[bool, list[str], dict]:
    failures = []
    ratios = {}
    if cand.get("exception") is not None:
        failures.append("candidate_exception")
    if cand.get("shape") != [DEPTH, WIDTH]:
        failures.append("candidate_shape")
    if not all(cand.get("prediction_finite_by_layer", [])):
        failures.append("candidate_nonfinite_prediction")
    if "final_layer_mse" not in cand or "final_layer_mse" not in parent:
        failures.append("missing_truth_metrics")
        return False, failures, ratios

    ratios["final_mse_ratio"] = cand["final_layer_mse"] / parent["final_layer_mse"]
    ratios["all_layer_mse_ratio"] = cand["all_layer_mse"] / parent["all_layer_mse"]
    per_ratios = []
    improved = 0
    for p, c in zip(parent["per_layer_mse"], cand["per_layer_mse"]):
        if c < p:
            improved += 1
        per_ratios.append(c / p if p > 0.0 else (1.0 if c == 0.0 else float("inf")))
    ratios["per_layer_ratios"] = per_ratios
    ratios["improved_layers"] = improved
    ratios["max_per_layer_degradation_ratio"] = max(per_ratios)
    ratios["flop_ratio"] = cand["flops_used"] / parent["flops_used"]

    p_res = float(parent.get("budget_summary", {}).get("residual_wall_time_s", 0.0))
    c_res = float(cand.get("budget_summary", {}).get("residual_wall_time_s", 0.0))
    ratios["parent_residual_wall_time_s"] = p_res
    ratios["candidate_residual_wall_time_s"] = c_res

    if ratios["final_mse_ratio"] > 0.95:
        failures.append("final_mse_ratio")
    if ratios["all_layer_mse_ratio"] > 0.98:
        failures.append("all_layer_mse_ratio")
    if improved < 12:
        failures.append("improved_layers")
    if ratios["max_per_layer_degradation_ratio"] > 1.10:
        failures.append("max_per_layer_degradation")
    if cand["flops_used"] > parent["flops_used"]:
        failures.append("flops")
    if c_res > 1.05 * p_res + 0.005:
        failures.append("residual_wall_time")
    return (not failures), failures, ratios


def clean_result(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "_prediction"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    parent_path = Path(args.parent).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    weights = build_weights()
    truth, counts = exact_truth()
    manifest = build_manifest(weights, truth, counts)
    if manifest["weights_concat_sha256"] != EXPECTED_WEIGHTS_SHA256:
        raise RuntimeError("fixture hash mismatch")
    if manifest["truth_sha256"] != EXPECTED_TRUTH_SHA256:
        raise RuntimeError("truth hash mismatch")
    (out / "R252_FIXTURE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    parent = run_estimator(parent_path, weights, "parent")
    add_truth_metrics(parent, truth)
    pgo, pfail = parent_gate(parent)
    result = {
        "schema": "arc.r252.target_free.v1",
        "fixture": manifest,
        "parent": clean_result(parent),
        "parent_go": pgo,
        "parent_failures": pfail,
        "candidate_constructed": False,
        "candidate": None,
        "candidate_go": False,
        "candidate_failures": [],
        "candidate_ratios": {},
        "decision": None,
    }

    if not pgo:
        result["decision"] = "INCONCLUSIVE_PARENT_GATE"
        (out / "R252_TARGET_FREE_RESULT.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        )
        return 20

    candidate_path = out / "R252_CANDIDATE_SOURCE.py"
    patch = construct_candidate(parent_path, candidate_path)
    result["candidate_constructed"] = True
    result["candidate_patch"] = patch

    cand = run_estimator(candidate_path, weights, "candidate")
    add_truth_metrics(cand, truth)
    cgo, cfail, ratios = candidate_gate(parent, cand)
    result["candidate"] = clean_result(cand)
    result["candidate_go"] = cgo
    result["candidate_failures"] = cfail
    result["candidate_ratios"] = ratios
    result["decision"] = (
        "TARGET_FREE_GO_PUBLIC_AUTHORIZED"
        if cgo
        else "DEVELOPMENT_NO_GO_TARGET_FREE"
    )
    (out / "R252_TARGET_FREE_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    return 0 if cgo else 31


if __name__ == "__main__":
    raise SystemExit(main())
