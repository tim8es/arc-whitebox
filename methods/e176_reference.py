"""E176 reference-only streaming angular Monte Carlo.

This module never imports the E176 estimator.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

@dataclass(frozen=True)
class ReferenceResult:
    final_mean: np.ndarray
    batch_final_means: np.ndarray
    coordinate_se: np.ndarray
    sample_count: int
    batch_count: int
    batch_size: int
    finite: bool

def _antithetic_batch(
    rng: np.random.Generator,
    *,
    n: int,
    batch_size: int,
) -> np.ndarray:
    if batch_size <= 0 or batch_size % 2:
        raise ValueError("batch_size must be positive and even")
    half = batch_size // 2
    z = rng.standard_normal((half, n))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    z *= math.sqrt(float(n))
    out = np.empty((batch_size, n), dtype=np.float64)
    out[0::2] = z
    out[1::2] = -z
    return out

def evaluate(samples: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(samples, dtype=np.float64)
    for w in weights:
        h = np.maximum(h @ np.asarray(w, dtype=np.float64).T, 0.0)
    return h

def radial_a1(n: int) -> float:
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )

def streaming_reference(
    weights: Sequence[np.ndarray],
    *,
    n: int,
    total_samples: int,
    batch_count: int,
    seed: int,
) -> ReferenceResult:
    if total_samples % batch_count:
        raise ValueError("total_samples must divide batch_count")
    batch_size = total_samples // batch_count
    if batch_size % 2:
        raise ValueError("batch size must preserve antithetic pairs")

    rng = np.random.Generator(np.random.PCG64(int(seed)))
    a1 = radial_a1(n)
    batches = []
    total = np.zeros(n, dtype=np.float64)

    for _ in range(batch_count):
        x = _antithetic_batch(rng, n=n, batch_size=batch_size)
        y = evaluate(x, weights)
        b = np.mean(y, axis=0, dtype=np.float64) * a1
        batches.append(b)
        total += b

    batch_final_means = np.stack(batches, axis=0)
    final_mean = total / float(batch_count)
    coordinate_se = (
        np.std(batch_final_means, axis=0, ddof=1)
        / math.sqrt(float(batch_count))
    )
    return ReferenceResult(
        final_mean=final_mean,
        batch_final_means=batch_final_means,
        coordinate_se=coordinate_se,
        sample_count=int(total_samples),
        batch_count=int(batch_count),
        batch_size=int(batch_size),
        finite=bool(
            np.isfinite(final_mean).all()
            and np.isfinite(batch_final_means).all()
            and np.isfinite(coordinate_se).all()
        ),
    )
