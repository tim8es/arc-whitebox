import numpy as np

from methods.e033_diagonal_edgeworth import (
    GH_WEIGHTS,
    GH_Z,
    linear_transport,
    relu_edgeworth_moments,
)


def test_embedded_normal_rule_moments():
    z = np.asarray(GH_Z, dtype=np.float64)
    w = np.asarray(GH_WEIGHTS, dtype=np.float64)
    assert z.shape == (16,)
    assert w.shape == (16,)
    assert abs(np.sum(w) - 1.0) < 1e-14
    assert abs(np.sum(w * z)) < 1e-14
    assert abs(np.sum(w * z * z) - 1.0) < 1e-13


def test_linear_cumulant_transport_matches_independence_formula():
    W = np.asarray([[1.0, -2.0], [0.5, 3.0]], dtype=np.float64)
    mu = np.asarray([0.2, -0.4])
    var = np.asarray([1.5, 0.7])
    k3 = np.asarray([0.3, -0.2])
    k4 = np.asarray([0.5, 0.1])
    got = linear_transport(np, W, mu, var, k3, k4)
    assert np.allclose(got[0], W @ mu)
    assert np.allclose(got[1], (W**2) @ var)
    assert np.allclose(got[2], (W**3) @ k3)
    assert np.allclose(got[3], (W**4) @ k4)


def test_gaussian_edgeworth_relu_update_is_finite_positive():
    mu = np.asarray([0.0, 0.3, -0.2])
    var = np.asarray([1.0, 0.7, 1.4])
    zeros = np.zeros_like(mu)
    out = relu_edgeworth_moments(np, mu, var, zeros, zeros)
    m, v, k3, k4, max_skew, max_kurt = out
    assert np.all(np.isfinite(m))
    assert np.all(np.isfinite(v))
    assert np.all(np.isfinite(k3))
    assert np.all(np.isfinite(k4))
    assert np.all(v >= 0.0)
    assert np.all(m >= 0.0)
    assert max_skew == 0.0
    assert max_kurt == 0.0


def test_edgeworth_update_is_deterministic():
    mu = np.asarray([0.1, -0.25])
    var = np.asarray([0.8, 1.2])
    k3 = np.asarray([0.05, -0.08])
    k4 = np.asarray([0.02, 0.04])
    a = relu_edgeworth_moments(np, mu, var, k3, k4)
    b = relu_edgeworth_moments(np, mu, var, k3, k4)
    for x, y in zip(a[:4], b[:4]):
        assert np.max(np.abs(x - y)) == 0.0
