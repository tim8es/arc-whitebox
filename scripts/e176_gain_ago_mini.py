#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import math
from pathlib import Path
import time

import numpy as np

from methods import e176_gain_ago as candidate

ROOT = Path("e176_evidence")
MANIFEST = Path("e176_manifest.json")
RESULT = Path("e176_result.json")

N = 256
DEPTH = 8
WEIGHT_SEED = 1760256
REFERENCE_SEED = 17665536
REFERENCE_SAMPLES = 65536
REFERENCE_BATCHES = 16
REFERENCE_BATCH_SIZE = REFERENCE_SAMPLES // REFERENCE_BATCHES

def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def raw_sha(array: np.ndarray) -> str:
    x = np.ascontiguousarray(array)
    return hashlib.sha256(x.tobytes()).hexdigest()

def save_array(name: str, array: np.ndarray) -> dict:
    ROOT.mkdir(parents=True, exist_ok=True)
    x = np.ascontiguousarray(array)
    path = ROOT / name
    np.save(path, x, allow_pickle=False)
    y = np.load(path, allow_pickle=False)
    if not np.array_equal(x, y):
        raise RuntimeError(f"reload mismatch: {name}")
    return {
        "path": str(path),
        "dtype": str(x.dtype),
        "shape": list(x.shape),
        "nbytes": int(x.nbytes),
        "file_sha256": file_sha(path),
        "raw_array_sha256": raw_sha(x),
        "reload_raw_array_sha256": raw_sha(y),
        "reload_equal": True,
    }

def generate_weights() -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    w = rng.standard_normal((DEPTH, N, N), dtype=np.float64)
    w *= math.sqrt(2.0 / float(N))
    return w

def coordinate_mse_and_se(pred: np.ndarray, ref: np.ndarray) -> tuple[float, float]:
    sq = (np.asarray(pred, dtype=np.float64) - np.asarray(ref, dtype=np.float64)) ** 2
    return float(np.mean(sq)), float(np.std(sq, ddof=1) / math.sqrt(sq.size))

