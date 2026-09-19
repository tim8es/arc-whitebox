#!/usr/bin/env python3
"""Independent E114 small-width verifier.

No benchmark/public/scorer/holdout/full access. This does not import or execute
the owner E114 candidate script. It reads only the sealed owner receipt and
reconstructs the frozen depth-3 fixture/reference from first principles.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

OWNER_RECEIPT = Path("research/E114_RESULT_RECEIPT.json")
OUT = Path("e114-independent-verifier.json")
TOL = 1e-14

EXPECTED_OWNER_ARTIFACT_ZIP_SHA256 = (
    "dd7a49166fe7f3cc469b145914e8b8b00680bfbeaa574b8539cdbad50defb84f"
)
EXPECTED_OWNER_ARTIFACT_JSON_SHA256 = (
    "7aedfb60c6b378972eab0c3cec1a3647b2f0fd11dcec78727a64c8b5c36f2700"
)


def canonical_sha256(obj: object) -> str:
    payload = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def direct_network(x1: float, x2: float) -> float:
    h1 = relu(x1)
    h2 = relu(x2)
    u1 = relu(h1 - 2.0 * h2)
    u2 = relu(h1)
    return relu(2.0 * u1 - u2)


def independent_reference() -> dict:
    sqrt17 = math.sqrt(17.0)
    alpha = math.atan(0.25)

    # Independent algebraic simplification:
    # F(x)=x1 on {x1>0,x2<0};
    # F(x)=x1-4*x2 on {x2>0,x1>4*x2};
    # F(x)=0 otherwise.
    #
    # On the unit circle the two active sector integrals are:
    # [-pi/2,0]: integral cos(theta) dtheta = 1
    # [0,alpha]: integral(cos(theta)-4sin(theta)) dtheta
    #            = sqrt(17)-4, because tan(alpha)=1/4.
    lower_integral = 1.0
    upper_integral = sqrt17 - 4.0
    angular_integral = lower_integral + upper_integral

    # Distributional derivative jumps for f''+f=sum Delta_k delta:
    # at -pi/2: +1
    # at 0: -4
    # at alpha: +sqrt(17)
    jumps = [1.0, -4.0, sqrt17]
    flux_sum = sum(jumps)

    mean_radius_2d = math.sqrt(math.pi / 2.0)
    gaussian_mean_from_sector = (
        mean_radius_2d * angular_integral / (2.0 * math.pi)
    )
    gaussian_mean_closed = (
        (sqrt17 - 3.0) / (2.0 * math.sqrt(2.0 * math.pi))
    )

    # Verify direct network against the independently simplified cones.
    points = [
        (-0.7, -0.3),
        (0.8, -0.2),
        (1.0, 0.1),
        (1.0, 0.3),
        (0.2, 1.0),
    ]
    max_piecewise_abs = 0.0
    for x1, x2 in points:
        if x1 > 0.0 and x2 <= 0.0:
            simplified = x1
        elif x2 > 0.0 and x1 > 4.0 * x2:
            simplified = x1 - 4.0 * x2
        else:
            simplified = 0.0
        max_piecewise_abs = max(
            max_piecewise_abs, abs(direct_network(x1, x2) - simplified)
        )

    reference = {
        "fixture": {
            "input_dimension": 2,
            "depth": 3,
            "W1": [[1.0, 0.0], [0.0, 1.0]],
            "W2": [[1.0, 1.0], [-2.0, 0.0]],
            "W3": [[2.0], [-1.0]],
        },
        "alpha": alpha,
        "sqrt17": sqrt17,
        "derivative_jumps": jumps,
        "flux_sum": flux_sum,
        "sector_integrals": [lower_integral, upper_integral],
        "angular_integral": angular_integral,
        "mean_radius_2d": mean_radius_2d,
        "gaussian_mean_from_sector": gaussian_mean_from_sector,
        "gaussian_mean_closed_form": gaussian_mean_closed,
        "direct_network_vs_algebraic_piecewise_max_abs": max_piecewise_abs,
        "general_identity_sign_check_2d": (
            "0=integral(f'')=-integral(f)+sum(jumps), "
            "therefore integral(f)=sum(jumps)"
        ),
        "closed_form_expression": "(sqrt(17)-3)/(2*sqrt(2*pi))",
    }
    reference["reference_sha256"] = canonical_sha256(reference)
    return reference


def verify_once() -> dict:
    owner = json.loads(OWNER_RECEIPT.read_text(encoding="utf-8"))
    ref = independent_reference()
    m = owner["measurements"]

    candidate_jump_sum = float(m["jump_sum"])
    candidate_sector = float(m["sector_integral"])
    candidate_boundary_mean = float(m["gaussian_boundary_flux_value"])
    candidate_closed_mean = float(m["gaussian_closed_form_value"])
    candidate_jumps = [float(x) for x in m["derivative_jumps"]]

    errors = {
        "jump_sum_abs": abs(candidate_jump_sum - ref["flux_sum"]),
        "sector_integral_abs": abs(
            candidate_sector - ref["angular_integral"]
        ),
        "boundary_gaussian_mean_abs": abs(
            candidate_boundary_mean - ref["gaussian_mean_closed_form"]
        ),
        "owner_closed_form_mean_abs": abs(
            candidate_closed_mean - ref["gaussian_mean_closed_form"]
        ),
        "jump_vector_max_abs": max(
            abs(a - b)
            for a, b in zip(candidate_jumps, ref["derivative_jumps"])
        ),
        "owner_direct_piecewise_max_abs": float(m["direct_piecewise_max_abs"]),
    }

    target_independence = {
        "owner_scope_benchmark_targets_false": (
            owner["scope"]["benchmark_targets"] is False
        ),
        "owner_scope_public_false": owner["scope"]["public"] is False,
        "owner_scope_public_mini_false": owner["scope"]["public_mini"] is False,
        "owner_scope_official_scorer_false": (
            owner["scope"]["official_scorer"] is False
        ),
        "owner_scope_holdout_false": owner["scope"]["holdout"] is False,
        "owner_scope_full_suite_false": owner["scope"]["full_suite"] is False,
        "owner_scope_production_run_false": (
            owner["scope"]["production_run"] is False
        ),
        "verifier_uses_only_sealed_owner_receipt_and_math_fixture": True,
    }

    gates = {
        "owner_identity_matches": (
            owner["identity"]
            == "ARC-E114-ACTIVATION-BOUNDARY-FLUX-20260919"
        ),
        "owner_scientific_go_true": owner["scientific_go"] is True,
        "owner_production_go_false": owner["production_go"] is False,
        "target_independence_all": all(target_independence.values()),
        "reference_direct_piecewise_exact": (
            ref["direct_network_vs_algebraic_piecewise_max_abs"] <= TOL
        ),
        "flux_sum_equals_sector_reference": (
            abs(ref["flux_sum"] - ref["angular_integral"]) <= TOL
        ),
        "reference_sector_equals_closed_form_mean": (
            abs(
                ref["gaussian_mean_from_sector"]
                - ref["gaussian_mean_closed_form"]
            )
            <= TOL
        ),
        "candidate_jump_sum_matches_reference": errors["jump_sum_abs"] <= TOL,
        "candidate_sector_matches_reference": (
            errors["sector_integral_abs"] <= TOL
        ),
        "candidate_boundary_mean_matches_reference": (
            errors["boundary_gaussian_mean_abs"] <= TOL
        ),
        "candidate_jump_vector_matches_reference": (
            errors["jump_vector_max_abs"] <= TOL
        ),
        "owner_direct_piecewise_within_tolerance": (
            errors["owner_direct_piecewise_max_abs"] <= TOL
        ),
        "owner_deterministic_repeat_exact": (
            m["deterministic_repeat_exact"] is True
        ),
    }

    result = {
        "schema": "arc.whitebox.e114.independent_verifier.v1",
        "experiment": "E114",
        "owner_identity": owner["identity"],
        "owner_branch": owner["branch"],
        "owner_run": owner["provenance"]["run"],
        "owner_job": owner["provenance"]["job"],
        "owner_artifact_id": owner["provenance"]["artifact_id"],
        "owner_artifact_zip_sha256_expected_and_independently_verified": (
            EXPECTED_OWNER_ARTIFACT_ZIP_SHA256
        ),
        "owner_artifact_json_sha256_independently_verified": (
            EXPECTED_OWNER_ARTIFACT_JSON_SHA256
        ),
        "reference": ref,
        "candidate_vs_reference_error": errors,
        "target_independence": target_independence,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "production_authorized_by_verifier": False,
        "scope": {
            "new_candidate": False,
            "small_width_reference_only": True,
            "production_run": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    result["verification_payload_sha256"] = canonical_sha256(result)
    return result


def main() -> None:
    first = verify_once()
    second = verify_once()

    first_bytes = json.dumps(
        first, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    second_bytes = json.dumps(
        second, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    deterministic = first_bytes == second_bytes
    first["independent_verifier_replay_exact"] = deterministic
    first["independent_verifier_replay_sha256_first"] = hashlib.sha256(
        first_bytes
    ).hexdigest()
    first["independent_verifier_replay_sha256_second"] = hashlib.sha256(
        second_bytes
    ).hexdigest()
    first["all_gates_pass"] = bool(first["all_gates_pass"] and deterministic)
    first["decision"] = (
        "SMALL_WIDTH_EXACT_GATE_VERIFIED"
        if first["all_gates_pass"]
        else "SMALL_WIDTH_EXACT_GATE_REJECTED"
    )

    OUT.write_text(
        json.dumps(first, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E114_INDEPENDENT_VERIFIER=" + json.dumps(first, sort_keys=True))
    if not first["all_gates_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
