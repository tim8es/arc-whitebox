from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from methods.e091_production_bridge import (
    E043_BASE_FLOPS,
    FEATURE_P,
    PHASE2_BUDGET,
    final_layer_coordinate_features,
    production_cost_ceiling,
)

E043_RUN = 35017111251
E043_JOB = 104543203284
E043_RAW_FINAL_MSE = 3.642770734802907e-06
RAW_TARGET = 1.89e-08
EXPECTED_E043_BLOB = "8777dde2b848dd8ae855f9040ca27b4c6f235989"
EXPECTED_E043_COMMIT = "d0108f7faccaa656d3908f5afeaa90e056881c71"

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "research" / "E091_PRODUCTION_BRIDGE_FREEZE.json"
OLD_SCREEN = ROOT / "research" / "E091_PRODUCTION_BASE_SCREEN.json"
OUT = ROOT / "e091_production_base_falsifier.json"


def _adversarial_span_test() -> dict[str, float | int | bool]:
    # Deliberately smaller than production width: this is a structural span falsifier,
    # not an accuracy estimate.  The same shared-beta geometry holds at width 1024.
    n = 64
    t = np.linspace(-1.5, 1.5, n, dtype=np.float64)
    prev = np.sin(1.7 * t) + 0.15 * t
    final = np.maximum(0.0, 0.7 * prev + 0.2 * np.cos(2.3 * t))
    base = np.vstack((0.5 * prev, prev, final))

    i = np.arange(n, dtype=np.float64)[:, None]
    j = np.arange(n, dtype=np.float64)[None, :]
    weight = 0.02 * np.sin(0.17 * (i + 1.0) * (j + 1.0)) + 0.01 * np.cos(
        0.11 * (i - j)
    )

    X = final_layer_coordinate_features(base, weight)
    rank = int(np.linalg.matrix_rank(X))

    k = np.arange(n, dtype=np.float64)
    z0 = np.sin(0.37 * (k + 1.0)) + 0.3 * np.cos(0.11 * (k + 1.0) ** 2)
    proj_coef, *_ = np.linalg.lstsq(X, z0, rcond=None)
    z_perp = z0 - X @ proj_coef
    orthogonality_max_abs = float(np.max(np.abs(X.T @ z_perp)))

    beta = np.linalg.solve(X.T @ X + np.eye(FEATURE_P), X.T @ z_perp)
    corrected = z_perp - X @ beta
    before = float(np.mean(z_perp * z_perp))
    after = float(np.mean(corrected * corrected))
    ratio = after / before

    return {
        "width": n,
        "feature_rank": rank,
        "feature_dim": FEATURE_P,
        "orthogonality_max_abs": orthogonality_max_abs,
        "ridge_beta_l2": float(np.linalg.norm(beta)),
        "mse_before": before,
        "mse_after": after,
        "mse_ratio_after_over_before": ratio,
        "uncorrectable_gate": bool(ratio >= 0.999999999),
    }


def main() -> int:
    freeze = json.loads(FREEZE.read_text())
    old_screen = json.loads(OLD_SCREEN.read_text())
    payload = freeze["payload"]
    selected = payload["selection_policy"]

    cost = production_cost_ceiling(1024)
    expected_feature = 16 * 1024 * 1024
    expected_correction = 2 * FEATURE_P * 1024
    expected_whole = E043_BASE_FLOPS + expected_feature + expected_correction

    provenance_gate = bool(
        selected["selected_experiment"] == "E043"
        and selected["selected_commit"] == EXPECTED_E043_COMMIT
        and selected["selected_estimator_blob"] == EXPECTED_E043_BLOB
        and selected["selected_base_flops"] == E043_BASE_FLOPS
        and payload["cost_gate"]["whole_candidate_flops_ceiling"] == expected_whole
    )
    arithmetic_gate = bool(
        cost["base_flops"] == E043_BASE_FLOPS
        and cost["feature_flops_ceiling"] == expected_feature
        and cost["correction_flops_ceiling"] == expected_correction
        and cost["whole_candidate_flops_ceiling"] == expected_whole
        and cost["passes_utilization_gate"]
    )

    stale_v1_detected = bool(
        old_screen["status"] == "NO_CURRENT_MEASURED_BASE_ADMISSIBLE"
        and selected["selected_experiment"] == "E043"
        and float(selected["selected_base_utilization"]) <= 0.135
    )

    adversarial = _adversarial_span_test()
    raw_multiple = E043_RAW_FINAL_MSE / RAW_TARGET
    required_fractional_reduction = 1.0 - RAW_TARGET / E043_RAW_FINAL_MSE

    receipt = {
        "schema": "arc.whitebox.e091.production_base_falsifier.v1",
        "experiment": "E091",
        "scope": "local_structural_no_public_no_scorer_no_holdout",
        "e043_primary_measurement": {
            "run": E043_RUN,
            "job": E043_JOB,
            "commit": EXPECTED_E043_COMMIT,
            "estimator_blob": EXPECTED_E043_BLOB,
            "flops_used": E043_BASE_FLOPS,
            "raw_final_mse": E043_RAW_FINAL_MSE,
            "raw_target": RAW_TARGET,
            "raw_over_target_multiple": raw_multiple,
            "required_fractional_mse_reduction": required_fractional_reduction,
        },
        "current_code_arithmetic": cost,
        "gates": {
            "freeze_matches_e043_primary_evidence": provenance_gate,
            "current_code_matches_frozen_arithmetic": arithmetic_gate,
            "v1_screen_is_stale_on_current_head": stale_v1_detected,
            "adversarial_orthogonal_residual_remains_uncorrected": adversarial[
                "uncorrectable_gate"
            ],
        },
        "adversarial_feature_span_falsifier": adversarial,
        "decision": "BUDGET_PASS_ACCURACY_SPAN_KILL_GATE_REQUIRED",
        "scientific_go": False,
        "terminal_no_go": False,
        "next_gate": (
            "On the preregistered disjoint synthetic-network corpus, compute the held-out "
            "residual component outside col(X). If that component alone implies final-layer "
            "MSE > 1.89e-8, terminate E091 before public/scorer/holdout/full."
        ),
    }

    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("E091_PRODUCTION_BASE_FALSIFIER=" + json.dumps(receipt, sort_keys=True))

    required = list(receipt["gates"].values())
    return 0 if all(required) else 2


if __name__ == "__main__":
    raise SystemExit(main())
