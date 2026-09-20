#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import types

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp
from whestbench.domain import MLP

from methods.e137_h137_countsketch import (
    BUDGET,
    D21_REL_GATE,
    H137Hook,
    PINNED_V25_GIT_BLOB,
    WIDTH,
    git_blob_sha1_bytes,
    patch_v25_source,
    summarize_records,
)

DEPTH = 16
MLP_SEEDS = (137200, 137201)
SETUP_SEED = 137137
V25_PATH = Path("vendor/e137_estimator_v25_pinned.py")
OUT = Path("e137-h137-stagea-countsketch.json")


class _Ctx:
    seed = SETUP_SEED


def _prediction_sha256(pred) -> str:
    a = np.asarray(pred, dtype=np.float32)
    return hashlib.sha256(a.tobytes(order="C")).hexdigest()


def _load_instrumented_v25(hook: H137Hook):
    raw = V25_PATH.read_bytes()
    blob = git_blob_sha1_bytes(raw)
    if blob != PINNED_V25_GIT_BLOB:
        raise RuntimeError(f"pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")
    patched = patch_v25_source(source)
    module = types.ModuleType("e137_instrumented_v25")
    module.__file__ = str(V25_PATH)
    module.__dict__["E137_HOOK"] = hook
    exec(compile(patched, str(V25_PATH), "exec"), module.__dict__)
    return module, blob


def _build_mlp(seed: int) -> MLP:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    scale = math.sqrt(2.0 / WIDTH)
    weights = [
        fnp.asarray((rng.standard_normal((WIDTH, WIDTH)) * scale).astype(np.float32))
        for _ in range(DEPTH)
    ]
    return MLP(width=WIDTH, depth=DEPTH, weights=weights, seed=0)


def _run_one(seed: int) -> tuple[dict, list]:
    hook = H137Hook()
    mod, blob = _load_instrumented_v25(hook)
    est = mod.Estimator()
    est.setup(_Ctx())
    mlp = _build_mlp(seed)

    with flops.BudgetContext(
        flop_budget=int(1e14),
        wall_time_limit_s=1200.0,
        quiet=True,
    ) as ctx:
        pred = est.predict(mlp, int(BUDGET))

    baseline_flops = int(ctx.flops_used)
    exact_namespace_flops = int(
        round(
            sum(
                float(r.flop_cost)
                for r in ctx.op_log
                if r.namespace and r.namespace.split(".")[-1] == "e137_old_exact"
            )
        )
    )

    summ = summarize_records(hook.records)
    sketch_upper = int(summ["sketch_contract_upper_flops"])
    exact_formula = int(summ["exact_contract_formula_flops"])
    candidate_flops = baseline_flops - exact_namespace_flops + sketch_upper

    records = [
        {
            "layer": r.layer,
            "ka": r.ka,
            "kb": r.kb,
            "factor_relative_error": r.factor_rel_error,
            "lifted_relative_error": r.lifted_rel_error,
            "exact_norm_sq": r.exact_norm_sq,
            "error_norm_sq": r.error_norm_sq,
            "exact_contract_formula_flops": r.exact_contract_formula_flops,
            "sketch_contract_upper_flops": r.sketch_contract_upper_flops,
        }
        for r in hook.records
    ]

    result = {
        "seed": seed,
        "pinned_v25_blob": blob,
        "prediction_sha256_no_target_scoring": _prediction_sha256(pred),
        "measurement_count": int(summ["measurement_count"]),
        "pooled_relative_d21_error": float(summ["pooled_relative_d21_error"]),
        "max_layer_relative_d21_error": float(summ["max_layer_relative_d21_error"]),
        "max_factor_vs_lifted_rel_error_gap": float(
            summ["max_factor_vs_lifted_rel_error_gap"]
        ),
        "baseline_measured_all_in_flops": baseline_flops,
        "baseline_measured_utilization": baseline_flops / BUDGET,
        "measured_exact_old_contract_flops": exact_namespace_flops,
        "formula_exact_old_contract_flops": exact_formula,
        "exact_formula_over_measured_namespace": (
            exact_formula / exact_namespace_flops if exact_namespace_flops else None
        ),
        "countsketch_old_contract_upper_flops": sketch_upper,
        "candidate_projected_all_in_flops": candidate_flops,
        "candidate_projected_utilization": candidate_flops / BUDGET,
        "projected_flop_savings": baseline_flops - candidate_flops,
        "projected_savings_fraction_of_baseline": (
            (baseline_flops - candidate_flops) / baseline_flops
        ),
        "finite": bool(
            summ["finite"]
            and np.isfinite(np.asarray(pred, dtype=np.float64)).all()
            and math.isfinite(candidate_flops)
        ),
        "records": records,
    }
    return result, hook.records


