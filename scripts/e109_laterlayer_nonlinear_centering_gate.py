#!/usr/bin/env python3
"""E109 exact later-layer nonlinear centering falsifier."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

OUT = Path("e109_laterlayer_nonlinear_centering.json")


def expectation(law: list[tuple[Fraction, Fraction]], fn) -> Fraction:
    return sum((p * fn(x) for x, p in law), Fraction(0, 1))


def variance(law: list[tuple[Fraction, Fraction]]) -> Fraction:
    mu = expectation(law, lambda x: x)
    return expectation(law, lambda x: (x - mu) ** 2)


def relu(x: Fraction) -> Fraction:
    return x if x > 0 else Fraction(0, 1)


def exact_counterexample() -> dict:
    law_a = [
        (Fraction(-1, 1), Fraction(1, 2)),
        (Fraction(1, 1), Fraction(1, 2)),
    ]
    law_b = [
        (Fraction(-2, 1), Fraction(1, 8)),
        (Fraction(0, 1), Fraction(3, 4)),
        (Fraction(2, 1), Fraction(1, 8)),
    ]

    a_mean = expectation(law_a, lambda x: x)
    b_mean = expectation(law_b, lambda x: x)
    a_var = variance(law_a)
    b_var = variance(law_b)
    a_relu = expectation(law_a, relu)
    b_relu = expectation(law_b, relu)

    return {
        "law_a_mean": str(a_mean),
        "law_b_mean": str(b_mean),
        "law_a_variance": str(a_var),
        "law_b_variance": str(b_var),
        "law_a_relu_mean": str(a_relu),
        "law_b_relu_mean": str(b_relu),
        "same_mean_variance": a_mean == b_mean == 0 and a_var == b_var == 1,
        "different_relu_mean": a_relu != b_relu,
        "relu_gap": str(a_relu - b_relu),
    }


def depth2_identity() -> dict:
    # q=+1 -> h1=(1,0), q=-1 -> h1=(0,1), second-layer weight=(1,-2)
    u_plus = Fraction(1, 1)
    u_minus = Fraction(-2, 1)
    exact_pair = (relu(u_plus) + relu(u_minus)) / 2
    linear_term = (u_plus + u_minus) / 4
    absolute_term = (abs(u_plus) + abs(u_minus)) / 4
    return {
        "u_plus": str(u_plus),
        "u_minus": str(u_minus),
        "linear_term": str(linear_term),
        "absolute_term": str(absolute_term),
        "exact_pair_relu_mean": str(exact_pair),
        "identity_holds": exact_pair == linear_term + absolute_term,
        "nonlinear_term_exceeds_linear_magnitude": abs(absolute_term) > abs(linear_term),
    }


def antisymmetry_fixture(alpha: Fraction = Fraction(1, 1)) -> dict:
    # IID block state S=(Y,G), with Y=G in {-1,+1} equiprobably.
    single = [
        (Fraction(-1, 1), Fraction(-1, 1), Fraction(1, 2)),
        (Fraction(1, 1), Fraction(1, 1), Fraction(1, 2)),
    ]

    rows: list[tuple[Fraction, Fraction, Fraction]] = []
    for ya, ga, pa in single:
        for yb, gb, pb in single:
            prob = pa * pb
            baseline = (ya + yb) / 2
            control = ga - gb
            rows.append((baseline, control, prob))

    e_b = sum((p * b for b, _, p in rows), Fraction(0, 1))
    e_c = sum((p * c for _, c, p in rows), Fraction(0, 1))
    cov = sum((p * (b - e_b) * (c - e_c) for b, c, p in rows), Fraction(0, 1))
    var_b = sum((p * (b - e_b) ** 2 for b, _, p in rows), Fraction(0, 1))
    var_c = sum((p * (c - e_c) ** 2 for _, c, p in rows), Fraction(0, 1))

    corrected = [(b - alpha * c, p) for b, c, p in rows]
    e_corr = sum((p * x for x, p in corrected), Fraction(0, 1))
    var_corr = sum((p * (x - e_corr) ** 2 for x, p in corrected), Fraction(0, 1))
    rhs = var_b + alpha * alpha * var_c

    swap_antisymmetry = True
    for ya, ga, _ in single:
        for yb, gb, _ in single:
            c_ab = ga - gb
            c_ba = gb - ga
            swap_antisymmetry &= c_ba == -c_ab

    return {
        "alpha": str(alpha),
        "baseline_mean": str(e_b),
        "control_mean": str(e_c),
        "baseline_control_covariance": str(cov),
        "baseline_variance": str(var_b),
        "control_variance": str(var_c),
        "corrected_variance": str(var_corr),
        "variance_identity_rhs": str(rhs),
        "swap_antisymmetry": swap_antisymmetry,
        "covariance_zero": cov == 0,
        "variance_identity_holds": var_corr == rhs,
        "correction_strictly_worsens_variance": var_corr > var_b,
    }


def run_once() -> dict:
    counterexample = exact_counterexample()
    depth2 = depth2_identity()
    antisym = antisymmetry_fixture()

    gates = {
        "moment2_counterexample_exact": (
            counterexample["same_mean_variance"]
            and counterexample["different_relu_mean"]
            and counterexample["law_a_relu_mean"] == "1/2"
            and counterexample["law_b_relu_mean"] == "1/4"
        ),
        "depth2_relu_identity_exact": (
            depth2["identity_holds"]
            and depth2["linear_term"] == "-1/4"
            and depth2["absolute_term"] == "3/4"
            and depth2["exact_pair_relu_mean"] == "1/2"
            and depth2["nonlinear_term_exceeds_linear_magnitude"]
        ),
        "antisymmetric_control_zero_mean": (
            antisym["swap_antisymmetry"] and antisym["control_mean"] == "0"
        ),
        "symmetric_baseline_orthogonal_to_antisymmetric_control": (
            antisym["covariance_zero"]
            and antisym["baseline_control_covariance"] == "0"
        ),
        "fixed_alpha_variance_cannot_improve": (
            antisym["variance_identity_holds"]
            and antisym["baseline_variance"] == "1/2"
            and antisym["control_variance"] == "2"
            and antisym["corrected_variance"] == "5/2"
            and antisym["correction_strictly_worsens_variance"]
        ),
    }

    return {
        "schema": "arc.whitebox.e109.laterlayer_nonlinear_centering_gate.v1",
        "experiment": "E109",
        "counterexample": counterexample,
        "depth2_identity": depth2,
        "antisymmetry_fixture": antisym,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "decision": (
            "STRUCTURAL_GATE_ESTABLISHED_MOMENT2_AND_ANTISYMMETRIC_CENTERING_NO_GO"
            if all(gates.values())
            else "IDENTITY_CHECK_FAILED"
        ),
        "next_gate": (
            "A deep nonlinear successor must exhibit an exactly centered "
            "later-layer statistic whose actual control is not antisymmetric "
            "under the two-Haar block swap."
        ),
        "scope": {
            "targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "e104_rerun": False,
            "production_estimator_run": False,
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
        first["decision"] = "IDENTITY_CHECK_FAILED"

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E109_LATERLAYER_CENTERING=" + json.dumps(first, sort_keys=True), flush=True)
    if not first["all_gates_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
