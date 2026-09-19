from __future__ import annotations

import math
import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e119_output_flux_tv_remainder import (
    output_observable,
    production_overhead_upper_flops,
    sketch_remainder_certificate,
    weight_only_tv_bound,
)


def test_first_layer_certificate_is_exact_for_one_relu() -> None:
    w = np.asarray([[3.0], [4.0]], dtype=np.float64)
    areas, variations, tv = weight_only_tv_bound([w], np.asarray([1.0]))
    assert abs(areas[0][0] - 10.0) <= 1e-14
    assert abs(variations[0][0] - 10.0) <= 1e-14
    assert abs(tv - 10.0) <= 1e-14


def test_bound_dominates_exact_scalar_flux_small_network() -> None:
    weights = he_weights(119119, width=4, depth=3)
    c = output_observable(4)
    cert = sketch_remainder_certificate(weights, cells=1024, observable=c)
    ref = build_exact_reference(weights)
    exact_tv = float(np.sum(np.abs(np.asarray(ref.boundary_jumps) @ c)))
    assert cert.finite
    assert exact_tv <= cert.scalar_tv_bound + 1e-12


def test_angular_factor_matches_midpoint_error_envelope() -> None:
    cert = sketch_remainder_certificate(
        [np.asarray([[1.0], [0.0]], dtype=np.float64)],
        cells=1024,
        observable=np.asarray([1.0]),
    )
    assert abs(cert.angular_factor - (1.0 - math.cos(math.pi / 1024))) <= 1e-18


def test_production_overhead_is_tiny_relative_to_cap() -> None:
    overhead = production_overhead_upper_flops(width=1024, depth=16)
    assert overhead == 95_433_280
    assert (73_719_476_736 + overhead) / (2**41) <= 0.13
