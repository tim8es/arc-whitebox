#!/usr/bin/env python3
"""R254 one-shot parent-first target-free harness for V25-BPK2K."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys, traceback
from pathlib import Path
import numpy as np
import flopscope as flops
import flopscope.numpy as fnp
from whestbench.domain import MLP
from r254_fixture import WIDTH, DEPTH, SEED, build_manifest
from r256_timing import capture_budget_telemetry, require_residual_wall_time

BUDGET=2**41
PARENT_SHA256="c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20"

OLD='''            K = {}
            for out_part, entries in PK2K_TABLE.items():
                acc2 = None
                for vpart, coef in entries:
                    prod = None
                    for blk in vpart:
                        fct = pk_slice(blk)
                        prod = fct if prod is None else prod * fct
                    contrib = prod * coef
                    acc2 = contrib if acc2 is None else acc2 + contrib
                K[out_part] = acc2
'''
NEW='''            K = {}
            for out_part, entries in PK2K_TABLE.items():
                terms = []
                for vpart, coef in entries:
                    prod = None
                    for blk in vpart:
                        fct = pk_slice(blk)
                        prod = fct if prod is None else prod * fct
                    terms.append(prod * coef)
                while len(terms) > 1:
                    nxt = []
                    pair_stop = len(terms) - (len(terms) % 2)
                    for ti in range(0, pair_stop, 2):
                        nxt.append(terms[ti] + terms[ti + 1])
                    if pair_stop < len(terms):
                        nxt.append(terms[-1])
                    terms = nxt
                K[out_part] = terms[0]
'''

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def import_estimator(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("import spec failed")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod.Estimator

def run(path:Path,weights:list[np.ndarray],label:str)->dict:
    Estimator=import_estimator(path,"r254_"+label)
    mlp=MLP(width=WIDTH,depth=DEPTH,
            weights=[fnp.asarray(w,dtype=fnp.float32) for w in weights],
            seed=SEED,name="r254-monomial-path-254001")
    mlp.validate()
    checkpoints=[]
    original=flops.as_symmetric
    def wrapped(x,*args,**kwargs):
        arr=np.asarray(x)
        cp={"call_index":len(checkpoints),"shape":list(arr.shape),
            "finite":bool(np.isfinite(arr).all()),
            "max_abs":float(np.max(np.abs(arr))) if arr.size else 0.0,
            "max_symmetry_residual":None}
        if arr.ndim==2 and arr.shape[0]==arr.shape[1] and arr.size:
            cp["max_symmetry_residual"]=float(np.max(np.abs(arr-arr.T)))
        checkpoints.append(cp)
        return original(x,*args,**kwargs)
    result={"label":label,"source_sha256":sha(path.read_bytes()),"exception":None,
            "symmetry_checkpoints":checkpoints}
    try:
        flops.as_symmetric=wrapped
        with flops.BudgetContext(flop_budget=BUDGET,wall_time_limit_s=120.0,quiet=True) as ctx:
            pred=Estimator().predict(mlp,budget=BUDGET)
        arr=np.asarray(pred,dtype=np.float64); telemetry=capture_budget_telemetry(ctx)
        result.update({"shape":list(arr.shape),"prediction_sha256":sha(np.asarray(pred,dtype="<f4").tobytes(order="C")),
                       "flops_used":int(ctx.flops_used),**telemetry,
                       "prediction_finite_by_layer":[bool(np.isfinite(arr[i]).all()) for i in range(arr.shape[0])],
                       "prediction_max_abs_by_layer":[float(np.max(np.abs(arr[i]))) for i in range(arr.shape[0])],
                       "_prediction":arr})
    except Exception as exc:
        result["exception"]={"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()}
    finally:
        flops.as_symmetric=original
    return result

def add_truth(r:dict,truth:np.ndarray)->None:
    if "_prediction" not in r or r["_prediction"].shape!=truth.shape:return
    err=r["_prediction"]-truth; per=np.mean(err*err,axis=1)
    r["per_layer_mse"]=[float(x) for x in per]
    r["all_layer_mse"]=float(np.mean(per)); r["final_layer_mse"]=float(per[-1])
    r["final_layer_max_abs_truth_error"]=float(np.max(np.abs(err[-1])))

def symmetry_failures(r:dict,prefix:str)->list[str]:
    out=[]; cps=r.get("symmetry_checkpoints",[])
    square=0
    for cp in cps:
        if not cp["finite"]:out.append(prefix+"_sym_nonfinite_"+str(cp["call_index"]))
        res=cp["max_symmetry_residual"]
        if res is not None:
            square+=1; tol=1e-6+1e-5*cp["max_abs"]
            if res>tol:out.append(prefix+"_symmetry_"+str(cp["call_index"]))
    if square<DEPTH:out.append(prefix+"_square_symmetry_checkpoint_count_"+str(square))
    return out

def parent_gate(r:dict)->tuple[bool,list[str]]:
    f=[]
    if r.get("source_sha256")!=PARENT_SHA256:f.append("parent_source_hash")
    if r.get("exception") is not None:f.append("parent_exception")
    if r.get("shape")!=[DEPTH,WIDTH]:f.append("parent_shape")
    if not all(r.get("prediction_finite_by_layer",[])):f.append("parent_prediction_nonfinite")
    if not (0<int(r.get("flops_used",0))<=BUDGET):f.append("parent_flops")
    f.extend(symmetry_failures(r,"parent"))
    return not f,f

def construct(parent:Path,candidate:Path)->dict:
    src=parent.read_text()
    count=src.count(OLD)
    if count!=1:raise RuntimeError(f"BPK2K source anchor count {count}")
    cand=src.replace(OLD,NEW)
    delta=NEW
    if "math." in delta or "float(" in delta or "/" in delta:
        raise RuntimeError("candidate source compliance delta failed")
    candidate.write_text(cand)
    return {"anchor_count":count,"parent_sha256":sha(src.encode()),"candidate_sha256":sha(cand.encode()),
            "real_arithmetic_formula_change":False,"coefficient_change":False,
            "new_math_star":False,"new_division":False,"new_scalar_materialization":False}

def candidate_gate(p:dict,c:dict)->tuple[bool,list[str],dict]:
    f=[]; m={}
    if c.get("exception") is not None:f.append("candidate_exception")
    if c.get("shape")!=[DEPTH,WIDTH]:f.append("candidate_shape")
    if not all(c.get("prediction_finite_by_layer",[])):f.append("candidate_nonfinite")
    f.extend(symmetry_failures(c,"candidate"))
    if "final_layer_mse" not in p or "final_layer_mse" not in c:
        return False,f+["missing_truth_metrics"],m
    def ratio(x,y):
        return y/x if x>0 else (1.0 if y==0 else float("inf"))
    m["final_mse_ratio"]=ratio(p["final_layer_mse"],c["final_layer_mse"])
    m["all_layer_mse_ratio"]=ratio(p["all_layer_mse"],c["all_layer_mse"])
    prs=[ratio(x,y) for x,y in zip(p["per_layer_mse"],c["per_layer_mse"])]
    m["per_layer_ratios"]=prs; m["improved_layers"]=sum(y<x for x,y in zip(p["per_layer_mse"],c["per_layer_mse"]))
    m["max_per_layer_degradation_ratio"]=max(prs)
    m["flop_ratio"]=c["flops_used"]/p["flops_used"]
    pr,pfail=require_residual_wall_time(p,"parent")
    cr,cfail=require_residual_wall_time(c,"candidate")
    if pfail:f.append(pfail)
    if cfail:f.append(cfail)
    m["parent_residual_wall_time_s"]=pr;m["candidate_residual_wall_time_s"]=cr
    if m["final_mse_ratio"]>0.95:f.append("final_mse_ratio")
    if m["all_layer_mse_ratio"]>0.98:f.append("all_layer_mse_ratio")
    if m["improved_layers"]<12:f.append("improved_layers")
    if m["max_per_layer_degradation_ratio"]>1.10:f.append("max_layer_degradation")
    if c["final_layer_max_abs_truth_error"]>p["final_layer_max_abs_truth_error"]:f.append("final_max_abs_truth_error")
    if c["flops_used"]>p["flops_used"]:f.append("flops")
    if pr is not None and cr is not None and cr>1.05*pr+0.005:f.append("residual_wall_time")
    return not f,f,m

def clean(r:dict)->dict:return {k:v for k,v in r.items() if k!="_prediction"}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--parent",required=True);ap.add_argument("--out-dir",required=True);a=ap.parse_args()
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);parent=Path(a.parent)
    weights,truth,fixture=build_manifest()
    result={"schema":"arc.r254.target_free.v1","fixture":fixture,"candidate_id":"V25-BPK2K-BALANCED-CUMULANT-REDUCTION",
            "parent_go":False,"candidate_constructed":False,"candidate_go":False}
    p=run(parent,weights,"parent");add_truth(p,truth);pgo,pfail=parent_gate(p)
    result["parent"]=clean(p);result["parent_go"]=pgo;result["parent_failures"]=pfail
    if not pgo:
        result["decision"]="INCONCLUSIVE_PARENT_GATE"
        (out/"R254_TARGET_FREE_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
        return 20
    candidate=out/"R254_CANDIDATE_SOURCE.py";patch=construct(parent,candidate)
    result["candidate_constructed"]=True;result["candidate_patch"]=patch
    c=run(candidate,weights,"candidate");add_truth(c,truth);cgo,cfail,metrics=candidate_gate(p,c)
    result["candidate"]=clean(c);result["candidate_go"]=cgo;result["candidate_failures"]=cfail;result["candidate_metrics"]=metrics
    result["decision"]="TARGET_FREE_GO_PUBLIC_AUTHORIZED" if cgo else "SCIENTIFIC_REJECT_TARGET_FREE"
    (out/"R254_TARGET_FREE_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return 0 if cgo else 31
if __name__=="__main__":raise SystemExit(main())
