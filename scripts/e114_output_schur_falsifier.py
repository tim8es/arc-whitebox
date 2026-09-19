from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_output_schur import (
    compressed_weights,
    exact_final_mean,
    exact_penultimate_preact_second_moment,
    layer2_intervals,
    make_network,
    output_weighted_diagonal,
    pooled_bias_mse,
    schur_rank_compression,
)

SEEDS = (114201, 114202, 114203, 114204)
WIDTH = 8
DEPTH = 4
RANK = 2
TARGET = 1.89e-8

BUDGET = 2**41
UTIL_CAP = 0.13
PROD_BASE_FLOPS = 149_114_620_592
PROD_ALL_IN_UPPER = 184_614_620_592
PROD_RANK = 64

OUT = Path("e114-output-schur-falsifier.json")
EXIT = Path("e114-output-schur-exit.txt")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def evaluate_seed(seed: int) -> dict:
    weights = make_network(seed=seed, width=WIDTH, depth=DEPTH)
    l2 = layer2_intervals(weights)
    m = exact_penultimate_preact_second_moment(l2, weights[2])
    d = output_weighted_diagonal(weights[3])
    comp = schur_rank_compression(m, d, rank=RANK)

    exact_mean, exact_intervals = exact_final_mean(weights)
    proxy_weights = compressed_weights(weights, comp["K"])
    proxy_mean, proxy_intervals = exact_final_mean(proxy_weights)
    actual = pooled_bias_mse(exact_mean, proxy_mean)

    finite = bool(
        np.isfinite(m).all()
        and np.isfinite(d).all()
        and np.isfinite(comp["K"]).all()
        and np.isfinite(comp["M_res"]).all()
        and np.isfinite(comp["B_eigenvalues"]).all()
        and np.isfinite(exact_mean).all()
        and np.isfinite(proxy_mean).all()
        and math.isfinite(actual)
        and math.isfinite(comp["remainder_bound"])
    )

    return {
        "seed": seed,
        "layer2_interval_count": len(l2),
        "exact_final_interval_count": exact_intervals,
        "proxy_final_interval_count": proxy_intervals,
        "second_moment_sha256": _sha(m),
        "reconstruction_sha256": _sha(np.asarray(comp["K"], dtype=np.float64)),
        "exact_final_mean_sha256": _sha(exact_mean),
        "proxy_final_mean_sha256": _sha(proxy_mean),
        "exact_final_mean": exact_mean.tolist(),
        "proxy_final_mean": proxy_mean.tolist(),
        "actual_pooled_final_mean_bias_mse": actual,
        "schur_remainder_bound_mse": float(comp["remainder_bound"]),
        "bound_over_target": float(comp["remainder_bound"] / TARGET),
        "actual_over_target": float(actual / TARGET),
        "bound_minus_actual": float(comp["remainder_bound"] - actual),
        "omitted_eigenvalue_sum": float(comp["omitted_eigenvalue_sum"]),
        "bound_vs_omitted_abs": float(
            abs(comp["remainder_bound"] - comp["omitted_eigenvalue_sum"])
        ),
        "weighted_spectrum": np.asarray(comp["B_eigenvalues"], dtype=np.float64).tolist(),
        "penultimate_second_moment_eigenvalues": np.asarray(
            comp["M_eigenvalues"], dtype=np.float64
        ).tolist(),
        "residual_min_eigenvalue": float(comp["min_residual_eigenvalue"]),
        "second_moment_support_rank": int(comp["support_rank"]),
        "finite": finite,
        "bound_valid": bool(actual <= comp["remainder_bound"] + 1e-12),
        "target_bound_pass": bool(comp["remainder_bound"] <= TARGET),
    }


def numeric_replay_delta(a: list[dict], b: list[dict]) -> float:
    keys = (
        "actual_pooled_final_mean_bias_mse",
        "schur_remainder_bound_mse",
        "bound_over_target",
        "actual_over_target",
        "bound_minus_actual",
        "omitted_eigenvalue_sum",
        "bound_vs_omitted_abs",
        "residual_min_eigenvalue",
    )
    delta = 0.0
    for x, y in zip(a, b, strict=True):
        for key in keys:
            delta = max(delta, abs(float(x[key]) - float(y[key])))
        delta = max(
            delta,
            float(
                np.max(
                    np.abs(
                        np.asarray(x["exact_final_mean"], dtype=np.float64)
                        - np.asarray(y["exact_final_mean"], dtype=np.float64)
                    )
                )
            ),
            float(
                np.max(
                    np.abs(
                        np.asarray(x["proxy_final_mean"], dtype=np.float64)
                        - np.asarray(y["proxy_final_mean"], dtype=np.float64)
                    )
                )
            ),
        )
    return delta


