from __future__ import annotations

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e121_haar_plane_orbit import (
    PRODUCTION_FRAMES,
    PRODUCTION_PHASES,
    haar_plane_orbit_mean,
    production_cost_receipt,
)


def test_candidate_does_not_need_reference_and_is_deterministic():
    weights = he_weights(114200, width=8, depth=4)
    a = haar_plane_orbit_mean(
        weights, frames=8, phases=64, seed=121200
    )
    b = haar_plane_orbit_mean(
        weights, frames=8, phases=64, seed=121200
    )
    assert np.array_equal(a.mean, b.mean)
    assert a.frame_orthogonality_max_abs == b.frame_orthogonality_max_abs
    assert a.ledger == b.ledger
    assert a.finite and b.finite


def test_two_dimensional_exact_reference_is_close_without_regions_in_candidate():
    weights = he_weights(114201, width=8, depth=4)
    exact = build_exact_reference(weights).mean
    got = haar_plane_orbit_mean(
        weights, frames=32, phases=64, seed=121201
    )
    assert got.frame_orthogonality_max_abs <= 2e-12
    assert np.mean((got.mean - exact) ** 2) < 1e-5


def test_frozen_production_cost_is_complete_and_under_cap():
    r = production_cost_receipt()
    assert r["frames"] == PRODUCTION_FRAMES == 128
    assert r["phases"] == PRODUCTION_PHASES == 64
    assert r["directions"] == 8192
    assert r["all_in_upper"] == 275184628736
    assert r["passes_cap"]
    assert r["utilization"] <= 0.13
