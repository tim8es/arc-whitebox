from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e118_boundary_flux_physical import (
    compressed_physical_estimate,
    full_exact_reference,
    make_network,
)

SEED = 118118
WIDTH = 8
DEPTH = 4
EXPANSION_CAP = 62
RMS_LIMIT = 1.37477270849e-4

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_INCREMENTAL_CAP = 136_758_472_261
PROD_TRANSITION_FLOPS = 2 * PROD_WIDTH**3
PROD_TRANSITION_COUNT = 62
PROD_TRANSITION_TOTAL = PROD_TRANSITION_COUNT * PROD_TRANSITION_FLOPS
PROD_HELPER_RESERVE = 3_600_000_000
PROD_INCREMENTAL_TOTAL = PROD_TRANSITION_TOTAL + PROD_HELPER_RESERVE
PROD_STATE_BYTES = PROD_WIDTH * PROD_WIDTH * 4

OUT = Path("e118-boundary-flux-physical.json")
EXIT = Path("e118-exit.txt")


def payload_digest(obj: dict) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def evaluate_once() -> dict:
    weights = make_network(SEED, width=WIDTH, depth=DEPTH)
    ref = full_exact_reference(weights)
    cand = compressed_physical_estimate(weights, expansion_cap=EXPANSION_CAP)

    actual_error = abs(cand["estimate"] - ref["mean"])
    production_live_state_bytes_lb = cand["max_live_queue"] * PROD_STATE_BYTES

    gates = {
        "finite_all": bool(
            all(
                math.isfinite(float(x))
                for x in (
                    ref["mean"],
                    ref["flux_mean"],
                    ref["boundary_jump_sum"],
                    cand["estimate"],
                    cand["remainder_certificate"],
                    actual_error,
                )
            )
        ),
        "exact_flux_sector_agreement_le_1e_12": ref["flux_sector_abs_diff"] <= 1e-12,
        "actual_error_within_certificate": actual_error <= cand["remainder_certificate"] + 1e-12,
        "remainder_certificate_le_rms_limit": cand["remainder_certificate"] <= RMS_LIMIT,
        "actual_error_le_rms_limit": actual_error <= RMS_LIMIT,
        "expansion_cap_exact": cand["expansions"] == EXPANSION_CAP or cand["queue_exhausted"],
        "production_incremental_budget_le_cap": PROD_INCREMENTAL_TOTAL <= PROD_INCREMENTAL_CAP,
    }

    result = {
        "schema": "arc.whitebox.e118.boundary_flux_physical.v1",
        "experiment": "E118",
        "identity": "ARC-E118-BOUNDARY-FLUX-PHYSICAL-COMPRESSION-20260919",
        "frozen_smallwidth": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": SEED,
            "observable": "normalized sum of final coordinates",
            "expansion_cap": EXPANSION_CAP,
            "zero_bias": True,
            "numerical_quadrature": False,
            "monte_carlo_truth": False,
        },
        "exact_reference": ref,
        "candidate": cand,
        "error": {
            "rms_limit": RMS_LIMIT,
            "actual_absolute_scalar_error": actual_error,
            "remainder_certificate": cand["remainder_certificate"],
            "actual_over_limit": actual_error / RMS_LIMIT,
            "certificate_over_limit": cand["remainder_certificate"] / RMS_LIMIT,
        },
        "production_accounting": {
            "incremental_cap_flops": PROD_INCREMENTAL_CAP,
            "dense_state_transition_flops": PROD_TRANSITION_FLOPS,
            "transition_count": PROD_TRANSITION_COUNT,
            "transition_total_flops": PROD_TRANSITION_TOTAL,
            "helpers_materialization_remainder_reserve_flops": PROD_HELPER_RESERVE,
            "all_in_incremental_ceiling_flops": PROD_INCREMENTAL_TOTAL,
            "incremental_margin_flops": PROD_INCREMENTAL_CAP - PROD_INCREMENTAL_TOTAL,
            "float32_dense_coefficient_bytes_per_live_state": PROD_STATE_BYTES,
            "production_dense_state_memory_lower_bound_at_observed_max_queue": production_live_state_bytes_lb,
            "high_dimensional_cone_helpers_proven_within_reserve": False,
            "note": (
                "The frozen helper reserve is only pursued if the exact small-width "
                "remainder gate passes. It does not; therefore no production cone "
                "materialization implementation is authorized."
            ),
        },
        "gates": gates,
    }

    deterministic_core = {
        "exact_reference": ref,
        "candidate": cand,
        "error": result["error"],
        "production_accounting": result["production_accounting"],
        "gates": gates,
    }
    result["deterministic_payload_sha256"] = payload_digest(deterministic_core)
    return result


def main() -> None:
    first = evaluate_once()
    second = evaluate_once()
    deterministic = first["deterministic_payload_sha256"] == second["deterministic_payload_sha256"]
    first["deterministic_replay_exact"] = deterministic
    first["gates"]["deterministic_replay_exact"] = deterministic

    science_pass = bool(
        first["gates"]["finite_all"]
        and first["gates"]["exact_flux_sector_agreement_le_1e_12"]
        and first["gates"]["actual_error_within_certificate"]
        and first["gates"]["remainder_certificate_le_rms_limit"]
        and first["gates"]["actual_error_le_rms_limit"]
        and first["gates"]["deterministic_replay_exact"]
        and first["gates"]["production_incremental_budget_le_cap"]
    )

    first["scientific_pass"] = science_pass
    first["production_go"] = False
    first["decision"] = (
        "SMALL_EXACT_PHYSICAL_REPRESENTATION_GO"
        if science_pass
        else "TERMINAL_NO_GO_DROP_E118"
    )
    first["scope"] = {
        "smallwidth_exact_only": True,
        "production_execution": False,
        "public": False,
        "public_mini": False,
        "official_scorer": False,
        "holdout": False,
        "full_suite": False,
        "benchmark_targets": False,
        "tuning": False,
        "sweep": False,
        "rescue": False,
        "rerun": False,
        "canonical_mutated": False,
        "ledger_mutated": False,
    }

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    EXIT.write_text("0\n" if science_pass else "2\n", encoding="utf-8")
    print("E118_BOUNDARY_FLUX_PHYSICAL=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
