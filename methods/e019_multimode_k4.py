"""E019 pooled multi-mode residual closure for memoryless K4 regeneration."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np

MODE_NAMES = ("cc", "k21", "t", "vv", "k31", "k22", "mc", "mm")


def _as64(value) -> np.ndarray:
    out = np.asarray(value, dtype=np.float64)
    if not np.all(np.isfinite(out)):
        raise ValueError("E019 inputs must be finite")
    return out


def _sym(a: np.ndarray) -> np.ndarray:
    return 0.5 * (a + a.T)


def _zero_diag(a: np.ndarray) -> np.ndarray:
    out = np.asarray(a, dtype=np.float64).copy()
    np.fill_diagonal(out, 0.0)
    return out


def _validate_live(live: Mapping[str, np.ndarray]) -> int:
    required = ("C", "mu", "var", "K21", "K3v", "K31", "K22")
    missing = [key for key in required if key not in live]
    if missing:
        raise KeyError(f"missing E019 live fields: {missing}")
    c = _as64(live["C"])
    if c.ndim != 2 or c.shape[0] != c.shape[1]:
        raise ValueError("C must be square")
    n = c.shape[0]
    for key in ("K21", "K31", "K22"):
        value = _as64(live[key])
        if value.shape != (n, n):
            raise ValueError(f"{key} must have shape {(n, n)}")
    for key in ("mu", "var", "K3v"):
        value = _as64(live[key])
        if value.shape != (n,):
            raise ValueError(f"{key} must have shape {(n,)}")
    return n


def mode_matrix(name: str, live: Mapping[str, np.ndarray]) -> np.ndarray:
    """Build one frozen F68 live mode, always with an exact zero diagonal."""
    _validate_live(live)
    c = _as64(live["C"])
    mu = _as64(live["mu"])
    var = _as64(live["var"])
    k21 = _as64(live["K21"])
    k3v = _as64(live["K3v"])
    k31 = _as64(live["K31"])
    k22 = _as64(live["K22"])

    if name == "cc":
        raw = c * c
    elif name == "k21":
        raw = _sym(mu[:, None] * k21.T)
    elif name == "t":
        raw = _sym(k3v[:, None] * mu[None, :])
    elif name == "vv":
        raw = var[:, None] * var[None, :]
    elif name == "k31":
        raw = _sym(k31)
    elif name == "k22":
        raw = k22
    elif name == "mc":
        raw = _sym(mu[:, None] * c)
    elif name == "mm":
        raw = mu[:, None] * mu[None, :]
    else:
        raise ValueError(f"unknown E019 mode: {name}")
    out = _zero_diag(raw)
    if not np.all(np.isfinite(out)):
        raise ValueError(f"non-finite E019 mode: {name}")
    return out


def streamed_mode_sum(live: Mapping[str, np.ndarray], coefficients) -> np.ndarray:
    """Stream the fixed eight modes through one accumulator; no mode bank is kept."""
    n = _validate_live(live)
    coeff = _as64(coefficients)
    if coeff.shape != (len(MODE_NAMES),):
        raise ValueError(f"coefficients must have shape {(len(MODE_NAMES),)}")
    acc = np.zeros((n, n), dtype=np.float64)
    for weight, name in zip(coeff, MODE_NAMES, strict=True):
        mode = mode_matrix(name, live)
        acc += float(weight) * mode
    np.fill_diagonal(acc, 0.0)
    if not np.all(np.isfinite(acc)):
        raise ValueError("non-finite E019 correction")
    return acc


def fit_pooled_coefficients(
    samples: Iterable[tuple[np.ndarray, Mapping[str, np.ndarray]]],
) -> np.ndarray:
    """Fit one shared coefficient vector using pooled Frobenius normal equations."""
    p = len(MODE_NAMES)
    gram = np.zeros((p, p), dtype=np.float64)
    rhs = np.zeros(p, dtype=np.float64)
    count = 0
    for residual, live in samples:
        target = _zero_diag(_as64(residual))
        n = _validate_live(live)
        if target.shape != (n, n):
            raise ValueError("residual/live shape mismatch")
        modes = [mode_matrix(name, live) for name in MODE_NAMES]
        for i, left in enumerate(modes):
            rhs[i] += float(np.vdot(left, target).real)
            for j in range(i, p):
                value = float(np.vdot(left, modes[j]).real)
                gram[i, j] += value
                if i != j:
                    gram[j, i] += value
        count += 1
    if count == 0:
        raise ValueError("at least one E019 fit sample is required")
    if not np.all(np.isfinite(gram)) or not np.all(np.isfinite(rhs)):
        raise ValueError("non-finite E019 normal equations")
    if np.linalg.matrix_rank(gram) != p:
        raise np.linalg.LinAlgError("E019 pooled mode Gram is rank-deficient")
    coefficients = np.linalg.solve(gram, rhs)
    if not np.all(np.isfinite(coefficients)):
        raise ValueError("non-finite E019 coefficients")
    return coefficients


def apply_closure(
    baseline_off: np.ndarray,
    live: Mapping[str, np.ndarray],
    coefficients,
    diagonal: np.ndarray,
) -> np.ndarray:
    """Add the E019 residual correction while preserving the exact K4 diagonal."""
    n = _validate_live(live)
    base = _zero_diag(_as64(baseline_off))
    diag = _as64(diagonal)
    if base.shape != (n, n) or diag.shape != (n,):
        raise ValueError("E019 closure shape mismatch")
    out = base + streamed_mode_sum(live, coefficients)
    np.fill_diagonal(out, diag)
    if not np.all(np.isfinite(out)):
        raise ValueError("non-finite E019 closure")
    return out
