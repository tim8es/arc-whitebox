from __future__ import annotations

import math

import numpy as np

from methods.e109_late_gatepair_sign_cv import (
    build_late_prefix_directions_billed,
    build_two_haar_inputs_billed,
    crossfit_correct_billed,
    gatepair_features_billed,
    sign_pair_mean,
)


def test_sign_pair_mean_special_cases() -> None:
    assert sign_pair_mean(0.0) == 0.0
    assert abs(sign_pair_mean(1.0) - 1.0) <= 1e-15
    assert abs(sign_pair_mean(-1.0) + 1.0) <= 1e-15
    rho = 0.5
    assert abs(sign_pair_mean(rho) - (2.0 / math.pi) * math.asin(rho)) <= 1e-15


def test_late_prefix_directions_are_deterministic_and_unit() -> None:
    rng = np.random.default_rng(109001)
    n = 12
    weights = [
        (rng.standard_normal((n, n)) * math.sqrt(2.0 / n)).astype(np.float32)
        for _ in range(5)
    ]
    u1 = np.asarray(
        build_late_prefix_directions_billed(weights, layer=5, rows=8),
        dtype=np.float64,
    )
    u2 = np.asarray(
        build_late_prefix_directions_billed(weights, layer=5, rows=8),
        dtype=np.float64,
    )
    np.testing.assert_array_equal(u1, u2)
    np.testing.assert_allclose(np.linalg.norm(u1, axis=1), 1.0, atol=2e-6, rtol=0.0)


def test_gatepair_controls_are_even_under_antipodes() -> None:
    rng = np.random.default_rng(109002)
    q = rng.standard_normal((20, 10))
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    dirs = rng.standard_normal((8, 10))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)

    z1, means = gatepair_features_billed(q.astype(np.float32), dirs.astype(np.float32))
    z2, means2 = gatepair_features_billed((-q).astype(np.float32), dirs.astype(np.float32))

    np.testing.assert_array_equal(np.asarray(z1), np.asarray(z2))
    np.testing.assert_allclose(np.asarray(means), np.asarray(means2), atol=0.0, rtol=0.0)
    assert np.isfinite(np.asarray(z1)).all()
    assert np.isfinite(np.asarray(means)).all()


def test_crossfit_zero_controls_returns_baseline() -> None:
    rng = np.random.default_rng(109003)
    y1 = rng.normal(size=(16, 7)).astype(np.float32)
    y2 = rng.normal(size=(16, 7)).astype(np.float32)
    z1 = np.zeros((16, 4), dtype=np.float32)
    z2 = np.zeros((16, 4), dtype=np.float32)

    candidate, baseline, beta1, beta2 = crossfit_correct_billed(y1, y2, z1, z2)
    np.testing.assert_allclose(np.asarray(candidate), np.asarray(baseline), atol=1e-14, rtol=0.0)
    np.testing.assert_array_equal(np.asarray(beta1), np.zeros((4, 7)))
    np.testing.assert_array_equal(np.asarray(beta2), np.zeros((4, 7)))


def test_two_haar_inputs_deterministic_and_antithetic() -> None:
    x1 = np.asarray(build_two_haar_inputs_billed(8, 109004), dtype=np.float32)
    x2 = np.asarray(build_two_haar_inputs_billed(8, 109004), dtype=np.float32)
    np.testing.assert_array_equal(x1, x2)
    assert x1.shape == (32, 8)
    np.testing.assert_array_equal(x1[:16] + x1[16:], np.zeros((16, 8), dtype=np.float32))
