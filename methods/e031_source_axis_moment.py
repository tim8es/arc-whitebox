from __future__ import annotations

import math

import numpy as np

CURRENT_U = 260.1
OLD_TIER_U = 106.8
BUDGET_U = 1024.0
TARGET_UTIL = 0.14


def source_basis(k: int) -> np.ndarray:
    """Frozen degree-2 deterministic orthonormal basis on the source axis."""
    if k < 1:
        raise ValueError("k must be positive")
    q = min(3, k)
    if k == 1:
        x = np.zeros(1, dtype=np.float64)
    else:
        x = np.linspace(-1.0, 1.0, k, dtype=np.float64)
    design = np.stack((np.ones(k, dtype=np.float64), x, x * x), axis=1)[:, :q]
    basis, _ = np.linalg.qr(design, mode="reduced")
    # QR signs are mathematically arbitrary. Freeze them by requiring the largest-magnitude
    # entry of each column to be positive, making serialization/diagnostics reproducible.
    for j in range(q):
        pivot = int(np.argmax(np.abs(basis[:, j])))
        if basis[pivot, j] < 0.0:
            basis[:, j] *= -1.0
    return basis


def projection_loss_from_gram(gram: np.ndarray, basis: np.ndarray) -> float:
    """Relative Frobenius residual after source-axis projection, using only a Gram matrix."""
    gram = np.asarray(gram, dtype=np.float64)
    basis = np.asarray(basis, dtype=np.float64)
    if gram.ndim != 2 or gram.shape[0] != gram.shape[1]:
        raise ValueError("gram must be square")
    if basis.ndim != 2 or basis.shape[0] != gram.shape[0]:
        raise ValueError("basis/gram source dimensions differ")
    total = float(np.trace(gram))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("gram energy must be positive and finite")
    kept = float(np.trace(basis.T @ gram @ basis))
    lost = max(0.0, total - kept)
    return math.sqrt(lost / total)


def compute_floor(proven_exact_saving_u: float) -> dict[str, float]:
    """Frozen optimistic cost arithmetic from the preregistered V29/V25 anatomy."""
    saving = float(proven_exact_saving_u)
    if not math.isfinite(saving) or saving < 0.0:
        raise ValueError("proven_exact_saving_u must be finite and non-negative")
    zero_old = CURRENT_U - OLD_TIER_U
    target_u = TARGET_UTIL * BUDGET_U
    required = zero_old - target_u
    projected_u = zero_old - saving
    return {
        "zero_old_floor_u": zero_old,
        "zero_old_floor_util": zero_old / BUDGET_U,
        "target_u": target_u,
        "required_additional_saving_u": required,
        "proven_exact_saving_u": saving,
        "projected_u": projected_u,
        "projected_util": projected_u / BUDGET_U,
    }
