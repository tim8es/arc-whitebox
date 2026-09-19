"""E111 exact small-width Gaussian-ReLU plug-in bias helpers."""

from __future__ import annotations

import math

import numpy as np

_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _phi(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) * _INV_SQRT_2PI


def _Phi(x: np.ndarray) -> np.ndarray:
    flat = np.asarray(x, dtype=np.float64).ravel()
    vals = np.fromiter(
        (0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return vals.reshape(np.shape(x))


def gaussian_relu_mean(mu, var):
    """E[ReLU(G)] for a Gaussian G with supplied mean and variance."""
    m = np.asarray(mu, dtype=np.float64)
    v = np.asarray(var, dtype=np.float64)
    if np.any(v < 0.0):
        raise ValueError("variance must be nonnegative")
    sigma = np.sqrt(v)

    if m.ndim == 0:
        if float(sigma) <= 0.0:
            return max(float(m), 0.0)
        alpha = float(m) / float(sigma)
        phi = math.exp(-0.5 * alpha * alpha) * _INV_SQRT_2PI
        Phi = 0.5 * (1.0 + math.erf(alpha / math.sqrt(2.0)))
        return float(sigma) * phi + float(m) * Phi

    out = np.maximum(m, 0.0).astype(np.float64, copy=True)
    mask = sigma > 0.0
    if np.any(mask):
        alpha = m[mask] / sigma[mask]
        out[mask] = sigma[mask] * _phi(alpha) + m[mask] * _Phi(alpha)
    return out


def make_frozen_network(*, seed: int, width: int, depth: int) -> list[np.ndarray]:
    if width <= 0 or depth <= 0:
        raise ValueError("width/depth must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights: list[np.ndarray] = []
    weights.append(
        np.asarray(rng.standard_normal((width, 1)), dtype=np.float64) * math.sqrt(2.0)
    )
    scale = math.sqrt(2.0 / float(width))
    for _ in range(1, depth):
        weights.append(
            np.asarray(rng.standard_normal((width, width)), dtype=np.float64) * scale
        )
    return weights


def _half_line_raw_moment(order: int) -> float:
    """Integral_0^inf x^order phi(x) dx."""
    k = int(order)
    if k < 0:
        raise ValueError("order must be nonnegative")
    return (
        (2.0 ** (0.5 * k - 1.0))
        * math.gamma((k + 1.0) / 2.0)
        / math.sqrt(math.pi)
    )


def exact_two_ray_layer(
    weight: np.ndarray,
    *,
    plus_prev: np.ndarray | None,
    minus_prev: np.ndarray | None,
    first_layer: bool,
) -> dict:
    """Closed-form layer law for a zero-bias ReLU network driven by X~N(0,1).

    The complete law is two rays:
      X>0: pre = X*a_plus
      X<0: pre = (-X)*a_minus.
    """
    w = np.asarray(weight, dtype=np.float64)
    if first_layer:
        if plus_prev is not None or minus_prev is not None:
            raise ValueError("first layer must not receive previous ray states")
        if w.ndim != 2 or w.shape[1] != 1:
            raise ValueError("first-layer weight must have shape (width,1)")
        a_plus = w[:, 0].copy()
        a_minus = -w[:, 0].copy()
    else:
        p = np.asarray(plus_prev, dtype=np.float64)
        m = np.asarray(minus_prev, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != w.shape[1]:
            raise ValueError("later-layer weight must be square")
        if p.shape != (w.shape[1],) or m.shape != (w.shape[1],):
            raise ValueError("ray state has incompatible shape")
        a_plus = w @ p
        a_minus = w @ m

    plus_post = np.maximum(a_plus, 0.0)
    minus_post = np.maximum(a_minus, 0.0)

    h1 = _half_line_raw_moment(1)
    h2 = _half_line_raw_moment(2)
    h3 = _half_line_raw_moment(3)
    h4 = _half_line_raw_moment(4)

    raw1 = h1 * (a_plus + a_minus)
    raw2 = h2 * (a_plus * a_plus + a_minus * a_minus)
    raw3 = h3 * (a_plus**3 + a_minus**3)
    raw4 = h4 * (a_plus**4 + a_minus**4)

    var = np.maximum(raw2 - raw1 * raw1, 0.0)
    plugin = np.asarray(gaussian_relu_mean(raw1, var), dtype=np.float64)
    exact_relu_mean = h1 * (plus_post + minus_post)

    central3 = raw3 - 3.0 * raw1 * raw2 + 2.0 * raw1**3
    central4 = raw4 - 4.0 * raw1 * raw3 + 6.0 * raw1**2 * raw2 - 3.0 * raw1**4
    skew = np.zeros_like(raw1)
    kurtosis = np.zeros_like(raw1)
    positive = var > 0.0
    skew[positive] = central3[positive] / np.power(var[positive], 1.5)
    kurtosis[positive] = central4[positive] / (var[positive] * var[positive])

    return {
        "a_plus": a_plus,
        "a_minus": a_minus,
        "plus_post": plus_post,
        "minus_post": minus_post,
        "pre_mean": raw1,
        "pre_var": var,
        "plugin_mean": plugin,
        "exact_relu_mean": exact_relu_mean,
        "bias": plugin - exact_relu_mean,
        "skew": skew,
        "kurtosis": kurtosis,
    }
