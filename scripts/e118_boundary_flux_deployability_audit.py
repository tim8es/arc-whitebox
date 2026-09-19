from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import numpy as np

BUDGET = 2**41
UTIL_LIMIT_NUM = 13
UTIL_LIMIT_DEN = 100
HARD_LIMIT = (UTIL_LIMIT_NUM * BUDGET) // UTIL_LIMIT_DEN
E104_BASE_FLOPS = 149_114_620_592
E104_HEADROOM = HARD_LIMIT - E104_BASE_FLOPS
RAW_MSE_TARGET = 1.89e-8
RMS_TARGET = math.sqrt(RAW_MSE_TARGET)
WIDTH_PROD = 1024
VECTOR_L2_TARGET = math.sqrt(WIDTH_PROD * RAW_MSE_TARGET)

OWNER_SCRIPT = Path("scripts/e114_activation_boundary_flux.py")
OWNER_PROTOCOL = Path("research/E114_PROTOCOL.md")
OWNER_RECEIPT = Path("research/E114_RESULT_RECEIPT.json")
OUT = Path("e118-boundary-flux-deployability-audit.json")


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out: list[float] = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + 1e-12 < root < hi - 1e-12:
            out.append(root)
    return out


def _dedup(values: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(values):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def _sector_integral(coeff: np.ndarray, lo: float, hi: float) -> float:
    a, b = map(float, coeff)
    return (
        a * (math.sin(hi) - math.sin(lo))
        + b * (-math.cos(hi) + math.cos(lo))
    )


def _angular_derivative(coeff: np.ndarray, theta: float) -> float:
    a, b = map(float, coeff)
    return -a * math.sin(theta) + b * math.cos(theta)


def generic_weight_driven_reference() -> dict:
    weights = [
        np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64),
        np.asarray([[1.0, 1.0], [-2.0, 0.0]], dtype=np.float64),
        np.asarray([[2.0], [-1.0]], dtype=np.float64),
    ]

    # (lo, hi, homogeneous coefficient matrix), where each activation row is
    # a*cos(theta)+b*sin(theta) on the current region.
    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]
    counts = []

    for weight in weights:
        next_intervals: list[tuple[float, float, np.ndarray]] = []
        for lo, hi, h_coeff in intervals:
            pre = weight.T @ h_coeff
            bounds = [lo, hi]
            for row in pre:
                bounds.extend(_roots(float(row[0]), float(row[1]), lo, hi))
            bounds = _dedup(bounds)

            for left, right in zip(bounds[:-1], bounds[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                direction = np.asarray(
                    [math.cos(mid), math.sin(mid)], dtype=np.float64
                )
                mask = (pre @ direction) > 0.0
                post = pre.copy()
                post[~mask, :] = 0.0
                next_intervals.append((left, right, post))
        intervals = next_intervals
        counts.append(len(intervals))

    intervals.sort(key=lambda item: item[0])
    angular_integral = sum(
        _sector_integral(coeff[0], lo, hi) for lo, hi, coeff in intervals
    )

    jumps = []
    for i, (lo, _hi, coeff_right) in enumerate(intervals):
        coeff_left = intervals[i - 1][2] if i > 0 else intervals[-1][2]
        jump = _angular_derivative(coeff_right[0], lo) - _angular_derivative(
            coeff_left[0], lo
        )
        jumps.append(jump)
    flux_sum = float(sum(jumps))

    mean_radius = math.sqrt(math.pi / 2.0)
    mean_from_sector = mean_radius * angular_integral / (2.0 * math.pi)
    mean_from_flux = mean_radius * flux_sum / (2.0 * math.pi)
    closed_form = (math.sqrt(17.0) - 3.0) / (2.0 * math.sqrt(2.0 * math.pi))

    nonzero_jumps = [x for x in jumps if abs(x) > 1e-14]

    return {
        "region_count_after_each_layer": counts,
        "final_region_count": len(intervals),
        "final_boundaries": [float(x[0]) for x in intervals],
        "nonzero_jump_count": len(nonzero_jumps),
        "nonzero_jumps": nonzero_jumps,
        "angular_integral": angular_integral,
        "flux_sum": flux_sum,
        "flux_vs_sector_abs_error": abs(flux_sum - angular_integral),
        "mean_from_sector": mean_from_sector,
        "mean_from_flux": mean_from_flux,
        "closed_form_mean": closed_form,
        "generic_vs_closed_form_abs_error": abs(mean_from_flux - closed_form),
        "finite": bool(
            all(
                math.isfinite(x)
                for x in (
                    angular_integral,
                    flux_sum,
                    mean_from_sector,
                    mean_from_flux,
                    closed_form,
                )
            )
        ),
    }


def _function_args_and_names(source: str) -> dict:
    tree = ast.parse(source)
    functions = {}
    imports = []
    constants = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = [arg.arg for arg in node.args.args]
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str)):
            constants.append(node.value)
    return {"functions": functions, "imports": imports, "constants": constants}


