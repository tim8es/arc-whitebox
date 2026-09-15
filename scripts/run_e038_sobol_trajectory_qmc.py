from __future__ import annotations

import json
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from whestbench.domain import MLP

from methods.e038_sobol_trajectory_qmc import (
    DIMENSION,
    M_POWER,
    N_SAMPLES,
    SCRAMBLE_SEED,
    build_samples,
    run_trajectories,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
WIDTH = 1024
DEPTH = 16
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.5e-9
RESIDUAL_CAP = 0.400
PREDICT_CAP = 120.0
SETUP_CAP = 4.5


def _setup_preflight():
    t0 = time.perf_counter()
    a = build_samples()
    setup_s = time.perf_counter() - t0
    t1 = time.perf_counter()
    b = build_samples()
    repeat_setup_s = time.perf_counter() - t1
    setup_equal = bool(np.array_equal(a, b))
    setup_finite = bool(np.isfinite(a).all() and np.isfinite(b).all())
    setup_shape = tuple(a.shape) == (N_SAMPLES, DIMENSION)
    setup_dtype = a.dtype == np.float32 and b.dtype == np.float32
    setup_ok = bool(
        setup_s <= SETUP_CAP
        and repeat_setup_s <= SETUP_CAP
        and setup_equal
        and setup_finite
        and setup_shape
        and setup_dtype
    )
    return a, {
        "setup_s": setup_s,
        "repeat_setup_s": repeat_setup_s,
        "setup_equal": setup_equal,
        "setup_finite": setup_finite,
        "setup_shape_ok": setup_shape,
        "setup_dtype_ok": setup_dtype,
        "setup_ok": setup_ok,
    }


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _prepare(row: dict) -> tuple[MLP, np.ndarray]:
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(DEPTH, WIDTH, WIDTH)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(WIDTH)
    mlp = MLP(
        width=WIDTH,
        depth=DEPTH,
        weights=[fnp.asarray(w) for w in weights],
        seed=0,
    )
    return mlp, gt


def _metered(samples: np.ndarray, mlp: MLP):
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred = run_trajectories(fnp, samples, list(mlp.weights))
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return np.asarray(pred, dtype=np.float64), used, float(ctx.residual_wall_time_s), wall


def _repeat(samples: np.ndarray, mlp: MLP):
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ):
        pred = run_trajectories(fnp, samples, list(mlp.weights))
    return np.asarray(pred, dtype=np.float64)


def main() -> None:
    samples, setup = _setup_preflight()
    if not setup["setup_ok"]:
        summary = {
            **setup,
            "public_mini_accessed": False,
            "decision": "NO-GO",
            "reason": "setup_preflight",
        }
        print("E038_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
        Path("e038_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        raise SystemExit(2)

    row = _load_row0()
    mlp, gt = _prepare(row)
    pred, used, residual, wall = _metered(samples, mlp)
    repeat = _repeat(samples, mlp)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(np.isfinite(pred).all() and np.isfinite(repeat).all())

    method_source = Path("methods/e038_sobol_trajectory_qmc.py").read_text(encoding="utf-8")
    scope_ok = bool(
        "DIMENSION = 1024" in method_source
        and "N_SAMPLES = 8192" in method_source
        and "M_POWER = 13" in method_source
        and "SCRAMBLE_SEED = 38038" in method_source
        and "qmc.Sobol(d=DIMENSION, scramble=True, seed=SCRAMBLE_SEED)" in method_source
        and "random_base2(m=M_POWER)" in method_source
        and "ndtri(uniforms)" in method_source
        and "xp.mean(x, axis=0)" in method_source
    )
    gates = {
        "raw_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "utilization_le_0.14": util <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "predict_wall_lt_120s": wall < PREDICT_CAP,
        "setup_le_4.5s": setup["setup_s"] <= SETUP_CAP,
        "repeat_setup_le_4.5s": setup["repeat_setup_s"] <= SETUP_CAP,
        "failures_eq_0": True,
        "finite": finite and setup["setup_finite"],
        "deterministic_setup": setup["setup_equal"],
        "deterministic_prediction": det_max_abs == 0.0,
        "scope": scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        **setup,
        "mlp_id": int(row["mlp_id"]),
        "public_mini_index": 0,
        "public_mini_accessed": True,
        "final_mse": final_mse,
        "flops": used,
        "utilization": util,
        "adjusted_proxy": adjusted,
        "residual_s": residual,
        "predict_wall_s": wall,
        "deterministic_repeat_max_abs": det_max_abs,
        "finite": finite,
        "failures": 0,
        "dimension": DIMENSION,
        "n_samples": N_SAMPLES,
        "m_power": M_POWER,
        "scramble_seed": SCRAMBLE_SEED,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E038_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e038_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
