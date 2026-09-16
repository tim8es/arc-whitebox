from __future__ import annotations

import numpy as np

from methods.e095_output_subspace_sampling import (
    antithetic_final_mean,
    canonical_top_subspace,
    covariance_state,
    generate_synthetic_mlp,
    project_residual,
)


def test_synthetic_mlp_and_covariance_state_are_deterministic_finite() -> None:
    weights_a = generate_synthetic_mlp(seed=95, width=12, depth=4)
    weights_b = generate_synthetic_mlp(seed=95, width=12, depth=4)
    assert all(np.array_equal(a, b) for a, b in zip(weights_a, weights_b, strict=True))

    means_a, cov_a = covariance_state(weights_a)
    means_b, cov_b = covariance_state(weights_a)
    assert means_a.shape == (4, 12)
    assert cov_a.shape == (12, 12)
    assert np.array_equal(means_a, means_b)
    assert np.array_equal(cov_a, cov_b)
    assert np.all(np.isfinite(means_a))
    assert np.all(np.isfinite(cov_a))
    assert np.max(np.abs(cov_a - cov_a.T)) <= 1e-14


def test_top_subspace_is_orthonormal_and_sign_canonical() -> None:
    rng = np.random.default_rng(9501)
    q, _ = np.linalg.qr(rng.normal(size=(10, 10)))
    eig = np.linspace(10.0, 1.0, 10)
    cov = q @ np.diag(eig) @ q.T

    u1 = canonical_top_subspace(cov, rank=6)
    u2 = canonical_top_subspace(cov, rank=6)

    assert u1.shape == (10, 6)
    assert np.array_equal(u1, u2)
    assert np.allclose(u1.T @ u1, np.eye(6), atol=1e-12, rtol=0.0)
    for column in range(u1.shape[1]):
        vector = u1[:, column]
        pivot = int(np.argmax(np.abs(vector)))
        assert vector[pivot] >= 0.0


def test_projected_residual_matches_explicit_projector() -> None:
    rng = np.random.default_rng(9502)
    q, _ = np.linalg.qr(rng.normal(size=(9, 9)))
    u = q[:, :3]
    base = rng.normal(size=9)
    sample = rng.normal(size=9)

    actual = project_residual(base, sample, u)
    expected = base + (u @ u.T) @ (sample - base)
    assert np.allclose(actual, expected, atol=1e-14, rtol=0.0)


def test_antithetic_final_mean_is_deterministic() -> None:
    weights = generate_synthetic_mlp(seed=9510, width=10, depth=3)
    first = antithetic_final_mean(weights, input_seed=12345, samples=2048)
    second = antithetic_final_mean(weights, input_seed=12345, samples=2048)

    assert first.shape == (10,)
    assert np.array_equal(first, second)
    assert np.all(np.isfinite(first))
