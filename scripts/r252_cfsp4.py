#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np

from r252_fixture import DEPTH, SEED, WIDTH, build_fixture

EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
EXPECTED_V25_SHA256 = "c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20"
BUDGET = 2**41

PATCH_ANCHOR = """            else:
                D3 = D21 = g4row = wk4m = None

            # ---- wick matrix ----
"""

CFSP4_BLOCK = """            else:
                D3 = D21 = g4row = wk4m = None

            if last:
                sigma_cf = fnp.sqrt(var)
                sigma2_cf = sigma_cf * sigma_cf
                sigma3_cf = sigma2_cf * sigma_cf
                sigma4_cf = sigma2_cf * sigma2_cf
                gamma1_cf = D3 / sigma3_cf
                gamma2_cf = g4row / sigma4_cf
                gamma1sq_cf = gamma1_cf * gamma1_cf
                cf_mean = fnp.zeros(n, dtype=f32)

                zcf = (gamma1_cf * 1.1937129433613964
                       + gamma2_cf * -0.6145196865994386
                       + gamma1sq_cf * 0.8987198602957184
                       + -2.8569700138728056)
                cf_mean = cf_mean + fnp.maximum(mu + sigma_cf * zcf, 0.0) * 0.011257411327720693

                zcf = (gamma1_cf * 0.13962038997193682
                       + gamma2_cf * 0.06565058435514533
                       + gamma1sq_cf * -0.04987782969646415
                       + -1.355626179974266)
                cf_mean = cf_mean + fnp.maximum(mu + sigma_cf * zcf, 0.0) * 0.2220759220056126

                zcf = gamma1_cf * -0.16666666666666666
                cf_mean = cf_mean + fnp.maximum(mu + sigma_cf * zcf, 0.0) * 0.5333333333333333

                zcf = (gamma1_cf * 0.13962038997193682
                       + gamma2_cf * -0.06565058435514533
                       + gamma1sq_cf * 0.04987782969646415
                       + 1.355626179974266)
                cf_mean = cf_mean + fnp.maximum(mu + sigma_cf * zcf, 0.0) * 0.2220759220056126

                zcf = (gamma1_cf * 1.1937129433613964
                       + gamma2_cf * 0.6145196865994386
                       + gamma1sq_cf * -0.8987198602957184
                       + 2.8569700138728056)
                cf_mean = cf_mean + fnp.maximum(mu + sigma_cf * zcf, 0.0) * 0.011257411327720693

                rows.append(cf_mean)
                break

            # ---- wick matrix ----
"""

SYM_ATOL = 1e-6
SYM_RTOL = 1e-5

class _Ctx:
    def __init__(self, seed: int):
        self.seed = int(seed)

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()

def arr_sha256(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes(order="C")).hexdigest()

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot construct import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def construct_candidate(parent: Path, candidate: Path) -> dict:
    src = parent.read_text(encoding="utf-8")
    if git_blob(parent) != EXPECTED_V25_BLOB:
        raise RuntimeError("pinned parent git blob mismatch before candidate construction")
    if sha256_file(parent) != EXPECTED_V25_SHA256:
        raise RuntimeError("pinned parent SHA256 mismatch before candidate construction")
    count = src.count(PATCH_ANCHOR)
    if count != 1:
        raise RuntimeError(f"patch anchor count {count}, expected 1")
    if "math." in CFSP4_BLOCK:
        raise RuntimeError("CFSP4 insertion contains prohibited math.*")
    numeric_delta = "\n".join(line for line in CFSP4_BLOCK.splitlines() if line.strip() and not line.lstrip().startswith("#"))
    if "/" in numeric_delta:
        raise RuntimeError("CFSP4 insertion contains unresolved Python division")
    new_src = src.replace(PATCH_ANCHOR, CFSP4_BLOCK, 1)
    if new_src.replace(CFSP4_BLOCK, PATCH_ANCHOR, 1) != src:
        raise RuntimeError("candidate differs beyond frozen insertion")
    candidate.write_text(new_src, encoding="utf-8")
    return {
        "parent_git_blob": git_blob(parent),
        "parent_sha256": sha256_file(parent),
        "candidate_git_blob": git_blob(candidate),
        "candidate_sha256": sha256_file(candidate),
        "patch_anchor_occurrences": count,
        "delta_contains_math_dot": "math." in CFSP4_BLOCK,
        "delta_contains_python_division": "/" in numeric_delta,
        "static_new_flops_upper": 100 * WIDTH,
        "static_skipped_parent_product_units_lower": WIDTH * 21 * (6 + 6 + 11),
    }

