"""E175 clean-room public gain-only covariance parent + AGO overlay.

The parent formula is reconstructed from the pinned official starter-kit
examples/03_covariance_propagation.py. This module does not import E164/E171
candidate code and contains no public dataset access.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Sequence

import numpy as np

BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
OFFICIAL_PARENT_FLOPS = 51_709_240_799
AGO_OVERLAY_UPPER = 9_437_184
INTEGRATION_RESERVE = 1_000_000_000
ALL_IN_UPPER = OFFICIAL_PARENT_FLOPS + AGO_OVERLAY_UPPER + INTEGRATION_RESERVE
VAR_FLOOR = 1e-12


@dataclass(frozen=True)
class Estimate:
    final_mean: np.ndarray
    first_gaussian_mean: np.ndarray
    first_gaussian_covariance: np.ndarray
    first_angular_mean: np.ndarray | None
    first_angular_covariance: np.ndarray | None
    finite: bool
    digest: str


def radial_a1(n: int) -> float:
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )


def _pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _cdf(x: np.ndarray) -> np.ndarray:
    return np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in x],
        dtype=np.float64,
    )


def gain_layer(
    mean: np.ndarray,
    covariance: np.ndarray,
    weight: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Official public gain-only K2 closure, clean-room orientation."""
    mu = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(covariance, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)

    pre_mean = w @ mu
    pre_cov = w @ cov @ w.T
    pre_cov = 0.5 * (pre_cov + pre_cov.T)

    var = np.maximum(np.diag(pre_cov), VAR_FLOOR)
    sigma = np.sqrt(var)
    alpha = pre_mean / sigma
    phi = _pdf(alpha)
    Phi = _cdf(alpha)

    out_mean = pre_mean * Phi + sigma * phi
    ez2 = (pre_mean * pre_mean + var) * Phi + pre_mean * sigma * phi
    out_var = np.maximum(ez2 - out_mean * out_mean, 0.0)

    # Deliberately gain-only. There is no C_ij^2 second-order Wick term.
    out_cov = pre_cov * (Phi[:, None] * Phi[None, :])
    np.fill_diagonal(out_cov, out_var)
    out_cov = 0.5 * (out_cov + out_cov.T)
    return out_mean, out_cov


def to_angular(
    gaussian_mean: np.ndarray,
    gaussian_covariance: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    mg = np.asarray(gaussian_mean, dtype=np.float64)
    cg = np.asarray(gaussian_covariance, dtype=np.float64)
    ma = mg / a1
    ca = cg - (1.0 / (a1 * a1) - 1.0) * np.outer(mg, mg)
    return ma, 0.5 * (ca + ca.T)


def to_gaussian(
    angular_mean: np.ndarray,
    angular_covariance: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    a1 = radial_a1(n)
    ma = np.asarray(angular_mean, dtype=np.float64)
    ca = np.asarray(angular_covariance, dtype=np.float64)
    mg = a1 * ma
    cg = ca + (1.0 - a1 * a1) * np.outer(ma, ma)
    return mg, 0.5 * (cg + cg.T)


def _digest(arrays: Sequence[np.ndarray]) -> str:
    h = hashlib.sha256()
    for x in arrays:
        y = np.ascontiguousarray(np.asarray(x, dtype=np.float64))
        h.update(str(y.shape).encode())
        h.update(y.dtype.str.encode())
        h.update(y.tobytes())
    return h.hexdigest()


def estimate(weights: Sequence[np.ndarray], *, ago: bool) -> Estimate:
    if not weights:
        raise ValueError("weights required")
    n = int(np.asarray(weights[0]).shape[0])
    mean = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    first_gm = first_gc = first_am = first_ac = None

    digest_arrays: list[np.ndarray] = []
    for layer, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError((layer, w.shape, n))
        mean, cov = gain_layer(mean, cov, w)
        if layer == 0:
            first_gm = mean.copy()
            first_gc = cov.copy()
            if ago:
                mean, cov = to_angular(mean, cov, n)
                first_am = mean.copy()
                first_ac = cov.copy()
        digest_arrays.extend([mean.copy(), cov.copy()])

    assert first_gm is not None and first_gc is not None
    final = radial_a1(n) * mean if ago else mean.copy()
    digest_arrays.append(final)
    finite = bool(
        np.isfinite(final).all()
        and all(np.isfinite(x).all() for x in digest_arrays)
    )
    return Estimate(
        final_mean=final.copy(),
        first_gaussian_mean=first_gm,
        first_gaussian_covariance=first_gc,
        first_angular_mean=first_am,
        first_angular_covariance=first_ac,
        finite=finite,
        digest=_digest(digest_arrays),
    )


def parent_estimate(weights: Sequence[np.ndarray]) -> Estimate:
    return estimate(weights, ago=False)


def candidate_estimate(weights: Sequence[np.ndarray]) -> Estimate:
    return estimate(weights, ago=True)


def production_cost() -> dict:
    return {
        "official_public_parent_measured_flops": OFFICIAL_PARENT_FLOPS,
        "ago_overlay_upper_flops": AGO_OVERLAY_UPPER,
        "integration_accounting_reserve_flops": INTEGRATION_RESERVE,
        "all_in_upper_flops": ALL_IN_UPPER,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization_upper": ALL_IN_UPPER / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - ALL_IN_UPPER,
        "pass": ALL_IN_UPPER <= CAP_FLOPS,
    }
