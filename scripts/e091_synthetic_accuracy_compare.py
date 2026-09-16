from __future__ import annotations

import json
from pathlib import Path

import numpy as np

BUDGET = 2**41
LAM = 1.0

W1 = np.array(
    [[1.0, -0.5], [-0.25, 0.75], [0.6, 0.4]], dtype=np.float64
)
W2 = np.array(
    [[0.8, -0.3, 0.5], [-0.4, 0.7, 0.2]], dtype=np.float64
)
U = np.array(
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


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def base(u: np.ndarray) -> np.ndarray:
    return relu(u @ W1.T) @ W2.T


def features(u: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [np.ones(len(u)), u[:, 0], u[:, 1], u[:, 0] ** 2 + u[:, 1] ** 2]
    )


def residual_truth(u: np.ndarray) -> np.ndarray:
    u0, u1 = u[:, 0], u[:, 1]
    z1 = 0.15 + 0.20 * u0 - 0.10 * u1 + 0.05 * u0 * u1
    z2 = -0.10 + 0.10 * u0 + 0.15 * u1 - 0.04 * u0**2
    return np.column_stack([z1, z2])


def direct_loo(X: np.ndarray, Z: np.ndarray, lam: float) -> np.ndarray:
    n, p = X.shape
    q = Z.shape[1]
    out = np.empty((n, q), dtype=np.float64)
    eye = np.eye(p, dtype=np.float64)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        Xm = X[mask]
        Zm = Z[mask]
        B = np.linalg.solve(Xm.T @ Xm + lam * eye, Xm.T @ Zm)
        out[i] = X[i] @ B
    return out


def press_loo(X: np.ndarray, Z: np.ndarray, lam: float) -> tuple[np.ndarray, float]:
    p = X.shape[1]
    A = X.T @ X + lam * np.eye(p, dtype=np.float64)
    Ainv = np.linalg.inv(A)
    B = Ainv @ X.T @ Z
    zhat = X @ B
    h = np.einsum("ij,jk,ik->i", X, Ainv, X)
    denom = 1.0 - h
    if np.min(denom) < 1e-6:
        raise RuntimeError(f"leverage gate failed: min(1-h)={np.min(denom)}")
    loo = (zhat - h[:, None] * Z) / denom[:, None]
    return loo, float(np.min(denom))


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))


def main() -> None:
    X = features(U)
    Z = residual_truth(U)
    B0 = base(U)
    Y = B0 + Z

    loo_direct = direct_loo(X, Z, LAM)
    loo_press, min_one_minus_h = press_loo(X, Z, LAM)
    parity_max_abs = float(np.max(np.abs(loo_direct - loo_press)))

    baseline_pred = B0
    corrected_pred = B0 + loo_press
    baseline_mse = mse(baseline_pred, Y)
    corrected_mse = mse(corrected_pred, Y)
    ratio = corrected_mse / baseline_mse
    improvement = 1.0 - ratio

    n, p = X.shape
    q = Z.shape[1]
    per_row_dense_dot_flops = (2 * p - 1) * q
    per_row_output_add_flops = q
    total_correction_flops = n * (per_row_dense_dot_flops + per_row_output_add_flops)
    correction_util = total_correction_flops / BUDGET

    repeat = base(U) + press_loo(X, Z, LAM)[0]
    repeat_max_abs = float(np.max(np.abs(corrected_pred - repeat)))

    result = {
        "schema": "arc.whitebox.e091.synthetic_accuracy_compare.v1",
        "experiment": "E091",
        "scope": "synthetic_only_no_public_no_scorer",
        "N": n,
        "p": p,
        "q": q,
        "lambda": LAM,
        "baseline_raw_mse_synthetic": baseline_mse,
        "corrected_raw_mse_synthetic": corrected_mse,
        "mse_ratio": ratio,
        "relative_mse_improvement": improvement,
        "press_vs_direct_max_abs": parity_max_abs,
        "min_one_minus_h": min_one_minus_h,
        "per_row_dense_dot_flops": per_row_dense_dot_flops,
        "per_row_output_add_flops": per_row_output_add_flops,
        "total_correction_flops_for_7_rows": total_correction_flops,
        "correction_utilization_vs_phase2_budget": correction_util,
        "deterministic_repeat_max_abs": repeat_max_abs,
        "finite": bool(np.isfinite(corrected_pred).all()),
        "phase2_raw_mse_evaluated": False,
        "phase2_raw_mse_unavailable_reason": (
            "E091 is authorized here for synthetic/local checks only; no admissible production "
            "base below the complete 0.135 utilization ceiling is frozen, and public/scorer/holdout "
            "data access is prohibited for this experiment."
        ),
    }

    gates = {
        "press_parity_le_1e-12": parity_max_abs <= 1e-12,
        "leverage_margin_ge_1e-6": min_one_minus_h >= 1e-6,
        "correction_improves_synthetic_mse": corrected_mse < baseline_mse,
        "deterministic_repeat_eq_0": repeat_max_abs == 0.0,
        "finite": result["finite"],
    }
    result["gates"] = gates
    result["decision"] = "LOCAL_GO" if all(gates.values()) else "LOCAL_NO_GO"

    print("E091_SYNTHETIC_ACCURACY " + json.dumps(result, sort_keys=True), flush=True)
    Path("e091_synthetic_accuracy_compare.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
