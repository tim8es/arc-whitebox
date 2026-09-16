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
    target_free_features,
    tiny_relu_base,
)

ROOT = Path(__file__).resolve().parents[1]


def _payload_hash(payload):
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def test_exact_rowwise_loo_identity_and_leverage():
    X, Z, _ = build_tiny_problem()
    lam = 1.0
    press, h = loo_press_predictions(X, Z, lam)
    direct = direct_loo_predictions(X, Z, lam)
    diff = press - direct
    assert np.max(np.abs(diff)) <= 1e-12
    assert np.linalg.norm(diff) / np.linalg.norm(direct) <= 1e-12
    assert np.min(1.0 - h) >= 1e-6


def test_omitted_target_invariance_and_full_fit_counterexample():
    X, Z, _ = build_tiny_problem()
    lam = 1.0
    i = 3
    delta = np.array([7.0, -5.0], dtype=np.float64)

    full0, _ = full_ridge_fit(X, Z, lam)
    loo0, _ = loo_press_predictions(X, Z, lam)

    Zp = Z.copy()
    Zp[i] += delta
    full1, _ = full_ridge_fit(X, Zp, lam)
    loo1, _ = loo_press_predictions(X, Zp, lam)

    assert np.max(np.abs(full1[i] - full0[i])) >= 1e-2
    assert np.max(np.abs(loo1[i] - loo0[i])) <= 1e-12


def test_signed_influence_gates():
    X, Z, _ = build_tiny_problem()
    metrics = signed_influence_metrics(X, Z, 1.0)
    assert metrics["max_row_l1"] <= 4.0
    assert metrics["max_negative_mass"] <= 1.5
    assert metrics["max_abs_weight"] <= 2.0
    assert metrics["max_abs_loo_prediction"] <= 4.0 * metrics["max_abs_target"]
    assert metrics["finite"] is True


def test_phase2_dense_correction_cost_gate():
    cost = dense_dot_cost(p=16, q=16384, dtype_bytes=4)
    assert cost["exact_flops"] == 507_904
    assert cost["ceiling_flops"] == 524_288
    assert cost["ceiling_fraction"] == 524_288 / PHASE2_BUDGET
    assert cost["ceiling_fraction"] <= 2.5e-7
    assert cost["coefficient_bytes"] == 1_048_576


def test_measured_tiny_deploy_has_actual_component_and_all_in_bill():
    X, Z, meta = build_tiny_problem()
    _, B = full_ridge_fit(X, Z, 1.0)
    expected = tiny_relu_base(meta["inputs"]) + target_free_features(meta["inputs"]) @ B

    measured, metrics = measure_tiny_deploy(meta["inputs"], B)
    repeat, repeat_metrics = measure_tiny_deploy(meta["inputs"], B)

    assert np.max(np.abs(measured - expected)) <= 1e-12
    assert np.array_equal(measured, repeat)
    assert metrics["component_flops"]["base"] > 0
    assert metrics["component_flops"]["features"] > 0
    assert metrics["component_flops"]["correction_dot"] > 0
    assert metrics["component_flops"]["output_add"] > 0
    assert metrics["all_in_flops"] == sum(metrics["component_flops"].values())
    assert metrics["actual_all_in_utilization"] == metrics["all_in_flops"] / PHASE2_BUDGET
    assert repeat_metrics["all_in_flops"] == metrics["all_in_flops"]
    assert repeat_metrics["component_flops"] == metrics["component_flops"]


def test_committed_freeze_and_disjoint_corpus_hashes():
    freeze = json.loads(
        (ROOT / "research" / "E091_FREEZE.json").read_text(encoding="utf-8")
    )
    corpus = json.loads(
        (ROOT / "research" / "E091_SYNTHETIC_CORPUS.json").read_text(encoding="utf-8")
    )

    assert _payload_hash(freeze["payload"]) == freeze["payload_sha256"]
    assert freeze["payload_sha256"] == (
        "80861326ea3258b67792801c529dacd1cf40fbc1cae9236f63bbea71afce80a1"
    )
    assert freeze["payload"]["feature_builder"]["target_arguments"] == []
    assert freeze["payload"]["preprocessing"] == {
        "dtype": "float64",
        "centering": "none",
        "scaling": "none",
        "imputation": "none",
        "row_weighting": "uniform",
        "feature_selection": "none",
    }
    assert freeze["payload"]["ridge"]["lambda"] == 1.0

    assert _payload_hash(corpus["payload"]) == corpus["payload_sha256"]
    assert corpus["payload_sha256"] == (
        "28c037d525a3e4e9b9d4c1955a05f9ccae1ff91b2a62696e742129ce95776ae7"
    )
    assert corpus["payload"]["source_kind"] == "synthetic_reference_only"
    disjoint = corpus["payload"]["disjointness"]
    assert disjoint["public_dataset_ids"] == []
    assert disjoint["scorer_dataset_ids"] == []
    assert disjoint["holdout_dataset_ids"] == []
    assert disjoint["full_suite_dataset_ids"] == []
    assert disjoint["generated_from_benchmark_targets"] is False

    X, Z, meta = build_tiny_problem()
    manifest_inputs = np.asarray(corpus["payload"]["inputs"], dtype=np.float64)
    manifest_targets = np.asarray(
        corpus["payload"]["residual_targets"], dtype=np.float64
    )
    assert np.max(np.abs(manifest_inputs - meta["inputs"])) == 0.0
    assert np.max(np.abs(manifest_targets - Z)) <= 1e-15
    assert X.shape == (7, 4)
