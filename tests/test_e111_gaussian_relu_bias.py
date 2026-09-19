from __future__ import annotations

import math

import numpy as np

from methods.e111_gaussian_relu_bias import (
    exact_two_ray_layer,
    gaussian_relu_mean,
    make_frozen_network,
)


def test_gaussian_relu_mean_standard_normal() -> None:
    got = gaussian_relu_mean(0.0, 1.0)
    want = 1.0 / math.sqrt(2.0 * math.pi)
    assert abs(got - want) <= 1e-15


def test_first_layer_two_ray_plugin_is_exact() -> None:
    weights = make_frozen_network(seed=111200, width=8, depth=4)
    state = exact_two_ray_layer(
        weights[0],
        plus_prev=None,
        minus_prev=None,
        first_layer=True,
    )
    np.testing.assert_allclose(
        state["plugin_mean"],
        state["exact_relu_mean"],
        atol=1e-14,
        rtol=0.0,
    )


def test_two_ray_reference_matches_direct_closed_form() -> None:
    w = np.array([[1.5], [-0.7], [0.2]], dtype=np.float64)
    state = exact_two_ray_layer(w, plus_prev=None, minus_prev=None, first_layer=True)
    inv = 1.0 / math.sqrt(2.0 * math.pi)
    exact = np.array([1.5, 0.7, 0.2]) * inv
    np.testing.assert_allclose(state["exact_relu_mean"], exact, atol=1e-15, rtol=0.0)


def test_frozen_network_is_deterministic() -> None:
    a = make_frozen_network(seed=111207, width=8, depth=4)
    b = make_frozen_network(seed=111207, width=8, depth=4)
    assert len(a) == len(b) == 4
    for x, y in zip(a, b, strict=True):
        np.testing.assert_array_equal(x, y)
