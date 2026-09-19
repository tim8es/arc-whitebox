from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 3968
PAIRS = TRAJECTORIES // 2
K = 8
PAIRS_PER_GROUP = PAIRS // K
HALF_GROUP = PAIRS_PER_GROUP // 2
WEIGHT_SEED = 109104
SEED_A = 109105
SEED_B = 109106
BUDGET = 2**41
UTIL_CAP = 0.13
ADMISSION_UPPER_FLOPS = 271_548_019_200
RAW_TARGET_SCALE = 1.89e-8
OUT = Path("e109-deep-stein-jvp-cv.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def build_deep_directions_billed(weights: list[np.ndarray]):
    g0 = np.zeros((WIDTH, K), dtype=np.float32)
    group = WIDTH // K
    amp = np.float32(1.0 / math.sqrt(group))
    for k in range(K):
        g0[k * group : (k + 1) * group, k] = amp
    g = fnp.asarray(g0, dtype=fnp.float32)
    for raw_w in reversed(weights):
        w = fnp.asarray(raw_w, dtype=fnp.float32)
        g = fnp.multiply(fnp.matmul(w, g), fnp.float32(0.5))
    norms = fnp.sqrt(fnp.sum(g * g, axis=0, dtype=fnp.float64))
    v = fnp.swapaxes(g / norms[None, :], 0, 1).astype(fnp.float32)
    return v, norms


def build_inputs_billed(seed: int):
    rng = fnp.random.default_rng(seed)
    pos = rng.standard_normal((PAIRS, WIDTH)).astype(fnp.float32)
    return fnp.concatenate((pos, -pos), axis=0)


def build_tangent_rows_billed(v):
    blocks = []
    for k in range(K):
        ones = fnp.ones((PAIRS_PER_GROUP, 1), dtype=fnp.float32)
        blocks.append(ones * v[k : k + 1, :])
    pos_t = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos_t, pos_t), axis=0)


def fit_beta_billed(y, c):
    ym = fnp.mean(y, axis=0, dtype=fnp.float64)
    cm = fnp.mean(c, axis=0, dtype=fnp.float64)
    yc = fnp.asarray(y, dtype=fnp.float64) - ym
    cc = fnp.asarray(c, dtype=fnp.float64) - cm
    num = fnp.mean(yc * cc, axis=0, dtype=fnp.float64)
    den = fnp.mean(cc * cc, axis=0, dtype=fnp.float64)
    return num / den, ym, cm, den


def crossfit_group_billed(y, c):
    ya, yb = y[:HALF_GROUP], y[HALF_GROUP:]
    ca, cb = c[:HALF_GROUP], c[HALF_GROUP:]
    beta_a, mean_ya, mean_ca, den_a = fit_beta_billed(ya, ca)
    beta_b, mean_yb, mean_cb, den_b = fit_beta_billed(yb, cb)
    left = mean_ya - beta_b * mean_ca
    right = mean_yb - beta_a * mean_cb
    return fnp.float64(0.5) * (left + right), beta_a, beta_b, den_a, den_b