def _sym_stage(index: int) -> str:
    return "initial_cov" if index == 0 else f"post_layer_{index - 1}"

def run_estimator(module, weights: list[np.ndarray], seed: int, label: str) -> dict:
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench.domain import MLP

    ws = [fnp.asarray(np.asarray(w, dtype=np.float32)) for w in weights]
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=ws, seed=int(seed), name=f"r252-{label}")
    est = module.Estimator()
    est.setup(_Ctx(seed))

    diagnostics: list[dict] = []
    original = flops.as_symmetric

    def wrapped(data, *args, **kwargs):
        a = np.asarray(data)
        finite = bool(np.isfinite(a).all())
        max_abs = float(np.max(np.abs(a))) if a.size else 0.0
        residual = float(np.max(np.abs(a - np.swapaxes(a, 0, 1)))) if a.ndim >= 2 else 0.0
        diagnostics.append({
            "call_index": len(diagnostics),
            "stage": _sym_stage(len(diagnostics)),
            "shape": list(a.shape),
            "finite": finite,
            "max_abs": max_abs,
            "symmetry_max_abs": residual,
            "allowed": SYM_ATOL + SYM_RTOL * max_abs,
        })
        return original(data, *args, **kwargs)

    flops.as_symmetric = wrapped
    start = time.perf_counter()
    try:
        with flops.BudgetContext(flop_budget=BUDGET, wall_time_limit_s=120.0, quiet=True) as ctx:
            pred = est.predict(mlp, BUDGET)
        elapsed = time.perf_counter() - start
        pred_np = np.asarray(pred, dtype=np.float64)
        result = {
            "ok": True,
            "output_shape": list(pred_np.shape),
            "output_finite": bool(np.isfinite(pred_np).all()),
            "output_sha256": arr_sha256(pred_np),
            "flops_used": int(ctx.flops_used),
            "residual_wall_time_s": float(getattr(ctx, "residual_wall_time_s", 0.0) or 0.0),
            "wall_time_s": float(elapsed),
            "symmetry_checkpoints": diagnostics,
            "per_layer": [
                {"layer": i, "finite": bool(np.isfinite(pred_np[i]).all()),
                 "max_abs": float(np.max(np.abs(pred_np[i]))), "sha256": arr_sha256(pred_np[i])}
                for i in range(pred_np.shape[0])
            ],
            "_prediction": pred_np,
        }
    except Exception as exc:
        result = {
            "ok": False,
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "wall_time_s": float(time.perf_counter() - start),
            "symmetry_checkpoints": diagnostics,
        }
    finally:
        flops.as_symmetric = original
    return result

def symmetry_gate(run: dict) -> bool:
    ds = run.get("symmetry_checkpoints") or []
    return len(ds) == 16 and all(d["finite"] for d in ds) and all(d["symmetry_max_abs"] <= d["allowed"] for d in ds)

def parent_gate(run: dict) -> dict:
    gates = {
        "run_ok": bool(run.get("ok")),
        "shape_16x1024": run.get("output_shape") == [DEPTH, WIDTH],
        "output_finite": bool(run.get("output_finite")),
        "symmetry_16_finite_tolerance": symmetry_gate(run),
        "per_layer_finite": bool(run.get("per_layer")) and all(x["finite"] for x in run.get("per_layer", [])),
        "flops_positive_within_budget": 0 < int(run.get("flops_used", 0) or 0) <= BUDGET,
    }
    return {"gates": gates, "pass": all(gates.values())}

def mse_rows(pred: np.ndarray, truth: np.ndarray) -> list[float]:
    d = pred - truth
    return [float(np.mean(d[i] * d[i])) for i in range(DEPTH)]

