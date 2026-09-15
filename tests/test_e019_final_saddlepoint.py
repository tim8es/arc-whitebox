import numpy as np

from methods.e019_final_saddlepoint import (
    GL_NODES,
    GL_WEIGHTS,
    NEWTON_ITERS,
    gaussian_relu_mean,
    saddlepoint_relu_mean,
)


def test_frozen_quadrature_and_newton_contract():
    assert NEWTON_ITERS == 6
    assert GL_NODES.shape == (32,)
    assert GL_WEIGHTS.shape == (32,)
    np.testing.assert_allclose(GL_NODES, -GL_NODES[::-1], rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(GL_WEIGHTS, GL_WEIGHTS[::-1], rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(np.sum(GL_WEIGHTS), 16.0, rtol=0.0, atol=1e-13)
    assert np.all(GL_NODES > -8.0)
    assert np.all(GL_NODES < 8.0)


def test_gaussian_limit_matches_analytic_relu_mean():
    mu = np.asarray([-3.0, -1.0, 0.0, 0.25, 1.5, 3.0], dtype=np.float64)
    var = np.asarray([0.25, 1.0, 4.0, 0.5, 2.0, 9.0], dtype=np.float64)
    zero = np.zeros_like(mu)

    result = saddlepoint_relu_mean(mu, var, zero, zero)
    expected = gaussian_relu_mean(mu, var)

    np.testing.assert_allclose(result.mean, expected, rtol=0.0, atol=1e-12)
    assert result.min_kpp == 1.0
    assert result.max_normalized_residual <= 1e-15
    assert result.finite_positive_kpp


def test_mild_non_gaussian_case_is_deterministic_finite_and_converged():
    mu = np.asarray([-0.4, 0.0, 0.8, 1.2], dtype=np.float64)
    var = np.asarray([0.8, 1.0, 1.5, 2.0], dtype=np.float64)
    k3 = np.asarray([0.01, -0.02, 0.03, -0.015], dtype=np.float64)
    k4 = np.asarray([0.005, 0.01, -0.004, 0.008], dtype=np.float64)

    first = saddlepoint_relu_mean(mu, var, k3, k4)
    second = saddlepoint_relu_mean(mu, var, k3, k4)

    np.testing.assert_array_equal(first.mean, second.mean)
    assert np.all(np.isfinite(first.mean))
    assert first.finite_positive_kpp
    assert first.min_kpp > 0.0
    assert first.max_normalized_residual <= 1e-5
