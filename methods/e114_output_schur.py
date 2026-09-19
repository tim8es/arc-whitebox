"""E114 output-specific Schur-complement final-mean compression helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

_TWO_PI = 2.0 * math.pi
_E_R_2D = math.sqrt(math.pi / 2.0)
_E_R2_2D = 2.0


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float
    coeff: np.ndarray  # shape (width, 2), post-activation linear map on this sector


def make_network(*, seed: int, width: int = 8, depth: int = 4) -> list[np.ndarray]:
    if depth != 4:
        raise ValueError("frozen E114 gate requires depth=4")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    out.append(
        np.asarray(rng.standard_normal((width, 2)), dtype=np.float64)
        * math.sqrt(2.0 / 2.0)
    )
    scale = math.sqrt(2.0 / float(width))
    for _ in range(1, depth):
        out.append(
            np.asarray(rng.standard_normal((width, width)), dtype=np.float64)
            * scale
        )
    return out


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1e-12 < x < hi - 1e-12:
            roots.append(x)
    return roots


def _dedup(values: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(values):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def _integral_q(lo: float, hi: float) -> np.ndarray:
    return np.array(
        [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
        dtype=np.float64,
    )


def _integral_qq(lo: float, hi: float) -> np.ndarray:
    delta = hi - lo
    cc = 0.5 * delta + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    ss = 0.5 * delta - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    cs = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    return np.array([[cc, cs], [cs, ss]], dtype=np.float64)


def relu_layer(intervals: list[Interval], weight: np.ndarray) -> list[Interval]:
    w = np.asarray(weight, dtype=np.float64)
    next_intervals: list[Interval] = []
    for item in intervals:
        pre = w @ item.coeff
        boundaries = [item.lo, item.hi]
        for row in pre:
            boundaries.extend(_roots(float(row[0]), float(row[1]), item.lo, item.hi))
        boundaries = _dedup(boundaries)
        for lo, hi in zip(boundaries[:-1], boundaries[1:]):
            if hi - lo <= 1e-13:
                continue
            mid = 0.5 * (lo + hi)
            q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
            active = (pre @ q) > 0.0
            coeff = pre.copy()
            coeff[~active, :] = 0.0
            next_intervals.append(Interval(lo, hi, coeff))
    return next_intervals


def layer2_intervals(weights: list[np.ndarray]) -> list[Interval]:
    intervals = [Interval(0.0, _TWO_PI, np.eye(2, dtype=np.float64))]
    intervals = relu_layer(intervals, weights[0])
    intervals = relu_layer(intervals, weights[1])
    return intervals


def exact_penultimate_preact_second_moment(
    layer2: list[Interval], w3: np.ndarray
) -> np.ndarray:
    w = np.asarray(w3, dtype=np.float64)
    width = w.shape[0]
    m = np.zeros((width, width), dtype=np.float64)
    for item in layer2:
        a = w @ item.coeff
        g = _integral_qq(item.lo, item.hi)
        m += a @ g @ a.T
    m *= _E_R2_2D / _TWO_PI
    return 0.5 * (m + m.T)


def exact_final_mean(weights: list[np.ndarray]) -> tuple[np.ndarray, int]:
    intervals = [Interval(0.0, _TWO_PI, np.eye(2, dtype=np.float64))]
    for w in weights:
        intervals = relu_layer(intervals, w)
    width = weights[-1].shape[0]
    angular = np.zeros(width, dtype=np.float64)
    for item in intervals:
        angular += item.coeff @ _integral_q(item.lo, item.hi)
    return _E_R_2D * angular / _TWO_PI, len(intervals)


def output_weighted_diagonal(w4: np.ndarray) -> np.ndarray:
    w = np.asarray(w4, dtype=np.float64)
    row_l1 = np.sum(np.abs(w), axis=1)
    d = np.mean(row_l1[:, None] * np.abs(w), axis=0)
    return d


def schur_rank_compression(
    second_moment: np.ndarray,
    d_pool: np.ndarray,
    *,
    rank: int,
    tol: float = 1e-12,
) -> dict:
    m = 0.5 * (
        np.asarray(second_moment, dtype=np.float64)
        + np.asarray(second_moment, dtype=np.float64).T
    )
    d = np.asarray(d_pool, dtype=np.float64)
    if m.shape[0] != m.shape[1] or d.shape != (m.shape[0],):
        raise ValueError("shape mismatch")
    if not 1 <= rank < m.shape[0]:
        raise ValueError("rank must be in [1,n-1]")

    eval_m, q_m = np.linalg.eigh(m)
    max_m = max(float(np.max(eval_m)), 0.0)
    support = eval_m > tol * max(1.0, max_m)

    sqrt_vals = np.zeros_like(eval_m)
    invsqrt_vals = np.zeros_like(eval_m)
    sqrt_vals[support] = np.sqrt(eval_m[support])
    invsqrt_vals[support] = 1.0 / sqrt_vals[support]

    sqrt_m = (q_m * sqrt_vals[None, :]) @ q_m.T
    invsqrt_m = (q_m * invsqrt_vals[None, :]) @ q_m.T

    b = sqrt_m @ np.diag(d) @ sqrt_m
    b = 0.5 * (b + b.T)
    eval_b, q_b = np.linalg.eigh(b)
    order = np.argsort(eval_b, kind="stable")[::-1]
    eval_b = eval_b[order]
    q_b = q_b[:, order]
    v = q_b[:, :rank]

    projector = v @ v.T
    k = sqrt_m @ projector @ invsqrt_m
    explained = sqrt_m @ projector @ sqrt_m
    residual = 0.5 * ((m - explained) + (m - explained).T)

    remainder_trace = float(np.dot(d, np.diag(residual)))
    omitted_sum = float(np.sum(np.maximum(eval_b[rank:], 0.0)))
    return {
        "K": k,
        "M_res": residual,
        "B_eigenvalues": eval_b,
        "M_eigenvalues": eval_m,
        "remainder_bound": remainder_trace,
        "omitted_eigenvalue_sum": omitted_sum,
        "min_residual_eigenvalue": float(np.min(np.linalg.eigvalsh(residual))),
        "support_rank": int(np.count_nonzero(support)),
    }


def compressed_weights(weights: list[np.ndarray], k: np.ndarray) -> list[np.ndarray]:
    out = [np.asarray(x, dtype=np.float64).copy() for x in weights]
    out[2] = np.asarray(k, dtype=np.float64) @ out[2]
    return out


def pooled_bias_mse(exact: np.ndarray, proxy: np.ndarray) -> float:
    delta = np.asarray(proxy, dtype=np.float64) - np.asarray(exact, dtype=np.float64)
    return float(np.mean(delta * delta))
