"""E105 target-free two-Haar-block risk certificate helpers."""

from __future__ import annotations

import math

import flopscope.numpy as fnp
import numpy as np


def mean_chi_radius(width: int) -> float:
    n = int(width)
    if n <= 0:
        raise ValueError("width must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0)
    )


def build_two_haar_inputs_billed(width: int, seed: int):
    """Exact E104 two-Haar-block law with all Gaussian RNG generated under flopscope."""
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


def two_block_statistics(block1: np.ndarray, block2: np.ndarray) -> tuple[np.ndarray, float]:
    """Return the two-block mean and unbiased target-free raw-MSE risk estimator."""
    b1 = np.asarray(block1, dtype=np.float64)
    b2 = np.asarray(block2, dtype=np.float64)
    if b1.shape != b2.shape:
        raise ValueError("block means must have identical shapes")
    estimate = (b1 + b2) / 2.0
    delta = b1 - b2
    risk = float(np.mean(delta * delta) / 4.0)
    return estimate, risk
