from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.special import ndtr


@dataclass(frozen=True)
class ReLULatentState:
    mean: np.ndarray
    exact_variance: np.ndarray
    factor: np.ndarray
    diag_residual: np.ndarray
    gram_eigenvalues: np.ndarray


def nystrom_from_covariance(xp, covariance, rank: int):
    n = int(covariance.shape[0])
    if covariance.shape != (n, n):
        raise ValueError("covariance must be square")
    if rank <= 0 or rank > n:
        raise ValueError("invalid rank")
    y = covariance[:, :rank]
    g = (covariance[:rank, :rank] + covariance[:rank, :rank].T) * 0.5
    evals, evecs = xp.linalg.eigh(g)
    if np.any(np.asarray(evals) <= 0) or not np.isfinite(np.asarray(evals)).all():
        raise ValueError("non-positive Nyström Gram eigenvalue")
    factor = y @ (evecs / xp.sqrt(evals)[None, :])
    return factor, evals


def _relu_marginals_numpy(mean: np.ndarray, variance: np.ndarray):
    sigma = np.sqrt(variance)
    alpha = mean / sigma
    phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    Phi = ndtr(alpha)
    relu_mean = sigma * phi + mean * Phi
    second = (variance + mean * mean) * Phi + mean * sigma * phi
    relu_var = second - relu_mean * relu_mean
    return relu_mean, relu_var


def post_relu_latent_update_numpy(
    mean: np.ndarray,
    diag_residual: np.ndarray,
    factor: np.ndarray,
    rank: int,
) -> ReLULatentState:
    mean = np.asarray(mean, dtype=np.float64)
    d = np.asarray(diag_residual, dtype=np.float64)
    u = np.asarray(factor, dtype=np.float64)
    n = int(mean.shape[0])
    if d.shape != (n,) or u.shape != (n, rank):
        raise ValueError("state shape mismatch")
    if np.any(d <= 0):
        raise ValueError("conditional diagonal variance must be positive")

    marginal_var = d + np.sum(u * u, axis=1)
    relu_mean, relu_var = _relu_marginals_numpy(mean, marginal_var)

    scale = math.sqrt(float(rank))
    loc = np.concatenate(
        [mean[None, :] + scale * u.T, mean[None, :] - scale * u.T], axis=0
    )
    sigma_eps = np.sqrt(d)[None, :]
    alpha = loc / sigma_eps
    phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    Phi = ndtr(alpha)
    conditional_mean = sigma_eps * phi + loc * Phi
    centered = (conditional_mean - np.mean(conditional_mean, axis=0, keepdims=True)) / math.sqrt(
        2.0 * float(rank)
    )

    gram = (centered @ centered.T + (centered @ centered.T).T) * 0.5
    evals, evecs = np.linalg.eigh(gram)
    order = np.argsort(evals)[-rank:]
    factor_out = centered.T @ evecs[:, order]
    d_out = relu_var - np.sum(factor_out * factor_out, axis=1)
    if np.min(d_out) < -1e-10:
        raise ValueError("negative post-ReLU diagonal residual")

    return ReLULatentState(
        mean=relu_mean,
        exact_variance=relu_var,
        factor=factor_out,
        diag_residual=d_out,
        gram_eigenvalues=evals[order],
    )
