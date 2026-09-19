from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from methods.e113_radial_sufficiency import (
    annealed_final_mean_from_state_radius,
    annealed_radius_multiplier,
    exact_angular_layers,
    make_weights,
    quenched_obstruction_certificate,
)

LATENT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 113113
RAW_TARGET = 1.89e-8
OUT = Path("e113-radial-sufficiency.json")


def max_reference_delta(a: dict, b: dict) -> float:
    delta = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        delta = max(
            delta,
            float(
                np.max(
                    np.abs(
                        np.asarray(la["post_mean"], dtype=np.float64)
                        - np.asarray(lb["post_mean"], dtype=np.float64)
                    )
                )
            ),
        )
        for order in (64, 96):
            delta = max(
                delta,
                abs(
                    float(la["expected_radius"][order])
                    - float(lb["expected_radius"][order])
                ),
            )
    return delta


def main() -> None:
    weights = make_weights(
        seed=WEIGHT_SEED,
        latent_dim=LATENT_DIM,
        width=WIDTH,
        depth=DEPTH,
    )

    ref = exact_angular_layers(weights, radius_orders=(64, 96))
    replay = exact_angular_layers(weights, radius_orders=(64, 96))
    replay_max_abs = max_reference_delta(ref, replay)

    final_mean = np.asarray(ref["layers"][-1]["post_mean"], dtype=np.float64)
    obstruction = [
        quenched_obstruction_certificate(w) for w in weights[1:]
    ]

    radius_convergence = []
    plugins = []
    for start_layer in (1, 2, 3):
        layer = ref["layers"][start_layer - 1]
        r64 = float(layer["expected_radius"][64])
        r96 = float(layer["expected_radius"][96])
        rel = abs(r64 - r96) / max(abs(r96), 1e-300)
        radius_convergence.append(
            {
                "start_layer": start_layer,
                "expected_radius_order64": r64,
                "expected_radius_order96": r96,
                "relative_difference": rel,
            }
        )

        remaining = DEPTH - start_layer
        predicted = annealed_final_mean_from_state_radius(
            r96, width=WIDTH, remaining_layers=remaining
        )
        bias = predicted - final_mean
        mse = float(np.mean(bias * bias))
        plugins.append(
            {
                "start_layer": start_layer,
                "remaining_annealed_layers": remaining,
                "predicted_common_final_coordinate_mean": predicted,
                "quenched_final_mean_mse": mse,
                "max_abs_bias": float(np.max(np.abs(bias))),
                "signed_average_bias": float(np.mean(bias)),
                "mse_over_raw_target": mse / RAW_TARGET,
                "passes_raw_target": mse <= RAW_TARGET,
            }
        )

    all_ranks_full = all(c["rank"] == WIDTH for c in obstruction)
    all_active = all(c["active_cone_residual"] <= 1e-10 for c in obstruction)
    all_jacobian_full = all(
        c["local_jacobian_rank"] == WIDTH for c in obstruction
    )
    all_radius_counterexamples = all(
        c["same_radius_delta"] == 0.0
        and c["same_radius_output_l2_delta"] > 1e-6
        for c in obstruction
    )
    radius_quad_ok = all(
        x["relative_difference"] <= 1e-10 for x in radius_convergence
    )
    plugin_all_pass = all(x["passes_raw_target"] for x in plugins)
    strongest_late_pass = plugins[-1]["passes_raw_target"]

    gates = {
        "all_realized_later_weights_full_rank": all_ranks_full,
        "active_cone_certificate_residual_le_1e_10": all_active,
        "local_active_jacobian_rank_eq_width": all_jacobian_full,
        "same_radius_constructive_counterexample": all_radius_counterexamples,
        "exact_final_mean_finite": bool(np.isfinite(final_mean).all()),
        "radius_quadrature_64_vs_96_rel_le_1e_10": radius_quad_ok,
        "deterministic_replay_exact": replay_max_abs == 0.0,
        "no_external_targets": True,
        "all_annealed_start_layers_mse_le_raw_target": plugin_all_pass,
        "late_start_layer3_mse_le_raw_target": strongest_late_pass,
    }

    integrity_names = list(gates)[:8]
    integrity_ok = all(gates[k] for k in integrity_names)
    scientific_ok = plugin_all_pass and strongest_late_pass
    decision = (
        "SMALL_EXACT_RADIAL_PLUGIN_GO"
        if integrity_ok and scientific_ok
        else "TERMINAL_NO_GO_DROP"
    )

    result = {
        "schema": "arc.whitebox.e113.radial_sufficiency_falsifier.v1",
        "experiment": "E113",
        "idempotency_key": "ARC-E113-ANNEALED-RADIAL-SUFFICIENCY-20260919",
        "network": {
            "latent_dim": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "zero_bias": True,
            "weight_law": "iid Gaussian He scale",
        },
        "mathematics": {
            "annealed_positive_closure": (
                "fresh Gaussian next-layer law depends on h only through ||h||"
            ),
            "annealed_radius_multiplier_width8": annealed_radius_multiplier(
                WIDTH, WIDTH
            ),
            "quenched_obstruction": (
                "on the all-positive cone, Jacobian rank is n; any C1 "
                "factorization through R^k has rank <=k, hence k>=n"
            ),
            "obstruction_scope": (
                "full next activation vector; C1 statistic; fixed realized "
                "full-rank square weight"
            ),
        },
        "reference": {
            "type": (
                "exact ReLU angular sectors + analytic final mean; deterministic "
                "Gauss-Legendre only for layer radius expectations"
            ),
            "final_interval_count": ref["final_interval_count"],
            "exact_quenched_final_mean": final_mean.tolist(),
            "raw_target_mse": RAW_TARGET,
        },
        "quenched_obstruction_certificates": obstruction,
        "radius_quadrature_convergence": radius_convergence,
        "annealed_radial_plugin": plugins,
        "determinism": {"replay_max_abs": replay_max_abs},
        "gates": gates,
        "decision": decision,
        "scientific_go": False,
        "production_shape_authorized": False,
        "scope": {
            "small_exact_synthetic_only": True,
            "public": False,
            "public_mini": False,
            "benchmark_targets": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rerun": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E113_RADIAL_SUFFICIENCY=" + json.dumps(result, sort_keys=True), flush=True)

    if not integrity_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
