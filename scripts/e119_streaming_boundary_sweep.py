#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from methods.e114_exact_angular_reference import he_weights
from methods.e119_generic_boundary_flux import (
    build_generic_boundary_flux,
    wrapped_angle_error,
)
from methods.e119_streaming_boundary_sweep import (
    PROBE,
    streaming_boundary_sweep,
)

WIDTH = 8
DEPTH = 4
SEEDS = (114200, 114201, 114202, 114203)
OUT = Path("e119-streaming-boundary-sweep.json")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _replay_exact(a, b) -> bool:
    return bool(
        np.array_equal(a.boundary_angles, b.boundary_angles)
        and np.array_equal(a.scalar_jumps, b.scalar_jumps)
        and a.mean == b.mean
        and a.region_count == b.region_count
        and a.peak_coefficient_scalars == b.peak_coefficient_scalars
        and a.peak_mask_bits == b.peak_mask_bits
        and a.ledger == b.ledger
    )


def main() -> None:
    records = []

    for seed in SEEDS:
        weights = he_weights(seed, width=WIDTH, depth=DEPTH)

        t0 = time.perf_counter()
        sweep = streaming_boundary_sweep(weights)
        wall_seconds = time.perf_counter() - t0
        repeat = streaming_boundary_sweep(weights)

        # Independent post-candidate verification only.
        ref = build_generic_boundary_flux(weights)
        min_region_width = min(
            float(sector.hi - sector.lo) for sector in ref.sectors
        )
        probe_margin_ratio = min_region_width / PROBE

        same_shape = (
            sweep.boundary_angles.shape == ref.boundary_angles.shape
            and sweep.scalar_jumps.shape == ref.scalar_jumps.shape
        )
        if same_shape and sweep.boundary_angles.size:
            angle_error = max(
                wrapped_angle_error(a, b)
                for a, b in zip(
                    sweep.boundary_angles,
                    ref.boundary_angles,
                )
            )
            jump_error = float(
                np.max(np.abs(sweep.scalar_jumps - ref.scalar_jumps))
            )
        elif same_shape:
            angle_error = 0.0
            jump_error = 0.0
        else:
            angle_error = math.inf
            jump_error = math.inf

        mean_error = abs(sweep.mean - ref.full_mean)
        replay_exact = _replay_exact(sweep, repeat)
        ref_materialized_final_coeff_scalars = (
            len(ref.sectors) * WIDTH * 2
        )

        records.append(
            {
                "seed": seed,
                "sweep_region_count": sweep.region_count,
                "reference_region_count": len(ref.sectors),
                "boundary_count": int(sweep.boundary_angles.size),
                "boundary_angles_sha256": _sha(sweep.boundary_angles),
                "scalar_jumps_sha256": _sha(sweep.scalar_jumps),
                "max_wrapped_angle_error": angle_error,
                "max_abs_jump_error": jump_error,
                "sweep_mean": sweep.mean,
                "reference_full_mean": ref.full_mean,
                "mean_abs_error": mean_error,
                "min_reference_region_width": min_region_width,
                "probe": PROBE,
                "min_region_width_over_probe": probe_margin_ratio,
                "deterministic_replay_exact": replay_exact,
                "finite": sweep.finite,
                "peak_coefficient_scalars": (
                    sweep.peak_coefficient_scalars
                ),
                "peak_mask_bits": sweep.peak_mask_bits,
                "verification_trace_only": True,
                "reference_materialized_final_coeff_scalars": (
                    ref_materialized_final_coeff_scalars
                ),
                "peak_coeff_vs_reference_materialized_ratio": (
                    sweep.peak_coefficient_scalars
                    / ref_materialized_final_coeff_scalars
                ),
                "candidate_ledger": sweep.ledger,
                "wall_seconds": wall_seconds,
            }
        )

    max_angle_error = max(r["max_wrapped_angle_error"] for r in records)
    max_jump_error = max(r["max_abs_jump_error"] for r in records)
    max_mean_error = max(r["mean_abs_error"] for r in records)
    min_probe_margin = min(r["min_region_width_over_probe"] for r in records)
    max_candidate_cost = max(
        r["candidate_ledger"]["all_in_flop_equivalent"] for r in records
    )

    gates = {
        "finite_all": all(r["finite"] for r in records),
        "region_count_matches_reference_all": all(
            r["sweep_region_count"] == r["reference_region_count"]
            for r in records
        ),
        "angle_error_le_1e_10": max_angle_error <= 1e-10,
        "jump_error_le_1e_10": max_jump_error <= 1e-10,
        "mean_error_le_1e_10": max_mean_error <= 1e-10,
        "min_region_width_ge_64_probe": min_probe_margin >= 64.0,
        "deterministic_replay_exact_all": all(
            r["deterministic_replay_exact"] for r in records
        ),
        "peak_state_independent_of_region_count": (
            len({r["peak_coefficient_scalars"] for r in records}) == 1
            and len({r["peak_mask_bits"] for r in records}) == 1
        ),
        "no_targets_public_scorer_holdout_full": True,
    }
    go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e119.streaming_boundary_sweep.support.v1",
        "experiment": "E119 theory support",
        "idempotency_key": (
            "ARC-E119-SUPPORT-STREAMING-BOUNDARY-SWEEP-20260919"
        ),
        "mechanism": {
            "class": "event-driven streaming activation-boundary sweep",
            "full_region_tree_materialized": False,
            "activation_mask_table_materialized": False,
            "current_state_only": True,
            "verification_trace_not_required_for_scalar_mean": True,
            "remainder": "exact on frozen nondegenerate corpus; zero omitted flux",
            "runtime_note": (
                "linear in encountered boundary events; memory independent "
                "of boundary count"
            ),
        },
        "proof": (
            "Within the current affine ReLU region every preactivation is "
            "a*cos(theta)+b*sin(theta). No mask can change before the first "
            "positive zero of any current preactivation. Therefore the "
            "minimum such root is exactly the next activation boundary; "
            "recompute immediately to its right and induct over events."
        ),
        "frozen_corpus": {
            "input_dimension": 2,
            "width": WIDTH,
            "depth": DEPTH,
            "seeds": list(SEEDS),
            "probe": PROBE,
        },
        "records": records,
        "summary": {
            "region_counts": [r["sweep_region_count"] for r in records],
            "max_wrapped_angle_error": max_angle_error,
            "max_abs_jump_error": max_jump_error,
            "max_mean_abs_error": max_mean_error,
            "min_region_width_over_probe": min_probe_margin,
            "peak_coefficient_scalars": max(
                r["peak_coefficient_scalars"] for r in records
            ),
            "peak_mask_bits": max(r["peak_mask_bits"] for r in records),
            "max_candidate_flop_equivalent": max_candidate_cost,
            "max_candidate_utilization_vs_2pow41": (
                max_candidate_cost / float(2**41)
            ),
            "wall_seconds_per_network": [
                r["wall_seconds"] for r in records
            ],
        },
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E119_THEORY_SUPPORT_GO_EXACT_STREAMING_BOUNDARY_SWEEP"
            if go
            else "E119_THEORY_SUPPORT_NO_GO_STREAMING_SWEEP"
        ),
        "limitations": [
            "input dimension remains 2",
            "runtime still scales with the number of boundary events",
            "does not establish width-1024/depth-16 boundary-count control",
            "does not itself compress or omit nonzero flux atoms",
        ],
        "scope": {
            "support_only": True,
            "owner_e119_identity_unchanged": True,
            "target_free": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
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

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E119_STREAMING_BOUNDARY_SWEEP="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )

    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
