import hashlib
import inspect
import json
from pathlib import Path

import numpy as np

from methods.e091_production_bridge import (
    FEATURE_COLUMNS,
    FEATURE_P,
    apply_shared_final_layer_ridge,
    final_layer_coordinate_features,
    production_cost_ceiling,
)

ROOT = Path(__file__).resolve().parents[1]


def _payload_hash(payload):
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _tiny_state(width=8, depth=4):
    rng = np.random.default_rng(91091)
    base = rng.normal(size=(depth, width)).astype(np.float64)
    weight = rng.normal(scale=1.0 / np.sqrt(width), size=(width, width)).astype(
        np.float64
    )
    return base, weight


def test_production_freeze_hash_and_target_independence():
    record = json.loads(
        (ROOT / "research" / "E091_PRODUCTION_BRIDGE_FREEZE.json").read_text(
            encoding="utf-8"
        )
    )
    assert _payload_hash(record["payload"]) == record["payload_sha256"]
    assert record["payload_sha256"] == (
        "4df3155d926e1074bf8e333fd622877056aa99f8f7d09fd3707e50f9156ea331"
    )
    payload = record["payload"]
    assert payload["status"] == "PRE_TARGET_FREEZE"
    assert payload["selection_policy"]["selected_experiment"] == "E043"
    assert payload["selection_policy"]["selected_commit"] == (
        "d0108f7faccaa656d3908f5afeaa90e056881c71"
    )
    assert payload["selection_policy"]["selected_estimator_blob"] == (
        "8777dde2b848dd8ae855f9040ca27b4c6f235989"
    )
    assert payload["feature_map"]["p"] == FEATURE_P
    assert tuple(payload["feature_map"]["columns"]) == FEATURE_COLUMNS
    assert payload["feature_map"]["target_arguments"] == []
    assert payload["corpus_policy"]["new_calibration_targets_materialized_before_this_freeze"] is False
    sig = inspect.signature(final_layer_coordinate_features)
    assert list(sig.parameters) == ["base_prediction", "last_weight"]


def test_feature_shape_finite_and_permutation_equivariance():
    base, weight = _tiny_state()
    X = final_layer_coordinate_features(base, weight)
    assert X.shape == (8, 16)
    assert np.all(np.isfinite(X))

    out_perm = np.array([3, 7, 0, 5, 2, 6, 1, 4])
    base_out = base.copy()
    base_out[-1] = base[-1, out_perm]
    weight_out = weight[:, out_perm]
    X_out = final_layer_coordinate_features(base_out, weight_out)
    np.testing.assert_allclose(X_out, X[out_perm], rtol=0.0, atol=2e-15)

    in_perm = np.array([6, 0, 7, 2, 4, 1, 5, 3])
    base_in = base.copy()
    base_in[-2] = base[-2, in_perm]
    weight_in = weight[in_perm, :]
    X_in = final_layer_coordinate_features(base_in, weight_in)
    np.testing.assert_allclose(X_in, X, rtol=0.0, atol=2e-15)


def test_shared_correction_only_changes_final_layer_and_is_equivariant():
    base, weight = _tiny_state()
    beta = np.linspace(-0.02, 0.03, FEATURE_P, dtype=np.float64)
    corrected = apply_shared_final_layer_ridge(base, weight, beta)
    np.testing.assert_array_equal(corrected[:-1], base[:-1])

    out_perm = np.array([3, 7, 0, 5, 2, 6, 1, 4])
    base_perm = base.copy()
    base_perm[-1] = base[-1, out_perm]
    weight_perm = weight[:, out_perm]
    corrected_perm = apply_shared_final_layer_ridge(base_perm, weight_perm, beta)
    np.testing.assert_allclose(
        corrected_perm[-1], corrected[-1, out_perm], rtol=0.0, atol=2e-15
    )


def test_phase2_whole_candidate_cost_ceiling_is_under_budget():
    cost = production_cost_ceiling(1024)
    assert cost["base_flops"] == 128_511_719_225
    assert cost["feature_flops_ceiling"] == 16_777_216
    assert cost["correction_flops_ceiling"] == 32_768
    assert cost["whole_candidate_flops_ceiling"] == 128_528_529_209
    assert abs(cost["whole_candidate_utilization_ceiling"] - 0.058448008171126276) <= 1e-18
    assert cost["passes_utilization_gate"] is True
    assert cost["whole_candidate_utilization_ceiling"] <= 0.135
