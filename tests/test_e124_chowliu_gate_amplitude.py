from __future__ import annotations

import math

import numpy as np

from methods.e124_chowliu_gate_amplitude import (
    AngularSector,
    exact_gaussian_mean,
    he_weights,
    maximum_mi_tree,
    enumerate_sectors,
    penultimate_stats,
    production_flop_proof,
    stats_integrity,
)


def test_exact_relu_coordinate_mean() -> None:
    w = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64)
    sectors = enumerate_sectors([w])
    mean = exact_gaussian_mean(sectors)
    expected = 1.0 / math.sqrt(2.0 * math.pi)
    assert np.max(np.abs(mean - expected)) <= 2e-15


def test_maximum_mi_tree_is_deterministic_and_spanning() -> None:
    mi = np.asarray(
        [
            [0.0, 0.9, 0.2, 0.1],
            [0.9, 0.0, 0.8, 0.3],
            [0.2, 0.8, 0.0, 0.7],
            [0.1, 0.3, 0.7, 0.0],
        ],
        dtype=np.float64,
    )
    assert maximum_mi_tree(mi) == ((0, 1), (1, 2), (2, 3))


def test_penultimate_pair_statistics_reconstruct_marginals() -> None:
    weights = he_weights(124124, width=4, depth=3)
    sectors = enumerate_sectors(weights)
    stats = penultimate_stats(sectors)
    diag = stats_integrity(stats)
    assert diag["finite"]
    assert diag["pair_nonnegative"]
    assert diag["pair_sum_max_abs_error"] <= 1e-12
    assert diag["pair_marginal_max_abs_error"] <= 1e-12
    assert diag["marginal_mean_reconstruction_max_abs_error"] <= 1e-12
    assert diag["pair_mean_reconstruction_max_abs_error"] <= 1e-12
    assert diag["tree_edge_count"] == 3
    assert diag["tree_connected"]
    assert diag["tree_acyclic"]


def test_production_flop_proof_matches_frozen_protocol() -> None:
    proof = production_flop_proof()
    assert proof["total_upper_flops"] == 143_078_584_832
    assert proof["matches_frozen_protocol_upper"]
    assert proof["utilization_upper"] == 143_078_584_832 / (2**41)
    assert proof["utilization_upper"] <= 0.13
