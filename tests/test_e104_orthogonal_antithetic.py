from __future__ import annotations

import ast
import inspect
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from methods.e104_orthogonal_antithetic import (
    Estimator,
    PRODUCTION_SAMPLES,
    orthogonal_antithetic_billed,
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


def _legacy_unbilled_rng_but_billed_transforms(width: int, total_samples: int, seed: int):
    n = int(width)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    blocks = []
    for _ in range(total_samples // (2 * n)):
        g = fnp.asarray(rng.standard_normal((n, n)).astype(np.float64))
        q, r = fnp.linalg.qr(g)
        signs = fnp.where(fnp.diag(r) < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        chi = fnp.asarray(rng.chisquare(df=n, size=n).astype(np.float64))
        radii = fnp.sqrt(chi)
        blocks.append(fnp.multiply(radii[:, None], q).astype(fnp.float32))
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def test_billed_sampler_matches_reference_and_bills_exact_rng_delta() -> None:
    width = 8
    total = 16
    seed = 103104

    reference = orthogonal_antithetic_numpy(width, total, seed)

    with flops.BudgetContext(flop_budget=10**9, quiet=True) as old_ctx:
        old = np.asarray(
            _legacy_unbilled_rng_but_billed_transforms(width, total, seed),
            dtype=np.float32,
        )

    with flops.BudgetContext(flop_budget=10**9, quiet=True) as new_ctx:
        new = np.asarray(
            orthogonal_antithetic_billed(width, total, seed),
            dtype=np.float32,
        )

    assert np.array_equal(new, reference)
    assert np.array_equal(old, reference)

    blocks = total // (2 * width)
    expected_rng_delta = blocks * 32 * (width * width + width)
    assert int(new_ctx.flops_used) - int(old_ctx.flops_used) == expected_rng_delta


def test_billed_sampler_has_no_plain_numpy_rng_draw() -> None:
    source = inspect.getsource(orthogonal_antithetic_billed)
    tree = ast.parse(source)
    plain_numpy_random = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and node.attr == "random"
        and isinstance(node.value, ast.Name)
        and node.value.id == "np"
    ]
    assert plain_numpy_random == []
    assert "fnp.random.default_rng" in source


def test_reference_sampler_antithetic_deterministic_and_orthogonal() -> None:
    width = 8
    x1 = orthogonal_antithetic_numpy(width, PRODUCTION_SAMPLES, 103104)
    x2 = orthogonal_antithetic_numpy(width, PRODUCTION_SAMPLES, 103104)
    assert np.array_equal(x1, x2)
    half = PRODUCTION_SAMPLES // 2
    assert float(np.max(np.abs(x1[:half] + x1[half:]))) == 0.0

    block = x1[:width].astype(np.float64)
    directions = block / np.linalg.norm(block, axis=1)[:, None]
    assert np.max(np.abs(directions @ directions.T - np.eye(width))) <= 5e-6


def test_estimator_small_shape_matches_row_vector_reference() -> None:
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
