from __future__ import annotations

import inspect
import math

import numpy as np

from methods.e110_deep_harmonic import (
    HALF_PI,
    block_partition,
    deep_output_directions,
    direct_block_value,
    enumerate_relu_sectors,
    exact_block_harmonic_stats,
    validate_block_partition,
    validate_sector_partition,
)


def _weights(seed: int, depth: int = 3) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return [rng.standard_normal((2, 2)) for _ in range(depth)]


def test_sector_partition_matches_direct_network() -> None:
    weights = _weights(110001, depth=4)
    sectors = enumerate_relu_sectors(weights)
    assert sectors
    assert abs(sectors[0].lo) <= 1e-15
    assert abs(sectors[-1].hi - 2.0 * math.pi) <= 1e-15
    assert validate_sector_partition(weights, sectors) <= 1e-11


def test_block_partition_matches_four_direction_haar_block() -> None:
    weights = _weights(110002, depth=4)
    sectors = enumerate_relu_sectors(weights)
    pieces = block_partition(sectors)
    assert pieces
    assert abs(pieces[0][0]) <= 1e-15
    assert abs(pieces[-1][1] - HALF_PI) <= 1e-15
    assert validate_block_partition(weights, pieces) <= 1e-11

    theta = 0.173
    direct = direct_block_value(weights, theta)
    assert direct.shape == (2,)
    assert np.isfinite(direct).all()


def test_width2_quartic_block_control_is_pure_fourth_harmonic() -> None:
    phi = 0.317
    u = np.asarray([math.cos(phi), math.sin(phi)])
    for theta in (0.11, 0.29, 0.61, 1.02):
        q = np.asarray([math.cos(theta), math.sin(theta)])
        qp = np.asarray([math.cos(theta + HALF_PI), math.sin(theta + HALF_PI)])
        center = 3.0 / 8.0
        direct = 0.5 * (((q @ u) ** 4 - center) + ((qp @ u) ** 4 - center))
        formula = 0.125 * math.cos(4.0 * (theta - phi))
        assert abs(direct - formula) <= 2e-15


def test_exact_stats_are_finite_and_residual_not_above_baseline() -> None:
    weights = _weights(110003, depth=3)
    sectors = enumerate_relu_sectors(weights)
    pieces = block_partition(sectors)
    directions = deep_output_directions(weights)
    stats = exact_block_harmonic_stats(pieces, directions)

    assert math.isfinite(stats["pooled_ratio"])
    assert stats["analytic_control_mean"] == 0.0
    assert stats["analytic_control_variance"] == 1.0 / 128.0
    for row in stats["outputs"]:
        assert row["residual_variance"] <= row["variance"] + 1e-12
        assert math.isfinite(row["correlation"])


def test_scope_has_no_external_target_access() -> None:
    funcs = (
        enumerate_relu_sectors,
        exact_block_harmonic_stats,
        deep_output_directions,
    )
    source = "\n".join(inspect.getsource(fn) for fn in funcs).lower()
    forbidden = ("aicrowd", "public", "scorer", "holdout", "requests", "load_dataset")
    assert all(token not in source for token in forbidden)
