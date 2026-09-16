from __future__ import annotations

import json
import math
import sys
import time
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e050_float64_v29 import (
    EXPECTED_BLOB,
    TraceCapture,
    UPSTREAM_RAW_URL,
    capture_lineno,
    git_blob_sha,
    load_module,
    mechanical_float64_source,
)

WIDTH = 32
DEPTH = 8
SEED = 50050
BUDGET = 2**41
UTIL_GATE = 0.30
ABS_GATE = 1e-10
REL_RMS_GATE = 1e-8


def fetch_upstream() -> str:
    with urllib.request.urlopen(UPSTREAM_RAW_URL, timeout=30) as response:
        source = response.read().decode("utf-8")
    observed = git_blob_sha(source)
    if observed != EXPECTED_BLOB:
        raise RuntimeError(f"upstream blob mismatch: {observed} != {EXPECTED_BLOB}")
    return source


def frozen_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = math.sqrt(2.0 / WIDTH)
    raw = rng.standard_normal((DEPTH, WIDTH, WIDTH)) * scale
    return [np.asarray(w, dtype=np.float32) for w in raw]


def run_once(module, source: str, filename: str, weights_np: list[np.ndarray]):
    weights = [fnp.asarray(w) for w in weights_np]
    mlp = SimpleNamespace(width=WIDTH, weights=weights)
    estimator = module.Estimator()
    capture = TraceCapture(filename=filename, lineno=capture_lineno(source), layers=[])
    old_trace = sys.gettrace()
    t0 = time.perf_counter()
    try:
        sys.settrace(capture.tracer)
        with flops.BudgetContext(flop_budget=int(1e15), wall_time_limit_s=1200.0, quiet=True) as ctx:
            prediction = estimator.predict(mlp, BUDGET)
            used = float(ctx.flops_used)
        residual = float(ctx.residual_wall_time_s)
    finally:
        sys.settrace(old_trace)
    wall = time.perf_counter() - t0
    return {
        "prediction": np.array(prediction, dtype=np.float64, copy=True),
        "layers": capture.layers,
        "flops": used,
        "residual_s": residual,
        "wall_s": wall,
    }


def finite_array(x) -> bool:
    return x is None or bool(np.isfinite(x).all())


def compare_array(ref, local):
    if ref is None and local is None:
        return {"available": False, "ref_finite": True, "local_finite": True, "pass": True, "reason": "state not active in frozen V29 control flow"}, 0.0
    if ref is None or local is None:
        return {"available": True, "ref_finite": finite_array(ref), "local_finite": finite_array(local), "pass": False, "reason": "state availability mismatch"}, 0.0
    ref_finite = bool(np.isfinite(ref).all())
    local_finite = bool(np.isfinite(local).all())
    if not ref_finite:
        return {"available": True, "ref_finite": False, "local_finite": local_finite, "pass": local_finite, "reason": "reference non-finite; delta gate not applicable"}, 0.0
    if not local_finite:
        return {"available": True, "ref_finite": True, "local_finite": False, "pass": False}, 0.0

    # Comparison arithmetic itself is metered and added to E050's all-in Stage-A bill.
    with flops.BudgetContext(flop_budget=int(1e12), wall_time_limit_s=120.0, quiet=True) as cctx:
        a = fnp.asarray(ref, dtype=fnp.float64)
        b = fnp.asarray(local, dtype=fnp.float64)
        d = b - a
        max_abs_v = fnp.max(fnp.abs(d))
        rms_d = fnp.sqrt(fnp.mean(d * d))
        rms_a = fnp.sqrt(fnp.mean(a * a))
        denom = fnp.maximum(rms_a, 1e-300)
        rel_v = rms_d / denom
        cmp_flops = float(cctx.flops_used)
    max_abs = float(max_abs_v)
    rel_rms = float(rel_v)
    return {
        "available": True,
        "ref_finite": True,
        "local_finite": True,
        "max_abs": max_abs,
        "rel_rms": rel_rms,
        "pass": max_abs <= ABS_GATE and rel_rms <= REL_RMS_GATE,
    }, cmp_flops


