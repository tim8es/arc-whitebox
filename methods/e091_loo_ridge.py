"""E091 target-free feature map and exact ridge/LOO algebra.

Synthetic/local reproducibility support only. No benchmark/public target access.
"""

from __future__ import annotations

import numpy as np

FEATURE_DIM = 12
RIDGE_LAMBDA = 1.0


def build_features(weights, base_prediction, state_var, state_d3):
    """Frozen p=12 target-free feature map from E091_FEATURE_FREEZE.md."""
    w = np.asarray(weights[-1], dtype=np.float64)
    b = np.asarray(base_prediction, dtype=np.float64)
    v = np.asarray(state_var, dtype=np.float64)
    d3 = np.asarray(state_d3, dtype=np.float64)
    x = np.asarray(
        [
            1.0,
            np.mean(b),
            np.std(b),
            np.mean(np.abs(b)),
            np.sqrt(np.mean(b * b)),
            np.mean(w),
            np.std(w),
            np.mean(np.abs(w)),
            np.sqrt(np.mean(w * w)),
            np.mean(v),
            np.std(v),
            np.mean(np.abs(d3)),
        ],
        dtype=np.float64,
    )
    if x.shape != (FEATURE_DIM,):
        raise ValueError(f"feature shape {x.shape} != {(FEATURE_DIM,)}")
    if not np.isfinite(x).all():
        raise ValueError("non-finite E091 feature")
    return x


def ridge_fit(X, Z, lam: float = RIDGE_LAMBDA):
    X = np.asarray(X, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.float64)
    if X.ndim != 2 or Z.ndim != 2 or X.shape[0] != Z.shape[0]:
        raise ValueError("X/Z shape mismatch")
    if lam <= 0.0:
        raise ValueError("ridge lambda must be positive")
    A = X.T @ X + float(lam) * np.eye(X.shape[1], dtype=np.float64)
    B = np.linalg.solve(A, X.T @ Z)
    return B, A


def press_loo_predictions(X, Z, lam: float = RIDGE_LAMBDA):
    """Exact leave-one-out residual predictions via PRESS/Sherman-Morrison."""
    X = np.asarray(X, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.float64)
    B, A = ridge_fit(X, Z, lam)
    Ainv_XT = np.linalg.solve(A, X.T)
    h = np.einsum("ij,ji->i", X, Ainv_XT)
    denom = 1.0 - h
    if np.min(denom) < 1e-6:
        raise ValueError("E091 leverage denominator gate failed")
    zhat = X @ B
    e = Z - zhat
    loo = zhat - (h / denom)[:, None] * e
    return loo, h, B


def direct_loo_predictions(X, Z, lam: float = RIDGE_LAMBDA):
    X = np.asarray(X, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.float64)
    out = np.empty_like(Z)
    for i in range(X.shape[0]):
        keep = np.arange(X.shape[0]) != i
        Bi, _ = ridge_fit(X[keep], Z[keep], lam)
        out[i] = X[i] @ Bi
    return out


def deploy_correction(x, B_frozen):
    x = np.asarray(x, dtype=np.float64)
    B = np.asarray(B_frozen, dtype=np.float64)
    if x.shape != (B.shape[0],):
        raise ValueError("feature/coefficient shape mismatch")
    return x @ B
