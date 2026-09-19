from __future__ import annotations

import math

import numpy as np

from methods.e113_radial_sufficiency import (
    annealed_final_mean_from_state_radius,
    annealed_radius_multiplier,
    exact_angular_layers,
    expected_chi,
    make_weights,
    quenched_obstruction_certificate,
)


def test_expected_chi_known_values():
    assert abs(expected_chi(1) - math.sqrt(2.0 / math.pi)) < 1e-14
    assert abs(expected_chi(2) - math.sqrt(math.pi / 2.0)) < 1e-14


def test_scalar_annealed_radius_multiplier():
    # d=m=1: ReLU(sqrt(2) g h) has radius multiplier
    # sqrt(2) E[g_+] = 1/sqrt(pi).
    got = annealed_radius_multiplier(1, 1)
    assert abs(got - 1.0 / math.sqrt(math.pi)) < 1e-14


def test_one_layer_exact_angular_mean_matches_gaussian_formula():
    weights = make_weights(seed=113001, latent_dim=2, width=4, depth=1)
    ref = exact_angular_layers(weights)
    exact = ref["layers"][0]["post_mean"]
    w = weights[0]
    expected = np.linalg.norm(w, axis=0) / math.sqrt(2.0 * math.pi)
    assert np.max(np.abs(exact - expected)) < 2e-12


def test_quenched_rank_and_same_radius_obstruction():
    weights = make_weights(seed=113002, latent_dim=2, width=8, depth=3)
    cert = quenched_obstruction_certificate(weights[1])
    assert cert["rank"] == 8
    assert cert["local_jacobian_rank"] == 8
    assert cert["active_cone_residual"] < 1e-10
    assert cert["same_radius_delta"] == 0.0
    assert cert["same_radius_output_l2_delta"] > 1e-6


def test_future_annealed_mean_is_linear_in_state_radius():
    a = annealed_final_mean_from_state_radius(
        1.25, width=8, remaining_layers=2
    )
    b = annealed_final_mean_from_state_radius(
        2.5, width=8, remaining_layers=2
    )
    assert abs(b - 2.0 * a) < 1e-15
