from __future__ import annotations

import inspect
import math

import flopscope as flops
import numpy as np

from methods.e108_firstlayer_transport_cv import (
    build_meanfield_transport_billed,
    build_two_haar_inputs_billed,
    crossfit_scalar_correct_billed,
    first_layer_exact_mean_billed,
    mean_chi_radius,
)


def test_first_layer_exact_mean_formula() -> None:
    w = np.asarray([[2.0, 0.0], [0.0, -3.0]], dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        got = np.asarray(first_layer_exact_mean_billed(w), dtype=np.float64)
    expected = np.asarray([2.0, 3.0], dtype=np.float64) / math.sqrt(2.0 * math.pi)
    assert np.allclose(got, expected, rtol=1e-12, atol=1e-12)


def test_meanfield_transport_orientation_and_half_gates() -> None:
    w1 = np.eye(2, dtype=np.float32)
    w2 = np.asarray([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    w3 = np.asarray([[2.0, -1.0], [0.5, 3.0]], dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        got = np.asarray(build_meanfield_transport_billed([w1, w2, w3]), dtype=np.float64)
    expected = (0.5 * w2.T) @ (0.5 * w3.T)
    assert np.allclose(got, expected, rtol=1e-6, atol=1e-6)


def test_crossfit_scalar_control_reduces_constructed_signal() -> None:
    rng = np.random.Generator(np.random.PCG64(108001))
    z1 = rng.normal(size=(256, 8)).astype(np.float32)
    z2 = rng.normal(size=(256, 8)).astype(np.float32)
    coef = np.linspace(0.5, 2.0, 8, dtype=np.float32)
    base = np.linspace(-0.25, 0.75, 8, dtype=np.float32)
    y1 = base + z1 * coef
    y2 = base + z2 * coef

    with flops.BudgetContext(flop_budget=10**9, quiet=True):
        candidate, baseline, beta1, beta2 = crossfit_scalar_correct_billed(
            y1, y2, z1, z2
        )

    candidate = np.asarray(candidate, dtype=np.float64)
    baseline = np.asarray(baseline, dtype=np.float64)
    assert np.max(np.abs(candidate - base)) < np.max(np.abs(baseline - base))
    assert np.all(np.isfinite(np.asarray(beta1)))
    assert np.all(np.isfinite(np.asarray(beta2)))


def test_two_haar_sampler_exact_antithetic_orthogonal_deterministic() -> None:
    width = 8
    radius = mean_chi_radius(width)
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x1 = np.asarray(build_two_haar_inputs_billed(width, 108105), dtype=np.float32)
    with flops.BudgetContext(flop_budget=10**10, quiet=True):
        x2 = np.asarray(build_two_haar_inputs_billed(width, 108105), dtype=np.float32)
    assert np.array_equal(x1, x2)
    assert x1.shape == (4 * width, width)
    half = x1.shape[0] // 2
    assert float(np.max(np.abs(x1[:half] + x1[half:]))) == 0.0
    for start in (0, width):
        q = x1[start : start + width].astype(np.float64) / radius
        assert np.max(np.abs(q @ q.T - np.eye(width))) <= 5e-6


def test_scope_contains_no_external_target_access() -> None:
    funcs = (
        build_two_haar_inputs_billed,
        first_layer_exact_mean_billed,
        build_meanfield_transport_billed,
        crossfit_scalar_correct_billed,
    )
    source = "\n".join(inspect.getsource(fn) for fn in funcs).lower()
    forbidden = ("aicrowd", "public", "scorer", "holdout", "requests", "load_dataset")
    assert all(token not in source for token in forbidden)
