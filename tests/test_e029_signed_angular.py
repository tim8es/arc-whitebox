from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e029_signed_angular import (
    build_support,
    fit_first_layer_weights,
    fit_first_layer_weights_from_preactivation,
    gaussian_radius_mean,
)


def _well_conditioned_w(n: int) -> np.ndarray:
    w = np.eye(n, dtype=np.float64)
    w += 0.15 * np.roll(np.eye(n, dtype=np.float64), 1, axis=1)
    return w


def test_support_is_exactly_three_unit_norm_blocks() -> None:
    n = 8
    w0 = _well_conditioned_w(n)
    u = build_support(np, w0)
    assert u.shape == (3 * n, n)
    np.testing.assert_allclose(u[:n], np.eye(n), rtol=0.0, atol=0.0)
    np.testing.assert_allclose(np.linalg.norm(u, axis=1), 1.0, rtol=1e-12, atol=1e-12)


def test_signed_projection_matches_all_first_layer_means_and_normalization() -> None:
    n = 8
    w0 = _well_conditioned_w(n)
    u = build_support(np, w0)
    radius = gaussian_radius_mean(n)
    weights, target, achieved = fit_first_layer_weights(np, w0, u, radius)
    assert weights.shape == (3 * n,)
    np.testing.assert_allclose(np.sum(weights), 1.0, rtol=0.0, atol=2e-10)
    np.testing.assert_allclose(achieved, target, rtol=2e-10, atol=2e-10)


def test_preactivation_reuse_matches_direct_fit() -> None:
    n = 8
    w0 = _well_conditioned_w(n)
    u = build_support(np, w0)
    z = u @ w0.T
    radius = gaussian_radius_mean(n)
    direct = fit_first_layer_weights(np, w0, u, radius)
    reused = fit_first_layer_weights_from_preactivation(np, w0, z, radius)
    for a, b in zip(direct, reused):
        np.testing.assert_allclose(a, b, rtol=2e-12, atol=2e-12)


def test_flopscope_solve_path_runs_without_fallback() -> None:
    n = 4
    w0_np = _well_conditioned_w(n).astype(np.float32)
    with flops.BudgetContext(flop_budget=10_000_000, wall_time_limit_s=30.0, quiet=True):
        w0 = fnp.asarray(w0_np)
        u = build_support(fnp, w0)
        z = u @ w0.T
        weights, target, achieved = fit_first_layer_weights_from_preactivation(
            fnp, w0, z, gaussian_radius_mean(n)
        )
    np.testing.assert_allclose(np.asarray(achieved), np.asarray(target), rtol=1e-5, atol=1e-7)
    np.testing.assert_allclose(float(np.asarray(weights).sum()), 1.0, rtol=0.0, atol=1e-6)


def test_gaussian_radius_mean_matches_gamma_ratio() -> None:
    for n in (4, 8, 32, 1024):
        exact = math.sqrt(2.0) * math.exp(math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0))
        assert abs(gaussian_radius_mean(n) - exact) <= 1e-13 * exact
