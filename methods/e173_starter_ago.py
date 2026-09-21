"""E173 starter-compatible integration of the verified E164 Angular Gauge Only mechanism.

This module contains only the production arithmetic. Research evidence capture and
filesystem I/O live in scripts/e173_capture_vectors.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator
from whestbench.domain import MLP


VAR_FLOOR = 1.0e-12
SUITE_WIDTH = 1024
SUITE_DEPTH = 16
BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
ANALYTIC_ALL_IN_FLOPS = 112_131_571_712


@dataclass(frozen=True)
class GaugeState:
    gaussian_mean: fnp.ndarray
    gaussian_covariance: fnp.ndarray
    angular_mean: fnp.ndarray
    angular_covariance: fnp.ndarray


def radial_a1(n: int) -> float:
    """Exact E[R/sqrt(n)] for R ~ chi_n."""
    if n <= 0:
        raise ValueError("n must be positive")
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )


def _to_angular(
    gaussian_mean: fnp.ndarray,
    gaussian_covariance: fnp.ndarray,
    n: int,
) -> tuple[fnp.ndarray, fnp.ndarray]:
    a1 = radial_a1(n)
    mean = gaussian_mean / a1
    correction = (1.0 / (a1 * a1) - 1.0) * fnp.outer(
        gaussian_mean,
        gaussian_mean,
    )
    covariance = gaussian_covariance - correction
    covariance = flops.as_symmetric(
        0.5 * (covariance + covariance.T),
        symmetry=(0, 1),
    )
    return mean, covariance


def _to_gaussian(
    angular_mean: fnp.ndarray,
    angular_covariance: fnp.ndarray,
    n: int,
) -> tuple[fnp.ndarray, fnp.ndarray]:
    a1 = radial_a1(n)
    mean = a1 * angular_mean
    covariance = angular_covariance + (1.0 - a1 * a1) * fnp.outer(
        angular_mean,
        angular_mean,
    )
    covariance = flops.as_symmetric(
        0.5 * (covariance + covariance.T),
        symmetry=(0, 1),
    )
    return mean, covariance


def _relu_k2_step(
    mean: fnp.ndarray,
    covariance: fnp.ndarray,
    weight: fnp.ndarray,
) -> tuple[fnp.ndarray, fnp.ndarray]:
    """One E164 K2 step in WhestBench weight orientation.

    WhestBench propagates row activations as x @ weight. For column moments this is
    weight.T @ mean, which is exactly E164 with row-weight W = weight.T.
    """

    pre_mean = weight.T @ mean
    left = weight.T @ covariance
    pre_covariance = left @ weight
    pre_covariance = flops.as_symmetric(
        0.5 * (pre_covariance + pre_covariance.T),
        symmetry=(0, 1),
    )

    variance = fnp.maximum(fnp.diag(pre_covariance), VAR_FLOOR)
    sigma = fnp.sqrt(variance)
    alpha = pre_mean / sigma
    phi = flops.stats.norm.pdf(alpha).astype(fnp.float32)
    Phi = flops.stats.norm.cdf(alpha).astype(fnp.float32)

    raw1 = sigma * phi + pre_mean * Phi
    raw2 = (
        (pre_mean * pre_mean + variance) * Phi
        + pre_mean * sigma * phi
    )

    off = fnp.copy(pre_covariance)
    fnp.fill_diagonal(off, 0.0)

    deriv2 = phi / sigma
    first = off * fnp.outer(Phi, Phi)
    second = 0.5 * (off * off) * fnp.outer(deriv2, deriv2)
    out_covariance = first + second

    out_variance = fnp.maximum(raw2 - raw1 * raw1, VAR_FLOOR)
    fnp.fill_diagonal(out_covariance, out_variance)
    out_covariance = flops.as_symmetric(
        0.5 * (out_covariance + out_covariance.T),
        symmetry=(0, 1),
    )
    return raw1, out_covariance


def _initial_state(width: int) -> tuple[fnp.ndarray, fnp.ndarray]:
    mean = fnp.zeros(width, dtype=fnp.float32)
    covariance = flops.as_symmetric(
        fnp.eye(width, dtype=fnp.float32),
        symmetry=(0, 1),
    )
    return mean, covariance


def _run_parent(mlp: MLP) -> fnp.ndarray:
    mean, covariance = _initial_state(mlp.width)
    rows = []
    for weight in mlp.weights:
        mean, covariance = _relu_k2_step(mean, covariance, weight)
        rows.append(mean)
    return fnp.stack(rows, axis=0)


def _run_ago(mlp: MLP) -> fnp.ndarray:
    mean, covariance = _initial_state(mlp.width)
    a1 = radial_a1(mlp.width)
    rows = []

    for layer_index, weight in enumerate(mlp.weights):
        mean, covariance = _relu_k2_step(mean, covariance, weight)
        if layer_index == 0:
            mean, covariance = _to_angular(
                mean,
                covariance,
                mlp.width,
            )
        rows.append(mean * a1)

    return fnp.stack(rows, axis=0)


def suite_shape(mlp: MLP) -> bool:
    return bool(
        mlp.width == SUITE_WIDTH
        and mlp.depth == SUITE_DEPTH
        and len(mlp.weights) == SUITE_DEPTH
    )


def analytic_cost_receipt() -> dict[str, int | float | bool]:
    total = ANALYTIC_ALL_IN_FLOPS
    return {
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - total,
        "passes_cap": total <= CAP_FLOPS,
    }


class ParentEstimator(BaseEstimator):
    """E164 parent closure in the current starter interface."""

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        return _run_parent(mlp)


class AGOEstimator(BaseEstimator):
    """E164 AGO on Phase-2 shape; exact parent fallback on every other shape."""

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        if not suite_shape(mlp):
            return _run_parent(mlp)
        return _run_ago(mlp)
