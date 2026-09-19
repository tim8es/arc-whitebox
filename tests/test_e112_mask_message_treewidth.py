from __future__ import annotations

import math

import numpy as np

from methods.e112_mask_message_treewidth import (
    exact_treewidth,
    explicit_table_log2_util_lower_bound,
    first_layer_mask_count_if_onto,
    graph_from_factor_scopes,
    is_complete_graph,
    make_dense_he_weights,
    max_budget_bag_bits,
    numeric_rank,
    scopes_from_weight_support,
    support_density,
)


def _graph(n: int, edges: list[tuple[int, int]]) -> tuple[int, ...]:
    scopes = [(u, v) for u, v in edges]
    return graph_from_factor_scopes(n, scopes)


def test_exact_treewidth_known_graphs() -> None:
    empty = _graph(5, [])
    assert exact_treewidth(empty).treewidth == 0

    path = _graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    assert exact_treewidth(path).treewidth == 1

    star = _graph(5, [(0, 1), (0, 2), (0, 3), (0, 4)])
    assert exact_treewidth(star).treewidth == 1

    cycle = _graph(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    assert exact_treewidth(cycle).treewidth == 2

    clique_scopes = [tuple(range(5))]
    clique = graph_from_factor_scopes(5, clique_scopes)
    assert is_complete_graph(clique)
    assert exact_treewidth(clique).treewidth == 4


def test_dense_weight_induces_full_scope_clique() -> None:
    w = np.arange(1, 17, dtype=np.float64).reshape(4, 4)
    scopes = scopes_from_weight_support(w)
    assert all(scope == (0, 1, 2, 3) for scope in scopes)
    graph = graph_from_factor_scopes(4, scopes)
    assert is_complete_graph(graph)
    assert exact_treewidth(graph).treewidth == 3


def test_full_rank_square_map_reaches_all_sign_masks() -> None:
    w = np.asarray([[1.0, 0.25], [-0.4, 1.2]])
    assert numeric_rank(w) == 2
    assert first_layer_mask_count_if_onto(w) == 4


def test_frozen_small_dense_family_is_full_rank_and_dense() -> None:
    for n in range(2, 9):
        weights = make_dense_he_weights(n, depth=4, seed=112000 + n)
        for w in weights:
            assert support_density(w) == 1.0
            assert numeric_rank(w) == n
            scopes = scopes_from_weight_support(w)
            graph = graph_from_factor_scopes(n, scopes)
            assert is_complete_graph(graph)
            assert exact_treewidth(graph).treewidth == n - 1


def test_budget_bag_gate() -> None:
    assert max_budget_bag_bits(0.13, 41) == 38
    assert explicit_table_log2_util_lower_bound(1024, 41) == 983.0
    assert math.log2(0.13) < 0.0
