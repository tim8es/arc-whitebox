from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from e052_v29_r256 import EXPECTED_BLOB, git_blob_sha1, load_e052, load_v29

WIDTH = 1024
DEPTH = 16
SEED = 52052
BUDGET = 2**41
UTIL_GATE = 0.30
DET_GATE = 1e-12
EFFECT_GATE = 1e-8


def make_mlp():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = math.sqrt(2.0 / WIDTH)
    weights = [
        (rng.standard_normal((WIDTH, WIDTH)) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]
    return SimpleNamespace(width=WIDTH, depth=DEPTH, weights=weights, seed=SEED, name="e052-stage-a")


def run_once(mod, mlp, tag):
    est = mod.Estimator()
    est.setup(
        SetupContext(
            width=WIDTH,
            depth=DEPTH,
            flop_budget=BUDGET,
            api_version="1",
            seed=SEED,
        )
    )
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        pred = est.predict(mlp, BUDGET)
    wall_s = time.perf_counter() - started
    est.teardown()
    arr = np.asarray(pred)
    return {
        "tag": tag,
        "prediction": arr,
        "finite": bool(np.isfinite(arr).all()),
        "flops": int(ctx.flops_used),
        "utilization": float(ctx.flops_used / BUDGET),
        "residual_s": float(ctx.residual_wall_time_s),
        "wall_s": float(wall_s),
    }


def compare_outputs(base, cand, repeat):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        b = fnp.asarray(base)
        c = fnp.asarray(cand)
        r = fnp.asarray(repeat)
        d = c - b
        dr = r - c
        per_layer_rms = fnp.sqrt(fnp.mean(d * d, axis=1))
        final_delta = d[-1]
        final_rms = fnp.sqrt(fnp.mean(final_delta * final_delta))
        final_max = fnp.max(fnp.abs(final_delta))
        repeat_max = fnp.max(fnp.abs(dr))
    return {
        "instrumentation_flops": int(ctx.flops_used),
        "per_layer_rms_delta": [float(x) for x in np.asarray(per_layer_rms)],
        "final_rms_delta": float(final_rms),
        "final_max_abs_delta": float(final_max),
        "determinism_max_abs_diff": float(repeat_max),
    }


def main() -> None:
    result = {
        "experiment": "E052",
        "stage": "A",
        "seed": SEED,
        "width": WIDTH,
        "depth": DEPTH,
        "budget": BUDGET,
        "upstream_blob": EXPECTED_BLOB,
        "stage_a_go": False,
    }
    try:
        base_mod, base_bytes = load_v29("e052_stage_base")
        cand_mod, cand_bytes = load_e052("e052_stage_cand")
        result["observed_blob_base"] = git_blob_sha1(base_bytes)
        result["observed_blob_candidate_origin"] = git_blob_sha1(cand_bytes)
        result["base_r_old2"] = int(base_mod.Estimator.R_OLD2)
        result["candidate_r_old2"] = int(cand_mod.Estimator.R_OLD2)
        source_ok = (
            result["observed_blob_base"] == EXPECTED_BLOB
            and result["observed_blob_candidate_origin"] == EXPECTED_BLOB
            and result["base_r_old2"] == 224
            and result["candidate_r_old2"] == 256
        )
        result["source_gate"] = bool(source_ok)
        if not source_ok:
            raise RuntimeError("source/constant gate failed")

        mlp = make_mlp()
        base = run_once(base_mod, mlp, "v29-r224")
        cand = run_once(cand_mod, mlp, "e052-r256")
        cand_repeat_mod, _ = load_e052("e052_stage_cand_repeat")
        repeat = run_once(cand_repeat_mod, mlp, "e052-r256-repeat")

        cmp = compare_outputs(base["prediction"], cand["prediction"], repeat["prediction"])
        deterministic = bool(cmp["determinism_max_abs_diff"] <= DET_GATE)
        finite = bool(cand["finite"] and repeat["finite"])
        util_gate = bool(cand["utilization"] <= UTIL_GATE)
        effect_gate = bool(cmp["final_rms_delta"] >= EFFECT_GATE)

        result.update(
            {
                "baseline_finite": base["finite"],
                "baseline_flops": base["flops"],
                "baseline_utilization": base["utilization"],
                "baseline_residual_s": base["residual_s"],
                "baseline_wall_s": base["wall_s"],
                "candidate_finite": cand["finite"],
                "candidate_flops": cand["flops"],
                "candidate_utilization": cand["utilization"],
                "candidate_residual_s": cand["residual_s"],
                "candidate_wall_s": cand["wall_s"],
                "repeat_finite": repeat["finite"],
                "repeat_flops": repeat["flops"],
                "repeat_utilization": repeat["utilization"],
                "repeat_residual_s": repeat["residual_s"],
                "repeat_wall_s": repeat["wall_s"],
                **cmp,
                "finite_gate": finite,
                "determinism_gate": deterministic,
                "util_gate": util_gate,
                "effect_gate": effect_gate,
            }
        )
        result["flop_delta"] = int(cand["flops"] - base["flops"])
        result["utilization_delta"] = float(cand["utilization"] - base["utilization"])
        result["stage_a_go"] = bool(source_ok and finite and deterministic and util_gate and effect_gate)
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    print("E052_STAGE_A_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    Path("e052-stage-a.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if not result.get("stage_a_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
