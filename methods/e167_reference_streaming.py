"""Streaming synthetic angular reference for E167.

Reference-only module. It never imports the AGO estimator.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class StreamingReference:
    angular_mean: np.ndarray
    batch_angular_means: np.ndarray
    sample_count: int
    batch_count: int
    batch_size: int
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


def _antithetic_batch(
    rng: np.random.Generator,
    n: int,
    batch_size: int,
) -> np.ndarray:
    if batch_size <= 0 or batch_size % 2:
        raise ValueError("batch_size must be positive and even")
    half = batch_size // 2
    z = rng.standard_normal((half, n))
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    z /= norms
    z *= math.sqrt(float(n))
    y = np.empty((batch_size, n), dtype=np.float64)
    y[0::2] = z
    y[1::2] = -z
    return y


def streaming_sphere_reference(
    weights: Sequence[np.ndarray],
    *,
    n: int,
    total_samples: int,
    batch_count: int,
    seed: int,
) -> StreamingReference:
    if total_samples % batch_count:
        raise ValueError("sample count must divide batch_count")
    batch_size = total_samples // batch_count
    if batch_size % 2:
        raise ValueError("each batch must preserve antithetic pairs")

    rng = np.random.Generator(np.random.PCG64(int(seed)))
    batch_means: list[np.ndarray] = []
    total_sum = np.zeros(n, dtype=np.float64)

    for _ in range(batch_count):
        y = _antithetic_batch(rng, n, batch_size)
        out = evaluate_network(y, weights)
        bsum = np.sum(out, axis=0, dtype=np.float64)
        total_sum += bsum
        batch_means.append(bsum / float(batch_size))

    batches = np.stack(batch_means, axis=0)
    mean = total_sum / float(total_samples)
    return StreamingReference(
        angular_mean=mean,
        batch_angular_means=batches,
        sample_count=int(total_samples),
        batch_count=int(batch_count),
        batch_size=int(batch_size),
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
    rays: int = 64,
) -> float:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    z = rng.standard_normal((rays, n))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    z *= math.sqrt(float(n))

    scale = np.exp(
        rng.uniform(math.log(0.2), math.log(3.0), size=rays)
    )
    lhs = evaluate_network(z * scale[:, None], weights)
    rhs = evaluate_network(z, weights) * scale[:, None]
    return float(
        np.linalg.norm(lhs - rhs)
        / max(float(np.linalg.norm(rhs)), 2.0**-500)
    )
