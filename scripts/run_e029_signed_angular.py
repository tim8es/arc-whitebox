from __future__ import annotations

import json
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq

from methods.e029_signed_angular import (
    build_support,
    fit_first_layer_weights_from_preactivation,
    gaussian_radius_mean,
)

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
WIDTH = 1024
DEPTH = 16
PAIR_COUNT = 3 * WIDTH
RAW_GATE = 2.45e-8
ADJUSTED_GATE = 2.5e-9
UTIL_GATE = 0.105
RESIDUAL_CAP = 0.400
LAYER1_REL_GATE = 1e-5
WEIGHT_SUM_GATE = 1e-5
WEIGHT_L1_GATE = 4.0


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
    weights_fnp = [fnp.asarray(w) for w in weights_np]
    return weights_np, weights_fnp, gt


def _predict(xp, weights):
    n = WIDTH
    m = PAIR_COUNT
    radius = gaussian_radius_mean(n)
    w0 = weights[0]
    support = build_support(xp, w0)
    if support.shape != (m, n):
        raise RuntimeError(f"frozen support shape mismatch: {support.shape}")

    # Reused both by the exact layer-1 constraint fit and the antipodal carrier.
    z0 = support @ w0.T
    pair_weights, target1, achieved1 = fit_first_layer_weights_from_preactivation(
        xp, w0, z0, radius
    )

    h_plus = xp.maximum(z0, 0.0)
    h_minus = xp.maximum(-z0, 0.0)
    pair = h_plus + h_minus
    mu0 = (0.5 * radius) * (pair_weights @ pair)
    means = [mu0]

    h = xp.concatenate([h_plus, h_minus], axis=0)
    for layer in range(1, DEPTH):
        h = xp.maximum(h @ weights[layer].T, 0.0)
        pair = h[:m] + h[m:]
        means.append((0.5 * radius) * (pair_weights @ pair))

    return xp.stack(means, axis=0), pair_weights, target1, achieved1


def _run_metered(weights):
    t0 = time.perf_counter()
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ) as ctx:
        pred, pair_weights, target1, achieved1 = _predict(fnp, weights)
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        np.asarray(pair_weights, dtype=np.float64),
        np.asarray(target1, dtype=np.float64),
        np.asarray(achieved1, dtype=np.float64),
        used,
        float(ctx.residual_wall_time_s),
        wall,
    )


def _run_repeat(weights):
    # A separate context is used only because fnp.linalg.solve requires an
    # active budget context.  Its FLOPs are intentionally excluded from the
    # reported candidate cost; this repeat exists solely for determinism.
    with flops.BudgetContext(
        flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
    ):
        pred, _, _, _ = _predict(fnp, weights)
    return np.asarray(pred, dtype=np.float64)


def main() -> None:
    row = _load_row0()
    weights_np, weights_fnp, gt = _prepare(row)

    pred, signed_w, target1, achieved1, used, residual, wall = _run_metered(weights_fnp)
    repeat = _run_repeat(weights_fnp)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    layer1_abs = np.abs(achieved1 - target1)
    layer1_max_abs = float(np.max(layer1_abs))
    layer1_max_rel = float(np.max(layer1_abs / np.maximum(np.abs(target1), 1e-30)))
    weight_sum = float(np.sum(signed_w))
    weight_l1 = float(np.sum(np.abs(signed_w)))
    weight_min = float(np.min(signed_w))
    weight_max = float(np.max(signed_w))
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(
        np.isfinite(pred).all()
        and np.isfinite(signed_w).all()
        and np.isfinite(target1).all()
        and np.isfinite(achieved1).all()
    )

    method_source = Path("methods/e029_signed_angular.py").read_text(encoding="utf-8")
    forbidden = ("pinv(", "lstsq(", "clip(", "ridge", "jitter", "fallback")
    scope_ok = (
        PAIR_COUNT == 3072
        and "xp.concatenate([eye, rows, cols], axis=0)" in method_source
        and all(token not in method_source.lower() for token in forbidden)
    )

    gates = {
        "final_mse_le_2.45e-08": final_mse <= RAW_GATE,
        "adjusted_lt_2.5e-09": adjusted < ADJUSTED_GATE,
        "util_le_0.105": util <= UTIL_GATE,
        "residual_lt_0.400s": residual < RESIDUAL_CAP,
        "layer1_max_rel_le_1e-5": layer1_max_rel <= LAYER1_REL_GATE,
        "weight_sum": abs(weight_sum - 1.0) <= WEIGHT_SUM_GATE,
        "weight_l1_le_4": weight_l1 <= WEIGHT_L1_GATE,
        "finite": finite,
        "deterministic": det_max_abs == 0.0,
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
        "layer1_max_abs": layer1_max_abs,
        "layer1_max_rel": layer1_max_rel,
        "weight_sum": weight_sum,
        "weight_l1": weight_l1,
        "weight_min": weight_min,
        "weight_max": weight_max,
        "det_max_abs": det_max_abs,
        "support_pairs": PAIR_COUNT,
        "support_endpoints": 2 * PAIR_COUNT,
        "finite": finite,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E029_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e029_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
