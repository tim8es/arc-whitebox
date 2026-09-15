from __future__ import annotations

import math

import numpy as np

from methods.e039_halfspace_gaussian_mixture import (
    component_relu_moments,
    frozen_initial_state,
    linear_covariance,
    run_halfspace_mixture,
    update_component_covariance,
)


def test_frozen_initial_state_reconstructs_standard_gaussian():
    m_plus, m_minus, cov, weights, direction = frozen_initial_state(np, 8)
    expected_direction = np.ones(8) / math.sqrt(8.0)
    np.testing.assert_allclose(direction, expected_direction, rtol=0.0, atol=0.0)
    np.testing.assert_array_equal(weights, np.asarray([0.5, 0.5]))
    weighted_mean = 0.5 * m_plus + 0.5 * m_minus
    assert float(np.max(np.abs(weighted_mean))) <= 1e-14
    reconstructed = cov + np.outer(m_plus, m_plus)
    assert float(np.max(np.abs(reconstructed - np.eye(8)))) <= 1e-12


def test_linear_shared_covariance_matches_explicit_product():
    w = np.asarray([[1.0, 0.2], [-0.5, 1.5], [0.3, -0.7]])
    cov = np.asarray([[1.2, 0.25], [0.25, 0.8]])
    got = linear_covariance(np, w, cov)
    np.testing.assert_allclose(got, w @ cov @ w.T, rtol=0.0, atol=1e-12)


def test_component_relu_moments_match_standard_normal_case():
    mean = np.asarray([0.0])
    var = np.asarray([1.0])
    post_mean, post_var, gain = component_relu_moments(np, mean, var)
    expected_mean = 1.0 / math.sqrt(2.0 * math.pi)
    expected_var = 0.5 - expected_mean**2
    np.testing.assert_allclose(post_mean, [expected_mean], rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(post_var, [expected_var], rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(gain, [0.5], rtol=0.0, atol=1e-12)


def test_component_covariance_diagonal_overwrite_is_exact():
    cov_pre = np.asarray([[1.2, 0.3], [0.3, 0.7]])
    gain = np.asarray([0.4, 0.8])
    var_post = np.asarray([0.25, 0.6])
    got = update_component_covariance(np, cov_pre, gain, var_post)
    np.testing.assert_allclose(np.diag(got), var_post, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(got[0, 1], gain[0] * gain[1] * cov_pre[0, 1], rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(got, got.T, rtol=0.0, atol=1e-12)


def test_synthetic_repeat_is_bit_identical_and_two_component():
    rng = np.random.default_rng(39039)
    weights = [rng.normal(size=(8, 8)) / math.sqrt(8.0) for _ in range(3)]
    out1, diag1 = run_halfspace_mixture(np, weights)
    out2, diag2 = run_halfspace_mixture(np, weights)
    np.testing.assert_array_equal(out1, out2)
    assert diag1 == diag2
    assert diag1["component_count"] == 2
    assert diag1["weights"] == [0.5, 0.5]
    assert np.isfinite(out1).all()
