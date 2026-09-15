"""E020 fixed quadratic/Hermite residual rider utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BASE_FEATURE_NAMES = (
    "alpha",
    "abs_alpha",
    "phi",
    "Phi",
    "pred_scaled",
    "d3_scaled",
    "d21_scaled",
)
BASE_WIDTH = len(BASE_FEATURE_NAMES)
DESIGN_WIDTH = 1 + BASE_WIDTH + BASE_WIDTH + BASE_WIDTH * (BASE_WIDTH - 1) // 2


@dataclass(frozen=True)
class LayerRiderFit:
    mean: np.ndarray
    scale: np.ndarray
    coefficients: np.ndarray
    rank: int
    condition: float


def _as_finite_2d(features) -> np.ndarray:
    x = np.asarray(features, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != BASE_WIDTH:
        raise ValueError(f"features must have shape (n,{BASE_WIDTH})")
    if not np.all(np.isfinite(x)):
        raise ValueError("E020 features must be finite")
    return x


def hermite_design(features, mean, scale) -> np.ndarray:
    """Return the frozen 36-column standardized degree-2/Hermite map."""
    x = _as_finite_2d(features)
    mu = np.asarray(mean, dtype=np.float64)
    sd = np.asarray(scale, dtype=np.float64)
    if mu.shape != (BASE_WIDTH,) or sd.shape != (BASE_WIDTH,):
        raise ValueError("mean/scale shape mismatch")
    if not np.all(np.isfinite(mu)) or not np.all(np.isfinite(sd)) or np.any(sd <= 0.0):
        raise ValueError("E020 normalization must be finite and strictly positive")

    z = (x - mu) / sd
    cols = [np.ones(x.shape[0], dtype=np.float64)]
    cols.extend(z[:, i] for i in range(BASE_WIDTH))
    cols.extend(z[:, i] * z[:, i] - 1.0 for i in range(BASE_WIDTH))
    for i in range(BASE_WIDTH):
        for j in range(i + 1, BASE_WIDTH):
            cols.append(z[:, i] * z[:, j])
    design = np.column_stack(cols)
    if design.shape[1] != DESIGN_WIDTH or not np.all(np.isfinite(design)):
        raise ValueError("invalid E020 design")
    return design


def fit_layer_rider(features, target, *, condition_limit: float = 1e8) -> LayerRiderFit:
    """Fit one deterministic pooled OLS rider with no ridge or feature selection."""
    x = _as_finite_2d(features)
    y = np.asarray(target, dtype=np.float64)
    if y.shape != (x.shape[0],) or not np.all(np.isfinite(y)):
        raise ValueError("target shape/finite mismatch")

    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    if np.any(~np.isfinite(scale)) or np.any(scale <= 0.0):
        raise np.linalg.LinAlgError("E020 base feature has zero/non-finite scale")
    design = hermite_design(x, mean, scale)
    singular = np.linalg.svd(design, compute_uv=False)
    rank = int(np.linalg.matrix_rank(design))
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0.0 else float("inf")
    if rank != DESIGN_WIDTH:
        raise np.linalg.LinAlgError(f"E020 design rank {rank} != {DESIGN_WIDTH}")
    if not np.isfinite(condition) or condition > float(condition_limit):
        raise np.linalg.LinAlgError(
            f"E020 design condition {condition} exceeds {float(condition_limit)}"
        )
    coefficients, _, fit_rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if int(fit_rank) != DESIGN_WIDTH or not np.all(np.isfinite(coefficients)):
        raise np.linalg.LinAlgError("E020 least-squares fit is not full-rank/finite")
    return LayerRiderFit(
        mean=mean,
        scale=scale,
        coefficients=coefficients,
        rank=rank,
        condition=condition,
    )


def apply_rider(features, fit: LayerRiderFit) -> np.ndarray:
    """Apply one frozen rider deterministically."""
    design = hermite_design(features, fit.mean, fit.scale)
    delta = design @ np.asarray(fit.coefficients, dtype=np.float64)
    if not np.all(np.isfinite(delta)):
        raise ValueError("non-finite E020 correction")
    return delta
