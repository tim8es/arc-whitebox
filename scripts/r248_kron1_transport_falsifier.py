#!/usr/bin/env python3
"""R248 target-free falsifier for V25-KRON1-YOUNG-TRANSPORT.

This is an offline synthetic oracle test only. It does not import whestbench,
open ARC datasets/targets, implement an estimator, or launch Actions.

The oracle uses the best Frobenius rank-1 Kronecker approximation from an SVD
of the Van Loan/Pitsianis rearrangement. This is strictly more favorable than
the frozen production candidate's one-power metered fnp approximation. If the
oracle fails the structural-fidelity gate, the production candidate is rejected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

CANDIDATE_ID = "V25-KRON1-YOUNG-TRANSPORT"
N = 256
D = 16
SEEDS = (248001, 248002, 248003, 248004)
FAMILIES = ("iid_column_scaled", "correlated_column_scaled")
EACH_MAX = 0.015
MEAN_TRANSPORT_MAX = 0.012
CONTROL_MAX = 1e-12


def rrms(candidate: np.ndarray, reference: np.ndarray) -> float:
    den = float(np.linalg.norm(reference.ravel()))
    if den == 0.0:
        return 0.0 if np.array_equal(candidate, reference) else float("inf")
    return float(np.linalg.norm((candidate - reference).ravel()) / den)


def rearrange_for_kron(matrix: np.ndarray, d: int) -> np.ndarray:
    n = d * d
    if matrix.shape != (n, n):
        raise ValueError("matrix shape does not match d*d")
    return matrix.reshape(d, d, d, d).transpose(0, 2, 1, 3).reshape(n, n)


def oracle_best_rank1_kron(matrix: np.ndarray, d: int) -> np.ndarray:
    rearranged = rearrange_for_kron(matrix, d)
    u, s, vh = np.linalg.svd(rearranged, full_matrices=False)
    left = (u[:, 0] * s[0]).reshape(d, d)
    right = vh[0, :].reshape(d, d)
    return np.kron(left, right)


def fixture(seed: int, family: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    # n=256 => 1/sqrt(n)=1/16 exactly; fixed literal avoids any shape-derived
    # Python sqrt/division in the fixture construction.
    w = rng.standard_normal((N, N)) * 0.0625
    if family == "iid_column_scaled":
        w1 = 0.25 + np.abs(rng.standard_normal(N))
    elif family == "correlated_column_scaled":
        a = rng.standard_normal(N)
        b = rng.standard_normal(N)
        w = w + 0.125 * np.outer(a, b)
        w1 = 0.25 + np.abs(rng.standard_normal(N))
    else:
        raise ValueError(f"unknown family: {family}")
    wd = w * w1.reshape(1, N)

    p = rng.standard_normal((N, N))
    a_leg = 0.75 * p + 0.25 * rng.standard_normal((N, N))
    return wd, a_leg, p


def run() -> dict:
    # Exact-Kronecker control validates the rearrangement/oracle implementation.
    c_rng = np.random.default_rng(248000)
    c_left = c_rng.standard_normal((D, D))
    c_right = c_rng.standard_normal((D, D))
    c_exact = np.kron(c_left, c_right)
    c_hat = oracle_best_rank1_kron(c_exact, D)
    control_rrms = rrms(c_hat, c_exact)

    rows = []
    replay_rows = []
    for family in FAMILIES:
        for seed in SEEDS:
            wd, a_leg, p_leg = fixture(seed, family)
            khat = oracle_best_rank1_kron(wd, D)
            ref_a = wd @ a_leg
            ref_p = wd @ p_leg
            cand_a = khat @ a_leg
            cand_p = khat @ p_leg
            row = {
                "family": family,
                "seed": seed,
                "operator_rrms": rrms(khat, wd),
                "transport_A_rrms": rrms(cand_a, ref_a),
                "transport_P_rrms": rrms(cand_p, ref_p),
                "finite": bool(
                    np.isfinite(khat).all()
                    and np.isfinite(cand_a).all()
                    and np.isfinite(cand_p).all()
                ),
            }
            rows.append(row)

            wd2, a2, p2 = fixture(seed, family)
            k2 = oracle_best_rank1_kron(wd2, D)
            replay_rows.append(
                bool(
                    np.array_equal(wd, wd2)
                    and np.array_equal(a_leg, a2)
                    and np.array_equal(p_leg, p2)
                    and np.array_equal(khat, k2)
                )
            )

    all_errors = [
        x
        for row in rows
        for x in (row["operator_rrms"], row["transport_A_rrms"], row["transport_P_rrms"])
    ]
    transported = [
        x for row in rows for x in (row["transport_A_rrms"], row["transport_P_rrms"])
    ]
    all_case_pass = all(
        row["finite"]
        and row["operator_rrms"] <= EACH_MAX
        and row["transport_A_rrms"] <= EACH_MAX
        and row["transport_P_rrms"] <= EACH_MAX
        for row in rows
    )
    go = bool(
        control_rrms <= CONTROL_MAX
        and all(replay_rows)
        and all_case_pass
        and float(np.mean(transported)) <= MEAN_TRANSPORT_MAX
    )
    result = {
        "schema": "arc.whitebox.r248.kron1_transport_falsifier_result.v1",
        "candidate_id": CANDIDATE_ID,
        "target_free": True,
        "public_dataset_opened": False,
        "targets_opened": False,
        "n": N,
        "d": D,
        "seeds": list(SEEDS),
        "families": list(FAMILIES),
        "oracle": "best Frobenius rank-1 Kronecker approximation by SVD of rearranged transport operator",
        "control_rrms": control_rrms,
        "control_max": CONTROL_MAX,
        "rows": rows,
        "deterministic_replay_cases": sum(replay_rows),
        "cases": len(rows),
        "max_any_rrms": float(max(all_errors)),
        "mean_transport_rrms": float(np.mean(transported)),
        "each_max": EACH_MAX,
        "mean_transport_max": MEAN_TRANSPORT_MAX,
        "go": go,
        "decision": "GO" if go else "DEVELOPMENT_NO_GO_TARGET_FREE_FALSIFIER",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["canonical_without_self_hash_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = run()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
