from __future__ import annotations

import numpy as np

from methods.e031_source_axis_moment import (
    compute_floor,
    projection_loss_from_gram,
    source_basis,
)


def test_source_basis_is_deterministic_and_orthonormal() -> None:
    for k in range(1, 16):
        q1 = source_basis(k)
        q2 = source_basis(k)
        assert np.array_equal(q1, q2)
        assert q1.shape == (k, min(3, k))
        assert np.allclose(q1.T @ q1, np.eye(min(3, k)), atol=1e-12, rtol=0.0)


def test_degree_two_source_dependence_projects_exactly() -> None:
    k = 9
    x = np.linspace(-1.0, 1.0, k)
    coeff = np.arange(3 * 4, dtype=np.float64).reshape(3, 4) / 7.0
    direct = np.stack([coeff[0] + t * coeff[1] + t * t * coeff[2] for t in x])
    q = source_basis(k)
    recon = q @ (q.T @ direct)
    assert np.allclose(recon, direct, atol=1e-12, rtol=0.0)


def test_gram_loss_matches_direct_projection() -> None:
    rng = np.random.default_rng(314159)
    k = 7
    a = rng.normal(size=(k, 4, 3))
    p = rng.normal(size=(k, 4, 3))
    flat = np.concatenate([a.reshape(k, -1), p.reshape(k, -1)], axis=1)
    gram = flat @ flat.T
    q = source_basis(k)
    direct_resid = flat - q @ (q.T @ flat)
    direct = np.linalg.norm(direct_resid) / np.linalg.norm(flat)
    via_gram = projection_loss_from_gram(gram, q)
    assert abs(direct - via_gram) <= 1e-12


def test_frozen_compute_floor() -> None:
    out = compute_floor(proven_exact_saving_u=0.0)
    assert abs(out["zero_old_floor_u"] - 153.3) <= 1e-12
    assert abs(out["zero_old_floor_util"] - (153.3 / 1024.0)) <= 1e-15
    assert abs(out["required_additional_saving_u"] - 9.94) <= 1e-12
    assert out["projected_util"] > 0.14
