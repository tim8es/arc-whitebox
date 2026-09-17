from __future__ import annotations

import math
from typing import Sequence

import numpy as np

_SQRT_2PI = math.sqrt(2.0 * math.pi)


def generate_synthetic_mlp(*, seed: int, width: int, depth: int) -> list[np.ndarray]:
    """Deterministic He-initialized dense ReLU MLP weights."""
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / float(width))
    return [
        np.asarray(rng.standard_normal((width, width)), dtype=np.float64) * scale
        for _ in range(depth)
    ]


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / _SQRT_2PI


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    # np.erf is not guaranteed across NumPy builds; math.erf keeps this helper
    # dependency-free and deterministic for the small synthetic Stage-A shapes.
    flat = np.asarray(x, dtype=np.float64).ravel()
    vals = np.fromiter((0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat),
                       dtype=np.float64, count=flat.size)
    return vals.reshape(np.shape(x))


def covariance_state(weights: Sequence[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Covariance-propagation mean trajectory plus final post-ReLU covariance.

    This mirrors the canonical baseline algebra but uses float64 NumPy for the
    synthetic-only E095 falsifier.
    """
    if not weights:
        raise ValueError("weights must be non-empty")
    width = int(np.asarray(weights[0]).shape[0])
    mu = np.zeros(width, dtype=np.float64)
    cov = np.eye(width, dtype=np.float64)
    rows: list[np.ndarray] = []

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        if w.shape != (width, width):
            raise ValueError("all weights must be square and have common width")

        mu_pre = w @ mu
        cov_pre = w @ cov @ w.T
        cov_pre = 0.5 * (cov_pre + cov_pre.T)

        var_pre = np.maximum(np.diag(cov_pre), 1e-12)
        sigma_pre = np.sqrt(var_pre)
        alpha = mu_pre / sigma_pre
        phi = _normal_pdf(alpha)
        Phi = _normal_cdf(alpha)

        mu = mu_pre * Phi + sigma_pre * phi
        ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sigma_pre * phi
        var_post = np.maximum(ez2 - mu * mu, 0.0)

        gain = np.where(sigma_pre > 1e-12, Phi, 0.0)
        cov = np.outer(gain, gain) * cov_pre
        np.fill_diagonal(cov, var_post)
        cov = 0.5 * (cov + cov.T)
        rows.append(mu.copy())

    return np.stack(rows, axis=0), cov


def canonical_top_subspace(cov: np.ndarray, *, rank: int) -> np.ndarray:
    """Top-eigenvalue subspace with deterministic column ordering and signs."""
    a = np.asarray(cov, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("cov must be square")
    if not (1 <= rank <= a.shape[0]):
        raise ValueError("invalid rank")

    a = 0.5 * (a + a.T)
    evals, evecs = np.linalg.eigh(a)
    order = np.argsort(evals, kind="stable")[::-1][:rank]
    u = np.asarray(evecs[:, order], dtype=np.float64).copy()

    for j in range(u.shape[1]):
        pivot = int(np.argmax(np.abs(u[:, j])))
        if u[pivot, j] < 0.0:
            u[:, j] *= -1.0
    return u


def project_residual(base: np.ndarray, sample: np.ndarray, subspace: np.ndarray) -> np.ndarray:
    """Return base + U U^T(sample-base) without explicitly forming U U^T."""
    b = np.asarray(base, dtype=np.float64)
    s = np.asarray(sample, dtype=np.float64)
    u = np.asarray(subspace, dtype=np.float64)
    if b.shape != s.shape or b.ndim != 1:
        raise ValueError("base and sample must be equal-length vectors")
    if u.ndim != 2 or u.shape[0] != b.shape[0]:
        raise ValueError("subspace has incompatible shape")
    delta = s - b
    return b + u @ (u.T @ delta)


def antithetic_final_mean(
    weights: Sequence[np.ndarray], *, input_seed: int, samples: int
) -> np.ndarray:
    """Monte-Carlo final mean using exactly paired x,-x trajectories."""
    if samples <= 0 or samples % 2:
        raise ValueError("samples must be a positive even integer")
    if not weights:
        raise ValueError("weights must be non-empty")
    width = int(np.asarray(weights[0]).shape[0])
    rng = np.random.Generator(np.random.PCG64(input_seed))
    half = samples // 2
    x = np.asarray(rng.standard_normal((half, width)), dtype=np.float64)
    h = np.concatenate((x, -x), axis=0)

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        h = h @ w.T
        np.maximum(h, 0.0, out=h)

    return np.mean(h, axis=0, dtype=np.float64)
