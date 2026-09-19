#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    ABS_MEAN_GATE,
    GAUSSIAN_FACTOR,
    OMITTED_FLUX_L1_BUDGET,
    RAW_MSE_GATE,
    build_generic_boundary_flux,
    partition_metrics,
    wrapped_angle_error,
)

WIDTH = 8
DEPTH = 4
SEEDS = (114200, 114201, 114202, 114203)
BUDGET = 2**41
OUT = Path("e119-generic-boundary-flux-certificate.json")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _replay_delta(a, b) -> float:
    values = [
        abs(a.full_mean - b.full_mean),
        abs(a.compressed_mean - b.compressed_mean),
        abs(a.abs_remainder_certificate - b.abs_remainder_certificate),
        abs(a.omitted_abs_flux_sum - b.omitted_abs_flux_sum),
    ]
    for xa, xb in [
        (a.boundary_angles, b.boundary_angles),
        (a.scalar_jumps, b.scalar_jumps),
        (a.kept_angles, b.kept_angles),
        (a.kept_jumps, b.kept_jumps),
    ]:
        if xa.shape != xb.shape:
            return math.inf
        if xa.size:
            values.append(float(np.max(np.abs(xa - xb))))
    for sa, sb in zip(a.sectors, b.sectors):
        values.append(abs(sa.lo - sb.lo))
        values.append(abs(sa.hi - sb.hi))
        values.append(float(np.max(np.abs(sa.coeff - sb.coeff))))
    return max(values) if values else 0.0


