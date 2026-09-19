#!/usr/bin/env python3
"""E115 exact dense-Hermite-chaos budget/science falsifier.

No targets, Monte Carlo, numerical quadrature, or external dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


RAW_TARGET_MSE = 1.89e-8
BUDGET = 2**41
UTIL_CAP = 0.13
D = 1024
WIDTH = 1024
LATE_LAYERS = 2


def payload() -> dict[str, object]:
    mu2 = 1.0 / (2.0 * math.pi)

    # Exact Parseval residuals for f(z)=ReLU(z), z~N(0,1),
    # after orthogonal projection onto probabilists' Hermites.
    r1 = 0.25 - mu2
    r2 = 0.25 - 1.5 * mu2

    b1 = math.comb(D + 1, 1)
    b2 = math.comb(D + 2, 2)

    # Favorable lower bound: dense linear transport only, no nonlinear
    # reprojection and no inherited/base estimator work.
    f1 = LATE_LAYERS * 2 * WIDTH * WIDTH * b1
    f2 = LATE_LAYERS * 2 * WIDTH * WIDTH * b2
    u1 = f1 / BUDGET
    u2 = f2 / BUDGET

    gates = {
        "r1_above_raw_target": r1 > RAW_TARGET_MSE,
        "r2_above_raw_target": r2 > RAW_TARGET_MSE,
        "basis_degree1_exact": b1 == 1025,
        "basis_degree2_exact": b2 == 525825,
        "degree1_budget_admitted": u1 <= UTIL_CAP,
        "degree2_budget_rejected": u2 > UTIL_CAP,
    }

    decision = (
        "TERMINAL_NO_GO_DENSE_TOTAL_DEGREE_HERMITE_CHAOS"
        if all(gates.values())
        else "FALSIFIER_GATE_FAILURE"
    )

    return {
        "schema": "arc.whitebox.e115.hermite_chaos_falsifier.v1",
        "mechanism": "dense_total_degree_wiener_hermite_chaos_with_parseval_remainder",
        "target_free": True,
        "monte_carlo": False,
        "numerical_quadrature": False,
        "production_shape": {
            "latent_dimension": D,
            "width": WIDTH,
            "late_layers_billed": LATE_LAYERS,
            "budget_flops": BUDGET,
            "utilization_cap": UTIL_CAP,
        },
        "exact_scalar_relu": {
            "l2_norm_sq": 0.5,
            "c0": 1.0 / math.sqrt(2.0 * math.pi),
            "c1": 0.5,
            "c2": 1.0 / (2.0 * math.sqrt(2.0 * math.pi)),
            "degree1_parseval_remainder_mse": r1,
            "degree2_parseval_remainder_mse": r2,
            "raw_target_mse_scale": RAW_TARGET_MSE,
            "degree1_remainder_over_target": r1 / RAW_TARGET_MSE,
            "degree2_remainder_over_target": r2 / RAW_TARGET_MSE,
        },
        "dense_basis": {
            "degree1_count": b1,
            "degree2_count": b2,
        },
        "two_late_layer_linear_transport_lower_bound": {
            "degree1_flops": f1,
            "degree1_utilization": u1,
            "degree2_flops": f2,
            "degree2_utilization": u2,
            "degree2_over_util_cap": u2 / UTIL_CAP,
            "excludes_nonlinear_reprojection": True,
            "excludes_base_estimator": True,
        },
        "gates": gates,
        "decision": decision,
        "scope": {
            "rules_out": "dense total-degree chaos transport",
            "does_not_rule_out": "separately preregistered low-rank/tensorized chaos with rank-growth certificate",
        },
    }


def verify_exact_formulas(p: dict[str, object]) -> None:
    exact = p["exact_scalar_relu"]
    assert isinstance(exact, dict)

    # Independent coefficient-energy reconstruction.
    c0 = float(exact["c0"])
    c1 = float(exact["c1"])
    c2 = float(exact["c2"])
    l2 = float(exact["l2_norm_sq"])
    r1_energy = l2 - (c0 * c0 + c1 * c1)
    r2_energy = r1_energy - 2.0 * c2 * c2

    assert math.isclose(
        r1_energy,
        float(exact["degree1_parseval_remainder_mse"]),
        rel_tol=0.0,
        abs_tol=2e-16,
    )
    assert math.isclose(
        r2_energy,
        float(exact["degree2_parseval_remainder_mse"]),
        rel_tol=0.0,
        abs_tol=2e-16,
    )


def canonical_json(p: dict[str, object]) -> str:
    return json.dumps(p, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    first = payload()
    verify_exact_formulas(first)
    second = payload()
    verify_exact_formulas(second)

    first_json = canonical_json(first)
    second_json = canonical_json(second)
    if first_json != second_json:
        raise SystemExit("determinism failure")
    if first["decision"] != "TERMINAL_NO_GO_DENSE_TOTAL_DEGREE_HERMITE_CHAOS":
        raise SystemExit("frozen falsifier gates did not reach preregistered decision")

    report = dict(first)
    report["deterministic_replay_exact"] = True
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print("E115_HERMITE_CHAOS_FALSIFIER=" + canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
