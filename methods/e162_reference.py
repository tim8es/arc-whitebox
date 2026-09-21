"""E162 verifier-only synthetic references.

This module is imported only after parent/AGO trajectories are frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class ExactCircleReference:
    final_angular_mean: np.ndarray
    first_angular_mean: np.ndarray
    first_angular_covariance: np.ndarray
    sector_count: int
    finite: bool


@dataclass(frozen=True)
class SphereReference:
    final_angular_mean: np.ndarray
    batch_final_angular_means: np.ndarray
    finite: bool


def evaluate_network(
    samples: np.ndarray,
    weights: Sequence[np.ndarray],
) -> np.ndarray:
    h = np.asarray(samples, dtype=np.float64)
    for raw in weights:
        w = np.asarray(raw, dtype=np.float64)
        h = np.maximum(h @ w.T, 0.0)
    return h


def _canonical_roots(
    row: np.ndarray,
    lo: float,
    hi: float,
) -> list[float]:
    a, b = map(float, row)
    if math.hypot(a, b) <= 1e-15:
        return []
    phase = math.atan2(b, a)
    first = phase + 0.5 * math.pi
    k0 = math.floor((lo - first) / math.pi) - 1
    k1 = math.ceil((hi - first) / math.pi) + 1
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        x = first + k * math.pi
        if lo + 1e-13 < x < hi - 1e-13:
            roots.append(x)
    return roots


def _integral_y(lo: float, hi: float) -> np.ndarray:
    rt2 = math.sqrt(2.0)
    return rt2 * np.array(
        [
            math.sin(hi) - math.sin(lo),
            -math.cos(hi) + math.cos(lo),
        ],
        dtype=np.float64,
    )


def _integral_yy(lo: float, hi: float) -> np.ndarray:
    d = hi - lo
    s2 = 0.5 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    c2 = 0.5 * (math.cos(2.0 * lo) - math.cos(2.0 * hi))
    return np.array(
        [
            [d + s2, c2],
            [c2, d - s2],
        ],
        dtype=np.float64,
    )


def _advance_sectors(
    sectors: list[tuple[float, float, np.ndarray]],
    weight: np.ndarray,
) -> list[tuple[float, float, np.ndarray]]:
    w = np.asarray(weight, dtype=np.float64)
    out: list[tuple[float, float, np.ndarray]] = []
    for lo, hi, amap in sectors:
        pre_map = w @ amap
        cuts = [lo, hi]
        for row in pre_map:
            cuts.extend(_canonical_roots(row, lo, hi))
        cuts = sorted(set(round(x, 14) for x in cuts))
        for a, b in zip(cuts[:-1], cuts[1:]):
            if b - a <= 1e-13:
                continue
            mid = 0.5 * (a + b)
            ymid = math.sqrt(2.0) * np.array(
                [math.cos(mid), math.sin(mid)],
                dtype=np.float64,
            )
            active = (pre_map @ ymid) > 0.0
            next_map = active[:, None] * pre_map
            out.append((a, b, next_map))
    return out


def exact_circle_reference(
    weights: Sequence[np.ndarray],
) -> ExactCircleReference:
    if not weights:
        raise ValueError("weights required")
    if np.asarray(weights[0]).shape != (2, 2):
        raise ValueError("exact circle reference requires width 2")

    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]

    first_mean = None
    first_cov = None

    for layer_idx, raw in enumerate(weights):
        sectors = _advance_sectors(
            sectors,
            np.asarray(raw, dtype=np.float64),
        )
        if layer_idx == 0:
            m = np.zeros(2, dtype=np.float64)
            second = np.zeros((2, 2), dtype=np.float64)
            for lo, hi, amap in sectors:
                m += amap @ _integral_y(lo, hi)
                second += amap @ _integral_yy(lo, hi) @ amap.T
            m /= 2.0 * math.pi
            second /= 2.0 * math.pi
            first_mean = m
            first_cov = second - m[:, None] * m[None, :]
            first_cov = 0.5 * (first_cov + first_cov.T)

    final_mean = np.zeros(2, dtype=np.float64)
    for lo, hi, amap in sectors:
        final_mean += amap @ _integral_y(lo, hi)
    final_mean /= 2.0 * math.pi

    assert first_mean is not None
    assert first_cov is not None
    finite = bool(
        np.isfinite(final_mean).all()
        and np.isfinite(first_mean).all()
        and np.isfinite(first_cov).all()
    )
    return ExactCircleReference(
        final_angular_mean=final_mean,
        first_angular_mean=first_mean,
        first_angular_covariance=first_cov,
        sector_count=len(sectors),
        finite=finite,
    )


def antithetic_sphere(
    n: int,
    samples: int,
    seed: int,
) -> np.ndarray:
    if samples <= 0 or samples % 2:
        raise ValueError("samples must be positive and even")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    half = samples // 2
    z = rng.standard_normal((half, n))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    z *= math.sqrt(float(n))
    out = np.empty((samples, n), dtype=np.float64)
    out[0::2] = z
    out[1::2] = -z
    return out


def sphere_reference(
    weights: Sequence[np.ndarray],
    *,
    samples: int,
    seed: int,
) -> SphereReference:
    n = int(np.asarray(weights[0]).shape[0])
    y = antithetic_sphere(n, samples, seed)
    final = evaluate_network(y, weights)
    mean = np.mean(final, axis=0, dtype=np.float64)

    if samples % 4:
        raise ValueError("samples must be divisible by 4")
    chunk = samples // 4
    batch = np.stack(
        [
            np.mean(
                final[i * chunk:(i + 1) * chunk],
                axis=0,
                dtype=np.float64,
            )
            for i in range(4)
        ],
        axis=0,
    )
    return SphereReference(
        final_angular_mean=mean,
        batch_final_angular_means=batch,
        finite=bool(
            np.isfinite(mean).all()
            and np.isfinite(batch).all()
        ),
    )


def homogeneity_relative_error(
    weights: Sequence[np.ndarray],
    *,
    n: int,
    seed: int,
    rays: int = 128,
) -> float:
    sample_count = 2 * ((rays + 1) // 2)
    y = antithetic_sphere(n, sample_count, seed)[:rays]
    rng = np.random.Generator(np.random.PCG64(int(seed) + 17))
    scale = np.exp(
        rng.uniform(math.log(0.2), math.log(3.0), size=rays)
    )
    left = evaluate_network(y * scale[:, None], weights)
    right = evaluate_network(y, weights) * scale[:, None]
    return float(
        np.linalg.norm(left - right)
        / max(float(np.linalg.norm(right)), 2.0**-500)
    )
