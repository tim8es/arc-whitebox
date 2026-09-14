import numpy as np

from methods.e016_rank1_k4 import apply_rank1_mode, build_q, fit_gamma


def _offdiag_outer(q):
    out = np.outer(q, q)
    np.fill_diagonal(out, 0.0)
    return out


def test_fit_gamma_recovers_shared_layer_scalar():
    rng = np.random.default_rng(20260915)
    n = 16
    lam = 0.007
    gamma_true = 0.35
    samples = []
    for _ in range(4):
        var = rng.uniform(0.5, 1.5, size=n)
        dg = 0.02 * var + rng.normal(0.0, 0.03, size=n)
        c = rng.normal(size=(n, n))
        c = 0.5 * (c + c.T)
        np.fill_diagonal(c, 0.0)
        q = build_q(dg, var)
        teacher = lam * c + gamma_true * _offdiag_outer(q)
        samples.append((teacher, c, dg, var, lam))

    gamma = fit_gamma(samples)
    assert abs(gamma - gamma_true) < 1e-10


def test_apply_mode_preserves_diagonal_and_is_deterministic():
    var = np.array([0.7, 1.0, 1.3, 0.9], dtype=np.float64)
    dg = np.array([0.03, 0.00, 0.08, -0.01], dtype=np.float64)
    c = np.arange(16, dtype=np.float64).reshape(4, 4)
    c = 0.5 * (c + c.T)
    np.fill_diagonal(c, 0.0)

    a = apply_rank1_mode(c, dg, var, lam=0.01, gamma=0.2)
    b = apply_rank1_mode(c, dg, var, lam=0.01, gamma=0.2)
    assert np.array_equal(a, b)
    assert np.count_nonzero(np.diag(a)) == 0
    assert np.all(np.isfinite(a))
