from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import numpy as np

from methods.e118_boundary_flux_physical import (
    compressed_physical_estimate,
    make_network,
)

SEED = 118118
WIDTH = 8
DEPTH = 4
EXPANSION_CAP = 62
RMS_LIMIT = 1.3747727085e-4

PROD_INCREMENTAL_CAP = 136_758_472_261
PROD_TRANSITION_FLOPS = 2 * 1024**3
PROD_TRANSITION_COUNT = 62
PROD_TRANSITION_TOTAL = PROD_TRANSITION_FLOPS * PROD_TRANSITION_COUNT
PROD_HELPER_RESERVE = 3_600_000_000
PROD_INCREMENTAL_TOTAL = PROD_TRANSITION_TOTAL + PROD_HELPER_RESERVE

METHOD_PATH = Path("methods/e118_boundary_flux_physical.py")
HARNESS_PATH = Path("scripts/e118_boundary_flux_physical.py")
OWNER_RECEIPT_PATH = Path("research/E118_TERMINAL_RECEIPT.json")
OUT = Path("e119-independent-boundary-audit.json")

TWO_PI = 2.0 * math.pi
MEAN_RADIUS_2D = math.sqrt(math.pi / 2.0)


def roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1e-12 < x < hi - 1e-12:
            out.append(x)
    return out


