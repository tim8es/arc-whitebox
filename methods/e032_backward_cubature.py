from __future__ import annotations

import math

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

_MASK_SEEDS = (0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344)


def gaussian_radius_mean(width: int) -> float:
    if width <= 0:
        raise ValueError("width must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma((float(width) + 1.0) / 2.0) - math.lgamma(float(width) / 2.0)
    )


def _check_power_of_two(n: int) -> None:
    if n <= 0 or (n & (n - 1)) != 0:
        raise ValueError("width must be a positive power of two")


def _walsh(xp, n: int):
    _check_power_of_two(n)
    h = xp.ones((1, 1), dtype=xp.float64)
    size = 1
    while size < n:
        top = xp.concatenate([h, h], axis=1)
        bottom = xp.concatenate([h, -h], axis=1)
        h = xp.concatenate([top, bottom], axis=0)
        size *= 2
    return h


def _mask_values(n: int, seed: int) -> list[float]:
    x = int(seed) & 0xFFFFFFFF
    out: list[float] = []
    for _ in range(n):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        x &= 0xFFFFFFFF
        out.append(1.0 if (x & 1) else -1.0)
    return out


def build_base_points(xp, n: int):
    _check_power_of_two(n)
    h = _walsh(xp, n) * (1.0 / math.sqrt(float(n)))
    blocks = []
    for seed in _MASK_SEEDS:
        signs = xp.asarray(_mask_values(n, seed), dtype=xp.float64)
        blocks.append(h * signs[None, :])
    return xp.concatenate(blocks, axis=0)


def backward_probes(xp, weights, n_probes: int = 8):
    if not weights:
        raise ValueError("weights must be non-empty")
    n = int(weights[0].shape[0])
    if n_probes <= 0 or n_probes > n:
        raise ValueError("invalid n_probes")
    h = _walsh(xp, n)[:n_probes] * (1.0 / math.sqrt(float(n)))
    g = h
    for w in reversed(weights):
        g = (g @ w) * 0.5
    norms = xp.sqrt(xp.sum(g * g, axis=1, keepdims=True))
    return g / xp.maximum(norms, 1e-30)


def apply_reflections(xp, points, probes):
    x = points
    for j in range(int(probes.shape[0])):
        g = probes[j]
        coeff = x @ g
        x = x - coeff[:, None] * (2.0 * g[None, :])
    return x


def endpoint_support(xp, weights):
    n = int(weights[0].shape[0])
    base = build_base_points(xp, n)
    probes = backward_probes(xp, weights, n_probes=8)
    rotated = apply_reflections(xp, base, probes)
    return xp.concatenate([rotated, -rotated], axis=0)


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        weights = list(mlp.weights)
        n = int(mlp.width)
        support = endpoint_support(fnp, weights)
        x = support.T
        radial = gaussian_radius_mean(n)
        rows = []
        for w in weights:
            x = fnp.maximum(w @ x, 0.0)
            rows.append(fnp.mean(x, axis=1) * radial)
        return fnp.stack(rows, axis=0)
