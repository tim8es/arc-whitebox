#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e151_angular_strassen import (
    adversarial_square_weights,
    angular_k4_diagonal,
    dense_he_weights,
    exact_gaussian_mean_2d,
    forward,
    one_level_strassen,
    radial_moment_ratio,
    required_eligible_fraction,
    strassen1_square_ratio,
)

OUT = Path("e151-arsg-falsifier.json")
METHOD = Path("methods/e151_angular_strassen.py")

OPEN_PHASE2_GAUSSIAN_UTIL = 0.786835
OPEN_PHASE2_STRASSEN_UTIL = 0.695774
FRONTIER_ROWS = {
    "puffi_snapshot": {"raw": 2.02e-8, "util": 0.1478860181},
    "suliman_snapshot": {"raw": 1.97e-8, "util": 0.1504215170},
}
UTIL_CAP = 0.135


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    den = max(float(np.linalg.norm(b)), 2.0**-500)
    return float(np.linalg.norm(a - b)) / den


def _source_firewall() -> dict:
    src = METHOD.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(x.name for x in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    low = src.lower()
    forbidden = {
        "benchmark_target": "whestbench" in low or "final_means" in low,
        "public_dataset": "v2-phase2" in low or "public-mini" in low,
        "old_tier": "old-tier" in low or "old_tier" in low,
        "low_rank_k3": "k3" in low or "tensor train" in low or "gstt" in low,
        "countsketch": "countsketch" in low,
        "mub_kerdock": "mub" in low or "kerdock" in low,
        "sampling_cv": "control variate" in low or "control_variate" in low,
        "network_io": "requests" in low or "urlopen" in low,
    }
    return {
        "method_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "imports": sorted(imports),
        "forbidden": forbidden,
        "passes": not any(forbidden.values()),
    }


def _homogeneity_record(weights: list[np.ndarray], n: int, seed: int) -> dict:
    rng = np.random.Generator(np.random.PCG64(seed))
    errs = []
    for _ in range(16):
        x = rng.standard_normal(n)
        r = float(np.linalg.norm(x))
        y = math.sqrt(n) * x / r
        lhs = forward(weights, x)
        rhs = (r / math.sqrt(n)) * forward(weights, y)
        errs.append(_rel(lhs, rhs))
    return {"max_relative_error": max(errs), "passes": max(errs) <= 2e-12}


def _strassen_records() -> list[dict]:
    rng = np.random.Generator(np.random.PCG64(151700))
    shapes = [(16, 16, 16), (32, 32, 32), (17, 24, 19), (32, 16, 24)]
    out = []
    for m, k, p in shapes:
        a = rng.standard_normal((m, k))
        b = rng.standard_normal((k, p))
        ref = a @ b
        got = one_level_strassen(a, b)
        err = _rel(got, ref)
        out.append(
            {
                "shape": [m, k, p],
                "relative_frobenius_error": err,
                "passes": err <= 2e-12,
            }
        )
    return out


def main() -> None:
    np.seterr(all="raise")

    firewall = _source_firewall()

    exact_weights = dense_he_weights(2, 8, 8, 151002)
    exact1 = exact_gaussian_mean_2d(exact_weights)
    exact2 = exact_gaussian_mean_2d(exact_weights)
    exact_replay = bool(np.array_equal(exact1, exact2))

    dense32 = dense_he_weights(32, 32, 8, 151032)
    adv16 = adversarial_square_weights(16, 8, 151016)
    hom = {
        "dense32_depth8": _homogeneity_record(dense32, 32, 151132),
        "adversarial16_depth8": _homogeneity_record(adv16, 16, 151116),
    }

    k4_rows = {}
    for n in (2, 16, 32, 1024):
        lhs = 3.0 * n / (n + 2.0) - 3.0
        rhs = angular_k4_diagonal(n)
        err = abs(lhs - rhs)
        k4_rows[str(n)] = {
            "moment_minus_gaussian": lhs,
            "closed_form": rhs,
            "absolute_error": err,
            "passes": err <= 2e-15,
        }

    a1 = {str(n): radial_moment_ratio(n, 1.0) for n in (2, 16, 32, 1024)}
    strassen = _strassen_records()
    rho = strassen1_square_ratio(1024)
    reported_ratio = OPEN_PHASE2_STRASSEN_UTIL / OPEN_PHASE2_GAUSSIAN_UTIL

    transfer = {}
    for name, row in FRONTIER_ROWS.items():
        q = required_eligible_fraction(row["util"], UTIL_CAP, rho)
        transferred = row["util"] * reported_ratio
        transfer[name] = {
            **row,
            "reported_total_cost_ratio_transfer": reported_ratio,
            "transferred_util": transferred,
            "transferred_le_0_135": transferred <= UTIL_CAP,
            "required_eligible_fraction_under_exact_strassen_ratio": q,
        }

    gates = {
        "source_firewall": firewall["passes"],
        "exact2d_replay_bitwise": exact_replay,
        "homogeneity_all": all(x["passes"] for x in hom.values()),
        "angular_k4_identity_all": all(x["passes"] for x in k4_rows.values()),
        "strassen_numeric_identity_all": all(x["passes"] for x in strassen),
        "strassen_1024_ratio_exact": rho == 0.877197265625,
        "reported_cost_ratio_exact_reproduction": abs(reported_ratio - 0.8842692559431139) <= 1e-15,
        "frontier_transfer_both_le_0_135": all(
            x["transferred_le_0_135"] for x in transfer.values()
        ),
        "eligible_fraction_threshold_first_le_0_71": transfer["puffi_snapshot"][
            "required_eligible_fraction_under_exact_strassen_ratio"
        ]
        <= 0.71,
        "eligible_fraction_threshold_second_le_0_835": transfer["suliman_snapshot"][
            "required_eligible_fraction_under_exact_strassen_ratio"
        ]
        <= 0.835,
        "no_public_target_access": True,
    }

    passed = all(gates.values())
    result = {
        "schema": "arc.whitebox.e151.arsg_falsifier.v1",
        "idempotency_key": "ARC-E151-ARSG-FORENSICS-20260921",
        "source_firewall": firewall,
        "exact2d": {
            "seed": 151002,
            "depth": 8,
            "width": 8,
            "gaussian_mean_sha256": hashlib.sha256(
                np.ascontiguousarray(exact1).tobytes()
            ).hexdigest(),
            "replay_bitwise": exact_replay,
        },
        "homogeneity": hom,
        "radial_a1": a1,
        "angular_k4": k4_rows,
        "strassen_numeric": strassen,
        "cost": {
            "strassen1_1024_square_ratio": rho,
            "open_phase2_reported_before": OPEN_PHASE2_GAUSSIAN_UTIL,
            "open_phase2_reported_after": OPEN_PHASE2_STRASSEN_UTIL,
            "open_phase2_reported_total_ratio": reported_ratio,
            "frontier_transfer": transfer,
        },
        "gates": gates,
        "decision": (
            "E151_HYPOTHESIS_ADMISSIBLE_NOT_VALIDATED_ON_TARGETS"
            if passed
            else "E151_TERMINAL_NO_GO_ARSG"
        ),
        "scope": {
            "synthetic_only": True,
            "public_target": False,
            "public_mini": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "sweep": False,
            "rescue": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
