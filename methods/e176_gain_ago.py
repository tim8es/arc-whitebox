"""E176 clean-room public gain-only covariance parent and one-time AGO gauge.

This module is independent of E175 and contains no reference/target/data access.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Sequence

import numpy as np

VAR_FLOOR = 1.0e-12
BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
OFFICIAL_PARENT_PRODUCTION_FLOPS = 51_709_240_799
PRODUCTION_GAUGE_READOUT_UPPER = 9_453_568
PRODUCTION_INTEGRATION_RESERVE = 64_000_000
PRODUCTION_CANDIDATE_UPPER = (
    OFFICIAL_PARENT_PRODUCTION_FLOPS
    + PRODUCTION_GAUGE_READOUT_UPPER
    + PRODUCTION_INTEGRATION_RESERVE
)

@dataclass(frozen=True)
class Estimate:
    all_layer_means: np.ndarray
    first_gaussian_mean: np.ndarray
    first_gaussian_covariance: np.ndarray
    first_angular_mean: np.ndarray | None
    first_angular_covariance: np.ndarray | None
    gauge_roundtrip_relative_error: float
    finite: bool
    raw_sha256: str

def radial_a1(n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return math.exp(
        0.5 * math.log(2.0 / float(n))
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )

def _pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

def _cdf(x: np.ndarray) -> np.ndarray:
    flat = np.ravel(np.asarray(x, dtype=np.float64))
    y = np.fromiter(
        (0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return y.reshape(np.asarray(x).shape)

def gain_only_layer(
    mean: np.ndarray,
    covariance: np.ndarray,
    weight: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Clean-room reconstruction of the official public gain-only K2 formula."""
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

    # Gain-only off diagonal. Intentionally no 0.5*C_ij^2 Wick correction.
    out_cov = pre_cov * np.outer(Phi, Phi)
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
    cg = ca + (1.0 - a1 * a1) * np.outer(ma, ma)
    cg = 0.5 * (cg + cg.T)
    return mg, cg

def _relative_state_error(
    m0: np.ndarray,
    c0: np.ndarray,
    m1: np.ndarray,
    c1: np.ndarray,
) -> float:
    num = math.sqrt(
        float(np.sum((m0 - m1) ** 2))
        + float(np.sum((c0 - c1) ** 2))
    )
    den = max(
        math.sqrt(float(np.sum(m0 * m0)) + float(np.sum(c0 * c0))),
        2.0**-500,
    )
    return num / den

def _raw_sha(array: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(array, dtype=np.float64))
    return hashlib.sha256(x.tobytes()).hexdigest()

def estimate(weights: Sequence[np.ndarray], *, ago: bool) -> Estimate:
    if not weights:
        raise ValueError("weights required")
    n = int(np.asarray(weights[0]).shape[0])
    if any(np.asarray(w).shape != (n, n) for w in weights):
        raise ValueError("all weights must be square and same width")

    mean = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    a1 = radial_a1(n)

    rows: list[np.ndarray] = []
    first_gm = first_gc = first_am = first_ac = None
    roundtrip = 0.0

    for layer, raw in enumerate(weights):
        mean, cov = gain_only_layer(mean, cov, raw)

        if layer == 0:
            first_gm = mean.copy()
            first_gc = cov.copy()
            if ago:
                first_am, first_ac = to_angular(mean, cov, n)
                gm2, gc2 = to_gaussian(first_am, first_ac, n)
                roundtrip = _relative_state_error(
                    first_gm, first_gc, gm2, gc2
                )
                mean, cov = first_am, first_ac

        rows.append((mean * a1).copy() if ago else mean.copy())

    pred = np.stack(rows, axis=0)
    arrays = [pred, first_gm, first_gc]
    if ago:
        arrays.extend([first_am, first_ac])
    finite = all(np.isfinite(np.asarray(x)).all() for x in arrays if x is not None)
    return Estimate(
        all_layer_means=pred,
        first_gaussian_mean=np.asarray(first_gm),
        first_gaussian_covariance=np.asarray(first_gc),
        first_angular_mean=None if first_am is None else np.asarray(first_am),
        first_angular_covariance=None if first_ac is None else np.asarray(first_ac),
        gauge_roundtrip_relative_error=float(roundtrip),
        finite=bool(finite),
        raw_sha256=_raw_sha(pred),
    )

def production_cost_receipt() -> dict[str, int | float | bool]:
    total = PRODUCTION_CANDIDATE_UPPER
    return {
        "parent_official_measured_flops": OFFICIAL_PARENT_PRODUCTION_FLOPS,
        "gauge_readout_upper_flops": PRODUCTION_GAUGE_READOUT_UPPER,
        "integration_reserve_flops": PRODUCTION_INTEGRATION_RESERVE,
        "candidate_all_in_upper_flops": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "candidate_utilization_upper": total / float(BUDGET_FLOPS),
        "passes_cap": total <= CAP_FLOPS,
    }

def mini_cost_receipt(n: int, depth: int) -> dict[str, int]:
    parent = depth * (4 * n**3 + 16 * n**2 + 64 * n)
    candidate = parent + 9 * n**2 + depth * n
    return {
        "parent_research_flop_upper": int(parent),
        "candidate_research_flop_upper": int(candidate),
        "candidate_incremental_flop_upper": int(candidate - parent),
    }
