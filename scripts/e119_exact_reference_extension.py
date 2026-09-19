#!/usr/bin/env python3
"""E119 exact-reference extension evidence over heterogeneous small dense MLPs."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import dense_he_weights
from methods.e119_exact_reference_compare import compare_generic_boundary_to_exact

OUT = Path("e119-exact-reference-extension.json")


def _manual_weights() -> list[np.ndarray]:
    return [
        np.array(
            [[1.0, -2.0, 0.5], [0.75, 1.25, -1.5]],
            dtype=np.float64,
        ),
        np.array(
            [[1.0, -0.5], [-1.25, 2.0], [0.8, 0.6]],
            dtype=np.float64,
        ),
        np.array([[1.2], [-0.7]], dtype=np.float64),
    ]


def _weights_digest(weights: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for w in weights:
        a = np.ascontiguousarray(w, dtype=np.float64)
        h.update(str(a.shape).encode("ascii"))
        h.update(a.tobytes())
    return h.hexdigest()


def _cases() -> list[tuple[str, list[np.ndarray]]]:
    return [
        ("he_119501_3", dense_he_weights(119501, widths=(3,))),
        ("he_119502_5_2", dense_he_weights(119502, widths=(5, 2))),
        ("he_119503_4_6_3", dense_he_weights(119503, widths=(4, 6, 3))),
        ("he_119504_8_5_7_2", dense_he_weights(119504, widths=(8, 5, 7, 2))),
        ("he_119505_3_8_4_6", dense_he_weights(119505, widths=(3, 8, 4, 6))),
        ("manual_dense_3_2_1", _manual_weights()),
    ]


def main() -> None:
    records = []
    replay_exact = True

    for name, weights in _cases():
        first = compare_generic_boundary_to_exact(weights)
        second = compare_generic_boundary_to_exact(weights)
        replay_exact = replay_exact and first == second

        payload = asdict(first)
        payload.update(
            {
                "case": name,
                "weight_shapes": [list(w.shape) for w in weights],
                "weights_sha256": _weights_digest(weights),
                "all_weights_dense_nonzero": all(
                    int(np.count_nonzero(w)) == int(w.size) for w in weights
                ),
            }
        )
        records.append(payload)

    summary = {
        "case_count": len(records),
        "max_depth": max(len(r["weight_shapes"]) for r in records),
        "max_width": max(
            max(shape[1] for shape in r["weight_shapes"]) for r in records
        ),
        "max_final_region_count": max(
            r["final_region_count_reference"] for r in records
        ),
        "max_sector_lo_error": max(r["max_sector_lo_error"] for r in records),
        "max_sector_hi_error": max(r["max_sector_hi_error"] for r in records),
        "max_sector_coeff_abs_error": max(
            r["max_sector_coeff_abs_error"] for r in records
        ),
        "max_reference_direct_eval_abs_error": max(
            r["max_reference_direct_eval_abs_error"] for r in records
        ),
        "max_generic_direct_eval_abs_error": max(
            r["max_generic_direct_eval_abs_error"] for r in records
        ),
        "max_boundary_angle_wrapped_error": max(
            r["max_boundary_angle_wrapped_error"] for r in records
        ),
        "max_scalar_jump_abs_error": max(
            r["max_scalar_jump_abs_error"] for r in records
        ),
        "max_generic_vs_reference_mean_abs_error": max(
            r["generic_vs_reference_mean_abs_error"] for r in records
        ),
        "max_reference_flux_vs_sector_mean_abs_error": max(
            r["reference_flux_vs_sector_mean_abs_error"] for r in records
        ),
        "deterministic_replay_exact": replay_exact,
    }

    gates = {
        "all_cases_finite": all(r["finite"] for r in records),
        "all_weights_dense_nonzero": all(
            r["all_weights_dense_nonzero"] for r in records
        ),
        "all_partitions_complete": all(r["partition_complete"] for r in records),
        "all_partitions_ordered": all(r["partition_ordered"] for r in records),
        "layer_region_counts_match": all(
            tuple(r["layer_region_counts_generic"])
            == tuple(r["layer_region_counts_reference"])
            for r in records
        ),
        "final_region_counts_match": all(
            r["final_region_count_generic"] == r["final_region_count_reference"]
            for r in records
        ),
        "partition_gap_overlap_le_1e_11": all(
            r["max_partition_gap"] <= 1e-11
            and r["max_partition_overlap"] <= 1e-11
            for r in records
        ),
        "sector_endpoint_error_le_1e_12": (
            summary["max_sector_lo_error"] <= 1e-12
            and summary["max_sector_hi_error"] <= 1e-12
        ),
        "sector_coeff_error_le_1e_12": (
            summary["max_sector_coeff_abs_error"] <= 1e-12
        ),
        "reference_direct_eval_error_le_1e_12": (
            summary["max_reference_direct_eval_abs_error"] <= 1e-12
        ),
        "generic_direct_eval_error_le_1e_12": (
            summary["max_generic_direct_eval_abs_error"] <= 1e-12
        ),
        "boundary_angle_error_le_1e_10": (
            summary["max_boundary_angle_wrapped_error"] <= 1e-10
        ),
        "scalar_jump_error_le_1e_10": (
            summary["max_scalar_jump_abs_error"] <= 1e-10
        ),
        "generic_mean_error_le_1e_10": (
            summary["max_generic_vs_reference_mean_abs_error"] <= 1e-10
        ),
        "reference_flux_identity_le_1e_10": (
            summary["max_reference_flux_vs_sector_mean_abs_error"] <= 1e-10
        ),
        "deterministic_replay_exact": replay_exact,
        "scope_reference_only_no_targets": True,
    }

    result = {
        "schema": "arc.whitebox.e119.exact_reference_extension.v1",
        "experiment": "E119",
        "role": "exact_reference_engineer",
        "branch": "review/e119-exact-reference-extension-20260919",
        "purpose": (
            "extend the angular exact-reference harness to arbitrary small dense "
            "2-D zero-bias ReLU weight chains and compare the generic E119 "
            "boundary implementation against exact sectors"
        ),
        "records": records,
        "summary": summary,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "decision": (
            "E119_EXACT_REFERENCE_EXTENSION_PASS"
            if all(gates.values())
            else "E119_EXACT_REFERENCE_EXTENSION_FAIL"
        ),
        "scope": {
            "input_dimension": 2,
            "max_width": 8,
            "max_depth": 4,
            "arbitrary_dense_weight_shapes": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "production_run": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E119_EXACT_REFERENCE_EXTENSION=" + json.dumps(result, sort_keys=True))

    if not result["all_gates_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
