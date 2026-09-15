from __future__ import annotations

import types

import flopscope as flops
import numpy as np
from whestbench.domain import MLP

from methods.e043_terminal_adjoint_k3 import (
    PINNED_BLOB_SHA,
    PINNED_COMMIT,
    PINNED_PATH,
    fetch_and_patch_pinned_source,
    replay_source_dense,
    suffix_product,
)


def test_pinned_identity():
    assert PINNED_COMMIT == "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
    assert PINNED_PATH == "estimators/estimator_v25.py"
    assert PINNED_BLOB_SHA == "195373a110215256b759d7c172ba8c923c62e5cc"


def test_replay_dense_source_matches_sequential_forward_transport():
    rng = np.random.default_rng(43)
    n = 9
    a = rng.normal(size=(n, n))
    p = np.eye(n)
    z = rng.normal(size=(n, 5))
    zf = rng.normal(size=(n, 3))
    transports = [rng.normal(size=(n, n)) / np.sqrt(n) for _ in range(4)]

    ref_a, ref_p, ref_z, ref_zf = a.copy(), p.copy(), z.copy(), zf.copy()
    for t in transports:
        ref_a = t @ ref_a
        ref_p = t @ ref_p
        ref_z = t @ ref_z
        ref_zf = t @ ref_zf

    got = replay_source_dense(a, p, z, zf, transports)
    for actual, expected in zip(got, (ref_a, ref_p, ref_z, ref_zf)):
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_replay_matches_explicit_suffix_product():
    rng = np.random.default_rng(44)
    n = 7
    a = rng.normal(size=(n, n))
    p = np.eye(n)
    z = rng.normal(size=(n, 2))
    transports = [rng.normal(size=(n, n)) / np.sqrt(n) for _ in range(3)]
    s = suffix_product(transports, n=n)
    got_a, got_p, got_z, got_zf = replay_source_dense(a, p, z, None, transports)
    np.testing.assert_allclose(got_a, s @ a, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(got_p, s @ p, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(got_z, s @ z, rtol=1e-12, atol=1e-12)
    assert got_zf is None


def test_empty_suffix_is_identity():
    rng = np.random.default_rng(45)
    n = 6
    a = rng.normal(size=(n, n))
    p = rng.normal(size=(n, n))
    z = rng.normal(size=(n, 2))
    got = replay_source_dense(a, p, z, None, [])
    np.testing.assert_array_equal(got[0], a)
    np.testing.assert_array_equal(got[1], p)
    np.testing.assert_array_equal(got[2], z)
    assert got[3] is None
    np.testing.assert_array_equal(suffix_product([], n=n), np.eye(n))


def test_real_pinned_patch_targets_compile_and_freeze_terminal_only_contract():
    patched, provenance = fetch_and_patch_pinned_source()
    assert provenance["blob_sha"] == PINNED_BLOB_SHA
    assert all(v == 1 for v in provenance["patch_counts"].values())
    assert "E043_TERMINAL_ADJOINT_K3 = True" in patched
    assert "skip_src = not last  # E043" in patched
    assert "e043_births" in patched
    assert "e043_replayed_births" in patched
    assert "NO_CONFINE = True  # E043" in patched
    assert "E042" not in patched
    assert "load_dataset(" not in patched
    assert "final_means" not in patched
    compile(patched, "<e043_patched_v25>", "exec")


def test_patched_estimator_runs_without_public_data_and_replays_all_births_once():
    patched, _ = fetch_and_patch_pinned_source()
    module = types.ModuleType("e043_patched_v25_smoke")
    exec(compile(patched, "<e043_patched_v25_smoke>", "exec"), module.__dict__)

    n = 33
    depth = 4
    weights = [np.eye(n, dtype=np.float32) * np.float32(0.20) for _ in range(depth)]
    mlp = MLP(width=n, depth=depth, weights=weights, seed=4300, name="e043-smoke")
    mlp.validate()
    estimator = module.Estimator()

    with flops.BudgetContext(flop_budget=20_000_000_000, quiet=True) as budget:
        prediction = estimator.predict(mlp, 20_000_000_000)

    prediction_np = np.asarray(prediction)
    assert prediction_np.shape == (depth, n)
    assert np.isfinite(prediction_np).all()
    assert budget.flops_used > 0
    assert estimator._e043_stored_births == depth - 1
    assert estimator._e043_replayed_births == depth - 1
    assert estimator._e043_nonterminal_replays == 0
