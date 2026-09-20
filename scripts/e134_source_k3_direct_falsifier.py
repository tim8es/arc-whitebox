#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e134_exact_angular_reference import build_exact_reference, he_weights
from methods.e134_source_k3_direct import (
    BUDGET,
    PROD_DEPTH,
    PROD_M,
    PROD_N,
    PROD_RN,
    PROD_RS,
    PROD_RY,
    RAW_MSE_TARGET,
    UTIL_CAP,
    production_cost_receipt,
    ranks_for_width,
    source_k3_direct_estimate,
)

NETWORK_SEEDS = (134200, 134201, 134202, 134203)
CANDIDATE_SEEDS = (134400, 134401, 134402, 134403)
WIDTH = 32
DEPTH = 8
TRAJECTORIES = 4096
OUT = Path("e134-source-k3-direct-closure.json")
CANDIDATE_PATH = Path("methods/e134_source_k3_direct.py")


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _source_audit() -> dict:
    source = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    io_calls: list[str] = []
    forbidden_names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                io_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    term in name
                    for term in [
                        "read_text", "read_bytes", "urlopen",
                        "request", "download", "loadtxt",
                        "genfromtxt", "read_csv", "read_parquet"
                    ]
                ):
                    io_calls.append(name)
        elif isinstance(node, ast.Name):
            if node.id.lower() in {
                "target", "final_means", "scorer", "holdout"
            }:
                forbidden_names.append(node.id)

    forbidden_imports = [
        x for x in imports
        if any(
            term in x.lower()
            for term in [
                "e134_exact", "e132", "e114", "whestbench",
                "dataset", "scorer", "requests", "urllib"
            ]
        )
    ]

    sig = inspect.signature(source_k3_direct_estimate)
    params = list(sig.parameters)
    shape_ok = params == ["weights", "trajectories", "seed"]

    return {
        "candidate_sha256": hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "io_network_calls": io_calls,
        "forbidden_names": sorted(set(forbidden_names)),
        "callable_parameters": params,
        "callable_only_weights_trajectories_seed": bool(shape_ok),
        "passes": bool(
            not forbidden_imports
            and not io_calls
            and not forbidden_names
            and shape_ok
        ),
    }


def _independent_production_cost() -> dict:
    n = PROD_N
    l = PROD_DEPTH
    m = PROD_M
    ry, rs, rn = PROD_RY, PROD_RS, PROD_RN
    hidden = l - 1
    parts = {
        "rng_materialization_upper": 32 * m * n,
        "dense_propagation_upper": m * l * (2 * n * n + 2 * n),
        "hidden_centering_moment_reductions_upper": hidden * 8 * m * n,
        "birth_sketch_projection_qr_upper": hidden * (
            4 * m * n * ry + 4 * n * ry * ry + 8 * ry**3
        ),
        "birth_cubic_core_upper": hidden * (8 * m * ry**3),
        "represented_source_basis_transport_upper": hidden * (
            2 * n * n * (2 * ry + rs + rn)
        ),
        "cubic_core_basis_transform_upper": hidden * (
            8 * (2 * ry**4 + rs**4 + rn**4)
        ),
        "shared_nested_rebase_upper": hidden * (
            4 * n * (2 * ry + 3 * rs + rn) ** 2
            + 16 * (rs + ry) ** 4
            + 16 * rn**4
        ),
        "final_k3_diagonal_upper": 8 * n * (
            2 * ry**3 + 3 * rs**3 + rn**3
        ),
        "final_mean_variance_reductions_upper": 8 * m * n,
        "edgeworth_scalar_helpers_upper": 64 * n,
        "helper_certificate_accounting_reserve": 5_000_000_000,
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget": BUDGET,
        "utilization": total / float(BUDGET),
        "utilization_cap": UTIL_CAP,
        "cap_flops": UTIL_CAP * BUDGET,
        "slack_flops": UTIL_CAP * BUDGET - total,
    }


def _estimate_equal(a, b) -> bool:
    arrays_equal = all(
        np.array_equal(x, y)
        for x, y in [
            (a.mean, b.mean),
            (a.baseline_mean, b.baseline_mean),
            (
                a.full_empirical_k3_closure_mean,
                b.full_empirical_k3_closure_mean,
            ),
            (a.certificate_bounds, b.certificate_bounds),
            (a.actual_closure_residual, b.actual_closure_residual),
            (a.kappa3_compressed, b.kappa3_compressed),
            (a.kappa3_empirical, b.kappa3_empirical),
        ]
    )
    scalars_equal = (
        a.certificate_mse == b.certificate_mse
        and a.penultimate_tensor_residual_fro
        == b.penultimate_tensor_residual_fro
        and a.max_core_symmetry_error == b.max_core_symmetry_error
        and a.max_slice_disagreement == b.max_slice_disagreement
        and a.max_birth_projection_identity_error
        == b.max_birth_projection_identity_error
        and a.nested_path_exercised == b.nested_path_exercised
        and a.finite == b.finite
    )
    dicts_equal = (
        a.deterministic_state_digest == b.deterministic_state_digest
        and a.ledger == b.ledger
        and a.diagnostics == b.diagnostics
    )
    return bool(arrays_equal and scalars_equal and dicts_equal)


