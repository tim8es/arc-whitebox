#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
SEEDS = (238120, 238121, 238122, 238123)
WIDTH = 12
DEPTH = 10
AGE_OLD = 4
R_OLD = 8
AGE_OLD2 = 7
R_OLD2 = 6
QPASS2 = 2
FIRST_SCALE = 0.50
LATER_SCALE_FACTOR = 0.65
SECTOR_CAP = 200_000
TWO_PI = 2.0 * math.pi
ROOT_TOL = 2.0**-42
SECTOR_TOL = 1e-13

BUDGET = 2**41
PARENT_PROD_FLOPS = 806_303_721_965
PROD_EXTRA_UPPER = 9 * 2 * 1024 * 384
PROD_UPPER = PARENT_PROD_FLOPS + PROD_EXTRA_UPPER
PROD_BREAK_EVEN = PARENT_PROD_FLOPS / PROD_UPPER
SMALL_EXTRA_UPPER = 3 * 2 * WIDTH * R_OLD
POOLED_RATIO_GATE = 0.95
WORST_RATIO_GATE = 1.05

OLD_PATCH = """                    Om = fnp.copy(w32[:, :r_old])          # fixed sketch (n, r)
                    Qp = (w1c * Qc) if ka > 0 else None     # post-wick old basis
                    for _pass in range(QPASS):
"""

NEW_PATCH = """                    Om = fnp.copy(w32[:, :r_old])          # fixed sketch (n, r)
                    Qp = (w1c * Qc) if ka > 0 else None     # post-wick old basis
                    if ka > 0:
                        Om = Om + Qp                         # R238 RSRF: recycle prior old-source subspace
                    for _pass in range(QPASS):
"""


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def arr_sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot construct module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights: list[np.ndarray] = []
    w0 = np.zeros((WIDTH, WIDTH), dtype=np.float32)
    w0[:2, :] = (
        np.float32(FIRST_SCALE)
        * rng.standard_normal((2, WIDTH)).astype(np.float32)
    )
    weights.append(w0)
    scale = np.float32(LATER_SCALE_FACTOR * math.sqrt(2.0 / WIDTH))
    for _ in range(1, DEPTH):
        w = rng.standard_normal((WIDTH, WIDTH)).astype(np.float32)
        w *= scale
        weights.append(w)
    return weights


class _Ctx:
    def __init__(self, seed: int):
        self.seed = int(seed)


def configure_estimator(module) -> None:
    module.Estimator.AGE_OLD = AGE_OLD
    module.Estimator.R_OLD = R_OLD
    module.Estimator.AGE_OLD2 = AGE_OLD2
    module.Estimator.R_OLD2 = R_OLD2
    module.Estimator.QPASS2 = QPASS2


def run_estimator(module, weights: Sequence[np.ndarray], seed: int) -> tuple[np.ndarray, int]:
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench.domain import MLP

    configure_estimator(module)
    ws = [fnp.asarray(np.asarray(w, dtype=np.float32)) for w in weights]
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=ws, seed=int(seed))
    est = module.Estimator()
    est.setup(_Ctx(seed))
    with flops.BudgetContext(
        flop_budget=10**14,
        wall_time_limit_s=600.0,
        quiet=True,
    ) as ctx:
        pred = est.predict(mlp, BUDGET)
    return np.asarray(pred, dtype=np.float64), int(ctx.flops_used)


def construct_candidate(parent_path: Path, candidate_path: Path) -> dict:
    src = parent_path.read_text(encoding="utf-8")
    count = src.count(OLD_PATCH)
    if count != 1:
        raise RuntimeError(f"frozen patch source occurrence count={count}, expected 1")
    new_src = src.replace(OLD_PATCH, NEW_PATCH, 1)
    # Exact anti-drift assertion: deleting the frozen insertion must recover parent text.
    if new_src.replace(
        """                    if ka > 0:
                        Om = Om + Qp                         # R238 RSRF: recycle prior old-source subspace
""",
        "",
        1,
    ) != src:
        raise RuntimeError("candidate differs beyond frozen RSRF insertion")
    candidate_path.write_text(new_src, encoding="utf-8")
    return {
        "parent_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "candidate_sha256": hashlib.sha256(new_src.encode()).hexdigest(),
        "parent_git_blob": git_blob(parent_path),
        "candidate_git_blob": git_blob(candidate_path),
        "patch_occurrences": count,
    }


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    phi = math.atan2(b, a)
    base = phi + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + SECTOR_TOL < x < hi - SECTOR_TOL:
            out.append(float(x))
    return out