def run_estimator(weights: list[np.ndarray], seed: int) -> dict:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)

        h = build_inputs_billed(seed)
        after_baseline_input = int(ctx.flops_used)
        input_np = np.asarray(h, dtype=np.float32).copy()

        v, direction_norms = build_deep_directions_billed(weights)
        t = build_tangent_rows_billed(v)
        projection = fnp.sum(
            fnp.asarray(h, dtype=fnp.float64) * fnp.asarray(t, dtype=fnp.float64),
            axis=1,
            dtype=fnp.float64,
        )
        after_control_setup = int(ctx.flops_used)

        baseline_rows = []
        forward_layer_flops = []
        tangent_layer_flops = []

        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            before_forward = int(ctx.flops_used)
            pre = fnp.matmul(h, w)
            h = fnp.maximum(pre, fnp.float32(0.0))
            baseline_rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            after_forward = int(ctx.flops_used)

            tpre = fnp.matmul(t, w)
            gate = pre > fnp.float32(0.0)
            t = tpre * gate
            after_tangent = int(ctx.flops_used)

            forward_layer_flops.append(after_forward - before_forward)
            tangent_layer_flops.append(after_tangent - after_forward)

        baseline_prediction = fnp.stack(baseline_rows, axis=0)
        after_baseline_stack = int(ctx.flops_used)

        y_pair = fnp.float32(0.5) * (h[:PAIRS] + h[PAIRS:])
        control = fnp.asarray(t, dtype=fnp.float64) - projection[:, None] * fnp.asarray(
            h, dtype=fnp.float64
        )
        c_pair = fnp.float64(0.5) * (control[:PAIRS] + control[PAIRS:])

        group_candidates = []
        beta_abs_parts = []
        den_parts = []
        for k in range(K):
            lo = k * PAIRS_PER_GROUP
            hi = (k + 1) * PAIRS_PER_GROUP
            cand, beta_a, beta_b, den_a, den_b = crossfit_group_billed(
                y_pair[lo:hi], c_pair[lo:hi]
            )
            group_candidates.append(cand)
            beta_abs_parts.extend((fnp.abs(beta_a), fnp.abs(beta_b)))
            den_parts.extend((den_a, den_b))

        candidate_final = fnp.mean(
            fnp.stack(group_candidates, axis=0), axis=0, dtype=fnp.float64
        )
        candidate_prediction = fnp.stack(
            baseline_rows[:-1] + [candidate_final], axis=0
        )
        beta_abs = fnp.concatenate(beta_abs_parts, axis=0)
        den_all = fnp.concatenate(den_parts, axis=0)
        control_mean = fnp.mean(c_pair, axis=0, dtype=fnp.float64)
        after_candidate = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started

    baseline_np = np.asarray(baseline_prediction, dtype=np.float64).copy()
    candidate_np = np.asarray(candidate_prediction, dtype=np.float64).copy()
    v_np = np.asarray(v, dtype=np.float64).copy()
    norm_np = np.asarray(direction_norms, dtype=np.float64).copy()
    beta_abs_np = np.asarray(beta_abs, dtype=np.float64).copy()
    den_np = np.asarray(den_all, dtype=np.float64).copy()
    control_mean_np = np.asarray(control_mean, dtype=np.float64).copy()

    half = PAIRS
    pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))

    baseline_input_flops = after_baseline_input - start_flops
    control_setup_flops = after_control_setup - after_baseline_input
    baseline_stack_flops = after_baseline_stack - (
        after_control_setup + sum(forward_layer_flops) + sum(tangent_layer_flops)
    )
    candidate_finalization_flops = after_candidate - after_baseline_stack

    reconciled = (
        baseline_input_flops
        + control_setup_flops
        + sum(forward_layer_flops)
        + sum(tangent_layer_flops)
        + baseline_stack_flops
        + candidate_finalization_flops
    )

    baseline_standalone_flops = (
        baseline_input_flops + sum(forward_layer_flops) + baseline_stack_flops
    )

    finite = bool(
        np.isfinite(baseline_np).all()
        and np.isfinite(candidate_np).all()
        and np.isfinite(v_np).all()
        and np.isfinite(norm_np).all()
        and np.isfinite(beta_abs_np).all()
        and np.isfinite(den_np).all()
        and np.isfinite(control_mean_np).all()
    )

    return {
        "baseline": baseline_np,
        "candidate": candidate_np,
        "baseline_sha256": digest(baseline_np),
        "candidate_sha256": digest(candidate_np),
        "shape": list(candidate_np.shape),
        "finite": finite,
        "antithetic_pair_max_abs": pair_max_abs,
        "direction_norm_min": float(np.min(norm_np)),
        "direction_norm_max": float(np.max(norm_np)),
        "direction_abs_max": float(np.max(np.abs(v_np))),
        "beta_abs_max": float(np.max(beta_abs_np)),
        "control_den_min": float(np.min(den_np)),
        "control_mean_rms": float(np.sqrt(np.mean(control_mean_np * control_mean_np))),
        "flops": {
            "baseline_input": baseline_input_flops,
            "control_setup": control_setup_flops,
            "forward_layers": forward_layer_flops,
            "forward_layer_total": int(sum(forward_layer_flops)),
            "tangent_layers": tangent_layer_flops,
            "tangent_layer_total": int(sum(tangent_layer_flops)),
            "baseline_stack": baseline_stack_flops,
            "candidate_finalization": candidate_finalization_flops,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": total / BUDGET,
            "baseline_standalone_flops": baseline_standalone_flops,
            "baseline_standalone_utilization": baseline_standalone_flops / BUDGET,
        },
        "wall_s": wall_s,
    }


def risk(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a[-1], dtype=np.float64) - np.asarray(b[-1], dtype=np.float64)
    return float(np.mean(d * d) / 2.0)


def compact(x: dict) -> dict:
    return {k: v for k, v in x.items() if k not in ("baseline", "candidate")}


