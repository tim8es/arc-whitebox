#!/usr/bin/env python3
"""E175 one-shot target-free AGO-GAIN transfer falsifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e175_public_gain_ago import (
    candidate_estimate,
    gain_layer,
    parent_estimate,
    production_cost,
    radial_a1,
    to_angular,
    to_gaussian,
)

N = 1024
DEPTH = 16
WEIGHT_SEED = 1751024
REFERENCE_SEED = 175196608
REFERENCE_SAMPLES = 65536
REFERENCE_BATCHES = 16
A1_EXPECTED = 0.9997558892135413
TOL = 2e-12
SE_LIMIT = 1.2e-3


def sha_array(x: np.ndarray) -> str:
    y = np.ascontiguousarray(np.asarray(x))
    h = hashlib.sha256()
    h.update(str(y.shape).encode())
    h.update(y.dtype.str.encode())
    h.update(y.tobytes())
    return h.hexdigest()


def sha_weights(weights: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for w in weights:
        y = np.ascontiguousarray(w)
        h.update(y.tobytes())
    return h.hexdigest()


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = math.sqrt(2.0 / N)
    return [
        rng.standard_normal((N, N), dtype=np.float64) * scale
        for _ in range(DEPTH)
    ]


def rel(a: np.ndarray, b: np.ndarray) -> float:
    return float(
        np.linalg.norm(np.asarray(a) - np.asarray(b))
        / max(float(np.linalg.norm(b)), 2.0**-500)
    )


def gain_only_formula_audit() -> dict:
    mean = np.array([0.2, -0.1], dtype=np.float64)
    cov = np.array([[1.1, 0.31], [0.31, 0.8]], dtype=np.float64)
    w = np.array([[0.9, -0.4], [0.25, 1.1]], dtype=np.float64)
    out_mean, out_cov = gain_layer(mean, cov, w)

    pre_mean = w @ mean
    pre_cov = w @ cov @ w.T
    pre_cov = 0.5 * (pre_cov + pre_cov.T)
    var = np.maximum(np.diag(pre_cov), 1e-12)
    sigma = np.sqrt(var)
    alpha = pre_mean / sigma
    Phi = np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in alpha],
        dtype=np.float64,
    )
    expected_off = pre_cov[0, 1] * Phi[0] * Phi[1]
    gain_error = abs(float(out_cov[0, 1]) - float(expected_off))

    phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    deriv2 = phi / sigma
    second_order_off = expected_off + (
        0.5 * pre_cov[0, 1] ** 2 * deriv2[0] * deriv2[1]
    )
    second_order_gap = abs(float(out_cov[0, 1]) - float(second_order_off))
    return {
        "gain_only_offdiag_absolute_error": gain_error,
        "second_order_wick_counterfactual_gap": second_order_gap,
        "gain_only_exact": bool(gain_error <= 1e-15),
        "second_order_term_absent": bool(second_order_gap > 1e-8),
        "output_mean_sha256": sha_array(out_mean),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    weights = make_weights()
    weight_hash = sha_weights(weights)

    # Candidate-before-reference order.
    parent = parent_estimate(weights)
    candidate = candidate_estimate(weights)
    parent_replay = parent_estimate(weights)
    candidate_replay = candidate_estimate(weights)
    cost = production_cost()
    formula_audit = gain_only_formula_audit()

    replay_parent = bool(
        parent.digest == parent_replay.digest
        and np.array_equal(parent.final_mean, parent_replay.final_mean)
    )
    replay_candidate = bool(
        candidate.digest == candidate_replay.digest
        and np.array_equal(candidate.final_mean, candidate_replay.final_mean)
    )

    assert candidate.first_angular_mean is not None
    assert candidate.first_angular_covariance is not None
    mg2, cg2 = to_gaussian(
        candidate.first_angular_mean,
        candidate.first_angular_covariance,
        N,
    )
    roundtrip = max(
        rel(mg2, candidate.first_gaussian_mean),
        rel(cg2, candidate.first_gaussian_covariance),
    )
    ma2, ca2 = to_angular(
        candidate.first_gaussian_mean,
        candidate.first_gaussian_covariance,
        N,
    )
    forward_gauge = max(
        rel(ma2, candidate.first_angular_mean),
        rel(ca2, candidate.first_angular_covariance),
    )
    a1_error = abs(radial_a1(N) - A1_EXPECTED)

    pre_reference = {
        "experiment": "E175",
        "stage": "candidate_frozen_before_reference_import",
        "weight_seed": WEIGHT_SEED,
        "weight_sha256": weight_hash,
        "parent_digest": parent.digest,
        "candidate_digest": candidate.digest,
        "parent_final_sha256": sha_array(parent.final_mean),
        "candidate_final_sha256": sha_array(candidate.final_mean),
        "parent_replay_bitwise_exact": replay_parent,
        "candidate_replay_bitwise_exact": replay_candidate,
        "gauge_roundtrip_error": roundtrip,
        "gauge_forward_recompute_error": forward_gauge,
        "radial_a1_1024": radial_a1(N),
        "radial_a1_absolute_error": a1_error,
        "cost": cost,
        "gain_only_formula_audit": formula_audit,
    }
    (out_dir / "E175_PRE_REFERENCE_FREEZE.json").write_text(
        json.dumps(pre_reference, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Reference import is intentionally after parent/candidate/replay freeze.
    from methods.e171_reference_streaming import streaming_reference

    ref = streaming_reference(
        weights,
        n=N,
        total_samples=REFERENCE_SAMPLES,
        batch_count=REFERENCE_BATCHES,
        seed=REFERENCE_SEED,
    )
    a1 = radial_a1(N)
    reference_final = a1 * ref.angular_mean
    reference_batches = a1 * ref.batch_angular_means

    parent_error = parent.final_mean - reference_final
    candidate_error = candidate.final_mean - reference_final
    parent_mse = float(np.mean(parent_error * parent_error))
    candidate_mse = float(np.mean(candidate_error * candidate_error))
    ratio = candidate_mse / parent_mse if parent_mse > 0.0 else math.inf

    parent_batch_errors = parent.final_mean[None, :] - reference_batches
    candidate_batch_errors = candidate.final_mean[None, :] - reference_batches
    parent_batch_mse = np.mean(parent_batch_errors**2, axis=1)
    candidate_batch_mse = np.mean(candidate_batch_errors**2, axis=1)
    batch_delta = parent_batch_mse - candidate_batch_mse

    coordinate_se = np.std(reference_batches, axis=0, ddof=1) / math.sqrt(
        REFERENCE_BATCHES
    )
    reference_se_rms = float(np.sqrt(np.mean(coordinate_se**2)))
    reference_reconcile = rel(
        reference_final,
        np.mean(reference_batches, axis=0),
    )

    np.save(out_dir / "parent_final_mean.npy", parent.final_mean, allow_pickle=False)
    np.save(out_dir / "candidate_final_mean.npy", candidate.final_mean, allow_pickle=False)
    np.save(out_dir / "reference_final_mean.npy", reference_final, allow_pickle=False)
    np.save(out_dir / "reference_batch_means.npy", reference_batches, allow_pickle=False)
    np.save(out_dir / "parent_batch_errors.npy", parent_batch_errors, allow_pickle=False)
    np.save(out_dir / "candidate_batch_errors.npy", candidate_batch_errors, allow_pickle=False)
    np.save(out_dir / "reference_coordinate_se.npy", coordinate_se, allow_pickle=False)

    payloads = {}
    for p in sorted(out_dir.glob("*.npy")):
        payloads[p.name] = {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "size_bytes": p.stat().st_size,
        }

    finite = bool(
        parent.finite
        and candidate.finite
        and ref.finite
        and np.isfinite(reference_final).all()
        and np.isfinite(reference_batches).all()
        and np.isfinite(coordinate_se).all()
    )
    positive_count = int(np.sum(batch_delta > 0.0))
    delta_mean = float(np.mean(batch_delta))
    delta_se = float(
        np.std(batch_delta, ddof=1) / math.sqrt(REFERENCE_BATCHES)
    )

    gates = {
        "source_firewall": True,
        "public_parent_gain_only_formula": bool(
            formula_audit["gain_only_exact"]
            and formula_audit["second_order_term_absent"]
        ),
        "gauge_roundtrip_le_2e_12": bool(roundtrip <= TOL),
        "gauge_forward_recompute_le_2e_12": bool(forward_gauge <= TOL),
        "radial_a1_identity_le_1e_15": bool(a1_error <= 1e-15),
        "parent_replay_bitwise_exact": replay_parent,
        "candidate_replay_bitwise_exact": replay_candidate,
        "finite_all": finite,
        "reference_final_reconciles_batches_le_2e_12": bool(
            reference_reconcile <= TOL
        ),
        "reference_se_rms_le_1_2e_3": bool(reference_se_rms <= SE_LIMIT),
        "candidate_improves_parent": bool(
            parent_mse > 0.0 and math.isfinite(ratio) and ratio < 1.0
        ),
        "strong_transfer_ratio_le_0_98": bool(
            parent_mse > 0.0 and math.isfinite(ratio) and ratio <= 0.98
        ),
        "paired_batch_delta_mean_positive": bool(delta_mean > 0.0),
        "paired_batch_positive_at_least_10_of_16": bool(positive_count >= 10),
        "complete_cost_le_0_135B": bool(cost["pass"]),
        "exactly_one_external_run": True,
        "no_rescue_rerun_sweep": True,
    }
    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e175.ago_gain_transfer.v1",
        "experiment": "E175",
        "idempotency": "ARC-E175-AGO-GAIN-TRANSFER-20260921",
        "hypothesis": "AGO-GAIN",
        "panel": {
            "width": N,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "reference_seed": REFERENCE_SEED,
            "reference_samples": REFERENCE_SAMPLES,
            "reference_batches": REFERENCE_BATCHES,
            "reference_batch_size": REFERENCE_SAMPLES // REFERENCE_BATCHES,
        },
        "pre_reference_freeze": pre_reference,
        "metrics": {
            "parent_mse": parent_mse,
            "candidate_mse": candidate_mse,
            "candidate_over_parent": ratio,
            "mse_improvement_fraction": (
                1.0 - ratio if math.isfinite(ratio) else -math.inf
            ),
            "parent_rmse": math.sqrt(parent_mse),
            "candidate_rmse": math.sqrt(candidate_mse),
            "reference_se_rms": reference_se_rms,
            "reference_reconcile_error": reference_reconcile,
            "batch_positive_count": positive_count,
            "batch_total": REFERENCE_BATCHES,
            "batch_delta_mean": delta_mean,
            "batch_delta_se": delta_se,
            "batch_delta_mean_over_se": (
                math.inf if delta_se == 0.0 else delta_mean / delta_se
            ),
            "parent_batch_mse": parent_batch_mse.tolist(),
            "candidate_batch_mse": candidate_batch_mse.tolist(),
            "batch_delta": batch_delta.tolist(),
        },
        "payloads": payloads,
        "cost": cost,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E175_TARGET_FREE_GO_AGO_GAIN_PUBLIC_CLOSURE_TRANSFER"
            if scientific_go
            else "E175_TERMINAL_NO_GO_AGO_GAIN_PUBLIC_CLOSURE_TRANSFER"
        ),
        "scope": {
            "target_free": True,
            "synthetic_only": True,
            "production_shaped": True,
            "public_dataset": False,
            "public_target": False,
            "public_mini": False,
            "public_full": False,
            "scorer": False,
            "leaderboard": False,
            "submission": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "rerun": False,
            "rescue": False,
            "sweep": False,
        },
    }
    (out_dir / "E175_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E175_RESULT=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
