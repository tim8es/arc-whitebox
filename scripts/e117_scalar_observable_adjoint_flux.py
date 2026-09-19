#!/usr/bin/env python3
"""E117 exact scalar-observable adjoint boundary-flux factorization test."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

OUT = Path("e117_scalar_observable_adjoint_flux.json")
TOL = 1e-14

F = Fraction

W1 = [[F(1), F(0)], [F(0), F(1)]]
W2 = [[F(1), F(1)], [F(-2), F(0)]]
W3 = [[F(2)], [F(-1)]]


def row_matmul(v, M):
    return [
        sum((v[i] * M[i][j] for i in range(len(v))), F(0))
        for j in range(len(M[0]))
    ]


def matvec(M, v):
    return [
        sum((M[i][j] * v[j] for j in range(len(v))), F(0))
        for i in range(len(M))
    ]


def hadamard(v, mask):
    return [x * F(int(m)) for x, m in zip(v, mask)]


def forward_masks(x):
    z1 = row_matmul(x, W1)
    m1 = tuple(z > 0 for z in z1)
    h1 = [z if m else F(0) for z, m in zip(z1, m1)]

    z2 = row_matmul(h1, W2)
    m2 = tuple(z > 0 for z in z2)
    h2 = [z if m else F(0) for z, m in zip(z2, m2)]

    z3 = row_matmul(h2, W3)
    m3 = (z3[0] > 0,)
    y = z3[0] if m3[0] else F(0)

    return {
        "z1": z1,
        "m1": m1,
        "z2": z2,
        "m2": m2,
        "z3": z3,
        "m3": m3,
        "y": y,
    }


def scalar_region_gradient(m1, m2, m3):
    # F = x W1 D1 W2 D2 W3 D3
    v = [W3[i][0] * F(int(m3[0])) for i in range(2)]
    v = hadamard(v, m2)
    v = matvec(W2, v)
    v = hadamard(v, m1)
    v = matvec(W1, v)
    return v


def l1_preactivation_gradient(j):
    return [W1[i][j] for i in range(2)]


def l1_downstream_adjoint(j, active_masks):
    m2 = active_masks["m2"]
    m3 = active_masks["m3"]
    v = [W3[i][0] * F(int(m3[0])) for i in range(2)]
    v = hadamard(v, m2)
    sens_h1 = matvec(W2, v)
    return sens_h1[j]


def final_preactivation_gradient(active_masks):
    m1 = active_masks["m1"]
    m2 = active_masks["m2"]
    # preactivation z3 excludes final ReLU mask.
    v = [W3[i][0] for i in range(2)]
    v = hadamard(v, m2)
    v = matvec(W2, v)
    v = hadamard(v, m1)
    return matvec(W1, v)


def vec_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def vec_scale(a, s):
    return [s * x for x in a]


def norm_float(a):
    return math.sqrt(sum(float(x * x) for x in a))


def as_strings(v):
    return [str(x) for x in v]


def facet_record(name, active_x, inactive_x, layer, neuron):
    active = forward_masks(active_x)
    inactive = forward_masks(inactive_x)

    g_active = scalar_region_gradient(active["m1"], active["m2"], active["m3"])
    g_inactive = scalar_region_gradient(
        inactive["m1"], inactive["m2"], inactive["m3"]
    )
    full_jump = vec_sub(g_active, g_inactive)

    if layer == 1:
        a = l1_preactivation_gradient(neuron)
        lam = l1_downstream_adjoint(neuron, active)
    elif layer == 3:
        a = final_preactivation_gradient(active)
        lam = F(1)
    else:
        raise ValueError("unsupported frozen facet layer")

    factored_jump = vec_scale(a, lam)
    exact_vector_identity = full_jump == factored_jump
    flux = float(lam) * norm_float(a)

    return {
        "name": name,
        "layer": layer,
        "neuron": neuron,
        "active_point": as_strings(active_x),
        "inactive_point": as_strings(inactive_x),
        "active_masks": {
            "m1": list(active["m1"]),
            "m2": list(active["m2"]),
            "m3": list(active["m3"]),
        },
        "inactive_masks": {
            "m1": list(inactive["m1"]),
            "m2": list(inactive["m2"]),
            "m3": list(inactive["m3"]),
        },
        "preactivation_input_gradient": as_strings(a),
        "scalar_downstream_adjoint": str(lam),
        "full_region_gradient_active": as_strings(g_active),
        "full_region_gradient_inactive": as_strings(g_inactive),
        "full_gradient_jump": as_strings(full_jump),
        "factored_gradient_jump": as_strings(factored_jump),
        "exact_vector_factorization": exact_vector_identity,
        "preactivation_gradient_norm": norm_float(a),
        "scalar_flux": flux,
    }


def run_once():
    # Points are integer/rational representatives of the adjacent regular cells.
    facets = [
        facet_record(
            "first_layer_x1_gate",
            [F(1), F(-1)],
            [F(-1), F(-1)],
            1,
            0,
        ),
        facet_record(
            "first_layer_x2_gate",
            [F(5), F(1)],
            [F(1), F(-1)],
            1,
            1,
        ),
        facet_record(
            "final_layer_gate",
            [F(5), F(1)],
            [F(3), F(1)],
            3,
            0,
        ),
    ]

    fluxes = [row["scalar_flux"] for row in facets]
    expected = [1.0, -4.0, math.sqrt(17.0)]
    flux_errors = [abs(a - b) for a, b in zip(fluxes, expected)]
    flux_sum = sum(fluxes)
    expected_sum = math.sqrt(17.0) - 3.0

    gaussian_from_scalar_flux = (
        math.sqrt(math.pi / 2.0) * flux_sum / (2.0 * math.pi)
    )
    gaussian_closed_form = (
        (math.sqrt(17.0) - 3.0) / (2.0 * math.sqrt(2.0 * math.pi))
    )

    gates = {
        "all_exact_gradient_factorizations": all(
            row["exact_vector_factorization"] for row in facets
        ),
        "facet_fluxes_match_1_minus4_sqrt17": max(flux_errors) <= TOL,
        "scalar_flux_sum_eq_sqrt17_minus3": abs(flux_sum - expected_sum) <= TOL,
        "gaussian_expectation_match": (
            abs(gaussian_from_scalar_flux - gaussian_closed_form) <= TOL
        ),
        "first_facet_lambda_eq_1": (
            facets[0]["scalar_downstream_adjoint"] == "1"
        ),
        "second_facet_lambda_eq_minus4": (
            facets[1]["scalar_downstream_adjoint"] == "-4"
        ),
        "final_facet_lambda_eq_1": (
            facets[2]["scalar_downstream_adjoint"] == "1"
        ),
        "final_gate_normal_eq_1_minus4": (
            facets[2]["preactivation_input_gradient"] == ["1", "-4"]
        ),
    }

    return {
        "schema": "arc.whitebox.e117.scalar_observable_adjoint_flux.v1",
        "experiment": "E117",
        "facets": facets,
        "scalar_fluxes": fluxes,
        "expected_scalar_fluxes": expected,
        "max_flux_abs_error": max(flux_errors),
        "scalar_flux_sum": flux_sum,
        "expected_flux_sum": expected_sum,
        "gaussian_expectation_from_scalar_flux": gaussian_from_scalar_flux,
        "gaussian_expectation_closed_form": gaussian_closed_form,
        "closed_form_expression": "(sqrt(17)-3)/(2*sqrt(2*pi))",
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "decision": (
            "EXACT_POSITIVE_SCALAR_OBSERVABLE_CONDITIONAL_TRANSPORT_VERIFIED"
            if all(gates.values())
            else "IDENTITY_GATE_FAILED"
        ),
        "scope": {
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "monte_carlo": False,
            "numerical_quadrature": False,
            "production_run": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main():
    first = run_once()
    second = run_once()
    deterministic = first == second
    first["deterministic_repeat_exact"] = deterministic
    first["all_gates_pass"] = bool(first["all_gates_pass"] and deterministic)
    if not deterministic:
        first["decision"] = "IDENTITY_GATE_FAILED"

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E117_SCALAR_OBSERVABLE_ADJOINT_FLUX=" + json.dumps(first, sort_keys=True))
    if not first["all_gates_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
