from __future__ import annotations

from collections.abc import Callable

import numpy as np


Array = np.ndarray


def _canonicalize_columns(q: Array) -> Array:
    """Fix column signs deterministically without changing the represented subspace."""
    q = np.array(q, dtype=np.float64, copy=True)
    for j in range(q.shape[1]):
        i = int(np.argmax(np.abs(q[:, j])))
        if q[i, j] < 0:
            q[:, j] *= -1.0
    return q


def fixed_oversampled_basis(
    apply_g: Callable[[Array], Array],
    omega: Array,
    *,
    rank: int = 384,
    ell: int = 400,
) -> Array:
    """One-pass oversampled spectral range construction frozen for E022.

    The operator ``apply_g`` is called exactly once.  The returned basis is the
    top-``rank`` eigentruncation of H = Y.T @ Y with Y = G @ Omega.
    """
    omega = np.asarray(omega, dtype=np.float64)
    if omega.ndim != 2:
        raise ValueError("omega must be a matrix")
    if omega.shape[1] != ell:
        raise ValueError(f"omega must have ell={ell} columns")
    if not (0 < rank <= ell <= omega.shape[0]):
        raise ValueError("require 0 < rank <= ell <= ambient dimension")

    y = np.asarray(apply_g(omega), dtype=np.float64)
    if y.shape != omega.shape:
        raise ValueError("G@Omega must have the same shape as Omega")
    if not np.all(np.isfinite(y)):
        raise ValueError("non-finite Y")

    h = y.T @ y
    evals, evecs = np.linalg.eigh(h)
    idx = np.argsort(evals)[-rank:][::-1]
    lam = evals[idx]
    if np.any(lam <= 0.0) or not np.all(np.isfinite(lam)):
        raise ValueError("top-r H eigenvalues must be finite and strictly positive")
    v = evecs[:, idx]
    q = y @ (v / np.sqrt(lam))

    # Symmetric eigensolvers are deterministic up to signs. Canonicalize only
    # those signs; no jitter, clipping, QR fallback, or second G application.
    return _canonicalize_columns(q)


def q1_basis(apply_g: Callable[[Array], Array], omega: Array, *, rank: int = 384) -> Array:
    """Frozen V25 one-pass q1 comparator: Q = qr(G @ Omega)."""
    omega = np.asarray(omega, dtype=np.float64)
    if omega.ndim != 2 or omega.shape[1] != rank:
        raise ValueError("q1 omega must have exactly rank columns")
    y = np.asarray(apply_g(omega), dtype=np.float64)
    q, _ = np.linalg.qr(y, mode="reduced")
    return _canonicalize_columns(q[:, :rank])


def principal_subspace_error(q: Array, teacher: Array) -> float:
    """Normalized Frobenius projector distance used by the frozen E022 gate."""
    q = np.asarray(q, dtype=np.float64)
    teacher = np.asarray(teacher, dtype=np.float64)
    if q.ndim != 2 or teacher.ndim != 2 or q.shape != teacher.shape:
        raise ValueError("q and teacher must have the same 2-D shape")
    pq = q @ q.T
    pt = teacher @ teacher.T
    denom = np.linalg.norm(pt, ord="fro")
    if denom == 0.0:
        raise ValueError("teacher projector has zero norm")
    return float(np.linalg.norm(pq - pt, ord="fro") / denom)


def exact_top_eigenspace(g: Array, rank: int = 384) -> Array:
    """Dense diagnostic teacher only; never intended for estimator state."""
    g = np.asarray(g, dtype=np.float64)
    if g.ndim != 2 or g.shape[0] != g.shape[1] or rank > g.shape[0]:
        raise ValueError("invalid dense Gram shape/rank")
    evals, evecs = np.linalg.eigh((g + g.T) * 0.5)
    idx = np.argsort(evals)[-rank:][::-1]
    return _canonicalize_columns(evecs[:, idx])
