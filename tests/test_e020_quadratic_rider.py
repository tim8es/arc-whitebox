import numpy as np

from methods.e020_quadratic_rider import (
    BASE_FEATURE_NAMES,
    DESIGN_WIDTH,
    apply_rider,
    fit_layer_rider,
    hermite_design,
)


def test_fixed_feature_contract_and_design_width():
    assert BASE_FEATURE_NAMES == (
        "alpha",
        "abs_alpha",
        "phi",
        "Phi",
        "pred_scaled",
        "d3_scaled",
        "d21_scaled",
    )
    assert DESIGN_WIDTH == 36


def test_hermite_design_is_deterministic_and_has_frozen_terms():
    rng = np.random.default_rng(2020)
    x = rng.normal(size=(64, 7))
    mean = np.zeros(7)
    scale = np.ones(7)
    a = hermite_design(x, mean, scale)
    b = hermite_design(x, mean, scale)
    assert np.array_equal(a, b)
    assert a.shape == (64, 36)
    np.testing.assert_array_equal(a[:, 0], np.ones(64))
    np.testing.assert_allclose(a[:, 1:8], x)
    np.testing.assert_allclose(a[:, 8:15], x * x - 1.0)


def test_pooled_ols_recovers_shared_quadratic_map_and_applies_deterministically():
    rng = np.random.default_rng(2021)
    x = rng.normal(size=(4096, 7))
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    design = hermite_design(x, mean, scale)
    truth = rng.normal(scale=0.02, size=DESIGN_WIDTH)
    target = design @ truth

    fit = fit_layer_rider(x, target, condition_limit=1e8)
    assert fit.rank == DESIGN_WIDTH
    assert fit.condition <= 1e8
    np.testing.assert_allclose(fit.coefficients, truth, rtol=1e-9, atol=1e-9)

    delta_a = apply_rider(x, fit)
    delta_b = apply_rider(x, fit)
    assert np.array_equal(delta_a, delta_b)
    np.testing.assert_allclose(delta_a, target, rtol=1e-9, atol=1e-9)
