"""E164 clean-room full-covariance parent and Angular Gauge Only candidate."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
PROD_N = 1024
PROD_DEPTH = 16
VAR_FLOOR = 1.0e-12


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
    cost: dict


def radial_a1(n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )


def _pdf(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * y * y) / math.sqrt(2.0 * math.pi)


def _cdf(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float64)
    return np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in y],
        dtype=np.float64,
    )


def _layer_step(
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

    variance = np.maximum(np.diag(pre_cov), VAR_FLOOR)
    sigma = np.sqrt(variance)
    alpha = pre_mean / sigma
    phi = _pdf(alpha)
    Phi = _cdf(alpha)

    raw1 = sigma * phi + pre_mean * Phi
    raw2 = (pre_mean * pre_mean + variance) * Phi + pre_mean * sigma * phi

    off = pre_cov.copy()
    np.fill_diagonal(off, 0.0)
    deriv1 = Phi
    deriv2 = phi / sigma

    out_cov = (
        off * (deriv1[:, None] * deriv1[None, :])
        + 0.5 * (off * off) * (deriv2[:, None] * deriv2[None, :])
    )
    out_var = np.maximum(raw2 - raw1 * raw1, VAR_FLOOR)
    np.fill_diagonal(out_cov, out_var)
    out_cov = 0.5 * (out_cov + out_cov.T)

    return LayerState(
        mean=raw1.copy(),
        covariance=out_cov.copy(),
        pre_mean=pre_mean.copy(),
        pre_covariance=pre_cov.copy(),
    )


def to_angular(
    gaussian_mean: np.ndarray,
    gaussian_covariance: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    mg = np.asarray(gaussian_mean, dtype=np.float64)
    cg = np.asarray(gaussian_covariance, dtype=np.float64)
    ma = mg / a1
    ca = cg - (1.0 / (a1 * a1) - 1.0) * (mg[:, None] * mg[None, :])
    ca = 0.5 * (ca + ca.T)
    return ma, ca


def to_gaussian(
    angular_mean: np.ndarray,
    angular_covariance: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    ma = np.asarray(angular_mean, dtype=np.float64)
    ca = np.asarray(angular_covariance, dtype=np.float64)
    mg = a1 * ma
    cg = ca + (1.0 - a1 * a1) * (ma[:, None] * ma[None, :])
    cg = 0.5 * (cg + cg.T)
    return mg, cg


def _run(
    weights: Sequence[np.ndarray],
    *,
    angular: bool,
) -> Estimate:
    if not weights:
        raise ValueError("weights required")

    n = int(np.asarray(weights[0]).shape[0])
    mean = np.zeros(n, dtype=np.float64)
    covariance = np.eye(n, dtype=np.float64)

    states: list[LayerState] = []
    first_g_mean: np.ndarray | None = None
    first_g_cov: np.ndarray | None = None
    first_a_mean: np.ndarray | None = None
    first_a_cov: np.ndarray | None = None

    for layer_index, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError(
                f"weight {layer_index} shape {w.shape}, expected {(n, n)}"
            )

        state = _layer_step(mean, covariance, w)

        if layer_index == 0:
            first_g_mean = state.mean.copy()
            first_g_cov = state.covariance.copy()
            if angular:
                mean, covariance = to_angular(
                    state.mean,
                    state.covariance,
                    n,
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

        states.append(state)

    assert first_g_mean is not None
    assert first_g_cov is not None

    final_mean = radial_a1(n) * mean if angular else mean.copy()

    finite = bool(
        np.isfinite(final_mean).all()
        and all(
            np.isfinite(s.mean).all()
            and np.isfinite(s.covariance).all()
            and np.isfinite(s.pre_mean).all()
            and np.isfinite(s.pre_covariance).all()
            for s in states
        )
    )

    return Estimate(
        final_mean=np.asarray(final_mean, dtype=np.float64).copy(),
        layers=tuple(states),
        first_gaussian_mean=first_g_mean,
        first_gaussian_covariance=first_g_cov,
        first_angular_mean=first_a_mean,
        first_angular_covariance=first_a_cov,
        finite=finite,
        cost=production_cost(),
    )


def parent_estimate(weights: Sequence[np.ndarray]) -> Estimate:
    return _run(weights, angular=False)


def ago_estimate(weights: Sequence[np.ndarray]) -> Estimate:
    return _run(weights, angular=True)


def production_cost() -> dict:
    n = PROD_N
    L = PROD_DEPTH
    parts = {
        "covariance_linear_transport": L * 4 * n**3,
        "mean_matvec": L * 2 * n**2,
        "nonlinear_second_order_arithmetic": L * 24 * n**2,
        "normal_scalar_work": L * 1024 * n,
        "helper_reserve": 20 * (2 * n**3),
        "angular_gauge_overlay": 8 * n**2 + 64 * L * n,
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - total,
        "matches_frozen_total": total == 112_131_571_712,
        "passes_cap": total <= CAP_FLOPS,
    }
