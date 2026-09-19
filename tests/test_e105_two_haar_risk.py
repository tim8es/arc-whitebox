from __future__ import annotations

import inspect
import math

import flopscope as flops
import numpy as np

from methods.e105_two_haar_risk import (
    build_two_haar_inputs_billed,
    mean_chi_radius,
    two_block_statistics,
)


def test_two_block_risk_formula_and_recomposition() -> None:
    b1 = np.asarray([1.0, 2.0, -1.0, 4.0], dtype=np.float64)
    b2 = np.asarray([3.0, -2.0, 1.0, 0.0], dtype=np.float64)
    estimate, risk = two_block_statistics(b1, b2)
    assert np.array_equal(estimate, (b1 + b2) / 2.0)
    assert risk == float(np.mean((b1 - b2) ** 2) / 4.0)


def test_target_free_risk_identity_monte_carlo() -> None:
    rng = np.random.Generator(np.random.PCG64(105001))
    draws = rng.normal(size=(200000, 2))
    m = np.mean(draws, axis=1)
    rh = (draws[:, 0] - draws[:, 1]) ** 2 / 4.0
    assert abs(float(np.mean(rh)) - float(np.var(m))) < 0.005


def test_billed_two_haar_sampler_is_antithetic_orthogonal_and_deterministic() -> None:
    width = 8
    total = 4 * width
    radius = mean_chi_radius(width)
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x1 = np.asarray(build_two_haar_inputs_billed(width, 105105), dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x2 = np.asarray(build_two_haar_inputs_billed(width, 105105), dtype=np.float32)

    assert x1.shape == (total, width)
    assert np.array_equal(x1, x2)
    half = total // 2
    assert float(np.max(np.abs(x1[:half] + x1[half:]))) == 0.0

    for start in (0, width):
        q = x1[start : start + width].astype(np.float64) / radius
        assert np.max(np.abs(q @ q.T - np.eye(width))) <= 5e-6


def test_sampler_scope_has_no_external_target_access() -> None:
    source = inspect.getsource(build_two_haar_inputs_billed).lower()
    forbidden = ("aicrowd", "public", "scorer", "holdout", "datasets", "requests")
    assert all(token not in source for token in forbidden)
    assert math.isfinite(mean_chi_radius(1024))
