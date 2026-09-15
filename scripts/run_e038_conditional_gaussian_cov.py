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

from methods.e038_conditional_gaussian_cov import (
    COND_EPS,
    GH_WEIGHTS,
    GH_Z,
    run_carrier,
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


def _run_once(mlp: MLP):
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred, diag_error, max_corr = run_carrier(fnp, list(mlp.weights))
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        used,
        float(ctx.residual_wall_time_s),
        wall,
        float(diag_error),
        float(max_corr),
    )


def _repeat_for_determinism(mlp: MLP) -> np.ndarray:
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ):
        pred, _, _ = run_carrier(fnp, list(mlp.weights))
    return np.asarray(pred, dtype=np.float64)


def main() -> None:
    row = _load_row0()
    mlp, gt = _prepare(row)
    pred, used, residual, wall, diag_error, max_corr = _run_once(mlp)
    repeat = _repeat_for_determinism(mlp)

    final = pred[-1]
    final_mse = float(np.mean((final - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(np.isfinite(pred).all() and np.isfinite(repeat).all())

    source = Path("methods/e038_conditional_gaussian_cov.py").read_text(encoding="utf-8")
    scope_ok = (
        len(GH_Z) == 16
        and len(GH_WEIGHTS) == 16
        and COND_EPS == 1.0e-15
        and "conditional_second_moment" in source
        and "0.5 * (second + second.T)" in source
        and "flops.stats.norm.cdf" in source
        and "k3" not in source.lower()
        and "k4" not in source.lower()
        and "source" not in source.lower()
    )

    gates = {
        "raw_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "utilization_le_0.14": util <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "failures_eq_0": True,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "finite": finite,
        "deterministic": det_max_abs == 0.0,
        "covariance_diag_error_le_1e-12": diag_error <= 1.0e-12,
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
        "deterministic_repeat_max_abs": det_max_abs,
        "covariance_diag_max_abs_error": diag_error,
        "max_abs_correlation_before_clipping": max_corr,
        "finite": finite,
        "failures": 0,
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
