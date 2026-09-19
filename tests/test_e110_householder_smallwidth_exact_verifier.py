from __future__ import annotations

import inspect
import math

import numpy as np

from methods.e110_householder_exact_verifier import (
    block_partition,
    deep_sensitivity,
    enumerate_relu_sectors,
    exact_householder_stats,
    householder,
    validate_block_partition,
    validate_sector_partition,
)


def _weights(seed: int = 110104, depth: int = 4) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return [
        rng.standard_normal((2, 2)).astype(np.float64) * math.sqrt(2.0 / 2.0)
        for _ in range(depth)
    ]


def test_exact_sector_and_block_representations() -> None:
    weights = _weights()
    sectors = enumerate_relu_sectors(weights)
    pieces = block_partition(sectors)
    assert sectors
    assert pieces
    assert validate_sector_partition(weights, sectors) <= 1e-11
    assert validate_block_partition(weights, pieces) <= 1e-11


def test_householder_is_orthogonal_and_weight_only() -> None:
    weights = _weights()
    v = deep_sensitivity(weights)
    r = householder(v)
    assert np.isfinite(v).all()
    assert abs(float(np.linalg.norm(v)) - 1.0) <= 1e-12
    assert float(np.max(np.abs(r.T @ r - np.eye(2)))) <= 1e-12


def test_exact_reference_reports_unbiased_candidate_mean() -> None:
    stats = exact_householder_stats(_weights())
    assert stats["nondegenerate_outputs"] >= 1
    assert stats["max_candidate_mean_abs_error"] <= 1e-12
    assert stats["max_reflected_marginal_mean_abs_error"] <= 1e-12
    assert math.isfinite(stats["pooled_variance_ratio"])


def test_verifier_helpers_have_no_external_target_access() -> None:
    funcs = (
        enumerate_relu_sectors,
        exact_householder_stats,
        deep_sensitivity,
    )
    source = "\n".join(inspect.getsource(fn) for fn in funcs).lower()
    forbidden = (
        "aicrowd",
        "load_dataset",
        "final_means",
        "official_scorer",
        "requests.get",
        "huggingface",
    )
    assert all(token not in source for token in forbidden)
