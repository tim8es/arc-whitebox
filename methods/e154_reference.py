"""Verifier-only references for E154.

This file is independent of methods.e154_angular_radial_k4 and may only be
imported by the falsifier after the candidate has been frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class SphereReference:
    final_angular_mean: np.ndarray
    input_k4_diag: np.ndarray
    pre_k4_diag: tuple[np.ndarray, ...]
    batch_final_means: np.ndarray
    finite: bool


def network_eval(
    x: np.ndarray,
    weights: Sequence[np.ndarray],
) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for raw in weights:
        h = np.maximum(h @ np.asarray(raw, dtype=np.float64), 0.0)
    return h


def _zero_crossings_for_linear_form(
    coeff: np.ndarray,
    lo: float,
    hi: float,
) -> list[float]:
    a, b = map(float, coeff)
    if math.hypot(a, b) <= 1e-15:
        return []
    phi = math.atan2(b, a)
    base = phi + 0.5 * math.pi
    out: list[float] = []
    k0 = math.floor((lo - base) / math.pi) - 1
    k1 = math.ceil((hi - base) / math.pi) + 1
    for k in range(k0, k1 + 1):
        z = base + k * math.pi
        if lo + 1e-14 < z < hi - 1e-14:
            out.append(z)
    return out


def exact_circle_angular_mean(
    weights: Sequence[np.ndarray],
) -> tuple[np.ndarray, int]:
    if not weights:
        raise ValueError("weights required")
    if np.asarray(weights[0]).shape != (2, 2):
        raise ValueError("exact circle reference requires width 2")

    # On each sector h(theta) = Y(theta) @ A, where
    # Y(theta)=sqrt(2)[cos(theta),sin(theta)].
    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]

    for raw in weights:
        w = np.asarray(raw, dtype=np.float64)
        new: list[tuple[float, float, np.ndarray]] = []
        for lo, hi, amap in sectors:
            bmap = amap @ w
            cuts = [lo, hi]
            for j in range(2):
                cuts.extend(
                    _zero_crossings_for_linear_form(
                        bmap[:, j], lo, hi
                    )
                )
            cuts = sorted(set(round(x, 15) for x in cuts))
            for a, b in zip(cuts[:-1], cuts[1:]):
                if b - a <= 1e-14:
                    continue
                mid = 0.5 * (a + b)
                ray = np.array([math.cos(mid), math.sin(mid)])
                active = (ray @ bmap) > 0.0
                next_map = bmap * active[None, :]
                new.append((a, b, next_map))
        sectors = new

    total = np.zeros(2, dtype=np.float64)
    rt2 = math.sqrt(2.0)
    for lo, hi, amap in sectors:
        integ_ray = rt2 * np.array(
            [
                math.sin(hi) - math.sin(lo),
                -math.cos(hi) + math.cos(lo),
            ],
            dtype=np.float64,
        )
        total += integ_ray @ amap
    return total / (2.0 * math.pi), len(sectors)


def antithetic_sphere(
    n: int,
    samples: int,
    seed: int,
) -> np.ndarray:
    if samples % 2:
        raise ValueError("samples must be even")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    half = samples // 2
    raw = rng.standard_normal((half, n))
    raw /= np.linalg.norm(raw, axis=1, keepdims=True)
    raw *= math.sqrt(float(n))
    out = np.empty((samples, n), dtype=np.float64)
    out[0::2] = raw
    out[1::2] = -raw
    return out


def _k4_diag(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    mu = np.mean(a, axis=0, dtype=np.float64)
    c = a - mu
    v = np.mean(c * c, axis=0, dtype=np.float64)
    m4 = np.mean(c**4, axis=0, dtype=np.float64)
    return m4 - 3.0 * v * v


def sphere_reference(
    weights: Sequence[np.ndarray],
    *,
    samples: int,
    seed: int,
) -> SphereReference:
    n = int(np.asarray(weights[0]).shape[0])
    y = antithetic_sphere(n, samples, seed)
    input_k4 = _k4_diag(y)

    h = y
    pre_k4: list[np.ndarray] = []
    for raw in weights:
        pre = h @ np.asarray(raw, dtype=np.float64)
        pre_k4.append(_k4_diag(pre))
        h = np.maximum(pre, 0.0)

    final_mean = np.mean(h, axis=0, dtype=np.float64)
    if samples % 4:
        raise ValueError("samples must be divisible by four")
    chunk = samples // 4
    batch = np.stack(
        [
            np.mean(h[i * chunk:(i + 1) * chunk], axis=0, dtype=np.float64)
            for i in range(4)
        ],
        axis=0,
    )
    finite = bool(
        np.isfinite(final_mean).all()
        and np.isfinite(input_k4).all()
        and all(np.isfinite(x).all() for x in pre_k4)
        and np.isfinite(batch).all()
    )
    return SphereReference(
        final_angular_mean=final_mean,
        input_k4_diag=input_k4,
        pre_k4_diag=tuple(pre_k4),
        batch_final_means=batch,
        finite=finite,
    )


def homogeneity_relative_error(
    weights: Sequence[np.ndarray],
    *,
    n: int,
    seed: int,
    rays: int = 128,
) -> float:
    y = antithetic_sphere(n, 2 * ((rays + 1) // 2), seed)[:rays]
    rng = np.random.Generator(np.random.PCG64(int(seed) + 1))
    scales = np.exp(rng.uniform(math.log(0.2), math.log(3.0), size=rays))
    base = network_eval(y, weights)
    scaled = network_eval(y * scales[:, None], weights)
    rhs = base * scales[:, None]
    return float(
        np.linalg.norm(scaled - rhs)
        / max(float(np.linalg.norm(rhs)), 2.0**-500)
    )
