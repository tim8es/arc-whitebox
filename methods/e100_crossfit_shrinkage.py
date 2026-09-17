from __future__ import annotations

import math
from typing import Sequence

import numpy as np

_SQRT_2PI = math.sqrt(2.0 * math.pi)


def generate_synthetic_mlp(*, seed: int, width: int, depth: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / float(width))
    return [
        np.asarray(rng.standard_normal((width, width)), dtype=np.float64) * scale
        for _ in range(depth)
    ]


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / _SQRT_2PI


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    flat = np.asarray(x, dtype=np.float64).ravel()
    vals = np.fromiter(
        (0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return vals.reshape(np.shape(x))


def covariance_state(weights: Sequence[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    if not weights:
        raise ValueError("weights must be non-empty")
    width = int(np.asarray(weights[0]).shape[0])
    mu = np.zeros(width, dtype=np.float64)
    cov = np.eye(width, dtype=np.float64)
    rows: list[np.ndarray] = []

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        if w.shape != (width, width):
            raise ValueError("all weights must share square width")

        mu_pre = w @ mu
        cov_pre = w @ cov @ w.T
        cov_pre = 0.5 * (cov_pre + cov_pre.T)

        var_pre = np.maximum(np.diag(cov_pre), 1e-12)
        sigma_pre = np.sqrt(var_pre)
        alpha = mu_pre / sigma_pre
        phi = _normal_pdf(alpha)
        Phi = _normal_cdf(alpha)

        mu = mu_pre * Phi + sigma_pre * phi
        ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sigma_pre * phi
        var_post = np.maximum(ez2 - mu * mu, 0.0)

        gain = np.where(sigma_pre > 1e-12, Phi, 0.0)
        cov = np.outer(gain, gain) * cov_pre
        np.fill_diagonal(cov, var_post)
        cov = 0.5 * (cov + cov.T)
        rows.append(mu.copy())

    return np.stack(rows, axis=0), cov


def canonical_top_subspace(cov: np.ndarray, *, rank: int) -> np.ndarray:
    a = np.asarray(cov, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("cov must be square")
    if not (1 <= rank <= a.shape[0]):
        raise ValueError("invalid rank")
    a = 0.5 * (a + a.T)
    evals, evecs = np.linalg.eigh(a)
    order = np.argsort(evals, kind="stable")[::-1][:rank]
    u = np.asarray(evecs[:, order], dtype=np.float64).copy()
    for j in range(u.shape[1]):
        pivot = int(np.argmax(np.abs(u[:, j])))
        if u[pivot, j] < 0.0:
            u[:, j] *= -1.0
    return u


def antithetic_final_samples(
    weights: Sequence[np.ndarray], *, input_seed: int, samples: int
) -> np.ndarray:
    if samples <= 0 or samples % 2:
        raise ValueError("samples must be a positive even integer")
    if not weights:
        raise ValueError("weights must be non-empty")
    width = int(np.asarray(weights[0]).shape[0])
    pair_count = samples // 2
    rng = np.random.Generator(np.random.PCG64(input_seed))
    x = np.asarray(rng.standard_normal((pair_count, width)), dtype=np.float64)

    h = np.empty((samples, width), dtype=np.float64)
    h[0::2] = x
    h[1::2] = -x

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        h = h @ w.T
        np.maximum(h, 0.0, out=h)
    return h


def split_antithetic_pairs(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] % 4:
        raise ValueError("sample count must be divisible by 4")
    pairs = x.reshape(x.shape[0] // 2, 2, x.shape[1])
    a = pairs[0::2].reshape(-1, x.shape[1]).copy()
    b = pairs[1::2].reshape(-1, x.shape[1]).copy()
    return a, b


def shrink_factor(*, noise_energy: float, residual_energy: float) -> float:
    n = max(float(noise_energy), 0.0)
    e = max(float(residual_energy), 1e-30)
    return float(np.clip(1.0 - n / e, 0.0, 1.0))


def group_stats(samples: np.ndarray, base: np.ndarray, subspace: np.ndarray) -> dict:
    x = np.asarray(samples, dtype=np.float64)
    b = np.asarray(base, dtype=np.float64)
    u = np.asarray(subspace, dtype=np.float64)
    if x.ndim != 2 or b.ndim != 1 or x.shape[1] != b.shape[0]:
        raise ValueError("incompatible samples/base shapes")
    if u.ndim != 2 or u.shape[0] != b.shape[0]:
        raise ValueError("incompatible subspace shape")
    n = x.shape[0]
    if n < 2:
        raise ValueError("need at least two samples")

    mean = np.mean(x, axis=0, dtype=np.float64)
    residual = mean - b
    rp = u @ (u.T @ residual)
    rq = residual - rp
    e_p = float(np.dot(rp, rp))
    e_q = float(np.dot(rq, rq))

    centered = x - mean
    centered_p = centered @ u
    denom = float(n * (n - 1))
    tau_p = float(np.sum(centered_p * centered_p, dtype=np.float64) / denom)
    tau_total = float(np.sum(centered * centered, dtype=np.float64) / denom)
    tau_q = max(0.0, tau_total - tau_p)

    return {
        "mean": mean,
        "residual": residual,
        "tau_p": tau_p,
        "tau_q": tau_q,
        "tau_total": tau_total,
        "e_p": e_p,
        "e_q": e_q,
        "a_p": shrink_factor(noise_energy=tau_p, residual_energy=e_p),
        "a_q": shrink_factor(noise_energy=tau_q, residual_energy=e_q),
    }


def _apply_group_shrink(
    residual: np.ndarray,
    subspace: np.ndarray,
    coeffs: tuple[float, float],
) -> np.ndarray:
    r = np.asarray(residual, dtype=np.float64)
    u = np.asarray(subspace, dtype=np.float64)
    a_p, a_q = float(coeffs[0]), float(coeffs[1])
    rp = u @ (u.T @ r)
    rq = r - rp
    return a_p * rp + a_q * rq


def crossfit_from_halves(
    base: np.ndarray,
    mean_a: np.ndarray,
    mean_b: np.ndarray,
    subspace: np.ndarray,
    coeffs_a: tuple[float, float],
    coeffs_b: tuple[float, float],
) -> np.ndarray:
    b = np.asarray(base, dtype=np.float64)
    ma = np.asarray(mean_a, dtype=np.float64)
    mb = np.asarray(mean_b, dtype=np.float64)
    if b.shape != ma.shape or b.shape != mb.shape:
        raise ValueError("base and half means must have the same shape")

    # A-side coefficients are applied only to B-side residual and vice versa.
    from_b = _apply_group_shrink(mb - b, subspace, coeffs_a)
    from_a = _apply_group_shrink(ma - b, subspace, coeffs_b)
    return b + 0.5 * (from_b + from_a)


def crossfit_estimate(
    base: np.ndarray,
    samples: np.ndarray,
    subspace: np.ndarray,
) -> tuple[np.ndarray, dict, dict]:
    a, b = split_antithetic_pairs(samples)
    sa = group_stats(a, base, subspace)
    sb = group_stats(b, base, subspace)
    estimate = crossfit_from_halves(
        base,
        sa["mean"],
        sb["mean"],
        subspace,
        (sa["a_p"], sa["a_q"]),
        (sb["a_p"], sb["a_q"]),
    )
    return estimate, sa, sb
