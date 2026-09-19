"""E108 exact-mean first-layer transported control-variate helpers."""

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
    """Frozen E104 law: two independent Haar blocks, analytic radius, exact antipodes."""
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


def first_layer_exact_mean_billed(weight0):
    """Exact E[ReLU(X @ W0.T)] for X~N(0,I), coordinatewise."""
    w = fnp.asarray(weight0, dtype=fnp.float32)
    if len(w.shape) != 2 or w.shape[0] != w.shape[1]:
        raise ValueError("weight0 must be square")
    row_sq = fnp.multiply(w, w)
    row_norm = fnp.sqrt(fnp.sum(row_sq, axis=1, dtype=fnp.float64))
    return row_norm / math.sqrt(2.0 * math.pi)


def build_meanfield_transport_billed(weights: Sequence):
    """Return product (0.5 W2.T)...(0.5 WL.T) for row-vector perturbations."""
    if len(weights) < 2:
        raise ValueError("at least two layers are required")
    first = fnp.swapaxes(fnp.asarray(weights[1], dtype=fnp.float32), 0, 1)
    transport = fnp.multiply(first, fnp.float32(0.5))
    for raw_w in weights[2:]:
        w_t = fnp.swapaxes(fnp.asarray(raw_w, dtype=fnp.float32), 0, 1)
        transport = fnp.matmul(
            transport,
            fnp.multiply(w_t, fnp.float32(0.5)),
        )
    return transport


def pair_first_layer_blocks_billed(h1, width: int):
    """Pair +/- first-layer activations into the two independent Haar blocks."""
    n = int(width)
    x = fnp.asarray(h1, dtype=fnp.float32)
    if x.shape != (4 * n, n):
        raise ValueError(f"unexpected first-layer shape {x.shape}")
    block1 = fnp.multiply(
        fnp.add(x[:n], x[2 * n : 3 * n]), fnp.float32(0.5)
    )
    block2 = fnp.multiply(
        fnp.add(x[n : 2 * n], x[3 * n : 4 * n]), fnp.float32(0.5)
    )
    return block1, block2


def transported_controls_billed(block1, block2, exact_mean, transport):
    f1 = fnp.asarray(block1, dtype=fnp.float32)
    f2 = fnp.asarray(block2, dtype=fnp.float32)
    mu = fnp.asarray(exact_mean, dtype=fnp.float64)
    t = fnp.asarray(transport, dtype=fnp.float32)
    if f1.shape != f2.shape or len(f1.shape) != 2:
        raise ValueError("paired first-layer blocks must match")
    centered1 = f1 - mu
    centered2 = f2 - mu
    z1 = fnp.matmul(centered1, t)
    z2 = fnp.matmul(centered2, t)
    return z1, z2


def final_pair_blocks_billed(hfinal, width: int):
    n = int(width)
    y = fnp.asarray(hfinal, dtype=fnp.float32)
    if y.shape != (4 * n, n):
        raise ValueError(f"unexpected final-layer shape {y.shape}")
    y1 = fnp.multiply(
        fnp.add(y[:n], y[2 * n : 3 * n]), fnp.float32(0.5)
    )
    y2 = fnp.multiply(
        fnp.add(y[n : 2 * n], y[3 * n : 4 * n]), fnp.float32(0.5)
    )
    return y1, y2


def crossfit_scalar_correct_billed(y1, y2, z1, z2):
    """Unbiased symmetric cross-fit with one transported control per output."""
    a = fnp.asarray(y1, dtype=fnp.float32)
    b = fnp.asarray(y2, dtype=fnp.float32)
    u = fnp.asarray(z1, dtype=fnp.float32)
    v = fnp.asarray(z2, dtype=fnp.float32)
    if a.shape != b.shape or u.shape != v.shape or a.shape != u.shape:
        raise ValueError("response/control block shapes must match")

    a_mean = fnp.mean(a, axis=0, dtype=fnp.float64)
    b_mean = fnp.mean(b, axis=0, dtype=fnp.float64)
    u_mean = fnp.mean(u, axis=0, dtype=fnp.float64)
    v_mean = fnp.mean(v, axis=0, dtype=fnp.float64)

    ac = a - a_mean
    bc = b - b_mean
    uc = u - u_mean
    vc = v - v_mean

    num1 = fnp.sum(fnp.multiply(uc, ac), axis=0, dtype=fnp.float64)
    num2 = fnp.sum(fnp.multiply(vc, bc), axis=0, dtype=fnp.float64)
    den1 = fnp.sum(fnp.multiply(uc, uc), axis=0, dtype=fnp.float64)
    den2 = fnp.sum(fnp.multiply(vc, vc), axis=0, dtype=fnp.float64)

    beta1 = num1 / den1
    beta2 = num2 / den2

    corrected1 = a_mean - fnp.multiply(beta2, u_mean)
    corrected2 = b_mean - fnp.multiply(beta1, v_mean)
    candidate = fnp.multiply(corrected1 + corrected2, 0.5)
    baseline = fnp.multiply(a_mean + b_mean, 0.5)
    return candidate, baseline, beta1, beta2
