from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e106_crossfit_quartic import (
    build_two_haar_inputs_billed,
    crossfit_correct_billed,
    mean_chi_radius,
    quartic_features_billed,
)

WIDTH = 1024
DEPTH = 16
FEATURES = 256
TRAJECTORIES = 4096
WEIGHT_SEED = 104104
SEED_A = 106105
SEED_B = 106106
BUDGET = 2**41
RAW_TARGET = 1.89e-8
ADJUSTED_TARGET = 2.5e-9
OUT = Path("e106-crossfit-quartic.json")


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

        u = fnp.asarray(weights[0][:FEATURES], dtype=fnp.float32)
        norms = fnp.sqrt(fnp.sum(fnp.multiply(u, u), axis=1))
        u = u / fnp.reshape(norms, (-1, 1))

        radius = mean_chi_radius(WIDTH)
        q = h[: 2 * WIDTH] / radius
        z = quartic_features_billed(q, u)
        z1 = z[:WIDTH]
        z2 = z[WIDTH : 2 * WIDTH]
        after_features = int(ctx.flops_used)

        candidate_rows = []
        baseline_rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)

            g1 = (h[:WIDTH] + h[2 * WIDTH : 3 * WIDTH]) * 0.5
            g2 = (h[WIDTH : 2 * WIDTH] + h[3 * WIDTH : 4 * WIDTH]) * 0.5
            candidate, baseline = crossfit_correct_billed(g1, g2, z1, z2)
            candidate_rows.append(candidate)
            baseline_rows.append(baseline)
            layer_cumulative.append(int(ctx.flops_used))

        candidate_prediction = fnp.stack(candidate_rows, axis=0)
        baseline_prediction = fnp.stack(baseline_rows, axis=0)
        after_stack = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started
    candidate_np = np.asarray(candidate_prediction, dtype=np.float64).copy()
    baseline_np = np.asarray(baseline_prediction, dtype=np.float64).copy()
    u_np = np.asarray(u, dtype=np.float64).copy()

    input_flops = after_input - start_flops
    feature_flops = after_features - after_input
    layer_flops = []
    previous = after_features
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization_flops = after_stack - previous
    reconciled = input_flops + feature_flops + sum(layer_flops) + finalization_flops

    return {
        "candidate": candidate_np,
        "baseline": baseline_np,
        "candidate_sha256": digest(candidate_np),
        "baseline_sha256": digest(baseline_np),
        "finite": bool(np.isfinite(candidate_np).all() and np.isfinite(baseline_np).all()),
        "shape": list(candidate_np.shape),
        "antithetic_pair_max_abs": pair_max_abs,
        "feature_direction_norm_max_abs_error": float(
            np.max(np.abs(np.linalg.norm(u_np, axis=1) - 1.0))
        ),
        "flops": {
            "input_construction": input_flops,
            "feature_setup": feature_flops,
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
        "candidate_raw_risk_le_1_89e_8": candidate_risk <= RAW_TARGET,
        "adjusted_proxy_lt_2_5e_9": adjusted_proxy < ADJUSTED_TARGET,
        "utilization_le_0_14": util <= 0.14,
        "candidate_risk_lt_baseline": candidate_risk < baseline_risk,
        "finite_all": a["finite"] and b["finite"] and a2["finite"] and b2["finite"],
        "shape_all": all(x["shape"] == [DEPTH, WIDTH] for x in (a, b, a2, b2)),
        "antithetic_exact_all": all(x["antithetic_pair_max_abs"] == 0.0 for x in (a, b, a2, b2)),
        "accounting_exact_all": all(x["flops"]["exact_reconciliation"] for x in (a, b, a2, b2)),
        "feature_directions_unit_all": all(x["feature_direction_norm_max_abs_error"] <= 2e-6 for x in (a, b, a2, b2)),
        "candidate_bitwise_deterministic": deterministic["a_candidate_bitwise"] and deterministic["b_candidate_bitwise"],
        "baseline_bitwise_deterministic": deterministic["a_baseline_bitwise"] and deterministic["b_baseline_bitwise"],
        "candidate_risk_repeat_abs_eq_0": deterministic["candidate_risk_repeat_abs"] == 0.0,
        "baseline_risk_repeat_abs_eq_0": deterministic["baseline_risk_repeat_abs"] == 0.0,
        "flop_ledgers_deterministic": deterministic["a_flops_equal"] and deterministic["b_flops_equal"],
        "no_targets_read": True,
    }
    go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e106.crossfit_quartic.v1",
        "experiment": "E106",
        "idempotency_key": "ARC-E106-CROSSFIT-QUARTIC-HAAR-CV-20260919",
        "width": WIDTH,
        "depth": DEPTH,
        "features": FEATURES,
        "trajectories_per_estimator": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seeds": [SEED_A, SEED_B],
        "budget": BUDGET,
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
        "scientific_go": False,
        "scope": {
            "synthetic_production_shape_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "canonical_mutated": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E106_CROSSFIT_QUARTIC=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
