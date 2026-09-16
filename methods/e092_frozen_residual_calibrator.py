"""Synthetic-only frozen residual calibrator for E092.

This module intentionally contains no benchmark/public-data access.  It provides
(1) a fixed target-free final-layer feature map, (2) fixed-lambda ridge fitting,
(3) deterministic synthetic MLP/reference generation, and (4) a NumPy copy of
the pinned covariance baseline used only by the E092 synthetic falsifier.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

_EPS = 1e-12
_SQRT_2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


@dataclass(frozen=True)
class FrozenRidgeModel:
    """Target-independent preprocessing plus fixed ridge coefficients."""

    coefficients: np.ndarray
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    lambda_: float


def generate_synthetic_mlp(seed: int, width: int, depth: int) -> tuple[np.ndarray, ...]:
    """Generate the frozen E092 synthetic MLP distribution."""
    if width <= 0 or depth <= 0:
        raise ValueError("width and depth must be positive")
    rng = np.random.default_rng(seed)
    scale = 1.0 / math.sqrt(float(width))
    return tuple(
        np.asarray(rng.standard_normal((width, width)) * scale, dtype=np.float64)
        for _ in range(depth)
    )


def antithetic_reference(
    weights: Sequence[np.ndarray], input_seed: int, samples: int
) -> np.ndarray:
    """High-sample deterministic antithetic Monte-Carlo reference means."""
    if samples <= 0 or samples % 2 != 0:
        raise ValueError("samples must be a positive even integer")
    width = int(np.asarray(weights[0]).shape[0])
    rng = np.random.default_rng(input_seed)
    half = samples // 2
    positive = np.asarray(rng.standard_normal((half, width)), dtype=np.float64)
    activation = np.concatenate([positive, -positive], axis=0)
    rows: list[np.ndarray] = []
    for weight in weights:
        activation = np.maximum(activation @ np.asarray(weight, dtype=np.float64), 0.0)
        rows.append(np.mean(activation, axis=0, dtype=np.float64))
    return np.stack(rows, axis=0)


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / _SQRT_2PI


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    erf = np.vectorize(math.erf, otypes=[np.float64])
    return 0.5 * (1.0 + erf(x / _SQRT_2))


def covariance_baseline_numpy(weights: Sequence[np.ndarray]) -> np.ndarray:
    """NumPy reproduction of the pinned covariance-propagation baseline."""
    width = int(np.asarray(weights[0]).shape[0])
    mu = np.zeros(width, dtype=np.float64)
    cov = np.eye(width, dtype=np.float64)
    rows: list[np.ndarray] = []

    for weight in weights:
        w = np.asarray(weight, dtype=np.float64)
        mu_pre = w.T @ mu
        cov_pre = w.T @ cov @ w

        var_pre = np.maximum(np.diag(cov_pre), _EPS)
        sigma_pre = np.sqrt(var_pre)
        alpha = mu_pre / sigma_pre
        pdf = _normal_pdf(alpha)
        cdf = _normal_cdf(alpha)

        mu = mu_pre * cdf + sigma_pre * pdf
        ez2 = (mu_pre * mu_pre + var_pre) * cdf + mu_pre * sigma_pre * pdf
        var_post = np.maximum(ez2 - mu * mu, 0.0)

        gain = np.where(sigma_pre > _EPS, cdf, 0.0)
        cov = np.outer(gain, gain) * cov_pre
        np.fill_diagonal(cov, var_post)
        cov = 0.5 * (cov + cov.T)
        rows.append(mu.copy())

    return np.stack(rows, axis=0)


def final_layer_features(base_prediction: np.ndarray, final_weight: np.ndarray) -> np.ndarray:
    """Build the frozen eight-dimensional target-free E092 feature map."""
    base = np.asarray(base_prediction, dtype=np.float64)
    weight = np.asarray(final_weight, dtype=np.float64)
    if base.ndim != 2 or weight.ndim != 2 or weight.shape[0] != weight.shape[1]:
        raise ValueError("expected base=(depth,width) and square final_weight")
    width = weight.shape[1]
    if base.shape[1] != width:
        raise ValueError("baseline width and weight width must match")

    b = base[-1]
    prev = base[-2] if base.shape[0] > 1 else np.zeros(width, dtype=np.float64)
    rms_b = math.sqrt(float(np.mean(b * b)) + _EPS)
    b_norm = b / rms_b

    w2 = weight * weight
    sum_w2 = np.sum(w2, axis=0)
    signed_skew = np.sum(weight * w2, axis=0) / (np.power(sum_w2, 1.5) + _EPS)
    concentration = np.sum(w2 * w2, axis=0) / (sum_w2 * sum_w2 + _EPS)

    prev_norm = math.sqrt(float(np.sum(prev * prev)) + _EPS)
    projection = (weight.T @ prev) / (np.sqrt(sum_w2) * prev_norm + _EPS)
    mean_prev2 = float(np.mean(prev * prev)) + _EPS
    energy_projection = (w2.T @ (prev * prev)) / (sum_w2 * mean_prev2 + _EPS) - 1.0

    features = np.column_stack(
        [
            np.ones(width, dtype=np.float64),
            b_norm,
            b_norm * b_norm,
            signed_skew,
            concentration,
            projection,
            energy_projection,
            b_norm * signed_skew,
        ]
    )
    if features.shape[1] != 8:
        raise AssertionError("E092 feature dimension drifted")
    return np.asarray(features, dtype=np.float64)


def _normalize_features(
    features: np.ndarray, mean: np.ndarray, scale: np.ndarray
) -> np.ndarray:
    normalized = (features - mean) / scale
    normalized[:, 0] = 1.0
    return normalized


def fit_frozen_ridge(
    features: np.ndarray, residual_targets: np.ndarray, lambda_: float = 1e-2
) -> FrozenRidgeModel:
    """Fit one fixed-lambda ridge model with target-independent preprocessing."""
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(residual_targets, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 8:
        raise ValueError("features must have shape (n, 8)")
    if y.ndim != 1 or y.shape[0] != x.shape[0]:
        raise ValueError("residual_targets must have shape (n,)")
    if lambda_ <= 0.0:
        raise ValueError("lambda_ must be positive")

    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    mean[0] = 0.0
    scale[0] = 1.0
    scale[1:] = np.maximum(scale[1:], _EPS)
    xn = _normalize_features(x, mean, scale)

    penalty = np.eye(x.shape[1], dtype=np.float64) * float(lambda_)
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(xn.T @ xn + penalty, xn.T @ y)
    return FrozenRidgeModel(
        coefficients=np.asarray(coefficients, dtype=np.float64),
        feature_mean=np.asarray(mean, dtype=np.float64),
        feature_scale=np.asarray(scale, dtype=np.float64),
        lambda_=float(lambda_),
    )


def apply_frozen_ridge(
    features: np.ndarray, base_final: np.ndarray, model: FrozenRidgeModel
) -> np.ndarray:
    """Apply a frozen correction without reading any target/reference value."""
    x = np.asarray(features, dtype=np.float64)
    base = np.asarray(base_final, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 8 or base.shape != (x.shape[0],):
        raise ValueError("shape mismatch between features and base_final")
    xn = _normalize_features(x, model.feature_mean, model.feature_scale)
    correction = xn @ model.coefficients
    return base + correction
