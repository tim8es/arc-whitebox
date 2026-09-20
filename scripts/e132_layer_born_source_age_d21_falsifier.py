#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e132_exact_angular_reference import build_exact_reference, he_weights
from methods.e132_layer_born_d21 import (
    PROD_CAP,
    RAW_MSE_TARGET,
    layer_born_d21_estimate,
    production_cost_receipt,
    ranks_for_width,
)

NETWORK_SEEDS = (132200, 132201, 132202, 132203)
CANDIDATE_SEEDS = (132400, 132401, 132402, 132403)
WIDTH = 8
DEPTH = 8
PILOT = 256
EVALUATION = 2048
OUT = Path("e132-layer-born-source-age-d21.json")
CANDIDATE_PATH = Path("methods/e132_layer_born_d21.py")


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
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open",
                "eval",
                "exec",
            }:
                io_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    x in name
                    for x in [
                        "read_text",
                        "read_bytes",
                        "urlopen",
                        "request",
                        "download",
                    ]
                ):
                    io_calls.append(name)

    forbidden_imports = [
        x
        for x in imports
        if any(
            term in x.lower()
            for term in [
                "e132_exact",
                "e114",
                "whestbench",
                "dataset",
                "scorer",
                "requests",
                "urllib",
            ]
        )
    ]
    sig = inspect.signature(layer_born_d21_estimate)
    params = list(sig.parameters)
    shape_ok = params == ["weights", "pilot", "evaluation", "seed"]
    return {
        "candidate_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "io_network_calls": io_calls,
        "callable_parameters": params,
        "callable_only_weights_pilot_evaluation_seed": shape_ok,
        "passes": bool(not forbidden_imports and not io_calls and shape_ok),
    }


def _independent_cost_formula(
    n: int,
    depth: int,
    pilot: int,
    evaluation: int,
    *,
    helper_reserve: int,
) -> dict:
    ry, rs, rn = ranks_for_width(n)
    hidden = depth - 1
    per_layer = 2 * n * n + 2 * n
    parts = {
        "rng_materialization_upper": 32 * (pilot + evaluation) * n,
        "network_propagation_upper": (
            pilot * hidden + evaluation * depth
        ) * per_layer,
        "pilot_d21_stats_upper": hidden * (
            2 * pilot * n * n + 12 * pilot * n
        ),
        "source_age_transport_upper": hidden * (
            8 * n * n * ry
            + 8 * n * n * rs
            + 2 * n * n * rn
            + 4 * n * rs * rn
        ),
        "birth_compression_upper": hidden * (
            4 * n * n * ry + 4 * n * ry * ry + 8 * ry**3
        ),
        "shared_rebase_upper": hidden * (
            4 * n * n * rs
            + 4 * n * (rs + ry) ** 2
            + 8 * (rs + ry) ** 3
            + 4 * n * rs * ry
        ),
        "nested_rebase_upper": hidden * (
            4 * n * rs * rn + 4 * rs * rn * rn + 8 * rn**3
        ),
        "state_reconstruction_upper": hidden * (
            4 * n * n * ry + 2 * n * n * rs + 4 * n * rs * rn
        ),
        "direction_normalization_upper": 6 * n * n,
        "direction_gram_upper": 2 * n**3,
        "evaluation_input_projection_upper": 2 * evaluation * n * n,
        "lowrank_d21_apply_upper": (
            4 * evaluation * n * (2 * ry + 3 * rs + rn)
        ),
        "final_d21_reconstruct_upper": (
            2 * n * n * (2 * ry + 3 * rs + rn)
        ),
        "rowwise_rho_upper": 3 * n * n,
        "final_correction_upper": (
            2 * evaluation * n * n + 8 * evaluation * n
        ),
        "certificate_upper": 16 * depth * n * n + 8 * n * n,
        "final_reductions_upper": 8 * evaluation * n,
        "helper_reserve": helper_reserve,
    }
    return {**parts, "all_in_upper": int(sum(parts.values()))}


def _ledger_matches(actual: dict, expected: dict) -> bool:
    for key, value in expected.items():
        if actual.get(key) != value:
            return False
    return True


