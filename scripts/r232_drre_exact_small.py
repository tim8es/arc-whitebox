#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
SEEDS = (232900, 232901, 232902, 232903)
WIDTH = 9
DEPTH = 10
R_OLD = 8
R_HIGH = 7
R_LOW = 6
AGE_OLD = 4
AGE_OLD2 = 7
GAMMA = 36.0 / 13.0
BUDGET = 2**41
PARENT_FLOPS = 806_303_721_965
COMBINE_FLOPS = 3 * 16 * 1024
PROD_UPPER = 2 * PARENT_FLOPS + COMBINE_FLOPS
SMALL_RATIO_GATE = 0.45
SECTOR_CAP = 200_000
TWO_PI = 2.0 * math.pi
ROOT_TOL = 2.0**-42
SECTOR_TOL = 1e-13


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def arr_sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_v25(path: Path):
    spec = importlib.util.spec_from_file_location("r232_pinned_v25", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot construct V25 module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights: list[np.ndarray] = []
    w0 = np.zeros((WIDTH, WIDTH), dtype=np.float32)
    # Only two Gaussian input coordinates are live, but every output coordinate is active.
    w0[:2, :] = rng.standard_normal((2, WIDTH)).astype(np.float32)
    weights.append(w0)
    scale = math.sqrt(2.0 / WIDTH)
    for _ in range(1, DEPTH):
        w = rng.standard_normal((WIDTH, WIDTH)).astype(np.float32)
        w *= np.float32(scale)
        weights.append(w)
    return weights


class _Ctx:
    def __init__(self, seed: int):
        self.seed = int(seed)


def run_v25(module, weights: Sequence[np.ndarray], r_old2: int, seed: int) -> tuple[np.ndarray, int]:
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench.domain import MLP

    module.Estimator.AGE_OLD = AGE_OLD
    module.Estimator.R_OLD = R_OLD
    module.Estimator.AGE_OLD2 = AGE_OLD2
    module.Estimator.R_OLD2 = int(r_old2)
    module.Estimator.QPASS2 = 2

    ws = [fnp.asarray(np.asarray(w, dtype=np.float32)) for w in weights]
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=ws, seed=int(seed))
    est = module.Estimator()
    est.setup(_Ctx(seed))
    with flops.BudgetContext(
        flop_budget=10**14,
        wall_time_limit_s=600.0,
        quiet=True,
    ) as ctx:
        pred = est.predict(mlp, 2**41)
    return np.asarray(pred, dtype=np.float64), int(ctx.flops_used)


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
    # Input X~N(0,I_WIDTH), but weights depend only on X0,X1.  coeff maps q in R2
    # to the live input vector.
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v25", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("r232-drre-falsifier.json"))
    args = ap.parse_args()

    blob = git_blob(args.v25)
    identity_ok = blob == EXPECTED_V25_BLOB
    if not identity_ok:
        raise SystemExit(f"pinned V25 blob mismatch: {blob}")

    module = load_v25(args.v25)
    records = []
    replay_all = True
    finite_all = True
    nonidentical_all = True

    # Candidate is fully constructed/frozen before exact truth for every fixture.
    frozen = []
    for seed in SEEDS:
        weights = make_weights(seed)
        high, fh = run_v25(module, weights, R_HIGH, seed + 10000)
        low, fl = run_v25(module, weights, R_LOW, seed + 20000)
        drre = high + GAMMA * (high - low)

        high2, _ = run_v25(module, weights, R_HIGH, seed + 10000)
        low2, _ = run_v25(module, weights, R_LOW, seed + 20000)
        drre2 = high2 + GAMMA * (high2 - low2)

        replay = (
            np.array_equal(high, high2)
            and np.array_equal(low, low2)
            and np.array_equal(drre, drre2)
        )
        finite = bool(
            np.isfinite(high).all()
            and np.isfinite(low).all()
            and np.isfinite(drre).all()
        )
        nonidentical = not np.array_equal(high, low)
        replay_all = replay_all and replay
        finite_all = finite_all and finite
        nonidentical_all = nonidentical_all and nonidentical

        frozen.append(
            {
                "seed": seed,
                "weights": weights,
                "high": high,
                "low": low,
                "drre": drre,
                "high_flops_small": fh,
                "low_flops_small": fl,
                "replay": replay,
                "finite": finite,
                "nonidentical": nonidentical,
                "high_sha256": arr_sha(high),
                "low_sha256": arr_sha(low),
                "drre_sha256": arr_sha(drre),
            }
        )

    # Verifier-only exact truth appears only after all candidate arrays are frozen.
    for item in frozen:
        exact, sector_counts = exact_final_mean(item["weights"])
        high_final = item["high"][-1]
        low_final = item["low"][-1]
        drre_final = item["drre"][-1]
        hm = mse(high_final, exact)
        lm = mse(low_final, exact)
        dm = mse(drre_final, exact)
        ratio = dm / hm if hm > 0.0 else math.inf
        records.append(
            {
                "seed": item["seed"],
                "exact_sha256": arr_sha(exact),
                "high_sha256": item["high_sha256"],
                "low_sha256": item["low_sha256"],
                "drre_sha256": item["drre_sha256"],
                "high_mse": hm,
                "low_mse": lm,
                "drre_mse": dm,
                "drre_over_high": ratio,
                "drre_beats_high": bool(dm < hm),
                "high_low_final_rms": float(
                    np.sqrt(np.mean((high_final - low_final) ** 2))
                ),
                "sector_counts": sector_counts,
                "final_sector_count": sector_counts[-1],
                "replay_bitwise_exact": item["replay"],
                "candidate_finite": item["finite"],
                "high_low_nonidentical": item["nonidentical"],
                "high_flops_small": item["high_flops_small"],
                "low_flops_small": item["low_flops_small"],
            }
        )

    pooled_high = float(np.mean([r["high_mse"] for r in records]))
    pooled_drre = float(np.mean([r["drre_mse"] for r in records]))
    pooled_ratio = pooled_drre / pooled_high if pooled_high > 0.0 else math.inf
    wins = int(sum(r["drre_beats_high"] for r in records))
    worst_ratio = float(max(r["drre_over_high"] for r in records))
    max_sectors = int(max(r["final_sector_count"] for r in records))

    prod_util = PROD_UPPER / BUDGET
    break_even = PARENT_FLOPS / PROD_UPPER
    projected_adjusted_ratio = pooled_ratio * (PROD_UPPER / PARENT_FLOPS)

    gates = {
        "pinned_v25_blob_exact": identity_ok,
        "candidate_finite_all": finite_all,
        "bitwise_replay_all": replay_all,
        "exact_reference_finite_all": bool(
            all(math.isfinite(r["high_mse"]) and math.isfinite(r["drre_mse"]) for r in records)
        ),
        "sector_cap_respected": max_sectors <= SECTOR_CAP,
        "high_low_nonidentical_all": nonidentical_all,
        "target_free_scope": True,
        "pooled_drre_over_high_le_0_45": pooled_ratio <= SMALL_RATIO_GATE,
        "drre_wins_ge_3_of_4": wins >= 3,
        "worst_drre_over_high_le_0_80": worst_ratio <= 0.80,
        "production_formula_exact": PROD_UPPER == 1_612_607_493_082,
        "production_under_budget": PROD_UPPER < BUDGET,
        "pooled_ratio_below_adjusted_break_even": pooled_ratio < break_even,
    }
    integrity_keys = [
        "pinned_v25_blob_exact",
        "candidate_finite_all",
        "bitwise_replay_all",
        "exact_reference_finite_all",
        "sector_cap_respected",
        "high_low_nonidentical_all",
        "target_free_scope",
        "production_formula_exact",
        "production_under_budget",
    ]
    scientific_keys = [
        "pooled_drre_over_high_le_0_45",
        "drre_wins_ge_3_of_4",
        "worst_drre_over_high_le_0_80",
        "pooled_ratio_below_adjusted_break_even",
    ]
    integrity_go = all(gates[k] for k in integrity_keys)
    scientific_go = integrity_go and all(gates[k] for k in scientific_keys)

    result = {
        "schema": "arc.whitebox.r232.drre_exact_small.v1",
        "job_id": "R232",
        "family": "dual-resolution Richardson debiasing of deterministic V25 source compression",
        "pinned_v25_blob": blob,
        "configuration": {
            "width": WIDTH,
            "depth": DEPTH,
            "seeds": list(SEEDS),
            "r_old": R_OLD,
            "r_high": R_HIGH,
            "r_low": R_LOW,
            "age_old": AGE_OLD,
            "age_old2": AGE_OLD2,
            "gamma": GAMMA,
            "bias_exponent": 2,
            "sector_cap": SECTOR_CAP,
        },
        "records": records,
        "summary": {
            "pooled_high_mse": pooled_high,
            "pooled_drre_mse": pooled_drre,
            "pooled_drre_over_high": pooled_ratio,
            "wins": wins,
            "worst_drre_over_high": worst_ratio,
            "max_final_sector_count": max_sectors,
            "production_all_in_upper": PROD_UPPER,
            "production_utilization_upper": prod_util,
            "raw_mse_break_even_ratio": break_even,
            "projected_adjusted_ratio_from_small": projected_adjusted_ratio,
        },
        "gates": gates,
        "integrity_go": bool(integrity_go),
        "scientific_go": bool(scientific_go),
        "decision": (
            "R232_SMALL_GO_DRRE"
            if scientific_go
            else "R232_TERMINAL_NO_GO_DRRE"
        ),
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
            "mini100_authorized": bool(scientific_go),
        },
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R232_DRRE=" + json.dumps(result, sort_keys=True), flush=True)

    if not integrity_go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
