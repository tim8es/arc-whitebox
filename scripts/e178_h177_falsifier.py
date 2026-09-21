#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
from pathlib import Path

import numpy as np

EXP = "E178"
BRANCH = "research/e178-h177-higher-order-ago-gauge-20260921"
E177_COMMIT = "e1536d36a5e2d641ab3596892847e2fcf41e83ab"
PUBLIC_REPO_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PUBLIC_V17_BLOB = "9c60c5a0bd92729f27bde23eeb619944e71beabe"
LAM0 = 1.9516e-3
N = 4
DEPTH = 3
SEED = 178177
STATE_LAYER = 1
IDENTITY_TOL = 2.0e-12
CLOSURE_RATIO_GATE = 0.98
BUDGET = 2**41
CAP = int(math.floor(0.135 * BUDGET))
PUBLIC_V17_C_OVER_B = 0.4921
PUBLIC_V17_COST_LOWER = PUBLIC_V17_C_OVER_B * BUDGET


def radial_moment(n: int, k: int) -> float:
    return math.exp(
        0.5 * k * math.log(2.0 / n)
        + math.lgamma((n + k) / 2.0)
        - math.lgamma(n / 2.0)
    )


def raw_from_samples(x: np.ndarray):
    x = np.asarray(x, dtype=np.float64)
    w = np.full(x.shape[0], 1.0 / x.shape[0], dtype=np.float64)
    return (
        np.einsum("s,si->i", w, x),
        np.einsum("s,si,sj->ij", w, x, x),
        np.einsum("s,si,sj,sk->ijk", w, x, x, x),
        np.einsum("s,si,sj,sk,sl->ijkl", w, x, x, x, x),
    )


def cumulants_from_raw(m1, m2, m3, m4):
    mu = np.asarray(m1, dtype=np.float64)
    k2 = m2 - np.einsum("i,j->ij", mu, mu)
    k3 = (
        m3
        - np.einsum("ij,k->ijk", m2, mu)
        - np.einsum("ik,j->ijk", m2, mu)
        - np.einsum("jk,i->ijk", m2, mu)
        + 2.0 * np.einsum("i,j,k->ijk", mu, mu, mu)
    )

    m3mu = (
        np.einsum("ijk,l->ijkl", m3, mu)
        + np.einsum("ijl,k->ijkl", m3, mu)
        + np.einsum("ikl,j->ijkl", m3, mu)
        + np.einsum("jkl,i->ijkl", m3, mu)
    )
    m2m2 = (
        np.einsum("ij,kl->ijkl", m2, m2)
        + np.einsum("ik,jl->ijkl", m2, m2)
        + np.einsum("il,jk->ijkl", m2, m2)
    )
    m2mumu = (
        np.einsum("ij,k,l->ijkl", m2, mu, mu)
        + np.einsum("ik,j,l->ijkl", m2, mu, mu)
        + np.einsum("il,j,k->ijkl", m2, mu, mu)
        + np.einsum("jk,i,l->ijkl", m2, mu, mu)
        + np.einsum("jl,i,k->ijkl", m2, mu, mu)
        + np.einsum("kl,i,j->ijkl", m2, mu, mu)
    )
    k4 = (
        m4
        - m3mu
        - m2m2
        + 2.0 * m2mumu
        - 6.0 * np.einsum("i,j,k,l->ijkl", mu, mu, mu, mu)
    )
    return (mu.copy(), k2, k3, k4)


