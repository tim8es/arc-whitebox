from __future__ import annotations

import numpy as np

from methods.e091_production_shape_exact import (
    exact_layer_means,
    fit_shared_ridge,
    generate_exact_family_weights,
)


def test_exact_family_small_shape_is_deterministic_and_nonnegative_after_first_layer():
    a = generate_exact_family_weights(seed=12345, width=8, depth=4)
    b = generate_exact_family_weights(seed=12345, width=8, depth=4)
    assert len(a) == 4
    assert all(w.shape == (8, 8) for w in a)
    assert all(w.dtype == np.float32 for w in a)
    for wa, wb in zip(a, b):
        np.testing.assert_array_equal(wa, wb)
    assert np.any(a[0] < 0.0)
    assert all(np.all(w >= 0.0) for w in a[1:])


def test_exact_mean_identity_matches_closed_form_propagation():
    weights = generate_exact_family_weights(seed=54321, width=7, depth=3)
    got = exact_layer_means(weights)
    first = np.sqrt(np.sum(weights[0].astype(np.float64) ** 2, axis=0)) / np.sqrt(
        2.0 * np.pi
    )
    second = first @ weights[1].astype(np.float64)
    third = second @ weights[2].astype(np.float64)
    expected = np.stack([first, second, third])
    np.testing.assert_allclose(got, expected, rtol=0.0, atol=1e-14)


def test_shared_ridge_has_frozen_lambda_and_expected_shape():
    rng = np.random.default_rng(91)
    X = rng.normal(size=(40, 16))
    beta_true = rng.normal(size=16)
    z = X @ beta_true
    beta = fit_shared_ridge(X, z, lam=1.0)
    assert beta.shape == (16,)
    assert np.isfinite(beta).all()
    # Ridge is deterministic and shrunk, not an unregularized exact solve.
    beta2 = fit_shared_ridge(X, z, lam=1.0)
    np.testing.assert_array_equal(beta, beta2)
    assert np.linalg.norm(beta) < np.linalg.norm(beta_true) + 1e-12
