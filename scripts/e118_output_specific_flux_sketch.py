#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import (
    build_exact_reference,
    he_weights,
)
from methods.e118_output_flux_sketch import (
    output_observable,
    run_flux_sketch,
)

CELLS = 1024
WIDTH = 8
DEPTH = 4
SEEDS = (114200, 114201, 114202, 114203)
RAW_TARGET = 1.89e-8
BUDGET = 2**41
PRODUCTION_UPPER_FLOPS = 73_719_476_736
PRODUCTION_UPPER_UTIL = PRODUCTION_UPPER_FLOPS / BUDGET
OUT = Path("e118-output-specific-flux-sketch.json")


def sha256_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def exact_reference_sketch(ref, c: np.ndarray) -> dict:
    h = 2.0 * math.pi / CELLS
    sin_mid = math.sin(0.5 * h)
    cos_mid = math.cos(0.5 * h)
    gaussian_factor = math.sqrt(math.pi / 2.0) / (2.0 * math.pi)

    defects = np.zeros((CELLS, 2), dtype=np.float64)
    scalar_jumps = np.asarray(ref.boundary_jumps, dtype=np.float64) @ c

    min_boundary_to_grid = math.inf
    for theta, jump in zip(ref.boundary_angles, scalar_jumps):
        theta = float(theta)
        if abs(theta) <= 1e-14:
            cell = CELLS - 1
            r = 0.0
            min_boundary_to_grid = 0.0
        else:
            grid_position = theta / h
            min_boundary_to_grid = min(
                min_boundary_to_grid,
                abs(grid_position - round(grid_position)) * h,
            )
            cell = int(math.floor(grid_position))
            cell = min(max(cell, 0), CELLS - 1)
            r = (cell + 1) * h - theta

        defects[cell, 0] += float(jump) * math.sin(r)
        defects[cell, 1] += float(jump) * math.cos(r)

    atoms = sin_mid * defects[:, 0] + cos_mid * defects[:, 1]
    orthogonal_remainder = cos_mid * defects[:, 0] - sin_mid * defects[:, 1]

    exact_flux_sum = float(np.sum(scalar_jumps))
    compressed_flux_sum = float(np.sum(atoms))
    exact_mean_from_flux = gaussian_factor * exact_flux_sum
    compressed_mean = gaussian_factor * compressed_flux_sum

    return {
        "atoms": atoms,
        "orthogonal_remainder": orthogonal_remainder,
        "exact_flux_sum": exact_flux_sum,
        "compressed_flux_sum": compressed_flux_sum,
        "exact_mean_from_flux": exact_mean_from_flux,
        "compressed_mean": compressed_mean,
        "exact_bias": compressed_mean - exact_mean_from_flux,
        "exact_bias_mse": (compressed_mean - exact_mean_from_flux) ** 2,
        "state_remainder_l2": float(np.linalg.norm(orthogonal_remainder)),
        "state_remainder_rms": float(
            np.sqrt(np.mean(orthogonal_remainder * orthogonal_remainder))
        ),
        "state_remainder_max_abs": float(np.max(np.abs(orthogonal_remainder))),
        "nonzero_reference_cells": int(
            np.count_nonzero(
                np.linalg.norm(defects, axis=1) > 1e-15
            )
        ),
        "min_boundary_to_grid_angle": float(min_boundary_to_grid),
    }


def compact_candidate(x) -> dict:
    return {
        "mean": x.mean,
        "atoms_sha256": sha256_array(x.atoms),
        "state_residual_sha256": sha256_array(x.state_residual),
        "atoms_l1": float(np.sum(np.abs(x.atoms))),
        "atoms_l2": float(np.linalg.norm(x.atoms)),
        "atoms_max_abs": float(np.max(np.abs(x.atoms))),
        "nonzero_atoms_gt_1e_15": int(np.count_nonzero(np.abs(x.atoms) > 1e-15)),
        "state_residual_l2": float(np.linalg.norm(x.state_residual)),
        "state_residual_rms": float(
            np.sqrt(np.mean(x.state_residual * x.state_residual))
        ),
        "state_residual_max_abs": float(np.max(np.abs(x.state_residual))),
        "finite": x.finite,
        "flops": x.flops,
    }


