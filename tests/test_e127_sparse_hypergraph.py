from __future__ import annotations

import math

import numpy as np

from methods.e127_sparse_hypergraph import (
    OPTIMISTIC_PAIR_COUNT_CAP,
    SMALL_CLUSTER_UNIT_CAP,
    cluster_bounds,
    envelope_diagnostics,
    enumerate_sectors,
    exact_gaussian_mean,
    exact_subset_observables,
    he_weights,
    is_downward_closed,
    mobius_clusters,
    production_flop_proof,
    propagate_one_layer,
    sparse_family,
)


def test_exact_relu_coordinate_mean() -> None:
    w = np.eye(2, dtype=np.float64)
    sectors = enumerate_sectors([w])
    mean = exact_gaussian_mean(sectors)
    expected = 1.0 / math.sqrt(2.0 * math.pi)
    assert np.max(np.abs(mean - expected)) <= 3e-15


def test_mobius_transform_reconstructs_full_value() -> None:
    values = np.asarray([[0.0], [1.0], [2.0], [4.0]], dtype=np.float64)
    delta = mobius_clusters(values)
    assert np.allclose(delta[:, 0], [0.0, 1.0, 2.0, 1.0])
    assert abs(float(np.sum(delta[:, 0])) - 4.0) <= 1e-15


def test_tiny_exact_joint_identity_and_envelope() -> None:
    weights = he_weights(127999, width=3, depth=3)
    pen = enumerate_sectors(weights[:-1])
    subset = exact_subset_observables(pen, weights[-1])
    delta = mobius_clusters(subset)
    direct = exact_gaussian_mean(propagate_one_layer(pen, weights[-1]))
    source_mean = exact_gaussian_mean(pen)
    bounds = cluster_bounds(source_mean, weights[-1])

    assert np.max(np.abs(subset[-1] - direct)) <= 1e-12
    assert np.max(np.abs(np.sum(delta, axis=0) - direct)) <= 1e-12
    assert envelope_diagnostics(delta, bounds)["pass_le_1e_12"]


def test_sparse_budget_and_production_accounting() -> None:
    bounds = np.zeros((1 << 4, 4), dtype=np.float64)
    for mask in range(1, 1 << 4):
        bounds[mask, :] = float(mask.bit_count())
    family = sparse_family(bounds, unit_cap=18)
    assert family["cluster_units"] <= 18
    assert is_downward_closed(family["selected_masks"], 4)

    proof = production_flop_proof()
    assert proof["baseline_total"] == 134_176_174_592
    assert proof["small_width_homologous_unit_cap"] == SMALL_CLUSTER_UNIT_CAP == 141
    assert proof["optimistic_pair_count_cap"] == OPTIMISTIC_PAIR_COUNT_CAP == 47
    assert not proof["full_order"]["2"]["passes_cap"]
