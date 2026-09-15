from __future__ import annotations

import math

import numpy as np

from methods.e038_conditional_gaussian_cov import (
    GH_WEIGHTS,
    GH_Z,
    conditional_second_moment,
    gaussian_relu_moments,
    linear_covariance,
    run_carrier,
)


def test_gaussian_relu_zero_mean_moments_are_exact():
    mu = np.array([0.0, 0.0])
    var = np.array([1.0, 4.0])
    mean, out_var = gaussian_relu_moments(np, mu, var)
    expected_mean = np.array([1.0, 2.0]) / math.sqrt(2.0 * math.pi)
    expected_var = var * (0.5 - 1.0 / (2.0 * math.pi))
    np.testing.assert_allclose(mean, expected_mean, rtol=0.0, atol=1e-14)
    np.testing.assert_allclose(out_var, expected_var, rtol=0.0, atol=1e-14)


def test_zero_correlation_pair_factorizes():
    mu = np.array([0.25, -0.4, 0.8])
    var = np.array([1.2, 0.7, 1.5])
    cov = np.diag(var)
    mean, out_var = gaussian_relu_moments(np, mu, var)
    second, max_corr = conditional_second_moment(np, mu, cov)
    expected = np.outer(mean, mean)
    np.fill_diagonal(expected, out_var + mean * mean)
    np.testing.assert_allclose(second, expected, rtol=0.0, atol=2e-10)
    assert abs(float(max_corr) - 1.0) <= 1e-12


def test_pair_update_is_symmetric_with_exact_diagonal():
    mu = np.array([0.1, -0.2, 0.3])
    cov = np.array(
        [[1.0, 0.35, -0.1], [0.35, 0.8, 0.22], [-0.1, 0.22, 1.4]],
        dtype=float,
    )
    mean, out_var = gaussian_relu_moments(np, mu, np.diag(cov))
    second, _ = conditional_second_moment(np, mu, cov)
    out_cov = second - np.outer(mean, mean)
    np.fill_diagonal(out_cov, out_var)
    np.testing.assert_allclose(out_cov, out_cov.T, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(np.diag(out_cov), out_var, rtol=0.0, atol=1e-12)


def test_linear_covariance_is_exact():
    w = np.array([[1.0, 2.0], [-0.5, 0.25]])
    cov = np.array([[1.2, 0.3], [0.3, 0.7]])
    got = linear_covariance(np, w, cov)
    np.testing.assert_allclose(got, (w @ cov) @ w.T, rtol=0.0, atol=0.0)


def test_frozen_nodes_and_synthetic_network_are_deterministic_and_finite():
    assert len(GH_Z) == len(GH_WEIGHTS) == 16
    assert abs(sum(GH_WEIGHTS) - 1.0) < 1e-14
    rng = np.random.default_rng(38038)
    weights = [rng.normal(scale=0.22, size=(5, 5)) for _ in range(3)]
    out1, diag1, corr1 = run_carrier(np, weights)
    out2, diag2, corr2 = run_carrier(np, weights)
    np.testing.assert_array_equal(out1, out2)
    assert diag1 == diag2
    assert corr1 == corr2
    assert np.isfinite(out1).all()
    assert diag1 <= 1e-12