def owner_source_audit() -> dict:
    source = OWNER_SCRIPT.read_text(encoding="utf-8")
    protocol = OWNER_PROTOCOL.read_text(encoding="utf-8")
    receipt = json.loads(OWNER_RECEIPT.read_text(encoding="utf-8"))
    parsed = _function_args_and_names(source)

    hardcoded_alpha = "alpha = math.atan(0.25)" in source
    hardcoded_regions = all(
        token in source
        for token in (
            "zero = (0.0, 0.0)",
            "lower_right = (1.0, 0.0)",
            "upper_wedge = (1.0, -4.0)",
        )
    )
    hardcoded_boundary_list = "first_layer_boundaries = [" in source
    generic_weight_argument = any(
        any(name in {"weights", "mlp", "network_state"} for name in args)
        for args in parsed["functions"].values()
    )
    generic_boundary_builder = any(
        name in parsed["functions"]
        for name in (
            "enumerate_boundaries",
            "build_boundaries",
            "activation_regions",
            "boundary_partition",
            "discover_boundaries",
        )
    )
    has_flopscope = any(
        (imp == "flopscope" or imp.startswith("flopscope.")) for imp in parsed["imports"]
    )
    has_budget_context = "BudgetContext" in source
    remainder_term_present = "remainder" in source.lower()
    production_algorithm_claimed = bool(receipt.get("production_go", False))

    return {
        "owner_script_git_role": "fixed-fixture exact identity demonstrator",
        "hardcoded_downstream_kink_angle": hardcoded_alpha,
        "hardcoded_final_region_coefficients": hardcoded_regions,
        "hardcoded_boundary_list_present": hardcoded_boundary_list,
        "generic_weight_or_mlp_argument_present": generic_weight_argument,
        "generic_boundary_constructor_present": generic_boundary_builder,
        "flopscope_import_present": has_flopscope,
        "budget_context_present": has_budget_context,
        "remainder_certificate_code_present": remainder_term_present,
        "owner_receipt_production_go": production_algorithm_claimed,
        "protocol_self_classification": (
            "identity, not yet a production algorithm"
            if "This is an identity, not yet a production algorithm." in protocol
            else "not-found"
        ),
        "oracle_free_deployable_implementation": bool(
            generic_weight_argument
            and generic_boundary_builder
            and not hardcoded_alpha
            and not hardcoded_regions
            and has_flopscope
            and has_budget_context
        ),
    }


