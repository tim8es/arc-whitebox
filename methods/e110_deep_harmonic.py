"""E110 exact width-2 angular-sector falsifier helpers."""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

TAU = 2.0 * math.pi
HALF_PI = 0.5 * math.pi


@dataclass(frozen=True)
class Sector:
    lo: float
    hi: float
    linear_map: np.ndarray  # shape (2, width): f(theta)=q(theta) @ linear_map


def direct_forward(weights: Sequence[np.ndarray], theta: float) -> np.ndarray:
    q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
    h = q
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        h = h @ w.T
        h = np.maximum(h, 0.0)
    return np.asarray(h, dtype=np.float64)


def _roots_of_linear_form(c: np.ndarray, lo: float, hi: float) -> list[float]:
    a = float(c[0])
    b = float(c[1])
    if math.hypot(a, b) <= 1e-14:
        return []
    base = math.atan2(b, a) + HALF_PI
    out: list[float] = []
    # All calls are within [0, 2*pi], so a small fixed range is sufficient.
    for k in range(-4, 5):
        root = base + k * math.pi
        if lo + 1e-12 < root < hi - 1e-12:
            out.append(root)
    return out


def _unique_sorted(values: list[float], tol: float = 1e-12) -> list[float]:
    values = sorted(values)
    out: list[float] = []
    for value in values:
        if not out or abs(value - out[-1]) > tol:
            out.append(value)
    return out


def enumerate_relu_sectors(weights: Sequence[np.ndarray]) -> list[Sector]:
    """Recursively enumerate exact sign sectors for a width-2 zero-bias ReLU MLP."""
    if not weights:
        raise ValueError("weights must be non-empty")
    for raw_w in weights:
        w = np.asarray(raw_w)
        if w.shape != (2, 2):
            raise ValueError("exact E110 falsifier requires width=2 square weights")

    sectors: list[Sector] = [
        Sector(0.0, TAU, np.eye(2, dtype=np.float64))
    ]

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        next_sectors: list[Sector] = []
        for sector in sectors:
            pre_map = sector.linear_map @ w.T
            cuts = [sector.lo, sector.hi]
            for j in range(2):
                cuts.extend(
                    _roots_of_linear_form(pre_map[:, j], sector.lo, sector.hi)
                )
            cuts = _unique_sorted(cuts)

            for lo, hi in zip(cuts[:-1], cuts[1:]):
                if hi - lo <= 1e-13:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.asarray([math.cos(mid), math.sin(mid)], dtype=np.float64)
                mask = (q @ pre_map) > 0.0
                active_map = pre_map * mask[None, :]
                next_sectors.append(Sector(lo, hi, active_map))
        sectors = next_sectors

    return sectors


def validate_sector_partition(
    weights: Sequence[np.ndarray],
    sectors: Sequence[Sector],
) -> float:
    max_abs = 0.0
    for sector in sectors:
        for frac in (0.21132486540518713, 0.5, 0.7886751345948129):
            theta = sector.lo + frac * (sector.hi - sector.lo)
            q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
            represented = q @ sector.linear_map
            direct = direct_forward(weights, theta)
            max_abs = max(max_abs, float(np.max(np.abs(represented - direct))))
    return max_abs


def meanfield_jacobian(weights: Sequence[np.ndarray]) -> np.ndarray:
    if not weights:
        raise ValueError("weights must be non-empty")
    j = 0.5 * np.asarray(weights[0], dtype=np.float64).T
    for raw_w in weights[1:]:
        j = j @ (0.5 * np.asarray(raw_w, dtype=np.float64).T)
    return j


def deep_output_directions(weights: Sequence[np.ndarray]) -> np.ndarray:
    j = meanfield_jacobian(weights)
    norms = np.linalg.norm(j, axis=0)
    if np.any(norms <= 1e-14):
        raise ValueError("degenerate mean-field output sensitivity")
    return j / norms[None, :]


def _find_sector(sectors: Sequence[Sector], theta: float) -> Sector:
    x = theta % TAU
    if abs(x - TAU) <= 1e-14:
        x = 0.0
    highs = [s.hi for s in sectors]
    idx = bisect.bisect_right(highs, x + 1e-14)
    if idx >= len(sectors):
        idx = len(sectors) - 1
    sector = sectors[idx]
    if not (sector.lo - 1e-11 <= x <= sector.hi + 1e-11):
        # Fall back to a linear scan for near-boundary roundoff only.
        for candidate in sectors:
            if candidate.lo - 1e-11 <= x <= candidate.hi + 1e-11:
                return candidate
        raise RuntimeError(f"angle {x} not covered by sector partition")
    return sector


