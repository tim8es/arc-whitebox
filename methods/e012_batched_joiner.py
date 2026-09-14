from __future__ import annotations

import flopscope.numpy as fnp


def candidate_scratch_bytes(n: int, rank: int, dtype_bytes: int = 4) -> int:
    """Persistent E012 scratch: inner and outer, each shaped (2, n, rank)."""
    return 2 * 2 * n * rank * dtype_bytes


def _check_inputs(ap, weights, omega) -> tuple[int, int]:
    if ap.ndim != 3 or ap.shape[0] != 2 or ap.shape[1] != ap.shape[2]:
        raise ValueError("ap must have shape (2, n, n)")
    n = ap.shape[1]
    if weights.shape != (2, n, 1):
        raise ValueError("weights must have shape (2, n, 1)")
    if omega.ndim != 2 or omega.shape[0] != n:
        raise ValueError("omega must have shape (n, rank)")
    return n, omega.shape[1]


def _scratch(ap, n: int, rank: int, inner, outer, out):
    if inner is None:
        inner = fnp.empty((2, n, rank), dtype=ap.dtype)
    if outer is None:
        outer = fnp.empty((2, n, rank), dtype=ap.dtype)
    if out is None:
        out = fnp.empty((n, rank), dtype=ap.dtype)
    return inner, outer, out


def joiner_separate(ap, weights, omega, *, inner=None, outer=None, out=None):
    """Frozen comparator: A and P weighted Gram actions as separate calls."""
    n, rank = _check_inputs(ap, weights, omega)
    inner, outer, out = _scratch(ap, n, rank, inner, outer, out)

    fnp.matmul(fnp.swapaxes(ap[0], -1, -2), omega, out=inner[0])
    fnp.multiply(inner[0], weights[0], out=inner[0])
    fnp.matmul(ap[0], inner[0], out=outer[0])

    fnp.matmul(fnp.swapaxes(ap[1], -1, -2), omega, out=inner[1])
    fnp.multiply(inner[1], weights[1], out=inner[1])
    fnp.matmul(ap[1], inner[1], out=outer[1])

    fnp.add(outer[0], outer[1], out=out)
    return out


def joiner_batched(ap, weights, omega, *, inner=None, outer=None, out=None):
    """E012 candidate: identical A/P actions with a leading batch dimension."""
    n, rank = _check_inputs(ap, weights, omega)
    inner, outer, out = _scratch(ap, n, rank, inner, outer, out)

    fnp.matmul(fnp.swapaxes(ap, -1, -2), omega, out=inner)
    fnp.multiply(inner, weights, out=inner)
    fnp.matmul(ap, inner, out=outer)
    fnp.add(outer[0], outer[1], out=out)
    return out
