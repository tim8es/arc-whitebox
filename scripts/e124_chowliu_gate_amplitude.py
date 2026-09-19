#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from methods.e124_chowliu_gate_amplitude import (
    exact_gaussian_mean,
    he_weights,
    linked_cluster_final_mean,
    enumerate_sectors,
    partition_diagnostics,
    penultimate_stats,
    production_flop_proof,
    propagate_one_layer,
    stats_integrity,
)

WIDTH = 8
DEPTH = 4
SEEDS = tuple(range(124200, 124208))
RAW_TARGET = 1.89e-8
OUT = Path("e124-chowliu-gate-amplitude.json")


def _one_pass() -> dict:
    records = []
    linked_biases = []
    ind_biases = []
    improvement_count = 0
    all_integrity = True

    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)

        pen_sectors = enumerate_sectors(weights[:-1])
        pen_partition = partition_diagnostics(pen_sectors)
        stats = penultimate_stats(pen_sectors)
        stat_diag = stats_integrity(stats)

        independent, linked = linked_cluster_final_mean(stats, weights[-1])

        final_sectors = propagate_one_layer(pen_sectors, weights[-1])
        final_partition = partition_diagnostics(final_sectors)
        exact = exact_gaussian_mean(final_sectors)

        ind_bias = independent - exact
        linked_bias = linked - exact
        ind_mse = float(np.mean(ind_bias * ind_bias))
        linked_mse = float(np.mean(linked_bias * linked_bias))
        if linked_mse < ind_mse:
            improvement_count += 1

        linked_biases.append(linked_bias)
        ind_biases.append(ind_bias)

        integrity = {
            "penultimate_partition_finite": pen_partition["finite"],
            "penultimate_partition_complete": pen_partition["complete"],
            "penultimate_partition_ordered": pen_partition["ordered"],
            "final_partition_finite": final_partition["finite"],
            "final_partition_complete": final_partition["complete"],
            "final_partition_ordered": final_partition["ordered"],
            "stats_finite": stat_diag["finite"],
            "gate_probability_range_ok": stat_diag["gate_probability_range_ok"],
            "pair_nonnegative": stat_diag["pair_nonnegative"],
            "pair_sum_error_le_1e_12": stat_diag["pair_sum_max_abs_error"] <= 1e-12,
            "pair_marginal_error_le_1e_12": stat_diag["pair_marginal_max_abs_error"] <= 1e-12,
            "marginal_mean_reconstruction_le_1e_12": (
                stat_diag["marginal_mean_reconstruction_max_abs_error"] <= 1e-12
            ),
            "pair_mean_reconstruction_le_1e_12": (
                stat_diag["pair_mean_reconstruction_max_abs_error"] <= 1e-12
            ),
            "tree_edge_count_7": stat_diag["tree_edge_count"] == WIDTH - 1,
            "tree_connected": stat_diag["tree_connected"],
            "tree_acyclic": stat_diag["tree_acyclic"],
            "candidate_and_exact_finite": bool(
                np.isfinite(independent).all()
                and np.isfinite(linked).all()
                and np.isfinite(exact).all()
            ),
        }
        all_integrity &= bool(all(integrity.values()))

        nonzero_mi = stats.mutual_information[np.triu_indices(WIDTH, 1)]

        records.append(
            {
                "seed": seed,
                "penultimate_sector_count": len(pen_sectors),
                "final_sector_count": len(final_sectors),
                "tree_edges": [list(x) for x in stats.tree_edges],
                "mutual_information_min": float(np.min(nonzero_mi)),
                "mutual_information_max": float(np.max(nonzero_mi)),
                "gate_prob_min": float(np.min(stats.gate_prob)),
                "gate_prob_max": float(np.max(stats.gate_prob)),
                "exact_final_mean": exact.tolist(),
                "independence_final_mean": independent.tolist(),
                "linked_final_mean": linked.tolist(),
                "independence_bias": ind_bias.tolist(),
                "linked_bias": linked_bias.tolist(),
                "independence_bias_mse": ind_mse,
                "linked_bias_mse": linked_mse,
                "linked_improves": linked_mse < ind_mse,
                "integrity": integrity,
                "stats_diagnostics": stat_diag,
                "penultimate_partition": pen_partition,
                "final_partition": final_partition,
            }
        )

    linked_flat = np.concatenate(linked_biases)
    ind_flat = np.concatenate(ind_biases)
    pooled_linked_mse = float(np.mean(linked_flat * linked_flat))
    pooled_ind_mse = float(np.mean(ind_flat * ind_flat))
    per_network_linked = [float(r["linked_bias_mse"]) for r in records]

    proof = production_flop_proof()

    gates = {
        "all_integrity_gates": all_integrity,
        "pooled_linked_mse_le_1_89e_8": pooled_linked_mse <= RAW_TARGET,
        "every_network_linked_mse_le_1_89e_8": all(
            x <= RAW_TARGET for x in per_network_linked
        ),
        "pooled_linked_strictly_below_independence": pooled_linked_mse < pooled_ind_mse,
        "linked_improves_at_least_6_of_8": improvement_count >= 6,
        "production_util_upper_le_0_13": proof["utilization_upper"] <= 0.13,
        "production_flop_formula_matches_protocol": proof["matches_frozen_protocol_upper"],
        "no_targets_public_scorer_holdout_full": True,
    }
    go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e124.chowliu_gate_amplitude.v1",
        "experiment": "E124",
        "idempotency_key": "ARC-E124-CHOWLIU-GATE-AMPLITUDE-CLUSTER-20260920",
        "mechanism": {
            "name": "Chow-Liu gate-amplitude linked-cluster late-ReLU closure",
            "full_mask_state": False,
            "gaussian_plugin": False,
            "shared_source_orbit": False,
            "control_variate": False,
            "tree_score": "binary gate mutual information",
            "tree_root": 0,
            "pair_state": "2x2 gate law plus endpoint conditional amplitude means",
        },
        "frozen_corpus": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seeds": list(SEEDS),
            "weight_law": "iid He-normal float64, zero bias",
            "exact_reference": "piecewise angular integration with analytic E[R]",
        },
        "records": records,
        "summary": {
            "raw_target_mse": RAW_TARGET,
            "pooled_linked_bias_mse": pooled_linked_mse,
            "pooled_independence_bias_mse": pooled_ind_mse,
            "linked_over_independence_mse": (
                pooled_linked_mse / pooled_ind_mse if pooled_ind_mse > 0.0 else None
            ),
            "linked_improvement_count": improvement_count,
            "max_network_linked_mse": max(per_network_linked),
            "min_network_linked_mse": min(per_network_linked),
            "pooled_linked_over_raw_target": pooled_linked_mse / RAW_TARGET,
        },
        "production_flop_proof": proof,
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E124_LOCAL_SCIENTIFIC_GO"
            if go
            else "TERMINAL_NO_GO_DROP_CHOWLIU_GATE_AMPLITUDE_CLUSTER"
        ),
        "scope": {
            "synthetic_exact_small_width_only": True,
            "candidate_reads_exact_final_reference": False,
            "production_scientific_run": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main() -> None:
    first = _one_pass()
    second = _one_pass()

    a = json.dumps(first, sort_keys=True, separators=(",", ":")).encode()
    b = json.dumps(second, sort_keys=True, separators=(",", ":")).encode()
    deterministic = a == b
    first["deterministic_replay"] = {
        "bitwise_json_equal": deterministic,
        "first_sha256": hashlib.sha256(a).hexdigest(),
        "second_sha256": hashlib.sha256(b).hexdigest(),
    }
    if not deterministic:
        first["scientific_go"] = False
        first["decision"] = "TERMINAL_INTEGRITY_NO_GO_NONDETERMINISTIC"

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E124_CHOWLIU=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
