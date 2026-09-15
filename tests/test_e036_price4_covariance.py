import math

import numpy as np

from methods.e036_price4_covariance import (
    covariance_update_price4,
    cp_marginal,
    leverage_birth,
    linear_covariance,
    price4_offdiag,
    price_coefficients,
    push_fifo,
    relu_k3_moments,
    run_carrier,
)


def test_price_coefficients_match_frozen_analytic_values():
    mu = np.asarray([0.0, 1.0], dtype=np.float64)
    var = np.asarray([1.0, 4.0], dtype=np.float64)
    p, q, r, s = price_coefficients(np, mu, var)
    sigma = np.sqrt(var)
    a = mu / sigma
    phi = np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)
    expected_p = np.asarray([0.5, 0.5 * (1.0 + math.erf(0.5 / math.sqrt(2.0)))])
    assert np.allclose(p, expected_p, rtol=0.0, atol=1e-14)
    assert np.allclose(q, phi / sigma, rtol=0.0, atol=1e-14)
    assert np.allclose(r, -a * phi / (sigma * sigma), rtol=0.0, atol=1e-14)
    assert np.allclose(s, (a * a - 1.0) * phi / (sigma**3), rtol=0.0, atol=1e-14)


def test_price4_polynomial_matches_explicit_outer_sum():
    c = np.asarray([[1.0, 0.2], [0.2, 2.0]], dtype=np.float64)
    p = np.asarray([0.4, 0.6])
    q = np.asarray([0.2, 0.3])
    r = np.asarray([-0.1, 0.05])
    s = np.asarray([0.02, -0.04])
    got = price4_offdiag(np, c, p, q, r, s)
    expected = (
        c * np.outer(p, p)
        + 0.5 * c**2 * np.outer(q, q)
        + (c**3 / 6.0) * np.outer(r, r)
        + (c**4 / 24.0) * np.outer(s, s)
    )
    assert np.allclose(got, expected, rtol=0.0, atol=0.0)


def test_covariance_update_is_symmetric_and_sets_diagonal():
    c = np.asarray([[1.0, 0.25], [0.25, 2.0]], dtype=np.float64)
    var_post = np.asarray([0.3, 0.7])
    p = np.asarray([0.5, 0.6])
    q = np.asarray([0.3, 0.2])
    r = np.asarray([0.1, -0.1])
    s = np.asarray([0.02, 0.03])
    got = covariance_update_price4(np, c, p, q, r, s, var_post)
    assert np.allclose(got, got.T, rtol=0.0, atol=1e-15)
    assert np.allclose(np.diag(got), var_post, rtol=0.0, atol=1e-15)


def test_linear_covariance_matches_explicit_product():
    w = np.asarray([[1.0, 0.2], [-0.5, 1.5], [0.3, -0.7]])
    cov = np.asarray([[1.2, 0.25], [0.25, 0.8]])
    assert np.allclose(linear_covariance(np, w, cov), w @ cov @ w.T)


def test_signed_k3_birth_fifo_invariants():
    atoms = np.asarray([[1.0, 2.0, -1.0, 0.5], [2.0, -1.0, 3.0, 1.5]])
    signs = np.asarray([1.0, -1.0, 1.0, -1.0])
    assert np.allclose(cp_marginal(np, atoms, signs), np.sum(atoms**3 * signs[None, :], axis=1))

    w = np.asarray([[1.0, 0.2, 3.0], [0.5, 0.1, -2.0]])
    k3 = np.asarray([0.25, -4.0, 0.125])
    atom, sign, idx = leverage_birth(np, w, k3)
    scores = np.abs(k3) * np.sum(np.abs(w) ** 3, axis=0)
    assert idx == int(np.argmax(scores))
    assert sign == np.sign(k3[idx])
    out_a, out_s = push_fifo(np, np.zeros((2, 4)), np.ones(4), atom, sign)
    assert out_a.shape == (2, 4) and out_s.shape == (4,)
    atom0, sign0, idx0 = leverage_birth(np, np.eye(3), np.zeros(3))
    assert idx0 == 0 and sign0 == 1.0 and np.allclose(atom0, 0.0)


def test_gaussian_zero_skew_marginal_relu_is_finite():
    mu = np.asarray([0.0])
    var = np.asarray([1.0])
    m, v, c3, _, max_skew = relu_k3_moments(np, mu, var, np.zeros(1))
    expected_m = 1.0 / math.sqrt(2.0 * math.pi)
    expected_v = 0.5 - expected_m**2
    assert np.isfinite(m[0]) and np.isfinite(v[0]) and np.isfinite(c3[0])
    assert abs(m[0] - expected_m) < 0.03
    assert abs(v[0] - expected_v) < 0.03
    assert max_skew == 0.0


def test_synthetic_carrier_repeat_is_exact():
    rng = np.random.default_rng(19)
    weights = [rng.normal(size=(5, 5)).astype(np.float64) / np.sqrt(5.0) for _ in range(3)]
    out1, skew1, idx1, diag1 = run_carrier(np, weights)
    out2, skew2, idx2, diag2 = run_carrier(np, weights)
    assert np.array_equal(out1, out2)
    assert float(skew1) == float(skew2)
    assert idx1 == idx2
    assert float(diag1) == float(diag2)
