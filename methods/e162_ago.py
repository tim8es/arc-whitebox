"""E162 clean-room Gaussian K2 parent and Angular Gauge Only candidate."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
PROD_N = 1024
PROD_DEPTH = 16
EPS = 1.0e-12


@dataclass(frozen=True)
class LayerState:
    mean: np.ndarray
    covariance: np.ndarray
    pre_mean: np.ndarray
    pre_covariance: np.ndarray


@dataclass(frozen=True)
class Estimate:
    final_mean: np.ndarray
    layers: tuple[LayerState, ...]
    first_gaussian_mean: np.ndarray
    first_gaussian_covariance: np.ndarray
    first_angular_mean: np.ndarray | None
    first_angular_covariance: np.ndarray | None
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


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in a],
        dtype=np.float64,
    )


def _relu_k2_step(
    mean: np.ndarray,
    covariance: np.ndarray,
    weight: np.ndarray,
) -> LayerState:
    mu = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(covariance, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)

    pre_mean = w @ mu
    pre_cov = w @ cov @ w.T
    pre_cov = 0.5 * (pre_cov + pre_cov.T)

    var = np.maximum(np.diag(pre_cov), EPS)
    sigma = np.sqrt(var)
    alpha = pre_mean / sigma
    phi = _normal_pdf(alpha)
    Phi = _normal_cdf(alpha)

    p1 = sigma * phi + pre_mean * Phi
    p2 = (pre_mean * pre_mean + var) * Phi + pre_mean * sigma * phi

    cov11 = pre_cov.copy()
    np.fill_diagonal(cov11, 0.0)
    w1 = Phi
    w2 = phi / sigma

    out_cov = (
        cov11 * (w1[:, None] * w1[None, :])
        + 0.5 * (cov11 * cov11) * (w2[:, None] * w2[None, :])
    )
    out_var = np.maximum(p2 - p1 * p1, EPS)
    np.fill_diagonal(out_cov, out_var)
    out_cov = 0.5 * (out_cov + out_cov.T)

    return LayerState(
        mean=p1.copy(),
        covariance=out_cov.copy(),
        pre_mean=pre_mean.copy(),
        pre_covariance=pre_cov.copy(),
    )


def gaussian_to_angular_state(
    mean_gaussian: np.ndarray,
    covariance_gaussian: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    mg = np.asarray(mean_gaussian, dtype=np.float64)
    cg = np.asarray(covariance_gaussian, dtype=np.float64)
    ma = mg / a1
    ca = cg - (1.0 / (a1 * a1) - 1.0) * (
        mg[:, None] * mg[None, :]
    )
    ca = 0.5 * (ca + ca.T)
    return ma, ca


def angular_to_gaussian_state(
    mean_angular: np.ndarray,
    covariance_angular: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    ma = np.asarray(mean_angular, dtype=np.float64)
    ca = np.asarray(covariance_angular, dtype=np.float64)
    mg = a1 * ma
    cg = ca + (1.0 - a1 * a1) * (ma[:, None] * ma[None, :])
    cg = 0.5 * (cg + cg.T)
    return mg, cg


def _estimate(
    weights: Sequence[np.ndarray],
    *,
    angular_gauge: bool,
) -> Estimate:
    if not weights:
        raise ValueError("weights required")
    n = int(np.asarray(weights[0]).shape[0])
    mean = np.zeros(n, dtype=np.float64)
    covariance = np.eye(n, dtype=np.float64)

    layers: list[LayerState] = []
    first_g_mean: np.ndarray | None = None
    first_g_cov: np.ndarray | None = None
    first_a_mean: np.ndarray | None = None
    first_a_cov: np.ndarray | None = None

    for layer_idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError(
                f"weight {layer_idx} shape {w.shape}, expected {(n, n)}"
            )

        state = _relu_k2_step(mean, covariance, w)

        if layer_idx == 0:
            first_g_mean = state.mean.copy()
            first_g_cov = state.covariance.copy()
            if angular_gauge:
                mean, covariance = gaussian_to_angular_state(
                    state.mean, state.covariance, n
                )
                first_a_mean = mean.copy()
                first_a_cov = covariance.copy()
                state = LayerState(
                    mean=mean.copy(),
                    covariance=covariance.copy(),
                    pre_mean=state.pre_mean,
                    pre_covariance=state.pre_covariance,
                )
            else:
                mean = state.mean
                covariance = state.covariance
        else:
            mean = state.mean
            covariance = state.covariance

        layers.append(state)

    assert first_g_mean is not None
    assert first_g_cov is not None

    final_mean = (
        radial_a1(n) * mean
        if angular_gauge
        else mean.copy()
    )

    finite = bool(
        np.isfinite(final_mean).all()
        and all(
            np.isfinite(x.mean).all()
            and np.isfinite(x.covariance).all()
            and np.isfinite(x.pre_mean).all()
            and np.isfinite(x.pre_covariance).all()
            for x in layers
        )
    )

    return Estimate(
        final_mean=np.asarray(final_mean, dtype=np.float64).copy(),
        layers=tuple(layers),
        first_gaussian_mean=first_g_mean,
        first_gaussian_covariance=first_g_cov,
        first_angular_mean=first_a_mean,
        first_angular_covariance=first_a_cov,
        finite=finite,
        production_cost=production_cost_receipt(),
    )


def gaussian_parent(weights: Sequence[np.ndarray]) -> Estimate:
    return _estimate(weights, angular_gauge=False)


def ago_candidate(weights: Sequence[np.ndarray]) -> Estimate:
    return _estimate(weights, angular_gauge=True)


def production_cost_receipt() -> dict:
    n = PROD_N
    L = PROD_DEPTH
    parts = {
        "covariance_linear_transport": L * 4 * n**3,
        "mean_dense_matvec": L * 2 * n**2,
        "k2_relu_arithmetic": L * 24 * n**2,
        "wick_scalar_work": L * 1024 * n,
        "parent_helper_reserve": 20 * (2 * n**3),
        "ago_gauge_overlay": 8 * n**2 + 64 * L * n,
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - total,
        "formula_matches_frozen_total": total == 112_131_571_712,
        "passes_cap": total <= CAP_FLOPS,
    }
