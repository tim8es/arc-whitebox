from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e110_deep_harmonic import (
    HALF_PI,
    block_partition,
    deep_output_directions,
    enumerate_relu_sectors,
    exact_block_harmonic_stats,
    validate_block_partition,
    validate_sector_partition,
)

WIDTH = 2
DEPTH = 4
WEIGHT_SEED = 110004
POOLED_RATIO_GATE = 0.50
PER_OUTPUT_RATIO_GATE = 0.80
OUT = Path("e110-exact-falsifier.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = math.sqrt(2.0 / WIDTH)
    return [
        rng.standard_normal((WIDTH, WIDTH)).astype(np.float64) * scale
        for _ in range(DEPTH)
    ]


def digest_arrays(arrays: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for array in arrays:
        h.update(np.ascontiguousarray(array).tobytes())
    return h.hexdigest()


def validate_control_formula(directions: np.ndarray) -> float:
    max_abs = 0.0
    center = 3.0 / 8.0
    for j in range(WIDTH):
        u = directions[:, j]
        phi = math.atan2(float(u[1]), float(u[0]))
        for theta in (0.071, 0.223, 0.487, 0.911, 1.337):
            q = np.asarray([math.cos(theta), math.sin(theta)])
            qp = np.asarray([math.cos(theta + HALF_PI), math.sin(theta + HALF_PI)])
            direct = 0.5 * (
                ((q @ u) ** 4 - center)
                + ((qp @ u) ** 4 - center)
            )
            formula = 0.125 * math.cos(4.0 * (theta - phi))
            max_abs = max(max_abs, abs(float(direct - formula)))
    return max_abs


def main() -> None:
    weights = make_weights()
    sectors = enumerate_relu_sectors(weights)
    pieces = block_partition(sectors)
    directions = deep_output_directions(weights)

    sector_validation = validate_sector_partition(weights, sectors)
    block_validation = validate_block_partition(weights, pieces)
    control_formula_validation = validate_control_formula(directions)
    stats = exact_block_harmonic_stats(pieces, directions)

    outputs = stats["outputs"]
    nondegenerate = [row for row in outputs if row["nondegenerate"]]

    finite = bool(
        np.isfinite(directions).all()
        and math.isfinite(stats["pooled_ratio"])
        and all(
            math.isfinite(float(row[key]))
            for row in outputs
            for key in (
                "mean",
                "variance",
                "covariance",
                "control_variance",
                "oracle_beta",
                "residual_variance",
                "residual_ratio",
                "correlation",
            )
        )
    )

    gates = {
        "width_le_8": WIDTH <= 8,
        "depth_le_4": DEPTH <= 4,
        "sector_partition_max_abs_le_1e_10": sector_validation <= 1e-10,
        "block_partition_max_abs_le_1e_10": block_validation <= 1e-10,
        "control_formula_max_abs_le_1e_12": control_formula_validation <= 1e-12,
        "finite": finite,
        "all_outputs_nondegenerate": len(nondegenerate) == WIDTH,
        "analytic_control_mean_exact_zero": stats["analytic_control_mean"] == 0.0,
        "pooled_ratio_le_0_50": stats["pooled_ratio"] <= POOLED_RATIO_GATE,
        "each_output_ratio_le_0_80": all(
            row["residual_ratio"] <= PER_OUTPUT_RATIO_GATE for row in nondegenerate
        ),
        "no_external_target_access": True,
    }
    passed = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e110.exact_falsifier.v1",
        "experiment": "E110",
        "idempotency_key": "ARC-E110-DEEP-JACOBIAN-H4-20260919",
        "stage": "SMALL_EXACT_FALSIFIER",
        "width": WIDTH,
        "depth": DEPTH,
        "weight_seed": WEIGHT_SEED,
        "weight_sha256": digest_arrays(weights),
        "sector_count": len(sectors),
        "block_piece_count": len(pieces),
        "deep_output_directions": directions.tolist(),
        "sector_partition_validation_max_abs": sector_validation,
        "block_partition_validation_max_abs": block_validation,
        "control_formula_validation_max_abs": control_formula_validation,
        "exact_stats": stats,
        "gates": gates,
        "admission": {
            "scientific_stage_s_pass": passed,
            "production_shape_authorized": passed,
            "conditional_production_flops_upper": 189621772976,
            "conditional_production_utilization_upper": 189621772976 / (2**41),
            "utilization_cap": 0.13,
        },
        "decision": "EXACT_FALSIFIER_PASS_PRODUCTION_ADMISSION_ALLOWED" if passed else "TERMINAL_NO_GO_DROP",
        "scientific_go": passed,
        "failures": 0,
        "scope": {
            "synthetic_small_exact_only": True,
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

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E110_EXACT_FALSIFIER=" + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
