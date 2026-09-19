#!/usr/bin/env python3
"""E114 exact activation-boundary flux identity test."""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path("e114_activation_boundary_flux.json")
TOL = 1e-14


def relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def network(theta: float) -> float:
    x1 = math.cos(theta)
    x2 = math.sin(theta)

    h1_1 = relu(x1)
    h1_2 = relu(x2)

    u1 = relu(h1_1 - 2.0 * h1_2)
    u2 = relu(h1_1)

    return relu(2.0 * u1 - u2)


def piecewise(theta: float, alpha: float) -> float:
    if -math.pi / 2.0 < theta < 0.0:
        return math.cos(theta)
    if 0.0 < theta < alpha:
        return math.cos(theta) - 4.0 * math.sin(theta)
    return 0.0


def tangent(theta: float) -> tuple[float, float]:
    return (-math.sin(theta), math.cos(theta))


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def derivative_jump(
    theta: float,
    left_coeff: tuple[float, float],
    right_coeff: tuple[float, float],
) -> float:
    delta = (
        right_coeff[0] - left_coeff[0],
        right_coeff[1] - left_coeff[1],
    )
    return dot(delta, tangent(theta))


def sector_integral(
    a: float,
    b: float,
    coeff: tuple[float, float],
) -> float:
    c1, c2 = coeff
    return (
        c1 * (math.sin(b) - math.sin(a))
        + c2 * (-math.cos(b) + math.cos(a))
    )


def run_once() -> dict:
    alpha = math.atan(0.25)
    sqrt17 = math.sqrt(17.0)
    expected_angular_integral = sqrt17 - 3.0

    # Final-output linear-region coefficients f(theta)=a dot q(theta).
    zero = (0.0, 0.0)
    lower_right = (1.0, 0.0)
    upper_wedge = (1.0, -4.0)

    check_angles = [
        -3.0 * math.pi / 4.0,  # inactive
        -math.pi / 4.0,        # lower-right active sector
        alpha / 2.0,           # third-layer active wedge
        0.5 * (alpha + math.pi / 2.0),  # inactive after third-layer kink
        math.pi,                # inactive opposite direction
    ]
    direct_diffs = [
        abs(network(theta) - piecewise(theta, alpha))
        for theta in check_angles
    ]
    direct_max_abs = max(direct_diffs)

    jump_minus_pi_over_2 = derivative_jump(
        -math.pi / 2.0, zero, lower_right
    )
    jump_zero = derivative_jump(0.0, lower_right, upper_wedge)
    jump_alpha = derivative_jump(alpha, upper_wedge, zero)
    jump_sum = jump_minus_pi_over_2 + jump_zero + jump_alpha

    integral_lower = sector_integral(
        -math.pi / 2.0, 0.0, lower_right
    )
    integral_upper = sector_integral(0.0, alpha, upper_wedge)
    sector_sum = integral_lower + integral_upper

    mean_radius_2d = math.sqrt(math.pi / 2.0)
    boundary_gaussian_mean = mean_radius_2d * jump_sum / (2.0 * math.pi)
    closed_form_gaussian_mean = (
        (sqrt17 - 3.0) / (2.0 * math.sqrt(2.0 * math.pi))
    )

    first_layer_boundaries = [
        -math.pi,
        -math.pi / 2.0,
        0.0,
        math.pi / 2.0,
        math.pi,
    ]
    distance_to_first_layer_boundary = min(
        abs(alpha - b) for b in first_layer_boundaries
    )

    gates = {
        "direct_network_matches_piecewise_le_1e_14": direct_max_abs <= TOL,
        "jump_minus_pi_over_2_eq_1": abs(jump_minus_pi_over_2 - 1.0) <= TOL,
        "jump_zero_eq_minus_4": abs(jump_zero + 4.0) <= TOL,
        "jump_alpha_eq_sqrt17": abs(jump_alpha - sqrt17) <= TOL,
        "jump_sum_eq_sqrt17_minus_3": (
            abs(jump_sum - expected_angular_integral) <= TOL
        ),
        "sector_integral_eq_sqrt17_minus_3": (
            abs(sector_sum - expected_angular_integral) <= TOL
        ),
        "boundary_flux_eq_sector_integral": abs(jump_sum - sector_sum) <= TOL,
        "gaussian_mean_closed_form_match": (
            abs(boundary_gaussian_mean - closed_form_gaussian_mean) <= TOL
        ),
        "downstream_kink_not_first_layer_boundary": (
            distance_to_first_layer_boundary > 1e-6
        ),
    }

    return {
        "schema": "arc.whitebox.e114.activation_boundary_flux.v1",
        "experiment": "E114",
        "fixture": {
            "input_dimension": 2,
            "depth": 3,
            "W1": [[1.0, 0.0], [0.0, 1.0]],
            "W2": [[1.0, 1.0], [-2.0, 0.0]],
            "W3": [[2.0], [-1.0]],
            "downstream_kink_angle": alpha,
            "downstream_kink_tan": 0.25,
        },
        "interior_direct_check_angles": check_angles,
        "direct_piecewise_max_abs": direct_max_abs,
        "derivative_jumps": {
            "minus_pi_over_2": jump_minus_pi_over_2,
            "zero": jump_zero,
            "atan_1_over_4": jump_alpha,
            "sum": jump_sum,
            "closed_form_sum": expected_angular_integral,
        },
        "sector_integrals": {
            "lower_right": integral_lower,
            "upper_wedge": integral_upper,
            "sum": sector_sum,
            "closed_form_sum": expected_angular_integral,
        },
        "gaussian_expectation": {
            "mean_radius_2d": mean_radius_2d,
            "boundary_flux_value": boundary_gaussian_mean,
            "closed_form_value": closed_form_gaussian_mean,
            "closed_form_expression": "(sqrt(17)-3)/(2*sqrt(2*pi))",
        },
        "first_layer_boundary_distance_of_downstream_kink": (
            distance_to_first_layer_boundary
        ),
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "decision": (
            "EXACT_POSITIVE_CLOSURE_ACTIVATION_BOUNDARY_FLUX_VERIFIED"
            if all(gates.values())
            else "IDENTITY_GATE_FAILED"
        ),
        "scope": {
            "monte_carlo": False,
            "numerical_quadrature": False,
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


def main() -> None:
    first = run_once()
    second = run_once()
    deterministic = first == second
    first["deterministic_repeat_exact"] = deterministic
    first["all_gates_pass"] = bool(first["all_gates_pass"] and deterministic)
    if not deterministic:
        first["decision"] = "IDENTITY_GATE_FAILED"

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E114_BOUNDARY_FLUX=" + json.dumps(first, sort_keys=True), flush=True)
    if not first["all_gates_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
