"""Synthetic-only E091 implementation-bridge falsifier.

This script never loads whestbench datasets, public data, scorer outputs, holdouts, or full-suite
artifacts. It verifies the committed freeze/corpus hashes and executes only the protocol-defined
tiny deterministic counterexample plus a flopscope-measured deploy path over that same synthetic
corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from methods.e091_loo_readiness import (
    PHASE2_BUDGET,
    build_tiny_problem,
    dense_dot_cost,
    direct_loo_predictions,
    full_ridge_fit,
    loo_press_predictions,
    measure_tiny_deploy,
    signed_influence_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research" / "E091_FREEZE.json"
CORPUS_PATH = ROOT / "research" / "E091_SYNTHETIC_CORPUS.json"


def canonical_payload_sha256(payload: object) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_hashed_record(path: Path) -> tuple[dict, str]:
    record = json.loads(path.read_text(encoding="utf-8"))
    payload = record["payload"]
    observed = canonical_payload_sha256(payload)
    declared = str(record["payload_sha256"])
    if observed != declared:
        raise AssertionError(f"{path.name} hash mismatch: {observed} != {declared}")
    return payload, observed


def _relative_frobenius(diff: np.ndarray, reference: np.ndarray) -> float:
    denom = float(np.linalg.norm(reference))
    return float(np.linalg.norm(diff) / denom) if denom > 0.0 else float(np.linalg.norm(diff))


def run_falsifier() -> dict[str, object]:
    freeze, freeze_hash = load_hashed_record(FREEZE_PATH)
    corpus, corpus_hash = load_hashed_record(CORPUS_PATH)

    expected_columns = ["1", "u0", "u1", "u0^2+u1^2"]
    freeze_ok = bool(
        freeze["schema"] == "arc.whitebox.e091.freeze.v1"
        and freeze["protocol_commit"] == "ceb7d53fbed3a0c5366fed0da878a8d6b11b8055"
        and freeze["feature_builder"]["columns"] == expected_columns
        and freeze["feature_builder"]["p"] == 4
        and freeze["feature_builder"]["target_arguments"] == []
        and freeze["preprocessing"]
        == {
            "dtype": "float64",
            "centering": "none",
            "scaling": "none",
            "imputation": "none",
            "row_weighting": "uniform",
            "feature_selection": "none",
        }
        and freeze["ridge"]["lambda"] == 1.0
        and freeze["ridge"]["jitter"] == "forbidden"
        and freeze["ridge"]["pseudoinverse"] == "forbidden"
    )

    disjoint = corpus["disjointness"]
    corpus_disjoint_ok = bool(
        corpus["schema"] == "arc.whitebox.e091.synthetic_corpus.v1"
        and corpus["source_kind"] == "synthetic_reference_only"
        and disjoint["public_dataset_ids"] == []
        and disjoint["scorer_dataset_ids"] == []
        and disjoint["holdout_dataset_ids"] == []
        and disjoint["full_suite_dataset_ids"] == []
        and disjoint["generated_from_benchmark_targets"] is False
    )

    X, Z, meta = build_tiny_problem()
    manifest_inputs = np.asarray(corpus["inputs"], dtype=np.float64)
    manifest_Z = np.asarray(corpus["residual_targets"], dtype=np.float64)
    manifest_input_max_abs = float(np.max(np.abs(manifest_inputs - meta["inputs"])))
    manifest_target_max_abs = float(np.max(np.abs(manifest_Z - Z)))
    manifest_parity_ok = bool(
        manifest_inputs.shape == meta["inputs"].shape
        and manifest_Z.shape == Z.shape
        and manifest_input_max_abs == 0.0
        and manifest_target_max_abs <= 1e-15
        and corpus["row_ids"] == [f"syn-{i:03d}" for i in range(len(X))]
    )

    lam = float(freeze["ridge"]["lambda"])
    press, h = loo_press_predictions(X, Z, lam)
    direct = direct_loo_predictions(X, Z, lam)
    parity_diff = press - direct
    parity_max_abs = float(np.max(np.abs(parity_diff)))
    parity_rel_frob = _relative_frobenius(parity_diff, direct)
    min_h = float(np.min(h))
    max_h = float(np.max(h))
    min_one_minus_h = float(np.min(1.0 - h))

    i = int(freeze["counterexample"]["row_zero_based"])
    delta = np.asarray(freeze["counterexample"]["delta"], dtype=np.float64)
    full0, B = full_ridge_fit(X, Z, lam)
    loo0, _ = loo_press_predictions(X, Z, lam)
    Zp = Z.copy()
    Zp[i] += delta
    full1, _ = full_ridge_fit(X, Zp, lam)
    loo1, _ = loo_press_predictions(X, Zp, lam)
    full_fit_self_target_sensitivity = float(np.max(np.abs(full1[i] - full0[i])))
    loo_self_target_invariance = float(np.max(np.abs(loo1[i] - loo0[i])))

    influence = signed_influence_metrics(X, Z, lam)
    influence_ok = bool(
        influence["max_row_l1"] <= 4.0
        and influence["max_negative_mass"] <= 1.5
        and influence["max_abs_weight"] <= 2.0
        and influence["max_abs_loo_prediction"] <= 4.0 * influence["max_abs_target"]
        and influence["finite"] is True
    )

    press_repeat, h_repeat = loo_press_predictions(X, Z, lam)
    _, B_repeat = full_ridge_fit(X, Z, lam)
    influence_repeat = signed_influence_metrics(X, Z, lam)
    deterministic_max_abs = float(
        max(
            np.max(np.abs(press_repeat - press)),
            np.max(np.abs(h_repeat - h)),
            np.max(np.abs(B_repeat - B)),
            np.max(
                np.abs(
                    np.asarray(influence_repeat["weights"], dtype=np.float64)
                    - np.asarray(influence["weights"], dtype=np.float64)
                )
            ),
        )
    )

    expected_deploy = np.asarray(meta["base"] + full0, dtype=np.float64)
    measured_deploy, measured_cost = measure_tiny_deploy(meta["inputs"], B)
    measured_repeat, measured_cost_repeat = measure_tiny_deploy(meta["inputs"], B)
    measured_output_max_abs = float(np.max(np.abs(measured_deploy - expected_deploy)))
    measured_output_rel_frob = _relative_frobenius(
        measured_deploy - expected_deploy, expected_deploy
    )
    measured_repeat_max_abs = float(np.max(np.abs(measured_repeat - measured_deploy)))
    measured_component_sum = int(sum(measured_cost["component_flops"].values()))
    measured_all_in_flops = int(measured_cost["all_in_flops"])
    measured_additive = measured_component_sum == measured_all_in_flops
    measured_repeat_cost_equal = bool(
        measured_cost_repeat["all_in_flops"] == measured_cost["all_in_flops"]
        and measured_cost_repeat["component_flops"] == measured_cost["component_flops"]
    )

    synthetic_cost = dense_dot_cost(p=int(X.shape[1]), q=int(Z.shape[1]), dtype_bytes=4)
    phase2_correction = dense_dot_cost(p=int(X.shape[1]), q=16384, dtype_bytes=4)
    phase2_cap = dense_dot_cost(p=16, q=16384, dtype_bytes=4)

    base_linear_flops = 19
    feature_flops = 3
    correction_flops = int(synthetic_cost["exact_flops"])
    synthetic_all_in_flops = base_linear_flops + feature_flops + correction_flops
    synthetic_all_in_utilization = synthetic_all_in_flops / PHASE2_BUDGET

    gates = {
        "freeze_hash": freeze_hash
        == "80861326ea3258b67792801c529dacd1cf40fbc1cae9236f63bbea71afce80a1",
        "corpus_hash": corpus_hash
        == "28c037d525a3e4e9b9d4c1955a05f9ccae1ff91b2a62696e742129ce95776ae7",
        "frozen_target_independent_config": freeze_ok,
        "corpus_disjoint": corpus_disjoint_ok,
        "manifest_parity": manifest_parity_ok,
        "identity_max_abs": parity_max_abs <= 1e-12,
        "identity_rel_frob": parity_rel_frob <= 1e-12,
        "leverage_denominator": min_one_minus_h >= 1e-6,
        "full_fit_counterexample": full_fit_self_target_sensitivity >= 1e-2,
        "loo_self_target_invariance": loo_self_target_invariance <= 1e-12,
        "signed_influence": influence_ok,
        "finite": bool(
            np.all(np.isfinite(X))
            and np.all(np.isfinite(Z))
            and np.all(np.isfinite(press))
            and np.all(np.isfinite(B))
        ),
        "deterministic": deterministic_max_abs == 0.0,
        "measured_deploy_output_max_abs": measured_output_max_abs <= 1e-12,
        "measured_deploy_output_rel_frob": measured_output_rel_frob <= 1e-12,
        "measured_deploy_component_additivity": measured_additive,
        "measured_deploy_deterministic": measured_repeat_max_abs == 0.0
        and measured_repeat_cost_equal,
        "measured_deploy_finite": bool(np.all(np.isfinite(measured_deploy))),
        "measured_deploy_nonzero_bill": measured_all_in_flops > 0,
        "phase2_correction_cost": bool(
            phase2_cap["exact_flops"] == 507_904
            and phase2_cap["ceiling_flops"] == 524_288
            and phase2_cap["ceiling_fraction"] <= 2.5e-7
            and phase2_cap["coefficient_bytes"] == 1_048_576
        ),
    }
    passed = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e091.synthetic_falsifier.v2",
        "experiment": "E091",
        "decision": "READINESS_IMPLEMENTATION_GO" if passed else "READINESS_NO_GO",
        "scientific_go": False,
        "scope": {
            "public": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets_read": False,
        },
        "hashes": {
            "freeze_payload_sha256": freeze_hash,
            "corpus_payload_sha256": corpus_hash,
        },
        "freeze": {
            "feature_columns": expected_columns,
            "p": int(X.shape[1]),
            "preprocessing": freeze["preprocessing"],
            "lambda": lam,
        },
        "corpus": {
            "corpus_id": corpus["corpus_id"],
            "n": int(X.shape[0]),
            "q": int(Z.shape[1]),
            "manifest_input_max_abs": manifest_input_max_abs,
            "manifest_target_max_abs": manifest_target_max_abs,
        },
        "identity": {
            "press_vs_direct_max_abs": parity_max_abs,
            "press_vs_direct_rel_frob": parity_rel_frob,
            "min_h": min_h,
            "max_h": max_h,
            "min_one_minus_h": min_one_minus_h,
        },
        "leakage_falsifier": {
            "counterexample_row": i,
            "full_fit_self_target_sensitivity_max_abs": full_fit_self_target_sensitivity,
            "loo_self_target_invariance_max_abs": loo_self_target_invariance,
        },
        "signed_influence": {
            "max_row_l1": influence["max_row_l1"],
            "max_negative_mass": influence["max_negative_mass"],
            "max_abs_weight": influence["max_abs_weight"],
            "max_abs_loo_prediction": influence["max_abs_loo_prediction"],
            "max_abs_target": influence["max_abs_target"],
            "finite": influence["finite"],
        },
        "determinism": {"max_abs_repeat_difference": deterministic_max_abs},
        "measured_deploy": {
            "output_max_abs_vs_numpy_reference": measured_output_max_abs,
            "output_rel_frob_vs_numpy_reference": measured_output_rel_frob,
            "repeat_output_max_abs": measured_repeat_max_abs,
            "repeat_cost_equal": measured_repeat_cost_equal,
            "component_flops": measured_cost["component_flops"],
            "component_flops_sum": measured_component_sum,
            "component_residual_wall_s": measured_cost["component_residual_wall_s"],
            "component_wall_s": measured_cost["component_wall_s"],
            "all_in_flops": measured_all_in_flops,
            "actual_all_in_utilization_vs_phase2_budget": measured_cost[
                "actual_all_in_utilization"
            ],
            "all_in_residual_wall_s": measured_cost["all_in_residual_wall_s"],
            "all_in_wall_s": measured_cost["all_in_wall_s"],
            "component_additivity": measured_additive,
        },
        "component_cost": {
            "synthetic_base_linear_scalar_flops": base_linear_flops,
            "synthetic_feature_scalar_flops": feature_flops,
            "synthetic_correction": synthetic_cost,
            "synthetic_all_in_scalar_flops": synthetic_all_in_flops,
            "synthetic_all_in_utilization_vs_phase2_budget": synthetic_all_in_utilization,
            "phase2_bridge_correction_p4_q16384": phase2_correction,
            "phase2_readiness_cap_p16_q16384": phase2_cap,
            "production_whole_candidate_all_in_utilization": None,
            "production_whole_candidate_blocker": (
                "No concrete Phase-2 base estimator is frozen by E091; the measured all-in "
                "value in this artifact is the complete frozen synthetic deploy path only, "
                "not a production scientific-candidate utilization claim."
            ),
        },
        "coefficient_matrix": {
            "shape": list(B.shape),
            "max_abs": float(np.max(np.abs(B))),
            "frobenius": float(np.linalg.norm(B)),
        },
        "gates": gates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("e091-readiness-diagnostic.json")
    )
    args = parser.parse_args()
    result = run_falsifier()
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print("E091_READINESS_JSON=" + json.dumps(result, sort_keys=True))
    if result["decision"] != "READINESS_IMPLEMENTATION_GO":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
