#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib, json, math, os, platform, sys
from pathlib import Path
import numpy as np
import torch
import flopscope as flops
import flopscope.numpy as fnp
from whestbench.domain import MLP

torch.set_default_dtype(torch.float64)
torch.set_grad_enabled(False)
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
torch.use_deterministic_algorithms(True)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"e146-h143-stage-a.json"
DEPTH=8; N=32; PARTICLES=128; LINES=64; RANK=16
BUDGET=2**41
V29_COMMIT=os.environ.get("E146_V29_COMMIT","UNKNOWN")
ARC_COMMIT=os.environ.get("E146_ARC_COMMIT","UNKNOWN")

def gf512_mul(a:int,b:int)->int:
    # GF(2^9), primitive polynomial x^9+x^4+1 (0x211).
    r=0
    while b:
        if b&1:r^=a
        b>>=1
        carry=a&0x100
        a=(a<<1)&0x1ff
        if carry:a^=0x11
    return r

def gf512_square(a): return gf512_mul(a,a)
def gf512_pow(a,p):
    r=1
    while p:
        if p&1:r=gf512_mul(r,a)
        a=gf512_square(a); p>>=1
    return r
def gf512_trace(a):
    t=a; z=a
    for _ in range(1,9):
        z=gf512_square(z); t^=z
    if t not in (0,1): raise AssertionError(("bad trace",t))
    return t

def kerdock_line_1024(u:int)->np.ndarray:
    # Carlet even-n construction, n=10 => m=9,t=4.
    bits=np.empty(1024,dtype=np.uint8)
    for c in range(1024):
        x=c&0x1ff; xn=c>>9; ux=gf512_mul(u,x)
        poly=gf512_pow(ux,3)^gf512_pow(ux,5)^gf512_pow(ux,9)^gf512_pow(ux,17)
        bits[c]=gf512_trace(poly)^(xn&gf512_trace(ux))
    return (1-2*bits.astype(np.int16)).astype(np.float64)

def restricted_mub128(n=N)->np.ndarray:
    lines=[]
    for u in range(LINES):
        v=kerdock_line_1024(u)[:n].copy()
        v/=np.linalg.norm(v)
        lines.append(v)
    x=np.stack(lines)
    x=np.concatenate([x,-x],axis=0)
    # Gaussian radial mean in n dimensions.
    radius=math.sqrt(2.0)*math.exp(math.lgamma((n+1)/2)-math.lgamma(n/2))
    return x*radius

def fix_qr(q,r):
    s=torch.where(torch.diagonal(r)<0,-torch.ones(r.shape[0]),torch.ones(r.shape[0]))
    return q*s.unsqueeze(0)

def make_weights(kind,seed):
    g=torch.Generator(device="cpu"); g.manual_seed(seed); out=[]
    if kind=="he":
        for _ in range(DEPTH):
            out.append(torch.randn((N,N),generator=g)*math.sqrt(2.0/N))
        return out
    gains=torch.linspace(0.65,1.35,N); gains/=torch.sqrt(torch.mean(gains.square()))
    for l in range(DEPTH):
        a=torch.randn((N,N),generator=g); b=torch.randn((N,N),generator=g)
        q1,r1=torch.linalg.qr(a); q2,r2=torch.linalg.qr(b)
        q1=fix_qr(q1,r1); q2=fix_qr(q2,r2)
        gg=gains if l%2==0 else torch.flip(gains,dims=(0,))
        out.append(math.sqrt(2.0)*(q1@torch.diag(gg)@q2.T))
    return out

