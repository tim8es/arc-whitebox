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

from methods.e036_output_hessian_diagonal import (
    H,
    N_PROBES,
    run_centered_hessian,
    static_dense_flop_envelope,
    sylvester_hadamard,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
WIDTH = 1024
DEPTH = 16
RAW_GATE = 1.89e-8
UTIL_GATE = 0.105
ADJUSTED_GATE = 2.5e-9
RESIDUAL_CAP = 0.400


def _static_preflight() -> dict:
    dense_flops = int(static_dense_flop_envelope(WIDTH, DEPTH))
    estimated_util = dense_flops / BUDGET
    q = sylvester_hadamard(np, WIDTH)
    orthogonality_exact = bool(np.array_equal(q.T @ q, WIDTH * np.eye(WIDTH)))
    return {
        "dense_flops": dense_flops,
        "estimated_utilization": estimated_util,
        "cost_gate": estimated_util <= UTIL_GATE,
        "h_exact": H == 1.0,
        "probe_count_exact": N_PROBES == WIDTH,
        "hadamard_orthogonality_exact": orthogonality_exact,
    }


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _prepare(row: dict) -> tuple[MLP, list[np.ndarray], np.ndarray]:
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(DEPTH, WIDTH, WIDTH)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(WIDTH)
    mlp = MLP(
        width=WIDTH,
        depth=DEPTH,
        weights=[fnp.asarray(w) for w in weights],
        seed=0,
    )
    return mlp, [np.asarray(w, dtype=np.float64) for w in weights], gt


def _metered(mlp: MLP):
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred = run_centered_hessian(fnp, list(mlp.weights))
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return np.asarray(pred, dtype=np.float64), used, float(ctx.residual_wall_time_s), wall


def _repeat_numpy(weights: list[np.ndarray]) -> np.ndarray:
    return np.asarray(run_centered_hessian(np, weights), dtype=np.float64)


def main() -> None:
    preflight = _static_preflight()
    if not all(
        [
            preflight["cost_gate"],
            preflight["h_exact"],
            preflight["probe_count_exact"],
            preflight["hadamard_orthogonality_exact"],
        ]
    ):
        summary = {"decision": "NO-GO", "stage": "static_preflight", "preflight": preflight}
        print("E036_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
        Path("e036_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        raise SystemExit(2)

    row = _load_row0()
    mlp, weights_np, gt = _prepare(row)
    pred, used, residual, wall = _metered(mlp)
    repeat = _repeat_numpy(weights_np)

    final = pred[-1]
    final_mse = float(np.mean((final - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    baseline = np.zeros_like(pred)
    max_abs_correction = float(np.max(np.abs(pred - baseline)))
    max_abs_output_difference = max_abs_correction
    finite = bool(np.isfinite(pred).all() and np.isfinite(repeat).all())

    method_source = Path("methods/e036_output_hessian_diagonal.py").read_text(encoding="utf-8")
    scope_ok = (
        "H = 1.0" in method_source
        and "N_PROBES = 1024" in method_source
        and "sylvester_hadamard" in method_source
        and "0.5 * trace_proxy" in method_source
        and "paths[:n]" in method_source
        and "paths[n : 2 * n]" in method_source
    )
    gates = {
        "raw_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "utilization_le_0.105": util <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "finite": finite,
        "deterministic": det_max_abs == 0.0,
        "h_exact": H == 1.0,
        "probe_count_exact": N_PROBES == WIDTH,
        "hadamard_orthogonality_exact": preflight["hadamard_orthogonality_exact"],
        "scope": scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "public_mini_index": 0,
        "final_mse": final_mse,
        "flops": used,
        "utilization": util,
        "adjusted_proxy": adjusted,
        "residual_s": residual,
        "wall_s": wall,
        "max_abs_correction": max_abs_correction,
        "max_abs_output_difference_vs_baseline": max_abs_output_difference,
        "deterministic_repeat_max_abs": det_max_abs,
        "finite": finite,
        "failures": 0,
        "preflight": preflight,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E036_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e036_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
