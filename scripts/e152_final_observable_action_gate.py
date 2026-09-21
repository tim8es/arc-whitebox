#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "e152-theory-gate.json"
PUBLIC_COMMIT = os.environ.get(
    "E152_PUBLIC_COMMIT",
    "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45",
)

def load_public_table():
    p = Path(os.environ["E152_PUBLIC_PATH"]) / "lean" / "k3_tables2.py"
    spec = importlib.util.spec_from_file_location("e152_public_k3_tables2", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned public K3 table")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def exact_small_witness() -> dict:
    n = 8
    q_r = 3
    q_l = 3

    # Integer coordinate queries: columns e0,e1,e2.
    S = np.zeros((n, q_r), dtype=np.int64)
    T = np.zeros((n, q_l), dtype=np.int64)
    for j in range(q_r):
        S[j, j] = 1
    for j in range(q_l):
        T[j, j] = 1

    E = np.zeros((n, n), dtype=np.int64)
    E[3, 4] = 1

    right = E @ S
    left = E.T @ T
    square = E.T * E.T

    return {
        "n": n,
        "q_right": q_r,
        "q_left": q_l,
        "q_total": q_r + q_l,
        "threshold_n_minus_1": n - 1,
        "hidden_matrix_nonzero_entries": [[3, 4, 1]],
        "zero_diagonal_exact": bool(np.all(np.diag(E) == 0)),
        "right_action_exact_zero": bool(np.array_equal(right, np.zeros_like(right))),
        "left_action_exact_zero": bool(np.array_equal(left, np.zeros_like(left))),
        "quadratic_closure_square_nonzero": bool(np.any(square != 0)),
        "quadratic_closure_support": np.argwhere(square != 0).tolist(),
        "dimension_zero_diag": n * (n - 1),
        "max_transcript_rank_bound": n * (q_r + q_l),
        "kernel_dimension_lower_bound": n * (n - 1) - n * (q_r + q_l),
        "adaptive_argument": (
            "Run deterministic adaptive queries on D=0; every answer is zero, "
            "freezing the query sequence. Any nonzero E in the final transcript "
            "kernel gives the identical zero transcript. The public quadratic "
            "D21T*D21T term separates D=0 and D=E."
        ),
    }

def primary_term_check(table) -> dict:
    target = ("d21T", "d21T", 6, 12, 0.25)
    terms = table.TERM_SPECS[(1, 1)]
    found = target in terms

    # WICK_PAIRS[6]=(2,1), WICK_PAIRS[12]=(4,1).
    wick6 = tuple(table.WICK_PAIRS[6])
    wick12 = tuple(table.WICK_PAIRS[12])

    # At mu=0,var=1 for ReLU:
    # w(2,1)=phi(0), w(4,1)=He_2(0)*phi(0)=-phi(0).
    # 1/4*w21*w41 = -1/(8*pi), exactly nonzero.
    multiplier = -1.0 / (8.0 * math.pi)

    return {
        "target_term": list(target),
        "found_in_pinned_public_table": bool(found),
        "wick_pair_left": list(wick6),
        "wick_pair_right": list(wick12),
        "zero_mean_unit_variance_multiplier_formula": "-1/(8*pi)",
        "zero_mean_unit_variance_multiplier_numeric": multiplier,
        "multiplier_nonzero": multiplier != 0.0,
    }

def production_lower_bound() -> dict:
    n = 1024
    q_total = n - 1
    depth = 16
    d21_layers = 14  # L01..L14; L15 final mean-only trim.
    age_old = 4

    # Dense-young source counts at D21-consuming layers:
    # L01..L04 -> 1,2,3,4; L05..L14 -> 4 each.
    source_counts = [1, 2, 3, 4] + [age_old] * 10
    assert len(source_counts) == d21_layers
    young_source_layer_instances = sum(source_counts)
    assert young_source_layer_instances == 50

    # For D_s = LA A^T + LP P^T:
    # D_s S uses A^T S, LA(...), P^T S, LP(...): four dense-thin
    # products, 2*n^2*q each => 8*n^2*q. Left actions same.
    # Total q_right+q_left = q_total.
    young_action_flops = young_source_layer_instances * 8 * n * n * q_total

    budget = 2**41
    cap_fraction = 0.135
    cap_flops = cap_fraction * budget

    public_units = {
        "young_transport": 60.71,
        "hub": 54.90,
        "shared": 27.91,
        "old_legs": 27.89,
        "covariance": 7.10,
        "closure_birth": 5.71,
    }
    public_crosscheck_units = sum(public_units.values())

    return {
        "n": n,
        "depth": depth,
        "d21_consuming_layers": d21_layers,
        "necessary_q_right_plus_q_left": q_total,
        "young_source_counts_by_layer_1_to_14": source_counts,
        "young_source_layer_instances": young_source_layer_instances,
        "dense_thin_flops_per_source_per_total_query_width": "8*n^2*q_total",
        "young_action_lower_flops": int(young_action_flops),
        "budget_flops": int(budget),
        "cap_fraction": cap_fraction,
        "cap_flops": cap_flops,
        "young_action_fraction_of_budget": young_action_flops / budget,
        "young_action_over_cap_flops": young_action_flops - cap_flops,
        "passes_cap": young_action_flops <= cap_flops,
        "information_lower_bound_scalars_per_layer": n * (n - 1),
        "full_d21_entries_per_layer": n * n,
        "information_fraction_of_full_d21": (n * (n - 1)) / (n * n),
        "public_namespace_crosscheck_units": public_units,
        "public_namespace_crosscheck_sum_units": public_crosscheck_units,
        "scope": (
            "FLOP lower bound is conditional on the pinned V29 dense-young "
            "factor/source-action circuit and standard dense-thin action identities; "
            "the information lower bound is algebraic."
        ),
    }

def main() -> None:
    table = load_public_table()
    witness = exact_small_witness()
    primary = primary_term_check(table)
    cost = production_lower_bound()

    gates = {
        "q_total_below_n_minus_1_in_witness":
            witness["q_total"] < witness["threshold_n_minus_1"],
        "hidden_zero_diag_state_exists":
            witness["zero_diagonal_exact"],
        "same_right_action_transcript":
            witness["right_action_exact_zero"],
        "same_left_action_transcript":
            witness["left_action_exact_zero"],
        "public_quadratic_d21_term_verified":
            primary["found_in_pinned_public_table"],
        "quadratic_term_separates_hidden_state":
            witness["quadratic_closure_square_nonzero"] and primary["multiplier_nonzero"],
        "production_action_floor_exceeds_cap":
            not cost["passes_cap"],
    }
    terminal = all(gates.values())

    result = {
        "schema": "arc.whitebox.e152.final_observable_action_gate.v1",
        "experiment": "E152",
        "idempotency_key": "ARC-E152-FINAL-OBSERVABLE-ADJOINT-THEORY-GATE-20260921",
        "public_commit": PUBLIC_COMMIT,
        "exact_small_witness": witness,
        "primary_term_check": primary,
        "production_lower_bound": cost,
        "gates": gates,
        "decision": (
            "E152_TERMINAL_NO_GO_EXACT_FINAL_OBSERVABLE_ACTION_ONLY"
            if terminal
            else "E152_THEORY_GATE_INCOMPLETE"
        ),
        "terminal_no_go": terminal,
        "scope": {
            "target_free": True,
            "benchmark_targets": False,
            "public_data": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "physical_network_run": False,
            "rank_sweep": False,
            "basis_sweep": False,
            "e142_replay": False,
            "e147_replay": False,
            "e148_replay": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E152_THEORY_GATE=" + json.dumps(result, sort_keys=True))
    if not terminal:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
