from __future__ import annotations

import json
import traceback
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from methods.e050_v29_float64_port import (
    BUDGET, DEPTH, SEED, WIDTH, UPSTREAM_RAW,
    TraceRecorder, build_module, compare_arrays,
    instrument_source, mechanical_float64_source, verify_upstream_bytes,
)

OUT = Path("artifacts/e050-stage-a.json")
ABS_TOL = 1e-10
REL_RMS_TOL = 1e-8
UTIL_GATE = 0.30


def load_frozen_source() -> str:
    data = urllib.request.urlopen(UPSTREAM_RAW, timeout=30).read()
    verify_upstream_bytes(data)
    return data.decode("utf-8")


def frozen_weights():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = 1.0 / np.sqrt(WIDTH)
    raw = [rng.standard_normal((WIDTH, WIDTH)) * scale for _ in range(DEPTH)]
    # Input is exactly identical float32 for both paths. The local V29 port performs
    # its own frozen float64 conversion inside BudgetContext and that conversion is metered.
    return [fnp.asarray(x, dtype=fnp.float32) for x in raw]


def make_mlp(weights):
    return SimpleNamespace(width=WIDTH, depth=DEPTH, seed=SEED, weights=weights)


def run_estimator(module, recorder: TraceRecorder, weights):
    est = module.Estimator()
    ctx = SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET, api_version="1", seed=SEED)
    error = None
    pred = None
    used = 0
    est.setup(ctx)
    try:
        try:
            with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
                pred = est.predict(make_mlp(weights), BUDGET)
            used = int(budget.flops_used)
        except Exception as exc:  # evidence capture only; no recovery/retry
            try:
                used = int(budget.flops_used)
            except Exception:
                used = 0
            error = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
    finally:
        est.teardown()
    return {
        "pred": None if pred is None else np.asarray(pred).copy(),
        "flops": used,
        "scan_flops": int(recorder.scan_flops),
        "first_nonfinite": recorder.first_nonfinite,
        "error": error,
        "records": recorder.records,
    }


def trace_map(run):
    out = {}
    for rec in run["records"]:
        out[(rec["layer"], rec["name"])] = rec
    return out


def compare_trace(ref, local):
    rmap = trace_map(ref)
    lmap = trace_map(local)
    names = ["mu", "var", "alpha", "W_all", "A_st", "P_st", "Z_st", "D3", "D21", "PK1", "PK2", "K2", "K11", "C", "dG", "final_output"]
    summary = {name: {"pairs": 0, "max_abs": 0.0, "max_rel_rms": 0.0, "comparison_flops": 0, "reference_nonfinite": []} for name in names}
    total_cmp = 0
    for key, rr in rmap.items():
        layer, name = key
        if name not in summary or key not in lmap:
            continue
        lr = lmap[key]
        if rr["value"] is None or lr["value"] is None:
            continue
        if not rr["finite"]:
            summary[name]["reference_nonfinite"].append(layer)
            continue
        if not lr["finite"]:
            summary[name]["max_abs"] = float("inf")
            summary[name]["max_rel_rms"] = float("inf")
            continue
        ma, mr, cf = compare_arrays(rr["value"], lr["value"])
        summary[name]["pairs"] += 1
        summary[name]["max_abs"] = max(summary[name]["max_abs"], ma)
        summary[name]["max_rel_rms"] = max(summary[name]["max_rel_rms"], mr)
        summary[name]["comparison_flops"] += cf
        total_cmp += cf
    return summary, total_cmp


def k4_identity(dtype):
    rng = np.random.Generator(np.random.PCG64(SEED + 1))
    W = fnp.asarray(rng.standard_normal((WIDTH, WIDTH)) / np.sqrt(WIDTH), dtype=dtype)
    g_prev = fnp.asarray(rng.standard_normal(WIDTH) * 1e-2, dtype=dtype)
    var_prev = fnp.asarray(0.5 + rng.random(WIDTH), dtype=dtype)
    var = fnp.asarray(0.5 + rng.random(WIDTH), dtype=dtype)
    lam_prev = 8.0876e-03 * 0.95
    ref = 6.58815e-03
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
        WW = W * W
        t_g = WW @ g_prev
        t_v = var - WW @ var_prev
        dG0 = t_g + t_v * lam_prev
        rr = fnp.mean(dG0) / fnp.mean(var)
        lam = lam_prev * fnp.power(fnp.clip(rr / ref, 0.5, 2.0), 1.0)
        dG = t_g + t_v * lam
    return np.asarray(dG).copy(), float(lam), int(budget.flops_used)


def finite_records(run):
    return bool(run["error"] is None and all(bool(r["finite"]) for r in run["records"]) and run["pred"] is not None and np.isfinite(run["pred"]).all())


def jsonify_run(run):
    return {
        "flops": run["flops"],
        "scan_flops": run["scan_flops"],
        "first_nonfinite": run["first_nonfinite"],
        "error": run["error"],
        "finite": finite_records(run),
        "record_count": len(run["records"]),
    }


