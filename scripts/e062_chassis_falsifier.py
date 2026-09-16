from __future__ import annotations

import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import whestbench

from methods.e062_chassis_falsifier import full_safety_audit, run_metered
from methods.e062_structure_fwht import antithetic_next_preact, signed_walsh_products

BUDGET = 2**41
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDICES = (0, 1, 2, 3)
GATE_A_RELRMS = 1e-6
GATE_A_MAXABS = 5e-6
GATE_B_WEIGHTED = 1e-4
GATE_C_POOLED = 1.01
GATE_C_PER_MLP = 1.03
GATE_D_FLOP_RATIO = 0.90
GATE_D_REMOVED_SHARE = 0.70
E051_RAW = 2.29004485946887e-08
E051_UTIL = 0.2670561845802695


def _walsh_matrix(width: int):
    vals = []
    for r in range(width):
        vals.append([1.0 if ((r & c).bit_count() & 1) == 0 else -1.0 for c in range(width)])
    return fnp.asarray(vals, dtype=fnp.float32)


def _parity_signs(width: int):
    return fnp.asarray(
        [1.0 if (i.bit_count() & 1) == 0 else -1.0 for i in range(width)],
        dtype=fnp.float32,
    )


def gate_a_audit(mlp):
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        width = int(mlp.width)
        h = _walsh_matrix(width)
        signs = _parity_signs(width)
        w0 = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
        w1 = fnp.asarray(mlp.weights[1], dtype=fnp.float32)

        got = signed_walsh_products(w0)
        direct0 = h @ w0
        direct1 = h @ (signs[:, None] * w0)
        ref = fnp.concatenate((direct0, direct1), axis=0)
        d0 = got - ref

        zero = fnp.asarray(0.0, dtype=fnp.float32)
        hpos = fnp.maximum(got, zero)
        hneg = fnp.maximum(-got, zero)
        w01 = w0 @ w1
        zw1 = signed_walsh_products(w01)
        _, neg_fold = antithetic_next_preact(got, hpos, w1, zw1)
        neg_ref = hneg @ w1
        d1 = neg_fold - neg_ref

        ss_err = fnp.sum(d0 * d0) + fnp.sum(d1 * d1)
        ss_ref = fnp.sum(ref * ref) + fnp.sum(neg_ref * neg_ref)
        rel = fnp.sqrt(
            ss_err / fnp.maximum(ss_ref, fnp.asarray(1e-30, dtype=fnp.float32))
        )
        maxabs = fnp.maximum(fnp.max(fnp.abs(d0)), fnp.max(fnp.abs(d1)))
    return {
        "rel_rms": float(rel),
        "max_abs": float(maxabs),
        "flops": int(ctx.flops_used),
        "residual_s": float(ctx.residual_wall_time_s),
        "wall_s": time.perf_counter() - started,
    }


def prediction_metric(prediction, target):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        p = fnp.asarray(prediction)
        t = fnp.asarray(target, dtype=p.dtype)
        delta = p[-1] - t
        raw = fnp.mean(delta * delta)
        finite = fnp.all(fnp.isfinite(p))
    return float(raw), bool(finite), int(ctx.flops_used)


def determinism_metric(a, b):
    with flops.BudgetContext(flop_budget=10**9, quiet=True) as ctx:
        d = fnp.max(fnp.abs(fnp.asarray(a) - fnp.asarray(b)))
    return float(d), int(ctx.flops_used)


def safety_audit(mlp):
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        items = full_safety_audit(mlp)
    return (
        items,
        int(ctx.flops_used),
        float(ctx.residual_wall_time_s),
        time.perf_counter() - started,
    )


