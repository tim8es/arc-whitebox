from __future__ import annotations

import numpy as np

from methods.e042_source_column_cubature import (
    PINNED_BLOB_SHA,
    PINNED_COMMIT,
    PINNED_PATH,
    Q_SUITE,
    cubature_gram,
    fetch_and_patch_pinned_source,
    quadrature_weight,
    source_nodes,
    transport_selected_columns,
)


def test_pinned_identity_and_frozen_suite_q():
    assert PINNED_COMMIT == "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
    assert PINNED_PATH == "estimators/estimator_v25.py"
    assert PINNED_BLOB_SHA == "195373a110215256b759d7c172ba8c923c62e5cc"
    assert Q_SUITE == 320


def test_suite_nodes_are_unique_deterministic_and_birth_dependent():
    j0 = source_nodes(1024, 0)
    j1 = source_nodes(1024, 1)
    np.testing.assert_array_equal(j0, source_nodes(1024, 0))
    assert j0.shape == (320,)
    assert len(set(j0.tolist())) == 320
    assert int(j0.min()) >= 0 and int(j0.max()) < 1024
    assert not np.array_equal(j0, j1)
    assert len(set(j1.tolist())) == 320


def test_quadrature_weight_preserves_constant_measure():
    for n in (8, 16, 257, 1024):
        j = source_nodes(n, 3)
        w = quadrature_weight(n)
        assert abs(w * len(j) - n) <= 1e-12


def test_cubature_gram_is_exact_at_full_nodes_and_matches_selected_reference():
    rng = np.random.default_rng(7)
    a = rng.normal(size=(7, 7))
    p = rng.normal(size=(7, 7))
    v = rng.normal(size=7)
    full = (a * p * v[None, :]) @ a.T
    got_full = cubature_gram(a, p, v, np.arange(7), 1.0)
    np.testing.assert_allclose(got_full, full, rtol=0.0, atol=1e-12)

    cols = np.array([0, 2, 5])
    omega = 7.0 / 3.0
    selected_ref = omega * (a[:, cols] * p[:, cols] * v[cols][None, :]) @ a[:, cols].T
    got_selected = cubature_gram(a, p, v, cols, omega)
    np.testing.assert_allclose(got_selected, selected_ref, rtol=0.0, atol=1e-12)


def test_linear_transport_preserves_selected_column_identity_across_two_layers():
    rng = np.random.default_rng(11)
    a = rng.normal(size=(9, 9))
    w1 = rng.normal(size=(9, 9))
    w2 = rng.normal(size=(9, 9))
    cols = np.array([0, 3, 8])
    got = transport_selected_columns([w1, w2], a, cols)
    ref = w2 @ (w1 @ a[:, cols])
    np.testing.assert_allclose(got, ref, rtol=0.0, atol=1e-12)
    assert got.shape == (9, 3)


def test_real_pinned_v25_patch_targets_are_exact_and_compiles():
    patched, provenance = fetch_and_patch_pinned_source()
    assert provenance["blob_sha"] == PINNED_BLOB_SHA
    counts = provenance["patch_counts"]
    assert counts["carrier_pools"] == 2
    assert all(v == 1 for k, v in counts.items() if k != "carrier_pools")
    assert "E042_Q_SUITE = 320" in patched
    assert "E042_SOURCE_COLUMN_CUBATURE = True" in patched
    assert "NO_CONFINE = True" in patched
    assert "final_means" not in patched
    assert "load_dataset(" not in patched
    compile(patched, "<e042_patched_v25>", "exec")
