from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

EXPERIMENT = "E099"
WIDTH = 1024
DEPTH = 16
PI = 0.1
BUDGET = 2**41
UTIL_LIMIT = 0.135
DENSE_CEILING_MULTIPLIER = 12
RESULT_PATH = Path("e099_shared_latent_2g_result.json")


def exact_relu_standard_normal_moments() -> dict[str, float]:
    mean = 1.0 / math.sqrt(2.0 * math.pi)
    raw2 = 0.5
    raw3 = math.sqrt(2.0 / math.pi)
    var = raw2 - mean * mean
    kappa3 = raw3 - 3.0 * mean * raw2 + 2.0 * mean**3
    return {
        "mean": mean,
        "raw2": raw2,
        "raw3": raw3,
        "variance": var,
        "central_third": kappa3,
    }


def latent_moments(pi: float) -> dict[str, float]:
    a_plus = math.sqrt((1.0 - pi) / pi)
    a_minus = -math.sqrt(pi / (1.0 - pi))
    mean = pi * a_plus + (1.0 - pi) * a_minus
    raw2 = pi * a_plus**2 + (1.0 - pi) * a_minus**2
    raw3 = pi * a_plus**3 + (1.0 - pi) * a_minus**3
    return {
        "a_plus": a_plus,
        "a_minus": a_minus,
        "mean": mean,
        "raw2": raw2,
        "raw3": raw3,
    }


def run_once() -> dict:
    relu = exact_relu_standard_normal_moments()
    latent = latent_moments(PI)

    v = relu["variance"]
    k3 = relu["central_third"]
    m3s = latent["raw3"]
    if not (v > 0.0 and k3 > 0.0 and m3s > 0.0):
        raise RuntimeError("unexpected sign in frozen analytic moments")

    d_scalar = float(np.cbrt(k3 / m3s))
    d = np.full(WIDTH, d_scalar, dtype=np.float64)

    # Exact eigenstructure for Sigma0 = v I - d d^T:
    # eigenvalue v with multiplicity n-1 and v - ||d||^2 once.
    d_norm_sq = float(d @ d)
    lambda_min_closed = v - d_norm_sq

    sigma0 = np.eye(WIDTH, dtype=np.float64) * v - np.outer(d, d)
    target_cov = np.eye(WIDTH, dtype=np.float64) * v
    reconstructed_cov = sigma0 + np.outer(d, d)
    covariance_reconstruction_max_abs = float(
        np.max(np.abs(reconstructed_cov - target_cov))
    )

    reconstructed_k3 = m3s * d**3
    target_k3 = np.full(WIDTH, k3, dtype=np.float64)
    kappa3_reconstruction_max_abs = float(
        np.max(np.abs(reconstructed_k3 - target_k3))
    )

    # A cheap numerical sanity check of the closed-form bad direction.
    u = np.ones(WIDTH, dtype=np.float64) / math.sqrt(WIDTH)
    rayleigh_bad_direction = float(u @ sigma0 @ u)
    rayleigh_vs_closed_abs = abs(rayleigh_bad_direction - lambda_min_closed)

    dense_flops_ceiling = DENSE_CEILING_MULTIPLIER * DEPTH * WIDTH**3
    utilization_ceiling = dense_flops_ceiling / BUDGET
    hard_flops_limit = UTIL_LIMIT * BUDGET
    slack_flops = hard_flops_limit - dense_flops_ceiling

    gates = {
        "finite": bool(
            np.isfinite(
                [
                    v,
                    k3,
                    m3s,
                    d_scalar,
                    lambda_min_closed,
                    covariance_reconstruction_max_abs,
                    kappa3_reconstruction_max_abs,
                    rayleigh_bad_direction,
                    utilization_ceiling,
                ]
            ).all()
        ),
        "latent_mean_abs_le_1e_15": abs(latent["mean"]) <= 1e-15,
        "latent_variance_abs_err_le_1e_15": abs(latent["raw2"] - 1.0) <= 1e-15,
        "covariance_reconstruction_le_1e_12": covariance_reconstruction_max_abs
        <= 1e-12,
        "kappa3_reconstruction_le_1e_12": kappa3_reconstruction_max_abs <= 1e-12,
        "closed_form_rayleigh_parity_le_1e_12": rayleigh_vs_closed_abs <= 1e-12,
        "sigma0_psd": lambda_min_closed >= -1e-12,
        "budget_ceiling_le_0_135": utilization_ceiling <= UTIL_LIMIT,
    }

    terminal_no_go = not gates["sigma0_psd"]
    decision = (
        "TERMINAL_STRUCTURAL_NO_GO"
        if terminal_no_go
        else "STRUCTURAL_GO_NEXT_NONLINEAR_PROPAGATION_GATE"
    )

    return {
        "schema": "arc.whitebox.e099.shared_latent_2g_falsifier.v1",
        "experiment": EXPERIMENT,
        "identity": {
            "width": WIDTH,
            "depth": DEPTH,
            "pi": PI,
            "latent_components": 2,
            "shared_latent": True,
            "width_independent_component_weight": True,
        },
        "relu_exact_moments": relu,
        "latent_moments": latent,
        "forced_skew_direction": {
            "d_scalar": d_scalar,
            "d_norm_sq": d_norm_sq,
            "variance": v,
            "central_third": k3,
            "lambda_min_sigma0_closed_form": lambda_min_closed,
            "rayleigh_bad_direction": rayleigh_bad_direction,
            "rayleigh_vs_closed_abs": rayleigh_vs_closed_abs,
        },
        "reconstruction": {
            "covariance_max_abs": covariance_reconstruction_max_abs,
            "kappa3_max_abs": kappa3_reconstruction_max_abs,
        },
        "budget_first": {
            "formula": "12*depth*width^3",
            "dense_flops_ceiling": dense_flops_ceiling,
            "budget": BUDGET,
            "utilization_ceiling": utilization_ceiling,
            "utilization_limit": UTIL_LIMIT,
            "slack_flops_before_special_functions": slack_flops,
        },
        "gates": gates,
        "terminal_no_go": terminal_no_go,
        "scientific_go": False,
        "decision": decision,
        "scope": {
            "public": False,
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
    deterministic_repeat_max_abs = 0.0 if first == second else math.inf
    first["deterministic_repeat_max_abs"] = deterministic_repeat_max_abs
    first["gates"]["deterministic_repeat_eq_0"] = deterministic_repeat_max_abs == 0.0

    RESULT_PATH.write_text(
        json.dumps(first, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print("E099_SHARED_LATENT_2G_JSON=" + json.dumps(first, sort_keys=True))

    if not all(
        first["gates"][name]
        for name in (
            "finite",
            "latent_mean_abs_le_1e_15",
            "latent_variance_abs_err_le_1e_15",
            "covariance_reconstruction_le_1e_12",
            "kappa3_reconstruction_le_1e_12",
            "closed_form_rayleigh_parity_le_1e_12",
            "budget_ceiling_le_0_135",
            "deterministic_repeat_eq_0",
        )
    ):
        raise SystemExit("non-kill integrity gate failed")


if __name__ == "__main__":
    main()