def main() -> None:
    audit = _source_audit()
    production = production_cost_receipt()
    independent_cost = _independent_production_cost()
    production_match = production["all_in_upper"] == independent_cost["all_in_upper"]
    component_match = all(
        production.get(k) == v
        for k, v in independent_cost.items()
        if k.endswith("_upper")
    )

    records = []
    finite_all = True
    deterministic_all = True
    nested_all = True
    max_sym = 0.0
    max_slice = 0.0
    max_birth = 0.0
    certificate_contains_all = True

    for net_seed, cand_seed in zip(NETWORK_SEEDS, CANDIDATE_SEEDS):
        weights = he_weights(net_seed, width=WIDTH, depth=DEPTH)

        # Candidate, baseline, source state and certificate are frozen first.
        candidate = source_k3_direct_estimate(
            weights,
            trajectories=TRAJECTORIES,
            seed=cand_seed,
        )
        replay = source_k3_direct_estimate(
            weights,
            trajectories=TRAJECTORIES,
            seed=cand_seed,
        )

        replay_exact = _estimate_equal(candidate, replay)
        certificate_contains = bool(
            np.all(
                np.abs(candidate.actual_closure_residual)
                <= candidate.certificate_bounds + 1e-12
            )
        )

        finite_all = finite_all and bool(candidate.finite)
        deterministic_all = deterministic_all and replay_exact
        nested_all = nested_all and bool(candidate.nested_path_exercised)
        max_sym = max(max_sym, candidate.max_core_symmetry_error)
        max_slice = max(max_slice, candidate.max_slice_disagreement)
        max_birth = max(
            max_birth,
            candidate.max_birth_projection_identity_error,
        )
        certificate_contains_all = (
            certificate_contains_all and certificate_contains
        )

        # Exact output mean is verifier-only and appears only after freeze.
        reference = build_exact_reference(weights)
        cand_mse = _mse(candidate.mean, reference.mean)
        base_mse = _mse(candidate.baseline_mean, reference.mean)

        records.append(
            {
                "network_seed": int(net_seed),
                "candidate_seed": int(cand_seed),
                "candidate_mean_sha256": _sha(candidate.mean),
                "baseline_mean_sha256": _sha(candidate.baseline_mean),
                "full_empirical_k3_closure_sha256": _sha(
                    candidate.full_empirical_k3_closure_mean
                ),
                "exact_mean_sha256": _sha(reference.mean),
                "candidate_mse": cand_mse,
                "baseline_mse": base_mse,
                "candidate_over_baseline": (
                    cand_mse / base_mse if base_mse > 0.0 else math.inf
                ),
                "candidate_over_raw_target": cand_mse / RAW_MSE_TARGET,
                "baseline_over_raw_target": base_mse / RAW_MSE_TARGET,
                "certificate_mse": candidate.certificate_mse,
                "certificate_over_raw_target": (
                    candidate.certificate_mse / RAW_MSE_TARGET
                ),
                "certificate_contains_actual_closure_residual": (
                    certificate_contains
                ),
                "certificate_max_bound": float(
                    np.max(candidate.certificate_bounds)
                ),
                "actual_closure_residual_max_abs": float(
                    np.max(np.abs(candidate.actual_closure_residual))
                ),
                "penultimate_tensor_residual_fro": (
                    candidate.penultimate_tensor_residual_fro
                ),
                "compressed_kappa3_fro": float(
                    np.linalg.norm(candidate.kappa3_compressed)
                ),
                "empirical_kappa3_fro": float(
                    np.linalg.norm(candidate.kappa3_empirical)
                ),
                "nested_path_exercised": bool(
                    candidate.nested_path_exercised
                ),
                "max_core_symmetry_error": (
                    candidate.max_core_symmetry_error
                ),
                "max_slice_disagreement": (
                    candidate.max_slice_disagreement
                ),
                "max_birth_projection_identity_error": (
                    candidate.max_birth_projection_identity_error
                ),
                "deterministic_replay_bitwise_exact": replay_exact,
                "exact_reference_finite": bool(reference.finite),
                "exact_layer_sector_counts": list(
                    reference.layer_sector_counts
                ),
                "exact_final_sector_count": int(
                    reference.final_sector_count
                ),
                "state_digest": candidate.deterministic_state_digest,
                "small_ledger": candidate.ledger,
            }
        )

    pooled_candidate = float(
        np.mean([r["candidate_mse"] for r in records])
    )
    pooled_baseline = float(
        np.mean([r["baseline_mse"] for r in records])
    )
    ratio = (
        pooled_candidate / pooled_baseline
        if pooled_baseline > 0.0 else math.inf
    )
    improve_count = int(
        sum(
            r["candidate_mse"] < r["baseline_mse"]
            for r in records
        )
    )
    max_certificate = max(r["certificate_mse"] for r in records)
    references_finite = all(
        r["exact_reference_finite"] for r in records
    )

    gates = {
        "candidate_values_finite_all": bool(finite_all),
        "deterministic_replay_bitwise_exact_all": bool(deterministic_all),
        "nested_age_ge_5_exercised_all": bool(nested_all),
        "core_symmetry_max_abs_le_1e_11": bool(max_sym <= 1e-11),
        "d3_d21_slice_disagreement_le_1e_12": bool(max_slice <= 1e-12),
        "birth_projection_identity_le_1e_11": bool(max_birth <= 1e-11),
        "certificate_contains_actual_closure_residual_all": bool(
            certificate_contains_all
        ),
        "candidate_source_audit_pass": bool(audit["passes"]),
        "reference_materialized_only_after_candidate": True,
        "exact_references_finite_all": bool(references_finite),
        "no_target_public_scorer_holdout_full": True,
        "pooled_candidate_mse_strictly_below_baseline": bool(
            pooled_candidate < pooled_baseline
        ),
        "candidate_improves_at_least_3_of_4": bool(improve_count >= 3),
        "pooled_candidate_over_baseline_le_0_95": bool(ratio <= 0.95),
        "certificate_mse_le_1_89e_8_every_network": bool(
            max_certificate <= RAW_MSE_TARGET
        ),
        "production_cost_formula_matches_independent_sum": bool(
            production_match and component_match
        ),
        "production_all_in_le_0_13_budget": bool(
            production["passes_cap"]
        ),
    }

    integrity_keys = [
        "candidate_values_finite_all",
        "deterministic_replay_bitwise_exact_all",
        "nested_age_ge_5_exercised_all",
        "core_symmetry_max_abs_le_1e_11",
        "d3_d21_slice_disagreement_le_1e_12",
        "birth_projection_identity_le_1e_11",
        "certificate_contains_actual_closure_residual_all",
        "candidate_source_audit_pass",
        "reference_materialized_only_after_candidate",
        "exact_references_finite_all",
        "no_target_public_scorer_holdout_full",
        "production_cost_formula_matches_independent_sum",
        "production_all_in_le_0_13_budget",
    ]
    scientific_keys = [
        "pooled_candidate_mse_strictly_below_baseline",
        "candidate_improves_at_least_3_of_4",
        "pooled_candidate_over_baseline_le_0_95",
        "certificate_mse_le_1_89e_8_every_network",
    ]
    integrity_go = bool(all(gates[k] for k in integrity_keys))
    scientific_go = bool(
        integrity_go and all(gates[k] for k in scientific_keys)
    )

    result = {
        "schema": "arc.whitebox.e134.source_k3_direct_closure.v1",
        "experiment": "E134",
        "idempotency_key": "ARC-E134-SOURCE-K3-DIRECT-CLOSURE-20260920",
        "mechanism": {
            "name": "source-age full-K3 direct Edgeworth ReLU-mean closure",
            "zero_mean_posthoc_correction": False,
            "full_k3_source_transport": True,
            "d3_d21_are_slices_of_same_source_tensor": True,
            "layer_born_projected_innovation": True,
            "source_age_schedule": {
                "age_0_1": "separate",
                "age_2_4": "shared basis",
                "age_ge_5": "nested basis",
            },
            "ranks_small": list(ranks_for_width(WIDTH)),
            "ranks_production": [PROD_RY, PROD_RS, PROD_RN],
            "trajectories": TRAJECTORIES,
            "target_fit": False,
        },
        "source_audit": audit,
        "records": records,
        "summary": {
            "pooled_candidate_mse": pooled_candidate,
            "pooled_baseline_mse": pooled_baseline,
            "candidate_over_baseline": ratio,
            "improve_count": improve_count,
            "max_certificate_mse": max_certificate,
            "max_certificate_over_raw_target": (
                max_certificate / RAW_MSE_TARGET
            ),
            "max_core_symmetry_error": max_sym,
            "max_slice_disagreement": max_slice,
            "max_birth_projection_identity_error": max_birth,
            "raw_mse_target": RAW_MSE_TARGET,
        },
        "production_cost": production,
        "independent_production_cost": independent_cost,
        "gates": gates,
        "integrity_go": integrity_go,
        "scientific_go": scientific_go,
        "decision": (
            "E134_LOCAL_SCIENTIFIC_GO_SOURCE_AGE_K3_DIRECT_CLOSURE"
            if scientific_go
            else "E134_TERMINAL_NO_GO_CLOSE_SOURCE_K3_DIRECT_CLOSURE"
        ),
        "scope": {
            "synthetic_exact_small_width_only": True,
            "target_free": True,
            "production_execution": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "merged": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E134_SOURCE_K3_DIRECT="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )

    if not integrity_go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
