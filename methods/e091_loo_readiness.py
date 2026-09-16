"""Synthetic-only E091 leave-one-out readiness algebra.

No benchmark/public/scorer data access exists in this module.
"""

from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

PHASE2_BUDGET = 2**41

_W1 = np.array(
    [[1.0, -0.5], [-0.25, 0.75], [0.6, 0.4]], dtype=np.float64
)
_W2 = np.array(
    [[0.8, -0.3, 0.5], [-0.4, 0.7, 0.2]], dtype=np.float64
)
_INPUTS = np.array(
    [
        [-1.0, -0.5],
        [-0.75, 0.25],
        [-0.25, 1.0],
        [0.25, -1.0],
        [0.5, 0.75],
        [1.0, -0.25],
        [1.25, 0.5],
    ],
    dtype=np.float64,
)


def tiny_relu_base(inputs: np.ndarray) -> np.ndarray:
    hidden = np.maximum(inputs @ _W1.T, 0.0)
    return hidden @ _W2.T


def target_free_features(inputs: np.ndarray) -> np.ndarray:
    """Frozen feature builder. It accepts inputs only, never targets/residuals."""
    u0 = inputs[:, 0]
    u1 = inputs[:, 1]
    return np.column_stack(
        [np.ones(len(inputs), dtype=np.float64), u0, u1, u0 * u0 + u1 * u1]
    )


def synthetic_residual_truth(inputs: np.ndarray) -> np.ndarray:
    """Deterministic synthetic/reference residual teacher for the bounded falsifier."""
    u0 = inputs[:, 0]
    u1 = inputs[:, 1]
    z1 = 0.15 + 0.20 * u0 - 0.10 * u1 + 0.05 * u0 * u1
    z2 = -0.10 + 0.10 * u0 + 0.15 * u1 - 0.04 * u0 * u0
    return np.column_stack([z1, z2])


def build_tiny_problem() -> tuple[np.ndarray, np.ndarray, dict]:
    inputs = _INPUTS.copy()
    base = tiny_relu_base(inputs)
    X = target_free_features(inputs)
    Z = synthetic_residual_truth(inputs)
    return X, Z, {"inputs": inputs, "base": base, "target": base + Z}


def _ridge_system(X: np.ndarray, Z: np.ndarray, lam: float):
    p = X.shape[1]
    A = X.T @ X + float(lam) * np.eye(p, dtype=np.float64)
    rhs = X.T @ Z
    B = np.linalg.solve(A, rhs)
    return A, B


def full_ridge_fit(
    X: np.ndarray, Z: np.ndarray, lam: float
) -> tuple[np.ndarray, np.ndarray]:
    _, B = _ridge_system(X, Z, lam)
    return X @ B, B


def loo_press_predictions(
    X: np.ndarray, Z: np.ndarray, lam: float
) -> tuple[np.ndarray, np.ndarray]:
    """Exact row-wise ridge LOO predictions from the PRESS/Sherman-Morrison identity."""
    A, B = _ridge_system(X, Z, lam)
    # Solve A V = X^T; V[:, i] = A^{-1} x_i.
    V = np.linalg.solve(A, X.T)
    h = np.einsum("ij,ji->i", X, V)
    fitted = X @ B
    err = Z - fitted
    denom = 1.0 - h
    loo = fitted - (h / denom)[:, None] * err
    return loo, h


def direct_loo_predictions(X: np.ndarray, Z: np.ndarray, lam: float) -> np.ndarray:
    """Reference implementation: N independent direct ridge refits."""
    n = X.shape[0]
    out = np.empty_like(Z, dtype=np.float64)
    for i in range(n):
        keep = np.arange(n) != i
        A, B = _ridge_system(X[keep], Z[keep], lam)
        # A is intentionally materialized by _ridge_system for direct parity semantics.
        _ = A
        out[i] = X[i] @ B
    return out


def signed_influence_metrics(X: np.ndarray, Z: np.ndarray, lam: float) -> dict:
    """Explicit signed weights of each omitted prediction on retained residual targets."""
    n = X.shape[0]
    max_row_l1 = 0.0
    max_negative_mass = 0.0
    max_abs_weight = 0.0
    max_abs_loo_prediction = 0.0
    finite = True
    all_weights: list[list[float]] = []

    for i in range(n):
        keep = np.arange(n) != i
        Xm = X[keep]
        Zm = Z[keep]
        A = Xm.T @ Xm + float(lam) * np.eye(X.shape[1], dtype=np.float64)
        v = np.linalg.solve(A, X[i])
        w = Xm @ v
        pred = w @ Zm
        all_weights.append(w.tolist())
        max_row_l1 = max(max_row_l1, float(np.sum(np.abs(w))))
        max_negative_mass = max(
            max_negative_mass, float(np.sum(np.maximum(-w, 0.0)))
        )
        max_abs_weight = max(max_abs_weight, float(np.max(np.abs(w))))
        max_abs_loo_prediction = max(
            max_abs_loo_prediction, float(np.max(np.abs(pred)))
        )
        finite = finite and bool(np.all(np.isfinite(w)) and np.all(np.isfinite(pred)))

    return {
        "max_row_l1": max_row_l1,
        "max_negative_mass": max_negative_mass,
        "max_abs_weight": max_abs_weight,
        "max_abs_loo_prediction": max_abs_loo_prediction,
        "max_abs_target": float(np.max(np.abs(Z))),
        "finite": bool(finite),
        "weights": all_weights,
    }


