from __future__ import annotations

import math

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    ABS_MEAN_GATE,
    build_generic_boundary_flux,
    partition_metrics,
    wrapped_angle_error,
)


def _compare_to_reference(weights: list[np.ndarray]) -> None:
    generic = build_generic_boundary_flux(weights)
    ref = build_exact_reference(weights)
    c = output_observable(ref.mean.shape[0])
    ref_jumps = np.asarray(ref.boundary_jumps, dtype=np.float64) @ c

    assert generic.finite
    p = partition_metrics(generic)
    assert p["complete"]
    assert p["ordered"]
    assert p["max_gap"] <= 1e-11
    assert p["max_overlap"] <= 1e-11
    assert len(generic.sectors) == len(ref.sectors)
    assert generic.boundary_angles.shape == ref.boundary_angles.shape
    assert generic.scalar_jumps.shape == ref_jumps.shape

    max_angle = max(
        wrapped_angle_error(a, b)
        for a, b in zip(generic.boundary_angles, ref.boundary_angles)
    )
    assert max_angle <= 1e-10
    np.testing.assert_allclose(generic.scalar_jumps, ref_jumps, atol=1e-10, rtol=0.0)

    exact_mean = float(c @ ref.mean)
    assert abs(generic.full_mean - exact_mean) <= 1e-10
    assert abs(generic.compressed_mean - generic.full_mean) <= (
        generic.abs_remainder_certificate + 1e-15
    )
    assert generic.abs_remainder_certificate <= ABS_MEAN_GATE + 1e-15
    assert generic.l1_minimal_under_certificate
    assert generic.flops["flopscope_exact_reconciliation"]


def test_generic_width4_depth3_matches_independent_reference() -> None:
    weights = he_weights(119403, width=4, depth=3)
    _compare_to_reference(weights)


def test_generic_original_e114_shape_is_weight_driven() -> None:
    weights = [
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64),
        np.array([[1.0, 1.0], [-2.0, 0.0]], dtype=np.float64),
        np.array([[2.0], [-1.0]], dtype=np.float64),
    ]
    _compare_to_reference(weights)


def test_generic_constructor_deterministic() -> None:
    weights = he_weights(119804, width=8, depth=4)
    a = build_generic_boundary_flux(weights)
    b = build_generic_boundary_flux(weights)

    assert a.full_mean == b.full_mean
    assert a.compressed_mean == b.compressed_mean
    assert a.abs_remainder_certificate == b.abs_remainder_certificate
    assert np.array_equal(a.boundary_angles, b.boundary_angles)
    assert np.array_equal(a.scalar_jumps, b.scalar_jumps)
    assert np.array_equal(a.kept_indices, b.kept_indices)
    assert np.array_equal(a.omitted_indices, b.omitted_indices)
    assert a.flops == b.flops