def dedup(xs: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(xs):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def q_integral(lo: float, hi: float) -> np.ndarray:
    return np.asarray(
        [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
        dtype=np.float64,
    )


def independent_exact_reference(weights: list[np.ndarray]) -> dict:
    # Independent region enumerator. It does not call owner full_exact_reference
    # or any owner root/state helper.
    states: list[tuple[float, float, np.ndarray]] = [
        (0.0, TWO_PI, np.eye(2, dtype=np.float64))
    ]
    layer_counts = [1]
    root_checks = 0
    roots_found = 0
    materialized = 1
    coeff_bytes = int(states[0][2].nbytes)

    for raw_weight in weights:
        w = np.asarray(raw_weight, dtype=np.float64)
        nxt: list[tuple[float, float, np.ndarray]] = []
        for lo, hi, coeff in states:
            pre = w @ coeff
            bounds = [lo, hi]
            for row in pre:
                root_checks += 1
                rr = roots(float(row[0]), float(row[1]), lo, hi)
                roots_found += len(rr)
                bounds.extend(rr)
            bounds = dedup(bounds)
            for left, right in zip(bounds[:-1], bounds[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                q = np.asarray([math.cos(mid), math.sin(mid)], dtype=np.float64)
                post = pre.copy()
                post[(pre @ q) <= 0.0, :] = 0.0
                nxt.append((left, right, post))
                materialized += 1
                coeff_bytes += int(post.nbytes)
        states = nxt
        layer_counts.append(len(states))

    width = int(weights[-1].shape[0])
    c = np.ones(width, dtype=np.float64) / math.sqrt(float(width))
    mean = 0.0
    angular_integral = 0.0
    coeffs: list[np.ndarray] = []
    states = sorted(states, key=lambda x: (x[0], x[1]))
    for lo, hi, coeff in states:
        scalar = c @ coeff
        coeffs.append(scalar)
        ang = float(scalar @ q_integral(lo, hi))
        angular_integral += ang
        mean += MEAN_RADIUS_2D / TWO_PI * ang

    jump_sum = 0.0
    for idx, (lo, _hi, _coeff) in enumerate(states):
        right = coeffs[idx]
        left = coeffs[idx - 1]
        tangent = np.asarray([-math.sin(lo), math.cos(lo)], dtype=np.float64)
        jump_sum += float((right - left) @ tangent)

    flux_mean = MEAN_RADIUS_2D / TWO_PI * jump_sum
    return {
        "mean": float(mean),
        "flux_mean": float(flux_mean),
        "flux_sector_abs_diff": float(abs(flux_mean - mean)),
        "angular_integral": float(angular_integral),
        "jump_sum": float(jump_sum),
        "layer_state_counts": layer_counts,
        "final_interval_count": len(states),
        "root_checks": root_checks,
        "roots_found": roots_found,
        "states_materialized": materialized,
        "coefficient_bytes_materialized": coeff_bytes,
    }


def source_purity_audit() -> dict:
    method = METHOD_PATH.read_text(encoding="utf-8")
    harness = HARNESS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(method)

    functions = {
        node.name: [arg.arg for arg in node.args.args]
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

    fixture_angle_literals = [
        "atan(0.25)",
        "atan(1/4)",
        "0.244978663126864",
        "upper_wedge",
        "lower_right",
    ]
    hardcoded_fixture_angle_or_region = any(x in method for x in fixture_angle_literals)

    generic_weight_api = (
        "weights" in functions.get("compressed_physical_estimate", [])
        and "weights" in functions.get("full_exact_reference", [])
        and "weight" in functions.get("expand_state", [])
    )
    root_from_coeff = (
        "pre = np.asarray(weight" in method
        and "_roots(float(row[0]), float(row[1]), state.lo, state.hi)" in method
    )
    candidate_uses_exact_reference = "full_exact_reference" in (
        method[
            method.index("def compressed_physical_estimate") :
        ]
        if "def compressed_physical_estimate" in method
        else ""
    )

    return {
        "candidate_accepts_actual_weights": generic_weight_api,
        "root_construction_derived_from_weighted_coefficients": root_from_coeff,
        "fixture_specific_angle_or_region_constants_absent": not hardcoded_fixture_angle_or_region,
        "candidate_selection_does_not_call_exact_reference": not candidate_uses_exact_reference,
        "frozen_seed_only_in_harness_not_candidate_method": (
            "118118" not in method and "SEED = 118118" in harness
        ),
        "gate_pass": bool(
            generic_weight_api
            and root_from_coeff
            and not hardcoded_fixture_angle_or_region
            and not candidate_uses_exact_reference
            and "118118" not in method
        ),
    }


def accounting_audit() -> dict:
    method = METHOD_PATH.read_text(encoding="utf-8")
    harness = HARNESS_PATH.read_text(encoding="utf-8")
    receipt = json.loads(OWNER_RECEIPT_PATH.read_text(encoding="utf-8"))

    classes = {
        "dense_state_transition": {
            "present": "pre = np.asarray(weight" in method,
            "explicit_costed": "PROD_TRANSITION_FLOPS" in harness,
        },
        "root_solving_and_checks": {
            "present": "_roots(" in method and "root_checks" in method,
            "explicit_costed": False,
        },
        "root_sort_and_dedup": {
            "present": "sorted(xs)" in method and "_dedup" in method,
            "explicit_costed": False,
        },
        "trig_midpoint_direction": {
            "present": "math.cos(mid)" in method and "math.sin(mid)" in method,
            "explicit_costed": False,
        },
        "mask_tests": {
            "present": "(pre @ q) <= 0.0" in method,
            "explicit_costed": False,
        },
        "coefficient_materialization": {
            "present": "pre.copy()" in method and "child_coefficient_bytes" in method,
            "explicit_costed": False,
        },
        "heap_priority_push_pop": {
            "present": "heapq.heappop" in method and "heapq.heappush" in method,
            "explicit_costed": False,
        },
        "frobenius_suffix_norms": {
            "present": 'ord="fro"' in method and "suffix_frobenius_products" in method,
            "explicit_costed": False,
        },
        "remainder_certificate_accumulation": {
            "present": "remainder = float(sum(unresolved_bound" in method,
            "explicit_costed": False,
        },
        "sector_integration": {
            "present": "_sector_q_integral" in method and "final_sector_contribution" in method,
            "explicit_costed": False,
        },
        "state_bookkeeping": {
            "present": "materialized_by_layer" in method and "max_live_queue" in method,
            "explicit_costed": False,
        },
    }

    missing = [name for name, d in classes.items() if d["present"] and not d["explicit_costed"]]
    has_flopscope = "flopscope" in method or "flopscope" in harness
    reserve_declared = "PROD_HELPER_RESERVE = 3_600_000_000" in harness
    reserve_proven = bool(
        receipt["production_accounting"].get(
            "high_dimensional_cone_helpers_proven_within_reserve", False
        )
    )
    formula_fits = PROD_INCREMENTAL_TOTAL <= PROD_INCREMENTAL_CAP

    return {
        "operation_classes": classes,
        "unbilled_or_underived_operation_classes": missing,
        "physical_flopscope_present": has_flopscope,
        "helper_reserve_declared": reserve_declared,
        "helper_reserve_flops": PROD_HELPER_RESERVE,
        "helper_reserve_derived_or_measured": reserve_proven,
        "transition_total_flops": PROD_TRANSITION_TOTAL,
        "stated_incremental_total_flops": PROD_INCREMENTAL_TOTAL,
        "incremental_cap_flops": PROD_INCREMENTAL_CAP,
        "stated_formula_fits_cap": formula_fits,
        "complete_accounting_gate": bool(
            formula_fits
            and has_flopscope
            and reserve_proven
            and len(missing) == 0
        ),
    }


def max_reference_delta(a: dict, b: dict) -> float:
    numeric = [
        "mean",
        "flux_mean",
        "flux_sector_abs_diff",
        "angular_integral",
        "jump_sum",
    ]
    d = max(abs(float(a[k]) - float(b[k])) for k in numeric)
    if a["layer_state_counts"] != b["layer_state_counts"]:
        return math.inf
    for k in (
        "final_interval_count",
        "root_checks",
        "roots_found",
        "states_materialized",
        "coefficient_bytes_materialized",
    ):
        if a[k] != b[k]:
            return math.inf
    return d


def main() -> None:
    weights = make_network(SEED, width=WIDTH, depth=DEPTH)
    ref1 = independent_exact_reference(weights)
    ref2 = independent_exact_reference(weights)
    repeat = max_reference_delta(ref1, ref2)

    candidate = compressed_physical_estimate(weights, expansion_cap=EXPANSION_CAP)
    actual_error = abs(float(candidate["estimate"]) - ref1["mean"])
    certificate = float(candidate["remainder_certificate"])

    purity = source_purity_audit()
    accounting = accounting_audit()

    exact_gate = {
        "independent_reference_flux_identity_le_1e_12": ref1["flux_sector_abs_diff"] <= 1e-12,
        "independent_reference_deterministic_repeat_eq_0": repeat == 0.0,
        "actual_error_within_owner_certificate": actual_error <= certificate + 1e-12,
        "actual_error_le_rms_limit": actual_error <= RMS_LIMIT,
        "remainder_certificate_le_rms_limit": certificate <= RMS_LIMIT,
    }
    exact_gate_pass = all(exact_gate.values())

    gates = {
        "generic_weight_driven_no_oracle": purity["gate_pass"],
        "exact_corpus_rms_and_certificate": exact_gate_pass,
        "complete_helper_materialization_certificate_flops": accounting[
            "complete_accounting_gate"
        ],
    }
    production_authorized = all(gates.values())

    result = {
        "schema": "arc.whitebox.e119.independent_boundary_audit.v1",
        "experiment": "E119",
        "reviewed_branch": "research/e118-boundary-flux-physical-compression-20260919",
        "reviewed_head": "9e1ef4c27fb68e7371ee9d025bf055ab8e33527d",
        "frozen_fixture": {
            "seed": SEED,
            "width": WIDTH,
            "depth": DEPTH,
            "expansion_cap": EXPANSION_CAP,
            "rms_limit": RMS_LIMIT,
        },
        "source_purity": purity,
        "independent_exact_reference": ref1,
        "candidate": {
            "estimate": float(candidate["estimate"]),
            "actual_abs_error_vs_independent_reference": actual_error,
            "remainder_certificate": certificate,
            "actual_error_over_rms_limit": actual_error / RMS_LIMIT,
            "certificate_over_rms_limit": certificate / RMS_LIMIT,
            "actual_error_within_certificate": actual_error <= certificate + 1e-12,
            "expansions": int(candidate["expansions"]),
            "unresolved_state_count": int(candidate["unresolved_state_count"]),
            "max_live_queue": int(candidate["max_live_queue"]),
            "root_checks": int(candidate["root_checks"]),
            "roots_materialized": int(candidate["roots_materialized"]),
            "coefficient_bytes_materialized": int(
                candidate["coefficient_bytes_materialized"]
            ),
        },
        "exact_corpus_gate": {
            "checks": exact_gate,
            "pass": exact_gate_pass,
        },
        "accounting": accounting,
        "gates": gates,
        "production_authorized": production_authorized,
        "decision": (
            "PRODUCTION_ADMISSION_PASS"
            if production_authorized
            else "INDEPENDENT_NO_GO_PRODUCTION_NOT_AUTHORIZED"
        ),
        "scope": {
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "benchmark_targets": False,
            "holdout": False,
            "full_suite": False,
            "production_run": False,
            "tuning": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E119_AUDIT=" + json.dumps(result, sort_keys=True), flush=True)

    # Source/reference verifier integrity failure is CI failure. Candidate scientific
    # or accounting NO-GO is a successful audit outcome.
    if not purity["gate_pass"]:
        raise SystemExit(2)
    if ref1["flux_sector_abs_diff"] > 1e-12 or repeat != 0.0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
