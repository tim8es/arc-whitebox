"""Frozen E018 importance-sampling primitives.

These helpers are diagnostic-only. They do not alter the canonical estimator.
"""

from __future__ import annotations

import numpy as np

SAMPLE_COUNT = 384


def seed_for(dump_index: int, layer: int, source_index: int) -> int:
    """Return the preregistered deterministic seed for one old-source contraction."""
    return 18018 + 1000 * int(dump_index) + 32 * int(layer) + int(source_index)


def norm_optimal_probabilities(
    ap: np.ndarray,
    aa: np.ndarray,
    pp: np.ndarray,
) -> np.ndarray:
    """Probability proportional to stacked AP/AA/PP column Frobenius norm.

    The final axis is the contraction-row index j. No clipping or probability
    floor is applied. The all-zero case is exactly uniform because every row is
    equivalent under the frozen norm objective.
    """
    ap64 = np.asarray(ap, dtype=np.float64)
    aa64 = np.asarray(aa, dtype=np.float64)
    pp64 = np.asarray(pp, dtype=np.float64)
    if ap64.shape != aa64.shape or ap64.shape != pp64.shape:
        raise ValueError("AP/AA/PP must have identical shapes")
    if ap64.ndim < 1:
        raise ValueError("AP/AA/PP must have a contraction axis")
    axes = tuple(range(ap64.ndim - 1))
    energy = np.sum(ap64 * ap64 + aa64 * aa64 + pp64 * pp64, axis=axes)
    scores = np.sqrt(energy)
    total = float(np.sum(scores))
    n = scores.shape[0]
    if n == 0:
        raise ValueError("empty contraction axis")
    if total == 0.0:
        return np.full(n, 1.0 / n, dtype=np.float64)
    probabilities = scores / total
    if not np.all(np.isfinite(probabilities)):
        raise ValueError("non-finite importance probabilities")
    return probabilities


def importance_draws(
    probabilities: np.ndarray,
    *,
    sample_count: int = SAMPLE_COUNT,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw with replacement and return indices plus inverse-probability weights."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("probabilities must be a non-empty vector")
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if np.any(p < 0.0) or not np.isclose(float(p.sum()), 1.0):
        raise ValueError("probabilities must be nonnegative and sum to one")
    rng = np.random.default_rng(int(seed))
    indices = rng.choice(p.size, size=int(sample_count), replace=True, p=p)
    selected = p[indices]
    if np.any(selected <= 0.0):
        raise ValueError("sampled a zero-probability index")
    weights = 1.0 / (float(sample_count) * selected)
    return indices, weights


def importance_sampled_sum(
    terms: np.ndarray,
    probabilities: np.ndarray,
    *,
    sample_count: int = SAMPLE_COUNT,
    seed: int,
) -> np.ndarray:
    """Unbiased with-replacement estimate of ``sum_j terms[j]``."""
    x = np.asarray(terms)
    p = np.asarray(probabilities, dtype=np.float64)
    if x.shape[0] != p.size:
        raise ValueError("terms first axis must match probabilities")
    indices, weights = importance_draws(
        p, sample_count=sample_count, seed=seed
    )
    scale_shape = (sample_count,) + (1,) * (x.ndim - 1)
    return np.sum(x[indices] * weights.reshape(scale_shape), axis=0)