def main() -> None:
    audit = _source_audit()
    production = production_cost_receipt()
    independent_production = _independent_cost_formula(
        1024, 16, 256, 2048, helper_reserve=2_000_000_000
    )
    production_match = _ledger_matches(
        production,
        independent_production,
    )

    records = []
    deterministic_all = True
    ledger_replay_all = True
    small_ledger_match_all = True
    finite_all = True
    nested_all = True
    birth_identity_max = 0.0
    diag_max = 0.0

    for net_seed, cand_seed in zip(NETWORK_SEEDS, CANDIDATE_SEEDS):
        weights = he_weights(net_seed, width=WIDTH, depth=DEPTH)

        candidate = layer_born_d21_estimate(
            weights,
            pilot=PILOT,
            evaluation=EVALUATION,
            seed=cand_seed,
        )
        replay = layer_born_d21_estimate(
            weights,
            pilot=PILOT,
            evaluation=EVALUATION,
            seed=cand_seed,
        )

        replay_exact = bool(
            np.array_equal(candidate.mean, replay.mean)
            and np.array_equal(
                candidate.baseline_mean, replay.baseline_mean
            )
            and np.array_equal(
                candidate.d21_correction, replay.d21_correction
            )
            and candidate.certificate_mse == replay.certificate_mse
            and candidate.diagnostics == replay.diagnostics
        )
        ledger_exact = candidate.ledger == replay.ledger
        expected_small = _independent_cost_formula(
            WIDTH,
            DEPTH,
            PILOT,
            EVALUATION,
            helper_reserve=0,
        )
        small_match = _ledger_matches(candidate.ledger, expected_small)

        deterministic_all = deterministic_all and replay_exact
        ledger_replay_all = ledger_replay_all and ledger_exact
        small_ledger_match_all = small_ledger_match_all and small_match
        finite_all = finite_all and candidate.finite
        nested_all = nested_all and candidate.nested_path_exercised
        birth_identity_max = max(
            birth_identity_max, candidate.birth_identity_max_abs
        )
        diag_max = max(
            diag_max,
            candidate.diagnostics["d21_correction_diag_max_abs"],
        )

        # Exact target is materialized only after candidate + replay are frozen.
        ref = build_exact_reference(weights)
        cand_mse = _mse(candidate.mean, ref.mean)
        base_mse = _mse(candidate.baseline_mean, ref.mean)

        records.append(
            {
                "network_seed": net_seed,
                "candidate_seed": cand_seed,
                "candidate_mean_sha256": _sha(candidate.mean),
                "baseline_mean_sha256": _sha(candidate.baseline_mean),
                "d21_correction_sha256": _sha(candidate.d21_correction),
                "exact_mean_sha256": _sha(ref.mean),
                "candidate_mse": cand_mse,
                "baseline_mse": base_mse,
                "candidate_over_baseline": (
                    cand_mse / base_mse if base_mse > 0.0 else math.inf
                ),
                "candidate_over_raw_target": cand_mse / RAW_MSE_TARGET,
                "certificate_mse": candidate.certificate_mse,
                "certificate_over_raw_target": (
                    candidate.certificate_mse / RAW_MSE_TARGET
                ),
                "certificate_pass": (
                    candidate.certificate_mse <= RAW_MSE_TARGET
                ),
                "candidate_finite": candidate.finite,
                "nested_path_exercised": candidate.nested_path_exercised,
                "birth_identity_max_abs": (
                    candidate.birth_identity_max_abs
                ),
                "d21_diag_max_abs": (
                    candidate.diagnostics[
                        "d21_correction_diag_max_abs"
                    ]
                ),
                "d21_fro": candidate.diagnostics[
                    "d21_correction_fro"
                ],
                "gamma": candidate.diagnostics["gamma"],
                "lipschitz_bound_max": candidate.diagnostics[
                    "lipschitz_bound_max"
                ],
                "hermite_sd_bound_max": candidate.diagnostics[
                    "hermite_sd_bound_max"
                ],
                "exact_layer_sector_counts": list(
                    ref.layer_sector_counts
                ),
                "exact_final_sector_count": len(ref.sectors),
                "deterministic_replay_bitwise_exact": replay_exact,
                "ledger_replay_exact": ledger_exact,
                "small_ledger_matches_independent_formula": small_match,
                "small_ledger": candidate.ledger,
            }
        )

    pooled_candidate = float(
        np.mean([r["candidate_mse"] for r in records])
    )
    pooled_baseline = float(
        np.mean([r["baseline_mse"] for r in records])
    )
    improve_count = sum(
        r["candidate_mse"] < r["baseline_mse"] for r in records
    )
    max_cert = max(r["certificate_mse"] for r in records)
    max_mse = max(r["candidate_mse"] for r in records)

    gates = {
        "candidate_finite_all": finite_all,
        "deterministic_replay_bitwise_exact_all": deterministic_all,
        "ledger_replay_exact_all": ledger_replay_all,
        "nested_age_ge_5_exercised_all": nested_all,
        "birth_identity_max_abs_le_1e_12": birth_identity_max <= 1e-12,
        "d21_correction_diagonal_exact_zero": diag_max == 0.0,
        "candidate_source_audit_pass": audit["passes"],
        "reference_materialized_only_after_candidate": True,
        "no_target_public_scorer_holdout_full": True,
        "pooled_candidate_mse_strictly_below_baseline": (
            pooled_candidate < pooled_baseline
        ),
        "candidate_improves_at_least_3_of_4": improve_count >= 3,
        "certificate_mse_le_1_89e_8_every_network": all(
            r["certificate_pass"] for r in records
        ),
        "pooled_candidate_mse_le_1_89e_8": (
            pooled_candidate <= RAW_MSE_TARGET
        ),
        "every_network_candidate_mse_le_1_89e_8": (
            max_mse <= RAW_MSE_TARGET
        ),
        "production_cost_formula_matches_independent_sum": production_match,
        "production_all_in_le_hard_cap": (
            production["all_in_upper"] <= PROD_CAP
        ),
        "small_ledger_matches_protocol_formula_all": small_ledger_match_all,
    }

    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e132.layer_born_source_age_d21.v1",
        "experiment": "E132",
        "idempotency_key": (
            "ARC-E132-LAYER-BORN-SOURCE-AGE-D21-20260920"
        ),
        "mechanism": {
            "name": (
                "layer-born source-age transported D21 Hermite estimator"
            ),
            "pilot": PILOT,
            "evaluation": EVALUATION,
            "source_age_ranks_width8": list(ranks_for_width(WIDTH)),
            "source_age_ranks_production": [32, 48, 24],
            "age_schedule": {
                "young": "ages 0,1 separate",
                "shared": "ages 2,3,4 common left basis",
                "nested": "age >=5 nested sub-basis of shared state",
            },
            "d21_transport": "(W o W)^T D W",
            "birth_definition": (
                "current empirical D21 minus transported compressed "
                "old-source prediction"
            ),
            "correction": (
                "off-diagonal D21 coefficient multiplying exactly "
                "zero-mean cubic Gaussian Hermite features"
            ),
            "conditional_unbiasedness": True,
            "target_fit": False,
        },
        "source_audit": audit,
        "records": records,
        "summary": {
            "pooled_candidate_mse": pooled_candidate,
            "pooled_baseline_mse": pooled_baseline,
            "candidate_over_baseline": (
                pooled_candidate / pooled_baseline
                if pooled_baseline > 0.0 else math.inf
            ),
            "improve_count": improve_count,
            "max_candidate_mse": max_mse,
            "max_certificate_mse": max_cert,
            "max_certificate_over_raw_target": (
                max_cert / RAW_MSE_TARGET
            ),
            "birth_identity_max_abs": birth_identity_max,
            "d21_diagonal_max_abs": diag_max,
            "raw_mse_target": RAW_MSE_TARGET,
        },
        "production_cost": production,
        "independent_production_cost_sum": independent_production,
        "protocol_arithmetic_erratum_applied": True,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E132_LOCAL_SMALL_WIDTH_GO"
            if scientific_go
            else "E132_TERMINAL_NO_GO_CLOSE_LAYER_BORN_SOURCE_AGE_D21"
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
        "E132_LAYER_BORN_D21=" + json.dumps(result, sort_keys=True),
        flush=True,
    )

    integrity_keys = [
        "candidate_finite_all",
        "deterministic_replay_bitwise_exact_all",
        "ledger_replay_exact_all",
        "nested_age_ge_5_exercised_all",
        "birth_identity_max_abs_le_1e_12",
        "d21_correction_diagonal_exact_zero",
        "candidate_source_audit_pass",
        "reference_materialized_only_after_candidate",
        "no_target_public_scorer_holdout_full",
        "production_cost_formula_matches_independent_sum",
        "small_ledger_matches_protocol_formula_all",
    ]
    if not all(gates[k] for k in integrity_keys):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
