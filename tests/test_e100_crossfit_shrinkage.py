from __future__ import annotations

import numpy as np

from methods.e100_crossfit_shrinkage import (
    antithetic_final_samples,
    canonical_top_subspace,
    covariance_state,
    crossfit_from_halves,
    generate_synthetic_mlp,
    group_stats,
    shrink_factor,
    split_antithetic_pairs,
)


def test_pair_split_preserves_adjacent_antithetic_pairs() -> None:
    rows = np.arange(16 * 3, dtype=np.float64).reshape(16, 3)
    a, b = split_antithetic_pairs(rows)
    expected_a = rows.reshape(8, 2, 3)[0::2].reshape(-1, 3)
    expected_b = rows.reshape(8, 2, 3)[1::2].reshape(-1, 3)
    np.testing.assert_array_equal(a, expected_a)
    np.testing.assert_array_equal(b, expected_b)


def test_synthetic_state_and_sample_stream_are_deterministic() -> None:
    w1 = generate_synthetic_mlp(seed=100, width=10, depth=3)
    w2 = generate_synthetic_mlp(seed=100, width=10, depth=3)
    assert all(np.array_equal(a, b) for a, b in zip(w1, w2, strict=True))

    means1, cov1 = covariance_state(w1)
    means2, cov2 = covariance_state(w1)
    np.testing.assert_array_equal(means1, means2)
    np.testing.assert_array_equal(cov1, cov2)
    assert np.isfinite(means1).all()
    assert np.isfinite(cov1).all()

    s1 = antithetic_final_samples(w1, input_seed=1001, samples=256)
    s2 = antithetic_final_samples(w1, input_seed=1001, samples=256)
    np.testing.assert_array_equal(s1, s2)
    assert s1.shape == (256, 10)
    assert np.isfinite(s1).all()


def test_top_subspace_is_canonical_orthonormal() -> None:
    rng = np.random.default_rng(1002)
    q, _ = np.linalg.qr(rng.normal(size=(9, 9)))
    cov = q @ np.diag(np.linspace(9.0, 1.0, 9)) @ q.T
    u = canonical_top_subspace(cov, rank=3)
    np.testing.assert_allclose(u.T @ u, np.eye(3), atol=1e-12, rtol=0.0)
    for j in range(3):
        pivot = int(np.argmax(np.abs(u[:, j])))
        assert u[pivot, j] >= 0.0


def test_shrink_factor_positive_part_rule() -> None:
    assert shrink_factor(noise_energy=0.0, residual_energy=4.0) == 1.0
    assert shrink_factor(noise_energy=1.0, residual_energy=4.0) == 0.75
    assert shrink_factor(noise_energy=4.0, residual_energy=4.0) == 0.0
    assert shrink_factor(noise_energy=8.0, residual_energy=4.0) == 0.0


def test_group_stats_decompose_noise_and_return_bounded_coefficients() -> None:
    rng = np.random.default_rng(1003)
    samples = rng.normal(size=(64, 7))
    base = rng.normal(size=7)
    q, _ = np.linalg.qr(rng.normal(size=(7, 7)))
    u = q[:, :2]

    stats = group_stats(samples, base, u)
    assert 0.0 <= stats["a_p"] <= 1.0
    assert 0.0 <= stats["a_q"] <= 1.0
    np.testing.assert_allclose(
        stats["tau_p"] + stats["tau_q"],
        stats["tau_total"],
        atol=1e-12,
        rtol=0.0,
    )
    np.testing.assert_allclose(
        stats["e_p"] + stats["e_q"],
        float(np.dot(stats["residual"], stats["residual"])),
        atol=1e-12,
        rtol=0.0,
    )


def test_crossfit_identity_limits() -> None:
    rng = np.random.default_rng(1004)
    base = rng.normal(size=8)
    ma = rng.normal(size=8)
    mb = rng.normal(size=8)
    q, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    u = q[:, :3]

    full = crossfit_from_halves(base, ma, mb, u, (1.0, 1.0), (1.0, 1.0))
    np.testing.assert_allclose(full, 0.5 * (ma + mb), atol=1e-14, rtol=0.0)

    zero = crossfit_from_halves(base, ma, mb, u, (0.0, 0.0), (0.0, 0.0))
    np.testing.assert_allclose(zero, base, atol=1e-14, rtol=0.0)