def main() -> int:
    source = load_frozen_source()
    ref_rec = TraceRecorder("upstream-f32")
    local1_rec = TraceRecorder("local-f64-1")
    local2_rec = TraceRecorder("local-f64-2")

    ref_mod = build_module(instrument_source(source), "e050_ref_f32", ref_rec)
    port_source = mechanical_float64_source(source)
    local1_mod = build_module(instrument_source(port_source), "e050_local_f64_1", local1_rec)
    local2_mod = build_module(instrument_source(port_source), "e050_local_f64_2", local2_rec)

    # Exact constants/order: module-level objects and frozen class knobs must match.
    constants_equal = all([
        ref_mod.WICK_PAIRS == local1_mod.WICK_PAIRS,
        ref_mod.WICK_UNIFIED == local1_mod.WICK_UNIFIED,
        ref_mod.PK2K_TABLE == local1_mod.PK2K_TABLE,
        ref_mod.CORR_BETA == local1_mod.CORR_BETA,
        ref_mod.LAM == local1_mod.LAM,
        ref_mod.REF_R == local1_mod.REF_R,
        ref_mod.BETA == local1_mod.BETA,
        ref_mod.Estimator.AGE_OLD == local1_mod.Estimator.AGE_OLD,
        ref_mod.Estimator.R_OLD == local1_mod.Estimator.R_OLD,
        ref_mod.Estimator.AGE_OLD2 == local1_mod.Estimator.AGE_OLD2,
        ref_mod.Estimator.R_OLD2 == local1_mod.Estimator.R_OLD2,
        ref_mod.Estimator.R_FB == local1_mod.Estimator.R_FB,
        ref_mod.Estimator.R_RES == local1_mod.Estimator.R_RES,
        ref_mod.STRASSEN_LEVELS == local1_mod.STRASSEN_LEVELS,
        ref_mod.STRASSEN_MIN == local1_mod.STRASSEN_MIN,
    ])

    weights = frozen_weights()
    ref = run_estimator(ref_mod, ref_rec, weights)
    local1 = run_estimator(local1_mod, local1_rec, weights)
    local2 = run_estimator(local2_mod, local2_rec, weights)

    component, cmp_flops = compare_trace(ref, local1)

    deterministic = False
    det_max_abs = float("inf")
    det_flops = 0
    if local1["pred"] is not None and local2["pred"] is not None:
        deterministic = bool(np.array_equal(local1["pred"], local2["pred"]))
        det_max_abs, _, det_flops = compare_arrays(local1["pred"], local2["pred"])
        deterministic = deterministic or det_max_abs <= 1e-12

    k4_f32, k4_lam32, k4_flops32 = k4_identity(fnp.float32)
    k4_f64, k4_lam64, k4_flops64 = k4_identity(fnp.float64)
    k4_abs, k4_rel, k4_cmp_flops = compare_arrays(k4_f32, k4_f64)
    k4_lam_abs = abs(k4_lam32 - k4_lam64)
    k4_pass = bool(np.isfinite(k4_f64).all() and k4_abs <= ABS_TOL and k4_rel <= REL_RMS_TOL and k4_lam_abs <= ABS_TOL)

    # Frozen component gate applies where the f32 reference remains finite.
    gated_names = ("D3", "D21", "dG", "final_output")
    component_pass = True
    for name in gated_names:
        s = component[name]
        if s["pairs"] > 0 and (s["max_abs"] > ABS_TOL or s["max_rel_rms"] > REL_RMS_TOL):
            component_pass = False

    local_all_in = int(local1["flops"] + local1["scan_flops"] + cmp_flops + det_flops + k4_flops64 + k4_cmp_flops)
    local_util = local_all_in / BUDGET
    stage_total = int(ref["flops"] + local1["flops"] + local2["flops"] + ref["scan_flops"] + local1["scan_flops"] + local2["scan_flops"] + cmp_flops + det_flops + k4_flops32 + k4_flops64 + k4_cmp_flops)

    local_finite = finite_records(local1)
    go = bool(constants_equal and local_finite and deterministic and component_pass and k4_pass and local_util <= UTIL_GATE)

    result = {
        "experiment": "E050",
        "stage": "A",
        "width": WIDTH,
        "depth": DEPTH,
        "seed": SEED,
        "budget": BUDGET,
        "upstream_blob": "17df1a073a24f96c4705b04bcf61ef60fa06dd0c",
        "mechanical_dtype_edits": 2,
        "constants_equal": constants_equal,
        "reference": jsonify_run(ref),
        "local_first": jsonify_run(local1),
        "local_repeat": jsonify_run(local2),
        "deterministic": deterministic,
        "deterministic_max_abs": det_max_abs,
        "component_deltas": component,
        "component_gate_pass": component_pass,
        "isolated_regen_k4": {
            "f32_flops": k4_flops32,
            "f64_flops": k4_flops64,
            "max_abs": k4_abs,
            "max_rel_rms": k4_rel,
            "lambda_f32": k4_lam32,
            "lambda_f64": k4_lam64,
            "lambda_abs": k4_lam_abs,
            "pass": k4_pass,
        },
        "local_all_in_flops": local_all_in,
        "local_utilization": local_util,
        "stage_total_flops": stage_total,
        "util_gate": UTIL_GATE,
        "stage_a_green": go,
        "terminal": "STAGE_A_GREEN_STOP_FOR_REVIEW" if go else "NO-GO/DROP",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print("E050_STAGE_A_JSON=" + json.dumps(result, sort_keys=True, default=str))
    # The workflow itself may stay green so the artifact is always uploaded; verdict is in JSON.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
