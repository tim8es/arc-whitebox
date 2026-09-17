"""E103 package implementation of the frozen E100 orthogonal sampler."""

from __future__ import annotations

import math
import time
from typing import Sequence

import flopscope.numpy as fnp
import numpy as np
from whestbench import BaseEstimator, SetupContext

PRODUCTION_SAMPLES = 4096


def _validate(width: int, total_samples: int) -> None:
    if width <= 0:
        raise ValueError("width must be positive")
    if total_samples <= 0 or total_samples % (2 * width):
        raise ValueError("total_samples must be divisible by 2*width")


def orthogonal_antithetic_numpy(width: int, total_samples: int, seed: int) -> np.ndarray:
    """Reference generator for tests/diagnostics; same frozen arithmetic as E100."""
    n = int(width)
    total = int(total_samples)
    _validate(n, total)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    blocks = []
    for _ in range(total // (2 * n)):
        g = rng.standard_normal((n, n)).astype(np.float64)
        q, r = np.linalg.qr(g)
        diag = np.diag(r)
        signs = np.where(diag < 0.0, -1.0, 1.0)
        q = q * signs[None, :]
        radii = np.sqrt(rng.chisquare(df=n, size=n)).astype(np.float64)
        blocks.append((radii[:, None] * q).astype(np.float32))
    pos = np.concatenate(blocks, axis=0)
    return np.concatenate((pos, -pos), axis=0)


def orthogonal_antithetic_billed(width: int, total_samples: int, seed: int):
    """Flopscope-billed generator used by the estimator.

    Random-number draws themselves are not arithmetic FLOPs; QR, sign/radial
    transforms, scaling, concatenation and downstream network arithmetic use
    flopscope.numpy.
    """
    n = int(width)
    total = int(total_samples)
    _validate(n, total)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    blocks = []
    for _ in range(total // (2 * n)):
        g = fnp.asarray(rng.standard_normal((n, n)).astype(np.float64))
        q, r = fnp.linalg.qr(g)
        diag = fnp.diag(r)
        signs = fnp.where(diag < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        chi = fnp.asarray(rng.chisquare(df=n, size=n).astype(np.float64))
        radii = fnp.sqrt(chi)
        block = fnp.multiply(radii[:, None], q).astype(fnp.float32)
        blocks.append(block)
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def propagate_numpy(weights: Sequence[np.ndarray], inputs: np.ndarray) -> np.ndarray:
    """Direct row-vector reference: h <- ReLU(h @ W)."""
    h = np.asarray(inputs, dtype=np.float32).copy()
    rows = []
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float32)
        h = h @ w
        np.maximum(h, np.float32(0.0), out=h)
        rows.append(np.mean(h, axis=0, dtype=np.float64))
    return np.stack(rows, axis=0)


class OrthogonalAntitheticEstimator(BaseEstimator):
    """Frozen N=4096 unbiased sampling estimator."""

    def __init__(self) -> None:
        self._seed = 0
        self._last_wall_s = None

    def setup(self, ctx: SetupContext) -> None:
        self._seed = int(ctx.seed)

    def predict(self, mlp, budget: int):
        _ = budget
        n = int(mlp.width)
        if int(mlp.depth) != len(mlp.weights):
            raise ValueError("mlp.depth must equal len(mlp.weights)")
        _validate(n, PRODUCTION_SAMPLES)
        started = time.perf_counter()
        h = orthogonal_antithetic_billed(n, PRODUCTION_SAMPLES, self._seed)
        rows = []
        for raw_w in mlp.weights:
            w = fnp.asarray(np.asarray(raw_w, dtype=np.float32))
            h = fnp.matmul(h, w)
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
        self._last_wall_s = time.perf_counter() - started
        return fnp.stack(rows, axis=0)

    def teardown(self) -> None:
        return None


Estimator = OrthogonalAntitheticEstimator