def main():
    result = {
        "experiment": "E062",
        "diagnostic": "four_mlp_full_vs_chassis",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "indices": list(INDICES),
        "budget": BUDGET,
        "e051_raw": E051_RAW,
        "e051_util": E051_UTIL,
        "failures": 1,
        "falsifier_go": False,
    }
    try:
        dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
        mlps = [whestbench.mlp_at(dataset, i) for i in INDICES]
        rows = [dataset[i] for i in INDICES]
        if any(int(m.width) != 1024 or int(m.depth) != 16 for m in mlps):
            raise RuntimeError("unexpected Phase-2 shape in frozen indices")

        gate_a = gate_a_audit(mlps[0])
        gate_a_ok = (
            gate_a["rel_rms"] <= GATE_A_RELRMS
            and gate_a["max_abs"] <= GATE_A_MAXABS
        )

        per_mlp = []
        full_raws = []
        chassis_raws = []
        full_allin = 0
        chassis_allin = 0
        removed_gemm = 0
        safety_num = 0.0
        safety_den = 0.0
        high_violations = 0
        total_violations = 0
        safety_flops = 0
        safety_residual = 0.0
        safety_wall = 0.0
        first_full_pred = None
        first_chassis_pred = None

        for idx, mlp, row in zip(INDICES, mlps, rows):
            full = run_metered(mlp, chassis=False, budget=BUDGET)
            chassis = run_metered(mlp, chassis=True, budget=BUDGET)
            if idx == INDICES[0]:
                first_full_pred = full.prediction
                first_chassis_pred = chassis.prediction

            target = row["final_means"]
            full_raw, full_finite, full_metric_flops = prediction_metric(
                full.prediction, target
            )
            chassis_raw, chassis_finite, chassis_metric_flops = prediction_metric(
                chassis.prediction, target
            )
            full_item_allin = full.flops + full_metric_flops
            chassis_item_allin = chassis.flops + chassis_metric_flops
            full_allin += full_item_allin
            chassis_allin += chassis_item_allin
            removed_gemm += int(chassis.stats["removed_gemm_flops"])
            full_raws.append(full_raw)
            chassis_raws.append(chassis_raw)

            audits, af, ar, aw = safety_audit(mlp)
            safety_flops += af
            safety_residual += ar
            safety_wall += aw
            for item in audits:
                safety_num += float(item["weighted_violation_num"])
                safety_den += float(item["weighted_violation_den"])
                high_violations += int(item["high_violation_count"])
                total_violations += int(item["violation_count"])

            ratio = chassis_raw / full_raw if full_raw > 0 else math.inf
            per_mlp.append(
                {
                    "index": idx,
                    "full_raw": full_raw,
                    "chassis_raw": chassis_raw,
                    "raw_ratio": ratio,
                    "full_finite": full_finite,
                    "chassis_finite": chassis_finite,
                    "full_predict_flops": full.flops,
                    "chassis_predict_flops": chassis.flops,
                    "full_all_in_flops": full_item_allin,
                    "chassis_all_in_flops": chassis_item_allin,
                    "full_residual_s": full.residual_s,
                    "chassis_residual_s": chassis.residual_s,
                    "full_wall_s": full.wall_s,
                    "chassis_wall_s": chassis.wall_s,
                    "removed_gemm_flops": int(chassis.stats["removed_gemm_flops"]),
                    "pilot_dead_removed": list(chassis.stats["pilot_dead_removed"]),
                    "exact_zero_removed_full": list(
                        full.stats["exact_zero_removed"]
                    ),
                    "exact_zero_removed_chassis": list(
                        chassis.stats["exact_zero_removed"]
                    ),
                    "suffix_counts": [
                        list(x) for x in chassis.stats["suffix_counts"]
                    ],
                    "safety": audits,
                }
            )

        pooled_full = sum(full_raws) / len(full_raws)
        pooled_chassis = sum(chassis_raws) / len(chassis_raws)
        pooled_ratio = pooled_chassis / pooled_full if pooled_full > 0 else math.inf
        weighted_violation = safety_num / safety_den if safety_den > 0 else 0.0
        gate_b_ok = weighted_violation <= GATE_B_WEIGHTED and high_violations == 0
        gate_c_ok = pooled_ratio <= GATE_C_POOLED and all(
            x["raw_ratio"] <= GATE_C_PER_MLP for x in per_mlp
        )
        flop_ratio = chassis_allin / full_allin
        measured_saving = full_allin - chassis_allin
        removed_share = removed_gemm / measured_saving if measured_saving > 0 else 0.0
        gate_d_ok = (
            flop_ratio <= GATE_D_FLOP_RATIO
            and removed_share >= GATE_D_REMOVED_SHARE
        )

        repeat_full = run_metered(mlps[0], chassis=False, budget=BUDGET)
        repeat_chassis = run_metered(mlps[0], chassis=True, budget=BUDGET)
        det_full, det_full_flops = determinism_metric(
            first_full_pred, repeat_full.prediction
        )
        det_chassis, det_chassis_flops = determinism_metric(
            first_chassis_pred, repeat_chassis.prediction
        )

        result.update(
            {
                "failures": 0,
                "gate_a": gate_a,
                "gate_a_pass": gate_a_ok,
                "weighted_sign_violation_mass": weighted_violation,
                "sign_violation_count": total_violations,
                "high_downstream_mass_violation_count": high_violations,
                "gate_b_pass": gate_b_ok,
                "pooled_full_raw_mse": pooled_full,
                "pooled_chassis_raw_mse": pooled_chassis,
                "pooled_raw_ratio": pooled_ratio,
                "gate_c_pass": gate_c_ok,
                "full_all_in_flops_4": full_allin,
                "chassis_all_in_flops_4": chassis_allin,
                "flops_ratio": flop_ratio,
                "measured_flops_saving": measured_saving,
                "removed_gemm_flops": removed_gemm,
                "removed_gemm_share_of_saving": removed_share,
                "gate_d_pass": gate_d_ok,
                "safety_audit_flops": safety_flops,
                "safety_audit_residual_s": safety_residual,
                "safety_audit_wall_s": safety_wall,
                "determinism_full_max_abs": det_full,
                "determinism_chassis_max_abs": det_chassis,
                "determinism_metric_flops": det_full_flops + det_chassis_flops,
                "repeat_full_predict_flops": repeat_full.flops,
                "repeat_chassis_predict_flops": repeat_chassis.flops,
                "per_mlp": per_mlp,
            }
        )
        result["falsifier_go"] = bool(
            gate_a_ok
            and gate_b_ok
            and gate_c_ok
            and gate_d_ok
            and det_full == 0.0
            and det_chassis == 0.0
        )
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)

    print("E062_CHASSIS_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    Path("e062-chassis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    if not result.get("falsifier_go", False):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
