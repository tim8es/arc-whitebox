from __future__ import annotations

import inspect

import flopscope as flops
import numpy as np

from methods.e106_crossfit_quartic import (
    build_two_haar_inputs_billed,
    crossfit_correct_billed,
    mean_chi_radius,
    quartic_features_billed,
)


def test_quartic_features_match_exact_formula() -> None:
    q = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    u = np.asarray([[1.0, 0.0]], dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        z = np.asarray(quartic_features_billed(q, u), dtype=np.float64)
    expected_center = 3.0 / (2.0 * 4.0)
    assert z.shape == (2, 1)
    assert np.allclose(z[:, 0], [1.0 - expected_center, -expected_center])


def test_crossfit_correction_reduces_constructed_quartic_signal() -> None:
    rng = np.random.Generator(np.random.PCG64(106001))
    z1 = rng.normal(size=(64, 4)).astype(np.float32)
    z2 = rng.normal(size=(64, 4)).astype(np.float32)
    coef = rng.normal(size=(4, 3)).astype(np.float32)
    base = np.asarray([0.25, -0.5, 1.25], dtype=np.float32)
    g1 = base + z1 @ coef
    g2 = base + z2 @ coef

    with flops.BudgetContext(flop_budget=10**9, quiet=True):
        candidate, baseline = crossfit_correct_billed(
            np.asarray(g1, dtype=np.float32),
            np.asarray(g2, dtype=np.float32),
            np.asarray(z1, dtype=np.float32),
            np.asarray(z2, dtype=np.float32),
        )

    candidate = np.asarray(candidate, dtype=np.float64)
    baseline = np.asarray(baseline, dtype=np.float64)
    assert np.max(np.abs(candidate - base)) < np.max(np.abs(baseline - base))
    assert np.all(np.isfinite(candidate))


def test_two_haar_sampler_exact_antithetic_and_deterministic() -> None:
    width = 8
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x1 = np.asarray(build_two_haar_inputs_billed(width, 106105), dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x2 = np.asarray(build_two_haar_inputs_billed(width, 106105), dtype=np.float32)
    assert np.array_equal(x1, x2)
    assert x1.shape == (4 * width, width)
    half = x1.shape[0] // 2
    assert float(np.max(np.abs(x1[:half] + x1[half:]))) == 0.0
    assert np.isfinite(mean_chi_radius(1024))


def test_scope_contains_no_external_target_access() -> None:
    source = (
        inspect.getsource(build_two_haar_inputs_billed)
        + inspect.getsource(quartic_features_billed)
        + inspect.getsource(crossfit_correct_billed)
    ).lower()
    forbidden = ("aicrowd", "public", "scorer", "holdout", "requests", "load_dataset")
    assert all(token not in source for token in forbidden)
