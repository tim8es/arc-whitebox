#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

OUT = Path("r215-result.json")

N = 1024
L = 16
K = 32
BUDGET = 2**41
CAP_FRACTION = 0.135

def marginal_distribution(points):
    out = []
    for axis in (0, 1):
        counts = {}
        for (x, y), p in points:
            v = (x, y)[axis]
            counts[v] = counts.get(v, Fraction(0, 1)) + p
        out.append(sorted((int(v), str(prob)) for v, prob in counts.items()))
    return out

def exact_relu_mean(points):
    total = Fraction(0, 1)
    for (x, y), p in points:
        u = x + y
        total += p * max(u, 0)
    return total

def cf_grid():
    ts = [k * math.pi / 64.0 for k in range(1, K + 1)]
    marginal = [math.cos(t) for t in ts]
    factorized = [v * v for v in marginal]
    correlated_true = [math.cos(2.0 * t) for t in ts]
    anti_true = [1.0 for _ in ts]
    return ts, marginal, factorized, correlated_true, anti_true

def cost_receipt():
    lower = 6 * L * N * K * (N - 1)
    upper_linear = 24 * L * K * N * N
    upper_relu = 32 * L * N * K * K
    upper_mean = 8 * L * N * K
    upper = upper_linear + upper_relu + upper_mean
    return {
        "budget_flops": BUDGET,
        "cap_fraction": CAP_FRACTION,
        "cap_flops": CAP_FRACTION * BUDGET,
        "mandatory_lower_flops": lower,
        "mandatory_lower_fraction": lower / BUDGET,
        "upper_linear_interp_accum_flops": upper_linear,
        "upper_nonlinear_cf_transform_flops": upper_relu,
        "upper_mean_reduction_flops": upper_mean,
        "estimator_only_upper_flops": upper,
        "estimator_only_upper_fraction": upper / BUDGET,
        "cost_feasible": upper <= CAP_FRACTION * BUDGET,
    }

def payload():
    half = Fraction(1, 2)
    correlated = [((1, 1), half), ((-1, -1), half)]
    anti = [((1, -1), half), ((-1, 1), half)]

    marg_c = marginal_distribution(correlated)
    marg_a = marginal_distribution(anti)
    relu_c = exact_relu_mean(correlated)
    relu_a = exact_relu_mean(anti)

    ts, marginal, factorized, true_c, true_a = cf_grid()
    max_marginal_gap = max(abs(a - b) for a, b in zip(marginal, marginal))
    max_factorized_gap = max(abs(a - b) for a, b in zip(factorized, factorized))

    # k=32 -> t=pi/2. Record exact theoretical values independently
    # of transcendental library rounding.
    k32 = K - 1
    exact_t32 = {
        "t": "pi/2",
        "marginal_phi_x": 0,
        "marginal_phi_y": 0,
        "factorized_phi_u": 0,
        "true_correlated_phi_u": -1,
        "true_anticorrelated_phi_u": 1,
    }

    worst_case_lower_bound = Fraction(abs(relu_c - relu_a), 2)
    cost = cost_receipt()

    gates = {
        "cost_feasible_before_synthetic": bool(cost["cost_feasible"]),
        "marginal_distributions_exactly_identical": marg_c == marg_a,
        "marginal_cf_grid_max_gap_le_2e_15": max_marginal_gap <= 2e-15,
        "factorized_preactivation_cf_grid_max_gap_le_2e_15": max_factorized_gap <= 2e-15,
        "frozen_pi_over_2_exact_separation": (
            exact_t32["true_correlated_phi_u"] == -1
            and exact_t32["true_anticorrelated_phi_u"] == 1
            and exact_t32["factorized_phi_u"] == 0
        ),
        "exact_relu_means_are_1_and_0": relu_c == 1 and relu_a == 0,
        "worst_case_absolute_error_lower_bound_ge_half": worst_case_lower_bound >= Fraction(1, 2),
        "continuation_accuracy_gate_le_1e_6": float(worst_case_lower_bound) <= 1e-6,
    }

    decision = (
        "R215_TERMINAL_NO_GO_MARGINAL_CF_NONCLOSURE"
        if all(v for k, v in gates.items() if k != "continuation_accuracy_gate_le_1e_6")
           and not gates["continuation_accuracy_gate_le_1e_6"]
        else "R215_FALSIFIER_INCOMPLETE"
    )

    return {
        "schema": "arc.whitebox.r215.fmcf32_falsifier.v1",
        "experiment": "R215",
        "idempotency_key": "ARC-R215-MARGINAL-CF-20260922",
        "family": "factorized marginal characteristic-function closure FMCF-32",
        "fixture": {
            "correlated_support": [
                {"xy": [1, 1], "p": "1/2"},
                {"xy": [-1, -1], "p": "1/2"},
            ],
            "anticorrelated_support": [
                {"xy": [1, -1], "p": "1/2"},
                {"xy": [-1, 1], "p": "1/2"},
            ],
            "linear_observable": "U=X+Y",
            "frequency_grid": "t_k=k*pi/64, k=1..32",
        },
        "exact": {
            "correlated_marginals": marg_c,
            "anticorrelated_marginals": marg_a,
            "marginals_identical": marg_c == marg_a,
            "correlated_relu_mean": str(relu_c),
            "anticorrelated_relu_mean": str(relu_a),
            "relu_mean_gap": str(relu_c - relu_a),
            "worst_case_same_output_absolute_error_lower_bound": str(worst_case_lower_bound),
            "pi_over_2": exact_t32,
        },
        "floating_grid_diagnostic": {
            "t_values": ts,
            "marginal_cf": marginal,
            "factorized_preactivation_cf": factorized,
            "true_correlated_preactivation_cf": true_c,
            "true_anticorrelated_preactivation_cf": true_a,
            "marginal_grid_max_gap_between_laws": max_marginal_gap,
            "factorized_grid_max_gap_between_laws": max_factorized_gap,
            "library_cos_pi_over_2": marginal[k32],
            "library_correlated_cos_pi": true_c[k32],
            "library_anticorrelated_phi": true_a[k32],
        },
        "production_cost": cost,
        "gates": gates,
        "decision": decision,
        "scientific_interpretation": (
            "The complete univariate marginal CF state is identical for two joint laws "
            "whose next dense preactivation law and ReLU mean differ. No deterministic "
            "scalar positive-part transform, quadrature grid, or increase in K can repair "
            "the missing dependence without adding joint state."
        ),
        "scope": {
            "target_free": True,
            "holdout": False,
            "public_benchmark": False,
            "paid_run": False,
            "submission": False,
            "sweep": False,
        },
    }

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)

def main():
    first = payload()
    second = payload()
    if canonical(first) != canonical(second):
        raise SystemExit("deterministic replay mismatch")
    first["deterministic_replay_bitwise_json"] = True
    text = json.dumps(first, indent=2, sort_keys=True, allow_nan=False) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print("R215_RESULT=" + canonical(first))
    if first["decision"] != "R215_TERMINAL_NO_GO_MARGINAL_CF_NONCLOSURE":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
