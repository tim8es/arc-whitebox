"""E109 late-prefix gate-pair sign control-variate helpers."""

from __future__ import annotations

import math
from typing import Sequence

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
    if n <= 0:
        raise ValueError("width must be positive")
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


def sign_pair_mean(rho: float) -> float:
    r = max(-1.0, min(1.0, float(rho)))
    return (2.0 / math.pi) * math.asin(r)


def build_late_prefix_directions_billed(
    weights: Sequence,
    *,
    layer: int,
    rows: int,
):
    """Mean-field prefix rows as normalized input-space late gate normals.

    layer is one-indexed. For layer ell:
      P_ell = (0.5 W_ell)...(0.5 W_2) W_1.
    """
    if layer < 1 or layer > len(weights):
        raise ValueError("invalid layer")
    first = fnp.asarray(weights[0], dtype=fnp.float32)
    if len(first.shape) != 2 or first.shape[0] != first.shape[1]:
        raise ValueError("weights must be square")
    n = int(first.shape[0])
    if rows <= 0 or rows > n or rows % 2:
        raise ValueError("rows must be positive, even, and <= width")

    prefix = first
    for raw_w in weights[1:layer]:
        w = fnp.asarray(raw_w, dtype=fnp.float32)
        prefix = fnp.matmul(fnp.multiply(w, fnp.float32(0.5)), prefix)

    u = prefix[:rows]
    norm = fnp.sqrt(fnp.sum(fnp.multiply(u, u), axis=1))
    return u / fnp.reshape(norm, (-1, 1))


def gatepair_features_billed(q, directions):
    """Centered pairwise sign controls with exact spherical means."""
    x = fnp.asarray(q, dtype=fnp.float32)
    u = fnp.asarray(directions, dtype=fnp.float32)
    if len(x.shape) != 2 or len(u.shape) != 2 or x.shape[1] != u.shape[1]:
        raise ValueError("q and directions must be 2D with equal ambient dimension")
    if u.shape[0] % 2:
        raise ValueError("direction count must be even")

    proj = fnp.matmul(x, fnp.swapaxes(u, 0, 1))
    s = fnp.where(proj >= 0.0, fnp.float32(1.0), fnp.float32(-1.0))
    pair_prod = fnp.multiply(s[:, 0::2], s[:, 1::2])

    rho = fnp.sum(fnp.multiply(u[0::2], u[1::2]), axis=1)
    rho = fnp.minimum(fnp.maximum(rho, fnp.float32(-1.0)), fnp.float32(1.0))
    means = fnp.multiply(fnp.arcsin(rho), fnp.float32(2.0 / math.pi))
    return pair_prod - means, means


def crossfit_correct_billed(y1, y2, z1, z2):
    """Symmetric cross-fit; coefficients are learned only on the opposite block."""
    a = fnp.asarray(y1, dtype=fnp.float32)
    b = fnp.asarray(y2, dtype=fnp.float32)
    f1 = fnp.asarray(z1, dtype=fnp.float32)
    f2 = fnp.asarray(z2, dtype=fnp.float32)
    if a.shape != b.shape or f1.shape != f2.shape or a.shape[0] != f1.shape[0]:
        raise ValueError("cross-fit blocks must have matching sample dimensions")

    a_mean = fnp.mean(a, axis=0, dtype=fnp.float64)
    b_mean = fnp.mean(b, axis=0, dtype=fnp.float64)
    z1_mean = fnp.mean(f1, axis=0, dtype=fnp.float64)
    z2_mean = fnp.mean(f2, axis=0, dtype=fnp.float64)

    ac = a - a_mean
    bc = b - b_mean
    z1c = f1 - z1_mean
    z2c = f2 - z2_mean

    num1 = fnp.matmul(fnp.swapaxes(z1c, 0, 1), ac)
    num2 = fnp.matmul(fnp.swapaxes(z2c, 0, 1), bc)
    den1 = fnp.sum(fnp.multiply(z1c, z1c), axis=0, dtype=fnp.float64)
    den2 = fnp.sum(fnp.multiply(z2c, z2c), axis=0, dtype=fnp.float64)

    nz1 = den1 > 0.0
    nz2 = den2 > 0.0
    den1_safe = fnp.where(nz1, den1, fnp.float64(1.0))
    den2_safe = fnp.where(nz2, den2, fnp.float64(1.0))
    beta1 = num1 / fnp.reshape(den1_safe, (-1, 1))
    beta2 = num2 / fnp.reshape(den2_safe, (-1, 1))
    beta1 = fnp.where(fnp.reshape(nz1, (-1, 1)), beta1, fnp.float64(0.0))
    beta2 = fnp.where(fnp.reshape(nz2, (-1, 1)), beta2, fnp.float64(0.0))

    correction1 = fnp.sum(beta2 * fnp.reshape(z1_mean, (-1, 1)), axis=0)
    correction2 = fnp.sum(beta1 * fnp.reshape(z2_mean, (-1, 1)), axis=0)

    corrected1 = a_mean - correction1
    corrected2 = b_mean - correction2
    candidate = fnp.multiply(corrected1 + corrected2, 0.5)
    baseline = fnp.multiply(a_mean + b_mean, 0.5)
    return candidate, baseline, beta1, beta2


def final_pair_blocks_billed(hfinal, width: int):
    n = int(width)
    y = fnp.asarray(hfinal, dtype=fnp.float32)
    if y.shape != (4 * n, n):
        raise ValueError(f"unexpected final-layer shape {y.shape}")
    y1 = fnp.multiply(y[:n] + y[2 * n : 3 * n], fnp.float32(0.5))
    y2 = fnp.multiply(y[n : 2 * n] + y[3 * n : 4 * n], fnp.float32(0.5))
    return y1, y2
