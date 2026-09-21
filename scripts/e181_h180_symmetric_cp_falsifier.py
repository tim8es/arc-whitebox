#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np

SCHEMA = "arc.whitebox.e181.h180.v1"
N_SMALL = 24
R_SMALL = 3 * N_SMALL
DEPTH = 16
IDENTITY_TOL = 1e-12
D21_GATE = 0.015
BIRTH_SEED = 181024
WEIGHT_SEED = 181025
IDENTITY_SEED = 181001


def canonical_json(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_rms(candidate: np.ndarray, parent: np.ndarray) -> float:
    num = float(np.sum((candidate - parent) ** 2))
    den = float(np.sum(parent**2))
    if den == 0.0:
        return 0.0 if num == 0.0 else math.inf
    return math.sqrt(num / den)


def d3_from_cp(U: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.sum((U**3) * lam[None, :], axis=1)


def d21_from_cp(U: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.einsum("q,iq,cq->ic", lam, U * U, U, optimize=True)


def dense_from_cp(U: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.einsum("q,iq,jq,kq->ijk", lam, U, U, U, optimize=True)


def exact_small_identity_metrics() -> dict:
    rng = np.random.default_rng(IDENTITY_SEED)
    n, r = 5, 7
    U = rng.normal(size=(n, r))
    lam = rng.normal(size=r)
    T = dense_from_cp(U, lam)

    idx = np.arange(n)
    d3_dense = T[idx, idx, idx]
    d21_dense = T[idx, idx, :]
    e_d3 = rel_rms(d3_from_cp(U, lam), d3_dense)
    e_d21 = rel_rms(d21_from_cp(U, lam), d21_dense)

    W = rng.normal(size=(n, n)) / math.sqrt(n)
    Ut = W @ U
    T_dense_transport = np.einsum(
        "ai,bj,ck,ijk->abc", W, W, W, T, optimize=True
    )
    T_cp_transport = dense_from_cp(Ut, lam)
    e_transport = rel_rms(T_cp_transport, T_dense_transport)

    Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    U_roundtrip = Q.T @ (Q @ U)
    e_roundtrip_d3 = rel_rms(d3_from_cp(U_roundtrip, lam), d3_from_cp(U, lam))
    e_roundtrip_d21 = rel_rms(d21_from_cp(U_roundtrip, lam), d21_from_cp(U, lam))
    e_roundtrip = max(e_roundtrip_d3, e_roundtrip_d21)

    metrics = {
        "carrier_d3_rel_rms": e_d3,
        "carrier_d21_rel_rms": e_d21,
        "linear_transport_rel_rms": e_transport,
        "roundtrip_d3_rel_rms": e_roundtrip_d3,
        "roundtrip_d21_rel_rms": e_roundtrip_d21,
        "roundtrip_max_rel_rms": e_roundtrip,
        "threshold": IDENTITY_TOL,
    }
    metrics["pass"] = bool(
        all(math.isfinite(v) and v <= IDENTITY_TOL for k, v in metrics.items()
            if k.endswith("rel_rms"))
    )
    return metrics


def top_energy_truncate(
    U: np.ndarray, lam: np.ndarray, rank: int
) -> tuple[np.ndarray, np.ndarray]:
    if U.shape[1] <= rank:
        return U, lam
    norms = np.linalg.norm(U, axis=0)
    score = np.abs(lam) * norms**3
    original_index = np.arange(score.size)
    keep = np.lexsort((original_index, -score))[:rank]
    return U[:, keep], lam[keep]


def run_structural() -> dict:
    rng_birth = np.random.default_rng(BIRTH_SEED)
    rng_w = np.random.default_rng(WEIGHT_SEED)

    U_parent = np.zeros((N_SMALL, 0), dtype=np.float64)
    l_parent = np.zeros((0,), dtype=np.float64)
    U_candidate = np.zeros((N_SMALL, 0), dtype=np.float64)
    l_candidate = np.zeros((0,), dtype=np.float64)

    parent_d21 = []
    candidate_d21 = []
    parent_d3 = []
    candidate_d3 = []
    layers = []

    for layer in range(DEPTH):
        U_birth = rng_birth.normal(size=(N_SMALL, N_SMALL))
        U_birth /= np.linalg.norm(U_birth, axis=0, keepdims=True)
        l_birth = (
            rng_birth.choice(np.array([-1.0, 1.0]), size=N_SMALL)
            * rng_birth.uniform(0.8, 1.2, size=N_SMALL)
        )

        U_parent = np.concatenate([U_parent, U_birth], axis=1)
        l_parent = np.concatenate([l_parent, l_birth])
        U_candidate = np.concatenate([U_candidate, U_birth], axis=1)
        l_candidate = np.concatenate([l_candidate, l_birth])
        U_candidate, l_candidate = top_energy_truncate(
            U_candidate, l_candidate, R_SMALL
        )

        p21 = d21_from_cp(U_parent, l_parent)
        c21 = d21_from_cp(U_candidate, l_candidate)
        p3 = d3_from_cp(U_parent, l_parent)
        c3 = d3_from_cp(U_candidate, l_candidate)

        if layer < DEPTH - 1:
            parent_d21.append(p21)
            candidate_d21.append(c21)
            parent_d3.append(p3)
            candidate_d3.append(c3)
            layers.append(
                {
                    "layer": layer,
                    "parent_components": int(U_parent.shape[1]),
                    "candidate_components": int(U_candidate.shape[1]),
                    "d21_rel_rms": rel_rms(c21, p21),
                    "d3_rel_rms": rel_rms(c3, p3),
                    "finite": bool(
                        np.isfinite(p21).all()
                        and np.isfinite(c21).all()
                        and np.isfinite(p3).all()
                        and np.isfinite(c3).all()
                    ),
                }
            )

        if layer < DEPTH - 1:
            Q, _ = np.linalg.qr(rng_w.normal(size=(N_SMALL, N_SMALL)))
            W = 0.72 * np.eye(N_SMALL) + 0.28 * Q
            U_parent = W @ U_parent
            U_candidate = W @ U_candidate

    arrays = {
        "parent_d21": np.stack(parent_d21),
        "candidate_d21": np.stack(candidate_d21),
        "parent_d3": np.stack(parent_d3),
        "candidate_d3": np.stack(candidate_d3),
    }
    max_d21 = max(x["d21_rel_rms"] for x in layers)
    max_d3 = max(x["d3_rel_rms"] for x in layers)
    worst_layer = max(layers, key=lambda x: x["d21_rel_rms"])["layer"]
    summary = {
        "n_small": N_SMALL,
        "rank_small": R_SMALL,
        "depth": DEPTH,
        "birth_seed": BIRTH_SEED,
        "weight_seed": WEIGHT_SEED,
        "max_d21_rel_rms": max_d21,
        "max_d3_rel_rms": max_d3,
        "worst_d21_layer": worst_layer,
        "threshold": D21_GATE,
        "all_finite": all(x["finite"] for x in layers),
        "pass": bool(
            all(x["finite"] for x in layers)
            and math.isfinite(max_d21)
            and max_d21 <= D21_GATE
        ),
    }
    return {"summary": summary, "layers": layers, "arrays": arrays}


def array_digest(arrays: dict[str, np.ndarray]) -> str:
    h = hashlib.sha256()
    for name in sorted(arrays):
        a = np.ascontiguousarray(arrays[name], dtype=np.float64)
        h.update(name.encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes(order="C"))
    return h.hexdigest()


def production_flop_ledger() -> dict:
    getcontext().prec = 50
    n = 1024
    rank = 3072
    u = Decimal(2 * n**3)
    budget = Decimal(2**41)

    transport = Decimal(15 * 3) * u
    d21 = Decimal(14 * 3) * u
    fixed_remainder = Decimal("37.6") * u

    # Fixed protocol charge for each of 15 aggregate reprojections:
    # norm scoring: 2*n*(R+n), lambda/norm score ops: 3*(R+n),
    # deterministic selection comparison envelope: ceil(log2(R))*(R+n).
    active = rank + n
    selection_levels = math.ceil(math.log2(rank))
    projection_per = Decimal(
        2 * n * active + 3 * active + selection_levels * active
    )
    projection = Decimal(15) * projection_per

    total = transport + d21 + fixed_remainder + projection
    c_over_b = total / budget
    total_u = total / u
    saving_u = Decimal("153.0") - total_u

    return {
        "n": n,
        "rank": rank,
        "depth": 16,
        "u_flops": str(u),
        "budget_flops": str(budget),
        "components_flops": {
            "cp_transport_15": str(transport),
            "d21_extract_14": str(d21),
            "frozen_non_young_remainder_37p6u": str(fixed_remainder),
            "projection_bookkeeping_15": str(projection),
        },
        "projection_selection_levels": selection_levels,
        "total_flops": str(total),
        "total_u": str(total_u),
        "c_over_b": str(c_over_b),
        "saving_from_no_old_parent_u": str(saving_u),
        "gates": {
            "c_over_b_le_0p135": bool(c_over_b <= Decimal("0.135")),
            "saving_ge_14p76u": bool(saving_u >= Decimal("14.76")),
        },
        "pass": bool(
            c_over_b <= Decimal("0.135") and saving_u >= Decimal("14.76")
        ),
    }


def write_json(path: Path, obj) -> None:
    path.write_text(canonical_json(obj), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    exact = exact_small_identity_metrics()
    write_json(out / "exact_small.json", exact)

    structural = run_structural()
    write_json(
        out / "structural_metrics.json",
        {"summary": structural["summary"], "layers": structural["layers"]},
    )
    for name, arr in structural["arrays"].items():
        np.save(out / f"{name}.npy", arr, allow_pickle=False)

    cost = production_flop_ledger()
    write_json(out / "flops.json", cost)

    # Deterministic replay inside the one armed workflow run.
    replay_structural = run_structural()
    first_digest = array_digest(structural["arrays"])
    second_digest = array_digest(replay_structural["arrays"])
    replay = {
        "mode": "in_process_deterministic_replay_same_frozen_seeds",
        "first_vector_digest": first_digest,
        "replay_vector_digest": second_digest,
        "match": first_digest == second_digest,
        "command": "python scripts/e181_h180_symmetric_cp_falsifier.py --out <fresh-dir>",
    }
    write_json(out / "replay.json", replay)

    first_failure = None
    if not exact["pass"]:
        first_failure = "exact_small_identity_gate"
    elif not structural["summary"]["pass"]:
        first_failure = "d21_rms_gate"
    elif not cost["pass"]:
        first_failure = "production_flop_gate"
    elif not replay["match"]:
        first_failure = "deterministic_replay_gate"

    accuracy_state = (
        "not_run_due_to_" + first_failure
        if first_failure
        else "not_run_no_reference_stage_armed_in_structural_falsifier"
    )

    receipt = {
        "schema": SCHEMA,
        "experiment": "E181",
        "hypothesis": "H180 aggregate symmetric-CP inherited-K3 carrier",
        "branch": "research/e181-h180-symmetric-cp-carrier-20260921",
        "github_arm_sha": os.environ.get("GITHUB_SHA"),
        "clean_base": "dff3dd65e9d2210e02418cca99e05556f6bf2c75",
        "e180_source_commit": "805d11f8d59d9a502aab8b5bbf935d2f865fecea",
        "e178_used": False,
        "rank_production": 3072,
        "rank_rule": "R=3n fixed; no sweep",
        "projection_rule": "top |lambda|*||u||^3, stable original-index tiebreak",
        "target_free": True,
        "benchmark_targets_exposed": False,
        "public_submission": False,
        "leaderboard_mutation": False,
        "baseline_mutation": False,
        "exact_small": exact,
        "structural": structural["summary"],
        "flops": cost,
        "replay": replay,
        "accuracy": {
            "state": accuracy_state,
            "candidate_parent_mse_ratio": None,
            "paired_relative_degradation_u95": None,
            "se": None,
            "reason": (
                "Frozen protocol suppresses MSE/SE reference exposure after any prior gate failure."
                if first_failure
                else "This armed job is the target-free structural falsifier only."
            ),
        },
        "first_failing_gate": first_failure,
        "decision": "NO-GO" if first_failure else "STRUCTURAL_GO_ONLY",
        "terminal": bool(first_failure),
    }

    if first_failure == "d21_rms_gate":
        receipt["terminal_reason"] = (
            f"max D21 relative RMS {structural['summary']['max_d21_rel_rms']:.17g} "
            f"> frozen threshold {D21_GATE:.17g}"
        )
    elif first_failure:
        receipt["terminal_reason"] = first_failure
    else:
        receipt["terminal_reason"] = None

    write_json(out / "receipt.json", receipt)

    # Evidence-source hashes are frozen into the manifest.
    extra_sources = []
    for source in [Path(__file__), Path("research/E181_PROTOCOL.md")]:
        if source.exists():
            extra_sources.append(
                {
                    "path": source.as_posix(),
                    "sha256": sha256_file(source),
                    "bytes": source.stat().st_size,
                }
            )

    files = []
    for path in sorted(out.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        files.append(
            {
                "path": path.name,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )

    manifest = {
        "schema": "arc.whitebox.e181.manifest.v1",
        "immutable_evidence": files,
        "source_files": extra_sources,
        "vector_digest": first_digest,
        "replay_match": replay["match"],
    }
    write_json(out / "manifest.json", manifest)

    print(canonical_json(receipt), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
