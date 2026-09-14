from __future__ import annotations

import numpy as np

from methods.e015_mz_prony import (
    auxiliary_state_count,
    fit_shared_order3,
    poles_from_coefficients,
    rollout_order3,
)


def _direct_form_ii(inputs: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    c1, c2, c3, d0, d1, d2, d3 = coefficients
    s1 = np.zeros_like(inputs[0], dtype=np.float64)
    s2 = np.zeros_like(s1)
    s3 = np.zeros_like(s1)
    outputs = []
    for u in inputs:
        w = u + c1 * s1 + c2 * s2 + c3 * s3
        y = d0 * w + d1 * s1 + d2 * s2 + d3 * s3
        outputs.append(y.copy())
        s3, s2, s1 = s2, s1, w
    return np.stack(outputs)


def test_global_fit_recovers_one_shared_order3_matrix_realization() -> None:
    rng = np.random.default_rng(20260914)
    expected = np.array([0.45, -0.12, 0.03, 0.80, 0.10, -0.05, 0.02], dtype=np.float64)
    inputs = [rng.normal(size=(12, 4, 4)) for _ in range(4)]
    targets = [_direct_form_ii(u, expected) for u in inputs]

    fitted = fit_shared_order3(inputs, targets, fit_start=3)

    assert fitted.shape == (7,)
    assert np.allclose(fitted, expected, rtol=1e-8, atol=1e-9)
    assert np.all(np.isfinite(poles_from_coefficients(fitted)))


def test_rollout_is_recursive_deterministic_and_uses_three_matrix_states() -> None:
    rng = np.random.default_rng(15)
    coefficients = np.array([0.35, -0.08, 0.015, 0.7, 0.15, -0.04, 0.01])
    inputs = rng.normal(size=(10, 5, 5))

    first = rollout_order3(inputs, coefficients)
    second = rollout_order3(inputs.copy(), coefficients.copy())

    assert auxiliary_state_count() == 3
    assert np.array_equal(first, second)
    assert np.allclose(first, _direct_form_ii(inputs, coefficients), rtol=0.0, atol=0.0)