def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    source = Path(candidate.__file__).read_text(encoding="utf-8").lower()
    source_audit = {
        "no_e175_reference": "e175" not in source,
        "no_deriv2": "deriv2" not in source,
        "no_off_square": "off * off" not in source,
        "no_pre_cov_square": "pre_cov * pre_cov" not in source,
        "candidate_imports_reference": "e176_reference" in source,
        "official_parent_blob": "675b3dd8f032f342112a99f431115b35f8481620",
    }
    if not (
        source_audit["no_e175_reference"]
        and source_audit["no_deriv2"]
        and source_audit["no_off_square"]
        and source_audit["no_pre_cov_square"]
        and not source_audit["candidate_imports_reference"]
    ):
        raise RuntimeError(f"source firewall failed: {source_audit}")

    weights = generate_weights()
    weights_payload = save_array("weights.npy", weights)
    weights_hash = raw_sha(weights)

    t0 = time.perf_counter()
    parent1 = candidate.estimate(list(weights), ago=False)
    parent_wall = time.perf_counter() - t0

    t0 = time.perf_counter()
    cand1 = candidate.estimate(list(weights), ago=True)
    candidate_wall = time.perf_counter() - t0

    parent2 = candidate.estimate(list(weights), ago=False)
    cand2 = candidate.estimate(list(weights), ago=True)

    parent_replay = bool(np.array_equal(parent1.all_layer_means, parent2.all_layer_means))
    candidate_replay = bool(np.array_equal(cand1.all_layer_means, cand2.all_layer_means))
    if not parent_replay or not candidate_replay:
        raise RuntimeError(
            f"deterministic replay failed parent={parent_replay} candidate={candidate_replay}"
        )

    # Candidate is frozen and retained before any reference import.
    pre_reference_payloads = [
        weights_payload,
        save_array("parent_all_layer_means.npy", parent1.all_layer_means),
        save_array("candidate_all_layer_means.npy", cand1.all_layer_means),
        save_array("parent_final_mean.npy", parent1.all_layer_means[-1]),
        save_array("candidate_final_mean.npy", cand1.all_layer_means[-1]),
        save_array("candidate_first_angular_mean.npy", cand1.first_angular_mean),
        save_array("candidate_first_angular_covariance.npy", cand1.first_angular_covariance),
    ]
    pre_reference_freeze = {
        p["path"]: p["file_sha256"] for p in pre_reference_payloads
    }
    pre_reference_freeze_sha256 = hashlib.sha256(
        json.dumps(pre_reference_freeze, sort_keys=True).encode("utf-8")
    ).hexdigest()

    production_cost = candidate.production_cost_receipt()
    mini_cost = candidate.mini_cost_receipt(N, DEPTH)

    # Mandatory ordering barrier: reference module imported only here.
    reference_module = importlib.import_module("methods.e176_reference")
    t0 = time.perf_counter()
    ref = reference_module.streaming_reference(
        list(weights),
        n=N,
        total_samples=REFERENCE_SAMPLES,
        batch_count=REFERENCE_BATCHES,
        seed=REFERENCE_SEED,
    )
    reference_wall = time.perf_counter() - t0

    reference_final = np.asarray(ref.final_mean, dtype=np.float64)
    reference_batches = np.asarray(ref.batch_final_means, dtype=np.float64)
    reference_se = np.asarray(ref.coordinate_se, dtype=np.float64)

    parent_final = np.asarray(parent1.all_layer_means[-1], dtype=np.float64)
    candidate_final = np.asarray(cand1.all_layer_means[-1], dtype=np.float64)

    parent_error = parent_final - reference_final
    candidate_error = candidate_final - reference_final
    parent_sq = parent_error * parent_error
    candidate_sq = candidate_error * candidate_error

    parent_mse, parent_coordinate_mse_se = coordinate_mse_and_se(parent_final, reference_final)
    candidate_mse, candidate_coordinate_mse_se = coordinate_mse_and_se(candidate_final, reference_final)
    ratio = candidate_mse / parent_mse if parent_mse > 0.0 else math.inf

    parent_batch_mse = np.mean(
        (reference_batches - parent_final[None, :]) ** 2, axis=1
    )
    candidate_batch_mse = np.mean(
        (reference_batches - candidate_final[None, :]) ** 2, axis=1
    )
    paired_delta = parent_batch_mse - candidate_batch_mse
    delta_mean = float(np.mean(paired_delta))
    delta_se = float(np.std(paired_delta, ddof=1) / math.sqrt(paired_delta.size))
    positive_count = int(np.count_nonzero(paired_delta > 0.0))

    ref_se_rms = float(np.sqrt(np.mean(reference_se * reference_se)))
    ref_reconcile = float(
        np.max(
            np.abs(
                reference_final
                - np.mean(reference_batches, axis=0, dtype=np.float64)
            )
        )
    )

    post_payloads = [
        save_array("reference_final_mean.npy", reference_final),
        save_array("reference_batch_final_means.npy", reference_batches),
        save_array("reference_coordinate_se.npy", reference_se),
        save_array("parent_final_error.npy", parent_error),
        save_array("candidate_final_error.npy", candidate_error),
        save_array("parent_final_squared_error.npy", parent_sq),
        save_array("candidate_final_squared_error.npy", candidate_sq),
        save_array("parent_batch_mse.npy", parent_batch_mse),
        save_array("candidate_batch_mse.npy", candidate_batch_mse),
        save_array("paired_batch_delta.npy", paired_delta),
    ]
    payloads = pre_reference_payloads + post_payloads

    all_arrays_finite = bool(
        parent1.finite
        and cand1.finite
        and ref.finite
        and all(
            np.isfinite(np.load(p["path"], allow_pickle=False)).all()
            for p in payloads
        )
    )

    reference_research_flops = 2 * REFERENCE_SAMPLES * DEPTH * N * N

    gates = {
        "source_firewall": bool(
            source_audit["no_e175_reference"]
            and not source_audit["candidate_imports_reference"]
        ),
        "gain_only_parent_audit": bool(
            source_audit["no_deriv2"]
            and source_audit["no_off_square"]
            and source_audit["no_pre_cov_square"]
        ),
        "gauge_roundtrip_le_2e_12": cand1.gauge_roundtrip_relative_error <= 2e-12,
        "parent_replay_bitwise": parent_replay,
        "candidate_replay_bitwise": candidate_replay,
        "all_arrays_finite": all_arrays_finite,
        "reference_batch_reconcile_le_2e_12": ref_reconcile <= 2e-12,
        "reference_se_rms_le_1p5e_3": ref_se_rms <= 1.5e-3,
        "candidate_mse_lt_parent": candidate_mse < parent_mse,
        "candidate_over_parent_le_0p98": ratio <= 0.98,
        "paired_delta_mean_positive": delta_mean > 0.0,
        "paired_delta_mean_gt_2se": delta_mean > 2.0 * delta_se,
        "positive_batches_ge_11_of_16": positive_count >= 11,
        "production_candidate_cost_le_0p135B": bool(production_cost["passes_cap"]),
        "exactly_one_external_run_protocol": True,
    }
    scientific_go = all(gates.values())

    manifest = {
        "schema": "arc.whitebox.e176.immutable_vectors.v1",
        "experiment": "E176",
        "fixture": {
            "width": N,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "reference_seed": REFERENCE_SEED,
            "reference_samples": REFERENCE_SAMPLES,
            "reference_batches": REFERENCE_BATCHES,
            "reference_batch_size": REFERENCE_BATCH_SIZE,
        },
        "weights_raw_sha256": weights_hash,
        "candidate_frozen_before_reference_import": True,
        "pre_reference_freeze_sha256": pre_reference_freeze_sha256,
        "payloads": payloads,
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = {
        "schema": "arc.whitebox.e176.result.v1",
        "experiment": "E176",
        "idempotency_key": "ARC-E176-CLEANROOM-AGO-GAIN-MINI-20260921",
        "decision": (
            "E176_TARGET_FREE_LOCAL_MINI_SCIENTIFIC_GO"
            if scientific_go
            else "E176_SCIENTIFIC_NO_GO"
        ),
        "scientific_go": scientific_go,
        "fixture": manifest["fixture"],
        "source_audit": source_audit,
        "weights_raw_sha256": weights_hash,
        "parent_prediction_raw_sha256": parent1.raw_sha256,
        "candidate_prediction_raw_sha256": cand1.raw_sha256,
        "candidate_frozen_before_reference_import": True,
        "pre_reference_freeze_sha256": pre_reference_freeze_sha256,
        "gauge_roundtrip_relative_error": cand1.gauge_roundtrip_relative_error,
        "replay": {
            "parent_bitwise_exact": parent_replay,
            "candidate_bitwise_exact": candidate_replay,
        },
        "metrics": {
            "parent_mse": parent_mse,
            "candidate_mse": candidate_mse,
            "candidate_over_parent": ratio,
            "improvement_fraction": 1.0 - ratio,
            "parent_coordinate_mse_se": parent_coordinate_mse_se,
            "candidate_coordinate_mse_se": candidate_coordinate_mse_se,
            "reference_coordinate_se_rms": ref_se_rms,
            "reference_batch_reconcile_max_abs": ref_reconcile,
            "paired_batch_delta_mean": delta_mean,
            "paired_batch_delta_se": delta_se,
            "paired_delta_mean_over_se": (
                delta_mean / delta_se if delta_se > 0.0 else math.inf
            ),
            "positive_batch_count": positive_count,
            "batch_count": int(paired_delta.size),
        },
        "flops": {
            "production": production_cost,
            "local_mini_research_upper": mini_cost,
            "reference_research_flop_upper": int(reference_research_flops),
            "reference_excluded_from_estimator_cost": True,
        },
        "wall_seconds": {
            "parent": parent_wall,
            "candidate": candidate_wall,
            "reference": reference_wall,
        },
        "manifest": {
            "path": str(MANIFEST),
            "sha256": None,
            "payload_count": len(payloads),
        },
        "gates": gates,
        "scope": {
            "synthetic_target_free": True,
            "public_dataset": False,
            "public_mini": False,
            "leaderboard": False,
            "submission": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "sweep": False,
            "rerun": False,
            "e175_rescue": False,
        },
    }
    result["manifest"]["sha256"] = file_sha(MANIFEST)
    RESULT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("E176_RESULT=" + json.dumps(result, sort_keys=True))
    if not scientific_go:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