def clean_run(run: dict) -> dict:
    return {k: v for k, v in run.items() if k != "_prediction"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v25", type=Path, required=True)
    ap.add_argument("--candidate-out", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    result = {
        "schema": "arc.whitebox.r252.cfsp4_target_free.v1",
        "job_id": "R252",
        "run_id": "R252-one-shot-actions-global-accuracy-20260923",
        "candidate_id": "V25-CFSP4-FINAL-CORNISH-FISHER-SIGMA-POINT",
        "parent_source": {"git_blob": git_blob(args.v25), "sha256": sha256_file(args.v25)},
        "candidate_constructed": False,
        "public_authorized": False,
    }
    if result["parent_source"]["git_blob"] != EXPECTED_V25_BLOB or result["parent_source"]["sha256"] != EXPECTED_V25_SHA256:
        result["decision"] = "R252_PARENT_INCONCLUSIVE"
        result["reason"] = "pinned parent identity mismatch"
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 20

    weights, truth = build_fixture()
    result["fixture"] = {"truth_sha256": arr_sha256(np.ascontiguousarray(truth.astype("<f8", copy=False))), "truth_shape": list(truth.shape)}

    parent = run_estimator(load_module(args.v25, "r252_parent_v25"), weights, SEED, "parent")
    pg = parent_gate(parent)
    result["parent"] = clean_run(parent)
    result["parent_gate"] = pg
    if not pg["pass"]:
        result["decision"] = "R252_PARENT_INCONCLUSIVE"
        result["reason"] = "unchanged parent failed one or more frozen parent gates"
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 20

    source = construct_candidate(args.v25, args.candidate_out)
    result["candidate_constructed"] = True
    result["candidate_source"] = source
    candidate = run_estimator(load_module(args.candidate_out, "r252_candidate_v25_cfsp4"), weights, SEED, "candidate")
    result["candidate"] = clean_run(candidate)
    if not candidate.get("ok"):
        result["target_free_gate"] = {"pass": False, "gates": {"run_ok": False}}
        result["decision"] = "R252_TARGET_FREE_NO_GO"
        result["reason"] = "candidate execution failed"
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 30

    pp, cp = parent["_prediction"], candidate["_prediction"]
    pm, cm = mse_rows(pp, truth), mse_rows(cp, truth)
    pmax = float(np.max(np.abs(pp[-1] - truth[-1])))
    cmax = float(np.max(np.abs(cp[-1] - truth[-1])))
    pres = float(parent.get("residual_wall_time_s", 0.0))
    cres = float(candidate.get("residual_wall_time_s", 0.0))
    tgates = {
        "source_patch_confined": source["patch_anchor_occurrences"] == 1,
        "delta_no_math_dot": not source["delta_contains_math_dot"],
        "delta_no_python_division": not source["delta_contains_python_division"],
        "static_cost_direction": source["static_new_flops_upper"] <= source["static_skipped_parent_product_units_lower"],
        "run_ok": bool(candidate.get("ok")),
        "shape_16x1024": candidate.get("output_shape") == [DEPTH, WIDTH],
        "output_finite": bool(candidate.get("output_finite")),
        "symmetry_16_finite_tolerance": symmetry_gate(candidate),
        "rows_0_14_byte_identical": bool(np.array_equal(cp[:-1], pp[:-1])),
        "final_mse_ratio_le_0_95": cm[-1] <= 0.95 * pm[-1],
        "final_max_abs_nonregression": cmax <= pmax,
        "flops_nonregression": int(candidate["flops_used"]) <= int(parent["flops_used"]),
        "residual_time_nonregression_5pct": cres <= 1.05 * pres,
    }
    result["target_free_metrics"] = {
        "parent_per_layer_mse": pm, "candidate_per_layer_mse": cm,
        "parent_final_mse": pm[-1], "candidate_final_mse": cm[-1],
        "final_mse_ratio": (cm[-1] / pm[-1]) if pm[-1] != 0.0 else None,
        "parent_final_max_abs": pmax, "candidate_final_max_abs": cmax,
        "parent_flops": int(parent["flops_used"]), "candidate_flops": int(candidate["flops_used"]),
        "parent_residual_wall_time_s": pres, "candidate_residual_wall_time_s": cres,
    }
    result["target_free_gate"] = {"gates": tgates, "pass": all(tgates.values())}
    if not result["target_free_gate"]["pass"]:
        result["decision"] = "R252_TARGET_FREE_NO_GO"
        result["reason"] = "one or more frozen target-free/source/cost gates failed"
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 30

    result["decision"] = "R252_TARGET_FREE_GO"
    result["public_authorized"] = True
    result["reason"] = "parent and all frozen target-free/source/cost gates passed"
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