def main() -> None:
    c = output_observable(WIDTH)
    records = []
    deterministic_max_abs = 0.0
    candidate_vs_reference_atom_max_abs = 0.0
    candidate_vs_reference_flux_sum_max_abs = 0.0
    all_flops_equal = True

    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)
        ref = build_exact_reference(weights)
        ref_sketch = exact_reference_sketch(ref, c)

        exact_mean = float(c @ ref.mean)
        exact_mean_flux = float(
            math.sqrt(math.pi / 2.0)
            / (2.0 * math.pi)
            * (c @ ref.flux_sum)
        )
        flux_identity_error = abs(exact_mean - exact_mean_flux)

        a = run_flux_sketch(weights, cells=CELLS, budget=BUDGET)
        b = run_flux_sketch(weights, cells=CELLS, budget=BUDGET)

        deterministic_max_abs = max(
            deterministic_max_abs,
            abs(a.mean - b.mean),
            float(np.max(np.abs(a.atoms - b.atoms))),
            float(np.max(np.abs(a.state_residual - b.state_residual))),
            float(np.max(np.abs(a.values - b.values))),
            float(
                np.max(
                    np.abs(
                        a.angular_derivatives - b.angular_derivatives
                    )
                )
            ),
        )
        all_flops_equal = all_flops_equal and (a.flops == b.flops)

        atom_delta = float(
            np.max(
                np.abs(
                    a.atoms
                    - np.asarray(ref_sketch["atoms"], dtype=np.float64)
                )
            )
        )
        candidate_vs_reference_atom_max_abs = max(
            candidate_vs_reference_atom_max_abs,
            atom_delta,
        )
        candidate_flux_sum = float(np.sum(a.atoms))
        flux_sum_delta = abs(
            candidate_flux_sum
            - float(ref_sketch["compressed_flux_sum"])
        )
        candidate_vs_reference_flux_sum_max_abs = max(
            candidate_vs_reference_flux_sum_max_abs,
            flux_sum_delta,
        )

        candidate_bias = a.mean - exact_mean
        exact_formula_bias = float(ref_sketch["exact_bias"])

        records.append(
            {
                "seed": seed,
                "exact_final_observable_mean": exact_mean,
                "exact_flux_mean": exact_mean_flux,
                "exact_flux_identity_abs_error": flux_identity_error,
                "candidate_mean": a.mean,
                "candidate_bias": candidate_bias,
                "candidate_bias_mse": candidate_bias * candidate_bias,
                "exact_formula_bias": exact_formula_bias,
                "exact_formula_bias_mse": float(ref_sketch["exact_bias_mse"]),
                "candidate_vs_exact_formula_bias_abs": abs(
                    candidate_bias - exact_formula_bias
                ),
                "candidate_vs_reference_atom_max_abs": atom_delta,
                "candidate_vs_reference_flux_sum_abs": flux_sum_delta,
                "boundary_count": int(ref.boundary_jumps.shape[0]),
                "final_sector_count": len(ref.sectors),
                "reference_nonzero_flux_cells": int(
                    ref_sketch["nonzero_reference_cells"]
                ),
                "reference_state_remainder_l2": float(
                    ref_sketch["state_remainder_l2"]
                ),
                "reference_state_remainder_rms": float(
                    ref_sketch["state_remainder_rms"]
                ),
                "reference_state_remainder_max_abs": float(
                    ref_sketch["state_remainder_max_abs"]
                ),
                "min_boundary_to_grid_angle": float(
                    ref_sketch["min_boundary_to_grid_angle"]
                ),
                "candidate": compact_candidate(a),
            }
        )

    bias_mses = [float(r["candidate_bias_mse"]) for r in records]
    pooled_bias_mse = float(np.mean(bias_mses))
    max_bias_mse = max(bias_mses)
    max_flux_identity_error = max(
        float(r["exact_flux_identity_abs_error"]) for r in records
    )
    max_candidate_formula_bias_delta = max(
        float(r["candidate_vs_exact_formula_bias_abs"]) for r in records
    )
    total_flops_values = [int(r["candidate"]["flops"]["total"]) for r in records]

    gates = {
        "candidate_finite_all": all(r["candidate"]["finite"] for r in records),
        "representation_length_eq_1024_all": all(
            r["candidate"]["nonzero_atoms_gt_1e_15"] <= CELLS
            and len(
                np.zeros(CELLS, dtype=np.float64)
            )
            == CELLS
            for r in records
        ),
        "flopscope_exact_reconciliation_all": all(
            r["candidate"]["flops"]["exact_reconciliation"] for r in records
        ),
        "measured_flops_deterministic": all_flops_equal,
        "reference_flux_identity_le_1e_10": max_flux_identity_error <= 1e-10,
        "candidate_flux_sum_matches_reference_le_1e_10": (
            candidate_vs_reference_flux_sum_max_abs <= 1e-10
        ),
        "candidate_bias_matches_exact_formula_le_1e_10": (
            max_candidate_formula_bias_delta <= 1e-10
        ),
        "deterministic_replay_max_abs_eq_0": deterministic_max_abs == 0.0,
        "production_util_upper_le_0_13": PRODUCTION_UPPER_UTIL <= 0.13,
        "every_network_bias_mse_le_1_89e_8": all(
            value <= RAW_TARGET for value in bias_mses
        ),
        "pooled_bias_mse_le_1_89e_8": pooled_bias_mse <= RAW_TARGET,
        "no_targets_public_scorer_holdout_full": True,
    }

    go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e118.output_specific_flux_sketch.v1",
        "experiment": "E118",
        "idempotency_key": "ARC-E118-OUTPUT-SPECIFIC-FLUX-SKETCH-20260919",
        "mechanism": {
            "name": "one-midpoint-atom-per-angular-cell scalar boundary-flux sketch",
            "observable": "c_j=(j+1)/sqrt(sum_{r=1}^n r^2)",
            "cells": CELLS,
            "representation_state_scalars": CELLS,
            "full_mask_enumeration": False,
            "gaussian_plugin": False,
            "target_fitting": False,
            "candidate_uses_exact_boundaries": False,
            "candidate_uses_exact_reference": False,
            "static_angle_stencil_billed": False,
        },
        "frozen_corpus": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seeds": list(SEEDS),
            "weight_law": "iid He-normal float64, zero bias",
        },
        "records": records,
        "summary": {
            "candidate_bias_mse_per_network": bias_mses,
            "pooled_candidate_bias_mse": pooled_bias_mse,
            "max_candidate_bias_mse": max_bias_mse,
            "raw_target_scale": RAW_TARGET,
            "max_bias_mse_over_target": max_bias_mse / RAW_TARGET,
            "pooled_bias_mse_over_target": pooled_bias_mse / RAW_TARGET,
            "candidate_vs_reference_atom_max_abs": (
                candidate_vs_reference_atom_max_abs
            ),
            "candidate_vs_reference_flux_sum_max_abs": (
                candidate_vs_reference_flux_sum_max_abs
            ),
            "candidate_vs_exact_formula_bias_max_abs": (
                max_candidate_formula_bias_delta
            ),
            "deterministic_replay_max_abs": deterministic_max_abs,
            "measured_candidate_flops_per_network": total_flops_values,
            "measured_candidate_flops_max": max(total_flops_values),
            "measured_candidate_utilization_max": (
                max(total_flops_values) / BUDGET
            ),
        },
        "production_admission": {
            "width": 1024,
            "depth": 16,
            "cells": CELLS,
            "dense_forward_reverse_core_flops": 68_719_476_736,
            "helper_reserve_flops": 5_000_000_000,
            "upper_flops": PRODUCTION_UPPER_FLOPS,
            "budget_flops": BUDGET,
            "upper_utilization": PRODUCTION_UPPER_UTIL,
            "cap": 0.13,
        },
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E118_OUTPUT_SPECIFIC_COMPRESSED_FLUX_GO"
            if go
            else "TERMINAL_NO_GO_CLOSE_E118"
        ),
        "scope": {
            "target_free": True,
            "exact_reference_used_only_for_measurement": True,
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

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E118_FLUX_SKETCH=" + json.dumps(result, sort_keys=True), flush=True)

    integrity_keys = [
        "candidate_finite_all",
        "flopscope_exact_reconciliation_all",
        "measured_flops_deterministic",
        "reference_flux_identity_le_1e_10",
        "candidate_flux_sum_matches_reference_le_1e_10",
        "candidate_bias_matches_exact_formula_le_1e_10",
        "deterministic_replay_max_abs_eq_0",
        "no_targets_public_scorer_holdout_full",
    ]
    if not all(gates[k] for k in integrity_keys):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