def sha_arrays(xs):
    h=hashlib.sha256()
    for x in xs:
        a=np.ascontiguousarray(np.asarray(x,dtype=np.float64))
        h.update(str(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()

def zero_diag(a):
    a=np.asarray(a,dtype=np.float64).copy(); np.fill_diagonal(a,0.0); return a

def d21_samples(z):
    z=np.asarray(z,dtype=np.float64)
    c=z-z.mean(axis=0,keepdims=True)
    return zero_diag(np.einsum("ri,rj->ij",c*c,c,optimize=True)/z.shape[0])

def range_project(resid, sketch):
    q,_=np.linalg.qr(resid@sketch,mode="reduced")
    q,_=np.linalg.qr(resid@(resid.T@q),mode="reduced")
    return q@(q.T@resid)

def production_cost():
    n=1024; L=16; Np=128; r=16
    prop=2*Np*n*n*L
    d21=2*Np*n*n*L
    repair=12*Np*n*L
    proj=4*n*n*r*(L-1)
    total=prop+d21+repair+proj
    return dict(particle_dense_propagation=prop,empirical_d21=d21,
                moment_repair=repair,rank16_projection_injection=proj,
                all_in_incremental=total,budget=BUDGET,
                fraction=total/BUDGET,cap_fraction=0.00437546,
                pass_gate=total/BUDGET<=0.00437546)

def import_v29():
    p=os.environ["E146_V29_PATH"]
    sys.path.insert(0,str(Path(p)/"estimators"))
    return importlib.import_module("estimator_v29")

def run_v29_capture(weights):
    mod=import_v29()
    d21=[]; moments=[]
    orig_ds=mod.Estimator._dslices
    def ds(self,*a,**kw):
        d3,x=orig_ds(self,*a,**kw)
        if x is not None: d21.append(np.asarray(x,dtype=np.float64).copy())
        return d3,x
    mod.Estimator._dslices=ds
    OrigW=mod.WickCache
    class CapW(OrigW):
        def __init__(self,mean,var):
            moments.append((np.asarray(mean,dtype=np.float64).copy(),
                            np.asarray(var,dtype=np.float64).copy()))
            super().__init__(mean,var)
    mod.WickCache=CapW
    try:
        est=mod.Estimator()
        class C: seed=146
        with flops.BudgetContext(flop_budget=int(1e14),wall_time_limit_s=600,quiet=True):
            est.setup(C())
        ws=[fnp.asarray(w.T.detach().numpy().astype(np.float32)) for w in weights]
        mlp=MLP(width=N,depth=DEPTH,weights=ws,seed=146)
        with flops.BudgetContext(flop_budget=int(1e14),wall_time_limit_s=600,quiet=True):
            est.predict(mlp,BUDGET)
    finally:
        mod.Estimator._dslices=orig_ds; mod.WickCache=OrigW
    # D21 is unavailable at layer0 and trimmed at final layer: expect layers 1..6/7.
    return d21,moments

def candidate(weights):
    d21_base,mom=run_v29_capture(weights)
    if len(d21_base)<2 or len(mom)<DEPTH:
        raise RuntimeError(f"instrumentation mismatch d21={len(d21_base)} moments={len(mom)}")
    cloud=restricted_mub128()
    cloud_d21=[]
    for l,w in enumerate(weights):
        w32=w.T.detach().numpy()
        z=cloud@w32
        mu,var=mom[l]
        sm=z.mean(0); sv=z.var(0)
        scale=np.sqrt(np.maximum(var,1e-14)/np.maximum(sv,1e-14))
        z=mu+(z-sm)*scale
        cloud_d21.append(d21_samples(z))
        cloud=np.maximum(z,0.0)
    # Captured _dslices calls correspond to noninitial preactivations in order.
    repaired=[]; used_cloud=[]
    for j,b in enumerate(d21_base):
        layer=j+1
        c=cloud_d21[layer]
        resid=c-b
        sketch=weights[layer].T.detach().numpy()[:,:RANK]
        repaired.append(zero_diag(b+range_project(resid,sketch)))
        used_cloud.append(c)
    return d21_base,repaired,used_cloud,mom

def exact_reference(weights,count):
    # Imported only after candidate arrays have been frozen.
    from mlp_kprop.kprop_harmonic import Kind,coerce_input,linear_kprop,nonlin_kprop
    from mlp_kprop.wick import relu_wick_coef
    k=coerce_input({1:torch.zeros(N),2:torch.eye(N)},k_max=3,kind=Kind.SIMPLE)
    refs=[]
    for l,w in enumerate(weights):
        pre=linear_kprop(k,w,k_max=3,set_metric=None)
        if l>0 and len(refs)<count:
            t=pre[3].to_tensor()
            idx=torch.arange(N)
            refs.append(zero_diag(t[idx,idx,:].detach().numpy()))
        k=nonlin_kprop(pre,nonlin_wick_coef=relu_wick_coef,k_max=3,
                      kind=Kind.SIMPLE,use_pK=True,factor=True)
    return refs

def fixture(name,kind,seed):
    weights=make_weights(kind,seed)
    b1,r1,c1,m1=candidate(weights)
    frozen_sha=sha_arrays(b1+r1+c1+[x for pair in m1 for x in pair])
    b2,r2,c2,m2=candidate(weights)
    replay_sha=sha_arrays(b2+r2+c2+[x for pair in m2 for x in pair])
    deterministic=frozen_sha==replay_sha and all(np.array_equal(x,y) for x,y in zip(b1+r1,b2+r2))
    # Exact materialization begins only here.
    exact=exact_reference(weights,len(b1))
    if len(exact)!=len(b1): raise RuntimeError((len(exact),len(b1)))
    e0=[]; e1=[]; layer_rat=[]
    for b,r,e in zip(b1,r1,exact):
        a=float(np.linalg.norm(b-e)); z=float(np.linalg.norm(r-e))
        e0.append(a); e1.append(z); layer_rat.append(z/max(a,2**-500))
    pooled=math.sqrt(sum(x*x for x in e1)/max(sum(x*x for x in e0),2**-1000))
    finite=all(np.isfinite(x).all() for x in b1+r1+exact)
    return dict(name=name,kind=kind,seed=seed,width=N,depth=DEPTH,
                evaluated_layers=len(exact),candidate_frozen_sha256=frozen_sha,
                replay_sha256=replay_sha,deterministic_replay_bitwise_exact=deterministic,
                pooled_repaired_over_baseline_d21=pooled,max_layer_ratio=max(layer_rat),
                layer_ratios=layer_rat,baseline_error_norms=e0,repaired_error_norms=e1,
                finite=bool(finite))

def main():
    fixtures=[fixture("he32","he",146032),fixture("adversarial32","adversarial",146132)]
    cost=production_cost()
    gates={
      "he32_ratio_le_0p90":fixtures[0]["pooled_repaired_over_baseline_d21"]<=0.90,
      "adversarial32_ratio_le_0p90":fixtures[1]["pooled_repaired_over_baseline_d21"]<=0.90,
      "max_layer_ratio_le_1p05_all":all(x["max_layer_ratio"]<=1.05 for x in fixtures),
      "deterministic_replay_all":all(x["deterministic_replay_bitwise_exact"] for x in fixtures),
      "finite_all":all(x["finite"] for x in fixtures),
      "incremental_cost_le_0p00437546B":cost["pass_gate"],
      "candidate_before_exact_reference":True,
      "target_public_scorer_holdout_full_firewall":True,
      "pinned_v29_commit_verified":V29_COMMIT=="18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45",
      "pinned_arc_commit_verified":ARC_COMMIT=="93d091a4c26c042bfffa28f2e76a81bc0aba94bb",
    }
    go=all(gates.values())
    result={
      "schema":"arc.whitebox.e146.h143_stage_a.v1","experiment":"E146","hypothesis":"H143",
      "mechanism":"MUB128 in-flow D21 birth-feedback repair on pinned V29",
      "v29_commit":V29_COMMIT,"arc_commit":ARC_COMMIT,
      "frozen":{"lines":64,"particles":128,"rank":16,"depth":8,
                "fixtures":[["he32",146032],["adversarial32",146132]],
                "small_fixture_line_rule":"first 32 coordinates of canonical line from production 1024-D Kerdock bases u=0..63, renormalized"},
      "fixtures":fixtures,"production_incremental_cost":cost,"gates":gates,
      "stage_a_go":go,
      "decision":"E146_STAGE_A_GO_HANDOFF_VERIFIER" if go else "E146_TERMINAL_NO_GO_H143",
      "scope":{"synthetic_only":True,"benchmark_targets":False,"public":False,
               "scorer":False,"holdout":False,"full_suite":False,"final_mse_validation":False,
               "particle_sweep":False,"rank_sweep":False,"layer_sweep":False,"rerun":False},
      "environment":{"python":platform.python_version(),"numpy":np.__version__,"torch":torch.__version__}
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("E146_STAGE_A="+json.dumps(result,sort_keys=True))
    if not go: raise SystemExit(1)

if __name__=="__main__": main()
