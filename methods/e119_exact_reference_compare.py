"""Reusable E119 exact-reference comparison for generic boundary implementations."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from methods.e114_exact_angular_reference import (
    build_exact_reference,
    enumerate_layer_sectors,
    evaluate_network_direction,
)
from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    GAUSSIAN_FACTOR,
    build_generic_boundary_flux,
    partition_metrics,
    wrapped_angle_error,
)


@dataclass(frozen=True)
class BoundaryReferenceComparison:
    layer_region_counts_generic: tuple[int, ...]
    layer_region_counts_reference: tuple[int, ...]
    final_region_count_generic: int
    final_region_count_reference: int
    partition_complete: bool
    partition_ordered: bool
    max_partition_gap: float
    max_partition_overlap: float
    max_sector_lo_error: float
    max_sector_hi_error: float
    max_sector_coeff_abs_error: float
    max_reference_direct_eval_abs_error: float
    max_generic_direct_eval_abs_error: float
    max_boundary_angle_wrapped_error: float
    max_scalar_jump_abs_error: float
    generic_scalar_mean: float
    reference_sector_scalar_mean: float
    reference_flux_scalar_mean: float
    generic_vs_reference_mean_abs_error: float
    reference_flux_vs_sector_mean_abs_error: float
    finite: bool


def _max_abs(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return math.inf
    if a.size == 0:
        return 0.0
    return float(np.max(np.abs(a - b)))


def compare_generic_boundary_to_exact(
    weights: Sequence[np.ndarray],
    *,
    budget: int = 2**41,
) -> BoundaryReferenceComparison:
    """Compare generic E119 construction against the independent angular oracle."""
    generic = build_generic_boundary_flux(weights, budget=budget)
    reference = build_exact_reference(weights)
    layer_reference = enumerate_layer_sectors(weights)
    c = output_observable(reference.mean.shape[0])

    p = partition_metrics(generic)

    generic_sectors = generic.sectors
    reference_sectors = reference.sectors
    same_sector_count = len(generic_sectors) == len(reference_sectors)

    lo_err = 0.0
    hi_err = 0.0
    coeff_err = 0.0
    ref_direct_err = 0.0
    generic_direct_err = 0.0

    if not same_sector_count:
        lo_err = hi_err = coeff_err = math.inf
        ref_direct_err = generic_direct_err = math.inf
    else:
        for gs, rs in zip(generic_sectors, reference_sectors):
            lo_err = max(lo_err, abs(float(gs.lo) - float(rs.lo)))
            hi_err = max(hi_err, abs(float(gs.hi) - float(rs.hi)))
            coeff_err = max(coeff_err, _max_abs(gs.coeff, rs.coeff))

            # Three deterministic interior probes make the sector oracle
            # independently answerable by direct raw-network evaluation.
            for frac in (0.25, 0.5, 0.75):
                theta = float(rs.lo + frac * (rs.hi - rs.lo))
                q = np.array([math.cos(theta), math.sin(theta)], dtype=np.float64)
                direct = evaluate_network_direction(weights, theta)
                ref_value = rs.coeff @ q
                gen_value = gs.coeff @ q
                ref_direct_err = max(
                    ref_direct_err,
                    _max_abs(np.asarray(ref_value), np.asarray(direct)),
                )
                generic_direct_err = max(
                    generic_direct_err,
                    _max_abs(np.asarray(gen_value), np.asarray(direct)),
                )

    ref_angles = np.asarray(reference.boundary_angles, dtype=np.float64)
    ref_scalar_jumps = np.asarray(reference.boundary_jumps, dtype=np.float64) @ c
    same_boundary_shape = (
        generic.boundary_angles.shape == ref_angles.shape
        and generic.scalar_jumps.shape == ref_scalar_jumps.shape
    )
    if same_boundary_shape and generic.boundary_angles.size:
        angle_err = max(
            wrapped_angle_error(a, b)
            for a, b in zip(generic.boundary_angles, ref_angles)
        )
        jump_err = _max_abs(generic.scalar_jumps, ref_scalar_jumps)
    elif same_boundary_shape:
        angle_err = 0.0
        jump_err = 0.0
    else:
        angle_err = jump_err = math.inf

    sector_mean = float(c @ reference.mean)
    flux_mean = float(GAUSSIAN_FACTOR * np.sum(ref_scalar_jumps, dtype=np.float64))

    finite_values = [
        lo_err,
        hi_err,
        coeff_err,
        ref_direct_err,
        generic_direct_err,
        angle_err,
        jump_err,
        generic.full_mean,
        sector_mean,
        flux_mean,
    ]
    finite = bool(
        generic.finite
        and all(math.isfinite(x) for x in finite_values)
        and p["finite"]
    )

    return BoundaryReferenceComparison(
        layer_region_counts_generic=tuple(generic.layer_region_counts),
        layer_region_counts_reference=tuple(len(x) for x in layer_reference),
        final_region_count_generic=len(generic_sectors),
        final_region_count_reference=len(reference_sectors),
        partition_complete=bool(p["complete"]),
        partition_ordered=bool(p["ordered"]),
        max_partition_gap=float(p["max_gap"]),
        max_partition_overlap=float(p["max_overlap"]),
        max_sector_lo_error=lo_err,
        max_sector_hi_error=hi_err,
        max_sector_coeff_abs_error=coeff_err,
        max_reference_direct_eval_abs_error=ref_direct_err,
        max_generic_direct_eval_abs_error=generic_direct_err,
        max_boundary_angle_wrapped_error=float(angle_err),
        max_scalar_jump_abs_error=float(jump_err),
        generic_scalar_mean=float(generic.full_mean),
        reference_sector_scalar_mean=sector_mean,
        reference_flux_scalar_mean=flux_mean,
        generic_vs_reference_mean_abs_error=abs(generic.full_mean - sector_mean),
        reference_flux_vs_sector_mean_abs_error=abs(flux_mean - sector_mean),
        finite=finite,
    )