def raw_from_cumulants(k1, k2, k3, k4):
    mu = np.asarray(k1, dtype=np.float64)
    m1 = mu.copy()
    m2 = k2 + np.einsum("i,j->ij", mu, mu)
    m3 = (
        k3
        + np.einsum("ij,k->ijk", k2, mu)
        + np.einsum("ik,j->ijk", k2, mu)
        + np.einsum("jk,i->ijk", k2, mu)
        + np.einsum("i,j,k->ijk", mu, mu, mu)
    )
    k3mu = (
        np.einsum("ijk,l->ijkl", k3, mu)
        + np.einsum("ijl,k->ijkl", k3, mu)
        + np.einsum("ikl,j->ijkl", k3, mu)
        + np.einsum("jkl,i->ijkl", k3, mu)
    )
    k2k2 = (
        np.einsum("ij,kl->ijkl", k2, k2)
        + np.einsum("ik,jl->ijkl", k2, k2)
        + np.einsum("il,jk->ijkl", k2, k2)
    )
    k2mumu = (
        np.einsum("ij,k,l->ijkl", k2, mu, mu)
        + np.einsum("ik,j,l->ijkl", k2, mu, mu)
        + np.einsum("il,j,k->ijkl", k2, mu, mu)
        + np.einsum("jk,i,l->ijkl", k2, mu, mu)
        + np.einsum("jl,i,k->ijkl", k2, mu, mu)
        + np.einsum("kl,i,j->ijkl", k2, mu, mu)
    )
    m4 = (
        k4
        + k3mu
        + k2k2
        + k2mumu
        + np.einsum("i,j,k,l->ijkl", mu, mu, mu, mu)
    )
    return (m1, m2, m3, m4)


def gauge(kappas, n: int, *, to_angular: bool):
    raw = raw_from_cumulants(*kappas)
    scaled = []
    for order, arr in enumerate(raw, start=1):
        a = radial_moment(n, order)
        scaled.append(arr / a if to_angular else arr * a)
    return cumulants_from_raw(*scaled)


def offdiag(a):
    b = np.array(a, dtype=np.float64, copy=True)
    np.fill_diagonal(b, 0.0)
    return b


def slices(kappas):
    _, k2, k3, k4 = kappas
    n = k2.shape[0]
    idx = np.arange(n)
    d21 = np.empty((n, n), dtype=np.float64)
    k31 = np.empty((n, n), dtype=np.float64)
    k22 = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            d21[i, j] = k3[i, i, j]
            k31[i, j] = k4[i, i, i, j]
            k22[i, j] = k4[i, i, j, j]
    return {
        "k1": kappas[0],
        "k2": k2,
        "d3": k3[idx, idx, idx],
        "d21": offdiag(d21),
        "k4": k4,
        "k4_4": k4[idx, idx, idx, idx],
        "k4_31": offdiag(k31),
        "k4_22": offdiag(k22),
    }


