from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def build_q(dg: np.ndarray, var: np.ndarray) -> np.ndarray:
    """Neuron-resolved fourth-order residual from the frozen E016 memo."""
    dg64 = np.asarray(dg, dtype=np.float64)
    var64 = np.asarray(var, dtype=np.float64)
    if dg64.shape != var64.shape or dg64.ndim != 1:
        raise ValueError("dg and var must be matching vectors")
    mean_var = float(np.mean(var64))
    denom = float(np.sqrt(np.mean(var64 * var64)))
    if not np.isfinite(mean_var) or not np.isfinite(denom) or mean_var == 0.0 or denom == 0.0:
        raise ValueError("non-finite or zero variance scale")
    rho = float(np.mean(dg64)) / mean_var
    q = (dg64 - rho * var64) / denom
    if not np.all(np.isfinite(q)):
        raise ValueError("non-finite q")
    return q


def offdiag_outer(q: np.ndarray) -> np.ndarray:
    q64 = np.asarray(q, dtype=np.float64)
    out = np.outer(q64, q64)
    np.fill_diagonal(out, 0.0)
    return out


def fit_gamma(samples: Iterable[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]]) -> float:
    """One global scalar for one layer, pooled over fit MLPs by Frobenius LS."""
    numer = 0.0
    denom = 0.0
    count = 0
    for teacher, c_off, dg, var, lam in samples:
        teacher64 = np.asarray(teacher, dtype=np.float64)
        c64 = np.asarray(c_off, dtype=np.float64)
        if teacher64.shape != c64.shape or teacher64.ndim != 2 or teacher64.shape[0] != teacher64.shape[1]:
            raise ValueError("teacher and c_off must be matching square matrices")
        q = build_q(dg, var)
        basis = offdiag_outer(q)
        residual = teacher64 - float(lam) * c64
        numer += float(np.sum(basis * residual, dtype=np.float64))
        denom += float(np.sum(basis * basis, dtype=np.float64))
        count += 1
    if count == 0 or denom == 0.0 or not np.isfinite(denom):
        raise ValueError("degenerate gamma fit")
    gamma = numer / denom
    if not np.isfinite(gamma):
        raise ValueError("non-finite gamma")
    return float(gamma)


def apply_rank1_mode(
    c_off: np.ndarray,
    dg: np.ndarray,
    var: np.ndarray,
    *,
    lam: float,
    gamma: float,
) -> np.ndarray:
    c64 = np.asarray(c_off, dtype=np.float64)
    q = build_q(dg, var)
    out = float(lam) * c64 + float(gamma) * offdiag_outer(q)
    np.fill_diagonal(out, 0.0)
    if not np.all(np.isfinite(out)):
        raise ValueError("non-finite closure")
    return out
