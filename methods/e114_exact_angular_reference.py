"""Reusable exact 2-D angular reference for E114 boundary-flux compression diagnostics.

This module is reference-only. It does not choose a deployable compression
mechanism. It enumerates exact ReLU angular sectors for zero-bias networks,
computes exact Gaussian final-output moments and E114 boundary-flux objects,
then evaluates externally supplied output-space projectors/observables.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np

_TWO_PI = 2.0 * math.pi
_ROOT_TOL = 2.0 ** -40
_SECTOR_TOL = 1e-13


@dataclass(frozen=True)
class AngularSector:
    lo: float
    hi: float
    coeff: np.ndarray  # shape (output_width, 2): h(theta)=coeff @ [cos,sin]


@dataclass(frozen=True)
class ExactAngularReference:
    sectors: tuple[AngularSector, ...]
    mean: np.ndarray
    second_moment: np.ndarray
    covariance: np.ndarray
    boundary_angles: np.ndarray
    boundary_jumps: np.ndarray
    flux_sum: np.ndarray
    flux_gram: np.ndarray
    flux_mean: np.ndarray
    mean_radius: float
    second_radius_moment: float


def he_weights(
    seed: int,
    *,
    width: int,
    depth: int,
    input_dim: int = 2,
) -> list[np.ndarray]:
    """Deterministic float64 iid He-normal weights."""
    if input_dim != 2:
        raise ValueError("exact angular reference currently requires input_dim=2")
    if width <= 0 or depth <= 0:
        raise ValueError("width/depth must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    first = rng.standard_normal((input_dim, width)).astype(np.float64)
    first *= math.sqrt(2.0 / input_dim)
    out.append(first)
    for _ in range(1, depth):
        w = rng.standard_normal((width, width)).astype(np.float64)
        w *= math.sqrt(2.0 / width)
        out.append(w)
    return out



def dense_he_weights(
    seed: int,
    *,
    widths: Sequence[int],
    input_dim: int = 2,
) -> list[np.ndarray]:
    """Deterministic float64 dense He-normal chain with arbitrary small widths."""
    if input_dim != 2:
        raise ValueError("exact angular reference currently requires input_dim=2")
    if not widths:
        raise ValueError("widths must be non-empty")
    if any(int(w) <= 0 for w in widths):
        raise ValueError("all widths must be positive")

    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    fan_in = int(input_dim)
    for raw_width in widths:
        width = int(raw_width)
        w = rng.standard_normal((fan_in, width)).astype(np.float64)
        w *= math.sqrt(2.0 / fan_in)
        out.append(w)
        fan_in = width
    return out


def evaluate_network_direction(
    weights: Sequence[np.ndarray],
    theta: float,
) -> np.ndarray:
    """Direct float64 network evaluation on q(theta), independent of sector state."""
    _validate_weights(weights)
    h = np.array([math.cos(theta), math.sin(theta)], dtype=np.float64)
    for raw_w in weights:
        h = h @ np.asarray(raw_w, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return np.asarray(h, dtype=np.float64)


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
        if lo + _SECTOR_TOL < root < hi - _SECTOR_TOL:
            roots.append(float(root))
    return roots


def _dedup(values: Iterable[float], tol: float = _ROOT_TOL) -> list[float]:
    out: list[float] = []
    for value in sorted(float(v) for v in values):
        if not out or abs(value - out[-1]) > tol:
            out.append(value)
    return out


def _first_basis_integral(lo: float, hi: float) -> np.ndarray:
    return np.array(
        [
            math.sin(hi) - math.sin(lo),
            -math.cos(hi) + math.cos(lo),
        ],
        dtype=np.float64,
    )


def _second_basis_integral(lo: float, hi: float) -> np.ndarray:
    delta = hi - lo
    cc = 0.5 * delta + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    ss = 0.5 * delta - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    cs = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    return np.array([[cc, cs], [cs, ss]], dtype=np.float64)


def _validate_weights(weights: Sequence[np.ndarray]) -> None:
    if not weights:
        raise ValueError("weights must be non-empty")
    previous_width = 2
    for idx, raw in enumerate(weights):
        w = np.asarray(raw)
        if w.ndim != 2 or w.shape[0] != previous_width or w.shape[1] <= 0:
            raise ValueError(
                f"weight {idx} has shape {w.shape}; expected ({previous_width}, next_width)"
            )
        if not np.isfinite(w).all():
            raise ValueError(f"weight {idx} is non-finite")
        previous_width = int(w.shape[1])


def enumerate_layer_sectors(
    weights: Sequence[np.ndarray],
) -> tuple[tuple[AngularSector, ...], ...]:
    """Enumerate the complete angular partition after every ReLU layer."""
    _validate_weights(weights)
    current: list[AngularSector] = [
        AngularSector(0.0, _TWO_PI, np.eye(2, dtype=np.float64))
    ]
    layers: list[tuple[AngularSector, ...]] = []

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        nxt: list[AngularSector] = []
        for sector in current:
            pre = w.T @ sector.coeff
            boundaries = [sector.lo, sector.hi]
            for row in pre:
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
                if right - left <= _SECTOR_TOL:
                    continue
                mid = 0.5 * (left + right)
                q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                active = (pre @ q) > 0.0
                coeff = pre.copy()
                coeff[~active, :] = 0.0
                nxt.append(AngularSector(left, right, coeff))
        current = nxt
        if not current:
            raise RuntimeError("angular partition became empty")
        layers.append(tuple(current))

    return tuple(layers)


def enumerate_final_sectors(weights: Sequence[np.ndarray]) -> tuple[AngularSector, ...]:
    """Enumerate the complete exact final angular partition."""
    return enumerate_layer_sectors(weights)[-1]


def partition_diagnostics(sectors: Sequence[AngularSector]) -> dict:
    ordered = True
    complete = True
    finite = True
    max_gap = 0.0
    max_overlap = 0.0

    if not sectors:
        return {
            "ordered": False,
            "complete": False,
            "finite": False,
            "max_gap": math.inf,
            "max_overlap": math.inf,
        }

    if abs(float(sectors[0].lo)) > 1e-12:
        complete = False
    if abs(float(sectors[-1].hi) - _TWO_PI) > 1e-12:
        complete = False

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
        "ordered": ordered,
        "complete": complete,
        "finite": finite,
        "max_gap": max_gap,
        "max_overlap": max_overlap,
    }


def _boundary_flux(
    sectors: Sequence[AngularSector],
) -> tuple[np.ndarray, np.ndarray]:
    if not sectors:
        raise ValueError("sectors must be non-empty")
    width = sectors[0].coeff.shape[0]
    angles: list[float] = []
    jumps: list[np.ndarray] = []

    # Internal boundaries.
    for left_sector, right_sector in zip(sectors[:-1], sectors[1:]):
        theta = float(left_sector.hi)
        tangent = np.array([-math.sin(theta), math.cos(theta)], dtype=np.float64)
        jump = (right_sector.coeff - left_sector.coeff) @ tangent
        angles.append(theta)
        jumps.append(jump)

    # Periodic 2pi -> 0 boundary.
    theta = 0.0
    tangent = np.array([0.0, 1.0], dtype=np.float64)
    jump = (sectors[0].coeff - sectors[-1].coeff) @ tangent
    angles.append(theta)
    jumps.append(jump)

    if jumps:
        return (
            np.asarray(angles, dtype=np.float64),
            np.stack(jumps, axis=0).astype(np.float64, copy=False),
        )
    return (
        np.zeros(0, dtype=np.float64),
        np.zeros((0, width), dtype=np.float64),
    )


def build_exact_reference(weights: Sequence[np.ndarray]) -> ExactAngularReference:
    """Compute exact Gaussian final-output mean/covariance and E114 flux objects."""
    sectors = enumerate_final_sectors(weights)
    width = sectors[0].coeff.shape[0]

    angular_first = np.zeros(width, dtype=np.float64)
    angular_second = np.zeros((width, width), dtype=np.float64)

    for sector in sectors:
        b1 = _first_basis_integral(sector.lo, sector.hi)
        b2 = _second_basis_integral(sector.lo, sector.hi)
        angular_first += sector.coeff @ b1
        angular_second += sector.coeff @ b2 @ sector.coeff.T

    mean_radius = math.sqrt(math.pi / 2.0)
    second_radius = 2.0
    mean = mean_radius * angular_first / _TWO_PI
    second = second_radius * angular_second / _TWO_PI
    covariance = second - np.outer(mean, mean)
    covariance = 0.5 * (covariance + covariance.T)

    angles, jumps = _boundary_flux(sectors)
    flux_sum = np.sum(jumps, axis=0, dtype=np.float64)
    flux_gram = jumps.T @ jumps
    flux_mean = mean_radius * flux_sum / _TWO_PI

    return ExactAngularReference(
        sectors=sectors,
        mean=mean,
        second_moment=second,
        covariance=covariance,
        boundary_angles=angles,
        boundary_jumps=jumps,
        flux_sum=flux_sum,
        flux_gram=flux_gram,
        flux_mean=flux_mean,
        mean_radius=mean_radius,
        second_radius_moment=second_radius,
    )


def canonicalize_basis_signs(u: np.ndarray) -> np.ndarray:
    out = np.asarray(u, dtype=np.float64).copy()
    if out.ndim != 2:
        raise ValueError("basis must be 2-D")
    for col in range(out.shape[1]):
        v = out[:, col]
        idx = int(np.argmax(np.abs(v)))
        if v[idx] < 0.0:
            out[:, col] *= -1.0
    return out


def oracle_flux_basis(reference: ExactAngularReference, rank: int) -> np.ndarray:
    """Reference-only top-eigenvector basis of exact flux Gram."""
    width = reference.mean.shape[0]
    if rank < 0 or rank > width:
        raise ValueError("rank out of range")
    if rank == 0:
        return np.zeros((width, 0), dtype=np.float64)
    evals, evecs = np.linalg.eigh(reference.flux_gram)
    order = np.argsort(evals)[::-1]
    return canonicalize_basis_signs(evecs[:, order[:rank]])


def _projector_from_basis(basis: np.ndarray, width: int) -> tuple[np.ndarray, np.ndarray]:
    u = np.asarray(basis, dtype=np.float64)
    if u.ndim != 2 or u.shape[0] != width:
        raise ValueError(f"basis must have shape ({width},k)")
    gram = u.T @ u
    if u.shape[1] and np.max(np.abs(gram - np.eye(u.shape[1]))) > 1e-10:
        raise ValueError("basis columns must be orthonormal")
    p = u @ u.T
    q = np.eye(width, dtype=np.float64) - p
    return p, q


def projection_metrics(reference: ExactAngularReference, basis: np.ndarray) -> dict:
    """Exact output/flux bias, covariance and remainder for a supplied basis."""
    width = reference.mean.shape[0]
    p, q = _projector_from_basis(basis, width)
    mu = reference.mean
    cov = reference.covariance

    compressed_mean = p @ mu
    residual_mean = q @ mu
    bias = compressed_mean - mu

    compressed_cov = p @ cov @ p
    residual_cov = q @ cov @ q
    cross_cov = p @ cov @ q
    residual_second = residual_cov + np.outer(residual_mean, residual_mean)

    output_second_trace = float(np.trace(reference.second_moment))
    remainder_mse_total = float(np.trace(residual_second))
    relative_remainder = (
        remainder_mse_total / output_second_trace
        if output_second_trace > 0.0
        else 0.0
    )

    residual_flux_sum = q @ reference.flux_sum
    total_flux_energy = float(np.trace(reference.flux_gram))
    residual_flux_energy = float(np.trace(q @ reference.flux_gram @ q))
    relative_flux_energy = (
        residual_flux_energy / total_flux_energy
        if total_flux_energy > 0.0
        else 0.0
    )

    per_observable = []
    for j in range(width):
        per_observable.append(
            {
                "output": j,
                "exact_mean": float(mu[j]),
                "compressed_mean": float(compressed_mean[j]),
                "bias": float(bias[j]),
                "exact_variance": float(cov[j, j]),
                "residual_variance": float(residual_cov[j, j]),
                "residual_mse": float(residual_second[j, j]),
                "flux_mean_remainder": float(
                    reference.mean_radius * residual_flux_sum[j] / _TWO_PI
                ),
            }
        )

    return {
        "rank": int(np.asarray(basis).shape[1]),
        "projector": p,
        "residual_projector": q,
        "compressed_mean": compressed_mean,
        "residual_mean": residual_mean,
        "bias": bias,
        "bias_l2": float(np.linalg.norm(bias)),
        "bias_mse_across_outputs": float(np.mean(bias * bias)),
        "compressed_covariance": compressed_cov,
        "residual_covariance": residual_cov,
        "cross_covariance": cross_cov,
        "residual_second_moment": residual_second,
        "remainder_mse_total": remainder_mse_total,
        "relative_remainder_mse": relative_remainder,
        "flux_mean_remainder": residual_flux_sum,
        "flux_energy_total": total_flux_energy,
        "flux_energy_residual": residual_flux_energy,
        "relative_flux_energy_residual": relative_flux_energy,
        "per_observable": per_observable,
        "projector_symmetry_max_abs": float(np.max(np.abs(p - p.T))),
        "projector_idempotence_max_abs": float(np.max(np.abs(p @ p - p))),
    }


def observable_metrics(
    reference: ExactAngularReference,
    basis: np.ndarray,
    observable: np.ndarray,
) -> dict:
    """Exact scalar final-observable compression metrics for supplied c."""
    width = reference.mean.shape[0]
    c = np.asarray(observable, dtype=np.float64).reshape(-1)
    if c.shape != (width,):
        raise ValueError(f"observable must have shape ({width},)")
    p, q = _projector_from_basis(basis, width)
    mu = reference.mean
    cov = reference.covariance
    residual_mean = q @ mu
    residual_cov = q @ cov @ q
    bias = -float(c @ residual_mean)
    residual_variance = float(c @ residual_cov @ c)
    return {
        "exact_mean": float(c @ mu),
        "compressed_mean": float(c @ (p @ mu)),
        "bias": bias,
        "residual_variance": residual_variance,
        "residual_mse": residual_variance + bias * bias,
    }


def reference_numeric_arrays(reference: ExactAngularReference) -> list[np.ndarray]:
    """Flattened list used by deterministic replay checks."""
    arrays = [
        reference.mean,
        reference.second_moment,
        reference.covariance,
        reference.boundary_angles,
        reference.boundary_jumps,
        reference.flux_sum,
        reference.flux_gram,
        reference.flux_mean,
    ]
    for sector in reference.sectors:
        arrays.append(np.array([sector.lo, sector.hi], dtype=np.float64))
        arrays.append(sector.coeff)
    return arrays
