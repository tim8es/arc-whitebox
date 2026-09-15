from __future__ import annotations

import numpy as np

from methods.e037_signed_k3_k4_response import (
    connected_k4_from_raw,
    covariance_update,
    cp_marginal3,
    cp_marginal4,
    leverage_birth3,
    leverage_birth4,
    linear_covariance,
    push_fifo,
    relu_k3_k4_moments,
    run_carrier,
)


def test_signed_cp_marginals_match_explicit_powers():
    atoms = np.asarray([[1.0, 2.0, -1.0, 0.5], [-2.0, 0.25, 1.5, -0.75]])
    signs = np.asarray([1.0, -1.0, 1.0, -1.0])
    np.testing.assert_allclose(cp_marginal3(np, atoms, signs), np.sum(signs * atoms**3, axis=1))
    np.testing.assert_allclose(cp_marginal4(np, atoms, signs), np.sum(signs * atoms**4, axis=1))


def test_leverage_births_and_zero_signs_are_frozen():
    w = np.asarray([[1.0, -2.0, 0.5], [0.25, 1.5, -3.0], [2.0, 0.5, 1.0]])
    k3 = np.asarray([0.0, -8.0, 1.0])
    atom3, sign3, idx3 = leverage_birth3(np, w, k3)
    scores3 = np.abs(k3) * np.sum(np.abs(w) ** 3, axis=0)
    assert idx3 == int(np.argmax(scores3))
    assert float(sign3) == (-1.0 if k3[idx3] < 0 else 1.0)
    np.testing.assert_allclose(atom3, w[:, idx3] * np.abs(k3[idx3]) ** (1.0 / 3.0))

    k4 = np.asarray([0.0, 16.0, -81.0])
    atom4, sign4, idx4 = leverage_birth4(np, w, k4)
    scores4 = np.abs(k4) * np.sum(np.abs(w) ** 4, axis=0)
    assert idx4 == int(np.argmax(scores4))
    assert float(sign4) == (-1.0 if k4[idx4] < 0 else 1.0)
    np.testing.assert_allclose(atom4, w[:, idx4] * np.abs(k4[idx4]) ** 0.25)

    _, zero_sign3, _ = leverage_birth3(np, np.eye(2), np.zeros(2))
    _, zero_sign4, _ = leverage_birth4(np, np.eye(2), np.zeros(2))
    assert float(zero_sign3) == 1.0
    assert float(zero_sign4) == 1.0


def test_fifo_is_exact_rank_four():
    atoms = np.arange(12.0).reshape(3, 4)
    signs = np.asarray([1.0, -1.0, 1.0, -1.0])
    out_a, out_s = push_fifo(np, atoms, signs, np.asarray([20.0, 21.0, 22.0]), -1.0)
    assert out_a.shape == (3, 4)
    assert out_s.shape == (4,)
    np.testing.assert_array_equal(out_a[:, :3], atoms[:, 1:])
    np.testing.assert_array_equal(out_a[:, 3], [20.0, 21.0, 22.0])
    np.testing.assert_array_equal(out_s, [-1.0, 1.0, -1.0, -1.0])


def test_covariance_and_connected_k4_algebra():
    w = np.asarray([[1.0, 2.0], [-0.5, 0.25]])
    c = np.asarray([[2.0, 0.3], [0.3, 1.5]])
    np.testing.assert_allclose(linear_covariance(np, w, c), w @ c @ w.T)

    m1 = np.asarray([1.0])
    m2 = np.asarray([5.0])
    m3 = np.asarray([13.0])
    m4 = np.asarray([49.0])
    centered4 = m4 - 4*m1*m3 + 6*m1*m1*m2 - 3*m1**4
    var = m2 - m1*m1
    expected = centered4 - 3*var*var
    np.testing.assert_allclose(connected_k4_from_raw(np, m1, m2, m3, m4), expected)


def test_gaussian_relu_and_covariance_diagonal():
    mu = np.asarray([0.0, 0.25])
    var = np.asarray([1.0, 0.5])
    zeros = np.zeros(2)
    m1, out_var, k3, k4, gain, _, _ = relu_k3_k4_moments(np, mu, var, zeros, zeros)
    assert np.isfinite(np.concatenate([m1, out_var, k3, k4, gain])).all()
    # The frozen 16-node rule crosses the ReLU kink; "near analytic" is a
    # quadrature sanity check, not an exactness claim.
    assert abs(m1[0] - 1.0 / np.sqrt(2.0*np.pi)) < 2e-2
    assert abs(out_var[0] - (0.5 - 1.0/(2.0*np.pi))) < 2e-2

    cov_pre = np.asarray([[1.0, 0.2], [0.2, 0.5]])
    cov_post = covariance_update(np, cov_pre, gain, out_var)
    np.testing.assert_allclose(cov_post, cov_post.T, rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(np.diag(cov_post), out_var, rtol=0.0, atol=1e-12)


def test_synthetic_carrier_is_bit_deterministic():
    rng = np.random.default_rng(37037)
    weights = [rng.normal(scale=0.2, size=(8, 8)) for _ in range(3)]
    a = run_carrier(np, weights)
    b = run_carrier(np, weights)
    np.testing.assert_array_equal(a[0], b[0])
    assert a[3] == b[3]
    assert a[4] == b[4]
    assert float(a[5]) <= 1e-12
