from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e109_late_gatepair_sign_cv import (
    build_late_prefix_directions_billed,
    build_two_haar_inputs_billed,
    crossfit_correct_billed,
    final_pair_blocks_billed,
    gatepair_features_billed,
    mean_chi_radius,
)

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 109104
SEED_A = 109105
SEED_B = 109106
LATE_LAYER = 12
DIRECTION_ROWS = 128
CONTROLS = 64
BUDGET = 2**41
UTIL_CAP = 0.13
RAW_TARGET = 1.89e-8
MATERIAL_RATIO = 0.90
PRECODE_UPPER_FLOPS = 175_236_871_088
OUT = Path("e109-late-gatepair-sign-cv.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def run_estimator(weights: list[np.ndarray], direction_seed: int) -> dict:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)

        h = build_two_haar_inputs_billed(WIDTH, direction_seed)
        after_input = int(ctx.flops_used)

        input_np = np.asarray(h, dtype=np.float32).copy()
        half = TRAJECTORIES // 2
        antithetic_pair_max_abs = float(
            np.max(np.abs(input_np[:half] + input_np[half:]))
        )

        directions = build_late_prefix_directions_billed(
            weights, layer=LATE_LAYER, rows=DIRECTION_ROWS
        )
        radius = mean_chi_radius(WIDTH)
        q = h[: 2 * WIDTH] / fnp.float32(radius)
        z, analytic_means = gatepair_features_billed(q, directions)
        z1 = z[:WIDTH]
        z2 = z[WIDTH : 2 * WIDTH]
        after_control_setup = int(ctx.flops_used)

        baseline_rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            baseline_rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        y1, y2 = final_pair_blocks_billed(h, WIDTH)
        candidate_final, baseline_final, beta1, beta2 = crossfit_correct_billed(
            y1, y2, z1, z2
        )

        candidate_prediction = fnp.stack(
            baseline_rows[:-1] + [candidate_final], axis=0
        )
        baseline_prediction = fnp.stack(
            baseline_rows[:-1] + [baseline_final], axis=0
        )
        after_stack = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started

    candidate_np = np.asarray(candidate_prediction, dtype=np.float64).copy()
    baseline_np = np.asarray(baseline_prediction, dtype=np.float64).copy()
    directions_np = np.asarray(directions, dtype=np.float64).copy()
    means_np = np.asarray(analytic_means, dtype=np.float64).copy()
    beta1_np = np.asarray(beta1, dtype=np.float64).copy()
    beta2_np = np.asarray(beta2, dtype=np.float64).copy()
    z1_np = np.asarray(z1, dtype=np.float64).copy()
    z2_np = np.asarray(z2, dtype=np.float64).copy()

    input_flops = after_input - start_flops
    control_setup_flops = after_control_setup - after_input
    layer_flops = []
    previous = after_control_setup
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization_flops = after_stack - previous
    reconciled = (
        input_flops
        + control_setup_flops
        + sum(layer_flops)
        + finalization_flops
    )

    direction_norm_error = float(
        np.max(np.abs(np.linalg.norm(directions_np, axis=1) - 1.0))
    )
    baseline_final_recompose = float(
        np.max(
            np.abs(
                baseline_np[-1]
                - np.asarray(baseline_final, dtype=np.float64)
            )
        )
    )
    control_mean_rms = [
        float(np.sqrt(np.mean(np.mean(z1_np, axis=0) ** 2))),
        float(np.sqrt(np.mean(np.mean(z2_np, axis=0) ** 2))),
    ]
    beta_abs_max = float(
        max(np.max(np.abs(beta1_np)), np.max(np.abs(beta2_np)))
    )

    finite = bool(
        np.isfinite(candidate_np).all()
        and np.isfinite(baseline_np).all()
        and np.isfinite(directions_np).all()
        and np.isfinite(means_np).all()
        and np.isfinite(beta1_np).all()
        and np.isfinite(beta2_np).all()
        and np.isfinite(z1_np).all()
        and np.isfinite(z2_np).all()
    )

    return {
        "candidate": candidate_np,
        "baseline": baseline_np,
        "candidate_sha256": digest(candidate_np),
        "baseline_sha256": digest(baseline_np),
        "finite": finite,
        "shape": list(candidate_np.shape),
        "antithetic_pair_max_abs": antithetic_pair_max_abs,
        "direction_norm_max_abs_error": direction_norm_error,
        "analytic_control_mean_min": float(np.min(means_np)),
        "analytic_control_mean_max": float(np.max(means_np)),
        "control_block_mean_rms": control_mean_rms,
        "beta_abs_max": beta_abs_max,
        "baseline_final_recompose_max_abs": baseline_final_recompose,
        "flops": {
            "input_construction": input_flops,
            "control_setup": control_setup_flops,
            "layers": layer_flops,
            "layer_total": int(sum(layer_flops)),
            "finalization": finalization_flops,
            "total": total,
            "reconciled_sum": int(reconciled),
            "exact_reconciliation": bool(reconciled == total),
            "utilization": float(total / BUDGET),
        },
        "wall_s": wall_s,
    }


def risk(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a[-1], dtype=np.float64) - np.asarray(b[-1], dtype=np.float64)
    return float(np.mean(d * d) / 2.0)


def compact(x: dict) -> dict:
    return {k: v for k, v in x.items() if k not in ("candidate", "baseline")}


def main() -> None:
    weights = make_weights()

    a = run_estimator(weights, SEED_A)
    b = run_estimator(weights, SEED_B)
    candidate_risk = risk(a["candidate"], b["candidate"])
    baseline_risk = risk(a["baseline"], b["baseline"])

    a2 = run_estimator(weights, SEED_A)
    b2 = run_estimator(weights, SEED_B)
    candidate_risk2 = risk(a2["candidate"], b2["candidate"])
    baseline_risk2 = risk(a2["baseline"], b2["baseline"])

    ratio = candidate_risk / baseline_risk if baseline_risk > 0.0 else math.inf
    util = max(a["flops"]["utilization"], b["flops"]["utilization"])
    competition_go = bool(candidate_risk <= RAW_TARGET and util <= UTIL_CAP)
    material_go = bool(ratio <= MATERIAL_RATIO and candidate_risk < baseline_risk)

    deterministic = {
        "a_candidate_bitwise": bool(np.array_equal(a["candidate"], a2["candidate"])),
        "b_candidate_bitwise": bool(np.array_equal(b["candidate"], b2["candidate"])),
        "a_baseline_bitwise": bool(np.array_equal(a["baseline"], a2["baseline"])),
        "b_baseline_bitwise": bool(np.array_equal(b["baseline"], b2["baseline"])),
        "candidate_risk_repeat_abs": abs(candidate_risk - candidate_risk2),
        "baseline_risk_repeat_abs": abs(baseline_risk - baseline_risk2),
        "a_flops_equal": a["flops"] == a2["flops"],
        "b_flops_equal": b["flops"] == b2["flops"],
    }

    integrity = {
        "finite_all": all(x["finite"] for x in (a, b, a2, b2)),
        "shape_all": all(x["shape"] == [DEPTH, WIDTH] for x in (a, b, a2, b2)),
        "antithetic_exact_all": all(
            x["antithetic_pair_max_abs"] == 0.0 for x in (a, b, a2, b2)
        ),
        "direction_norm_error_le_2e_6": all(
            x["direction_norm_max_abs_error"] <= 2e-6 for x in (a, b, a2, b2)
        ),
        "analytic_control_means_bounded": all(
            -1.0 <= x["analytic_control_mean_min"]
            and x["analytic_control_mean_max"] <= 1.0
            for x in (a, b, a2, b2)
        ),
        "candidate_bitwise_deterministic": (
            deterministic["a_candidate_bitwise"]
            and deterministic["b_candidate_bitwise"]
        ),
        "baseline_bitwise_deterministic": (
            deterministic["a_baseline_bitwise"]
            and deterministic["b_baseline_bitwise"]
        ),
        "candidate_risk_repeat_abs_eq_0": (
            deterministic["candidate_risk_repeat_abs"] == 0.0
        ),
        "baseline_risk_repeat_abs_eq_0": (
            deterministic["baseline_risk_repeat_abs"] == 0.0
        ),
        "accounting_exact_all": all(
            x["flops"]["exact_reconciliation"] for x in (a, b, a2, b2)
        ),
        "flop_ledgers_deterministic": (
            deterministic["a_flops_equal"] and deterministic["b_flops_equal"]
        ),
        "measured_utilization_le_0_13": util <= UTIL_CAP,
        "precode_upper_utilization_le_0_13": (
            PRECODE_UPPER_FLOPS / BUDGET <= UTIL_CAP
        ),
        "baseline_recompose_le_1e_12": all(
            x["baseline_final_recompose_max_abs"] <= 1e-12
            for x in (a, b, a2, b2)
        ),
        "no_targets_read": True,
    }
    integrity_go = bool(all(integrity.values()))
    local_mechanism_go = bool(integrity_go and material_go)
    decision = (
        "LOCAL_MECHANISM_GO_COMPETITION_GO"
        if local_mechanism_go and competition_go
        else "LOCAL_MECHANISM_GO_COMPETITION_NO_GO"
        if local_mechanism_go
        else "TERMINAL_NO_GO_DROP"
    )

    out = {
        "schema": "arc.whitebox.e109.late_gatepair_sign_cv.v1",
        "experiment": "E109",
        "idempotency_key": "ARC-E109-LATE-GATEPAIR-SIGN-CV-20260919",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories_per_estimator": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seeds": [SEED_A, SEED_B],
        "late_prefix_layer": LATE_LAYER,
        "direction_rows": DIRECTION_ROWS,
        "controls": CONTROLS,
        "budget": BUDGET,
        "utilization_cap": UTIL_CAP,
        "precode_upper_flops": PRECODE_UPPER_FLOPS,
        "precode_upper_utilization": PRECODE_UPPER_FLOPS / BUDGET,
        "candidate_raw_mse_risk_estimate": candidate_risk,
        "baseline_raw_mse_risk_estimate": baseline_risk,
        "candidate_over_baseline": ratio,
        "relative_risk_reduction_fraction": 1.0 - ratio,
        "competition_raw_target_scale": RAW_TARGET,
        "candidate_over_raw_target_scale": candidate_risk / RAW_TARGET,
        "material_ratio_gate": MATERIAL_RATIO,
        "max_measured_utilization": util,
        "a": compact(a),
        "b": compact(b),
        "repeat_a": compact(a2),
        "repeat_b": compact(b2),
        "determinism": deterministic,
        "integrity_gates": integrity,
        "material_explanation_gate": {
            "candidate_over_baseline_le_0_90": ratio <= MATERIAL_RATIO,
            "candidate_risk_lt_baseline": candidate_risk < baseline_risk,
            "pass": material_go,
        },
        "competition_gate": {
            "candidate_risk_le_1_89e_8": candidate_risk <= RAW_TARGET,
            "utilization_le_0_13": util <= UTIL_CAP,
            "pass": competition_go,
        },
        "local_mechanism_go": local_mechanism_go,
        "competition_go": competition_go,
        "decision": decision,
        "scope": {
            "synthetic_production_shape_only": True,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "sweep": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path("e109-exit.txt").write_text(
        "0\n" if local_mechanism_go else "2\n", encoding="utf-8"
    )
    print("E109_LATE_GATEPAIR_SIGN_CV=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
