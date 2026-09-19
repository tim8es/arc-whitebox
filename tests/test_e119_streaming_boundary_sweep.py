from __future__ import annotations

import numpy as np

from methods.e114_exact_angular_reference import he_weights
from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    GAUSSIAN_FACTOR,
    build_generic_boundary_flux,
    wrapped_angle_error,
)
from methods.e119_streaming_boundary_sweep import (
    PROBE,
    streaming_boundary_sweep,
)


def test_streaming_sweep_matches_owner_reference_one_network():
    weights = he_weights(114200, width=8, depth=4)
    sweep = streaming_boundary_sweep(weights)
    ref = build_generic_boundary_flux(weights)
    assert sweep.region_count == len(ref.sectors)
    assert sweep.boundary_angles.shape == ref.boundary_angles.shape
    assert max(
        wrapped_angle_error(a, b)
        for a, b in zip(sweep.boundary_angles, ref.boundary_angles)
    ) <= 1e-10
    assert np.max(np.abs(sweep.scalar_jumps - ref.scalar_jumps)) <= 1e-10
    assert abs(sweep.mean - ref.full_mean) <= 1e-10


def test_streaming_state_does_not_scale_with_region_count():
    a = streaming_boundary_sweep(he_weights(114200, width=8, depth=4))
    b = streaming_boundary_sweep(he_weights(114202, width=8, depth=4))
    assert a.region_count != b.region_count
    assert a.peak_coefficient_scalars == b.peak_coefficient_scalars
    assert a.peak_mask_bits == b.peak_mask_bits
    assert a.peak_coefficient_scalars == 64
    assert a.peak_mask_bits == 32


def test_deterministic_replay_exact():
    weights = he_weights(114203, width=8, depth=4)
    a = streaming_boundary_sweep(weights)
    b = streaming_boundary_sweep(weights)
    assert np.array_equal(a.boundary_angles, b.boundary_angles)
    assert np.array_equal(a.scalar_jumps, b.scalar_jumps)
    assert a.mean == b.mean
    assert a.ledger == b.ledger
