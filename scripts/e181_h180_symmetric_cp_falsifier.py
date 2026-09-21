#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

SEED = 181180
N_PROD = 1024
R_PROD = 3072
BUDGET = 2**41
UNIT = 2**31
CAP_RATIO = 0.135
NO_OLD_PARENT_U = 153.0
MIN_SAVING_U = 14.76
D21_GATE = 0.015
EXACT_TOL = 1e-12


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def array_sha256(a: np.ndarray) -> str:
    b = np.ascontiguousarray(a)
    header = f"{b.dtype.str}|{b.shape}|C|".encode()
    return sha256_bytes(header + b.tobytes(order="C"))


def general_d3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.sum(a * b * c, axis=1)


def general_d21(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    d21 = ((a * b) @ c.T + (a * c) @ b.T + (b * c) @ a.T) / 3.0
    np.fill_diagonal(d21, 0.0)
    return d21


def cp_d3(u: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.sum((u * u * u) * lam[None, :], axis=1)


def cp_d21(u: np.ndarray, lam: np.ndarray) -> np.ndarray:
    left = (u * u) * lam[None, :]
    d21 = left @ u.T
    np.fill_diagonal(d21, 0.0)
    return d21


def polarize(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    j = a.shape[1]
    u = np.concatenate(
        [a + b + c, a + b - c, a - b + c, -a + b + c], axis=1
    )
    one = np.full(j, 1.0 / 24.0, dtype=np.float64)
    lam = np.concatenate([one, -one, -one, -one])
    return u, lam


def prune_energy(u: np.ndarray, lam: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if u.shape[1] <= rank:
        idx = np.arange(u.shape[1], dtype=np.int64)
        return np.array(u, copy=True), np.array(lam, copy=True), idx
    norms = np.sqrt(np.sum(u * u, axis=0))
    score = np.abs(lam) * norms * norms * norms
    order = np.argsort(-score, kind="stable")
    idx = order[:rank]
    return np.ascontiguousarray(u[:, idx]), np.ascontiguousarray(lam[idx]), idx


def dense_general(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    terms = (
        np.einsum("ir,jr,kr->ijk", a, b, c, optimize=True)
        + np.einsum("ir,jr,kr->ijk", a, c, b, optimize=True)
        + np.einsum("ir,jr,kr->ijk", b, a, c, optimize=True)
        + np.einsum("ir,jr,kr->ijk", b, c, a, optimize=True)
        + np.einsum("ir,jr,kr->ijk", c, a, b, optimize=True)
        + np.einsum("ir,jr,kr->ijk", c, b, a, optimize=True)
    )
    return terms / 6.0


def dense_cp(u: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.einsum("r,ir,jr,kr->ijk", lam, u, u, u, optimize=True)


def relerr(a: np.ndarray, b: np.ndarray) -> float:
    den = max(float(np.max(np.abs(b))), 1e-300)
    return float(np.max(np.abs(a - b)) / den)


def rms(a: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(a, dtype=np.float64), dtype=np.float64)))


def exact_small() -> dict:
    rng = np.random.default_rng(SEED + 1)
    n, j = 5, 7
    a = rng.standard_normal((n, j)) / math.sqrt(n)
    b = rng.standard_normal((n, j)) / math.sqrt(n)
    c = rng.standard_normal((n, j)) / math.sqrt(n)
    u, lam = polarize(a, b, c)

    t_parent = dense_general(a, b, c)
    t_cp = dense_cp(u, lam)
    d3_parent = np.einsum("iii->i", t_parent)
    d3_formula = general_d3(a, b, c)
    d3_cp = cp_d3(u, lam)
    d21_dense = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for k in range(n):
            d21_dense[i, k] = 0.0 if i == k else t_parent[i, i, k]
    d21_parent = general_d21(a, b, c)
    d21_cp = cp_d21(u, lam)

    w = rng.standard_normal((n, n)) / math.sqrt(n)
    at, bt, ct = w @ a, w @ b, w @ c
    ut = w @ u
    t_transport_factors = dense_general(at, bt, ct)
    t_transport_cp = dense_cp(ut, lam)
    t_transport_direct = np.einsum("ai,bj,ck,ijk->abc", w, w, w, t_parent, optimize=True)

    metrics = {
        "tensor_polarization_relmax": relerr(t_cp, t_parent),
        "d3_dense_formula_relmax": relerr(d3_formula, d3_parent),
        "d3_cp_relmax": relerr(d3_cp, d3_parent),
        "d21_dense_formula_relmax": relerr(d21_parent, d21_dense),
        "d21_cp_relmax": relerr(d21_cp, d21_dense),
        "transport_parent_relmax": relerr(t_transport_factors, t_transport_direct),
        "transport_cp_relmax": relerr(t_transport_cp, t_transport_direct),
    }
    metrics["max_rel_error"] = max(metrics.values())
    metrics["pass"] = bool(metrics["max_rel_error"] <= EXACT_TOL)
    return metrics


def make_factors(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Dense correlated factor triples: target-free, estimator-state-like, rank J=n.
    s = 1.0 / math.sqrt(n)
    z0 = rng.standard_normal((n, n)) * s
    z1 = rng.standard_normal((n, n)) * s
    z2 = rng.standard_normal((n, n)) * s
    a = z0
    b = 0.55 * z0 + math.sqrt(1.0 - 0.55**2) * z1
    c = 0.35 * z0 + 0.25 * z1 + math.sqrt(1.0 - 0.35**2 - 0.25**2) * z2
    rs1 = 0.55 + 0.35 * rng.random(n)
    rs2 = 0.60 + 0.30 * rng.random(n)
    a = rs1[:, None] * a
    b = rs2[:, None] * b
    return np.ascontiguousarray(a), np.ascontiguousarray(b), np.ascontiguousarray(c)


def candidate_path(
    a0: np.ndarray,
    b0: np.ndarray,
    c0: np.ndarray,
    w: np.ndarray,
    wick: np.ndarray,
    a1: np.ndarray,
    b1: np.ndarray,
    c1: np.ndarray,
    rank: int,
) -> tuple[np.ndarray, np.ndarray, dict]:
    u0, l0 = polarize(a0, b0, c0)
    u, lam, idx0 = prune_energy(u0, l0, rank)
    stage0_d21 = cp_d21(u, lam)
    stage0_d3 = cp_d3(u, lam)

    u = w @ u
    u *= wick[:, None]
    u1, l1 = polarize(a1, b1, c1)
    u = np.concatenate([u, u1], axis=1)
    lam = np.concatenate([lam, l1])
    u, lam, idx1 = prune_energy(u, lam, rank)
    stage1_d21 = cp_d21(u, lam)
    stage1_d3 = cp_d3(u, lam)
    meta = {
        "stage0_kept": int(idx0.size),
        "stage1_kept": int(idx1.size),
        "stage0_input_terms": int(u0.shape[1]),
        "stage1_input_terms": int(rank + u1.shape[1]),
    }
    return stage1_d21, stage1_d3, {"stage0_d21": stage0_d21, "stage0_d3": stage0_d3, **meta}


def structural_run(n: int, rank: int) -> dict:
    rng = np.random.default_rng(SEED)
    a0, b0, c0 = make_factors(rng, n)
    a1, b1, c1 = make_factors(rng, n)
    w = rng.standard_normal((n, n)) / math.sqrt(n)
    wick = 0.55 + 0.35 * rng.random(n)

    p0_d21 = general_d21(a0, b0, c0)
    p0_d3 = general_d3(a0, b0, c0)

    a0t = (w @ a0) * wick[:, None]
    b0t = (w @ b0) * wick[:, None]
    c0t = (w @ c0) * wick[:, None]
    p1_d21 = general_d21(a0t, b0t, c0t) + general_d21(a1, b1, c1)
    p1_d3 = general_d3(a0t, b0t, c0t) + general_d3(a1, b1, c1)

    c1_d21, c1_d3, meta1 = candidate_path(a0, b0, c0, w, wick, a1, b1, c1, rank)
    c2_d21, c2_d3, meta2 = candidate_path(a0, b0, c0, w, wick, a1, b1, c1, rank)

    stage0_err = rms(meta1["stage0_d21"] - p0_d21) / max(rms(p0_d21), 1e-300)
    stage1_err = rms(c1_d21 - p1_d21) / max(rms(p1_d21), 1e-300)
    d3_stage1_err = rms(c1_d3 - p1_d3) / max(rms(p1_d3), 1e-300)
    finite = bool(
        np.isfinite(p1_d21).all()
        and np.isfinite(c1_d21).all()
        and np.isfinite(p1_d3).all()
        and np.isfinite(c1_d3).all()
    )
    replay = bool(np.array_equal(c1_d21, c2_d21) and np.array_equal(c1_d3, c2_d3))

    return {
        "parent_d21": p1_d21,
        "candidate_d21": c1_d21,
        "parent_d3": p1_d3,
        "candidate_d3": c1_d3,
        "metrics": {
            "n": n,
            "rank": rank,
            "stage0_d21_rms_ratio": float(stage0_err),
            "stage1_d21_rms_ratio": float(stage1_err),
            "stage1_d3_rms_ratio": float(d3_stage1_err),
            "d21_gate": D21_GATE,
            "finite": finite,
            "replay_bitwise": replay,
            "pass": bool(finite and replay and max(stage0_err, stage1_err) <= D21_GATE),
            "candidate_meta": {k: v for k, v in meta1.items() if not isinstance(v, np.ndarray)},
            "replay_meta_equal": bool(
                {k: v for k, v in meta1.items() if not isinstance(v, np.ndarray)}
                == {k: v for k, v in meta2.items() if not isinstance(v, np.ndarray)}
            ),
        },
    }


def cost_ledger(n: int = N_PROD, rank: int = R_PROD) -> dict:
    rho = rank / n
    transport_u = 15.0 * rho
    d21_u = 14.0 * rho
    fixed_remainder_u = 37.6

    overhead_flops = 520 * n * n
    overhead_u = overhead_flops / UNIT
    total_u = transport_u + d21_u + fixed_remainder_u + overhead_u
    total_flops = total_u * UNIT
    ratio = total_flops / BUDGET
    saving_u = NO_OLD_PARENT_U - total_u
    return {
        "budget_flops": BUDGET,
        "unit_flops": UNIT,
        "rank": rank,
        "rho": rho,
        "transport_u": transport_u,
        "d21_extraction_u": d21_u,
        "fixed_remainder_u": fixed_remainder_u,
        "projection_overhead_flops": int(overhead_flops),
        "projection_overhead_u": overhead_u,
        "candidate_total_u": total_u,
        "candidate_total_flops": int(round(total_flops)),
        "candidate_cost_ratio": ratio,
        "cap_ratio": CAP_RATIO,
        "no_old_parent_u": NO_OLD_PARENT_U,
        "saving_u": saving_u,
        "min_saving_u": MIN_SAVING_U,
        "pass": bool(ratio <= CAP_RATIO and saving_u >= MIN_SAVING_U),
        "accounting_kind": "frozen full-chain classical arithmetic ledger; no Strassen credit",
    }


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("research/e181_artifacts"))
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    exact = exact_small()
    if args.smoke:
        n, rank = 48, 144
    else:
        n, rank = N_PROD, R_PROD

    structural = structural_run(n, rank)
    cost = cost_ledger()

    vector_path = out / "E181_IMMUTABLE_VECTORS.npz"
    np.savez_compressed(
        vector_path,
        parent_d21=structural["parent_d21"],
        candidate_d21=structural["candidate_d21"],
        parent_d3=structural["parent_d3"],
        candidate_d3=structural["candidate_d3"],
    )

    arrays = {
        "parent_d21": structural["parent_d21"],
        "candidate_d21": structural["candidate_d21"],
        "parent_d3": structural["parent_d3"],
        "candidate_d3": structural["candidate_d3"],
    }
    vector_hashes = {
        k: {"sha256": array_sha256(v), "shape": list(v.shape), "dtype": str(v.dtype)}
        for k, v in arrays.items()
    }

    if not exact["pass"]:
        terminal_reason = "G1_EXACT_SMALL_IDENTITY_FAILURE"
    elif not structural["metrics"]["pass"]:
        terminal_reason = "G2_D21_RMS_GATE_FAILURE"
    elif not cost["pass"]:
        terminal_reason = "G3_COST_GATE_FAILURE"
    else:
        terminal_reason = None

    accuracy = {
        "status": "NOT_RUN_BY_FROZEN_GATE" if terminal_reason else "REQUIRES_SEPARATE_REFERENCE_BEARING_MINI",
        "candidate_parent_mse_ratio": None,
        "paired_relative_degradation_se": None,
        "paired_degradation_upper95": None,
        "gate_ratio": 1.02,
        "gate_upper95": 0.02,
    }

    receipt = {
        "experiment": "E181",
        "hypothesis": "H180 aggregate symmetric-CP carrier",
        "branch": "research/e181-h180-symmetric-cp-carrier-cleanroom-20260921",
        "rank": R_PROD,
        "seed": SEED,
        "run_kind": "smoke" if args.smoke else "single_target_free_owner_run",
        "ancestry": {
            "e177": "e1536d36a5e2d641ab3596892847e2fcf41e83ab",
            "e180_branch": "research/e180-cost-wall-cp-20260921",
            "arc_reference": "93d091a4c26c042bfffa28f2e76a81bc0aba94bb",
            "public_v29": "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45",
            "e178_used": False,
        },
        "exact_small": exact,
        "structural": structural["metrics"],
        "cost": cost,
        "accuracy": accuracy,
        "terminal_reason": terminal_reason,
        "scientific_go": False,
        "protocol_go": bool(exact["pass"] and structural["metrics"]["replay_bitwise"]),
        "submission_readiness": False,
        "forbidden_actions": {
            "rank_sweep": False,
            "projection_rescue": False,
            "source_age_hybrid": False,
            "public_submission": False,
            "leaderboard_mutation": False,
            "baseline_mutation": False,
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "vector_hashes": vector_hashes,
    }
    receipt_path = out / "E181_RECEIPT.json"
    write_json(receipt_path, receipt)

    results = {
        "exact_small": exact,
        "structural": structural["metrics"],
        "cost": cost,
        "accuracy": accuracy,
        "terminal_reason": terminal_reason,
    }
    results_path = out / "E181_RESULTS.json"
    write_json(results_path, results)

    manifest = {
        "files": {},
        "array_hashes": vector_hashes,
        "seed": SEED,
        "rank": R_PROD,
    }
    for p in [vector_path, receipt_path, results_path]:
        manifest["files"][p.name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    manifest_path = out / "E181_MANIFEST.json"
    write_json(manifest_path, manifest)
    (out / "E181_MANIFEST.sha256").write_text(
        f"{sha256_file(manifest_path)}  {manifest_path.name}\n", encoding="utf-8"
    )

    print(json.dumps({
        "exact_small": exact,
        "structural": structural["metrics"],
        "cost": cost,
        "terminal_reason": terminal_reason,
        "receipt": str(receipt_path),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
