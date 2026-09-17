from __future__ import annotations

from types import SimpleNamespace

import flopscope as flops
import numpy as np
from whestbench import SetupContext

from methods.e103_orthogonal_antithetic import (
    Estimator,
    PRODUCTION_SAMPLES,
    orthogonal_antithetic_numpy,
    propagate_numpy,
)


def _weights(seed: int, width: int, depth: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(np.sqrt(2.0 / width))
    return [
        (rng.standard_normal((width, width), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(depth)
    ]


def test_reference_sampler_is_exactly_antithetic_deterministic_and_orthogonal() -> None:
    width = 8
    x1 = orthogonal_antithetic_numpy(width, PRODUCTION_SAMPLES, 103104)
    x2 = orthogonal_antithetic_numpy(width, PRODUCTION_SAMPLES, 103104)
    assert np.array_equal(x1, x2)
    half = PRODUCTION_SAMPLES // 2
    assert float(np.max(np.abs(x1[:half] + x1[half:]))) == 0.0
    block = x1[:width].astype(np.float64)
    directions = block / np.linalg.norm(block, axis=1)[:, None]
    assert np.max(np.abs(directions @ directions.T - np.eye(width))) <= 5e-6


def test_production_estimator_small_shape_matches_row_vector_reference() -> None:
    width = 8
    depth = 3
    seed = 103104
    weights = _weights(103103, width, depth)
    mlp = SimpleNamespace(width=width, depth=depth, weights=weights, seed=103103)

    estimator = Estimator()
    estimator.setup(
        SetupContext(
            width=width,
            depth=depth,
            flop_budget=10**12,
            api_version="1",
            seed=seed,
        )
    )
    with flops.BudgetContext(flop_budget=10**12, quiet=True):
        actual = np.asarray(estimator.predict(mlp, 10**12), dtype=np.float64)
    estimator.teardown()

    inputs = orthogonal_antithetic_numpy(width, PRODUCTION_SAMPLES, seed)
    expected = propagate_numpy(weights, inputs)

    assert actual.shape == (depth, width)
    assert np.all(np.isfinite(actual))
    assert np.allclose(actual, expected, atol=2e-6, rtol=2e-6)
