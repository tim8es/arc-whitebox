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

from methods.e035_covariance_signed_k3 import run_carrier

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
        pred, max_skew, selected, diag_error = run_carrier(fnp, list(mlp.weights))
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        used,
        float(ctx.residual_wall_time_s),
        wall,
        float(max_skew),
        [int(x) for x in selected],
        float(diag_error),
    )


def _repeat(mlp: MLP):
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ):
        pred, _, selected, diag_error = run_carrier(fnp, list(mlp.weights))
    return (
        np.asarray(pred, dtype=np.float64),
        [int(x) for x in selected],
        float(diag_error),
    )


def main() -> None:
    row = _load_row0()
    mlp, gt = _prepare(row)
    pred, used, residual, wall, max_skew, selected, diag_error = _metered(mlp)
    repeat, selected_repeat, diag_repeat = _repeat(mlp)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(
        np.isfinite(pred).all()
        and np.isfinite(max_skew)
        and np.isfinite(diag_error)
    )

    method_source = Path("methods/e035_covariance_signed_k3.py").read_text(encoding="utf-8")
    scope_ok = (
        "cov = xp.eye(n" in method_source
        and "linear_covariance" in method_source
        and "flops.stats.norm.cdf" in method_source
        and "atoms = xp.zeros((n, 4)" in method_source
        and "push_fifo" in method_source
        and "leverage_birth" in method_source
        and "import numpy" not in method_source
    )
    gates = {
        "raw_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "utilization_le_0.14": util <= UTIL_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "finite": finite,
        "deterministic": (
            det_max_abs == 0.0
            and selected == selected_repeat
            and diag_error == diag_repeat
        ),
        "covariance_diagonal_identity": diag_error == 0.0,
        "scope": scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "final_mse": final_mse,
        "flops": used,
        "utilization": util,
        "adjusted_proxy": adjusted,
        "residual_s": residual,
        "wall_s": wall,
        "max_abs_standardized_skew": max_skew,
        "selected_newborn_indices": selected,
        "selected_repeat": selected_repeat,
        "covariance_diagonal_max_abs_error": diag_error,
        "repeat_covariance_diagonal_max_abs_error": diag_repeat,
        "deterministic_repeat_max_abs": det_max_abs,
        "finite": finite,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E035_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e035_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
