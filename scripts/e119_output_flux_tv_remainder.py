#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e118_output_flux_sketch import run_flux_sketch
from methods.e119_output_flux_tv_remainder import (
    output_observable,
    production_overhead_upper_flops,
    sketch_remainder_certificate,
)

CELLS = 1024
WIDTH = 8
DEPTH = 4
SEEDS = (114200, 114201, 114202, 114203)
RMS_LIMIT = 1.3747727085e-4
E118_PRODUCTION_UPPER = 73_719_476_736
BUDGET = 2**41
OUT = Path("e119-output-flux-tv-remainder.json")


def _one_pass() -> dict:
    c = output_observable(WIDTH)
    records = []
    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)
        cert = sketch_remainder_certificate(weights, cells=CELLS, observable=c)
        ref = build_exact_reference(weights)
        sketch = run_flux_sketch(weights, cells=CELLS, budget=BUDGET)

        scalar_jumps = np.asarray(ref.boundary_jumps, dtype=np.float64) @ c
        exact_tv = float(np.sum(np.abs(scalar_jumps)))
        exact_mean = float(c @ ref.mean)
        exact_flux_mean = float(
            math.sqrt(math.pi / 2.0)
            / (2.0 * math.pi)
            * float(c @ ref.flux_sum)
        )
        exact_flux_identity_error = abs(exact_mean - exact_flux_mean)
        exact_sketch_bias = float(sketch.mean - exact_mean)

        records.append(
            {
                "seed": seed,
                "boundary_count": int(ref.boundary_jumps.shape[0]),
                "exact_scalar_total_variation": exact_tv,
                "weight_only_scalar_tv_bound": cert.scalar_tv_bound,
                "tv_bound_over_exact": (
                    cert.scalar_tv_bound / exact_tv if exact_tv > 0.0 else math.inf
                ),
                "angular_factor": cert.angular_factor,
                "gaussian_factor": cert.gaussian_factor,
                "computable_absolute_mean_bound": cert.absolute_mean_bound,
                "exact_sketch_bias": exact_sketch_bias,
                "exact_sketch_abs_bias": abs(exact_sketch_bias),
                "bound_over_actual_abs_bias": (
                    cert.absolute_mean_bound / abs(exact_sketch_bias)
                    if exact_sketch_bias != 0.0
                    else math.inf
                ),
                "exact_flux_identity_abs_error": exact_flux_identity_error,
                "tv_certificate_valid": exact_tv <= cert.scalar_tv_bound + 1e-12,
                "sketch_bias_certificate_valid": (
                    abs(exact_sketch_bias) <= cert.absolute_mean_bound + 1e-12
                ),
                "candidate_finite": cert.finite,
                "area_bounds": [x.tolist() for x in cert.area_bounds],
                "variation_bounds": [x.tolist() for x in cert.variation_bounds],
            }
        )

    bounds = np.asarray(
        [r["computable_absolute_mean_bound"] for r in records], dtype=np.float64
    )
    exact_biases = np.asarray(
        [r["exact_sketch_bias"] for r in records], dtype=np.float64
    )
    exact_tvs = np.asarray(
        [r["exact_scalar_total_variation"] for r in records], dtype=np.float64
    )
    tv_bounds = np.asarray(
        [r["weight_only_scalar_tv_bound"] for r in records], dtype=np.float64
    )

    rms_bound = float(np.sqrt(np.mean(bounds * bounds)))
    rms_actual_bias = float(np.sqrt(np.mean(exact_biases * exact_biases)))
    required_tv = float(
        RMS_LIMIT
        / (
            math.sqrt(math.pi / 2.0)
            / (2.0 * math.pi)
            * (1.0 - math.cos(math.pi / CELLS))
        )
    )
    prod_overhead = production_overhead_upper_flops(width=1024, depth=16)
    prod_all_in = E118_PRODUCTION_UPPER + prod_overhead
    prod_util = prod_all_in / BUDGET

    gates = {
        "all_candidate_finite": all(r["candidate_finite"] for r in records),
        "exact_flux_identity_le_1e_10": all(
            r["exact_flux_identity_abs_error"] <= 1e-10 for r in records
        ),
        "tv_bound_dominates_exact_all": all(
            r["tv_certificate_valid"] for r in records
        ),
        "mean_bound_dominates_exact_sketch_bias_all": all(
            r["sketch_bias_certificate_valid"] for r in records
        ),
        "production_util_le_0_13": prod_util <= 0.13,
        "rms_bound_le_1_3747727085e_4": rms_bound <= RMS_LIMIT,
        "no_targets_public_scorer_holdout_full": True,
    }

    decision = (
        "E119_TV_REMAINDER_CERTIFICATE_GO"
        if all(gates.values())
        else "TERMINAL_MATHEMATICAL_NO_GO_CLOSE_TV_REMAINDER"
    )

    return {
        "schema": "arc.whitebox.e119.output_flux_tv_remainder.v1",
        "experiment": "E119",
        "idempotency_key": "ARC-E119-OUTPUT-FLUX-TV-REMAINDER-20260919",
        "mechanism": {
            "name": "weight-only total-variation omitted-boundary flux certificate",
            "cells": CELLS,
            "observable": "c_j=(j+1)/sqrt(sum r^2)",
            "candidate_uses_exact_boundaries": False,
            "candidate_uses_exact_reference": False,
            "recurrence": {
                "first_layer": "A1=V1=2*column_l2_norm(W1)",
                "later_area": "A_next=W_+^T A",
                "later_variation": "V_next=A_next+2*abs(W)^T V",
                "scalar_tv": "abs(c)^T V_L",
                "mean_bound": "g*(1-cos(pi/M))*scalar_tv",
            },
        },
        "frozen_corpus": {
            "width": WIDTH,
            "depth": DEPTH,
            "input_dimension": 2,
            "seeds": list(SEEDS),
        },
        "records": records,
        "summary": {
            "rms_limit": RMS_LIMIT,
            "rms_computable_bound": rms_bound,
            "rms_bound_over_limit": rms_bound / RMS_LIMIT,
            "rms_exact_sketch_bias": rms_actual_bias,
            "rms_bound_over_actual_bias": (
                rms_bound / rms_actual_bias if rms_actual_bias > 0 else math.inf
            ),
            "required_tv_bound_for_limit": required_tv,
            "mean_exact_scalar_tv": float(np.mean(exact_tvs)),
            "mean_weight_only_tv_bound": float(np.mean(tv_bounds)),
            "mean_tv_bound_over_exact": float(np.mean(tv_bounds / exact_tvs)),
        },
        "production_cost": {
            "e118_upper_flops": E118_PRODUCTION_UPPER,
            "certificate_overhead_upper_flops": prod_overhead,
            "all_in_upper_flops": prod_all_in,
            "utilization": prod_util,
            "cap": 0.13,
        },
        "gates": gates,
        "scientific_go": bool(all(gates.values())),
        "decision": decision,
        "scope": {
            "exact_small_width_only": True,
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
        first["decision"] = "TERMINAL_INTEGRITY_NO_GO"

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E119_TV_REMAINDER=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
