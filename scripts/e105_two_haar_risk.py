from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e105_two_haar_risk import (
    build_two_haar_inputs_billed,
    mean_chi_radius,
    two_block_statistics,
)

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 104104
DIRECTION_SEED = 104105
BUDGET = 2**41
EXPECTED_E104_PREDICTION_SHA256 = "ae0bfae00c7379673320a3a098c716272c7d9164588bcc73bd59bc7516c017e0"
EXPECTED_FULLY_BILLED_FLOPS = 149_114_550_960
RAW_TARGET = 1.89e-8
ADJUSTED_TARGET = 2.5e-9
OUT = Path("e105-two-haar-risk.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def _hash(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def run_once(weights: list[np.ndarray]) -> dict:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)
        h = build_two_haar_inputs_billed(WIDTH, DIRECTION_SEED)
        after_input = int(ctx.flops_used)

        input_np = np.asarray(h, dtype=np.float32).copy()
        half = TRAJECTORIES // 2
        pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))

        rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w, dtype=fnp.float32)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        prediction = fnp.stack(rows, axis=0)
        after_stack = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started

    pred = np.asarray(prediction, dtype=np.float64).copy()
    final_h = np.asarray(h, dtype=np.float32).copy()
    n = WIDTH

    block1_rows = np.concatenate((final_h[:n], final_h[2 * n : 3 * n]), axis=0)
    block2_rows = np.concatenate((final_h[n : 2 * n], final_h[3 * n : 4 * n]), axis=0)
    block1 = np.mean(block1_rows, axis=0, dtype=np.float64)
    block2 = np.mean(block2_rows, axis=0, dtype=np.float64)
    recomposed, raw_risk = two_block_statistics(block1, block2)
    recompose_max_abs = float(np.max(np.abs(recomposed - pred[-1])))

    input_flops = after_input - start_flops
    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization_flops = after_stack - previous
    reconciled = input_flops + sum(layer_flops) + finalization_flops
    utilization = total / BUDGET
    multiplier = max(0.1, utilization)
    adjusted_proxy = raw_risk * multiplier

    return {
        "prediction": pred,
        "prediction_sha256": _hash(pred),
        "block1_sha256": _hash(block1),
        "block2_sha256": _hash(block2),
        "finite": bool(
            np.isfinite(pred).all()
            and np.isfinite(block1).all()
            and np.isfinite(block2).all()
            and np.isfinite(raw_risk)
        ),
        "shape": list(pred.shape),
        "antithetic_pair_max_abs": pair_max_abs,
        "block_recompose_max_abs": recompose_max_abs,
        "raw_mse_risk_estimate": raw_risk,
        "score_multiplier": multiplier,
        "adjusted_risk_proxy": adjusted_proxy,
        "flops": {
            "input_construction": input_flops,
            "layers": layer_flops,
            "layer_total": int(sum(layer_flops)),
            "finalization": finalization_flops,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": utilization,
        },
        "wall_s": wall_s,
    }


def compact(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "prediction"}


def main() -> None:
    weights = make_weights()
    first = run_once(weights)
    second = run_once(weights)

    prediction_equal = bool(np.array_equal(first["prediction"], second["prediction"]))
    prediction_repeat_max_abs = float(
        np.max(np.abs(first["prediction"] - second["prediction"]))
    )
    risk_repeat_abs = abs(
        first["raw_mse_risk_estimate"] - second["raw_mse_risk_estimate"]
    )
    flops_equal = first["flops"] == second["flops"]

    gates = {
        "raw_mse_risk_le_1_89e_8": first["raw_mse_risk_estimate"] <= RAW_TARGET,
        "adjusted_risk_proxy_lt_2_5e_9": first["adjusted_risk_proxy"] < ADJUSTED_TARGET,
        "utilization_le_0_14": first["flops"]["utilization"] <= 0.14,
        "finite_both": first["finite"] and second["finite"],
        "shape_16x1024_both": first["shape"] == [DEPTH, WIDTH] and second["shape"] == [DEPTH, WIDTH],
        "exact_accounting_both": first["flops"]["exact_reconciliation"] and second["flops"]["exact_reconciliation"],
        "fully_billed_total_exact_both": first["flops"]["total"] == EXPECTED_FULLY_BILLED_FLOPS and second["flops"]["total"] == EXPECTED_FULLY_BILLED_FLOPS,
        "prediction_matches_frozen_e104": first["prediction_sha256"] == EXPECTED_E104_PREDICTION_SHA256 and second["prediction_sha256"] == EXPECTED_E104_PREDICTION_SHA256,
        "prediction_bitwise_deterministic": prediction_equal,
        "prediction_repeat_max_abs_eq_0": prediction_repeat_max_abs == 0.0,
        "risk_repeat_abs_eq_0": risk_repeat_abs == 0.0,
        "flop_ledger_exactly_deterministic": flops_equal,
        "antithetic_exact_both": first["antithetic_pair_max_abs"] == 0.0 and second["antithetic_pair_max_abs"] == 0.0,
        "block_recompose_le_1e_12_both": first["block_recompose_max_abs"] <= 1e-12 and second["block_recompose_max_abs"] <= 1e-12,
        "no_targets_read": True,
    }
    frontier_go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e105.two_haar_risk.v1",
        "experiment": "E105",
        "idempotency_key": "ARC-E105-TWO-HAAR-RISK-20260919",
        "parent": "E104 Haar radial Rao-Blackwellization",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories": TRAJECTORIES,
        "haar_blocks": 2,
        "weight_seed": WEIGHT_SEED,
        "direction_seed": DIRECTION_SEED,
        "budget": BUDGET,
        "mean_chi_radius": mean_chi_radius(WIDTH),
        "raw_target": RAW_TARGET,
        "adjusted_target": ADJUSTED_TARGET,
        "expected_fully_billed_flops": EXPECTED_FULLY_BILLED_FLOPS,
        "first": compact(first),
        "second": compact(second),
        "determinism": {
            "prediction_bitwise_equal": prediction_equal,
            "prediction_repeat_max_abs": prediction_repeat_max_abs,
            "risk_repeat_abs": risk_repeat_abs,
            "flop_ledger_exactly_equal": flops_equal,
        },
        "gates": gates,
        "frontier_go": frontier_go,
        "scientific_go": False,
        "decision": "RISK_CERTIFICATE_GO" if frontier_go else "TERMINAL_NO_GO_DROP",
        "interpretation": "raw_mse_risk_estimate is the target-free unbiased two-block stochastic MSE-risk estimator, not benchmark-target MSE",
        "scope": {
            "production_shape_synthetic_only": True,
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
    print("E105_TWO_HAAR_RISK=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
