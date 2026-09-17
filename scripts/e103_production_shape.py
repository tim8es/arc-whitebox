from __future__ import annotations

import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import numpy as np
from whestbench import SetupContext

from methods.e103_orthogonal_antithetic import (
    Estimator,
    PRODUCTION_SAMPLES,
    orthogonal_antithetic_numpy,
)

WIDTH = 1024
DEPTH = 16
WEIGHT_SEED = 103103
SAMPLE_SEED = 103104
BUDGET = 2**41
ANALYTIC_E100_FLOPS = 140_319_042_219
OUT = Path("e103-production-shape.json")


def make_mlp() -> SimpleNamespace:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    weights = [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]
    return SimpleNamespace(
        width=WIDTH,
        depth=DEPTH,
        weights=weights,
        seed=WEIGHT_SEED,
    )


def main() -> None:
    mlp = make_mlp()
    estimator = Estimator()
    estimator.setup(
        SetupContext(
            width=WIDTH,
            depth=DEPTH,
            flop_budget=BUDGET,
            api_version="1",
            seed=SAMPLE_SEED,
        )
    )

    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        prediction = estimator.predict(mlp, BUDGET)
    wall_s = time.perf_counter() - started
    estimator.teardown()

    pred = np.asarray(prediction, dtype=np.float64)
    measured_flops = int(ctx.flops_used)
    utilization = measured_flops / BUDGET

    # Target-free marginal diagnostic using the exact frozen input generator.
    inputs = orthogonal_antithetic_numpy(WIDTH, PRODUCTION_SAMPLES, SAMPLE_SEED)
    half = PRODUCTION_SAMPLES // 2
    pair_max_abs = float(np.max(np.abs(inputs[:half] + inputs[half:])))
    flat = inputs.astype(np.float64, copy=False).reshape(-1)
    variance = float(np.mean(flat * flat))
    fourth = float(np.mean(flat ** 4))

    gates = {
        "shape_1024x16": pred.shape == (DEPTH, WIDTH),
        "trajectories_4096": PRODUCTION_SAMPLES == 4096,
        "finite_output": bool(np.isfinite(pred).all()),
        "antithetic_pair_exact": pair_max_abs == 0.0,
        "measured_util_le_0_12": utilization <= 0.12,
        "measured_util_le_0_135": utilization <= 0.135,
        "input_variance_in_0_95_1_05": 0.95 <= variance <= 1.05,
        "input_fourth_in_2_7_3_3": 2.7 <= fourth <= 3.3,
        "no_targets_read": True,
    }
    decision = (
        "PRODUCTION_SHAPE_IMPLEMENTATION_GO_ONLY"
        if all(gates.values())
        else "TERMINAL_E103_NO_GO"
    )

    result = {
        "schema": "arc.whitebox.e103.production_shape.v1",
        "experiment": "E103",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories": PRODUCTION_SAMPLES,
        "weight_seed": WEIGHT_SEED,
        "sample_seed": SAMPLE_SEED,
        "budget": BUDGET,
        "prediction_shape": list(pred.shape),
        "finite": bool(np.isfinite(pred).all()),
        "prediction_max_abs": float(np.max(np.abs(pred))),
        "measured_flops": measured_flops,
        "measured_utilization": utilization,
        "analytic_e100_flops": ANALYTIC_E100_FLOPS,
        "analytic_e100_utilization": ANALYTIC_E100_FLOPS / BUDGET,
        "measured_minus_analytic_flops": measured_flops - ANALYTIC_E100_FLOPS,
        "wall_s": wall_s,
        "input_marginal": {
            "antithetic_pair_max_abs": pair_max_abs,
            "variance_about_zero": variance,
            "fourth_moment": fourth,
        },
        "gates": gates,
        "decision": decision,
        "scientific_go": False,
        "raw_mse_evaluated": False,
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E103_PRODUCTION_SHAPE=" + json.dumps(result, sort_keys=True), flush=True)
    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
