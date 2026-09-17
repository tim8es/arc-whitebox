#!/usr/bin/env python3
"""E102 full third-cumulant tensor-rank lower-bound falsifier."""

from __future__ import annotations

import json
import math
from pathlib import Path

EXPERIMENT = "E102"
OFFICIAL_WIDTH = 1024
TEST_WIDTH = 8
MAX_COMPACT_RANK = 64
RESULT_PATH = Path("e102_k3_tensor_rank_result.json")


def matrix_rank(rows: list[list[float]], tol: float = 1e-12) -> int:
    a = [row[:] for row in rows]
    m = len(a)
    n = len(a[0]) if m else 0
    rank = 0
    col = 0
    while rank < m and col < n:
        pivot = max(range(rank, m), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) <= tol:
            col += 1
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pv = a[rank][col]
        a[rank] = [x / pv for x in a[rank]]
        for r in range(m):
            if r == rank:
                continue
            f = a[r][col]
            if abs(f) > tol:
                a[r] = [x - f * y for x, y in zip(a[r], a[rank])]
        rank += 1
        col += 1
    return rank


def target_unfolding(n: int, kappa: float) -> list[list[float]]:
    rows = [[0.0] * (n * n) for _ in range(n)]
    for i in range(n):
        rows[i][i * n + i] = kappa
    return rows


def latent_unfolding(d: list[float], gamma: float) -> list[list[float]]:
    n = len(d)
    right = [d[j] * d[k] for j in range(n) for k in range(n)]
    return [[gamma * d[i] * x for x in right] for i in range(n)]


def run_once() -> dict:
    mu = 1.0 / math.sqrt(2.0 * math.pi)
    kappa = math.sqrt(2.0 / math.pi) - 1.5 * mu + 2.0 * mu**3

    target = target_unfolding(TEST_WIDTH, kappa)
    target_rank = matrix_rank(target)

    test_factors = [
        ([float(i + 1) for i in range(TEST_WIDTH)], 1.0),
        ([(-1.0 if i % 2 else 1.0) * (i + 1.0) for i in range(TEST_WIDTH)], -0.75),
        ([1.0, 0.0, -2.0, 0.5, 0.0, 3.0, -1.0, 2.0], 2.5),
    ]
    factor_ranks = [
        matrix_rank(latent_unfolding(d, gamma)) for d, gamma in test_factors
    ]

    official_lower_bound = OFFICIAL_WIDTH
    log10_states = official_lower_bound * math.log10(2.0)

    integrity = {
        "finite_positive_kappa": math.isfinite(kappa) and kappa > 0.0,
        "test_target_rank_eq_8": target_rank == TEST_WIDTH,
        "all_test_factor_ranks_le_1": all(r <= 1 for r in factor_ranks),
    }
    scientific = {
        "official_latent_factor_lower_bound_le_64": official_lower_bound
        <= MAX_COMPACT_RANK
    }
    decision = (
        "ANALYTIC_GO" if all(scientific.values()) else "TERMINAL_ANALYTIC_NO_GO"
    )

    return {
        "schema": "arc.whitebox.e102.k3_tensor_rank_bound.v1",
        "experiment": EXPERIMENT,
        "relu_scalar_third_cumulant": kappa,
        "test_crosscheck": {
            "width": TEST_WIDTH,
            "target_mode1_shape": [TEST_WIDTH, TEST_WIDTH * TEST_WIDTH],
            "target_unfolding_rank": target_rank,
            "rank_one_factor_unfolding_ranks": factor_ranks,
        },
        "official_bound": {
            "width": OFFICIAL_WIDTH,
            "proof": "rank(K3_mode1)=n and rank(sum_{a=1}^m gamma_a d_a(d_a tensor d_a)^T)<=m",
            "latent_factor_lower_bound": official_lower_bound,
            "max_compact_rank": MAX_COMPACT_RANK,
            "binary_explicit_state_exponent": official_lower_bound,
            "binary_explicit_state_log10": log10_states,
        },
        "integrity_gates": integrity,
        "scientific_gates": scientific,
        "scientific_go": decision == "ANALYTIC_GO",
        "decision": decision,
        "scope": {
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "benchmark_holdout": False,
            "full_suite": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main() -> None:
    first = run_once()
    second = run_once()
    deterministic = first == second
    first["deterministic_repeat_max_abs"] = 0.0 if deterministic else math.inf
    first["integrity_gates"]["deterministic_repeat_eq_0"] = deterministic

    RESULT_PATH.write_text(
        json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("E102_K3_TENSOR_RANK_JSON=" + json.dumps(first, sort_keys=True))

    if not all(first["integrity_gates"].values()):
        raise SystemExit("E102 integrity gate failed")


if __name__ == "__main__":
    main()
