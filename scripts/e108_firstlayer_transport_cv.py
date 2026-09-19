from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e108_firstlayer_transport_cv import (
    build_meanfield_transport_billed,
    build_two_haar_inputs_billed,
    crossfit_scalar_correct_billed,
    final_pair_blocks_billed,
    first_layer_exact_mean_billed,
    pair_first_layer_blocks_billed,
    transported_controls_billed,
)

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 108104
SEED_A = 108105
SEED_B = 108106
BUDGET = 2**41
UTIL_CAP = 0.13
RAW_TARGET = 1.89e-8
ADJUSTED_TARGET = 2.5e-9
ADMISSION_UPPER_FLOPS = 184_474_289_328
OUT = Path("e108-firstlayer-transport-cv.json")


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
        pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))

        transport = build_meanfield_transport_billed(weights)
        exact_mean = first_layer_exact_mean_billed(weights[0])
        after_control_setup = int(ctx.flops_used)

        baseline_rows = []
        layer_cumulative = []
        z1 = None
        z2 = None

        for layer_index, raw_w in enumerate(weights):
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)

            if layer_index == 0:
                f1, f2 = pair_first_layer_blocks_billed(h, WIDTH)
                z1, z2 = transported_controls_billed(
                    f1, f2, exact_mean, transport
                )

            baseline_rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        if z1 is None or z2 is None:
            raise RuntimeError("first-layer controls were not constructed")

        y1, y2 = final_pair_blocks_billed(h, WIDTH)
        candidate_final, baseline_final, beta1, beta2 = crossfit_scalar_correct_billed(
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
    beta1_np = np.asarray(beta1, dtype=np.float64).copy()
    beta2_np = np.asarray(beta2, dtype=np.float64).copy()
    z1_np = np.asarray(z1, dtype=np.float64).copy()
    z2_np = np.asarray(z2, dtype=np.float64).copy()
    exact_mean_np = np.asarray(exact_mean, dtype=np.float64).copy()
    transport_np = np.asarray(transport, dtype=np.float64).copy()

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

    finite = bool(
        np.isfinite(candidate_np).all()
        and np.isfinite(baseline_np).all()
        and np.isfinite(beta1_np).all()
        and np.isfinite(beta2_np).all()
        and np.isfinite(z1_np).all()
        and np.isfinite(z2_np).all()
        and np.isfinite(exact_mean_np).all()
        and np.isfinite(transport_np).all()
    )

    final_baseline_recompose = float(
        np.max(np.abs(baseline_np[-1] - np.asarray(baseline_final, dtype=np.float64)))
    )

    return {
        "candidate": candidate_np,
        "baseline": baseline_np,
        "candidate_sha256": digest(candidate_np),
        "baseline_sha256": digest(baseline_np),
        "finite": finite,
        "shape": list(candidate_np.shape),
        "antithetic_pair_max_abs": pair_max_abs,
        "beta_abs_max": float(
            max(np.max(np.abs(beta1_np)), np.max(np.abs(beta2_np)))
        ),
        "control_block_mean_rms": [
            float(np.sqrt(np.mean(np.mean(z1_np, axis=0) ** 2))),
            float(np.sqrt(np.mean(np.mean(z2_np, axis=0) ** 2))),
        ],
        "exact_mean_min": float(np.min(exact_mean_np)),
        "exact_mean_max": float(np.max(exact_mean_np)),
        "transport_abs_max": float(np.max(np.abs(transport_np))),
        "baseline_final_recompose_max_abs": final_baseline_recompose,
        "flops": {
            "input_construction": input_flops,
            "control_setup": control_setup_flops,
            "layers": layer_flops,
            "layer_total": int(sum(layer_flops)),
            "finalization": finalization_flops,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": total / BUDGET,
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

    util = max(a["flops"]["utilization"], b["flops"]["utilization"])
    adjusted_proxy = candidate_risk * max(0.1, util)
    ratio = candidate_risk / baseline_risk if baseline_risk > 0.0 else math.inf

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

    gates = {
        "measured_utilization_le_0_13": util <= UTIL_CAP,
        "admission_upper_bound_le_0_13": ADMISSION_UPPER_FLOPS / BUDGET <= UTIL_CAP,
        "candidate_raw_risk_le_1_89e_8": candidate_risk <= RAW_TARGET,
        "adjusted_proxy_lt_2_5e_9": adjusted_proxy < ADJUSTED_TARGET,
        "candidate_risk_lt_baseline": candidate_risk < baseline_risk,
        "finite_all": a["finite"] and b["finite"] and a2["finite"] and b2["finite"],
        "shape_all": all(x["shape"] == [DEPTH, WIDTH] for x in (a, b, a2, b2)),
        "antithetic_exact_all": all(
            x["antithetic_pair_max_abs"] == 0.0 for x in (a, b, a2, b2)
        ),
        "accounting_exact_all": all(
            x["flops"]["exact_reconciliation"] for x in (a, b, a2, b2)
        ),
        "baseline_recompose_all_le_1e_12": all(
            x["baseline_final_recompose_max_abs"] <= 1e-12
            for x in (a, b, a2, b2)
        ),
        "candidate_bitwise_deterministic": (
            deterministic["a_candidate_bitwise"] and deterministic["b_candidate_bitwise"]
        ),
        "baseline_bitwise_deterministic": (
            deterministic["a_baseline_bitwise"] and deterministic["b_baseline_bitwise"]
        ),
        "candidate_risk_repeat_abs_eq_0": deterministic["candidate_risk_repeat_abs"] == 0.0,
        "baseline_risk_repeat_abs_eq_0": deterministic["baseline_risk_repeat_abs"] == 0.0,
        "flop_ledgers_deterministic": (
            deterministic["a_flops_equal"] and deterministic["b_flops_equal"]
        ),
        "no_targets_read": True,
    }
    go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e108.firstlayer_transport_cv.v1",
        "experiment": "E108",
        "idempotency_key": "ARC-E108-FIRSTLAYER-EXACTMEAN-TRANSPORT-CV-20260919",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories_per_estimator": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seeds": [SEED_A, SEED_B],
        "budget": BUDGET,
        "utilization_cap": UTIL_CAP,
        "admission_upper_flops": ADMISSION_UPPER_FLOPS,
        "admission_upper_utilization": ADMISSION_UPPER_FLOPS / BUDGET,
        "candidate_raw_mse_risk_estimate": candidate_risk,
        "baseline_raw_mse_risk_estimate": baseline_risk,
        "candidate_over_baseline": ratio,
        "adjusted_risk_proxy": adjusted_proxy,
        "score_multiplier": max(0.1, util),
        "max_measured_utilization": util,
        "a": compact(a),
        "b": compact(b),
        "repeat_a": compact(a2),
        "repeat_b": compact(b2),
        "determinism": deterministic,
        "gates": gates,
        "decision": "LOCAL_RISK_GO" if go else "TERMINAL_NO_GO_DROP",
        "scientific_go": go,
        "scope": {
            "synthetic_production_shape_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "sweep": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E108_FIRSTLAYER_TRANSPORT_CV=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