def _dedup(values: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(values):
        if not out or abs(x - out[-1]) > ROOT_TOL:
            out.append(x)
    return out


@dataclass
class Sector:
    lo: float
    hi: float
    coeff: np.ndarray


def _merge_adjacent(sectors: list[Sector]) -> list[Sector]:
    if not sectors:
        return sectors
    out = [sectors[0]]
    for sec in sectors[1:]:
        prev = out[-1]
        if (
            abs(prev.hi - sec.lo) <= ROOT_TOL
            and prev.coeff.shape == sec.coeff.shape
            and np.array_equal(prev.coeff, sec.coeff)
        ):
            out[-1] = Sector(prev.lo, sec.hi, prev.coeff)
        else:
            out.append(sec)
    return out


def exact_final_mean(weights: Sequence[np.ndarray]) -> tuple[np.ndarray, list[int]]:
    c0 = np.zeros((WIDTH, 2), dtype=np.float64)
    c0[0, 0] = 1.0
    c0[1, 1] = 1.0
    sectors = [Sector(0.0, TWO_PI, c0)]
    counts: list[int] = []

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        nxt: list[Sector] = []
        for sec in sectors:
            pre = w.T @ sec.coeff
            bounds = [sec.lo, sec.hi]
            for row in pre:
                bounds.extend(_roots(float(row[0]), float(row[1]), sec.lo, sec.hi))
            bounds = _dedup(bounds)
            for lo, hi in zip(bounds[:-1], bounds[1:]):
                if hi - lo <= SECTOR_TOL:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                coeff = pre.copy()
                coeff[(pre @ q) <= 0.0, :] = 0.0
                nxt.append(Sector(lo, hi, coeff))
        sectors = _merge_adjacent(nxt)
        counts.append(len(sectors))
        if len(sectors) > SECTOR_CAP:
            raise RuntimeError(f"exact sector cap exceeded: {len(sectors)}>{SECTOR_CAP}")

    angular = np.zeros(WIDTH, dtype=np.float64)
    for sec in sectors:
        integral_q = np.array(
            [
                math.sin(sec.hi) - math.sin(sec.lo),
                -math.cos(sec.hi) + math.cos(sec.lo),
            ],
            dtype=np.float64,
        )
        angular += sec.coeff @ integral_q
    mean_r = math.sqrt(math.pi / 2.0)
    return mean_r * angular / TWO_PI, counts


def mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def write_result(path: Path, result: dict) -> None:
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v25", type=Path, required=True)
    ap.add_argument("--candidate-out", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    blob = git_blob(args.v25)
    if blob != EXPECTED_V25_BLOB:
        result = {
            "schema": "arc.whitebox.r238.rsrf_exact_small.v1",
            "job_id": "R238",
            "decision": "R238_BASE_INCONCLUSIVE",
            "base_executable": False,
            "candidate_constructed": False,
            "error": f"pinned V25 blob mismatch: {blob}",
            "pinned_v25_blob": blob,
        }
        write_result(args.out, result)
        return 20

    parent_module = load_module(args.v25, "r238_pinned_v25_parent")
    frozen: list[dict] = []

    # Mandatory prerequisite: run the unchanged pinned source first on every fixture.
    try:
        for seed in SEEDS:
            weights = make_weights(seed)
            parent, parent_flops = run_estimator(parent_module, weights, seed + 10000)
            if not np.isfinite(parent).all():
                raise RuntimeError(f"parent non-finite on seed {seed}")
            frozen.append(
                {
                    "seed": seed,
                    "weights": weights,
                    "parent": parent,
                    "parent_flops": parent_flops,
                    "parent_sha256": arr_sha(parent),
                }
            )
    except Exception as exc:
        result = {
            "schema": "arc.whitebox.r238.rsrf_exact_small.v1",
            "job_id": "R238",
            "family": "RSRF-V25 recycled-start range finder",
            "decision": "R238_BASE_INCONCLUSIVE",
            "base_executable": False,
            "candidate_constructed": False,
            "pinned_v25_blob": blob,
            "configuration": {
                "width": WIDTH,
                "depth": DEPTH,
                "seeds": list(SEEDS),
                "age_old": AGE_OLD,
                "r_old": R_OLD,
                "age_old2": AGE_OLD2,
                "r_old2": R_OLD2,
                "qpass2": QPASS2,
                "first_scale": FIRST_SCALE,
                "later_scale_factor": LATER_SCALE_FACTOR,
            },
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            "scope": {
                "synthetic_only": True,
                "candidate_executed": False,
                "candidate_constructed": False,
                "mini100_authorized": False,
                "benchmark_data": False,
                "holdout": False,
                "submission": False,
                "paid_compute": False,
                "canonical_v25_mutated": False,
            },
        }
        write_result(args.out, result)
        print("R238_BASE=" + json.dumps(result, sort_keys=True), flush=True)
        return 20

    # Only after every base fixture executed do we construct the candidate.
    patch = construct_candidate(args.v25, args.candidate_out)
    candidate_module = load_module(args.candidate_out, "r238_rsrf_v25_candidate")

    integrity_ok = True
    candidate_frozen: list[dict] = []
    try:
        for item in frozen:
            seed = item["seed"]
            weights = item["weights"]
            cand, cand_flops = run_estimator(candidate_module, weights, seed + 20000)
            cand2, cand_flops2 = run_estimator(candidate_module, weights, seed + 20000)
            replay = np.array_equal(cand, cand2) and cand_flops == cand_flops2
            finite = bool(np.isfinite(cand).all() and np.isfinite(cand2).all())
            integrity_ok = integrity_ok and replay and finite
            candidate_frozen.append(
                {
                    **item,
                    "candidate": cand,
                    "candidate_flops": cand_flops,
                    "candidate_sha256": arr_sha(cand),
                    "candidate_replay_sha256": arr_sha(cand2),
                    "candidate_replay_bitwise": replay,
                    "candidate_finite": finite,
                }
            )
    except Exception as exc:
        result = {
            "schema": "arc.whitebox.r238.rsrf_exact_small.v1",
            "job_id": "R238",
            "family": "RSRF-V25 recycled-start range finder",
            "decision": "R238_SMALL_INTEGRITY_FAIL",
            "base_executable": True,
            "candidate_constructed": True,
            "pinned_v25_blob": blob,
            "patch": patch,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            "scope": {
                "synthetic_only": True,
                "mini100_authorized": False,
                "benchmark_data": False,
                "holdout": False,
                "submission": False,
                "paid_compute": False,
                "canonical_v25_mutated": False,
            },
        }
        write_result(args.out, result)
        print("R238_CANDIDATE_ERROR=" + json.dumps(result, sort_keys=True), flush=True)
        return 21

    # Exact truth is constructed only after all candidate arrays are frozen.
    records: list[dict] = []
    try:
        for item in candidate_frozen:
            exact, sector_counts = exact_final_mean(item["weights"])
            parent_final = item["parent"][-1]
            cand_final = item["candidate"][-1]
            pm = mse(parent_final, exact)
            cm = mse(cand_final, exact)
            ratio = cm / pm if pm > 0.0 else math.inf
            records.append(
                {
                    "seed": item["seed"],
                    "parent_sha256": item["parent_sha256"],
                    "candidate_sha256": item["candidate_sha256"],
                    "candidate_replay_sha256": item["candidate_replay_sha256"],
                    "exact_sha256": arr_sha(exact),
                    "parent_mse": pm,
                    "candidate_mse": cm,
                    "candidate_over_parent": ratio,
                    "candidate_beats_parent": bool(cm < pm),
                    "parent_candidate_final_rms": float(np.sqrt(np.mean((parent_final - cand_final) ** 2))),
                    "parent_flops_small": item["parent_flops"],
                    "candidate_flops_small": item["candidate_flops"],
                    "flop_delta_small": item["candidate_flops"] - item["parent_flops"],
                    "candidate_replay_bitwise": item["candidate_replay_bitwise"],
                    "candidate_finite": item["candidate_finite"],
                    "sector_counts": sector_counts,
                    "final_sector_count": sector_counts[-1],
                }
            )
    except Exception as exc:
        result = {
            "schema": "arc.whitebox.r238.rsrf_exact_small.v1",
            "job_id": "R238",
            "family": "RSRF-V25 recycled-start range finder",
            "decision": "R238_SMALL_INTEGRITY_FAIL",
            "base_executable": True,
            "candidate_constructed": True,
            "pinned_v25_blob": blob,
            "patch": patch,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            "scope": {
                "synthetic_only": True,
                "mini100_authorized": False,
                "benchmark_data": False,
                "holdout": False,
                "submission": False,
                "paid_compute": False,
                "canonical_v25_mutated": False,
            },
        }
        write_result(args.out, result)
        return 21

    pooled_parent = float(np.mean([r["parent_mse"] for r in records]))
    pooled_candidate = float(np.mean([r["candidate_mse"] for r in records]))
    pooled_ratio = pooled_candidate / pooled_parent if pooled_parent > 0 else math.inf
    wins = int(sum(r["candidate_beats_parent"] for r in records))
    worst_ratio = float(max(r["candidate_over_parent"] for r in records))
    differs = int(sum(r["parent_candidate_final_rms"] > 0.0 for r in records))
    max_sectors = int(max(r["final_sector_count"] for r in records))
    deltas = [int(r["flop_delta_small"]) for r in records]

    gates = {
        "pinned_v25_blob_exact": blob == EXPECTED_V25_BLOB,
        "base_executable_all": True,
        "candidate_patch_once": patch["patch_occurrences"] == 1,
        "candidate_finite_all": all(r["candidate_finite"] for r in records),
        "candidate_bitwise_replay_all": all(r["candidate_replay_bitwise"] for r in records),
        "exact_reference_finite_all": all(
            math.isfinite(r["parent_mse"]) and math.isfinite(r["candidate_mse"]) for r in records
        ),
        "sector_cap_respected": max_sectors <= SECTOR_CAP,
        "candidate_differs_ge_3_of_4": differs >= 3,
        "pooled_candidate_over_parent_le_0_95": pooled_ratio <= POOLED_RATIO_GATE,
        "candidate_wins_ge_3_of_4": wins >= 3,
        "worst_candidate_over_parent_le_1_05": worst_ratio <= WORST_RATIO_GATE,
        "small_flop_delta_nonnegative_all": all(d >= 0 for d in deltas),
        "small_flop_delta_le_576_all": all(d <= SMALL_EXTRA_UPPER for d in deltas),
        "production_formula_exact": PROD_UPPER == 806_310_799_853,
        "production_under_budget": PROD_UPPER < BUDGET,
        "pooled_ratio_below_adjusted_break_even": pooled_ratio < PROD_BREAK_EVEN,
        "target_free_scope": True,
    }
    integrity_keys = [
        "pinned_v25_blob_exact",
        "base_executable_all",
        "candidate_patch_once",
        "candidate_finite_all",
        "candidate_bitwise_replay_all",
        "exact_reference_finite_all",
        "sector_cap_respected",
        "candidate_differs_ge_3_of_4",
        "small_flop_delta_nonnegative_all",
        "small_flop_delta_le_576_all",
        "production_formula_exact",
        "production_under_budget",
        "target_free_scope",
    ]
    science_keys = [
        "pooled_candidate_over_parent_le_0_95",
        "candidate_wins_ge_3_of_4",
        "worst_candidate_over_parent_le_1_05",
        "pooled_ratio_below_adjusted_break_even",
    ]
    integrity_go = all(gates[k] for k in integrity_keys)
    science_go = integrity_go and all(gates[k] for k in science_keys)
    decision = "R238_SMALL_GO_RSRF" if science_go else "R238_SMALL_NO_GO_RSRF"

    result = {
        "schema": "arc.whitebox.r238.rsrf_exact_small.v1",
        "job_id": "R238",
        "family": "RSRF-V25 recycled-start range finder",
        "decision": decision,
        "base_executable": True,
        "candidate_constructed": True,
        "pinned_v25_blob": blob,
        "patch": patch,
        "configuration": {
            "width": WIDTH,
            "depth": DEPTH,
            "seeds": list(SEEDS),
            "age_old": AGE_OLD,
            "r_old": R_OLD,
            "age_old2": AGE_OLD2,
            "r_old2": R_OLD2,
            "qpass2": QPASS2,
            "first_scale": FIRST_SCALE,
            "later_scale_factor": LATER_SCALE_FACTOR,
            "sector_cap": SECTOR_CAP,
        },
        "records": records,
        "summary": {
            "pooled_parent_mse": pooled_parent,
            "pooled_candidate_mse": pooled_candidate,
            "pooled_candidate_over_parent": pooled_ratio,
            "candidate_wins": wins,
            "candidate_differs": differs,
            "worst_candidate_over_parent": worst_ratio,
            "max_final_sector_count": max_sectors,
            "small_flop_deltas": deltas,
            "small_extra_upper": SMALL_EXTRA_UPPER,
            "production_parent_flops": PARENT_PROD_FLOPS,
            "production_extra_upper": PROD_EXTRA_UPPER,
            "production_all_in_upper": PROD_UPPER,
            "production_utilization_upper": PROD_UPPER / BUDGET,
            "raw_mse_break_even_ratio": PROD_BREAK_EVEN,
            "projected_adjusted_ratio_from_small": pooled_ratio * (PROD_UPPER / PARENT_PROD_FLOPS),
        },
        "gates": gates,
        "integrity_go": bool(integrity_go),
        "scientific_go": bool(science_go),
        "scope": {
            "synthetic_only": True,
            "benchmark_data": False,
            "public_mini": False,
            "scorer": False,
            "holdout": False,
            "submission": False,
            "target_fit": False,
            "paid_compute": False,
            "canonical_v25_mutated": False,
            "mini100_authorized": bool(science_go),
        },
    }
    write_result(args.out, result)
    print("R238_RSRF=" + json.dumps(result, sort_keys=True), flush=True)
    return 0 if integrity_go else 21


if __name__ == "__main__":
    raise SystemExit(main())
