from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 104104
DIRECTION_SEED = 104105
BUDGET = 2**41
OUT = Path("e104-production-independent-verify.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def reference_haar_directions_numpy() -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(DIRECTION_SEED))
    blocks: list[np.ndarray] = []
    positive = TRAJECTORIES // 2
    if positive % WIDTH:
        raise RuntimeError("positive sample count must be divisible by width")
    for _ in range(positive // WIDTH):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        blocks.append(q * signs[None, :])
    return np.concatenate(blocks, axis=0)


def build_inputs_billed(seed: int):
    rng = np.random.Generator(np.random.PCG64(seed))
    blocks = []
    positive = TRAJECTORIES // 2
    mu_r = mean_chi_radius(WIDTH)
    for _ in range(positive // WIDTH):
        g = fnp.asarray(rng.standard_normal((WIDTH, WIDTH)).astype(np.float64))
        q, r = fnp.linalg.qr(g)
        diag = fnp.diag(r)
        signs = fnp.where(diag < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        block = fnp.multiply(q, mu_r).astype(fnp.float32)
        blocks.append(block)
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def run_once(weights: list[np.ndarray]) -> dict:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)
        h = build_inputs_billed(DIRECTION_SEED)
        after_input = int(ctx.flops_used)

        input_np = np.asarray(h, dtype=np.float32)
        half = TRAJECTORIES // 2
        pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))
        input_norm_sq = np.sum(
            input_np[:half].astype(np.float64) ** 2, axis=1
        )
        mu_r = mean_chi_radius(WIDTH)
        radius_max_abs = float(np.max(np.abs(np.sqrt(input_norm_sq) - mu_r)))

        rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        prediction = fnp.stack(rows, axis=0)
        after_stack = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started
    pred = np.asarray(prediction, dtype=np.float64).copy()

    input_flops = after_input - start_flops
    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization_flops = after_stack - previous
    reconciled = input_flops + sum(layer_flops) + finalization_flops

    return {
        "prediction": pred,
        "prediction_sha256": hashlib.sha256(pred.tobytes()).hexdigest(),
        "finite": bool(np.isfinite(pred).all()),
        "shape": list(pred.shape),
        "prediction_max_abs": float(np.max(np.abs(pred))),
        "antithetic_pair_max_abs": pair_max_abs,
        "radius_max_abs_vs_mean_chi": radius_max_abs,
        "flops": {
            "start": start_flops,
            "input_construction": input_flops,
            "layers": layer_flops,
            "finalization": finalization_flops,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": total / BUDGET,
        },
        "wall_s": wall_s,
    }


def homogeneity_check(weights: list[np.ndarray], directions: np.ndarray) -> float:
    q = directions[0].astype(np.float32)
    radius = np.float32(1.75)

    def propagate(x: np.ndarray) -> np.ndarray:
        h = x[None, :].astype(np.float32)
        rows = []
        for w in weights:
            h = h @ w.T
            np.maximum(h, np.float32(0.0), out=h)
            rows.append(h[0].astype(np.float64))
        return np.stack(rows, axis=0)

    base = propagate(q)
    scaled = propagate(radius * q)
    denom = max(float(np.max(np.abs(scaled))), 1e-30)
    return float(np.max(np.abs(scaled - float(radius) * base)) / denom)


def main() -> None:
    weights = make_weights()
    reference_directions = reference_haar_directions_numpy()
    hom_rel = homogeneity_check(weights, reference_directions)

    first = run_once(weights)
    second = run_once(weights)

    prediction_equal = bool(np.array_equal(first["prediction"], second["prediction"]))
    flop_ledger_equal = first["flops"] == second["flops"]
    max_abs_repeat = float(np.max(np.abs(first["prediction"] - second["prediction"])))

    gates = {
        "finite_both": first["finite"] and second["finite"],
        "shape_16x1024_both": first["shape"] == [DEPTH, WIDTH] and second["shape"] == [DEPTH, WIDTH],
        "antithetic_exact_both": first["antithetic_pair_max_abs"] == 0.0 and second["antithetic_pair_max_abs"] == 0.0,
        "prediction_bitwise_deterministic": prediction_equal,
        "prediction_repeat_max_abs_eq_0": max_abs_repeat == 0.0,
        "flop_ledger_exactly_deterministic": flop_ledger_equal,
        "accounting_exact_both": first["flops"]["exact_reconciliation"] and second["flops"]["exact_reconciliation"],
        "util_le_0_12_both": first["flops"]["utilization"] <= 0.12 and second["flops"]["utilization"] <= 0.12,
        "util_le_0_135_both": first["flops"]["utilization"] <= 0.135 and second["flops"]["utilization"] <= 0.135,
        "homogeneity_rel_le_2e_6": hom_rel <= 2e-6,
        "no_targets_read": True,
    }

    compact_first = {k: v for k, v in first.items() if k != "prediction"}
    compact_second = {k: v for k, v in second.items() if k != "prediction"}

    out = {
        "schema": "arc.whitebox.e104.production_independent_verify.v1",
        "experiment": "E104",
        "mechanism_changed": False,
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seed": DIRECTION_SEED,
        "budget": BUDGET,
        "mean_chi_radius": mean_chi_radius(WIDTH),
        "homogeneity_relative_error": hom_rel,
        "first": compact_first,
        "second": compact_second,
        "determinism": {
            "prediction_bitwise_equal": prediction_equal,
            "prediction_repeat_max_abs": max_abs_repeat,
            "flop_ledger_exactly_equal": flop_ledger_equal,
            "prediction_sha256_equal": first["prediction_sha256"] == second["prediction_sha256"],
        },
        "gates": gates,
        "verified": bool(all(gates.values())),
        "scientific_go": False,
        "raw_mse_evaluated": False,
        "scope": {
            "production_shape_synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_PRODUCTION_INDEPENDENT_VERIFY=" + json.dumps(out, sort_keys=True), flush=True)
    if not out["verified"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
