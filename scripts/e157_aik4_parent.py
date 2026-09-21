"""E157 frozen clean-room angular K2 parent arithmetic.

No benchmark imports. No K4 state. No Strassen. This module is deterministic
numpy-only arithmetic used by the E157 target-free falsifier.
"""
from __future__ import annotations

import math
import numpy as np


def radial_a1(n: int) -> float:
    # Stable exact chi-ratio through lgamma.
    return math.sqrt(2.0 / n) * math.exp(
        math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0)
    )


def relu_wick(mean: np.ndarray, var: np.ndarray, k: int, p: int) -> np.ndarray:
    """ARC ReLU Wick coefficient convention E[d^k ReLU(Z)^p]."""
    var = np.maximum(var, 1e-300)
    sigma = np.sqrt(var)
    alpha = mean / sigma
    phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    cdf = 0.5 * np.vectorize(math.erfc)(-alpha / math.sqrt(2.0))

    if p == 1:
        if k == 0:
            return sigma * phi + mean * cdf
        if k == 1:
            return cdf
        if k == 2:
            return phi / sigma
        if k == 3:
            return -alpha * phi / (sigma**2)
        if k == 4:
            return (alpha**2 - 1.0) * phi / (sigma**3)
    elif p == 2:
        if k == 0:
            return (mean**2 + var) * cdf + mean * sigma * phi
        if k == 1:
            return 2.0 * (sigma * phi + mean * cdf)
        if k == 2:
            return 2.0 * cdf
        if k == 3:
            return 2.0 * phi / sigma
        if k == 4:
            return -2.0 * alpha * phi / (sigma**2)
    elif p == 3:
        if k == 0:
            return sigma**3 * (
                (2.0 + alpha**2) * phi
                + (3.0 * alpha + alpha**3) * cdf
            )
        if k == 1:
            return 3.0 * sigma**2 * (
                alpha * phi + (1.0 + alpha**2) * cdf
            )
        if k == 2:
            return 6.0 * (sigma * phi + mean * cdf)
        if k == 3:
            return 6.0 * cdf
        if k == 4:
            return 6.0 * phi / sigma
    elif p == 4:
        if k == 0:
            return sigma**4 * (
                (5.0 * alpha + alpha**3) * phi
                + (3.0 + 6.0 * alpha**2 + alpha**4) * cdf
            )
        if k == 1:
            return 4.0 * sigma**3 * (
                (2.0 + alpha**2) * phi
                + (3.0 * alpha + alpha**3) * cdf
            )
        if k == 2:
            return 12.0 * sigma**2 * (
                alpha * phi + (1.0 + alpha**2) * cdf
            )
        if k == 3:
            return 24.0 * (sigma * phi + mean * cdf)
        if k == 4:
            return 24.0 * cdf
    raise ValueError((k, p))


def _zero_diag(a: np.ndarray) -> np.ndarray:
    out = np.array(a, dtype=np.float64, copy=True)
    np.fill_diagonal(out, 0.0)
    return out


def k2_relu_step(
    mean: np.ndarray,
    cov: np.ndarray,
    *,
    d4: np.ndarray | None = None,
    d22: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Frozen K2 nonlinear arithmetic.

    d4/d22 are permitted only for the E157 first-birth overlay. The parent
    always calls this function with both None.
    """
    var = np.diag(cov)
    w01 = relu_wick(mean, var, 0, 1)
    w02 = relu_wick(mean, var, 0, 2)
    w11 = relu_wick(mean, var, 1, 1)
    w21 = relu_wick(mean, var, 2, 1)

    p1 = w01.copy()
    p2 = w02.copy()
    if d4 is not None:
        p1 = p1 + relu_wick(mean, var, 4, 1) * d4 / 24.0
        p2 = p2 + relu_wick(mean, var, 4, 2) * d4 / 24.0

    off = _zero_diag(cov)
    cross = (
        off * (w11[:, None] * w11[None, :])
        + 0.5 * (off * off) * (w21[:, None] * w21[None, :])
    )
    if d22 is not None:
        cross = cross + 0.25 * d22 * (w21[:, None] * w21[None, :])

    out_mean = p1
    out_var = p2 - p1 * p1
    out_cov = 0.5 * (cross + cross.T)
    np.fill_diagonal(out_cov, out_var)
    return out_mean, out_cov


def parent_predict_angular(weights: list[np.ndarray]) -> np.ndarray:
    """Angular K2 parent. No K4/c4 state exists anywhere."""
    n = int(weights[0].shape[1])
    mean = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    for w in weights:
        mean = w @ mean
        cov = w @ cov @ w.T
        cov = 0.5 * (cov + cov.T)
        mean, cov = k2_relu_step(mean, cov)
    return radial_a1(n) * mean


def production_parent_cost_upper(n: int = 1024, depth: int = 16) -> int:
    """Frozen complete conservative production upper bound.

    Per layer allowance:
      4*n^3 : covariance sandwich;
      200*n^2 + 1000*n : mean matvec, Wick functions, cross-covariance
                         elementwise work, symmetrization, radial bookkeeping.
    One extra 2*n^3 allowance explicitly covers ownership/materialization of the
    first-layer M=W0 W0^T even though it is the same preactivation covariance.
    """
    return int((4 * depth + 2) * n**3 + 200 * depth * n**2 + 1000 * depth * n)


def production_overlay_cost_upper(n: int = 1024) -> int:
    return int(20 * n**2 + 100 * n)
