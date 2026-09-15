from __future__ import annotations

import numpy as np

from methods.e044_fixed_checkpoint_k3_replay import (
    CHECKPOINTS,
    PINNED_BLOB_SHA,
    PINNED_COMMIT,
    PINNED_PATH,
    checkpoint_live_counts,
    checkpoint_source_uses,
    compose_newborn_operator,
    compose_segment_operator,
    fetch_and_patch_pinned_source,
    reconstruct_checkpoint,
)


def test_frozen_identity_and_checkpoint_schedule():
    assert PINNED_COMMIT == "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
    assert PINNED_PATH == "estimators/estimator_v25.py"
    assert PINNED_BLOB_SHA == "195373a110215256b759d7c172ba8c923c62e5cc"
    assert CHECKPOINTS == (7, 11, 15)
    assert checkpoint_live_counts(16) == (7, 11, 15)
    assert checkpoint_source_uses(16) == 33


def _explicit_segment(weights, w1_hist, start_checkpoint, checkpoint):
    out = None
    for layer in range(start_checkpoint + 1, checkpoint + 1):
        w = weights[layer].T
        wd = w * w1_hist[layer - 1][None, :]
        out = wd if out is None else wd @ out
    return out


def test_composed_segment_equals_explicit_layer_transport():
    weights = [
        np.asarray([[1.0, 0.2], [0.1, 0.9]]),
        np.asarray([[0.8, 0.3], [-0.2, 1.1]]),
        np.asarray([[1.2, -0.1], [0.4, 0.7]]),
        np.asarray([[0.9, 0.5], [0.2, 1.0]]),
    ]
    w1 = [
        np.asarray([0.6, 0.8]),
        np.asarray([0.7, 0.5]),
        np.asarray([0.9, 0.4]),
    ]
    got = compose_segment_operator(np, weights, w1, 0, 3)
    ref = _explicit_segment(weights, w1, 0, 3)
    np.testing.assert_allclose(got, ref, rtol=0.0, atol=1e-14)


def test_newborn_operator_is_raw_first_then_wd():
    weights = [
        np.eye(2),
        np.asarray([[1.0, 0.2], [0.3, 0.8]]),
        np.asarray([[0.7, -0.1], [0.4, 1.1]]),
        np.asarray([[1.2, 0.5], [-0.2, 0.9]]),
    ]
    w1 = [
        np.asarray([0.5, 0.7]),
        np.asarray([0.8, 0.6]),
        np.asarray([0.4, 0.9]),
    ]
    got = compose_newborn_operator(np, weights, w1, birth=0, checkpoint=3)
    ref = weights[3].T * w1[2][None, :]
    ref = ref @ (weights[2].T * w1[1][None, :])
    ref = ref @ weights[1].T
    np.testing.assert_allclose(got, ref, rtol=0.0, atol=1e-14)


def test_checkpoint_reconstruction_preserves_complete_record_cardinality():
    n = 2
    weights = [np.eye(n) for _ in range(4)]
    w1 = [np.asarray([0.5, 0.75]), np.asarray([0.8, 0.6]), np.asarray([0.9, 0.4])]
    births = []
    for b in range(3):
        a = np.eye(n) * float(b + 1)
        rr = np.full((n, 2), float(b + 2))
        lr = np.full((n, 2), float(b + 3))
        s = np.full(n, float(b + 4))
        e = np.full(n, float(b + 5))
        ff = np.full((n, 2), float(b + 6))
        births.append((a, rr, lr, s, e, ff))

    state = reconstruct_checkpoint(
        np,
        weights,
        w1,
        births,
        checkpoint=3,
        previous_checkpoint=-1,
        previous_state=None,
    )
    assert state["A"].shape == (3, n, n)
    assert state["P"].shape == (3, n, n)
    assert state["Z"].shape == (3, n, 2)
    assert state["L"].shape == (3, n, 2)
    assert state["Zf"].shape == (3, n, 2)
    assert state["births"] == (0, 1, 2)
    for b in range(3):
        op = compose_newborn_operator(np, weights, w1, birth=b, checkpoint=3)
        np.testing.assert_allclose(state["P"][b], op, rtol=0.0, atol=1e-14)
        np.testing.assert_allclose(state["A"][b], op @ births[b][0], rtol=0.0, atol=1e-14)
        np.testing.assert_allclose(state["Z"][b], op @ births[b][1], rtol=0.0, atol=1e-14)
        np.testing.assert_allclose(state["L"][b], births[b][2], rtol=0.0, atol=0.0)
        np.testing.assert_allclose(state["Zf"][b], op @ births[b][5], rtol=0.0, atol=1e-14)


def test_real_pinned_patch_targets_unique_and_no_selector_logic():
    patched, provenance = fetch_and_patch_pinned_source()
    assert provenance["blob_sha"] == PINNED_BLOB_SHA
    assert all(v == 1 for v in provenance["patch_counts"].values())
    assert "E044_CHECKPOINTS = (7, 11, 15)" in patched
    assert "reconstruct_checkpoint" in patched
    assert "V21_NO_CONFINE" in patched
    for forbidden in ("knapsack", "KEEP_BIRTHS", "capacity", "selector"):
        assert forbidden not in patched
