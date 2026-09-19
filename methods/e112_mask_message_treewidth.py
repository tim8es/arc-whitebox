"""E112 exact finite-state mask-message structural falsifier."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class TreewidthResult:
    treewidth: int
    order: tuple[int, ...]


def graph_from_factor_scopes(num_vars: int, scopes: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Return an undirected primal graph as bit-mask adjacency rows."""
    if num_vars < 0:
        raise ValueError("num_vars must be nonnegative")
    adj = [0] * num_vars
    for raw_scope in scopes:
        scope = sorted(set(int(v) for v in raw_scope))
        if any(v < 0 or v >= num_vars for v in scope):
            raise ValueError("scope variable out of range")
        for i, u in enumerate(scope):
            for v in scope[i + 1 :]:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return tuple(adj)


def scopes_from_weight_support(weight: np.ndarray) -> list[tuple[int, ...]]:
    """One exact mask factor scope per next-layer unit."""
    w = np.asarray(weight)
    if w.ndim != 2:
        raise ValueError("weight must be rank-2")
    scopes: list[tuple[int, ...]] = []
    for row in w:
        scopes.append(tuple(int(i) for i in np.flatnonzero(row != 0)))
    return scopes


def induced_width(adjacency: Sequence[int], order: Sequence[int]) -> int:
    """Width of one elimination order, including exact fill-in."""
    n = len(adjacency)
    if tuple(sorted(order)) != tuple(range(n)):
        raise ValueError("order must be a permutation of all vertices")
    adj = list(int(x) for x in adjacency)
    alive = (1 << n) - 1
    max_width = 0

    for v in order:
        neigh_mask = adj[v] & alive & ~(1 << v)
        width = neigh_mask.bit_count()
        max_width = max(max_width, width)

        neigh = [u for u in range(n) if (neigh_mask >> u) & 1]
        for i, u in enumerate(neigh):
            for w in neigh[i + 1 :]:
                adj[u] |= 1 << w
                adj[w] |= 1 << u

        alive &= ~(1 << v)

    return max_width


def exact_treewidth(adjacency: Sequence[int]) -> TreewidthResult:
    """Exact treewidth by exhaustive elimination order; intended for n<=8."""
    n = len(adjacency)
    if n > 8:
        raise ValueError("E112 exact falsifier only supports n<=8")
    best_width = math.inf
    best_order: tuple[int, ...] = tuple(range(n))
    for order in itertools.permutations(range(n)):
        width = induced_width(adjacency, order)
        if width < best_width:
            best_width = width
            best_order = tuple(order)
            if best_width == 0:
                break
    return TreewidthResult(int(best_width), best_order)


def is_complete_graph(adjacency: Sequence[int]) -> bool:
    n = len(adjacency)
    full = (1 << n) - 1
    return all(int(adjacency[v]) == (full & ~(1 << v)) for v in range(n))


def support_density(weight: np.ndarray) -> float:
    w = np.asarray(weight)
    return float(np.count_nonzero(w) / w.size)


def numeric_rank(weight: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(np.asarray(weight, dtype=np.float64)))


def first_layer_mask_count_if_onto(weight: np.ndarray) -> int:
    """Exact feasible orthant count for a square full-rank linear map."""
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise ValueError("weight must be square")
    n = w.shape[0]
    if numeric_rank(w) != n:
        raise ValueError("onto certificate requires full rank")
    return 1 << n


def make_dense_he_weights(width: int, depth: int, seed: int) -> list[np.ndarray]:
    if width < 1 or depth < 1:
        raise ValueError("width/depth must be positive")
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / width)
    return [
        rng.standard_normal((width, width)).astype(np.float64) * scale
        for _ in range(depth)
    ]


def max_budget_bag_bits(util_cap: float, budget_log2: int = 41) -> int:
    if not (0.0 < util_cap <= 1.0):
        raise ValueError("util_cap must lie in (0,1]")
    return math.floor(budget_log2 + math.log2(util_cap))


def explicit_table_log2_util_lower_bound(
    bag_bits: int, budget_log2: int = 41
) -> float:
    """log2 utilization under the favorable lower bound of one FLOP/state."""
    if bag_bits < 0:
        raise ValueError("bag_bits must be nonnegative")
    return float(bag_bits - budget_log2)