def block_partition(sectors: Sequence[Sector]) -> list[tuple[float, float, np.ndarray]]:
    """Return [0,pi/2] intervals with exact B(theta)=A cos+B sin coefficients.

    The coefficient matrix has shape (2, width): first row multiplies cos(theta),
    second row multiplies sin(theta).
    """
    cuts = [0.0, HALF_PI]
    for sector in sectors:
        for boundary in (sector.lo, sector.hi):
            if boundary <= 1e-12 or boundary >= TAU - 1e-12:
                continue
            for k in range(4):
                shifted = boundary - k * HALF_PI
                if 1e-12 < shifted < HALF_PI - 1e-12:
                    cuts.append(shifted)
    cuts = _unique_sorted(cuts)

    pieces: list[tuple[float, float, np.ndarray]] = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        if hi - lo <= 1e-13:
            continue
        mid = 0.5 * (lo + hi)
        coeff = np.zeros((2, 2), dtype=np.float64)
        for k in range(4):
            delta = k * HALF_PI
            angle = (mid + delta) % TAU
            sector = _find_sector(sectors, angle)
            c = sector.linear_map
            cd = math.cos(delta)
            sd = math.sin(delta)
            # c[0,j]*cos(theta+delta)+c[1,j]*sin(theta+delta)
            coeff[0, :] += c[0, :] * cd + c[1, :] * sd
            coeff[1, :] += -c[0, :] * sd + c[1, :] * cd
        coeff *= 0.25
        pieces.append((lo, hi, coeff))
    return pieces


def _integral_linear(a: float, b: float, lo: float, hi: float) -> float:
    return a * (math.sin(hi) - math.sin(lo)) + b * (math.cos(lo) - math.cos(hi))


def _integral_linear_square(a: float, b: float, lo: float, hi: float) -> float:
    ic2 = 0.5 * (hi - lo) + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    is2 = 0.5 * (hi - lo) - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    isc = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    return a * a * ic2 + b * b * is2 + 2.0 * a * b * isc


def _primitive_cos1_cos4(theta: float, phase4: float) -> float:
    return 0.5 * (
        math.sin(3.0 * theta - phase4) / 3.0
        + math.sin(5.0 * theta - phase4) / 5.0
    )


def _primitive_sin1_cos4(theta: float, phase4: float) -> float:
    return 0.5 * (
        -math.cos(5.0 * theta - phase4) / 5.0
        + math.cos(3.0 * theta - phase4) / 3.0
    )


def exact_block_harmonic_stats(
    pieces: Sequence[tuple[float, float, np.ndarray]],
    directions: np.ndarray,
) -> dict:
    """Analytically integrate block variance and deep fourth-harmonic covariance."""
    u = np.asarray(directions, dtype=np.float64)
    if u.shape != (2, 2):
        raise ValueError("directions must have shape (2,2)")

    period = HALF_PI
    var_z = 1.0 / 128.0
    outputs = []

    for j in range(2):
        i1 = 0.0
        i2 = 0.0
        ibz = 0.0
        phi = math.atan2(float(u[1, j]), float(u[0, j]))
        phase4 = 4.0 * phi

        for lo, hi, coeff in pieces:
            a = float(coeff[0, j])
            b = float(coeff[1, j])
            i1 += _integral_linear(a, b, lo, hi)
            i2 += _integral_linear_square(a, b, lo, hi)

            dc = _primitive_cos1_cos4(hi, phase4) - _primitive_cos1_cos4(lo, phase4)
            ds = _primitive_sin1_cos4(hi, phase4) - _primitive_sin1_cos4(lo, phase4)
            ibz += 0.125 * (a * dc + b * ds)

        mean = i1 / period
        second = i2 / period
        variance = second - mean * mean
        covariance = ibz / period

        if variance < 0.0 and variance > -1e-13:
            variance = 0.0

        if variance <= 1e-18:
            residual = variance
            ratio = 1.0
            corr = 0.0
            beta = 0.0
            nondegenerate = False
        else:
            beta = covariance / var_z
            residual = variance - covariance * covariance / var_z
            if residual < 0.0 and residual > -1e-13:
                residual = 0.0
            ratio = residual / variance
            corr = covariance / math.sqrt(variance * var_z)
            nondegenerate = True

        outputs.append(
            {
                "output": j,
                "phi": phi,
                "mean": mean,
                "variance": variance,
                "covariance": covariance,
                "control_variance": var_z,
                "oracle_beta": beta,
                "residual_variance": residual,
                "residual_ratio": ratio,
                "correlation": corr,
                "nondegenerate": nondegenerate,
            }
        )

    total_var = sum(x["variance"] for x in outputs)
    total_residual = sum(x["residual_variance"] for x in outputs)
    pooled_ratio = total_residual / total_var if total_var > 0.0 else math.inf

    return {
        "outputs": outputs,
        "pooled_variance": total_var,
        "pooled_residual_variance": total_residual,
        "pooled_ratio": pooled_ratio,
        "pooled_reduction_fraction": 1.0 - pooled_ratio,
        "analytic_control_mean": 0.0,
        "analytic_control_variance": var_z,
    }


def direct_block_value(weights: Sequence[np.ndarray], theta: float) -> np.ndarray:
    values = [
        direct_forward(weights, theta + k * HALF_PI)
        for k in range(4)
    ]
    return np.mean(np.stack(values, axis=0), axis=0)


def validate_block_partition(
    weights: Sequence[np.ndarray],
    pieces: Sequence[tuple[float, float, np.ndarray]],
) -> float:
    max_abs = 0.0
    for lo, hi, coeff in pieces:
        for frac in (0.25, 0.5, 0.75):
            theta = lo + frac * (hi - lo)
            q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
            represented = q @ coeff
            direct = direct_block_value(weights, theta)
            max_abs = max(max_abs, float(np.max(np.abs(represented - direct))))
    return max_abs
