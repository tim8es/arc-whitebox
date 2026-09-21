"""Verifier-only dense K3 reference for E147 exact-small falsifier.

Independent from methods.e147_rap_k3.  It materializes full n^3 K3 tensors and
must only be invoked after the candidate trajectory has been frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


SIGMA_EPS = 2.0 ** -40


@dataclass(frozen=True)
class ExactLayer:
    k3: np.ndarray
    d3: np.ndarray
    d21: np.ndarray
    pre_k3: np.ndarray
    pre_mean: np.ndarray
    pre_var: np.ndarray
    mean: np.ndarray
    covariance: np.ndarray
    wick1: np.ndarray
    birth_k3: np.ndarray


@dataclass(frozen=True)
class ExactReference:
    layers: tuple[ExactLayer, ...]
    final_mean: np.ndarray
    finite: bool


def _pdf(a: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)


def _cdf(a: np.ndarray) -> np.ndarray:
    return np.array(
        [0.5 * (1.0 + math.erf(float(x) / math.sqrt(2.0))) for x in a],
        dtype=np.float64,
    )


def _relu_moments(
    mean: np.ndarray,
    var: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mu = np.asarray(mean, dtype=np.float64)
    vv = np.maximum(np.asarray(var, dtype=np.float64), SIGMA_EPS**2)
    sig = np.sqrt(vv)
    a = mu / sig
    phi = _pdf(a)
    Phi = _cdf(a)
    m1 = sig * phi + mu * Phi
    m2 = (mu * mu + vv) * Phi + mu * sig * phi
    m3 = (mu**3 + 3.0 * mu * vv) * Phi + (
        mu * mu * sig + 2.0 * sig**3
    ) * phi
    out_var = np.maximum(m2 - m1 * m1, SIGMA_EPS**2)
    k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1**3
    return m1, out_var, Phi, k3


def _linear_k3(k3: np.ndarray, w: np.ndarray) -> np.ndarray:
    if not np.any(k3):
        return np.zeros_like(k3)
    return np.einsum(
        "abc,ai,bj,ck->ijk",
        k3,
        w,
        w,
        w,
        optimize=True,
    )


def _d_slices(k3: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = k3.shape[0]
    idx = np.arange(n)
    d3 = k3[idx, idx, idx].copy()
    d21 = k3[idx, idx, :].copy()
    np.fill_diagonal(d21, 0.0)
    return d3, d21


def _edgeworth_mean(
    gaussian_mean: np.ndarray,
    pre_mean: np.ndarray,
    pre_var: np.ndarray,
    pre_d3: np.ndarray,
) -> np.ndarray:
    sig = np.sqrt(np.maximum(pre_var, SIGMA_EPS**2))
    a = pre_mean / sig
    coeff = -pre_mean * _pdf(a) / (6.0 * sig**3)
    return gaussian_mean + coeff * pre_d3


def build_exact_reference(weights: Sequence[np.ndarray]) -> ExactReference:
    if len(weights) != 8:
        raise ValueError("frozen exact-small depth is 8")
    n = int(np.asarray(weights[0]).shape[0])
    mu = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    k3 = np.zeros((n, n, n), dtype=np.float64)
    layers: list[ExactLayer] = []
    final_mean = np.zeros(n, dtype=np.float64)

    for l, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError(f"weight {l} shape {w.shape}, expected {(n, n)}")

        pre_mu = w.T @ mu
        pre_cov = w.T @ cov @ w
        pre_cov = 0.5 * (pre_cov + pre_cov.T)
        pre_var = np.maximum(np.diag(pre_cov), SIGMA_EPS**2)
        gaussian_mean, out_var, wick1, birth3 = _relu_moments(
            pre_mu, pre_var
        )

        pre_k3 = _linear_k3(k3, w)
        pre_d3, _ = _d_slices(pre_k3)
        if l == len(weights) - 1:
            final_mean = _edgeworth_mean(
                gaussian_mean, pre_mu, pre_var, pre_d3
            )

        scaled = (
            pre_k3
            * wick1[:, None, None]
            * wick1[None, :, None]
            * wick1[None, None, :]
        )
        idx = np.arange(n)
        scaled[idx, idx, idx] += birth3
        k3 = scaled

        d3, d21 = _d_slices(k3)
        cov_next = (wick1[:, None] * pre_cov) * wick1[None, :]
        np.fill_diagonal(cov_next, out_var)
        cov_next = 0.5 * (cov_next + cov_next.T)

        layers.append(
            ExactLayer(
                k3=k3.copy(),
                d3=d3,
                d21=d21,
                pre_k3=pre_k3.copy(),
                pre_mean=pre_mu.copy(),
                pre_var=pre_var.copy(),
                mean=gaussian_mean.copy(),
                covariance=cov_next.copy(),
                wick1=wick1.copy(),
                birth_k3=birth3.copy(),
            )
        )

        mu = gaussian_mean
        cov = cov_next

    finite = bool(
        np.isfinite(final_mean).all()
        and all(
            np.isfinite(x.k3).all()
            and np.isfinite(x.d3).all()
            and np.isfinite(x.d21).all()
            for x in layers
        )
    )
    return ExactReference(
        layers=tuple(layers),
        final_mean=final_mean,
        finite=finite,
    )