def dense_dot_cost(p: int, q: int, dtype_bytes: int = 4) -> dict:
    exact = (2 * int(p) - 1) * int(q)
    ceiling = 2 * int(p) * int(q)
    return {
        "p": int(p),
        "q": int(q),
        "exact_flops": exact,
        "ceiling_flops": ceiling,
        "ceiling_fraction": ceiling / PHASE2_BUDGET,
        "coefficient_bytes": int(p) * int(q) * int(dtype_bytes),
    }


def _fnp_tiny_base(inputs):
    w1 = fnp.asarray(_W1, dtype=fnp.float64)
    w2 = fnp.asarray(_W2, dtype=fnp.float64)
    hidden = fnp.maximum(inputs @ w1.T, 0.0)
    return hidden @ w2.T


def _fnp_target_free_features(inputs):
    u0 = inputs[:, 0]
    u1 = inputs[:, 1]
    radius2 = u0 * u0 + u1 * u1
    ones = fnp.ones(len(inputs), dtype=fnp.float64)
    return fnp.stack([ones, u0, u1, radius2], axis=1)


def _budget_metrics(budget) -> dict:
    return {
        "flops": int(budget.flops_used),
        "residual_wall_s": float(budget.residual_wall_time_s),
        "wall_s": float(budget.wall_time_s),
    }


def measure_tiny_deploy(
    inputs: np.ndarray, B: np.ndarray
) -> tuple[np.ndarray, dict[str, object]]:
    """Measure the complete frozen tiny deploy path with flopscope.

    Ridge calibration/LOO work is deliberately outside this function because the E091
    protocol defines it as offline-only. The measured deploy path is exactly base prediction,
    target-free feature extraction, one dense correction dot, and the final output add.
    """
    inputs_f = fnp.asarray(np.asarray(inputs, dtype=np.float64), dtype=fnp.float64)
    coef_f = fnp.asarray(np.asarray(B, dtype=np.float64), dtype=fnp.float64)

    with flops.BudgetContext(
        flop_budget=PHASE2_BUDGET, wall_time_limit_s=1.0
    ) as base_budget:
        base = _fnp_tiny_base(inputs_f)
    base_metrics = _budget_metrics(base_budget)

    with flops.BudgetContext(
        flop_budget=PHASE2_BUDGET, wall_time_limit_s=1.0
    ) as feature_budget:
        features = _fnp_target_free_features(inputs_f)
    feature_metrics = _budget_metrics(feature_budget)

    with flops.BudgetContext(
        flop_budget=PHASE2_BUDGET, wall_time_limit_s=1.0
    ) as correction_budget:
        correction = features @ coef_f
    correction_metrics = _budget_metrics(correction_budget)

    with flops.BudgetContext(
        flop_budget=PHASE2_BUDGET, wall_time_limit_s=1.0
    ) as add_budget:
        output = base + correction
    add_metrics = _budget_metrics(add_budget)

    with flops.BudgetContext(
        flop_budget=PHASE2_BUDGET, wall_time_limit_s=1.0
    ) as all_in_budget:
        all_base = _fnp_tiny_base(inputs_f)
        all_features = _fnp_target_free_features(inputs_f)
        all_correction = all_features @ coef_f
        all_output = all_base + all_correction
    all_in_metrics = _budget_metrics(all_in_budget)

    components = {
        "base": base_metrics["flops"],
        "features": feature_metrics["flops"],
        "correction_dot": correction_metrics["flops"],
        "output_add": add_metrics["flops"],
    }
    metrics: dict[str, object] = {
        "component_flops": components,
        "component_residual_wall_s": {
            "base": base_metrics["residual_wall_s"],
            "features": feature_metrics["residual_wall_s"],
            "correction_dot": correction_metrics["residual_wall_s"],
            "output_add": add_metrics["residual_wall_s"],
        },
        "component_wall_s": {
            "base": base_metrics["wall_s"],
            "features": feature_metrics["wall_s"],
            "correction_dot": correction_metrics["wall_s"],
            "output_add": add_metrics["wall_s"],
        },
        "all_in_flops": all_in_metrics["flops"],
        "actual_all_in_utilization": all_in_metrics["flops"] / PHASE2_BUDGET,
        "all_in_residual_wall_s": all_in_metrics["residual_wall_s"],
        "all_in_wall_s": all_in_metrics["wall_s"],
    }
    return np.asarray(all_output, dtype=np.float64), metrics
