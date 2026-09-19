"""E119 generic weight-driven boundary-flux construction and omission certificate.

This is a direct deployability bridge from E118/E114 for two-dimensional,
zero-bias ReLU networks with width <= 8 and depth <= 4.

The constructor mechanically discovers angular regions from weights, computes
the scalar final-observable derivative jumps, and compresses the boundary atom
list with a rigorous L1 omitted-flux certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e118_output_flux_sketch import output_observable


TWO_PI = 2.0 * math.pi
ROOT_TOL = 2.0 ** -40
SECTOR_TOL = 1e-13
RAW_MSE_GATE = 1.89e-8
ABS_MEAN_GATE = math.sqrt(RAW_MSE_GATE)
GAUSSIAN_FACTOR = math.sqrt(math.pi / 2.0) / TWO_PI
OMITTED_FLUX_L1_BUDGET = ABS_MEAN_GATE / GAUSSIAN_FACTOR


@dataclass(frozen=True)
class GenericSector:
    lo: float
    hi: float
    coeff: np.ndarray


@dataclass(frozen=True)
class GenericBoundaryFlux:
    sectors: tuple[GenericSector, ...]
    boundary_angles: np.ndarray
    scalar_jumps: np.ndarray
    full_mean: float
    kept_indices: np.ndarray
    omitted_indices: np.ndarray
    kept_angles: np.ndarray
    kept_jumps: np.ndarray
    compressed_mean: float
    omitted_abs_flux_sum: float
    abs_remainder_certificate: float
    next_omission_abs_flux: float | None
    l1_minimal_under_certificate: bool
    layer_region_counts: tuple[int, ...]
    flops: dict
    finite: bool


def _validate_weights(weights: Sequence[np.ndarray]) -> tuple[int, int]:
    if not weights:
        raise ValueError("weights must be non-empty")
    if len(weights) > 4:
        raise ValueError("E119 supports depth <= 4")

    previous = 2
    final_width = None
    max_width = 0
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous or w.shape[1] <= 0:
            raise ValueError(
                f"weight {idx} has shape {w.shape}; expected ({previous}, next_width)"
            )
        if w.shape[1] > 8:
            raise ValueError("E119 supports width <= 8")
        if not np.isfinite(w).all():
            raise ValueError(f"weight {idx} contains non-finite values")
        previous = int(w.shape[1])
        final_width = previous
        max_width = max(max_width, previous)

    assert final_width is not None
    return final_width, max_width


def _roots_in_interval(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + SECTOR_TOL < root < hi - SECTOR_TOL:
            roots.append(float(root))
    return roots


def _dedup(values: Iterable[float], tol: float = ROOT_TOL) -> list[float]:
    out: list[float] = []
    for value in sorted(float(v) for v in values):
        if not out or abs(value - out[-1]) > tol:
            out.append(value)
    return out


def _partition_metrics(sectors: Sequence[GenericSector]) -> dict:
    if not sectors:
        return {
            "complete": False,
            "ordered": False,
            "finite": False,
            "max_gap": math.inf,
            "max_overlap": math.inf,
        }

    complete = abs(float(sectors[0].lo)) <= 1e-12
    complete = complete and abs(float(sectors[-1].hi) - TWO_PI) <= 1e-12
    ordered = True
    finite = True
    max_gap = 0.0
    max_overlap = 0.0

    prev_hi = float(sectors[0].lo)
    for sector in sectors:
        lo = float(sector.lo)
        hi = float(sector.hi)
        if not (math.isfinite(lo) and math.isfinite(hi)):
            finite = False
        if not np.isfinite(sector.coeff).all():
            finite = False
        if hi <= lo:
            ordered = False
        delta = lo - prev_hi
        if delta > 0.0:
            max_gap = max(max_gap, delta)
        elif delta < 0.0:
            max_overlap = max(max_overlap, -delta)
        if abs(delta) > 1e-11:
            complete = False
        prev_hi = hi

    return {
        "complete": complete,
        "ordered": ordered,
        "finite": finite,
        "max_gap": max_gap,
        "max_overlap": max_overlap,
    }


def _manual_sort_charge(n: int) -> int:
    if n <= 1:
        return 0
    return 8 * n * int(math.ceil(math.log2(max(n, 2))))


def build_generic_boundary_flux(
    weights: Sequence[np.ndarray],
    *,
    budget: int = 2**41,
) -> GenericBoundaryFlux:
    """Mechanically construct regions, scalar jumps, compression, and certificate."""
    final_width, _ = _validate_weights(weights)
    observable = output_observable(final_width)

    sectors: list[GenericSector] = [
        GenericSector(0.0, TWO_PI, np.eye(2, dtype=np.float64))
    ]
    layer_region_counts: list[int] = []
    layer_dense_flops: list[int] = []

    manual = {
        "root_solve_candidates": 0,
        "midpoint_trig": 0,
        "midpoint_signs": 0,
        "boundary_tangent_trig": 0,
        "scalar_jump_eval": 0,
        "sort": 0,
        "certificate": 0,
    }

    with flops.BudgetContext(flop_budget=budget, quiet=True) as ctx:
        flops_start = int(ctx.flops_used)

        for raw_w in weights:
            w_np = np.asarray(raw_w, dtype=np.float64)
            w_f = fnp.asarray(w_np, dtype=fnp.float64)
            layer_start = int(ctx.flops_used)
            next_sectors: list[GenericSector] = []

            for sector in sectors:
                a_f = fnp.asarray(sector.coeff, dtype=fnp.float64)
                pre_f = fnp.matmul(fnp.swapaxes(w_f, 0, 1), a_f)
                pre = np.asarray(pre_f, dtype=np.float64).copy()

                boundaries = [sector.lo, sector.hi]
                for row in pre:
                    manual["root_solve_candidates"] += 32
                    boundaries.extend(
                        _roots_in_interval(
                            float(row[0]),
                            float(row[1]),
                            sector.lo,
                            sector.hi,
                        )
                    )
                boundaries = _dedup(boundaries)

                for left, right in zip(boundaries[:-1], boundaries[1:]):
                    if right - left <= SECTOR_TOL:
                        continue
                    mid = 0.5 * (left + right)
                    manual["midpoint_trig"] += 32
                    q = np.array(
                        [math.cos(mid), math.sin(mid)],
                        dtype=np.float64,
                    )
                    manual["midpoint_signs"] += 4 * int(pre.shape[0])
                    active = (pre @ q) > 0.0
                    coeff = pre.copy()
                    coeff[~active, :] = 0.0
                    next_sectors.append(GenericSector(left, right, coeff))

            layer_end = int(ctx.flops_used)
            layer_dense_flops.append(layer_end - layer_start)
            sectors = next_sectors
            layer_region_counts.append(len(sectors))

        flops_end = int(ctx.flops_used)

    if not sectors:
        raise RuntimeError("generic construction produced no final sectors")

    boundary_angles: list[float] = []
    scalar_jumps: list[float] = []

    for left_sector, right_sector in zip(sectors[:-1], sectors[1:]):
        theta = float(left_sector.hi)
        manual["boundary_tangent_trig"] += 32
        tangent = np.array(
            [-math.sin(theta), math.cos(theta)],
            dtype=np.float64,
        )
        diff = right_sector.coeff - left_sector.coeff
        manual["scalar_jump_eval"] += 5 * final_width + 4
        jump = float(observable @ (diff @ tangent))
        boundary_angles.append(theta)
        scalar_jumps.append(jump)

    # Periodic 2pi -> 0 boundary.
    theta = 0.0
    manual["boundary_tangent_trig"] += 32
    tangent = np.array([0.0, 1.0], dtype=np.float64)
    diff = sectors[0].coeff - sectors[-1].coeff
    manual["scalar_jump_eval"] += 5 * final_width + 4
    jump = float(observable @ (diff @ tangent))
    boundary_angles.append(theta)
    scalar_jumps.append(jump)

    angles_np = np.asarray(boundary_angles, dtype=np.float64)
    jumps_np = np.asarray(scalar_jumps, dtype=np.float64)
    full_mean = GAUSSIAN_FACTOR * float(np.sum(jumps_np, dtype=np.float64))

    n_atoms = int(jumps_np.shape[0])
    manual["sort"] += _manual_sort_charge(n_atoms)
    order = sorted(
        range(n_atoms),
        key=lambda i: (abs(float(jumps_np[i])), float(angles_np[i]), int(i)),
    )

    omitted: list[int] = []
    omitted_abs = 0.0
    next_omission_abs: float | None = None

    for idx in order:
        manual["certificate"] += 6
        candidate_abs = abs(float(jumps_np[idx]))
        if omitted_abs + candidate_abs <= OMITTED_FLUX_L1_BUDGET:
            omitted.append(idx)
            omitted_abs += candidate_abs
        else:
            next_omission_abs = candidate_abs
            break

    omitted_set = set(omitted)
    kept = [i for i in range(n_atoms) if i not in omitted_set]

    kept_indices = np.asarray(kept, dtype=np.int64)
    omitted_indices = np.asarray(omitted, dtype=np.int64)
    kept_angles = angles_np[kept_indices] if kept else np.zeros(0, dtype=np.float64)
    kept_jumps = jumps_np[kept_indices] if kept else np.zeros(0, dtype=np.float64)

    compressed_mean = GAUSSIAN_FACTOR * float(
        np.sum(kept_jumps, dtype=np.float64)
    )
    certificate = GAUSSIAN_FACTOR * omitted_abs

    if len(omitted) == n_atoms:
        minimal = True
    else:
        if next_omission_abs is None:
            remaining_abs = sorted(
                abs(float(jumps_np[i]))
                for i in range(n_atoms)
                if i not in omitted_set
            )
            next_omission_abs = remaining_abs[0] if remaining_abs else None
        minimal = bool(
            next_omission_abs is not None
            and omitted_abs + float(next_omission_abs)
            > OMITTED_FLUX_L1_BUDGET
        )

    manual_total = int(sum(manual.values()))
    dense_total = int(flops_end - flops_start)
    all_in = dense_total + manual_total
    partition = _partition_metrics(sectors)

    finite = bool(
        partition["finite"]
        and np.isfinite(angles_np).all()
        and np.isfinite(jumps_np).all()
        and math.isfinite(full_mean)
        and math.isfinite(compressed_mean)
        and math.isfinite(certificate)
    )

    return GenericBoundaryFlux(
        sectors=tuple(sectors),
        boundary_angles=angles_np,
        scalar_jumps=jumps_np,
        full_mean=full_mean,
        kept_indices=kept_indices,
        omitted_indices=omitted_indices,
        kept_angles=kept_angles,
        kept_jumps=kept_jumps,
        compressed_mean=compressed_mean,
        omitted_abs_flux_sum=float(omitted_abs),
        abs_remainder_certificate=float(certificate),
        next_omission_abs_flux=(
            None if next_omission_abs is None else float(next_omission_abs)
        ),
        l1_minimal_under_certificate=minimal,
        layer_region_counts=tuple(layer_region_counts),
        flops={
            "budget_context_dense_layer_flops": layer_dense_flops,
            "flopscope_dense_flops": dense_total,
            "flopscope_reconciled_sum": int(sum(layer_dense_flops)),
            "flopscope_exact_reconciliation": int(sum(layer_dense_flops))
            == dense_total,
            "manual_geometry_breakdown": manual,
            "manual_geometry_flop_equivalent": manual_total,
            "all_in_accounted_flops": all_in,
            "all_in_utilization_vs_2pow41": all_in / float(2**41),
            "manual_charge_schedule_frozen": True,
        },
        finite=finite,
    )


def partition_metrics(result: GenericBoundaryFlux) -> dict:
    return _partition_metrics(result.sectors)


def wrapped_angle_error(a: float, b: float) -> float:
    d = abs(float(a) - float(b)) % TWO_PI
    return min(d, TWO_PI - d)
