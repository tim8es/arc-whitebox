"""E154 clean-room angular-radial K4 candidate.

No E151 dependency. No exact-reference dependency. No public data dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
PROD_N = 1024
PROD_DEPTH = 16
STRASSEN_LEVELS = 0
EPS = 1.0e-12


@dataclass(frozen=True)
class ClosureLayer:
    pre_mean: np.ndarray
    pre_covariance: np.ndarray
    pre_variance: np.ndarray
    pre_k4_diag: np.ndarray
    mean: np.ndarray
    covariance: np.ndarray


@dataclass(frozen=True)
class ClosureEstimate:
    angular_mean: np.ndarray
    gaussian_mean: np.ndarray
    layers: tuple[ClosureLayer, ...]
    finite: bool
    production_cost: dict


def radial_a1(n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )


def radial_moment_factors(n: int) -> tuple[float, float, float, float]:
    a1 = radial_a1(n)
    return (
        a1,
        1.0,
        ((n + 1.0) / n) * a1,
        (n + 2.0) / n,
    )


def gaussian_from_angular_k4(
    angular_raw_moments: tuple[float, float, float, float],
    n: int,
) -> float:
    m1, m2, m3, m4 = map(float, angular_raw_moments)
    a1, a2, a3, a4 = radial_moment_factors(n)
    return (
        a4 * m4
        - 4.0 * a1 * a3 * m1 * m3
        - 3.0 * a2 * a2 * m2 * m2
        + 12.0 * a1 * a1 * a2 * m1 * m1 * m2
        - 6.0 * a1**4 * m1**4
    )


def sphere_input_k4_diag(n: int) -> float:
    return -6.0 / (n + 2.0)


def sphere_linear_k4_diag(variance: np.ndarray, n: int) -> np.ndarray:
    v = np.asarray(variance, dtype=np.float64)
    return -6.0 * v * v / (n + 2.0)


def sphere_linear_k31(covariance: np.ndarray, n: int) -> np.ndarray:
    c = np.asarray(covariance, dtype=np.float64)
    d = np.diag(c)
    return -6.0 * d[:, None] * c / (n + 2.0)


def sphere_linear_k22(covariance: np.ndarray, n: int) -> np.ndarray:
    c = np.asarray(covariance, dtype=np.float64)
    d = np.diag(c)
    return -2.0 * (
        d[:, None] * d[None, :] + 2.0 * c * c
    ) / (n + 2.0)


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in a],
        dtype=np.float64,
    )


def _gaussian_relu_raw12(
    mean: np.ndarray,
    variance: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mu = np.asarray(mean, dtype=np.float64)
    var = np.maximum(np.asarray(variance, dtype=np.float64), EPS)
    sigma = np.sqrt(var)
    alpha = mu / sigma
    phi = _normal_pdf(alpha)
    Phi = _normal_cdf(alpha)
    g1 = sigma * phi + mu * Phi
    g2 = (mu * mu + var) * Phi + mu * sigma * phi
    return g1, g2, alpha, phi, Phi


def _step(
    mean: np.ndarray,
    covariance: np.ndarray,
    weight: np.ndarray,
    *,
    use_k4: bool,
    angular_dimension: int,
) -> ClosureLayer:
    w = np.asarray(weight, dtype=np.float64)
    mu = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(covariance, dtype=np.float64)

    pre_mean = w.T @ mu
    pre_cov = w.T @ cov @ w
    pre_cov = 0.5 * (pre_cov + pre_cov.T)
    pre_var = np.maximum(np.diag(pre_cov), EPS)

    g1, g2, alpha, phi, Phi = _gaussian_relu_raw12(
        pre_mean, pre_var
    )

    k4 = sphere_linear_k4_diag(pre_var, angular_dimension)

    if use_k4:
        sigma = np.sqrt(pre_var)
        wick4_relu = ((alpha * alpha - 1.0) * phi) / (sigma**3)
        wick4_relu2 = -2.0 * alpha * phi / pre_var
        out_mean = g1 + (k4 * wick4_relu) / 24.0
        out_raw2 = g2 + (k4 * wick4_relu2) / 24.0
    else:
        out_mean = g1
        out_raw2 = g2

    out_var = np.maximum(out_raw2 - out_mean * out_mean, EPS)
    out_cov = (Phi[:, None] * pre_cov) * Phi[None, :]
    np.fill_diagonal(out_cov, out_var)
    out_cov = 0.5 * (out_cov + out_cov.T)

    return ClosureLayer(
        pre_mean=pre_mean.copy(),
        pre_covariance=pre_cov.copy(),
        pre_variance=pre_var.copy(),
        pre_k4_diag=k4.copy(),
        mean=out_mean.copy(),
        covariance=out_cov.copy(),
    )


def angular_closure(
    weights: Sequence[np.ndarray],
    *,
    use_k4: bool,
) -> ClosureEstimate:
    if not weights:
        raise ValueError("weights required")
    n = int(np.asarray(weights[0]).shape[0])
    mean = np.zeros(n, dtype=np.float64)
    covariance = np.eye(n, dtype=np.float64)
    layers: list[ClosureLayer] = []

    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError(f"weight {idx} has shape {w.shape}")
        layer = _step(
            mean,
            covariance,
            w,
            use_k4=use_k4,
            angular_dimension=n,
        )
        layers.append(layer)
        mean = layer.mean
        covariance = layer.covariance

    a1 = radial_a1(n)
    gaussian_mean = a1 * mean
    finite = bool(
        np.isfinite(gaussian_mean).all()
        and all(
            np.isfinite(x.pre_mean).all()
            and np.isfinite(x.pre_covariance).all()
            and np.isfinite(x.pre_k4_diag).all()
            and np.isfinite(x.mean).all()
            and np.isfinite(x.covariance).all()
            for x in layers
        )
    )
    return ClosureEstimate(
        angular_mean=mean.copy(),
        gaussian_mean=gaussian_mean.copy(),
        layers=tuple(layers),
        finite=finite,
        production_cost=production_cost_receipt(),
    )


def production_cost_receipt() -> dict:
    n = PROD_N
    L = PROD_DEPTH
    parts = {
        "covariance_classical_two_gemm": L * 4 * n**3,
        "mean_matvec": L * 2 * n**2,
        "relu_covariance_update": L * 16 * n**2,
        "k4_diagonal_and_wick": L * 512 * n,
        "radial_scalar_helpers": L * 128 * n,
        "helper_accounting_reserve": 20 * (2 * n**3),
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - total,
        "strassen_levels": STRASSEN_LEVELS,
        "formula_matches_frozen_total": total == 111_981_625_344,
        "passes_cap": total <= CAP_FLOPS,
    }