def remainder_and_cost_audit(source_audit: dict) -> dict:
    generic_mechanism = bool(source_audit["oracle_free_deployable_implementation"])
    remainder_present = bool(source_audit["remainder_certificate_code_present"])
    billed = bool(
        source_audit["flopscope_import_present"] and source_audit["budget_context_present"]
    )

    return {
        "raw_mse_target": RAW_MSE_TARGET,
        "uniform_per_coordinate_abs_error_sufficient_bound": RMS_TARGET,
        "width_1024_vector_l2_sufficient_bound": VECTOR_L2_TARGET,
        "flux_remainder_identity": (
            "e_j = E[R]/(|S^{d-1}|*(d-1)) * "
            "sum_{omitted Gamma} integral_Gamma J_Gamma"
        ),
        "computable_omitted_flux_bound_present": remainder_present,
        "generic_boundary_state_or_compression_cost_billed": billed and generic_mechanism,
        "helper_cost_billed": billed and generic_mechanism,
        "certificate_cost_billed": billed and remainder_present and generic_mechanism,
        "standalone_all_in_flop_ceiling": HARD_LIMIT,
        "e104_layered_base_flops": E104_BASE_FLOPS,
        "e104_incremental_headroom": E104_HEADROOM,
        "measured_or_rigorous_generic_boundary_core_flops": None,
        "measured_or_rigorous_helper_flops": None,
        "measured_or_rigorous_certificate_flops": None,
        "all_in_cost_gate": False,
        "remainder_gate": False,
        "reason": (
            "Owner E114 contains no generic boundary construction/compression path, "
            "no computable omitted-flux remainder certificate, and no flopscope "
            "ledger for boundary/helper/certificate work. Therefore production "
            "all-in cost and approximation error are unestablished."
        ),
    }


def main() -> None:
    ref1 = generic_weight_driven_reference()
    ref2 = generic_weight_driven_reference()

    repeat_delta = max(
        abs(float(ref1[k]) - float(ref2[k]))
        for k in (
            "angular_integral",
            "flux_sum",
            "mean_from_sector",
            "mean_from_flux",
            "closed_form_mean",
        )
    )
    repeat_structural = (
        ref1["region_count_after_each_layer"] == ref2["region_count_after_each_layer"]
        and ref1["final_boundaries"] == ref2["final_boundaries"]
        and ref1["nonzero_jumps"] == ref2["nonzero_jumps"]
    )

    source = owner_source_audit()
    rc = remainder_and_cost_audit(source)

    gate_a = {
        "finite": ref1["finite"],
        "flux_vs_sector_abs_error_le_1e_12": ref1["flux_vs_sector_abs_error"] <= 1e-12,
        "generic_vs_closed_form_abs_error_le_1e_12": (
            ref1["generic_vs_closed_form_abs_error"] <= 1e-12
        ),
        "deterministic_repeat_max_abs_eq_0": repeat_delta == 0.0,
        "deterministic_structure_exact": repeat_structural,
    }
    gate_a_pass = all(gate_a.values())

    gate_b = {
        "generic_weight_driven_boundary_mechanism": source[
            "oracle_free_deployable_implementation"
        ],
        "remainder_certificate_meets_error_gate": rc["remainder_gate"],
        "all_in_flops_including_helpers_certificate_established": rc[
            "all_in_cost_gate"
        ],
        "helper_cost_explicitly_billed": rc["helper_cost_billed"],
        "certificate_cost_explicitly_billed": rc["certificate_cost_billed"],
    }
    gate_b_pass = all(gate_b.values())

    if not gate_a_pass:
        decision = "VERIFIER_FAILURE_DO_NOT_INTERPRET_DEPLOYABILITY"
    elif not gate_b_pass:
        decision = "DEPLOYABILITY_NO_GO_ORACLE_FIXTURE_ONLY"
    else:
        decision = "BOTH_GATES_PASS_PRODUCTION_ADMISSION_ONLY"

    result = {
        "schema": "arc.whitebox.e118.boundary_flux_deployability_audit.v1",
        "experiment": "E118",
        "reviewed_e114_head": "b9f64030f65da9b32fc7718d04fb108ee1a73dab",
        "independent_small_width_reference": ref1,
        "determinism": {
            "repeat_max_abs": repeat_delta,
            "repeat_structure_exact": repeat_structural,
        },
        "owner_source_audit": source,
        "remainder_and_cost_audit": rc,
        "gate_a_exact_small_width": {
            "checks": gate_a,
            "pass": gate_a_pass,
        },
        "gate_b_deployability": {
            "checks": gate_b,
            "pass": gate_b_pass,
        },
        "decision": decision,
        "production_authorized": bool(gate_a_pass and gate_b_pass),
        "scientific_identity_valid": gate_a_pass,
        "scope": {
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "benchmark_targets": False,
            "holdout": False,
            "full_suite": False,
            "production_run": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E118_AUDIT=" + json.dumps(result, sort_keys=True), flush=True)

    if not gate_a_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
