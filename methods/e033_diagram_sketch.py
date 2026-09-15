from __future__ import annotations

import numpy as np


def offdiag(a: np.ndarray) -> np.ndarray:
    x = np.asarray(a, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] != x.shape[1]:
        raise ValueError("a must be square")
    out = x.copy()
    np.fill_diagonal(out, 0.0)
    return out


def best_symmetric_rank_capture(a: np.ndarray, rank: int) -> float:
    x = np.asarray(a, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] != x.shape[1]:
        raise ValueError("a must be square")
    n = x.shape[0]
    if rank <= 0 or rank > n:
        raise ValueError("rank must be in 1..n")
    sym = 0.5 * (x + x.T)
    eig = np.linalg.eigvalsh(sym)
    energy = eig * eig
    total = float(np.sum(energy, dtype=np.float64))
    if total == 0.0:
        return 1.0
    kept = np.sort(energy)[-rank:]
    return float(np.sum(kept, dtype=np.float64) / total)


def hutchinson_bilinear(a: np.ndarray, p: np.ndarray, signs: np.ndarray) -> np.ndarray:
    a64 = np.asarray(a, dtype=np.float64)
    p64 = np.asarray(p, dtype=np.float64)
    s64 = np.asarray(signs, dtype=np.float64)
    if a64.ndim != 2 or p64.shape != a64.shape:
        raise ValueError("a and p must have matching (sources, width) shape")
    if s64.ndim != 2 or s64.shape[1] != a64.shape[0] or s64.shape[0] == 0:
        raise ValueError("signs must have shape (probes, sources)")
    ahat = s64 @ a64
    phat = s64 @ p64
    return (ahat.T @ phat) / float(s64.shape[0])
