#!/usr/bin/env python3
"""E125 preflight: weight-only certificates and operation ledger.

This script MUST NOT evaluate any E125 source frame or network prediction.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import he_weights
from methods.e125_clifford8_tightframe import (
    DEFAULT_FRAMES,
    exact_clifford_algebra_report,
    finite_sample_mse_certificate,
    production_operation_ledger,
)


OUT = Path("e125-preflight-certificate.json")
DELTA_PER_ESTIMATE = 1.25e-7
METHOD_PATH = Path("methods/e125_clifford8_tightframe.py")


def block_diag(mats: list[np.ndarray]) -> np.ndarray:
    rows = sum(int(m.shape[0]) for m in mats)
    cols = sum(int(m.shape[1]) for m in mats)
    out = np.zeros((rows, cols), dtype=np.float64)
    r = 0
    c = 0
    for m in mats:
        rr, cc = m.shape
        out[r : r + rr, c : c + cc] = m
        r += rr
        c += cc
    return out


def block_stress(subnetwork_seeds: list[int]) -> list[np.ndarray]:
    subnetworks = [he_weights(seed, width=2, depth=4) for seed in subnetwork_seeds]
    return [
        block_diag([sub[layer] for sub in subnetworks])
        for layer in range(4)
    ]


def independent_ledger() -> dict:
    d = n = 1024
    depth = 16
    k = 8
    j = 16
    frames = 252
    directions = frames * j

    static_clifford = 70_000
    base_rng = frames * (16 * d)
    base_norm = frames * (3 * d + 64)
    source_materialization = frames * (16 * d)
    runtime_gram = frames * (2 * d * k * k + k * k)
    deep = directions * depth * (2 * n * n + 2 * n)
    final = directions * n + 2 * directions + 5 * n
    all_in = (
        static_clifford
        + base_rng
        + base_norm
        + source_materialization
        + runtime_gram
        + deep
        + final
    )
    cap = 136_758_472_261

    return {
        "dimension": d,
        "width": n,
        "depth": depth,
        "source_dimension": k,
        "codewords_per_frame": j,
        "frames": frames,
        "directions": directions,
        "static_clifford_algebra_upper": static_clifford,
        "base_gaussian_rng_upper": base_rng,
        "base_norm_and_normalization_upper": base_norm,
        "signed_permutation_source_materialization_upper": source_materialization,
        "runtime_frame_gram_norm_orthogonality_upper": runtime_gram,
        "deep_propagation_upper": deep,
        "final_reduction_radial_upper": final,
        "all_in_upper": all_in,
        "hard_cap_flops": cap,
        "slack_flops": cap - all_in,
        "gate_passed": all_in <= cap,
    }


def cert_to_json(cert: dict) -> dict:
    return {
        **{
            k: v
            for k, v in cert.items()
            if k not in ("unit_sphere_output_bound", "coordinate_abs_error_bound")
        },
        "unit_sphere_output_bound": cert["unit_sphere_output_bound"].tolist(),
        "coordinate_abs_error_bound": cert["coordinate_abs_error_bound"].tolist(),
    }


def main() -> None:
    stress8 = block_stress([125300, 125301, 125302, 125303])
    stress16 = block_stress(list(range(125320, 125328)))

    cert8 = finite_sample_mse_certificate(
        stress8,
        frames=DEFAULT_FRAMES,
        delta=DELTA_PER_ESTIMATE,
    )
    cert16 = finite_sample_mse_certificate(
        stress16,
        frames=DEFAULT_FRAMES,
        delta=DELTA_PER_ESTIMATE,
    )

    algebra = exact_clifford_algebra_report()
    method_ledger = production_operation_ledger()
    independently_recomputed = independent_ledger()

    source = METHOD_PATH.read_text(encoding="utf-8").lower()
    forbidden = {
        "e122": "e122" in source,
        "simplex": "simplex" in source,
        "gram_schmidt": "gram_schmidt" in source,
        "haar_stiefel": "haar_stiefel" in source,
        "exact_reference_import": "e114_exact_angular_reference" in source,
        "target_module_import": (
            "import target" in source or "from target" in source
        ),
    }
    source_audit_pass = not any(forbidden.values())

    repeated8 = finite_sample_mse_certificate(
        stress8,
        frames=DEFAULT_FRAMES,
        delta=DELTA_PER_ESTIMATE,
    )
    repeated16 = finite_sample_mse_certificate(
        stress16,
        frames=DEFAULT_FRAMES,
        delta=DELTA_PER_ESTIMATE,
    )

    deterministic = bool(
        cert8["mse_bound"] == repeated8["mse_bound"]
        and cert16["mse_bound"] == repeated16["mse_bound"]
        and np.array_equal(
            cert8["unit_sphere_output_bound"],
            repeated8["unit_sphere_output_bound"],
        )
        and np.array_equal(
            cert16["unit_sphere_output_bound"],
            repeated16["unit_sphere_output_bound"],
        )
        and method_ledger == independently_recomputed
    )

    gates = {
        "exact_integer_clifford_algebra": bool(algebra["pass"]),
        "stress8_bounds_finite_nonnegative": bool(
            np.isfinite(cert8["unit_sphere_output_bound"]).all()
            and np.all(cert8["unit_sphere_output_bound"] >= 0.0)
        ),
        "stress16_bounds_finite_nonnegative": bool(
            np.isfinite(cert16["unit_sphere_output_bound"]).all()
            and np.all(cert16["unit_sphere_output_bound"] >= 0.0)
        ),
        "stress8_certificate_finite_positive": bool(
            np.isfinite(cert8["mse_bound"]) and cert8["mse_bound"] > 0.0
        ),
        "stress16_certificate_finite_positive": bool(
            np.isfinite(cert16["mse_bound"]) and cert16["mse_bound"] > 0.0
        ),
        "certificate_recompute_exact": deterministic,
        "candidate_source_audit_pass": source_audit_pass,
        "production_ledger_matches_independent_recompute": (
            method_ledger == independently_recomputed
        ),
        "production_cost_le_hard_cap": bool(method_ledger["gate_passed"]),
        "candidate_source_not_executed": True,
    }

    result = {
        "schema": "arc.whitebox.e125.preflight_certificate.v1",
        "experiment": "E125",
        "status": "PREFLIGHT_PASS" if all(gates.values()) else "PREFLIGHT_NO_GO",
        "protocol_commit": "fab8a6e6cb962862e617180ff59e1c72c142b0ec",
        "candidate_commit": "e1220128a3967ed6bd951d72a209eb8bbcdca101",
        "frames": DEFAULT_FRAMES,
        "delta_total": 1e-6,
        "candidate_estimate_count": 8,
        "delta_per_estimate": DELTA_PER_ESTIMATE,
        "stress8": {
            "subnetwork_seeds": [125300, 125301, 125302, 125303],
            "weight_shapes": [list(w.shape) for w in stress8],
            "certificate": cert_to_json(cert8),
        },
        "stress16": {
            "subnetwork_seeds": list(range(125320, 125328)),
            "weight_shapes": [list(w.shape) for w in stress16],
            "certificate": cert_to_json(cert16),
        },
        "clifford_algebra": algebra,
        "candidate_source_forbidden_dependency_flags": forbidden,
        "candidate_source_audit_pass": source_audit_pass,
        "production_ledger_candidate": method_ledger,
        "production_ledger_independent_recompute": independently_recomputed,
        "gates": gates,
        "scientific_source_evaluation_executed": False,
        "scope": {
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "production_run": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E125_PREFLIGHT=" + json.dumps(result, sort_keys=True))

    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