def main() -> None:
    reference_source = fetch_upstream()
    local_source, transform_count = mechanical_float64_source(reference_source)
    ref_filename = "<e050-v29-f32-reference>"
    loc_filename = "<e050-v29-f64-local>"
    ref_module = load_module(reference_source, "e050_v29_f32_reference", ref_filename)
    loc_module = load_module(local_source, "e050_v29_f64_local", loc_filename)
    weights = frozen_weights()

    reference = run_once(ref_module, reference_source, ref_filename, weights)
    local = run_once(loc_module, local_source, loc_filename, weights)
    # Frozen local repeat solely for determinism, within this one Stage-A job.
    repeat_module = load_module(local_source, "e050_v29_f64_repeat", "<e050-v29-f64-repeat>")
    repeat = run_once(repeat_module, local_source, "<e050-v29-f64-repeat>", weights)

    comparisons = []
    compare_flops = 0.0
    if len(reference["layers"]) != len(local["layers"]):
        comparisons.append({"component": "layer_count", "pass": False, "reference": len(reference["layers"]), "local": len(local["layers"])})
    for r, l in zip(reference["layers"], local["layers"]):
        if r["layer"] != l["layer"]:
            comparisons.append({"component": "layer_id", "pass": False, "reference": r["layer"], "local": l["layer"]})
            continue
        for key in ("k3_d3", "d21", "dg"):
            item, extra = compare_array(r[key], l[key])
            compare_flops += extra
            item.update({"layer": r["layer"], "component": key})
            comparisons.append(item)
    final_cmp, extra = compare_array(reference["prediction"], local["prediction"])
    compare_flops += extra
    final_cmp.update({"component": "final_prediction"})
    comparisons.append(final_cmp)

    det_cmp, det_extra = compare_array(local["prediction"], repeat["prediction"])
    compare_flops += det_extra
    det_max_abs = det_cmp.get("max_abs", 0.0) if det_cmp.get("available") else 0.0
    deterministic = bool(det_cmp.get("local_finite", False) and det_max_abs <= 1e-12)

    local_components_finite = all(finite_array(x[k]) for x in local["layers"] for k in ("k3_d3", "d21", "dg"))
    local_finite = bool(np.isfinite(local["prediction"]).all() and local_components_finite)
    comparison_pass = all(bool(x.get("pass", False)) for x in comparisons)
    all_in_flops = local["flops"] + compare_flops
    utilization = all_in_flops / BUDGET
    scope_ok = (
        transform_count > 0
        and local_source == reference_source.replace("fnp.float32", "fnp.float64")
        and git_blob_sha(reference_source) == EXPECTED_BLOB
    )

    gates = {
        "local_finite": local_finite,
        "deterministic_le_1e-12": deterministic,
        "component_deltas": comparison_pass,
        "utilization_le_0.30": utilization <= UTIL_GATE,
        "mechanical_scope": scope_ok,
    }
    decision = "GREEN" if all(gates.values()) else "NO-GO"
    summary = {
        "decision": decision,
        "upstream_blob": EXPECTED_BLOB,
        "transform_count": transform_count,
        "width": WIDTH,
        "depth": DEPTH,
        "seed": SEED,
        "reference_flops": reference["flops"],
        "local_predict_flops": local["flops"],
        "comparison_flops": compare_flops,
        "all_in_flops": all_in_flops,
        "utilization": utilization,
        "reference_residual_s": reference["residual_s"],
        "local_residual_s": local["residual_s"],
        "local_repeat_flops": repeat["flops"],
        "determinism_max_abs": det_max_abs,
        "reference_finite": bool(np.isfinite(reference["prediction"]).all()),
        "local_finite": local_finite,
        "captured_layers_reference": len(reference["layers"]),
        "captured_layers_local": len(local["layers"]),
        "comparisons": comparisons,
        "gates": gates,
    }
    print("E050_STAGE_A " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e050_stage_a.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    if decision != "GREEN":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