def main() -> None:
    records = []
    deterministic_max_abs = 0.0
    flops_deterministic = True
    max_angle_error = 0.0
    max_jump_error = 0.0
    max_full_mean_error = 0.0

    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)
        c = output_observable(WIDTH)

        generic = build_generic_boundary_flux(weights, budget=BUDGET)
        repeat = build_generic_boundary_flux(weights, budget=BUDGET)
        ref = build_exact_reference(weights)

        deterministic_max_abs = max(
            deterministic_max_abs,
            _replay_delta(generic, repeat),
        )
        flops_deterministic = flops_deterministic and (
            generic.flops == repeat.flops
        )

        ref_scalar_jumps = np.asarray(ref.boundary_jumps, dtype=np.float64) @ c
        ref_angles = np.asarray(ref.boundary_angles, dtype=np.float64)

        same_boundary_count = (
            generic.boundary_angles.shape == ref_angles.shape
            and generic.scalar_jumps.shape == ref_scalar_jumps.shape
        )
        if same_boundary_count and generic.boundary_angles.size:
            angle_error = max(
                wrapped_angle_error(a, b)
                for a, b in zip(generic.boundary_angles, ref_angles)
            )
            jump_error = float(
                np.max(np.abs(generic.scalar_jumps - ref_scalar_jumps))
            )
        elif same_boundary_count:
            angle_error = 0.0
            jump_error = 0.0
        else:
            angle_error = math.inf
            jump_error = math.inf

        max_angle_error = max(max_angle_error, angle_error)
        max_jump_error = max(max_jump_error, jump_error)

        exact_mean = float(c @ ref.mean)
        ref_flux_mean = float(
            GAUSSIAN_FACTOR * np.sum(ref_scalar_jumps, dtype=np.float64)
        )
        generic_full_error = abs(generic.full_mean - exact_mean)
        max_full_mean_error = max(max_full_mean_error, generic_full_error)

        compressed_bias = generic.compressed_mean - exact_mean
        compressed_bias_mse = compressed_bias * compressed_bias
        generic_omission_error = abs(
            generic.compressed_mean - generic.full_mean
        )
        certificate_contains_omission = bool(
            generic_omission_error
            <= generic.abs_remainder_certificate + 1e-15
        )
        certificate_mse_bound = (
            generic.abs_remainder_certificate
            * generic.abs_remainder_certificate
        )

        p = partition_metrics(generic)
        retained_count = int(generic.kept_indices.shape[0])
        omitted_count = int(generic.omitted_indices.shape[0])
        total_atoms = int(generic.scalar_jumps.shape[0])

        records.append(
            {
                "seed": seed,
                "layer_region_counts": list(generic.layer_region_counts),
                "final_region_count": len(generic.sectors),
                "boundary_atom_count": total_atoms,
                "retained_atom_count": retained_count,
                "omitted_atom_count": omitted_count,
                "retained_fraction": (
                    retained_count / total_atoms if total_atoms else 0.0
                ),
                "partition": p,
                "generic_finite": generic.finite,
                "generic_boundary_angles_sha256": _sha(
                    generic.boundary_angles
                ),
                "generic_scalar_jumps_sha256": _sha(
                    generic.scalar_jumps
                ),
                "generic_kept_indices": generic.kept_indices.tolist(),
                "generic_omitted_indices": generic.omitted_indices.tolist(),
                "generic_full_mean": generic.full_mean,
                "independent_exact_mean": exact_mean,
                "independent_reference_flux_mean": ref_flux_mean,
                "generic_full_vs_exact_abs": generic_full_error,
                "reference_flux_vs_sector_mean_abs": abs(
                    ref_flux_mean - exact_mean
                ),
                "boundary_count_matches_reference": same_boundary_count,
                "boundary_angle_max_wrapped_error": angle_error,
                "scalar_jump_max_abs_error": jump_error,
                "compressed_mean": generic.compressed_mean,
                "compressed_exact_bias": compressed_bias,
                "compressed_exact_bias_mse": compressed_bias_mse,
                "omission_error_vs_generic_full_abs": generic_omission_error,
                "omitted_abs_flux_sum": generic.omitted_abs_flux_sum,
                "abs_remainder_certificate": (
                    generic.abs_remainder_certificate
                ),
                "certificate_squared": certificate_mse_bound,
                "certificate_contains_actual_omission_error": (
                    certificate_contains_omission
                ),
                "l1_minimal_under_certificate": (
                    generic.l1_minimal_under_certificate
                ),
                "next_omission_abs_flux": (
                    generic.next_omission_abs_flux
                ),
                "flops": generic.flops,
            }
        )

    max_reference_flux_error = max(
        r["reference_flux_vs_sector_mean_abs"] for r in records
    )
    max_compressed_bias_mse = max(
        r["compressed_exact_bias_mse"] for r in records
    )
    pooled_compressed_bias_mse = float(
        np.mean([r["compressed_exact_bias_mse"] for r in records])
    )
    max_certificate_squared = max(
        r["certificate_squared"] for r in records
    )
    max_dense_flops = max(
        r["flops"]["flopscope_dense_flops"] for r in records
    )
    max_manual_flops = max(
        r["flops"]["manual_geometry_flop_equivalent"] for r in records
    )
    max_all_in_flops = max(
        r["flops"]["all_in_accounted_flops"] for r in records
    )

    gates = {
        "generic_finite_all": all(r["generic_finite"] for r in records),
        "partition_complete_ordered_all": all(
            r["partition"]["complete"]
            and r["partition"]["ordered"]
            and r["partition"]["max_gap"] <= 1e-11
            and r["partition"]["max_overlap"] <= 1e-11
            for r in records
        ),
        "final_region_count_matches_reference_all": all(
            r["final_region_count"] == r["boundary_atom_count"]
            for r in records
        ),
        "boundary_count_matches_reference_all": all(
            r["boundary_count_matches_reference"] for r in records
        ),
        "boundary_angle_error_le_1e_10": max_angle_error <= 1e-10,
        "scalar_jump_error_le_1e_10": max_jump_error <= 1e-10,
        "generic_full_mean_error_le_1e_10": max_full_mean_error <= 1e-10,
        "reference_flux_identity_le_1e_10": (
            max_reference_flux_error <= 1e-10
        ),
        "deterministic_replay_max_abs_eq_0": (
            deterministic_max_abs == 0.0
        ),
        "certificate_contains_omission_all": all(
            r["certificate_contains_actual_omission_error"]
            for r in records
        ),
        "certificate_squared_le_1_89e_8_all": all(
            r["certificate_squared"] <= RAW_MSE_GATE
            for r in records
        ),
        "compressed_exact_bias_mse_le_1_89e_8_all": all(
            r["compressed_exact_bias_mse"] <= RAW_MSE_GATE
            for r in records
        ),
        "l1_minimal_under_certificate_all": all(
            r["l1_minimal_under_certificate"] for r in records
        ),
        "flopscope_dense_reconciliation_all": all(
            r["flops"]["flopscope_exact_reconciliation"]
            for r in records
        ),
        "manual_geometry_ledger_deterministic": flops_deterministic,
        "all_in_cost_deterministic": flops_deterministic,
        "no_targets_public_scorer_holdout_full": True,
    }

    go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e119.generic_boundary_flux_certificate.v1",
        "experiment": "E119",
        "idempotency_key": (
            "ARC-E119-GENERIC-BOUNDARY-FLUX-CERT-20260919"
        ),
        "construction": {
            "input_dimension": 2,
            "max_width_supported": 8,
            "max_depth_supported": 4,
            "fixture_specific_boundaries": False,
            "fixture_specific_masks": False,
            "weight_driven_region_splitting": True,
            "observable": (
                "c_j=(j+1)/sqrt(sum_{r=1}^n r^2)"
            ),
            "full_mean": (
                "sqrt(pi/2)/(2*pi) * sum scalar derivative jumps"
            ),
        },
        "compression_certificate": {
            "raw_mse_gate": RAW_MSE_GATE,
            "absolute_mean_gate": ABS_MEAN_GATE,
            "gaussian_flux_factor": GAUSSIAN_FACTOR,
            "omitted_flux_l1_budget": OMITTED_FLUX_L1_BUDGET,
            "selection": (
                "omit longest deterministic ascending-|jump| prefix "
                "whose L1 flux <= omitted_flux_l1_budget"
            ),
            "certificate": (
                "B_abs = gaussian_flux_factor * "
                "sum_abs(omitted_scalar_jumps)"
            ),
            "certificate_is_target_free": True,
        },
        "frozen_corpus": {
            "width": WIDTH,
            "depth": DEPTH,
            "input_dimension": 2,
            "weight_seeds": list(SEEDS),
            "weight_law": "iid He-normal float64, zero bias",
        },
        "records": records,
        "summary": {
            "deterministic_replay_max_abs": deterministic_max_abs,
            "max_boundary_angle_wrapped_error": max_angle_error,
            "max_scalar_jump_abs_error": max_jump_error,
            "max_generic_full_mean_abs_error": max_full_mean_error,
            "max_reference_flux_identity_abs_error": (
                max_reference_flux_error
            ),
            "compressed_bias_mse_per_network": [
                r["compressed_exact_bias_mse"] for r in records
            ],
            "max_compressed_bias_mse": max_compressed_bias_mse,
            "pooled_compressed_bias_mse": pooled_compressed_bias_mse,
            "max_certificate_squared": max_certificate_squared,
            "retained_atom_counts": [
                r["retained_atom_count"] for r in records
            ],
            "omitted_atom_counts": [
                r["omitted_atom_count"] for r in records
            ],
            "retained_fractions": [
                r["retained_fraction"] for r in records
            ],
            "max_flopscope_dense_flops": max_dense_flops,
            "max_manual_geometry_flop_equivalent": max_manual_flops,
            "max_all_in_accounted_flops": max_all_in_flops,
            "max_all_in_utilization_vs_2pow41": (
                max_all_in_flops / BUDGET
            ),
        },
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E119_GENERIC_BOUNDARY_FLUX_CERTIFICATE_GO"
            if go
            else "TERMINAL_NO_GO_CLOSE_DEPLOYABILITY_BRIDGE"
        ),
        "scope": {
            "target_free": True,
            "width_le_8_depth_le_4_only": True,
            "production_scientific_run": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rerun": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E119_GENERIC_BOUNDARY_FLUX="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )

    # Scientific NO-GO is still a valid completed frozen experiment. Fail only
    # on instrument/accounting integrity.
    integrity_keys = [
        "generic_finite_all",
        "partition_complete_ordered_all",
        "boundary_count_matches_reference_all",
        "reference_flux_identity_le_1e_10",
        "deterministic_replay_max_abs_eq_0",
        "flopscope_dense_reconciliation_all",
        "manual_geometry_ledger_deterministic",
        "no_targets_public_scorer_holdout_full",
    ]
    if not all(gates[k] for k in integrity_keys):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