def rel_max(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return float(np.max(np.abs(a - b)) / max(float(np.max(np.abs(a))), 1.0e-12))


def identity_metrics(source, round_trip):
    a = slices(source)
    b = slices(round_trip)
    return {name: rel_max(a[name], b[name]) for name in a}


def harmonic_g(k4: np.ndarray):
    n = k4.shape[0]
    trace2 = np.einsum("ijkk->ij", k4)
    return (
        (6.0 / (n + 4.0)) * trace2
        - (3.0 / ((n + 2.0) * (n + 4.0))) * np.trace(trace2) * np.eye(n)
    )


def fixture():
    sign = np.asarray(list(itertools.product([-1.0, 1.0], repeat=N)), dtype=np.float64)
    axes = []
    for i in range(N):
        v = np.zeros(N, dtype=np.float64)
        v[i] = math.sqrt(N)
        axes.extend([v.copy(), -v.copy()])
    directions = np.vstack([sign, np.asarray(axes, dtype=np.float64)])
    assert directions.shape == (24, N)
    assert np.array_equal(np.linalg.norm(directions, axis=1), np.full(24, math.sqrt(N)))

    rng = np.random.default_rng(SEED)
    weights = np.stack(
        [rng.normal(0.0, math.sqrt(2.0 / N), size=(N, N)) for _ in range(DEPTH)]
    )

    x = directions.copy()
    activations = []
    for w in weights:
        x = np.maximum(x @ w, 0.0)
        activations.append(x.copy())

    angular_state = activations[STATE_LAYER]
    angular = cumulants_from_raw(*raw_from_samples(angular_state))
    gaussian = gauge(angular, N, to_angular=False)
    recovered_angular = gauge(gaussian, N, to_angular=True)
    recovered_gaussian = gauge(recovered_angular, N, to_angular=False)

    rng2 = np.random.default_rng(SEED + 1)
    generic_a = cumulants_from_raw(*raw_from_samples(rng2.normal(size=(37, N))))
    generic_g = gauge(generic_a, N, to_angular=False)
    generic_a_rt = gauge(generic_g, N, to_angular=True)
    generic_g_rt = gauge(generic_a_rt, N, to_angular=False)

    id_a = identity_metrics(generic_a, generic_a_rt)
    id_g = identity_metrics(generic_g, generic_g_rt)
    fixture_id_a = identity_metrics(angular, recovered_angular)
    fixture_id_g = identity_metrics(gaussian, recovered_gaussian)

    ga = harmonic_g(angular[3])
    gg = harmonic_g(gaussian[3])
    gha = np.diag(np.diag(ga)) + LAM0 * offdiag(angular[1])
    ghg = np.diag(np.diag(gg)) + LAM0 * offdiag(gaussian[1])
    mask = ~np.eye(N, dtype=bool)
    mse_a = float(np.mean((gha[mask] - ga[mask]) ** 2))
    mse_g = float(np.mean((ghg[mask] - gg[mask]) ** 2))
    ratio = mse_a / mse_g

    arrays = {
        "directions": directions,
        "weights": weights,
        "angular_state": angular_state,
        "angular_k1": angular[0],
        "angular_k2": angular[1],
        "angular_k3": angular[2],
        "angular_k4": angular[3],
        "gaussian_k1": gaussian[0],
        "gaussian_k2": gaussian[1],
        "gaussian_k3": gaussian[2],
        "gaussian_k4": gaussian[3],
        "angular_G": ga,
        "gaussian_G": gg,
        "angular_Ghat": gha,
        "gaussian_Ghat": ghg,
    }
    metrics = {
        "radial_moments": {str(k): radial_moment(N, k) for k in range(1, 5)},
        "identity_generic_A_to_G_to_A": id_a,
        "identity_generic_G_to_A_to_G": id_g,
        "identity_fixture_A_to_G_to_A": fixture_id_a,
        "identity_fixture_G_to_A_to_G": fixture_id_g,
        "closure": {
            "lambda0": LAM0,
            "parent_gaussian_mse_off": mse_g,
            "h177_angular_mse_off": mse_a,
            "h177_over_parent": ratio,
            "gate_ratio": CLOSURE_RATIO_GATE,
            "passes": bool(ratio <= CLOSURE_RATIO_GATE),
        },
    }
    return arrays, metrics


def array_hashes(arrays):
    out = {}
    for name in sorted(arrays):
        a = np.ascontiguousarray(arrays[name])
        h = hashlib.sha256()
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
        out[name] = h.hexdigest()
    return out


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def json_dump(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    head_sha = os.environ.get("GITHUB_SHA", "local")
    out = Path("research/e178_evidence") / str(run_id)
    out.mkdir(parents=True, exist_ok=False)

    arrays1, metrics1 = fixture()
    hashes1 = array_hashes(arrays1)
    arrays2, metrics2 = fixture()
    hashes2 = array_hashes(arrays2)
    replay = {
        "array_hashes_first": hashes1,
        "array_hashes_replay": hashes2,
        "arrays_bitwise_equal": hashes1 == hashes2,
        "metrics_json_equal": json.dumps(metrics1, sort_keys=True) == json.dumps(metrics2, sort_keys=True),
    }

    all_identity = [
        value
        for key, group in metrics1.items()
        if key.startswith("identity_")
        for value in group.values()
    ]
    identity_pass = bool(max(all_identity) <= IDENTITY_TOL)
    replay_pass = bool(replay["arrays_bitwise_equal"] and replay["metrics_json_equal"])
    closure_pass = bool(metrics1["closure"]["passes"])
    cost_pass = bool(PUBLIC_V17_COST_LOWER <= CAP)

    if not identity_pass:
        decision = "TERMINAL_NO_GO_IDENTITY"
    elif not replay_pass:
        decision = "TERMINAL_NO_GO_REPLAY"
    elif not closure_pass:
        decision = "TERMINAL_NO_GO_CLOSURE"
    elif not cost_pass:
        decision = "TERMINAL_NO_GO_COST"
    else:
        decision = "GO_TARGET_FREE_H177"

    result = {
        "schema": "arc.whitebox.e178.result.v1",
        "experiment": EXP,
        "hypothesis": "H177 higher-order AGO gauge",
        "fixture": {
            "n": N,
            "depth": DEPTH,
            "seed": SEED,
            "support_count": 24,
            "state_layer_zero_indexed": STATE_LAYER,
            "zero_bias": True,
            "target_free": True,
        },
        "metrics": metrics1,
        "gates": {
            "identity_tol": IDENTITY_TOL,
            "identity_max_error": max(all_identity),
            "identity_pass": identity_pass,
            "replay_pass": replay_pass,
            "closure_pass": closure_pass,
            "full_cost_pass": cost_pass,
        },
        "cost": {
            "budget_flops": BUDGET,
            "cap_flops": CAP,
            "public_v17_c_over_b": PUBLIC_V17_C_OVER_B,
            "public_v17_cost_lower_bound_flops": PUBLIC_V17_COST_LOWER,
            "public_v17_over_cap_ratio": PUBLIC_V17_COST_LOWER / CAP,
            "h177_overlay_lower_bound_flops": 0,
            "full_cost_lower_bound_flops": PUBLIC_V17_COST_LOWER,
            "logic": "unchanged V17 already exceeds 0.135B; even a zero-cost H177 overlay cannot pass",
        },
        "decision": decision,
    }

    np.savez(out / "vectors.npz", **arrays1)
    json_dump(out / "result.json", result)
    json_dump(out / "replay.json", replay)

    manifest = {
        "schema": "arc.whitebox.e178.manifest.v1",
        "run_id": str(run_id),
        "head_sha": head_sha,
        "payload_sha256": {
            name: sha256_file(out / name)
            for name in ("vectors.npz", "result.json", "replay.json")
        },
        "array_sha256": hashes1,
        "source_pins": {
            "e177_commit": E177_COMMIT,
            "public_repo_commit": PUBLIC_REPO_COMMIT,
            "public_v17_blob": PUBLIC_V17_BLOB,
        },
    }
    json_dump(out / "manifest.json", manifest)
    manifest_sha = sha256_file(out / "manifest.json")

    receipt = {
        "schema": "arc.whitebox.e178.terminal_receipt.v1",
        "experiment": EXP,
        "branch": BRANCH,
        "run_id": str(run_id),
        "armed_head_sha": head_sha,
        "status": "GO" if decision.startswith("GO_") else "TERMINAL_NO_GO",
        "decision": decision,
        "scientific_closure_go": closure_pass and identity_pass and replay_pass,
        "production_cost_go": cost_pass,
        "no_public_target_or_scorer": True,
        "no_rank_seed_lambda_sweep": True,
        "lambda_refit": False,
        "rerun_authorized": False,
        "manifest_sha256": manifest_sha,
        "gates": result["gates"],
        "cost": result["cost"],
        "closure": metrics1["closure"],
        "ancestry": {
            "e177_commit": E177_COMMIT,
            "e176_used": False,
            "public_v17_commit": PUBLIC_REPO_COMMIT,
            "public_v17_blob": PUBLIC_V17_BLOB,
        },
        "authorization": "target-free E178 only; no public Mini/full/holdout/scorer/submission/leaderboard authorization",
    }
    json_dump(out / "E178_TERMINAL_RECEIPT.json", receipt)

    print(json.dumps({
        "decision": decision,
        "identity_max_error": result["gates"]["identity_max_error"],
        "closure_ratio": metrics1["closure"]["h177_over_parent"],
        "cost_c_over_b_lower_bound": PUBLIC_V17_C_OVER_B,
        "out": str(out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
