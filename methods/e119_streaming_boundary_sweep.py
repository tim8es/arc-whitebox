"""E119 theory support: event-driven streaming boundary-flux sweep.

The candidate keeps only the current affine state, finds the next activation
event, emits one scalar derivative jump, and discards the previous state.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from methods.e118_output_flux_sketch import output_observable
from methods.e119_generic_boundary_flux import (
    GAUSSIAN_FACTOR,
    ROOT_TOL,
    TWO_PI,
)

PROBE = 2.0 ** -32
EVENT_TOL = 1e-13


@dataclass(frozen=True)
class SweepResult:
    boundary_angles: np.ndarray
    scalar_jumps: np.ndarray
    mean: float
    region_count: int
    peak_coefficient_scalars: int
    peak_mask_bits: int
    ledger: dict
    finite: bool


@dataclass(frozen=True)
class _CurrentState:
    final_coeff: np.ndarray
    pre_coeffs: tuple[np.ndarray, ...]
    masks: tuple[np.ndarray, ...]


def _roots_strictly_after(
    a: float, b: float, lo: float, hi: float = TWO_PI
) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + EVENT_TOL < root < hi - EVENT_TOL:
            roots.append(float(root))
    return roots


def _state_at(
    weights: Sequence[np.ndarray],
    theta: float,
    ledger: dict,
) -> _CurrentState:
    q = np.array([math.cos(theta), math.sin(theta)], dtype=np.float64)
    ledger["state_probe_trig"] += 32

    coeff = np.eye(2, dtype=np.float64)
    pre_coeffs: list[np.ndarray] = []
    masks: list[np.ndarray] = []

    previous = 2
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        next_width = int(w.shape[1])
        # Conservative multiply+add convention, matching owner E119 style.
        ledger["dense_coefficient_propagation"] += 4 * previous * next_width
        pre = w.T @ coeff
        ledger["probe_sign_eval"] += 4 * next_width
        active = (pre @ q) > 0.0
        ledger["coefficient_mask_apply"] += 2 * next_width

        out = pre.copy()
        out[~active, :] = 0.0
        pre_coeffs.append(pre)
        masks.append(active)
        coeff = out
        previous = next_width

    return _CurrentState(
        final_coeff=coeff,
        pre_coeffs=tuple(pre_coeffs),
        masks=tuple(masks),
    )


def _next_event(
    state: _CurrentState,
    lo: float,
    ledger: dict,
) -> float:
    candidates: list[float] = []
    for pre in state.pre_coeffs:
        for row in pre:
            ledger["root_solve_candidates"] += 32
            candidates.extend(
                _roots_strictly_after(
                    float(row[0]),
                    float(row[1]),
                    lo,
                )
            )
    if not candidates:
        return TWO_PI
    return min(candidates)


def streaming_boundary_sweep(
    weights: Sequence[np.ndarray],
    *,
    max_events: int = 10000,
) -> SweepResult:
    if not weights or len(weights) > 4:
        raise ValueError("requires 1..4 ReLU layers")
    previous = 2
    for w in weights:
        a = np.asarray(w, dtype=np.float64)
        if a.ndim != 2 or a.shape[0] != previous:
            raise ValueError("incompatible weight shapes")
        if a.shape[1] <= 0 or a.shape[1] > 8:
            raise ValueError("width must be <=8")
        if not np.isfinite(a).all():
            raise ValueError("non-finite weights")
        previous = int(a.shape[1])

    final_width = previous
    c = output_observable(final_width)
    ledger = {
        "dense_coefficient_propagation": 0,
        "state_probe_trig": 0,
        "probe_sign_eval": 0,
        "coefficient_mask_apply": 0,
        "root_solve_candidates": 0,
        "boundary_tangent_trig": 0,
        "scalar_jump_eval": 0,
        "running_sum": 0,
    }

    lo = 0.0
    state = _state_at(weights, PROBE, ledger)
    initial_final = state.final_coeff.copy()
    angles: list[float] = []
    jumps: list[float] = []
    region_count = 0

    peak_coeff = max(
        sum(int(pre.size) for pre in state.pre_coeffs),
        int(state.final_coeff.size),
    )
    peak_masks = sum(int(mask.size) for mask in state.masks)

    while lo < TWO_PI - EVENT_TOL:
        region_count += 1
        if region_count > max_events:
            raise RuntimeError("event cap exceeded")

        event = _next_event(state, lo, ledger)
        if event >= TWO_PI - EVENT_TOL:
            break

        right_probe = event + PROBE
        if right_probe >= TWO_PI:
            raise RuntimeError("right probe crosses periodic endpoint")
        right = _state_at(weights, right_probe, ledger)

        ledger["boundary_tangent_trig"] += 32
        tangent = np.array(
            [-math.sin(event), math.cos(event)],
            dtype=np.float64,
        )
        diff = right.final_coeff - state.final_coeff
        ledger["scalar_jump_eval"] += 5 * final_width + 4
        jump = float(c @ (diff @ tangent))
        ledger["running_sum"] += 1

        angles.append(float(event))
        jumps.append(jump)
        lo = float(event)
        state = right

        peak_coeff = max(
            peak_coeff,
            sum(int(pre.size) for pre in state.pre_coeffs),
            int(state.final_coeff.size),
        )
        peak_masks = max(
            peak_masks,
            sum(int(mask.size) for mask in state.masks),
        )

    # Periodic 2pi -> 0 boundary, kept last to match E114/E119 ordering.
    ledger["boundary_tangent_trig"] += 32
    tangent0 = np.array([0.0, 1.0], dtype=np.float64)
    diff0 = initial_final - state.final_coeff
    ledger["scalar_jump_eval"] += 5 * final_width + 4
    periodic_jump = float(c @ (diff0 @ tangent0))
    ledger["running_sum"] += 1
    angles.append(0.0)
    jumps.append(periodic_jump)

    angles_np = np.asarray(angles, dtype=np.float64)
    jumps_np = np.asarray(jumps, dtype=np.float64)
    mean = GAUSSIAN_FACTOR * float(np.sum(jumps_np, dtype=np.float64))

    manual_total = int(sum(ledger.values()))
    finite = bool(
        np.isfinite(angles_np).all()
        and np.isfinite(jumps_np).all()
        and math.isfinite(mean)
    )

    return SweepResult(
        boundary_angles=angles_np,
        scalar_jumps=jumps_np,
        mean=mean,
        region_count=region_count,
        peak_coefficient_scalars=peak_coeff,
        peak_mask_bits=peak_masks,
        ledger={
            **ledger,
            "all_in_flop_equivalent": manual_total,
            "boundary_count_independent_peak_state": True,
        },
        finite=finite,
    )
