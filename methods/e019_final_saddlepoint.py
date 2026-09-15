from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

NEWTON_ITERS = 6

# Fixed 32-node Gauss-Legendre rule mapped from [-1, 1] to [-8, 8].
GL_NODES = np.asarray(
    [
        -7.978110894795853,
        -7.884892092362147,
        -7.718098044700051,
        -7.479248607501917,
        -7.170569246128417,
        -6.79494090986056,
        -6.355870367743539,
        -5.857456949922318,
        -5.304354135441722,
        -4.701726057926098,
        -4.055199271457835,
        -3.3708102090450827,
        -2.6549488182570213,
        -1.9142988980170965,
        -1.155775692662372,
        -0.3864613255019066,
        0.3864613255019066,
        1.155775692662372,
        1.9142988980170965,
        2.6549488182570213,
        3.3708102090450827,
        4.055199271457835,
        4.701726057926098,
        5.304354135441722,
        5.857456949922318,
        6.355870367743539,
        6.79494090986056,
        7.170569246128417,
        7.479248607501917,
        7.718098044700051,
        7.884892092362147,
        7.978110894795853,
    ],
    dtype=np.float64,
)
GL_WEIGHTS = np.asarray(
    [
        0.056148880075764046,
        0.13019515784724595,
        0.2031365224740962,
        0.2741909033041741,
        0.3426871841778147,
        0.40798447409900873,
        0.4694727478282845,
        0.5265777822108935,
        0.5787663528707867,
        0.6255511662965618,
        0.6664953938155737,
        0.7012167440352303,
        0.7293910295661102,
        0.7507551926464361,
        0.7651097606341977,
        0.7723207081178213,
        0.7723207081178213,
        0.7651097606341977,
        0.7507551926464361,
        0.7293910295661102,
        0.7012167440352303,
        0.6664953938155737,
        0.6255511662965618,
        0.5787663528707867,
        0.5265777822108935,
        0.4694727478282845,
        0.40798447409900873,
        0.3426871841778147,
        0.2741909033041741,
        0.2031365224740962,
        0.13019515784724595,
        0.056148880075764046,
    ],
    dtype=np.float64,
)

_SQRT_2PI = math.sqrt(2.0 * math.pi)
_SQRT_2 = math.sqrt(2.0)


@dataclass(frozen=True)
class SaddlepointResult:
    mean: np.ndarray
    min_kpp: float
    max_normalized_residual: float
    finite_positive_kpp: bool


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    flat = np.asarray(x, dtype=np.float64).reshape(-1)
    out = np.fromiter(
        (0.5 * (1.0 + math.erf(float(v) / _SQRT_2)) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return out.reshape(np.shape(x))


def gaussian_relu_mean(kappa1: np.ndarray, kappa2: np.ndarray) -> np.ndarray:
    mu = np.asarray(kappa1, dtype=np.float64)
    var = np.asarray(kappa2, dtype=np.float64)
    sigma = np.sqrt(var)
    alpha = mu / sigma
    phi = np.exp(-0.5 * alpha * alpha) / _SQRT_2PI
    Phi = _normal_cdf(alpha)
    return sigma * phi + mu * Phi


def saddlepoint_relu_mean(
    kappa1: np.ndarray,
    kappa2: np.ndarray,
    kappa3: np.ndarray,
    kappa4: np.ndarray,
) -> SaddlepointResult:
    mu, var, k3, k4 = np.broadcast_arrays(
        np.asarray(kappa1, dtype=np.float64),
        np.asarray(kappa2, dtype=np.float64),
        np.asarray(kappa3, dtype=np.float64),
        np.asarray(kappa4, dtype=np.float64),
    )
    original_shape = mu.shape
    mu = mu.reshape(-1)
    var = var.reshape(-1)
    k3 = k3.reshape(-1)
    k4 = k4.reshape(-1)

    sigma = np.sqrt(var)
    c3 = k3 / (sigma**3)
    c4 = k4 / (sigma**4)

    x = GL_NODES[None, :]
    c3c = c3[:, None]
    c4c = c4[:, None]
    t = np.broadcast_to(x, (mu.size, GL_NODES.size)).copy()

    with np.errstate(divide="ignore", invalid="ignore", over="ignore", under="ignore"):
        for _ in range(NEWTON_ITERS):
            kp = t + 0.5 * c3c * t * t + (c4c / 6.0) * t * t * t
            kpp = 1.0 + c3c * t + 0.5 * c4c * t * t
            t = t - (kp - x) / kpp

        kp = t + 0.5 * c3c * t * t + (c4c / 6.0) * t * t * t
        kpp = 1.0 + c3c * t + 0.5 * c4c * t * t
        K = 0.5 * t * t + (c3c / 6.0) * t * t * t + (c4c / 24.0) * t**4
        density = np.exp(K - t * x) / np.sqrt(2.0 * math.pi * kpp)

        phi_x = np.exp(-0.5 * x * x) / _SQRT_2PI
        z = mu[:, None] + sigma[:, None] * x
        correction = np.sum(
            GL_WEIGHTS[None, :] * np.maximum(z, 0.0) * (density - phi_x),
            axis=1,
        )
        mean = gaussian_relu_mean(mu, var) + correction
        normalized_residual = np.abs(kp - x) / (1.0 + np.abs(x))

    finite_positive = bool(np.all(np.isfinite(kpp)) and np.all(kpp > 0.0))
    min_kpp = float(np.min(kpp)) if np.all(np.isfinite(kpp)) else float("nan")
    max_residual = (
        float(np.max(normalized_residual))
        if np.all(np.isfinite(normalized_residual))
        else float("inf")
    )
    return SaddlepointResult(
        mean=mean.reshape(original_shape),
        min_kpp=min_kpp,
        max_normalized_residual=max_residual,
        finite_positive_kpp=finite_positive,
    )
