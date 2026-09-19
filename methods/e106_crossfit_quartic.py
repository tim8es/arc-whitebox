"""E106 cross-fitted quartic spherical control variate helpers."""

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


def quartic_features_billed(q, directions):
    qf = fnp.asarray(q, dtype=fnp.float32)
    uf = fnp.asarray(directions, dtype=fnp.float32)
    if len(qf.shape) != 2 or len(uf.shape) != 2 or qf.shape[1] != uf.shape[1]:
        raise ValueError("q and directions must be 2D with equal ambient dimension")
    n = int(qf.shape[1])
    proj = fnp.matmul(qf, fnp.swapaxes(uf, 0, 1))
    sq = fnp.multiply(proj, proj)
    fourth = fnp.multiply(sq, sq)
    return fourth - (3.0 / float(n * (n + 2)))


def crossfit_correct_billed(g1, g2, z1, z2):
    y1 = fnp.asarray(g1, dtype=fnp.float32)
    y2 = fnp.asarray(g2, dtype=fnp.float32)
    f1 = fnp.asarray(z1, dtype=fnp.float32)
    f2 = fnp.asarray(z2, dtype=fnp.float32)
    if y1.shape != y2.shape or f1.shape != f2.shape or y1.shape[0] != f1.shape[0]:
        raise ValueError("cross-fit blocks must have matching sample dimensions")

    b1 = fnp.mean(y1, axis=0, dtype=fnp.float64)
    b2 = fnp.mean(y2, axis=0, dtype=fnp.float64)

    z1m = fnp.mean(f1, axis=0)
    z2m = fnp.mean(f2, axis=0)
    y1m = fnp.mean(y1, axis=0)
    y2m = fnp.mean(y2, axis=0)

    z1c = f1 - z1m
    z2c = f2 - z2m
    y1c = y1 - y1m
    y2c = y2 - y2m

    num1 = fnp.matmul(fnp.swapaxes(z1c, 0, 1), y1c)
    num2 = fnp.matmul(fnp.swapaxes(z2c, 0, 1), y2c)
    den1 = fnp.sum(fnp.multiply(z1c, z1c), axis=0)
    den2 = fnp.sum(fnp.multiply(z2c, z2c), axis=0)

    beta1 = num1 / fnp.reshape(den1, (-1, 1))
    beta2 = num2 / fnp.reshape(den2, (-1, 1))

    correction1 = fnp.sum(beta2 * fnp.reshape(z1m, (-1, 1)), axis=0)
    correction2 = fnp.sum(beta1 * fnp.reshape(z2m, (-1, 1)), axis=0)

    corrected1 = b1 - correction1
    corrected2 = b2 - correction2
    candidate = (corrected1 + corrected2) * 0.5
    baseline = (b1 + b2) * 0.5
    return candidate, baseline
