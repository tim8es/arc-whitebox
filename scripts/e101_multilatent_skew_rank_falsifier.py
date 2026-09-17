#!/usr/bin/env python3
"""E101 deterministic multi-latent skew-rank lower-bound falsifier."""

from __future__ import annotations

import json
import math
from pathlib import Path

EXPERIMENT = "E101"
N = 1024
PI = 0.1
MAX_COMPACT_RANK = 64
RESULT_PATH = Path("e101_multilatent_skew_rank_result.json")
E099_LAMBDA_MIN_REFERENCE = -252.126983267117


def run_once() -> dict:
    mu = 1.0 / math.sqrt(2.0 * math.pi)
    raw2 = 0.5
    raw3 = math.sqrt(2.0 / math.pi)
    variance = raw2 - mu * mu
    kappa3 = raw3 - 3.0 * mu * raw2 + 2.0 * mu**3

    a_plus = math.sqrt((1.0 - PI) / PI)
    a_minus = -math.sqrt(PI / (1.0 - PI))
    latent_mean = PI * a_plus + (1.0 - PI) * a_minus
    latent_raw2 = PI * a_plus**2 + (1.0 - PI) * a_minus**2
    latent_m3 = PI * a_plus**3 + (1.0 - PI) * a_minus**3

    c = kappa3 / latent_m3
    min_row_latent_variance = c ** (2.0 / 3.0)
    rank_lower_bound_real = N * min_row_latent_variance / variance
    rank_lower_bound_integer = math.ceil(rank_lower_bound_real - 1e-15)

    # The single-shared-latent E099 obstruction is the rank-one special case.
    e099_lambda_min = variance - N * min_row_latent_variance
    e099_crosscheck_abs = abs(e099_lambda_min - E099_LAMBDA_MIN_REFERENCE)

    log10_explicit_states = rank_lower_bound_integer * math.log10(2.0)
    scientific_gates = {
        "latent_rank_le_64": rank_lower_bound_integer <= MAX_COMPACT_RANK,
        "explicit_state_exponent_le_64": rank_lower_bound_integer <= MAX_COMPACT_RANK,
    }
    integrity_gates = {
        "finite": all(
            math.isfinite(x)
            for x in (
                mu,
                variance,
                kappa3,
                latent_mean,
                latent_raw2,
                latent_m3,
                c,
                min_row_latent_variance,
                rank_lower_bound_real,
                e099_lambda_min,
                log10_explicit_states,
            )
        ),
        "latent_mean_abs_le_1e_15": abs(latent_mean) <= 1e-15,
        "latent_variance_abs_err_le_1e_15": abs(latent_raw2 - 1.0) <= 1e-15,
        "e099_rank1_crosscheck_le_1e_9": e099_crosscheck_abs <= 1e-9,
    }

    decision = (
        "ANALYTIC_GO"
        if all(scientific_gates.values())
        else "TERMINAL_ANALYTIC_NO_GO"
    )
    return {
        "schema": "arc.whitebox.e101.multilatent_skew_rank_bound.v1",
        "experiment": EXPERIMENT,
        "identity": {
            "width": N,
            "pi": PI,
            "max_compact_rank": MAX_COMPACT_RANK,
            "independent_standardized_binary_latents": True,
        },
        "relu_exact_moments": {
            "mean": mu,
            "variance": variance,
            "central_third": kappa3,
        },
        "latent_exact_moments": {
            "a_plus": a_plus,
            "a_minus": a_minus,
            "mean": latent_mean,
            "variance": latent_raw2,
            "m3": latent_m3,
        },
        "lower_bound": {
            "c_kappa3_over_m3": c,
            "min_row_latent_variance_c_pow_2_over_3": min_row_latent_variance,
            "formula": "m >= n*(kappa3/m3)^(2/3)/variance",
            "rank_lower_bound_real": rank_lower_bound_real,
            "rank_lower_bound_integer": rank_lower_bound_integer,
            "rank_fraction_of_width": rank_lower_bound_integer / N,
            "explicit_mixture_state_exponent": rank_lower_bound_integer,
            "explicit_mixture_state_log10": log10_explicit_states,
        },
        "e099_rank1_crosscheck": {
            "lambda_min": e099_lambda_min,
            "reference": E099_LAMBDA_MIN_REFERENCE,
            "abs_error": e099_crosscheck_abs,
        },
        "integrity_gates": integrity_gates,
        "scientific_gates": scientific_gates,
        "scientific_go": decision == "ANALYTIC_GO",
        "decision": decision,
        "scope": {
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "benchmark_holdout": False,
            "full_suite": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main() -> None:
    first = run_once()
    second = run_once()
    deterministic_repeat = first == second
    first["deterministic_repeat_max_abs"] = 0.0 if deterministic_repeat else math.inf
    first["integrity_gates"]["deterministic_repeat_eq_0"] = deterministic_repeat

    RESULT_PATH.write_text(
        json.dumps(first, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print("E101_MULTILATENT_SKEW_RANK_JSON=" + json.dumps(first, sort_keys=True))

    if not all(first["integrity_gates"].values()):
        raise SystemExit("E101 integrity gate failed")


if __name__ == "__main__":
    main()
