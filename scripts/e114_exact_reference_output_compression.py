#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from methods.e114_exact_angular_reference import (
    build_exact_reference,
    he_weights,
    oracle_flux_basis,
    partition_diagnostics,
    projection_metrics,
    reference_numeric_arrays,
)

WIDTH = 8
DEPTH = 4
SEEDS = (114200, 114201, 114202, 114203)
ORACLE_RANKS = (1, 2, 4)
OUT = Path("e114-exact-reference-output-compression.json")


def _matrix_summary(a: np.ndarray) -> dict[str, Any]:
    arr = np.asarray(a, dtype=np.float64)
    return {
        "shape": list(arr.shape),
        "trace": float(np.trace(arr)) if arr.ndim == 2 else None,
        "fro": float(np.linalg.norm(arr)),
        "max_abs": float(np.max(np.abs(arr))) if arr.size else 0.0,
    }


def _offdiag_rms(a: np.ndarray) -> float:
    arr = np.asarray(a, dtype=np.float64).copy()
    np.fill_diagonal(arr, 0.0)
    return float(np.sqrt(np.mean(arr * arr)))


def _run_seed(seed: int) -> tuple[dict[str, Any], list[np.ndarray]]:
    weights = he_weights(seed, width=WIDTH, depth=DEPTH)
    ref = build_exact_reference(weights)
    partition = partition_diagnostics(ref.sectors)

    flux_delta = np.asarray(ref.mean - ref.flux_mean, dtype=np.float64)
    cov_eigs = np.linalg.eigvalsh(ref.covariance)

    identity = projection_metrics(ref, np.eye(WIDTH, dtype=np.float64))
    zero = projection_metrics(ref, np.zeros((WIDTH, 0), dtype=np.float64))

    zero_second_delta = np.asarray(
        zero["residual_second_moment"] - ref.second_moment,
        dtype=np.float64,
    )

    oracle = {}
    replay_arrays = reference_numeric_arrays(ref)

    for rank in ORACLE_RANKS:
        basis = oracle_flux_basis(ref, rank)
        metrics = projection_metrics(ref, basis)
        replay_arrays.extend(
            [
                basis,
                metrics["projector"],
                metrics["bias"],
                metrics["compressed_covariance"],
                metrics["residual_covariance"],
                metrics["cross_covariance"],
                metrics["residual_second_moment"],
            ]
        )
        oracle[str(rank)] = {
            "rank": rank,
            "basis": basis.tolist(),
            "bias": np.asarray(metrics["bias"], dtype=np.float64).tolist(),
            "bias_l2": float(metrics["bias_l2"]),
            "bias_mse_across_outputs": float(metrics["bias_mse_across_outputs"]),
            "bias_max_abs": float(np.max(np.abs(metrics["bias"]))),
            "compressed_covariance": np.asarray(
                metrics["compressed_covariance"], dtype=np.float64
            ).tolist(),
            "residual_covariance": np.asarray(
                metrics["residual_covariance"], dtype=np.float64
            ).tolist(),
            "cross_covariance": np.asarray(
                metrics["cross_covariance"], dtype=np.float64
            ).tolist(),
            "residual_second_moment": np.asarray(
                metrics["residual_second_moment"], dtype=np.float64
            ).tolist(),
            "residual_covariance_trace": float(
                np.trace(metrics["residual_covariance"])
            ),
            "cross_covariance_fro": float(
                np.linalg.norm(metrics["cross_covariance"])
            ),
            "remainder_mse_total": float(metrics["remainder_mse_total"]),
            "relative_remainder_mse": float(metrics["relative_remainder_mse"]),
            "flux_energy_total": float(metrics["flux_energy_total"]),
            "flux_energy_residual": float(metrics["flux_energy_residual"]),
            "relative_flux_energy_residual": float(
                metrics["relative_flux_energy_residual"]
            ),
            "projector_symmetry_max_abs": float(
                metrics["projector_symmetry_max_abs"]
            ),
            "projector_idempotence_max_abs": float(
                metrics["projector_idempotence_max_abs"]
            ),
            "per_observable": metrics["per_observable"],
        }

    record = {
        "seed": seed,
        "width": WIDTH,
        "depth": DEPTH,
        "final_sector_count": len(ref.sectors),
        "boundary_count": int(ref.boundary_jumps.shape[0]),
        "partition": partition,
        "exact_mean": ref.mean.tolist(),
        "exact_second_moment": ref.second_moment.tolist(),
        "exact_covariance": ref.covariance.tolist(),
        "covariance_trace": float(np.trace(ref.covariance)),
        "covariance_offdiag_rms": _offdiag_rms(ref.covariance),
        "covariance_min_eigenvalue": float(np.min(cov_eigs)),
        "covariance_max_eigenvalue": float(np.max(cov_eigs)),
        "flux_sum": ref.flux_sum.tolist(),
        "flux_gram": ref.flux_gram.tolist(),
        "flux_gram_trace": float(np.trace(ref.flux_gram)),
        "flux_mean": ref.flux_mean.tolist(),
        "flux_vs_sector_mean_max_abs": float(np.max(np.abs(flux_delta))),
        "identity_projector": {
            "bias_max_abs": float(np.max(np.abs(identity["bias"]))),
            "remainder_mse_total": float(identity["remainder_mse_total"]),
            "flux_energy_residual": float(identity["flux_energy_residual"]),
        },
        "zero_projector": {
            "second_moment_reconstruction_max_abs": float(
                np.max(np.abs(zero_second_delta))
            ),
            "remainder_mse_total": float(zero["remainder_mse_total"]),
            "exact_second_moment_trace": float(np.trace(ref.second_moment)),
        },
        "oracle_flux_capacity_reference_only": oracle,
    }
    return record, replay_arrays


