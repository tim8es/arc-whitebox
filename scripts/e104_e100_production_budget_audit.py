from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

BUDGET = 2**41
UTIL_LIMIT = 0.135
E104_MEASURED_FLOPS = 149_114_620_592
E100_CORRECTED_REVIEW_ENVELOPE = 151_000_000_000
E104_EXPECTED_RNG_DELTA = 67_174_400
WIDTH = 1024
TRAJECTORIES = 4096

METHOD_PATH = Path("methods/e104_orthogonal_antithetic.py")
HARNESS_PATH = Path("scripts/e104_production_shape.py")
RECEIPT_PATH = Path("research/E104_PRODUCTION_RECEIPT.md")
OUT = Path("e104-e100-production-budget-audit.json")


def _function_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            end = getattr(node, "end_lineno", None)
            if end is None:
                raise RuntimeError(f"missing end_lineno for {name}")
            return "\n".join(lines[node.lineno - 1 : end])
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == name:
                    end = getattr(child, "end_lineno", None)
                    if end is None:
                        raise RuntimeError(f"missing end_lineno for {name}")
                    return "\n".join(lines[child.lineno - 1 : end])
    raise RuntimeError(f"function {name} not found")


def _source_firewall() -> dict:
    method = METHOD_PATH.read_text(encoding="utf-8")
    harness = HARNESS_PATH.read_text(encoding="utf-8")
    receipt = RECEIPT_PATH.read_text(encoding="utf-8")

    billed = _function_source(method, "orthogonal_antithetic_billed")
    predict = _function_source(method, "predict")
    reference = _function_source(method, "orthogonal_antithetic_numpy")

    required_billed_tokens = [
        "fnp.random.default_rng",
        "rng.standard_normal",
        "fnp.linalg.qr",
        "fnp.diag",
        "fnp.where",
        "rng.chisquare",
        "fnp.sqrt",
        "fnp.multiply",
        "astype(fnp.float32)",
        "fnp.concatenate",
    ]
    required_predict_tokens = [
        "orthogonal_antithetic_billed",
        "fnp.asarray",
        "fnp.matmul",
        "fnp.maximum",
        "fnp.mean",
        "fnp.stack",
    ]

    budget_pos = harness.index("with flops.BudgetContext")
    diagnostic_pos = harness.index(
        "inputs = orthogonal_antithetic_numpy(WIDTH, PRODUCTION_SAMPLES, SAMPLE_SEED)"
    )

    return {
        "billed_generator_has_required_flopscope_ops": all(
            token in billed for token in required_billed_tokens
        ),
        "predict_has_required_flopscope_ops": all(
            token in predict for token in required_predict_tokens
        ),
        "plain_numpy_rng_absent_from_billed_generator": "np.random" not in billed,
        "plain_numpy_numeric_ops_absent_from_predict": "np." not in predict,
        "reference_numpy_rng_confined_to_reference_function": "np.random" in reference,
        "reference_diagnostic_occurs_after_budget_context": diagnostic_pos > budget_pos,
        "receipt_records_exact_rng_delta": str(E104_EXPECTED_RNG_DELTA) in receipt,
        "receipt_records_measured_total": str(E104_MEASURED_FLOPS) in receipt,
    }


def block_replicate_mse_fnp(final_h):
    """Unbiased randomization-MSE estimator from the two existing independent blocks.

    Layout is the frozen E104 layout:
      positive block 0, positive block 1, negative block 0, negative block 1.

    For independent block estimates Y0,Y1 and grand mean (Y0+Y1)/2,
    E[(Y0-Y1)^2 / 4] = Var((Y0+Y1)/2) coordinatewise.
    No target and no new random draw are used.
    """
    n = WIDTH
    if final_h.shape != (TRAJECTORIES, WIDTH):
        raise ValueError(f"unexpected final_h shape {final_h.shape}")

    paired0 = fnp.add(final_h[0:n], final_h[2 * n : 3 * n])
    paired1 = fnp.add(final_h[n : 2 * n], final_h[3 * n : 4 * n])

    block0 = fnp.sum(paired0, axis=0, dtype=fnp.float64) / float(2 * n)
    block1 = fnp.sum(paired1, axis=0, dtype=fnp.float64) / float(2 * n)

    delta = fnp.subtract(block0, block1)
    per_coordinate_mse = fnp.multiply(delta, delta) * 0.25
    return fnp.mean(per_coordinate_mse, dtype=fnp.float64)


def block_replicate_mse_numpy(final_h: np.ndarray) -> float:
    n = WIDTH
    paired0 = final_h[0:n].astype(np.float64) + final_h[2 * n : 3 * n].astype(np.float64)
    paired1 = final_h[n : 2 * n].astype(np.float64) + final_h[3 * n : 4 * n].astype(np.float64)
    block0 = np.sum(paired0, axis=0, dtype=np.float64) / float(2 * n)
    block1 = np.sum(paired1, axis=0, dtype=np.float64) / float(2 * n)
    delta = block0 - block1
    return float(np.mean(delta * delta, dtype=np.float64) * 0.25)


