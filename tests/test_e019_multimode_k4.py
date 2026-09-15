import numpy as np

from methods.e019_multimode_k4 import (
    MODE_NAMES,
    apply_closure,
    fit_pooled_coefficients,
    mode_matrix,
    streamed_mode_sum,
)


def _live(seed: int, n: int = 24):
    rng = np.random.default_rng(seed)
    c = rng.normal(size=(n, n))
    c = 0.5 * (c + c.T)
    k21 = rng.normal(size=(n, n))
    k31 = rng.normal(size=(n, n))
    k22 = rng.normal(size=(n, n))
    k22 = 0.5 * (k22 + k22.T)
    mu = rng.normal(size=n)
    var = rng.uniform(0.5, 1.5, size=n)
    k3v = rng.normal(size=n)
    return {
        "C": c,
        "mu": mu,
        "var": var,
        "K21": k21,
        "K3v": k3v,
        "K31": k31,
        "K22": k22,
    }


def test_frozen_mode_set():
    assert MODE_NAMES == ("cc", "k21", "t", "vv", "k31", "k22", "mc", "mm")


def test_pooled_fit_recovers_one_shared_coefficient_vector():
    truth = np.array([0.11, -0.07, 0.05, 0.03, -0.09, 0.08, 0.04, -0.02])
    samples = []
    for seed in range(4):
        live = _live(1900 + seed)
        residual = streamed_mode_sum(live, truth)
        samples.append((residual, live))

    fitted = fit_pooled_coefficients(samples)
    np.testing.assert_allclose(fitted, truth, rtol=1e-9, atol=1e-9)


def test_modes_and_closure_are_offdiagonal_finite_and_deterministic():
    live = _live(1919)
    coeffs = np.array([0.02, -0.01, 0.03, -0.04, 0.01, 0.005, -0.02, 0.015])
    n = live["C"].shape[0]
    baseline_off = live["C"].copy()
    np.fill_diagonal(baseline_off, 0.0)
    diagonal = np.linspace(0.2, 1.2, n)

    for name in MODE_NAMES:
        mode = mode_matrix(name, live)
        assert np.all(np.isfinite(mode))
        assert np.array_equal(np.diag(mode), np.zeros(n))

    correction_a = streamed_mode_sum(live, coeffs)
    correction_b = streamed_mode_sum(live, coeffs)
    assert np.array_equal(correction_a, correction_b)
    assert np.array_equal(np.diag(correction_a), np.zeros(n))

    closed_a = apply_closure(baseline_off, live, coeffs, diagonal)
    closed_b = apply_closure(baseline_off, live, coeffs, diagonal)
    assert np.array_equal(closed_a, closed_b)
    np.testing.assert_array_equal(np.diag(closed_a), diagonal)
    assert np.all(np.isfinite(closed_a))