def _max_array_delta(a: list[np.ndarray], b: list[np.ndarray]) -> float:
    if len(a) != len(b):
        return math.inf
    delta = 0.0
    for x, y in zip(a, b):
        xa = np.asarray(x, dtype=np.float64)
        ya = np.asarray(y, dtype=np.float64)
        if xa.shape != ya.shape:
            return math.inf
        if xa.size:
            delta = max(delta, float(np.max(np.abs(xa - ya))))
    return delta


def main() -> None:
    first_records = []
    second_records = []
    replay_deltas = []

    for seed in SEEDS:
        first, first_arrays = _run_seed(seed)
        second, second_arrays = _run_seed(seed)
        first_records.append(first)
        second_records.append(second)
        replay_deltas.append(_max_array_delta(first_arrays, second_arrays))

    # Pooled reference-only capacity summaries. These do not select a mechanism.
    pooled = {}
    for rank in ORACLE_RANKS:
        key = str(rank)
        remainder_num = sum(
            r["oracle_flux_capacity_reference_only"][key]["remainder_mse_total"]
            for r in first_records
        )
        remainder_den = sum(
            float(np.trace(np.asarray(r["exact_second_moment"], dtype=np.float64)))
            for r in first_records
        )
        flux_num = sum(
            r["oracle_flux_capacity_reference_only"][key]["flux_energy_residual"]
            for r in first_records
        )
        flux_den = sum(r["flux_gram_trace"] for r in first_records)
        pooled[key] = {
            "rank": rank,
            "pooled_relative_output_remainder_mse": (
                remainder_num / remainder_den if remainder_den > 0.0 else 0.0
            ),
            "pooled_relative_flux_energy_remainder": (
                flux_num / flux_den if flux_den > 0.0 else 0.0
            ),
            "max_network_bias_mse_across_outputs": max(
                r["oracle_flux_capacity_reference_only"][key][
                    "bias_mse_across_outputs"
                ]
                for r in first_records
            ),
            "max_network_bias_max_abs": max(
                r["oracle_flux_capacity_reference_only"][key]["bias_max_abs"]
                for r in first_records
            ),
            "max_network_cross_covariance_fro": max(
                r["oracle_flux_capacity_reference_only"][key][
                    "cross_covariance_fro"
                ]
                for r in first_records
            ),
            "max_observable_residual_mse": max(
                obs["residual_mse"]
                for r in first_records
                for obs in r["oracle_flux_capacity_reference_only"][key][
                    "per_observable"
                ]
            ),
        }

    all_partition_ok = all(
        r["partition"]["ordered"]
        and r["partition"]["complete"]
        and r["partition"]["finite"]
        and r["partition"]["max_gap"] <= 1e-11
        and r["partition"]["max_overlap"] <= 1e-11
        for r in first_records
    )
    all_finite = all(
        np.isfinite(np.asarray(r["exact_mean"], dtype=np.float64)).all()
        and np.isfinite(np.asarray(r["exact_covariance"], dtype=np.float64)).all()
        and np.isfinite(np.asarray(r["flux_gram"], dtype=np.float64)).all()
        for r in first_records
    )
    max_flux_mean_delta = max(r["flux_vs_sector_mean_max_abs"] for r in first_records)
    max_cov_sym = max(
        float(
            np.max(
                np.abs(
                    np.asarray(r["exact_covariance"], dtype=np.float64)
                    - np.asarray(r["exact_covariance"], dtype=np.float64).T
                )
            )
        )
        for r in first_records
    )
    min_cov_eig = min(r["covariance_min_eigenvalue"] for r in first_records)
    identity_max = max(
        max(
            r["identity_projector"]["bias_max_abs"],
            abs(r["identity_projector"]["remainder_mse_total"]),
            abs(r["identity_projector"]["flux_energy_residual"]),
        )
        for r in first_records
    )
    zero_reconstruct_max = max(
        r["zero_projector"]["second_moment_reconstruction_max_abs"]
        for r in first_records
    )
    projector_sym_max = max(
        r["oracle_flux_capacity_reference_only"][str(k)][
            "projector_symmetry_max_abs"
        ]
        for r in first_records
        for k in ORACLE_RANKS
    )
    projector_idem_max = max(
        r["oracle_flux_capacity_reference_only"][str(k)][
            "projector_idempotence_max_abs"
        ]
        for r in first_records
        for k in ORACLE_RANKS
    )

    monotone = True
    for r in first_records:
        flux_vals = [
            r["oracle_flux_capacity_reference_only"][str(k)][
                "relative_flux_energy_residual"
            ]
            for k in ORACLE_RANKS
        ]
        output_vals = [
            r["oracle_flux_capacity_reference_only"][str(k)][
                "relative_remainder_mse"
            ]
            for k in ORACLE_RANKS
        ]
        monotone = monotone and all(
            flux_vals[i + 1] <= flux_vals[i] + 1e-12
            for i in range(len(flux_vals) - 1)
        )
        monotone = monotone and all(
            output_vals[i + 1] <= output_vals[i] + 1e-12
            for i in range(len(output_vals) - 1)
        )

    deterministic_max_abs = max(replay_deltas)

    gates = {
        "all_numeric_reference_finite": all_finite,
        "partition_complete_ordered": all_partition_ok,
        "flux_vs_sector_mean_max_abs_le_1e_10": max_flux_mean_delta <= 1e-10,
        "covariance_symmetry_max_abs_le_1e_12": max_cov_sym <= 1e-12,
        "covariance_min_eigenvalue_ge_minus_1e_10": min_cov_eig >= -1e-10,
        "identity_projector_zero_remainder_le_1e_12": identity_max <= 1e-12,
        "zero_projector_second_moment_reconstruction_le_1e_12": (
            zero_reconstruct_max <= 1e-12
        ),
        "oracle_projector_symmetry_le_1e_12": projector_sym_max <= 1e-12,
        "oracle_projector_idempotence_le_1e_12": projector_idem_max <= 1e-12,
        "oracle_remainders_nonincreasing_with_rank": monotone,
        "deterministic_replay_max_abs_eq_0": deterministic_max_abs == 0.0,
        "no_targets_public_scorer_holdout_full": True,
    }
    passed = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e114.exact_reference_output_compression.v1",
        "experiment": "E114",
        "tracking_key": "ARC-E114-EXACT-REFERENCE-OUTPUT-COMPRESSION-20260919",
        "identity": "reference-only extension of E114 activation-boundary flux",
        "fixture": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seeds": list(SEEDS),
            "weight_law": "iid He-normal float64, zero bias",
            "monte_carlo": False,
            "numerical_quadrature": False,
        },
        "measurements": first_records,
        "pooled_oracle_capacity_reference_only": pooled,
        "instrument_summary": {
            "network_count": len(first_records),
            "max_flux_vs_sector_mean_abs": max_flux_mean_delta,
            "max_covariance_symmetry_abs": max_cov_sym,
            "min_covariance_eigenvalue": min_cov_eig,
            "max_identity_remainder_abs": identity_max,
            "max_zero_projector_reconstruction_abs": zero_reconstruct_max,
            "max_oracle_projector_symmetry_abs": projector_sym_max,
            "max_oracle_projector_idempotence_abs": projector_idem_max,
            "deterministic_replay_max_abs": deterministic_max_abs,
            "final_sector_counts": [r["final_sector_count"] for r in first_records],
            "boundary_counts": [r["boundary_count"] for r in first_records],
            "covariance_offdiag_rms": [
                r["covariance_offdiag_rms"] for r in first_records
            ],
        },
        "gates": gates,
        "reference_harness_verified": passed,
        "decision": (
            "E114_EXACT_REFERENCE_HARNESS_VERIFIED"
            if passed
            else "REFERENCE_INSTRUMENT_NO_GO"
        ),
        "scope": {
            "new_compression_mechanism": False,
            "oracle_capacity_is_reference_only": True,
            "production_run": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E114_EXACT_REFERENCE=" + json.dumps(result, sort_keys=True), flush=True)
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
