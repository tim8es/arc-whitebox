from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

COEFFICIENT_COUNT = 7
AUXILIARY_STATES = 3


def _as_sequence(array: np.ndarray) -> np.ndarray:
    seq = np.asarray(array, dtype=np.float64)
    if seq.ndim < 2:
        raise ValueError("trajectory must have a time axis and at least one value axis")
    return seq


def auxiliary_state_count() -> int:
    return AUXILIARY_STATES


def fit_shared_order3(
    inputs: Iterable[np.ndarray],
    targets: Iterable[np.ndarray],
    *,
    fit_start: int = 3,
) -> np.ndarray:
    """Fit one shared matrix-valued ARX(3) realization by global least squares.

    Each matrix entry contributes equally to the same seven scalar coefficients:
    three denominator coefficients followed by four numerator coefficients.
    """
    if fit_start < 3:
        raise ValueError("fit_start must be at least 3 for an order-3 realization")

    gram = np.zeros((COEFFICIENT_COUNT, COEFFICIENT_COUNT), dtype=np.float64)
    rhs = np.zeros(COEFFICIENT_COUNT, dtype=np.float64)
    rows = 0

    input_list: Sequence[np.ndarray] = list(inputs)
    target_list: Sequence[np.ndarray] = list(targets)
    if len(input_list) != len(target_list) or not input_list:
        raise ValueError("inputs and targets must contain the same nonzero trajectory count")

    for raw_u, raw_y in zip(input_list, target_list, strict=True):
        u = _as_sequence(raw_u)
        y = _as_sequence(raw_y)
        if u.shape != y.shape:
            raise ValueError("input and target trajectory shapes must match")
        if u.shape[0] <= fit_start:
            raise ValueError("trajectory is too short for the requested fit_start")

        for t in range(fit_start, u.shape[0]):
            features = (
                y[t - 1],
                y[t - 2],
                y[t - 3],
                u[t],
                u[t - 1],
                u[t - 2],
                u[t - 3],
            )
            flat = [np.asarray(feature, dtype=np.float64).reshape(-1) for feature in features]
            target = y[t].reshape(-1)
            for i in range(COEFFICIENT_COUNT):
                rhs[i] += float(np.dot(flat[i], target))
                for j in range(i, COEFFICIENT_COUNT):
                    value = float(np.dot(flat[i], flat[j]))
                    gram[i, j] += value
                    if i != j:
                        gram[j, i] += value
            rows += target.size

    if rows == 0:
        raise ValueError("no fit rows were accumulated")
    coefficients, *_ = np.linalg.lstsq(gram, rhs, rcond=None)
    return np.asarray(coefficients, dtype=np.float64)


def rollout_order3(inputs: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """Roll a frozen order-3 direct-form-II matrix memory without teacher forcing."""
    u = _as_sequence(inputs)
    coeff = np.asarray(coefficients, dtype=np.float64)
    if coeff.shape != (COEFFICIENT_COUNT,):
        raise ValueError("coefficients must have shape (7,)")

    c1, c2, c3, d0, d1, d2, d3 = coeff
    s1 = np.zeros_like(u[0], dtype=np.float64)
    s2 = np.zeros_like(s1)
    s3 = np.zeros_like(s1)
    outputs = np.empty_like(u, dtype=np.float64)

    for t, current in enumerate(u):
        w = current + c1 * s1 + c2 * s2 + c3 * s3
        outputs[t] = d0 * w + d1 * s1 + d2 * s2 + d3 * s3
        s3, s2, s1 = s2, s1, w
    return outputs


def poles_from_coefficients(coefficients: np.ndarray) -> np.ndarray:
    coeff = np.asarray(coefficients, dtype=np.float64)
    if coeff.shape != (COEFFICIENT_COUNT,):
        raise ValueError("coefficients must have shape (7,)")
    c1, c2, c3 = coeff[:3]
    return np.roots(np.array([1.0, -c1, -c2, -c3], dtype=np.float64))
