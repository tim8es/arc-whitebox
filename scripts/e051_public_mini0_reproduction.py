from __future__ import annotations

import json
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench
from whestbench import SetupContext

from methods.e051_v29_adapter import DEPTH, EXPECTED_BLOB, WIDTH, git_blob_sha1, load_exact_v29

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
RAW_GATE = 2.30e-8
UTIL_GATE = 0.30
DET_GATE = 1e-12


def setup_estimator(estimator) -> None:
    estimator.setup(SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET, api_version="1", seed=0))


def run_predict(mod, mlp):
    estimator = mod.Estimator()
    setup_estimator(estimator)
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        prediction = estimator.predict(mlp, BUDGET)
    wall_s = time.perf_counter() - started
    estimator.teardown()
    return prediction, int(ctx.flops_used), float(ctx.residual_wall_time_s), wall_s


def metric_flops_and_mse(prediction, target):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        p = fnp.asarray(prediction)
        t = fnp.asarray(target)
        delta = p[-1] - t
        raw = fnp.mean(delta * delta)
    return float(raw), int(ctx.flops_used)


def determinism_metric(a, b):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        aa = fnp.asarray(a)
        bb = fnp.asarray(b)
        diff = fnp.max(fnp.abs(aa - bb))
    return float(diff), int(ctx.flops_used)


def main() -> None:
    result = {"experiment":"E051","dataset":DATASET,"revision":REVISION,"split":SPLIT,"index":INDEX,"budget":BUDGET,"upstream_blob":EXPECTED_BLOB,"failures":1,"reproduction_go":False}
    try:
        mod, exact_bytes = load_exact_v29()
        result["observed_blob"] = git_blob_sha1(exact_bytes)
        dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
        row = dataset[INDEX]
        mlp = whestbench.mlp_at(dataset, INDEX)
        target = np.asarray(row["final_means"])
        result["width"] = int(mlp.width); result["depth"] = int(mlp.depth)
        if int(mlp.width) != WIDTH or int(mlp.depth) != DEPTH:
            raise RuntimeError(f"unexpected mini0 shape width={mlp.width} depth={mlp.depth}")
        pred1, predict_flops, residual_s, wall_s = run_predict(mod, mlp)
        pred1_np = np.asarray(pred1)
        finite = bool(np.isfinite(pred1_np).all())
        raw_mse, metric_flops = metric_flops_and_mse(pred1, target)
        all_in_flops = int(predict_flops + metric_flops)
        utilization = float(all_in_flops / BUDGET)
        pred2, repeat_flops, repeat_residual_s, repeat_wall_s = run_predict(mod, mlp)
        repeat_np = np.asarray(pred2)
        repeat_finite = bool(np.isfinite(repeat_np).all())
        det_max, det_metric_flops = determinism_metric(pred1, pred2)
        deterministic = bool(det_max <= DET_GATE)
        result.update({"failures":0,"finite":finite,"repeat_finite":repeat_finite,"raw_final_mse":raw_mse,"predict_flops":predict_flops,"metric_flops":metric_flops,"all_in_flops":all_in_flops,"utilization":utilization,"residual_s":residual_s,"wall_s":wall_s,"repeat_predict_flops":repeat_flops,"repeat_residual_s":repeat_residual_s,"repeat_wall_s":repeat_wall_s,"determinism_metric_flops":det_metric_flops,"determinism_max_abs_diff":det_max,"deterministic":deterministic,"raw_gate":raw_mse <= RAW_GATE,"util_gate":utilization <= UTIL_GATE,"determinism_gate":deterministic})
        result["reproduction_go"] = bool(finite and repeat_finite and result["failures"] == 0 and result["raw_gate"] and result["util_gate"] and result["determinism_gate"])
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)
    print("E051_REPRODUCTION_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    Path("e051-mini0.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if not result.get("reproduction_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
