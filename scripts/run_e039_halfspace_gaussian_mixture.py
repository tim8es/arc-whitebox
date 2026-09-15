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

from methods.e039_halfspace_gaussian_mixture import run_halfspace_mixture

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


def _metered(mlp: MLP):
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred, diagnostics = run_halfspace_mixture(fnp, list(mlp.weights))
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        diagnostics,
        used,
        float(ctx.residual_wall_time_s),
        wall,
    )


def _repeat_numpy(row: dict):
    weights = np.asarray(row["weights"], dtype=np.float64).reshape(DEPTH, WIDTH, WIDTH)
    pred, diagnostics = run_halfspace_mixture(np, [w for w in weights])
    return np.asarray(pred, dtype=np.float64), diagnostics


def main() -> None:
    row = _load_row0()
    mlp, gt = _prepare(row)
    pred, diagnostics, used, residual, wall = _metered(mlp)
    repeat, repeat_diag = _repeat_numpy(row)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(np.isfinite(pred).all())

    method_source = Path("methods/e039_halfspace_gaussian_mixture.py").read_text(encoding="utf-8")
    scope_ok = (
        "SQRT_2_OVER_PI" in method_source
        and "0.5 * cov_plus + 0.5 * cov_minus" in method_source
        and "0.5 * m_plus + 0.5 * m_minus" in method_source
        and "linear_covariance" in method_source
        and "K3" not in method_source
        and "K4" not in method_source
    )

    init_mean_error = float(diagnostics["init_mean_error"])
    init_cov_error = float(diagnostics["init_cov_error"])
    max_diag_error = float(diagnostics["max_diag_error"])
    component_count = int(diagnostics["component_count"])
    weights = list(diagnostics["weights"])
    repeat_same_meta = (
        repeat_diag["component_count"] == diagnostics["component_count"]
        and repeat_diag["weights"] == diagnostics["weights"]
    )

    gates = {
        "raw_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "utilization_le_0.14": util <= UTIL_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "finite": finite,
        "deterministic": det_max_abs == 0.0 and repeat_same_meta,
        "init_mean_error_le_1e-14": init_mean_error <= 1e-14,
        "init_cov_error_le_1e-12": init_cov_error <= 1e-12,
        "covariance_diagonal_identity_le_1e-12": max_diag_error <= 1e-12,
        "component_count_eq_2": component_count == 2,
        "weights_eq_half": weights == [0.5, 0.5],
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
        "failures": 0,
        "residual_s": residual,
        "wall_s": wall,
        "init_mean_error": init_mean_error,
        "init_cov_error": init_cov_error,
        "covariance_diagonal_max_abs_error": max_diag_error,
        "component_count": component_count,
        "weights": weights,
        "deterministic_repeat_max_abs": det_max_abs,
        "finite": finite,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E039_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e039_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
