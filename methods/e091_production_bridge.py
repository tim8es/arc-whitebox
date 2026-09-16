"""Target-independent E091 production-bridge features.

This module deliberately contains no corpus loader and no target/residual argument.
The feature map was frozen in ``research/E091_PRODUCTION_BRIDGE_FREEZE.json``
before any new calibration targets are permitted to be materialized.
"""

from __future__ import annotations

import numpy as np

PHASE2_BUDGET = 2**41
PHASE2_WIDTH = 1024
FEATURE_P = 16
E043_BASE_FLOPS = 128_511_719_225

FEATURE_COLUMNS = (
    "1",
    "base_final",
    "base_final^2",
    "base_final_layer_mean",
    "base_final_layer_rms",
    "base_final_centered",
    "abs(base_final_centered)",
    "incoming_last_weight_col_l2",
    "incoming_last_weight_col_l2_centered",
    "incoming_last_weight_col_mean",
    "incoming_last_weight_col_abs_mean",
    "linear_mean_proxy=base_prev@W_last_col",
    "abs(linear_mean_proxy)",
    "base_prev_layer_mean",
    "base_prev_layer_rms",
    "relu(linear_mean_proxy)",
)


def final_layer_coordinate_features(
    base_prediction: np.ndarray, last_weight: np.ndarray
) -> np.ndarray:
    """Return one frozen 16-D target-free feature row per final-layer neuron.

    ``base_prediction`` is the already-computed base estimator output with shape
    ``(depth, width)``. ``last_weight`` is the final dense matrix with the
    repository convention ``activation @ weight`` and shape ``(width, width)``.
    """

    base = np.asarray(base_prediction, dtype=np.float64)
    weight = np.asarray(last_weight, dtype=np.float64)
    if base.ndim != 2 or base.shape[0] < 2:
        raise ValueError("base_prediction must have shape (depth>=2, width)")
    width = int(base.shape[1])
    if weight.shape != (width, width):
        raise ValueError("last_weight must have shape (width, width)")

    prev = base[-2]
    final = base[-1]

    final_mean = float(np.mean(final))
    final_rms = float(np.sqrt(np.mean(final * final)))
    final_centered = final - final_mean

    col_l2 = np.sqrt(np.sum(weight * weight, axis=0))
    col_l2_centered = col_l2 - float(np.mean(col_l2))
    col_mean = np.mean(weight, axis=0)
    col_abs_mean = np.mean(np.abs(weight), axis=0)

    linear_proxy = prev @ weight
    prev_mean = float(np.mean(prev))
    prev_rms = float(np.sqrt(np.mean(prev * prev)))

    ones = np.ones(width, dtype=np.float64)
    X = np.column_stack(
        (
            ones,
            final,
            final * final,
            ones * final_mean,
            ones * final_rms,
            final_centered,
            np.abs(final_centered),
            col_l2,
            col_l2_centered,
            col_mean,
            col_abs_mean,
            linear_proxy,
            np.abs(linear_proxy),
            ones * prev_mean,
            ones * prev_rms,
            np.maximum(linear_proxy, 0.0),
        )
    )
    if X.shape != (width, FEATURE_P):
        raise AssertionError(f"unexpected feature shape {X.shape}")
    if not np.all(np.isfinite(X)):
        raise FloatingPointError("non-finite E091 production feature")
    return X


def apply_shared_final_layer_ridge(
    base_prediction: np.ndarray, last_weight: np.ndarray, beta: np.ndarray
) -> np.ndarray:
    """Apply one shared frozen ridge vector to final-layer neuron features only."""

    base = np.asarray(base_prediction, dtype=np.float64)
    coeff = np.asarray(beta, dtype=np.float64)
    if coeff.shape != (FEATURE_P,):
        raise ValueError(f"beta must have shape ({FEATURE_P},)")
    X = final_layer_coordinate_features(base, last_weight)
    out = base.copy()
    out[-1] = out[-1] + X @ coeff
    return out


def production_cost_ceiling(width: int = PHASE2_WIDTH) -> dict[str, float | int]:
    """Conservative scalar-FLOP ceiling frozen before calibration targets.

    The feature ceiling intentionally over-bills reductions, abs/sqrt operations,
    and the final matrix-vector proxy as ``16*n^2``.  The correction ceiling is
    ``2*p*n``.  It is a readiness upper bound, not a flopscope replacement.
    """

    n = int(width)
    if n <= 0:
        raise ValueError("width must be positive")
    feature = 16 * n * n
    correction = 2 * FEATURE_P * n
    total = E043_BASE_FLOPS + feature + correction
    return {
        "base_flops": E043_BASE_FLOPS,
        "feature_flops_ceiling": feature,
        "correction_flops_ceiling": correction,
        "whole_candidate_flops_ceiling": total,
        "whole_candidate_utilization_ceiling": total / PHASE2_BUDGET,
        "utilization_limit": 0.135,
        "passes_utilization_gate": bool(total <= 0.135 * PHASE2_BUDGET),
    }