def main() -> None:
    if PAIRS % K or PAIRS_PER_GROUP % 2:
        raise RuntimeError("frozen pair/group geometry is invalid")

    weights = make_weights()

    a = run_estimator(weights, SEED_A)
    b = run_estimator(weights, SEED_B)
    candidate_risk = risk(a["candidate"], b["candidate"])
    baseline_risk = risk(a["baseline"], b["baseline"])

    a2 = run_estimator(weights, SEED_A)
    b2 = run_estimator(weights, SEED_B)
    candidate_risk2 = risk(a2["candidate"], b2["candidate"])
    baseline_risk2 = risk(a2["baseline"], b2["baseline"])

    candidate_util = max(a["flops"]["utilization"], b["flops"]["utilization"])
    baseline_util = max(
        a["flops"]["baseline_standalone_utilization"],
        b["flops"]["baseline_standalone_utilization"],
    )
    ratio = candidate_risk / baseline_risk if baseline_risk > 0.0 else math.inf
    candidate_adjusted = candidate_risk * max(0.1, candidate_util)
    baseline_adjusted = baseline_risk * max(0.1, baseline_util)

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

    runs = (a, b, a2, b2)
    gates = {
        "admission_upper_util_le_0_13": ADMISSION_UPPER_FLOPS / BUDGET <= UTIL_CAP,
        "measured_util_le_0_13": candidate_util <= UTIL_CAP,
        "exact_accounting_all": all(x["flops"]["exact_reconciliation"] for x in runs),
        "finite_all": all(x["finite"] for x in runs),
        "shape_all_16x1024": all(x["shape"] == [DEPTH, WIDTH] for x in runs),
        "antithetic_exact_all": all(x["antithetic_pair_max_abs"] == 0.0 for x in runs),
        "direction_norms_positive_all": all(x["direction_norm_min"] > 0.0 for x in runs),
        "control_denominators_positive_all": all(x["control_den_min"] > 0.0 for x in runs),
        "candidate_bitwise_deterministic": (
            deterministic["a_candidate_bitwise"] and deterministic["b_candidate_bitwise"]
        ),
        "baseline_bitwise_deterministic": (
            deterministic["a_baseline_bitwise"] and deterministic["b_baseline_bitwise"]
        ),
        "risk_replay_exact": (
            deterministic["candidate_risk_repeat_abs"] == 0.0
            and deterministic["baseline_risk_repeat_abs"] == 0.0
        ),
        "flop_ledgers_deterministic": (
            deterministic["a_flops_equal"] and deterministic["b_flops_equal"]
        ),
        "candidate_risk_lt_baseline": candidate_risk < baseline_risk,
        "candidate_over_baseline_le_0_80": ratio <= 0.80,
        "adjusted_proxy_improves_baseline": candidate_adjusted < baseline_adjusted,
        "no_targets_read": True,
    }
    scientific_go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e109.deep_stein_jvp_cv.v1",
        "experiment": "E109",
        "idempotency_key": "ARC-E109-DEEP-STEIN-JVP-CV-20260919",
        "mechanism": "deep Gaussian-Stein final-layer directional-JVP control variate",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories_per_estimator": TRAJECTORIES,
        "antithetic_pairs": PAIRS,
        "control_directions": K,
        "pairs_per_direction": PAIRS_PER_GROUP,
        "weight_seed": WEIGHT_SEED,
        "estimator_seeds": [SEED_A, SEED_B],
        "budget": BUDGET,
        "utilization_cap": UTIL_CAP,
        "admission_upper_flops": ADMISSION_UPPER_FLOPS,
        "admission_upper_utilization": ADMISSION_UPPER_FLOPS / BUDGET,
        "candidate_raw_mse_risk_estimate": candidate_risk,
        "baseline_raw_mse_risk_estimate": baseline_risk,
        "candidate_over_baseline": ratio,
        "relative_risk_reduction_fraction": 1.0 - ratio,
        "candidate_adjusted_risk_proxy": candidate_adjusted,
        "baseline_adjusted_risk_proxy": baseline_adjusted,
        "candidate_score_multiplier": max(0.1, candidate_util),
        "baseline_score_multiplier": max(0.1, baseline_util),
        "competition_raw_target_scale": RAW_TARGET_SCALE,
        "candidate_over_raw_target_scale": candidate_risk / RAW_TARGET_SCALE,
        "max_candidate_utilization": candidate_util,
        "baseline_utilization": baseline_util,
        "a": compact(a),
        "b": compact(b),
        "repeat_a": compact(a2),
        "repeat_b": compact(b2),
        "determinism": deterministic,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "TARGET_FREE_DEEP_NONLINEAR_RISK_GO"
            if scientific_go
            else "TERMINAL_NO_GO_DROP"
        ),
        "scope": {
            "synthetic_production_shape_only": True,
            "iid_gaussian_antithetic": True,
            "haar_or_orthogonal_sampling": False,
            "rao_blackwell": False,
            "qmc_or_cubature": False,
            "latent_mixture": False,
            "first_layer_exact_mean": False,
            "public": False,
            "public_mini": False,
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
    print("E109_DEEP_STEIN_JVP_CV=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
