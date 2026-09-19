"""E109 spherical-Stein Jacobian control-variate helpers."""

from __future__ import annotations

import math

import flopscope.numpy as fnp


def mean_chi_radius(width: int) -> float:
    n = int(width)
    if n <= 0:
        raise ValueError("width must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0)
    )


def build_two_haar_inputs_billed(width: int, seed: int):
    n = int(width)
    rng = fnp.random.default_rng(int(seed))
    radius = mean_chi_radius(n)
    blocks = []
    for _ in range(2):
        g = rng.standard_normal((n, n))
        q, r = fnp.linalg.qr(g)
        signs = fnp.where(fnp.diag(r) < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        blocks.append(fnp.multiply(q, radius).astype(fnp.float32))
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def spherical_stein_control_billed(g, dg_tangent, q_dot_u, width: int):
    y = fnp.asarray(g, dtype=fnp.float32)
    dy = fnp.asarray(dg_tangent, dtype=fnp.float32)
    s = fnp.asarray(q_dot_u, dtype=fnp.float32)
    return dy - (float(width - 1) * fnp.reshape(s, (-1, 1)) * y)


def crossfit_scalar_control_billed(g1, g2, c1, c2):
    y1 = fnp.asarray(g1, dtype=fnp.float32)
    y2 = fnp.asarray(g2, dtype=fnp.float32)
    z1 = fnp.asarray(c1, dtype=fnp.float32)
    z2 = fnp.asarray(c2, dtype=fnp.float32)
    if y1.shape != y2.shape or z1.shape != z2.shape or y1.shape != z1.shape:
        raise ValueError("all cross-fit arrays must have the same shape")

    b1 = fnp.mean(y1, axis=0, dtype=fnp.float64)
    b2 = fnp.mean(y2, axis=0, dtype=fnp.float64)
    y1m = fnp.mean(y1, axis=0)
    y2m = fnp.mean(y2, axis=0)
    z1m = fnp.mean(z1, axis=0)
    z2m = fnp.mean(z2, axis=0)
    y1c = y1 - y1m
    y2c = y2 - y2m
    z1c = z1 - z1m
    z2c = z2 - z2m
    num1 = fnp.sum(fnp.multiply(z1c, y1c), axis=0)
    num2 = fnp.sum(fnp.multiply(z2c, y2c), axis=0)
    den1 = fnp.sum(fnp.multiply(z1c, z1c), axis=0)
    den2 = fnp.sum(fnp.multiply(z2c, z2c), axis=0)
    beta1 = num1 / den1
    beta2 = num2 / den2
    corrected1 = b1 - beta2 * z1m
    corrected2 = b2 - beta1 * z2m
    candidate = (corrected1 + corrected2) * 0.5
    baseline = (b1 + b2) * 0.5
    return candidate, baseline, beta1, beta2
