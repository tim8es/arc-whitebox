from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e109_spherical_stein import (
    build_two_haar_inputs_billed,
    crossfit_scalar_control_billed,
    mean_chi_radius,
    spherical_stein_control_billed,
)

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 109104
SEED_A = 109105
SEED_B = 109106
BUDGET = 2**41
RAW_TARGET = 1.89e-8
OUT = Path("e109-spherical-stein-jacobian.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def anchor_direction_billed(weights: list[np.ndarray]):
    radius = mean_chi_radius(WIDTH)
    q0_np = np.full((WIDTH,), 1.0 / math.sqrt(WIDTH), dtype=np.float32)

    def grad_sum(x):
        h = fnp.reshape(x, (1, WIDTH))
        masks = []
        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            z = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            mask = z > fnp.float32(0.0)
            h = fnp.maximum(z, fnp.float32(0.0))
            masks.append(mask)
        grad = fnp.asarray(np.ones((1, WIDTH), dtype=np.float32))
        for raw_w, mask in zip(reversed(weights), reversed(masks)):
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            grad = fnp.where(mask, grad, fnp.float32(0.0))
            grad = fnp.matmul(grad, w)
        return fnp.reshape(grad, (WIDTH,))

    q0 = fnp.asarray(q0_np)
    xpos = fnp.multiply(q0, radius)
    xneg = -xpos
    gp = grad_sum(xpos)
    gn = grad_sum(xneg)
    gq = fnp.multiply(gp - gn, 0.5 * radius)
    norm = fnp.sqrt(fnp.sum(fnp.multiply(gq, gq)))
    return gq / norm


def run_estimator(weights: list[np.ndarray], direction_seed: int) -> dict:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)
        u = anchor_direction_billed(weights)
        after_anchor = int(ctx.flops_used)

        h = build_two_haar_inputs_billed(WIDTH, direction_seed)
        input_np = np.asarray(h, dtype=np.float32).copy()
        after_input = int(ctx.flops_used)

        radius = mean_chi_radius(WIDTH)
        qpos = h[: 2 * WIDTH] / radius
        ucol = fnp.reshape(u, (WIDTH, 1))
        proj = fnp.reshape(fnp.matmul(qpos, ucol), (2 * WIDTH,))
        tangent = u[None, :] - fnp.reshape(proj, (-1, 1)) * qpos
        dpos = fnp.multiply(tangent, radius)
        dh = fnp.concatenate((dpos, -dpos), axis=0)
        after_tangent = int(ctx.flops_used)

        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            wt = fnp.swapaxes(w, 0, 1)
            z = fnp.matmul(h, wt)
            dz = fnp.matmul(dh, wt)
            mask = z > fnp.float32(0.0)
            h = fnp.maximum(z, fnp.float32(0.0))
            dh = fnp.where(mask, dz, fnp.float32(0.0))
        after_layers = int(ctx.flops_used)

        g1 = (h[:WIDTH] + h[2 * WIDTH : 3 * WIDTH]) * 0.5
        g2 = (h[WIDTH : 2 * WIDTH] + h[3 * WIDTH : 4 * WIDTH]) * 0.5
        dg1 = (dh[:WIDTH] + dh[2 * WIDTH : 3 * WIDTH]) * 0.5
        dg2 = (dh[WIDTH : 2 * WIDTH] + dh[3 * WIDTH : 4 * WIDTH]) * 0.5

        q1 = qpos[:WIDTH]
        q2 = qpos[WIDTH : 2 * WIDTH]
        s1 = fnp.reshape(fnp.matmul(q1, ucol), (WIDTH,))
        s2 = fnp.reshape(fnp.matmul(q2, ucol), (WIDTH,))
        c1 = spherical_stein_control_billed(g1, dg1, s1, WIDTH)
        c2 = spherical_stein_control_billed(g2, dg2, s2, WIDTH)
        candidate, baseline, beta1, beta2 = crossfit_scalar_control_billed(
            g1, g2, c1, c2
        )
        after_control = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started

    candidate_np = np.asarray(candidate, dtype=np.float64).copy()
    baseline_np = np.asarray(baseline, dtype=np.float64).copy()
    beta1_np = np.asarray(beta1, dtype=np.float64).copy()
    beta2_np = np.asarray(beta2, dtype=np.float64).copy()
    u_np = np.asarray(u, dtype=np.float64).copy()
    h_np = np.asarray(h, dtype=np.float32)
    c1_np = np.asarray(c1, dtype=np.float64)
    c2_np = np.asarray(c2, dtype=np.float64)

    half = TRAJECTORIES // 2
    pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))

    anchor_flops = after_anchor - start_flops
    input_flops = after_input - after_anchor
    tangent_flops = after_tangent - after_input
    layer_flops = after_layers - after_tangent
    control_flops = after_control - after_layers
    reconciled = anchor_flops + input_flops + tangent_flops + layer_flops + control_flops

    finite = bool(
        np.isfinite(candidate_np).all()
        and np.isfinite(baseline_np).all()
        and np.isfinite(beta1_np).all()
        and np.isfinite(beta2_np).all()
        and np.isfinite(c1_np).all()
        and np.isfinite(c2_np).all()
        and np.isfinite(h_np).all()
    )

    return {
        "candidate": candidate_np,
        "baseline": baseline_np,
        "candidate_sha256": digest(candidate_np),
        "baseline_sha256": digest(baseline_np),
        "finite": finite,
        "anchor_unit_norm_error": abs(float(np.linalg.norm(u_np)) - 1.0),
        "anchor_sha256": digest(u_np),
        "antithetic_pair_max_abs": pair_max_abs,
        "control_block_mean_rms": [
            float(np.sqrt(np.mean(np.mean(c1_np, axis=0) ** 2))),
            float(np.sqrt(np.mean(np.mean(c2_np, axis=0) ** 2))),
        ],
        "beta_max_abs": max(
            float(np.max(np.abs(beta1_np))), float(np.max(np.abs(beta2_np)))
        ),
        "flops": {
            "anchor": anchor_flops,
            "input": input_flops,
            "tangent_setup": tangent_flops,
            "layers_base_plus_jvp": layer_flops,
            "control_crossfit": control_flops,
            "total": total,
            "reconciled": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": total / BUDGET,
        },
        "wall_s": wall_s,
    }


