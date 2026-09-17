"""Frozen E091 production-shape exact-ground-truth synthetic family.

The family is fixed by ``research/E091_PRODUCTION_SHAPE_EXACT_FAMILY_FREEZE.json``.
It is intentionally benchmark-free.  The first dense layer may have signed weights; every
later dense matrix is elementwise nonnegative.  With zero biases, the first preactivation is
Gaussian under X~N(0,I), and after the first ReLU all subsequent ReLUs are identities.
Therefore every layer mean is available exactly without Monte Carlo.
"""

from __future__ import annotations

import math

import numpy as np

FROZEN_SUFFIX_SIGMA = 0.35
FROZEN_SUFFIX_GAIN = 0.97
FROZEN_RIDGE_LAMBDA = 1.0


def generate_exact_family_weights(
    seed: int,
    width: int = 1024,
    depth: int = 16,
) -> list[np.ndarray]:
    """Generate one deterministic dense production-shape member of the frozen family."""
    n = int(width)
    d = int(depth)
    if n <= 0 or d <= 0:
        raise ValueError("width and depth must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights: list[np.ndarray] = [
        rng.normal(0.0, 1.0 / math.sqrt(n), size=(n, n)).astype(np.float32)
    ]
    # exp(N(-sigma^2/2,sigma^2)) has mean one.  Dividing by n and multiplying
    # by the frozen gain gives expected column sum ~= gain while keeping all
    # post-first-layer weights nonnegative.
    log_mu = -0.5 * FROZEN_SUFFIX_SIGMA * FROZEN_SUFFIX_SIGMA
    for _ in range(1, d):
        raw = rng.normal(log_mu, FROZEN_SUFFIX_SIGMA, size=(n, n))
        w = (FROZEN_SUFFIX_GAIN / n) * np.exp(raw)
        weights.append(w.astype(np.float32))
    return weights


def exact_layer_means(weights: list[np.ndarray]) -> np.ndarray:
    """Return exact layer means for X~N(0,I) for the frozen nonnegative-suffix family."""
    if not weights:
        raise ValueError("weights must be non-empty")
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2 or first.shape[0] != first.shape[1]:
        raise ValueError("weights must be square dense matrices")
    width = first.shape[0]
    for w in weights[1:]:
        a = np.asarray(w)
        if a.shape != (width, width):
            raise ValueError("all weights must have common square shape")
        if np.any(a < 0.0):
            raise ValueError("all suffix weights must be elementwise nonnegative")

    mu = np.sqrt(np.sum(first * first, axis=0)) / math.sqrt(2.0 * math.pi)
    rows = [mu.copy()]
    for w in weights[1:]:
        mu = mu @ np.asarray(w, dtype=np.float64)
        rows.append(mu.copy())
    out = np.stack(rows, axis=0)
    if not np.isfinite(out).all():
        raise FloatingPointError("non-finite exact mean")
    return out


def fit_shared_ridge(X: np.ndarray, z: np.ndarray, lam: float = FROZEN_RIDGE_LAMBDA) -> np.ndarray:
    """Fit the frozen single shared ridge vector; calibration is network-disjoint offline work."""
    design = np.asarray(X, dtype=np.float64)
    target = np.asarray(z, dtype=np.float64)
    if design.ndim != 2 or target.ndim != 1 or design.shape[0] != target.shape[0]:
        raise ValueError("expected X=(N,p), z=(N,)")
    if not np.isfinite(design).all() or not np.isfinite(target).all():
        raise FloatingPointError("non-finite ridge input")
    reg = float(lam)
    if reg <= 0.0:
        raise ValueError("lambda must be positive")
    p = design.shape[1]
    A = design.T @ design + reg * np.eye(p, dtype=np.float64)
    rhs = design.T @ target
    beta = np.linalg.solve(A, rhs)
    if not np.isfinite(beta).all():
        raise FloatingPointError("non-finite ridge coefficient")
    return beta
