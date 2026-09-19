from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

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

WIDTHS = tuple(range(2, 9))
DEPTH = 4
PRODUCTION_WIDTH = 1024
BUDGET_LOG2 = 41
UTIL_CAP = 0.13
OUT = Path("e112-mask-message-treewidth.json")


def _array_sha256(arrays: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for x in arrays:
        h.update(np.ascontiguousarray(x).tobytes())
    return h.hexdigest()


def _one_pass() -> dict:
    width_rows = []
    all_dense = True
    all_full_rank = True
    all_complete = True
    all_tw_dense = True
    all_masks_feasible = True
    all_finite = True

    for n in WIDTHS:
        seed = 112000 + n
        weights = make_dense_he_weights(n, DEPTH, seed)
        layer_rows = []

        feasible_masks = first_layer_mask_count_if_onto(weights[0])
        all_masks_feasible &= feasible_masks == (1 << n)

        for layer, w in enumerate(weights):
            density = support_density(w)
            rank = numeric_rank(w)
            scopes = scopes_from_weight_support(w)
            graph = graph_from_factor_scopes(n, scopes)
            tw = exact_treewidth(graph)
            min_abs = float(np.min(np.abs(w)))
            max_abs = float(np.max(np.abs(w)))
            complete = is_complete_graph(graph)

            row = {
                "layer": layer,
                "support_density": density,
                "rank": rank,
                "min_abs_weight": min_abs,
                "max_abs_weight": max_abs,
                "factor_scope_sizes": [len(s) for s in scopes],
                "primal_complete": complete,
                "exact_treewidth": tw.treewidth,
                "witness_order": list(tw.order),
                "bag_bits": tw.treewidth + 1,
                "explicit_table_states": 1 << (tw.treewidth + 1),
            }
            layer_rows.append(row)

            all_dense &= density == 1.0
            all_full_rank &= rank == n
            all_complete &= complete
            all_tw_dense &= tw.treewidth == n - 1
            all_finite &= math.isfinite(min_abs) and math.isfinite(max_abs)

        width_rows.append(
            {
                "width": n,
                "depth": DEPTH,
                "seed": seed,
                "weights_sha256": _array_sha256(weights),
                "first_layer_feasible_mask_count": feasible_masks,
                "expected_all_mask_count": 1 << n,
                "layers": layer_rows,
            }
        )

    max_bag_bits = max_budget_bag_bits(UTIL_CAP, BUDGET_LOG2)
    prod_bag_bits = PRODUCTION_WIDTH
    prod_tw = PRODUCTION_WIDTH - 1
    prod_log2_util_lower = explicit_table_log2_util_lower_bound(
        prod_bag_bits, BUDGET_LOG2
    )
    prod_log10_states = PRODUCTION_WIDTH * math.log10(2.0)
    prod_log10_util_lower = prod_log2_util_lower * math.log10(2.0)
    budget_cap_flops = UTIL_CAP * (2**BUDGET_LOG2)

    integrity = {
        "all_values_finite": all_finite,
        "all_weight_matrices_fully_dense": all_dense,
        "all_weight_matrices_full_rank": all_full_rank,
        "all_primal_graphs_complete": all_complete,
        "all_exact_treewidth_equal_n_minus_1": all_tw_dense,
        "all_first_layer_masks_feasible_by_onto_certificate": all_masks_feasible,
        "no_external_target_access": True,
    }
    structural_confirmation = bool(all(integrity.values()))

    production = {
        "width": PRODUCTION_WIDTH,
        "dense_primal_treewidth_theorem": prod_tw,
        "required_bag_bits": prod_bag_bits,
        "max_bag_bits_from_one_flop_per_state_budget": max_bag_bits,
        "explicit_table_state_count_decimal": str(1 << PRODUCTION_WIDTH),
        "explicit_table_log10_states": prod_log10_states,
        "budget_flops": 2**BUDGET_LOG2,
        "utilization_cap": UTIL_CAP,
        "budget_cap_flops": budget_cap_flops,
        "one_flop_per_state_log2_utilization_lower_bound": prod_log2_util_lower,
        "one_flop_per_state_log10_utilization_lower_bound": prod_log10_util_lower,
        "representation_fits_budget": prod_bag_bits <= max_bag_bits,
    }

    terminal_no_go = structural_confirmation and not production["representation_fits_budget"]

    return {
        "schema": "arc.whitebox.e112.mask_message_treewidth_falsifier.v1",
        "experiment": "E112",
        "idempotency_key": "ARC-E112-EXACT-MASK-MESSAGE-TREEWIDTH-20260919",
        "candidate": "exact finite-state activation-mask junction-tree message passing",
        "widths": list(WIDTHS),
        "depth": DEPTH,
        "width_results": width_rows,
        "integrity_gates": integrity,
        "small_structural_confirmation": structural_confirmation,
        "production_lower_bound": production,
        "scientific_go": False,
        "production_shape_authorized": False,
        "decision": (
            "TERMINAL_STRUCTURAL_NO_GO_DROP"
            if terminal_no_go
            else "SMALL_STRUCTURAL_GO_REQUIRES_SEPARATE_ADMISSION"
        ),
        "blocker": (
            "Dense full-scope mask factors induce K_n; full-rank first layer makes all "
            "2^n sign masks feasible. Exact explicit junction-tree messages therefore "
            "need a 2^n table. At n=1024, even one FLOP per state exceeds the 0.13*2^41 "
            "budget by an astronomical factor."
            if terminal_no_go
            else None
        ),
        "scope": {
            "cheap_structural_only": True,
            "trajectory_forward_pass": False,
            "production_shape_run": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main() -> None:
    first = _one_pass()
    second = _one_pass()
    first_bytes = json.dumps(first, sort_keys=True, separators=(",", ":")).encode()
    second_bytes = json.dumps(second, sort_keys=True, separators=(",", ":")).encode()
    deterministic = first_bytes == second_bytes

    first["deterministic_replay"] = {
        "bitwise_json_equal": deterministic,
        "first_sha256": hashlib.sha256(first_bytes).hexdigest(),
        "second_sha256": hashlib.sha256(second_bytes).hexdigest(),
    }
    if not deterministic:
        first["decision"] = "TERMINAL_INTEGRITY_NO_GO"
        first["production_shape_authorized"] = False

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E112_MASK_MESSAGE_TREEWIDTH=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
