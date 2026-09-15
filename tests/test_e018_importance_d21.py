import numpy as np

from methods.e018_importance_d21 import (
    SAMPLE_COUNT,
    importance_sampled_sum,
    norm_optimal_probabilities,
    seed_for,
)


def test_frozen_sample_count_and_seed_rule() -> None:
    assert SAMPLE_COUNT == 384
    assert seed_for(4, 8, 0) == 22274
    assert seed_for(7, 14, 3) == 25469


def test_norm_optimal_probabilities_follow_stacked_ap_aa_pp_energy() -> None:
    ap = np.array([[3.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    aa = np.array([[0.0, 4.0, 0.0], [0.0, 0.0, 0.0]])
    pp = np.array([[0.0, 0.0, 12.0], [0.0, 0.0, 0.0]])
    p = norm_optimal_probabilities(ap, aa, pp)
    np.testing.assert_allclose(p, np.array([3.0, 4.0, 12.0]) / 19.0)
    assert np.isclose(p.sum(), 1.0)


def test_zero_energy_distribution_is_uniform_without_clipping() -> None:
    z = np.zeros((2, 4), dtype=np.float64)
    p = norm_optimal_probabilities(z, z, z)
    np.testing.assert_allclose(p, np.full(4, 0.25))


def test_importance_sampled_sum_is_deterministic_for_frozen_seed() -> None:
    terms = np.arange(30, dtype=np.float64).reshape(5, 2, 3)
    p = np.array([0.1, 0.2, 0.25, 0.15, 0.3], dtype=np.float64)
    a = importance_sampled_sum(terms, p, sample_count=384, seed=12345)
    b = importance_sampled_sum(terms, p, sample_count=384, seed=12345)
    np.testing.assert_array_equal(a, b)


def test_importance_sampled_sum_matches_manual_with_replacement_reweighting() -> None:
    terms = np.array([[1.0], [3.0], [7.0]], dtype=np.float64)
    p = np.array([0.2, 0.3, 0.5], dtype=np.float64)
    seed = 77
    sample_count = 8
    rng = np.random.default_rng(seed)
    idx = rng.choice(3, size=sample_count, replace=True, p=p)
    expected = np.mean(terms[idx] / p[idx, None], axis=0)
    actual = importance_sampled_sum(
        terms, p, sample_count=sample_count, seed=seed
    )
    np.testing.assert_allclose(actual, expected)
