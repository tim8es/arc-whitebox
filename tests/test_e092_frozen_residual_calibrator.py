from __future__ import annotations

import inspect

import numpy as np

from methods.e092_frozen_residual_calibrator import (
    FrozenRidgeModel,
    antithetic_reference,
    apply_frozen_ridge,
    covariance_baseline_numpy,
    final_layer_features,
    fit_frozen_ridge,
    generate_synthetic_mlp,
)


def test_feature_map_is_finite_deterministic_and_frozen_width() -> None:
    weights = generate_synthetic_mlp(seed=7, width=8, depth=4)
    baseline = covariance_baseline_numpy(weights)

    first = final_layer_features(baseline, weights[-1])
    second = final_layer_features(baseline, weights[-1])

    assert first.shape == (8, 8)
    assert np.array_equal(first, second)
    assert np.all(np.isfinite(first))
    assert np.array_equal(first[:, 0], np.ones(8, dtype=np.float64))


def test_ridge_fit_recovers_known_target_without_target_in_feature_api() -> None:
    rng = np.random.default_rng(92)
    x = rng.normal(size=(64, 8))
    x[:, 0] = 1.0
    truth = np.array([0.04, -0.03, 0.02, 0.01, -0.015, 0.025, -0.005, 0.012])
    residual = x @ truth
    base = np.linspace(0.2, 0.8, x.shape[0])

    model = fit_frozen_ridge(x, residual, lambda_=1e-2)
    adjusted = apply_frozen_ridge(x, base, model)

    assert isinstance(model, FrozenRidgeModel)
    assert model.coefficients.shape == (8,)
    assert np.mean((adjusted - (base + residual)) ** 2) < 1e-7

    signature = inspect.signature(final_layer_features)
    forbidden = {"target", "targets", "y", "residual", "reference"}
    assert forbidden.isdisjoint(signature.parameters)


def test_synthetic_generator_and_reference_are_deterministic() -> None:
    weights_a = generate_synthetic_mlp(seed=123, width=6, depth=3)
    weights_b = generate_synthetic_mlp(seed=123, width=6, depth=3)
    assert all(np.array_equal(a, b) for a, b in zip(weights_a, weights_b, strict=True))

    ref_a = antithetic_reference(weights_a, input_seed=999, samples=2048)
    ref_b = antithetic_reference(weights_a, input_seed=999, samples=2048)
    baseline = covariance_baseline_numpy(weights_a)

    assert ref_a.shape == (3, 6)
    assert baseline.shape == (3, 6)
    assert np.array_equal(ref_a, ref_b)
    assert np.all(np.isfinite(ref_a))
    assert np.all(np.isfinite(baseline))