def _one_pass() -> dict:
    per_mlp = []
    all_records = []
    for seed in MLP_SEEDS:
        rec, layers = _run_one(seed)
        per_mlp.append(rec)
        all_records.extend(layers)

    pooled = summarize_records(all_records)
    candidate_flops = [int(r["candidate_projected_all_in_flops"]) for r in per_mlp]
    baseline_flops = [int(r["baseline_measured_all_in_flops"]) for r in per_mlp]

    gates = {
        "pinned_v25_blob_identity": all(
            r["pinned_v25_blob"] == PINNED_V25_GIT_BLOB for r in per_mlp
        ),
        "all_finite": all(bool(r["finite"]) for r in per_mlp),
        "old_tier_measurement_each_mlp": all(r["measurement_count"] > 0 for r in per_mlp),
        "pooled_relative_d21_error_le_0_022": (
            float(pooled["pooled_relative_d21_error"]) <= D21_REL_GATE
        ),
        "candidate_all_in_strictly_below_v25": all(
            c < b for c, b in zip(candidate_flops, baseline_flops)
        ),
        "candidate_all_in_within_budget": all(c <= BUDGET for c in candidate_flops),
        "factor_vs_lifted_error_gap_le_1e_5": (
            float(pooled["max_factor_vs_lifted_rel_error_gap"]) <= 1e-5
        ),
        "no_target_reference_scorer_access": True,
    }
    scientific_go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e137.h137.stagea.countsketch.v1",
        "experiment": "E137-H137-STAGEA",
        "idempotency_key": "ARC-E137-H137-STAGEA-COUNTSKETCH-S512-20260921",
        "mechanism": {
            "name": "old-tier CountSketch contraction patch",
            "sketch_width": 512,
            "width": WIDTH,
            "hash": "balanced PCG64 permutation, two original columns per bucket",
            "signs": "PCG64 Rademacher per original column",
            "seed_rule": "137512000 + V25 source-count/layer index",
            "baseline_state_evolution_uses_exact_v25": True,
            "final_mse_validation_performed": False,
        },
        "corpus": {
            "kind": "synthetic official-shape target-free",
            "width": WIDTH,
            "depth": DEPTH,
            "weight_law": "PCG64 iid N(0,2/1024), float32",
            "mlp_seeds": list(MLP_SEEDS),
            "setup_seed": SETUP_SEED,
            "benchmark_weights": False,
            "targets": False,
        },
        "per_mlp": per_mlp,
        "pooled": {
            "measurement_count": int(pooled["measurement_count"]),
            "relative_d21_error": float(pooled["pooled_relative_d21_error"]),
            "relative_d21_error_gate": D21_REL_GATE,
            "max_layer_relative_d21_error": float(
                pooled["max_layer_relative_d21_error"]
            ),
            "max_factor_vs_lifted_rel_error_gap": float(
                pooled["max_factor_vs_lifted_rel_error_gap"]
            ),
            "max_candidate_projected_all_in_flops": max(candidate_flops),
            "max_candidate_projected_utilization": max(candidate_flops) / BUDGET,
            "mean_baseline_measured_all_in_flops": float(np.mean(baseline_flops)),
            "mean_candidate_projected_all_in_flops": float(np.mean(candidate_flops)),
            "mean_projected_flop_savings": float(
                np.mean([b - c for b, c in zip(baseline_flops, candidate_flops)])
            ),
        },
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "H137_STAGEA_GO_FINAL_MSE_VALIDATION_AUTHORIZED"
            if scientific_go
            else "TERMINAL_NO_GO_CLOSE_H137_COUNTSKETCH_S512"
        ),
        "scope": {
            "target_free": True,
            "final_mse_validation": False,
            "public_dataset": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def main() -> None:
    first = _one_pass()
    second = _one_pass()

    a = json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    b = json.dumps(second, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    deterministic = a == b

    first["deterministic_replay"] = {
        "bitwise_json_equal": deterministic,
        "first_sha256": hashlib.sha256(a).hexdigest(),
        "second_sha256": hashlib.sha256(b).hexdigest(),
    }

    if not deterministic:
        first["scientific_go"] = False
        first["gates"]["deterministic_replay_bitwise_exact"] = False
        first["decision"] = "TERMINAL_NO_GO_CLOSE_H137_COUNTSKETCH_S512"
    else:
        first["gates"]["deterministic_replay_bitwise_exact"] = True

    OUT.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E137_H137_STAGEA=" + json.dumps(first, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
