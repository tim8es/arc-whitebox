import numpy as np

from methods.e034_signed_k3_response import (
    cp_marginal,
    leverage_birth,
    push_fifo,
    relu_k3_moments,
)


def test_cp_marginal_matches_signed_cubes():
    a = np.asarray([[1.0, 2.0, -1.0, 0.5], [2.0, -1.0, 3.0, 1.5]])
    s = np.asarray([1.0, -1.0, 1.0, -1.0])
    got = cp_marginal(np, a, s)
    expected = np.sum((a**3) * s[None, :], axis=1)
    assert np.allclose(got, expected)


def test_transport_directional_marginal_identity():
    w = np.asarray([[1.0, 2.0], [-0.5, 1.0]])
    a = np.asarray([[0.2, -0.4, 0.5, 0.1], [0.7, 0.3, -0.2, 0.6]])
    s = np.asarray([1.0, -1.0, -1.0, 1.0])
    transported = w @ a
    assert np.allclose(cp_marginal(np, transported, s), np.sum(s * transported**3, axis=1))


def test_leverage_birth_is_fixed_argmax():
    w = np.asarray([[1.0, 0.2, 3.0], [0.5, 0.1, -2.0]])
    k3 = np.asarray([0.25, -4.0, 0.125])
    atom, sign, idx = leverage_birth(np, w, k3)
    scores = np.abs(k3) * np.sum(np.abs(w) ** 3, axis=0)
    assert idx == int(np.argmax(scores))
    scale = abs(k3[idx]) ** (1.0 / 3.0)
    assert np.allclose(atom, scale * w[:, idx])
    assert sign == np.sign(k3[idx])


def test_fifo_keeps_four_slots():
    a = np.zeros((3, 4))
    s = np.ones(4)
    atom = np.asarray([1.0, 2.0, 3.0])
    out_a, out_s = push_fifo(np, a, s, atom, -1.0)
    assert out_a.shape == (3, 4)
    assert out_s.shape == (4,)
    assert np.allclose(out_a[:, -1], atom)
    assert out_s[-1] == -1.0


def test_gaussian_relu_update_is_finite():
    mu = np.asarray([0.0, 0.2, -0.3])
    var = np.asarray([1.0, 0.8, 1.2])
    k3 = np.zeros(3)
    m, v, c3, p, max_skew = relu_k3_moments(np, mu, var, k3)
    assert np.all(np.isfinite(m))
    assert np.all(np.isfinite(v))
    assert np.all(np.isfinite(c3))
    assert np.all(np.isfinite(p))
    assert np.all(v >= 0.0)
    assert max_skew == 0.0
