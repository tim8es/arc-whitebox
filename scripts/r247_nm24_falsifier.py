#!/usr/bin/env python3
"""R247 target-free falsifier for V25-NM24-YOUNG-D21-RIGHT-SPARSIFY.

No ARC dataset, targets, estimator, scorer, or benchmark is opened. This isolates the
candidate's affected D21 contraction on deterministic synthetic states.
"""
import argparse, hashlib, json, math
import numpy as np

SEEDS=(247001,247002,247003,247004)
N=128
K=8
ERR_EACH_MAX=0.015
ERR_MEAN_MAX=0.012
IDENTITY_MAX=1e-14

def nm24(x):
    x=np.asarray(x,dtype=np.float64)
    if x.shape[-1] % 4:
        raise ValueError("last dimension must be divisible by 4")
    g=x.reshape(*x.shape[:-1],x.shape[-1]//4,4)
    order=np.argsort(-np.abs(g),axis=-1,kind="stable")
    keep=order[...,:2]
    mask=np.zeros(g.shape,dtype=bool)
    np.put_along_axis(mask,keep,True,axis=-1)
    kept=np.where(mask,g,0.0)
    e_all=np.sum(g*g,axis=-1,keepdims=True)
    e_keep=np.sum(kept*kept,axis=-1,keepdims=True)
    scale=np.sqrt(np.divide(e_all,e_keep,out=np.ones_like(e_all),where=e_keep>0))
    return (kept*scale).reshape(x.shape)

def contract(LA,LP,A,P):
    return np.einsum("kij,kcj->ic",LA,A,optimize=False)+np.einsum("kij,kcj->ic",LP,P,optimize=False)

def fixture(seed,family):
    rng=np.random.Generator(np.random.PCG64(seed))
    A=rng.normal(0,1/math.sqrt(N),size=(K,N,N))
    P=rng.normal(0,1/math.sqrt(N),size=(K,N,N))
    if family=="iid":
        LA=rng.normal(0,1/math.sqrt(N),size=(K,N,N))
        LP=rng.normal(0,1/math.sqrt(N),size=(K,N,N))
    elif family=="v25_like_correlated":
        w=rng.normal(0,1,size=(K,1,N))
        e=rng.normal(0,0.25,size=(K,1,N))
        ss=rng.normal(0,0.25,size=(K,1,N))
        AP=A*P
        PP=P*P
        MP=PP*ss+3.0*AP*e
        LA=2.0*AP*w+PP*e
        LP=A*A*w+PP*(ss/3.0)+(2.0/3.0)*MP
    else:
        raise ValueError(family)
    return LA,LP,A,P

def rrms(a,b):
    num=np.mean((a-b)**2)
    den=np.mean(a*a)
    return math.sqrt(num/den) if den>0 else (0.0 if num==0 else math.inf)

def run():
    cases=[]
    for family in ("iid","v25_like_correlated"):
        for seed in SEEDS:
            LA,LP,A,P=fixture(seed,family)
            exact=contract(LA,LP,A,P)
            ident=contract(LA,LP,A.copy(),P.copy())
            cand=contract(LA,LP,nm24(A),nm24(P))
            cand2=contract(LA,LP,nm24(A),nm24(P))
            cases.append({
                "family":family,"seed":seed,
                "identity_rrms":rrms(exact,ident),
                "candidate_d21_rrms":rrms(exact,cand),
                "deterministic_max_abs":float(np.max(np.abs(cand-cand2))),
                "finite":bool(np.isfinite(cand).all())
            })
    errs=[x["candidate_d21_rrms"] for x in cases]
    gates={
      "case_count":len(cases)==8,
      "all_finite":all(x["finite"] for x in cases),
      "deterministic":all(x["deterministic_max_abs"]==0.0 for x in cases),
      "identity":all(x["identity_rrms"]<=IDENTITY_MAX for x in cases),
      "each_d21_rrms_le_0p015":all(x["candidate_d21_rrms"]<=ERR_EACH_MAX for x in cases),
      "mean_d21_rrms_le_0p012":sum(errs)/len(errs)<=ERR_MEAN_MAX
    }
    payload={
      "schema":"arc.whitebox.r247.nm24_falsifier.v1",
      "candidate_id":"V25-NM24-YOUNG-D21-RIGHT-SPARSIFY",
      "target_free":True,"n":N,"young_sources":K,"seeds":list(SEEDS),
      "thresholds":{"identity_max":IDENTITY_MAX,"each_d21_rrms_max":ERR_EACH_MAX,"mean_d21_rrms_max":ERR_MEAN_MAX},
      "cases":cases,
      "mean_d21_rrms":sum(errs)/len(errs),
      "max_d21_rrms":max(errs),
      "gates":gates,
      "go":all(gates.values())
    }
    canon=json.dumps(payload,sort_keys=True,separators=(",",":"))
    payload["canonical_without_self_hash_sha256"]=hashlib.sha256(canon.encode()).hexdigest()
    return payload

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    a=ap.parse_args()
    p=run()
    txt=json.dumps(p,indent=2,sort_keys=True)+"\n"
    if a.output:
        open(a.output,"w",encoding="utf-8").write(txt)
    print(txt,end="")
    raise SystemExit(0 if p["go"] else 2)
