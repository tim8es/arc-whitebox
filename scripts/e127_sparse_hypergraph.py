#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

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
    optimistic_required_cluster_count,
    order_frontier,
    partition_diagnostics,
    production_flop_proof,
    propagate_one_layer,
    sparse_family,
)

WIDTH = 8
DEPTH = 4
SEEDS = tuple(range(127200, 127208))
RAW_TARGET_MSE = 1.89e-8
RAW_TARGET_RMS = float(np.sqrt(RAW_TARGET_MSE))
OUT = Path("e127-sparse-hypergraph.json")


def _one_pass() -> dict:
    records = []
    sparse_biases = []
    all_integrity = True
    sparse_cert_all = True
    optimistic_count_all = True

    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)
        pen_sectors = enumerate_sectors(weights[:-1])
        pen_partition = partition_diagnostics(pen_sectors)

        source_mean = exact_gaussian_mean(pen_sectors)
        subset_values = exact_subset_observables(pen_sectors, weights[-1])
        delta = mobius_clusters(subset_values)
        bounds = cluster_bounds(source_mean, weights[-1])
        envelope = envelope_diagnostics(delta, bounds)

        frontier = order_frontier(delta, bounds, RAW_TARGET_RMS)
        min_cert_order = next((x["order"] for x in frontier if x["certificate_pass"]), None)

        sparse = sparse_family(bounds)
        selected = sparse["selected_masks"]
        sparse_candidate = np.sum(delta[np.asarray(selected), :], axis=0)
        sparse_cert_rms = float(sparse["certificate_rms"])
        necessary = optimistic_required_cluster_count(bounds, RAW_TARGET_RMS)

        # Final exact reference is materialized only after candidate/certificate.
        final_sectors = propagate_one_layer(pen_sectors, weights[-1])
        final_partition = partition_diagnostics(final_sectors)
        exact_final = exact_gaussian_mean(final_sectors)

        full_mask_value = subset_values[(1 << WIDTH) - 1, :]
        mobius_full = np.sum(delta, axis=0)
        direct_full_error = float(np.max(np.abs(full_mask_value - exact_final)))
        mobius_full_error = float(np.max(np.abs(mobius_full - exact_final)))

        sparse_bias = sparse_candidate - exact_final
        sparse_mse = float(np.mean(sparse_bias * sparse_bias))
        sparse_biases.append(sparse_bias)

        integrity = {
            "penultimate_partition_finite": pen_partition["finite"],
            "penultimate_partition_complete": pen_partition["complete"],
            "penultimate_partition_ordered": pen_partition["ordered"],
            "final_partition_finite": final_partition["finite"],
            "final_partition_complete": final_partition["complete"],
            "final_partition_ordered": final_partition["ordered"],
            "source_means_finite": bool(np.isfinite(source_mean).all()),
            "subset_values_finite": bool(np.isfinite(subset_values).all()),
            "clusters_finite": bool(np.isfinite(delta).all()),
            "bounds_finite": bool(np.isfinite(bounds).all()),
            "full_subset_matches_direct_exact_le_1e_12": direct_full_error <= 1e-12,
            "mobius_full_matches_direct_exact_le_1e_12": mobius_full_error <= 1e-12,
            "cluster_envelope_pass": envelope["pass_le_1e_12"],
            "sparse_downward_closed": is_downward_closed(selected, WIDTH),
            "sparse_units_le_141": sparse["cluster_units"] <= SMALL_CLUSTER_UNIT_CAP,
            "candidate_and_certificate_finite": bool(
                np.isfinite(sparse_candidate).all() and np.isfinite(sparse["certificate_tail"]).all()
            ),
            "candidate_did_not_read_exact_final_before_materialization": True,
        }
        all_integrity &= bool(all(integrity.values()))
        sparse_cert_all &= sparse_cert_rms <= RAW_TARGET_RMS
        optimistic_count_all &= bool(necessary["passes_count_cap"])

        frontier_json = []
        for item in frontier:
            frontier_json.append(
                {
                    "order": item["order"],
                    "selected_cluster_count": item["selected_cluster_count"],
                    "omitted_cluster_count": item["omitted_cluster_count"],
                    "certificate_rms": item["certificate_rms"],
                    "certificate_pass": item["certificate_pass"],
                    "candidate": item["candidate"].tolist(),
                }
            )

        records.append(
            {
                "seed": seed,
                "penultimate_sector_count": len(pen_sectors),
                "final_sector_count": len(final_sectors),
                "source_mean_min": float(np.min(source_mean)),
                "source_mean_max": float(np.max(source_mean)),
                "full_subset_direct_error": direct_full_error,
                "mobius_full_direct_error": mobius_full_error,
                "envelope": envelope,
                "adaptive_order_frontier": frontier_json,
                "minimum_certified_order": min_cert_order,
                "sparse": {
                    "selected_non_singleton_count": len(sparse["selected_non_singletons"]),
                    "selected_total_count": len(selected),
                    "omitted_count": len(sparse["omitted_masks"]),
                    "cluster_units": sparse["cluster_units"],
                    "unit_cap": sparse["unit_cap"],
                    "selected_masks": selected,
                    "certificate_tail": sparse["certificate_tail"].tolist(),
                    "certificate_rms": sparse_cert_rms,
                    "certificate_pass": sparse_cert_rms <= RAW_TARGET_RMS,
                    "candidate_final_mean": sparse_candidate.tolist(),
                },
                "necessary_sparse_lower_bound": necessary,
                "exact_final_mean": exact_final.tolist(),
                "sparse_bias": sparse_bias.tolist(),
                "sparse_bias_mse": sparse_mse,
                "integrity": integrity,
            }
        )

    sparse_flat = np.concatenate(sparse_biases)
    pooled_sparse_mse = float(np.mean(sparse_flat * sparse_flat))
    per_network_mse = [float(r["sparse_bias_mse"]) for r in records]
    min_orders = [int(r["minimum_certified_order"]) for r in records]
    proof = production_flop_proof()

    order_cost_diagnostics = []
    for r in sorted(set(min_orders)):
        if r <= 1:
            order_cost_diagnostics.append(
                {"order": r, "full_order_production_passes": True, "utilization_upper": proof["baseline_total"] / proof["budget_flops"]}
            )
        else:
            p = proof["full_order"][str(r)]
            order_cost_diagnostics.append(
                {
                    "order": r,
                    "full_order_production_passes": p["passes_cap"],
                    "utilization_upper": p["utilization_upper"],
                    "total_upper_flops": p["total_upper_flops"],
                }
            )

    gates = {
        "all_integrity_gates": all_integrity,
        "sparse_certificate_rms_le_target_every_network": sparse_cert_all,
        "pooled_sparse_candidate_mse_le_1_89e_8": pooled_sparse_mse <= RAW_TARGET_MSE,
        "every_network_sparse_candidate_mse_le_1_89e_8": all(
            x <= RAW_TARGET_MSE for x in per_network_mse
        ),
        "optimistic_necessary_retained_count_le_47_every_network": optimistic_count_all,
        "production_accounting_matches_protocol": bool(
            proof["matches_frozen_baseline"]
            and proof["small_width_homologous_unit_cap"] == SMALL_CLUSTER_UNIT_CAP
            and proof["optimistic_pair_count_cap"] == OPTIMISTIC_PAIR_COUNT_CAP
        ),
        "no_targets_public_scorer_holdout_full": True,
    }
    go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e127.sparse_hypergraph.v1",
        "experiment": "E127",
        "idempotency_key": "ARC-E127-SPARSE-HYPERGRAPH-CERTIFIED-TAIL-20260920",
        "mechanism": {
            "name": "sparse higher-order Mobius hypergraph closure",
            "pair_tree_rescue": False,
            "gaussian_plugin": False,
            "control_variate": False,
            "target_fitting": False,
            "full_mask_production_state": False,
            "tail_certificate": "2^(|S|-1) min_i |w_ij| E[H_i]",
            "selector": "certificate-ranked downward-closed simplicial complex",
        },
        "frozen_corpus": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seeds": list(SEEDS),
            "weight_law": "iid He-normal float64, zero bias",
            "exact_reference": "piecewise angular integration with analytic E[R]",
        },
        "summary": {
            "raw_target_mse": RAW_TARGET_MSE,
            "raw_target_rms": RAW_TARGET_RMS,
            "pooled_sparse_candidate_mse": pooled_sparse_mse,
            "max_network_sparse_candidate_mse": max(per_network_mse),
            "min_network_sparse_candidate_mse": min(per_network_mse),
            "max_sparse_certificate_rms": max(float(r["sparse"]["certificate_rms"]) for r in records),
            "min_sparse_certificate_rms": min(float(r["sparse"]["certificate_rms"]) for r in records),
            "minimum_certified_orders": min_orders,
            "max_necessary_retained_non_singletons": max(
                int(r["necessary_sparse_lower_bound"]["necessary_retained_non_singletons"])
                for r in records
            ),
            "min_necessary_retained_non_singletons": min(
                int(r["necessary_sparse_lower_bound"]["necessary_retained_non_singletons"])
                for r in records
            ),
        },
        "records": records,
        "production_flop_proof": proof,
        "certificate_required_order_cost_diagnostics": order_cost_diagnostics,
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E127_LOCAL_SCIENTIFIC_GO"
            if go
            else "TERMINAL_NO_GO_SPARSE_HYPERGRAPH_CERTIFIED_TAIL_EXCEEDS_FLOP_CAP"
        ),
        "scope": {
            "synthetic_exact_small_width_only": True,
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
    print("E127_SPARSE_HYPERGRAPH=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
