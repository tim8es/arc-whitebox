"""Verifier-only target-free references for E164."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CircleReference:
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


def evaluate(samples: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(samples, dtype=np.float64)
    for raw in weights:
        w = np.asarray(raw, dtype=np.float64)
        h = np.maximum(h @ w.T, 0.0)
    return h


def _roots(row: np.ndarray, lo: float, hi: float) -> list[float]:
    a, b = map(float, row)
    if math.hypot(a, b) <= 1e-15:
        return []
    phase = math.atan2(b, a)
    zero0 = phase + 0.5 * math.pi
    k0 = math.floor((lo - zero0) / math.pi) - 1
    k1 = math.ceil((hi - zero0) / math.pi) + 1
    out: list[float] = []
    for k in range(k0, k1 + 1):
        z = zero0 + k * math.pi
        if lo + 1e-13 < z < hi - 1e-13:
            out.append(z)
    return out


def _int_y(lo: float, hi: float) -> np.ndarray:
    rt2 = math.sqrt(2.0)
    return rt2 * np.array(
        [
            math.sin(hi) - math.sin(lo),
            -math.cos(hi) + math.cos(lo),
        ],
        dtype=np.float64,
    )


def _int_yy(lo: float, hi: float) -> np.ndarray:
    d = hi - lo
    diag_shift = 0.5 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    off = 0.5 * (math.cos(2.0 * lo) - math.cos(2.0 * hi))
    return np.array(
        [
            [d + diag_shift, off],
            [off, d - diag_shift],
        ],
        dtype=np.float64,
    )


def _next_sectors(
    sectors: list[tuple[float, float, np.ndarray]],
    weight: np.ndarray,
) -> list[tuple[float, float, np.ndarray]]:
    w = np.asarray(weight, dtype=np.float64)
    out: list[tuple[float, float, np.ndarray]] = []

    for lo, hi, amap in sectors:
        premap = w @ amap
        cuts = [lo, hi]
        for row in premap:
            cuts.extend(_roots(row, lo, hi))
        cuts = sorted(set(round(x, 14) for x in cuts))

        for a, b in zip(cuts[:-1], cuts[1:]):
            if b - a <= 1e-13:
                continue
            mid = 0.5 * (a + b)
            ymid = math.sqrt(2.0) * np.array(
                [math.cos(mid), math.sin(mid)],
                dtype=np.float64,
            )
            active = (premap @ ymid) > 0.0
            out.append((a, b, active[:, None] * premap))

    return out


def exact_circle(weights: Sequence[np.ndarray]) -> CircleReference:
    if not weights:
        raise ValueError("weights required")
    if np.asarray(weights[0]).shape != (2, 2):
        raise ValueError("exact circle requires width 2")

    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]

    first_mean: np.ndarray | None = None
    first_cov: np.ndarray | None = None

    for layer_index, raw in enumerate(weights):
        sectors = _next_sectors(
            sectors,
            np.asarray(raw, dtype=np.float64),
        )

        if layer_index == 0:
            mean = np.zeros(2, dtype=np.float64)
            second = np.zeros((2, 2), dtype=np.float64)
            for lo, hi, amap in sectors:
                mean += amap @ _int_y(lo, hi)
                second += amap @ _int_yy(lo, hi) @ amap.T
            mean /= 2.0 * math.pi
            second /= 2.0 * math.pi
            first_mean = mean
            first_cov = second - mean[:, None] * mean[None, :]
            first_cov = 0.5 * (first_cov + first_cov.T)

    final_mean = np.zeros(2, dtype=np.float64)
    for lo, hi, amap in sectors:
        final_mean += amap @ _int_y(lo, hi)
    final_mean /= 2.0 * math.pi

    assert first_mean is not None
    assert first_cov is not None

    return CircleReference(
        final_angular_mean=final_mean,
        first_angular_mean=first_mean,
        first_angular_covariance=first_cov,
        sector_count=len(sectors),
        finite=bool(
            np.isfinite(final_mean).all()
            and np.isfinite(first_mean).all()
            and np.isfinite(first_cov).all()
        ),
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


def sphere_mean_reference(
    weights: Sequence[np.ndarray],
    *,
    samples: int,
    seed: int,
) -> SphereReference:
    n = int(np.asarray(weights[0]).shape[0])
    y = antithetic_sphere(n, samples, seed)
    final = evaluate(y, weights)
    mean = np.mean(final, axis=0, dtype=np.float64)

    if samples % 4:
        raise ValueError("samples must be divisible by 4")
    chunk = samples // 4
    batches = np.stack(
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
        batch_final_angular_means=batches,
        finite=bool(
            np.isfinite(mean).all()
            and np.isfinite(batches).all()
        ),
    )


def homogeneity_error(
    weights: Sequence[np.ndarray],
    *,
    n: int,
    seed: int,
    rays: int = 128,
) -> float:
    count = 2 * ((rays + 1) // 2)
    y = antithetic_sphere(n, count, seed)[:rays]
    rng = np.random.Generator(np.random.PCG64(int(seed) + 37))
    scale = np.exp(
        rng.uniform(math.log(0.2), math.log(3.0), size=rays)
    )
    left = evaluate(y * scale[:, None], weights)
    right = evaluate(y, weights) * scale[:, None]
    return float(
        np.linalg.norm(left - right)
        / max(float(np.linalg.norm(right)), 2.0**-500)
    )