def _measure_error_estimator() -> dict:
    # Deterministic, target-free audit fixture. Its construction is outside the
    # measured BudgetContext because the production helper consumes existing final_h.
    rows = np.arange(TRAJECTORIES, dtype=np.float32)[:, None]
    cols = np.arange(WIDTH, dtype=np.float32)[None, :]
    fixture = ((rows % 17.0) * np.float32(1e-3) + (cols % 13.0) * np.float32(2e-4)).astype(
        np.float32
    )
    expected = block_replicate_mse_numpy(fixture)

    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        got = block_replicate_mse_fnp(fnp.asarray(fixture, dtype=fnp.float32))

    got_float = float(np.asarray(got))
    return {
        "flops": int(ctx.flops_used),
        "value": got_float,
        "numpy_reference": expected,
        "abs_error": abs(got_float - expected),
        "no_rng": True,
        "reuses_existing_final_activations": True,
        "independent_replicates": 2,
        "statistical_identity": "E[(Y0-Y1)^2/4] = Var((Y0+Y1)/2) coordinatewise",
        "limitation": (
            "unbiased randomization-MSE estimate, not a deterministic fixed-seed "
            "bias/error certificate"
        ),
    }


def main() -> None:
    hard_limit_real = UTIL_LIMIT * BUDGET
    hard_limit_floor = math.floor(hard_limit_real)
    remaining_before_error = hard_limit_floor - E104_MEASURED_FLOPS

    firewall = _source_firewall()
    error = _measure_error_estimator()

    total_with_error = E104_MEASURED_FLOPS + error["flops"]
    remaining_after_error = hard_limit_floor - total_with_error

    gates = {
        "e104_measured_below_competition_limit": E104_MEASURED_FLOPS <= hard_limit_floor,
        "e100_corrected_envelope_below_competition_limit": E100_CORRECTED_REVIEW_ENVELOPE
        <= hard_limit_floor,
        "all_candidate_rng_numeric_ops_billed": all(firewall.values()),
        "error_estimator_matches_numpy_le_1e_15": error["abs_error"] <= 1e-15,
        "error_estimator_has_no_rng": error["no_rng"],
        "error_estimator_fits_remaining_budget": total_with_error <= hard_limit_floor,
        "remaining_after_error_positive": remaining_after_error > 0,
    }

    result = {
        "schema": "arc.whitebox.e104_e100.production_budget_audit.v1",
        "scope": "review-only; no candidate scientific rerun; no benchmark/public targets",
        "competition_budget": {
            "budget": BUDGET,
            "utilization_limit": UTIL_LIMIT,
            "hard_flop_limit_real": hard_limit_real,
            "hard_flop_limit_floor": hard_limit_floor,
        },
        "e100": {
            "original_stage_a_static_total": 140_319_042_219,
            "corrected_review_envelope": E100_CORRECTED_REVIEW_ENVELOPE,
            "correction_reason": "float64 full-Q/R QR plus previously omitted RNG/helper work",
        },
        "e104": {
            "measured_flops": E104_MEASURED_FLOPS,
            "measured_utilization": E104_MEASURED_FLOPS / BUDGET,
            "measured_rng_delta_vs_e103": E104_EXPECTED_RNG_DELTA,
            "remaining_flops_before_error_estimator": remaining_before_error,
            "remaining_utilization_before_error_estimator": remaining_before_error / BUDGET,
        },
        "source_billing_firewall": firewall,
        "admissible_error_estimator": error,
        "with_error_estimator": {
            "total_flops": total_with_error,
            "utilization": total_with_error / BUDGET,
            "remaining_flops": remaining_after_error,
            "remaining_utilization": remaining_after_error / BUDGET,
        },
        "gates": gates,
        "decision": (
            "BUDGET_AND_BILLING_AUDIT_PASS"
            if all(gates.values())
            else "BUDGET_OR_BILLING_AUDIT_FAIL"
        ),
        "scientific_go": False,
        "raw_mse_evaluated": False,
        "notes": [
            "E104 measured prediction path bills Gaussian RNG, chi-square RNG, QR/sign/sqrt/radial transforms, casts, dense forwards, ReLUs and reductions through flopscope.",
            "The NumPy reference sampler in the E104 harness executes after the BudgetContext and is target-free diagnostic-only; it is not part of the returned prediction.",
            "Synthetic MLP weight generation is environment/input construction outside Estimator.predict and is not candidate estimator cost.",
            "The proposed two-block MSE estimator requires no fresh RNG or forward trajectories and can be integrated in a successor experiment without changing the returned prediction.",
            "Its unbiasedness concerns randomization variance/MSE under the frozen unbiased sampling law; it does not certify fixed-seed bias.",
        ],
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_E100_PRODUCTION_BUDGET_AUDIT=" + json.dumps(result, sort_keys=True))

    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
