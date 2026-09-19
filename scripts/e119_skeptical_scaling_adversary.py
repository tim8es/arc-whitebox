#!/usr/bin/env python3
"""E119 skeptical scaling adversary against absolute-L1 boundary compression."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    OMITTED_FLUX_L1_BUDGET,
    RAW_MSE_GATE,
    build_generic_boundary_flux,
    wrapped_angle_error,
)

SCALE = 8.0
NONZERO_TOL = 1e-12
ANGLE_TOL = 1e-10
REL_TOL = 1e-10

CASES = (
    {"name": "A", "width": 4, "depth": 3, "seed": 119401},
    {"name": "B", "width": 6, "depth": 4, "seed": 119601},
    {"name": "C", "width": 8, "depth": 4, "seed": 119801},
)


def _max_wrapped_angle_error(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return math.inf
    if a.size == 0:
        return 0.0
    return max(wrapped_angle_error(float(x), float(y)) for x, y in zip(a, b))


def _scaled_tol(scale: float) -> float:
    return 1e-9 * max(1.0, float(scale))


def _case(case: dict[str, int | str]) -> dict[str, object]:
    width = int(case["width"])
    depth = int(case["depth"])
    seed = int(case["seed"])

    base_weights = he_weights(seed, width=width, depth=depth, input_dim=2)
    scaled_weights = [SCALE * np.asarray(w, dtype=np.float64) for w in base_weights]

    dense = all(
        bool(np.isfinite(w).all()) and bool(np.count_nonzero(w) == w.size)
        for w in scaled_weights
    )

    base = build_generic_boundary_flux(base_weights)
    scaled = build_generic_boundary_flux(scaled_weights)
    reference = build_exact_reference(scaled_weights)
    observable = output_observable(width)
    ref_scalar_jumps = np.asarray(reference.boundary_jumps @ observable, dtype=np.float64)
    ref_mean = float(observable @ reference.mean)

    scale_total = SCALE**depth

    generic_ref_count_match = len(scaled.sectors) == len(reference.sectors)
    boundary_shape_match = (
        scaled.boundary_angles.shape == reference.boundary_angles.shape
        and scaled.scalar_jumps.shape == ref_scalar_jumps.shape
    )

    angle_ref_error = (
        _max_wrapped_angle_error(scaled.boundary_angles, reference.boundary_angles)
        if boundary_shape_match
        else math.inf
    )
    jump_ref_error = (
        float(np.max(np.abs(scaled.scalar_jumps - ref_scalar_jumps)))
        if boundary_shape_match and scaled.scalar_jumps.size
        else (0.0 if boundary_shape_match else math.inf)
    )
    max_abs_jump = (
        float(np.max(np.abs(ref_scalar_jumps))) if ref_scalar_jumps.size else 0.0
    )
    jump_ref_tol = _scaled_tol(max_abs_jump)
    mean_ref_error = abs(float(scaled.full_mean) - ref_mean)
    mean_ref_tol = _scaled_tol(abs(ref_mean))

    base_scaled_shape_match = (
        base.boundary_angles.shape == scaled.boundary_angles.shape
        and base.scalar_jumps.shape == scaled.scalar_jumps.shape
    )
    angle_scale_error = (
        _max_wrapped_angle_error(base.boundary_angles, scaled.boundary_angles)
        if base_scaled_shape_match
        else math.inf
    )

    expected_scaled_jumps = scale_total * base.scalar_jumps
    scaling_abs_error = (
        float(np.max(np.abs(scaled.scalar_jumps - expected_scaled_jumps)))
        if base_scaled_shape_match and scaled.scalar_jumps.size
        else (0.0 if base_scaled_shape_match else math.inf)
    )
    scaling_rel_error = (
        scaling_abs_error / max(1.0, float(np.max(np.abs(expected_scaled_jumps))))
        if base_scaled_shape_match
        else math.inf
    )

    nonzero = np.abs(scaled.scalar_jumps) > NONZERO_TOL
    nonzero_indices = set(np.flatnonzero(nonzero).astype(int).tolist())
    omitted_indices = set(np.asarray(scaled.omitted_indices, dtype=np.int64).astype(int).tolist())
    omitted_nonzero_indices = sorted(nonzero_indices & omitted_indices)

    nonzero_count = int(np.count_nonzero(nonzero))
    zero_count = int(scaled.scalar_jumps.size - nonzero_count)
    min_nonzero_abs_jump = (
        float(np.min(np.abs(scaled.scalar_jumps[nonzero]))) if nonzero_count else math.inf
    )
    retained_nonzero_count = nonzero_count - len(omitted_nonzero_indices)
    retained_nonzero_fraction = (
        retained_nonzero_count / nonzero_count if nonzero_count else 1.0
    )
    compressed_bias = float(scaled.compressed_mean - scaled.full_mean)

    exact_gates = {
        "dense_finite_weights": dense,
        "generic_final_region_count_matches_reference": generic_ref_count_match,
        "generic_boundary_shape_matches_reference": boundary_shape_match,
        "generic_boundary_angle_error_le_1e_10": angle_ref_error <= ANGLE_TOL,
        "generic_jump_matches_reference": jump_ref_error <= jump_ref_tol,
        "generic_mean_matches_reference": mean_ref_error <= mean_ref_tol,
        "base_scaled_boundary_shape_match": base_scaled_shape_match,
        "base_scaled_region_count_identical": len(base.sectors) == len(scaled.sectors),
        "base_scaled_boundary_angles_identical": angle_scale_error <= ANGLE_TOL,
        "jump_scaling_relative_error_le_1e_10": scaling_rel_error <= REL_TOL,
        "certificate_squared_within_gate": (
            scaled.abs_remainder_certificate * scaled.abs_remainder_certificate
            <= RAW_MSE_GATE + 1e-30
        ),
        "actual_compressed_bias_within_certificate": (
            abs(compressed_bias) <= scaled.abs_remainder_certificate + 1e-12
        ),
    }

    adversary_success = bool(
        nonzero_count > 0
        and len(omitted_nonzero_indices) == 0
        and min_nonzero_abs_jump > OMITTED_FLUX_L1_BUDGET
    )

    return {
        **case,
        "scale_per_layer": SCALE,
        "scale_total": scale_total,
        "base_layer_region_counts": list(base.layer_region_counts),
        "scaled_layer_region_counts": list(scaled.layer_region_counts),
        "base_final_region_count": len(base.sectors),
        "scaled_final_region_count": len(scaled.sectors),
        "reference_final_region_count": len(reference.sectors),
        "total_boundary_atoms": int(scaled.scalar_jumps.size),
        "nonzero_boundary_atoms": nonzero_count,
        "zero_boundary_atoms": zero_count,
        "omitted_total_atoms": int(scaled.omitted_indices.size),
        "omitted_nonzero_atoms": len(omitted_nonzero_indices),
        "retained_nonzero_atoms": retained_nonzero_count,
        "retained_nonzero_fraction": retained_nonzero_fraction,
        "min_nonzero_abs_jump": min_nonzero_abs_jump,
        "omitted_flux_l1_budget": OMITTED_FLUX_L1_BUDGET,
        "min_nonzero_over_budget": min_nonzero_abs_jump / OMITTED_FLUX_L1_BUDGET,
        "next_omission_abs_flux": scaled.next_omission_abs_flux,
        "abs_remainder_certificate": scaled.abs_remainder_certificate,
        "compressed_bias_abs": abs(compressed_bias),
        "boundary_angle_reference_max_error": angle_ref_error,
        "scalar_jump_reference_max_abs_error": jump_ref_error,
        "scalar_jump_reference_tolerance": jump_ref_tol,
        "generic_mean_reference_abs_error": mean_ref_error,
        "generic_mean_reference_tolerance": mean_ref_tol,
        "base_scaled_boundary_angle_max_error": angle_scale_error,
        "jump_scaling_max_abs_error": scaling_abs_error,
        "jump_scaling_relative_error": scaling_rel_error,
        "exact_gates": exact_gates,
        "exact_all_pass": all(exact_gates.values()),
        "adversary_success": adversary_success,
        "flops": scaled.flops,
    }


def run_once() -> dict[str, object]:
    cases = [_case(case) for case in CASES]
    exact_all = all(bool(c["exact_all_pass"]) for c in cases)
    adversary_all = all(bool(c["adversary_success"]) for c in cases)

    if not exact_all:
        decision = "E119_SKEPTICAL_REFERENCE_OR_SCALING_GATE_FAILED"
    elif adversary_all:
        decision = "TERMINAL_NO_GO_E119_GENERIC_ABSOLUTE_L1_BOUNDARY_COMPRESSION"
    else:
        decision = "E119_GENERIC_BOUNDARY_COMPRESSION_SURVIVES_ADVERSARIAL_REVIEW"

    return {
        "schema": "arc.whitebox.e119.skeptical_scaling_adversary.v1",
        "reviewed_mechanism": (
            "generic weight-driven boundary construction plus independent-atom "
            "absolute-L1 omitted-flux certificate"
        ),
        "scale_per_layer": SCALE,
        "nonzero_tolerance": NONZERO_TOL,
        "omitted_flux_l1_budget": OMITTED_FLUX_L1_BUDGET,
        "raw_mse_gate": RAW_MSE_GATE,
        "cases": cases,
        "exact_all_pass": exact_all,
        "adversary_all_cases": adversary_all,
        "compression_survival_requirement": (
            "omit at least one nonzero boundary atom on every adversarial case "
            "while preserving the frozen rigorous certificate"
        ),
        "decision": decision,
        "scope": {
            "target_free": True,
            "public": False,
            "benchmark": False,
            "scorer": False,
            "holdout_full": False,
            "tuning": False,
            "seed_or_scale_sweep": False,
            "canonical_mutation": False,
            "ledger_mutation": False,
            "does_not_falsify_e114_exactness": True,
            "does_not_falsify_e119_generic_construction": True,
            "rules_out": (
                "frozen E119 independent-atom absolute-L1 omission rule as a "
                "generic material-compression mechanism"
            ),
        },
    }


def canonical(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    first = run_once()
    second = run_once()
    deterministic = canonical(first) == canonical(second)
    first["deterministic_replay_exact"] = deterministic

    if not deterministic:
        first["decision"] = "E119_SKEPTICAL_DETERMINISM_GATE_FAILED"

    text = json.dumps(first, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print("E119_SKEPTICAL_SCALING=" + canonical(first), flush=True)

    expected = "TERMINAL_NO_GO_E119_GENERIC_ABSOLUTE_L1_BOUNDARY_COMPRESSION"
    return 0 if first["decision"] == expected and deterministic else 2


if __name__ == "__main__":
    raise SystemExit(main())