def main() -> None:
    first = [evaluate_seed(seed) for seed in SEEDS]
    second = [evaluate_seed(seed) for seed in SEEDS]
    replay_delta = numeric_replay_delta(first, second)

    bounds = np.asarray(
        [row["schur_remainder_bound_mse"] for row in first], dtype=np.float64
    )
    actuals = np.asarray(
        [row["actual_pooled_final_mean_bias_mse"] for row in first], dtype=np.float64
    )

    pooled_bound = float(np.mean(bounds))
    pooled_actual = float(np.mean(actuals))
    max_bound = float(np.max(bounds))
    max_actual = float(np.max(actuals))

    integrity = {
        "finite_all": all(row["finite"] for row in first),
        "bound_valid_all": all(row["bound_valid"] for row in first),
        "residual_psd_all": all(
            row["residual_min_eigenvalue"] >= -1e-10 for row in first
        ),
        "bound_matches_omitted_spectrum_all": all(
            row["bound_vs_omitted_abs"] <= 1e-10 for row in first
        ),
        "deterministic_replay_max_abs_eq_0": replay_delta == 0.0,
        "width_depth_exact": WIDTH == 8 and DEPTH == 4,
        "rank_exact": RANK == 2,
    }

    target_gates = {
        "every_seed_remainder_le_1_89e_8": bool(np.all(bounds <= TARGET)),
        "pooled_remainder_le_1_89e_8": pooled_bound <= TARGET,
    }

    cost = {
        "production_width": 1024,
        "production_depth": 16,
        "production_rank": PROD_RANK,
        "base_flops": PROD_BASE_FLOPS,
        "all_in_upper_flops": PROD_ALL_IN_UPPER,
        "budget": BUDGET,
        "utilization_cap": UTIL_CAP,
        "all_in_upper_utilization": PROD_ALL_IN_UPPER / BUDGET,
        "admission_pass": PROD_ALL_IN_UPPER / BUDGET <= UTIL_CAP,
    }

    scientific_pass = bool(all(integrity.values()) and all(target_gates.values()))
    decision = (
        "SMALL_EXACT_REMAINDER_GO_DEFINE_PRODUCTION_GATE"
        if scientific_pass
        else "TERMINAL_NO_GO_DROP_OUTPUT_SCHUR_VARIANT"
    )

    result = {
        "schema": "arc.whitebox.e114.output_schur_finalmean.v1",
        "experiment": "E114",
        "identity": "ARC-E114-OUTPUT-SCHUR-FINALMEAN-20260919",
        "identity_firewall": {
            "parent_e114_activation_flux_preserved": True,
            "this_variant_is_output_schur_compression": True,
            "not_e112_factorized_cumulants": True,
            "not_e112_mask_treewidth": True,
            "not_e113_topk_gates": True,
            "not_e110_line_rb": True,
            "not_gaussian_plugin": True,
        },
        "frozen_smallwidth": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "rank": RANK,
            "seeds": SEEDS,
            "zero_bias": True,
            "reference": "exact analytic angular sector integration",
            "numerical_quadrature": False,
            "monte_carlo_truth": False,
        },
        "rows": first,
        "summary": {
            "target_mse_scale": TARGET,
            "pooled_schur_remainder_bound_mse": pooled_bound,
            "max_seed_schur_remainder_bound_mse": max_bound,
            "pooled_actual_proxy_bias_mse": pooled_actual,
            "max_seed_actual_proxy_bias_mse": max_actual,
            "pooled_bound_over_target": pooled_bound / TARGET,
            "max_bound_over_target": max_bound / TARGET,
            "pooled_actual_over_target": pooled_actual / TARGET,
            "deterministic_replay_max_abs": replay_delta,
        },
        "integrity_gates": integrity,
        "target_scale_gates": target_gates,
        "production_cost_admission": cost,
        "scientific_pass": scientific_pass,
        "decision": decision,
        "scope": {
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
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    EXIT.write_text("0\n" if scientific_pass else "2\n", encoding="utf-8")
    print("E114_OUTPUT_SCHUR=" + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
