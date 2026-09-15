from __future__ import annotations

import math


def gaussian_radius_mean(width: int) -> float:
    if width <= 0:
        raise ValueError("width must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma((float(width) + 1.0) / 2.0) - math.lgamma(float(width) / 2.0)
    )


def _normalize_rows(xp, x):
    norms = xp.sqrt(xp.sum(x * x, axis=1, keepdims=True))
    return x / norms


def build_support(xp, w0):
    if len(w0.shape) != 2 or w0.shape[0] != w0.shape[1]:
        raise ValueError("w0 must be square")
    n = int(w0.shape[0])
    eye = xp.eye(n, dtype=w0.dtype)
    rows = _normalize_rows(xp, w0)
    cols = _normalize_rows(xp, w0.T)
    return xp.concatenate([eye, rows, cols], axis=0)


def fit_first_layer_weights_from_preactivation(xp, w0, preactivation, radius_mean: float):
    n = int(w0.shape[0])
    if w0.shape != (n, n):
        raise ValueError("w0 must be square")
    if preactivation.shape != (3 * n, n):
        raise ValueError("preactivation must correspond to exactly three n-row blocks")

    m = int(preactivation.shape[0])
    response = (0.5 * float(radius_mean)) * xp.abs(preactivation).T
    target = xp.sqrt(xp.sum(w0 * w0, axis=1)) * (1.0 / math.sqrt(2.0 * math.pi))

    response64 = response.astype(xp.float64)
    target64 = target.astype(xp.float64)
    ones = xp.ones((1, m), dtype=xp.float64)
    c = xp.concatenate([response64, ones], axis=0)
    d = xp.concatenate([target64, xp.ones((1,), dtype=xp.float64)], axis=0)
    w_uniform = xp.ones((m,), dtype=xp.float64) * (1.0 / float(m))
    rhs = d - c @ w_uniform
    gram = c @ c.T
    correction = c.T @ xp.linalg.solve(gram, rhs)
    weights = w_uniform + correction
    achieved = response64 @ weights
    return weights, target64, achieved


def fit_first_layer_weights(xp, w0, support, radius_mean: float):
    n = int(w0.shape[0])
    if support.shape != (3 * n, n):
        raise ValueError("support must contain exactly three n-row blocks")
    preactivation = support @ w0.T
    return fit_first_layer_weights_from_preactivation(xp, w0, preactivation, radius_mean)
