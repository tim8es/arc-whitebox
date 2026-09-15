import numpy as np
import pytest

from experiments.e022_oversampled_basis import (
    fixed_oversampled_basis,
    principal_subspace_error,
)


def _orthonormal(a: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(a)
    return q


def test_fixed_oversampled_basis_uses_one_apply_g_and_returns_rank_r_basis():
    rng = np.random.default_rng(22022)
    n, rank, ell = 32, 8, 12
    u = _orthonormal(rng.standard_normal((n, n)))
    spectrum = np.geomspace(10.0, 1e-3, n)
    g = (u * spectrum) @ u.T
    omega = rng.standard_normal((n, ell))
    calls = 0

    def apply_g(x: np.ndarray) -> np.ndarray:
        nonlocal calls
        calls += 1
        return g @ x

    q = fixed_oversampled_basis(apply_g, omega, rank=rank, ell=ell)

    assert calls == 1
    assert q.shape == (n, rank)
    np.testing.assert_allclose(q.T @ q, np.eye(rank), atol=1e-10, rtol=1e-10)


def test_fixed_oversampled_basis_matches_manual_yty_top_rank_construction():
    rng = np.random.default_rng(17)
    n, rank, ell = 24, 6, 10
    a = rng.standard_normal((n, n))
    g = a @ a.T
    omega = rng.standard_normal((n, ell))
    y = g @ omega

    q = fixed_oversampled_basis(lambda x: g @ x, omega, rank=rank, ell=ell)

    h = y.T @ y
    evals, evecs = np.linalg.eigh(h)
    idx = np.argsort(evals)[-rank:][::-1]
    lam = evals[idx]
    v = evecs[:, idx]
    q_manual = y @ (v / np.sqrt(lam))

    assert principal_subspace_error(q, q_manual) <= 1e-10


def test_fixed_oversampled_basis_rejects_invalid_frozen_shapes():
    omega = np.ones((16, 10))
    with pytest.raises(ValueError):
        fixed_oversampled_basis(lambda x: x, omega, rank=12, ell=10)
    with pytest.raises(ValueError):
        fixed_oversampled_basis(lambda x: x, omega, rank=8, ell=11)


def test_principal_subspace_error_is_zero_for_rotated_same_subspace():
    rng = np.random.default_rng(4)
    q = _orthonormal(rng.standard_normal((20, 5)))
    r = _orthonormal(rng.standard_normal((5, 5)))
    assert principal_subspace_error(q, q @ r) <= 1e-12
