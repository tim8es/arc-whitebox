from __future__ import annotations

import numpy as np

RANK = 8

_ANCHOR = (
    "                lam_prev = float(LAM[min(li, len(LAM) - 1)])\n"
)
_MARKER = (
    "                if _os.environ.get(\"E031_DEBUG\", \"0\") == \"1\":\n"
    "                    DEBUG.append(dict(e031_layer=li, K22=K22, g_prev=g_prev))\n"
)


def best_rank(matrix: np.ndarray, rank: int = RANK) -> tuple[np.ndarray, float]:
    matrix = np.asarray(matrix, dtype=np.float64)
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    r = min(int(rank), s.size)
    approx = (u[:, :r] * s[:r]) @ vh[:r]
    denom = float(np.dot(s, s))
    retained = 1.0 if denom == 0.0 else float(np.dot(s[:r], s[:r]) / denom)
    return approx, retained


def transported_relative_error(
    w2: np.ndarray, exact_residual: np.ndarray, approx_residual: np.ndarray
) -> float:
    w2 = np.asarray(w2, dtype=np.float64)
    exact = w2 @ np.asarray(exact_residual, dtype=np.float64) @ w2.T
    approx = w2 @ np.asarray(approx_residual, dtype=np.float64) @ w2.T
    denom = float(np.linalg.norm(exact))
    num = float(np.linalg.norm(exact - approx))
    return 0.0 if denom == 0.0 and num == 0.0 else num / max(denom, np.finfo(np.float64).tiny)


def instrument_v25_source(source: str) -> tuple[str, str]:
    if source.count(_ANCHOR) != 1:
        raise ValueError(f"expected one V25 instrumentation anchor, got {source.count(_ANCHOR)}")
    patched = source.replace(_ANCHOR, _ANCHOR + _MARKER, 1)
    if patched.count(_MARKER) != 1:
        raise AssertionError("instrumentation marker count is not one")
    return patched, _MARKER