def build_two_haar_inputs_plain(seed: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    radius = mean_chi_radius(WIDTH)
    blocks = []
    for _ in range(2):
        g = rng.standard_normal((WIDTH, WIDTH))
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        blocks.append((q * signs[None, :] * radius).astype(np.float32))
    pos = np.concatenate(blocks, axis=0)
    return np.concatenate((pos, -pos), axis=0)


def risk(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
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

    max_util = max(x["flops"]["utilization"] for x in (a, b, a2, b2))
    ratio = candidate_risk / baseline_risk if baseline_risk > 0.0 else math.inf

    deterministic = {
        "candidate_a_bitwise": bool(np.array_equal(a["candidate"], a2["candidate"])),
        "candidate_b_bitwise": bool(np.array_equal(b["candidate"], b2["candidate"])),
        "baseline_a_bitwise": bool(np.array_equal(a["baseline"], a2["baseline"])),
        "baseline_b_bitwise": bool(np.array_equal(b["baseline"], b2["baseline"])),
        "candidate_risk_repeat_abs": abs(candidate_risk - candidate_risk2),
        "baseline_risk_repeat_abs": abs(baseline_risk - baseline_risk2),
        "anchor_a_same": a["anchor_sha256"] == a2["anchor_sha256"],
        "anchor_b_same": b["anchor_sha256"] == b2["anchor_sha256"],
        "flops_a_same": a["flops"] == a2["flops"],
        "flops_b_same": b["flops"] == b2["flops"],
    }

    gates = {
        "candidate_risk_le_raw_target": candidate_risk <= RAW_TARGET,
        "candidate_risk_lt_baseline": candidate_risk < baseline_risk,
        "utilization_le_0_135": max_util <= 0.135,
        "finite_all": all(x["finite"] for x in (a, b, a2, b2)),
        "antithetic_exact_all": all(x["antithetic_pair_max_abs"] == 0.0 for x in (a, b, a2, b2)),
        "anchor_unit_all": all(x["anchor_unit_norm_error"] <= 2e-6 for x in (a, b, a2, b2)),
        "accounting_exact_all": all(x["flops"]["exact_reconciliation"] for x in (a, b, a2, b2)),
        "candidate_bitwise_replay": deterministic["candidate_a_bitwise"] and deterministic["candidate_b_bitwise"],
        "baseline_bitwise_replay": deterministic["baseline_a_bitwise"] and deterministic["baseline_b_bitwise"],
        "risk_replay_exact": deterministic["candidate_risk_repeat_abs"] == 0.0 and deterministic["baseline_risk_repeat_abs"] == 0.0,
        "flop_replay_exact": deterministic["flops_a_same"] and deterministic["flops_b_same"],
        "no_targets_read": True,
    }
    go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e109.spherical_stein_jacobian_cv.v1",
        "experiment": "E109",
        "idempotency_key": "ARC-E109-SPHERICAL-STEIN-JACOBIAN-CV-20260919",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories_per_estimator": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seeds": [SEED_A, SEED_B],
        "candidate_raw_risk": candidate_risk,
        "baseline_e104_raw_risk": baseline_risk,
        "candidate_over_baseline": ratio,
        "risk_reduction_fraction": 1.0 - ratio,
        "raw_target": RAW_TARGET,
        "candidate_over_raw_target": candidate_risk / RAW_TARGET,
        "max_measured_utilization": max_util,
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
            "rerun": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E109_SPHERICAL_STEIN=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
