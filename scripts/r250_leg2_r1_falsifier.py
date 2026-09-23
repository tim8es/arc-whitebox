#!/usr/bin/env python3
"""R250 frozen target-free falsifier for V25-LEG2-R1-YOUNG-AP.

Offline synthetic oracle only. This is not estimator/submission code and uses no ARC
dataset, targets, candidate outputs, or public-network identities.
"""
import argparse, hashlib, json
import numpy as np

N = 192
LATENT = 24
SEEDS = (25001, 25002, 25003, 25004)
AGES = (0, 2)
PAIR_MAX = 0.015
CORE_MAX = 0.015
MEAN_CORE_MAX = 0.012
CONTROL_MAX = 1e-12

def rrms(x, y):
    den = np.linalg.norm(x.ravel())
    return float(np.linalg.norm((x-y).ravel()) / max(den, np.finfo(np.float64).tiny))

def channel_rank1(A, P):
    X = np.stack([A.ravel(), P.ravel()], axis=0)
    u, s, vh = np.linalg.svd(X, full_matrices=False)
    Xh = s[0] * np.outer(u[:, 0], vh[0])
    return Xh[0].reshape(A.shape), Xh[1].reshape(P.shape)

def core_d21(A, P, w2, s, e):
    AP = A * P
    PP = P * P
    MP = PP * s[None, :] + 3.0 * AP * e[None, :]
    LA = 2.0 * AP * w2[None, :] + PP * e[None, :]
    LP = A * A * w2[None, :] + (PP * s[None, :]) / 3.0 + (2.0 * MP) / 3.0
    D = LA @ A.T + LP @ P.T
    np.fill_diagonal(D, 0.0)
    return D

def realistic(seed, age):
    rng = np.random.default_rng(seed)
    B = rng.standard_normal((N, LATENT)) / np.sqrt(LATENT)
    C = B @ B.T
    d = np.sqrt(np.maximum(np.diag(C), 1e-12))
    C = C / d[:, None] / d[None, :]
    np.fill_diagonal(C, 0.0)
    w1_birth = 0.15 + 0.80 / (1.0 + np.exp(-rng.standard_normal(N)))
    W0 = rng.standard_normal((N, N)) / np.sqrt(N)
    A = W0 @ (w1_birth[:, None] * C)
    P = W0.copy()
    for _ in range(age):
        W = rng.standard_normal((N, N)) / np.sqrt(N)
        w = 0.10 + 0.85 / (1.0 + np.exp(-rng.standard_normal(N)))
        WD = W * w[None, :]
        A = WD @ A
        P = WD @ P
    w2 = 0.5 * rng.standard_normal(N)
    s = 0.5 * rng.standard_normal(N)
    e = 0.5 * rng.standard_normal(N)
    Ah, Ph = channel_rank1(A, P)
    D = core_d21(A, P, w2, s, e)
    Dh = core_d21(Ah, Ph, w2, s, e)
    return {
        "seed": seed, "age": age,
        "a_rrms": rrms(A, Ah), "p_rrms": rrms(P, Ph),
        "joint_rrms": float(np.sqrt((np.linalg.norm(A-Ah)**2 + np.linalg.norm(P-Ph)**2) /
                                    (np.linalg.norm(A)**2 + np.linalg.norm(P)**2))),
        "core_d21_rrms": rrms(D, Dh),
        "finite": bool(np.isfinite(Ah).all() and np.isfinite(Ph).all() and np.isfinite(Dh).all())
    }

def control():
    rng = np.random.default_rng(25000)
    A = rng.standard_normal((64,64))
    P = 1.75 * A
    w2 = rng.standard_normal(64)
    s = rng.standard_normal(64)
    e = rng.standard_normal(64)
    Ah, Ph = channel_rank1(A, P)
    D = core_d21(A, P, w2, s, e)
    Dh = core_d21(Ah, Ph, w2, s, e)
    return {"a_rrms":rrms(A,Ah),"p_rrms":rrms(P,Ph),"core_d21_rrms":rrms(D,Dh)}

def one_run():
    rows=[realistic(seed,age) for seed in SEEDS for age in AGES]
    ctl=control()
    mean_core=float(np.mean([r["core_d21_rrms"] for r in rows]))
    max_pair=max(max(r["a_rrms"],r["p_rrms"]) for r in rows)
    max_core=max(r["core_d21_rrms"] for r in rows)
    gates={
      "control": max(ctl.values()) <= CONTROL_MAX,
      "finite": all(r["finite"] for r in rows),
      "each_a_p_rrms": max_pair <= PAIR_MAX,
      "each_core_d21_rrms": max_core <= CORE_MAX,
      "mean_core_d21_rrms": mean_core <= MEAN_CORE_MAX
    }
    return {"control":ctl,"cases":rows,"summary":{
      "max_pair_rrms":max_pair,"max_core_d21_rrms":max_core,"mean_core_d21_rrms":mean_core,
      "gates":gates,"decision":"PASS" if all(gates.values()) else "FAIL"
    }}

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    a=one_run(); b=one_run()
    deterministic = canonical(a) == canonical(b)
    a["summary"]["gates"]["deterministic_replay"]=deterministic
    a["summary"]["decision"]="PASS" if all(a["summary"]["gates"].values()) else "FAIL"
    a["schema"]="arc.whitebox.r250.target_free_falsifier.v1"
    a["candidate_id"]="V25-LEG2-R1-YOUNG-AP"
    a["target_data_used"]=False
    a["public_panel_used"]=False
    pre=canonical(a)
    a["canonical_result_sha256"]=hashlib.sha256(pre.encode()).hexdigest()
    with open(args.out,"w",encoding="utf-8") as f:
        json.dump(a,f,indent=2,sort_keys=True,allow_nan=False); f.write("\n")
    print(json.dumps(a["summary"],sort_keys=True))
    return 0 if a["summary"]["decision"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
