import math

import numpy as np

from methods.e035_covariance_signed_k3 import (
    covariance_update,
    cp_marginal,
    leverage_birth,
    linear_covariance,
    push_fifo,
    relu_k3_moments,
    run_carrier,
)


def test_linear_covariance_matches_explicit_product():
    w = np.asarray([[1.0, 0.2], [-0.5, 1.5], [0.3, -0.7]])
    cov = np.asarray([[1.2, 0.25], [0.25, 0.8]])
    got = linear_covariance(np, w, cov)
    expected = w @ cov @ w.T
    assert np.allclose(got, expected)


def test_cp_marginal_matches_signed_cubes():
    atoms = np.asarray([[1.0, 2.0, -1.0, 0.5], [2.0, -1.0, 3.0, 1.5]])
    signs = np.asarray([1.0, -1.0, 1.0, -1.0])
    assert np.allclose(
        cp_marginal(np, atoms, signs),
        np.sum(atoms**3 * signs[None, :], axis=1),
    )


def test_leverage_birth_and_zero_sign_are_frozen():
    w = np.asarray([[1.0, 0.2, 3.0], [0.5, 0.1, -2.0]])
    k3 = np.asarray([0.25, -4.0, 0.125])
    atom, sign, idx = leverage_birth(np, w, k3)
    scores = np.abs(k3) * np.sum(np.abs(w) ** 3, axis=0)
    assert idx == int(np.argmax(scores))
    assert sign == np.sign(k3[idx])
    assert np.allclose(atom, abs(k3[idx]) ** (1.0 / 3.0) * w[:, idx])

    atom0, sign0, idx0 = leverage_birth(np, np.eye(3), np.zeros(3))
    assert idx0 == 0
    assert sign0 == 1.0
    assert np.allclose(atom0, 0.0)


def test_fifo_keeps_exactly_four_slots():
    atoms = np.zeros((3, 4))
    signs = np.ones(4)
    out_a, out_s = push_fifo(np, atoms, signs, np.asarray([1.0, 2.0, 3.0]), -1.0)
    assert out_a.shape == (3, 4)
    assert out_s.shape == (4,)
    assert np.allclose(out_a[:, -1], [1.0, 2.0, 3.0])
    assert out_s[-1] == -1.0


def test_gaussian_marginal_relu_rule_is_reasonable_and_finite():
    mu = np.asarray([0.0])
    var = np.asarray([1.0])
    k3 = np.asarray([0.0])
    m, v, c3, gain, max_skew = relu_k3_moments(np, mu, var, k3)
    expected_m = 1.0 / math.sqrt(2.0 * math.pi)
    expected_v = 0.5 - expected_m**2
    assert np.isfinite(m[0]) and np.isfinite(v[0]) and np.isfinite(c3[0])
    assert abs(m[0] - expected_m) < 0.03
    assert abs(v[0] - expected_v) < 0.03
    assert abs(gain[0] - 0.5) < 1e-12
    assert max_skew == 0.0


def test_covariance_update_overwrites_diagonal_exactly():
    cov_pre = np.asarray([[1.2, 0.3], [0.3, 0.7]])
    gain = np.asarray([0.4, 0.8])
    var_post = np.asarray([0.25, 0.6])
    got = covariance_update(np, cov_pre, gain, var_post)
    assert np.allclose(np.diag(got), var_post)
    assert np.allclose(got[0, 1], gain[0] * gain[1] * cov_pre[0, 1])
    assert np.allclose(got, got.T)


def test_synthetic_repeat_is_deterministic():
    rng = np.random.default_rng(11)
    weights = [rng.normal(size=(5, 5)).astype(np.float64) / np.sqrt(5.0) for _ in range(3)]
    out1, skew1, idx1, diag1 = run_carrier(np, weights)
    out2, skew2, idx2, diag2 = run_carrier(np, weights)
    assert np.array_equal(out1, out2)
    assert float(skew1) == float(skew2)
    assert idx1 == idx2
    assert float(diag1) == float(diag2)
