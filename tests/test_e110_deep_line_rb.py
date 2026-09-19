from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "e110_deep_line_rb.py"
SPEC = importlib.util.spec_from_file_location("e110_deep_line_rb", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_one_layer_relu_line_integral_matches_closed_form():
    weights = [np.eye(2, dtype=np.float64)]
    z = np.zeros(2, dtype=np.float64)
    v = np.array([1.0, 0.0], dtype=np.float64)
    result = MOD.conditional_mean_piecewise(weights, z, v, interval_cap=100)
    expected = np.array([1.0 / math.sqrt(2.0 * math.pi), 0.0])
    assert result["partition_ok"]
    assert np.max(np.abs(result["mean"] - expected)) <= 1e-14


def test_random_small_network_piecewise_integral_matches_dense_integral():
    weights = MOD.make_weights(4, 3, 9110)
    v, norm = MOD.deep_sensitivity_direction(weights)
    assert math.isfinite(norm) and norm > 0.0

    rng = np.random.Generator(np.random.PCG64(9111))
    x = rng.standard_normal(4)
    t = float(x @ v)
    z = x - t * v

    exact = MOD.conditional_mean_piecewise(weights, z, v, interval_cap=5000)
    dense = MOD.dense_normal_integral(
        weights, z, v, grid_points=16385, limit=8.0
    )
    err = float(np.max(np.abs(exact["mean"] - dense)))
    denom = max(float(np.max(np.abs(exact["mean"]))), 1e-12)
    assert err / denom <= 3e-4


def test_gaussian_projection_decomposition_is_orthogonal():
    weights = MOD.make_weights(5, 2, 9120)
    v, _ = MOD.deep_sensitivity_direction(weights)
    rng = np.random.Generator(np.random.PCG64(9121))
    x = rng.standard_normal((16, 5))
    t = x @ v
    z = x - t[:, None] * v[None, :]
    assert np.max(np.abs(z @ v)) <= 2e-15
    assert np.max(np.abs((z + t[:, None] * v[None, :]) - x)) <= 2e-15


def test_piecewise_partition_is_complete_and_ordered():
    weights = MOD.make_weights(4, 4, 9130)
    v, _ = MOD.deep_sensitivity_direction(weights)
    z = np.array([0.2, -0.4, 0.1, 0.3], dtype=np.float64)
    z = z - float(z @ v) * v
    result = MOD.conditional_mean_piecewise(weights, z, v, interval_cap=5000)
    segments = result["segments"]
    assert result["partition_ok"]
    assert segments[0].lo == -math.inf
    assert segments[-1].hi == math.inf
    assert all(a.hi == b.lo for a, b in zip(segments[:-1], segments[1:]))
