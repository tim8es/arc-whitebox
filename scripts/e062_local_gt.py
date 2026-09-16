from __future__ import annotations

import json
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench
from whestbench import SetupContext

from methods.e062_structure_fwht import Estimator

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 1.89e-8
UTIL_GATE = 0.135
E051_RAW = 2.29004485946887e-8
E051_UTIL = 0.2670561845802695


def run_predict(mlp):
    est = Estimator()
    est.setup(
        SetupContext(
            width=int(mlp.width),
            depth=int(mlp.depth),
            flop_budget=BUDGET,
            api_version="1",
            seed=62062,
        )
    )
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        pred = est.predict(mlp, BUDGET)
    wall_s = time.perf_counter() - started
    stats = dict(est.last_stats)
    est.teardown()
    return pred, int(ctx.flops_used), float(ctx.residual_wall_time_s), wall_s, stats


def metric(pred, target):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        p = fnp.asarray(pred)
        t = fnp.asarray(target)
        d = p[-1] - t
        mse = fnp.mean(d * d)
    return float(mse), int(ctx.flops_used)


def det_metric(a, b):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        aa = fnp.asarray(a)
        bb = fnp.asarray(b)
        diff = fnp.max(fnp.abs(aa - bb))
    return float(diff), int(ctx.flops_used)


def main() -> None:
    result = {
        "experiment": "E062",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "index": INDEX,
        "budget": BUDGET,
        "raw_gate_value": RAW_GATE,
        "util_gate_value": UTIL_GATE,
        "e051_raw": E051_RAW,
        "e051_util": E051_UTIL,
        "failures": 1,
        "local_go": False,
    }
    try:
        dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
        row = dataset[INDEX]
        mlp = whestbench.mlp_at(dataset, INDEX)
        target = np.asarray(row["final_means"])
        result["width"] = int(mlp.width)
        result["depth"] = int(mlp.depth)
        if int(mlp.width) != 1024 or int(mlp.depth) != 16:
            raise RuntimeError(
                f"unexpected Phase-2 shape width={mlp.width} depth={mlp.depth}"
            )

        p1, predict_flops, residual_s, wall_s, stats1 = run_predict(mlp)
        p1_np = np.asarray(p1)
        finite = bool(np.isfinite(p1_np).all())
        raw, metric_flops = metric(p1, target)
        all_in = int(predict_flops + metric_flops)
        util = float(all_in / BUDGET)

        p2, repeat_flops, repeat_residual_s, repeat_wall_s, stats2 = run_predict(mlp)
        p2_np = np.asarray(p2)
        repeat_finite = bool(np.isfinite(p2_np).all())
        det, det_flops = det_metric(p1, p2)
        deterministic = bool(det == 0.0)
        structural_active = bool(
            stats1.get("n_lines") == 2048
            and stats1.get("n_rows") == 4096
            and stats1.get("pilot_lines") == 256
            and len(stats1.get("suffix_dead_on_kink", ())) == 3
        )

        result.update(
            {
                "failures": 0,
                "finite": finite,
                "repeat_finite": repeat_finite,
                "raw_final_mse": raw,
                "predict_flops": predict_flops,
                "metric_flops": metric_flops,
                "all_in_flops": all_in,
                "utilization": util,
                "residual_s": residual_s,
                "wall_s": wall_s,
                "repeat_predict_flops": repeat_flops,
                "repeat_residual_s": repeat_residual_s,
                "repeat_wall_s": repeat_wall_s,
                "determinism_metric_flops": det_flops,
                "determinism_max_abs_diff": det,
                "deterministic": deterministic,
                "structural_active": structural_active,
                "stats": stats1,
                "repeat_stats_equal": stats1 == stats2,
                "raw_gate": raw <= RAW_GATE,
                "util_gate": util <= UTIL_GATE,
                "raw_vs_e051_ratio": raw / E051_RAW,
                "util_vs_e051_ratio": util / E051_UTIL,
            }
        )
        result["local_go"] = bool(
            finite
            and repeat_finite
            and deterministic
            and result["repeat_stats_equal"]
            and structural_active
            and result["raw_gate"]
            and result["util_gate"]
            and result["failures"] == 0
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    payload = json.dumps(result, sort_keys=True)
    print("E062_LOCAL_JSON=" + payload, flush=True)
    Path("e062-local.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    if not result.get("local_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
