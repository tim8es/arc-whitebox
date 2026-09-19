"""E113 exact annealed radial closure and quenched obstruction helpers."""

from __future__ import annotations

import math

import numpy as np


def expected_chi(df: int) -> float:
    k = int(df)
    if k < 0:
        raise ValueError("df must be nonnegative")
    if k == 0:
        return 0.0
    return math.sqrt(2.0) * math.exp(
        math.lgamma((k + 1.0) / 2.0) - math.lgamma(k / 2.0)
    )


def annealed_radius_multiplier(input_dim: int, output_width: int) -> float:
    d = int(input_dim)
    m = int(output_width)
    if d <= 0 or m <= 0:
        raise ValueError("dimensions must be positive")
    acc = 0.0
    denom = float(2**m)
    for k in range(1, m + 1):
        acc += math.comb(m, k) * expected_chi(k) / denom
    return math.sqrt(2.0 / d) * acc


def annealed_final_mean_from_state_radius(
    expected_radius: float, *, width: int, remaining_layers: int
) -> float:
    """Exact future-weight-annealed final coordinate mean.

    The supplied state is already after a realized layer. All remaining square
    width x width He-Gaussian matrices are averaged over.
    """
    n = int(width)
    r = int(remaining_layers)
    if n <= 0 or r <= 0 or expected_radius < 0.0:
        raise ValueError("invalid width/layer count/radius")
    multiplier = annealed_radius_multiplier(n, n)
    return (
        float(expected_radius)
        * (multiplier ** (r - 1))
        / math.sqrt(math.pi * n)
    )


def make_weights(
    *, seed: int, latent_dim: int, width: int, depth: int
) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights = [
        rng.standard_normal((latent_dim, width)).astype(np.float64)
        * math.sqrt(2.0 / latent_dim)
    ]
    for _ in range(1, depth):
        weights.append(
            rng.standard_normal((width, width)).astype(np.float64)
            * math.sqrt(2.0 / width)
        )
    return weights


def _roots_in_interval(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + 1e-12 < root < hi - 1e-12:
            roots.append(root)
    return roots


def _dedup(values: list[float]) -> list[float]:
    out: list[float] = []
    for value in sorted(values):
        if not out or abs(value - out[-1]) > 1e-11:
            out.append(value)
    return out


def _integrate_linear(coeff: np.ndarray, lo: float, hi: float) -> np.ndarray:
    a = coeff[:, 0]
    b = coeff[:, 1]
    return (
        a * (math.sin(hi) - math.sin(lo))
        + b * (-math.cos(hi) + math.cos(lo))
    )


def _integrate_norm_gauss_legendre(
    coeff: np.ndarray, lo: float, hi: float, order: int
) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    theta = 0.5 * (hi - lo) * nodes + 0.5 * (hi + lo)
    dirs = np.stack((np.cos(theta), np.sin(theta)), axis=0)
    vals = np.linalg.norm(coeff @ dirs, axis=0)
    return float(0.5 * (hi - lo) * np.dot(weights, vals))


def exact_angular_layers(
    weights: list[np.ndarray], *, radius_orders: tuple[int, int] = (64, 96)
) -> dict:
    """Exact sector propagation for a 2-D Gaussian input.

    Final coordinate means are analytic on sectors. Layer radius means use
    deterministic Gauss-Legendre integration of the exact sector representation.
    """
    if weights[0].shape[0] != 2:
        raise ValueError("exact angular helper requires latent_dim=2")

    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]
    e_r = math.sqrt(math.pi / 2.0)
    layers = []

    for layer_index, w in enumerate(weights):
        next_intervals: list[tuple[float, float, np.ndarray]] = []
        post_first_ang = np.zeros(w.shape[1], dtype=np.float64)

        for lo, hi, h_coeff in intervals:
            pre_coeff = w.T @ h_coeff
            boundaries = [lo, hi]
            for neuron in range(pre_coeff.shape[0]):
                boundaries.extend(
                    _roots_in_interval(
                        float(pre_coeff[neuron, 0]),
                        float(pre_coeff[neuron, 1]),
                        lo,
                        hi,
                    )
                )
            boundaries = _dedup(boundaries)
            for left, right in zip(boundaries[:-1], boundaries[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                direction = np.array(
                    [math.cos(mid), math.sin(mid)], dtype=np.float64
                )
                out_coeff = pre_coeff.copy()
                out_coeff[(pre_coeff @ direction) <= 0.0, :] = 0.0
                post_first_ang += _integrate_linear(out_coeff, left, right)
                next_intervals.append((left, right, out_coeff))

        radius_means = {}
        for order in radius_orders:
            angular_integral = sum(
                _integrate_norm_gauss_legendre(coeff, lo, hi, order)
                for lo, hi, coeff in next_intervals
            )
            radius_means[int(order)] = (
                e_r * angular_integral / (2.0 * math.pi)
            )

        post_mean = e_r * post_first_ang / (2.0 * math.pi)
        layers.append(
            {
                "layer": layer_index + 1,
                "interval_count": len(next_intervals),
                "post_mean": post_mean,
                "expected_radius": radius_means,
            }
        )
        intervals = next_intervals

    return {"layers": layers, "final_interval_count": len(intervals)}


def quenched_obstruction_certificate(weight: np.ndarray) -> dict:
    """Numerical certificate for the local rank obstruction on one fixed layer."""
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise ValueError("weight must be square")
    n = w.shape[0]
    rank = int(np.linalg.matrix_rank(w))
    h0 = np.linalg.solve(w.T, np.ones(n, dtype=np.float64))
    active = w.T @ h0
    residual = float(np.max(np.abs(active - 1.0)))

    h = np.arange(1.0, n + 1.0, dtype=np.float64)
    h /= np.linalg.norm(h)
    yp = np.maximum(w.T @ h, 0.0)
    ym = np.maximum(w.T @ (-h), 0.0)
    radius_delta = abs(float(np.linalg.norm(h)) - float(np.linalg.norm(-h)))
    output_delta = float(np.linalg.norm(yp - ym))

    return {
        "rank": rank,
        "dimension": n,
        "active_cone_residual": residual,
        "active_cone_min_preactivation": float(np.min(active)),
        "local_jacobian_rank": rank,
        "same_radius_delta": radius_delta,
        "same_radius_output_l2_delta": output_delta,
        "min_singular_value": float(np.linalg.svd(w, compute_uv=False)[-1]),
    }
