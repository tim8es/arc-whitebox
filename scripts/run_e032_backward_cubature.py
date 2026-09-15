from __future__ import annotations

import json
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq
from whestbench.domain import MLP

from methods.e032_backward_cubature import (
    Estimator,
    apply_reflections,
    backward_probes,
    build_base_points,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
WIDTH = 1024
DEPTH = 16
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.646e-9
RESIDUAL_CAP = 0.400
ENDPOINTS = 8192
PAIRS = 4096


class _Ctx:
    seed = 0


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _prepare(row: dict):
    weights_np = np.asarray(row["weights"], dtype=np.float32).reshape(DEPTH, WIDTH, WIDTH)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(WIDTH)
    mlp = MLP(
        width=WIDTH,
        depth=DEPTH,
        weights=[fnp.asarray(w) for w in weights_np],
        seed=0,
    )
    return weights_np, mlp, gt


def _predict_metered(mlp: MLP):
    est = Estimator()
    est.setup(_Ctx())
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred = est.predict(mlp, BUDGET)
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        used,
        float(ctx.residual_wall_time_s),
        wall,
    )


def _predict_repeat(mlp: MLP):
    est = Estimator()
    est.setup(_Ctx())
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ):
        pred = est.predict(mlp, BUDGET)
    return np.asarray(pred, dtype=np.float64)


def main() -> None:
    row = _load_row0()
    weights_np, mlp, gt = _prepare(row)

    pred, used, residual, wall = _predict_metered(mlp)
    repeat = _predict_repeat(mlp)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(np.isfinite(pred).all())

    base = build_base_points(np, WIDTH)
    probes = backward_probes(np, list(weights_np), n_probes=8)
    rotated = apply_reflections(np, base, probes)
    norm_max_abs = float(np.max(np.abs(np.sum(rotated * rotated, axis=1) - 1.0)))
    endpoints = np.concatenate([rotated, -rotated], axis=0)
    antipode_max_abs = float(np.max(np.abs(endpoints[:PAIRS] + endpoints[PAIRS:])))

    method_source = Path("methods/e032_backward_cubature.py").read_text(encoding="utf-8")
    scope_ok = (
        "import numpy" not in method_source
        and "n_probes=8" in method_source
        and "_MASK_SEEDS" in method_source
        and ENDPOINTS == 8192
        and PAIRS == 4096
    )

    gates = {
        "final_mse_le_1.89e-08": final_mse <= RAW_GATE,
        "util_le_0.14": util <= UTIL_GATE,
        "adjusted_le_2.646e-09": adjusted <= ADJUSTED_GATE,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "finite": finite,
        "deterministic": det_max_abs == 0.0,
        "support_exact": endpoints.shape == (ENDPOINTS, WIDTH),
        "antipodal": antipode_max_abs == 0.0,
        "unit_norm": norm_max_abs <= 1e-10,
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
        "det_max_abs": det_max_abs,
        "support_pairs": PAIRS,
        "support_endpoints": ENDPOINTS,
        "endpoint_norm_max_abs": norm_max_abs,
        "antipode_max_abs": antipode_max_abs,
        "finite": finite,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E032_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e032_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
