#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, statistics, traceback
from pathlib import Path
import numpy as np
from datasets import load_dataset
from huggingface_hub import hf_hub_download

DATASET="aicrowd/arc-whestbench-public-2026"; REVISION="v2-phase2"; SPLIT="mini"; BUDGET=2**41
EXPECTED_PARENT_SHA256="f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742"
EXPECTED_METADATA_SHA256="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAME_ORDER_SHA256="18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
PARENT_MEAN_ADJUSTED=8.170397440117225e-9; PARENT_MEAN_FLOPS=806_303_721_965

def sha_bytes(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def extract_fingerprints(parent_rows:list[dict])->dict:
    meta=Path(hf_hub_download(DATASET,"metadata.json",repo_type="dataset",revision=REVISION))
    meta_sha=sha_bytes(meta.read_bytes())
    if meta_sha!=EXPECTED_METADATA_SHA256: raise RuntimeError(f"metadata sha mismatch {meta_sha}")
    info=Path(hf_hub_download(DATASET,"prepared/mini/dataset_info.json",repo_type="dataset",revision=REVISION))
    feat=json.loads(info.read_text())["features"]
    if feat["mlp_seed"]["dtype"]!="int64": raise RuntimeError("mlp_seed dtype mismatch")
    if feat["all_layer_means"]["dtype"]!="float32" or feat["all_layer_means"]["shape"]!=[16,1024]: raise RuntimeError("target schema mismatch")
    ds=load_dataset(DATASET,revision=REVISION,split=SPLIT,streaming=True)
    ds=ds.select_columns(["mlp_name","mlp_seed","all_layer_means"]).with_format("numpy")
    records=[]
    for i,row in enumerate(ds):
        target=np.asarray(row["all_layer_means"])
        if target.dtype!=np.float32 or target.shape!=(16,1024): raise RuntimeError(f"target dtype/shape mismatch row {i}")
        target=np.ascontiguousarray(target,dtype=np.float32)
        records.append({"mlp_index":i,"name":str(row["mlp_name"]),"network_id":str(int(row["mlp_seed"])),"target_sha256":sha_bytes(target.tobytes(order="C"))})
    if len(records)!=100: raise RuntimeError(f"dataset row count {len(records)}")
    names=[r["name"] for r in records]
    name_sha=sha_bytes(json.dumps(names,separators=(",",":")).encode())
    if name_sha!=EXPECTED_NAME_ORDER_SHA256: raise RuntimeError(f"name order sha mismatch {name_sha}")
    mismatches=[]
    for i,(got,exp) in enumerate(zip(records,parent_rows)):
        expected={"name":str(exp["name"]),"network_id":str(exp["network_id"]),"target_sha256":str(exp["target_sha256"])}
        observed={k:got[k] for k in ("name","network_id","target_sha256")}
        if observed!=expected: mismatches.append({"index":i,"observed":observed,"expected":expected})
    return {"dataset":DATASET,"revision":REVISION,"split":SPLIT,"metadata_sha256":meta_sha,
            "dataset_info_sha256":sha_bytes(info.read_bytes()),"name_order_sha256":name_sha,
            "rows":100,"mismatches":mismatches,"exact_identity":not mismatches,"records":records}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-report",type=Path,required=True); ap.add_argument("--parent",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); args=ap.parse_args()
    payload={"schema":"arc.whitebox.r252.public_gate.v1","job_id":"R252","candidate_id":"V25-CFSP4-FINAL-CORNISH-FISHER-SIGMA-POINT","public_gate_pass":False}
    try:
        parent_raw=args.parent.read_bytes(); parent_sha=sha_bytes(parent_raw)
        if parent_sha!=EXPECTED_PARENT_SHA256: raise RuntimeError(f"parent normalized record SHA256 mismatch {parent_sha}")
        parent=json.loads(parent_raw); parent_rows=parent["per_network"]
        if len(parent_rows)!=100: raise RuntimeError("parent row count mismatch")
        fp=extract_fingerprints(parent_rows)
        payload["identity"]={k:v for k,v in fp.items() if k!="records"}
        if not fp["exact_identity"]: raise RuntimeError("published mini row/hash identity mismatch vs R209")
        report=json.loads(args.candidate_report.read_text()); results=report.get("results") or {}; cand=results.get("per_mlp") or []
        if len(cand)!=100: raise RuntimeError(f"candidate report row count {len(cand)}")
        n_failed=int(results.get("n_failed_mlps",0) or 0)
        rows=[]; max_recompute=0.0; gains=[]; improved=0; flops=[]; residuals=[]; scores=[]
        for i,(c,p,f) in enumerate(zip(cand,parent_rows,fp["records"])):
            name=str(c.get("mlp_name",""))
            if name!=f["name"] or name!=p["name"]: raise RuntimeError(f"candidate row/name mismatch at {i}: {name}")
            final_mse=float(c["final_layer_mse"]); cf=int(c["flops_used"]); cs=float(c["adjusted_final_layer_score"]); residual=float(c.get("residual_wall_time_s",0.0) or 0.0)
            recomputed=final_mse*max(0.1,cf/BUDGET); max_recompute=max(max_recompute,abs(recomputed-cs))
            ps=float(p["official_adjusted_score"]); gain=ps-cs; better=cs<ps
            improved+=int(better); gains.append(gain); flops.append(cf); residuals.append(residual); scores.append(cs)
            rows.append({"index":i,"name":name,"network_id":f["network_id"],"target_sha256":f["target_sha256"],
                         "parent_adjusted_score":ps,"candidate_adjusted_score":cs,"gain_parent_minus_candidate":gain,
                         "improved":better,"candidate_final_mse":final_mse,"candidate_flops":cf,"candidate_residual_wall_time_s":residual})
        mean_adjusted=float(sum(scores)/100); mean_flops=float(sum(flops)/100); max_residual=float(max(residuals))
        gain_mean=float(sum(gains)/100); gain_se=float(statistics.stdev(gains)/math.sqrt(100))
        gates={"exact_row_hash_identity":bool(fp["exact_identity"]),"zero_failures":n_failed==0,
               "mean_adjusted_le_0_95_parent":mean_adjusted<=0.95*PARENT_MEAN_ADJUSTED,
               "improved_ge_55":improved>=55,"paired_gain_gt_2se":gain_mean>2.0*gain_se,
               "mean_flops_le_parent":mean_flops<=PARENT_MEAN_FLOPS,"max_residual_lt_0_4":max_residual<0.4,
               "candidate_score_formula_recomputes":max_recompute<=1e-18}
        payload.update({"parent_record_sha256":parent_sha,"n_failed":n_failed,
          "metrics":{"parent_mean_adjusted":PARENT_MEAN_ADJUSTED,"candidate_mean_adjusted":mean_adjusted,
                     "candidate_parent_score_ratio":mean_adjusted/PARENT_MEAN_ADJUSTED,"improved_rows":improved,
                     "paired_gain_mean":gain_mean,"paired_gain_descriptive_se":gain_se,
                     "paired_gain_over_se":gain_mean/gain_se if gain_se else None,
                     "candidate_mean_flops":mean_flops,"parent_mean_flops":PARENT_MEAN_FLOPS,
                     "max_residual_wall_time_s":max_residual,"score_recompute_max_abs":max_recompute},
          "gates":gates,"public_gate_pass":all(gates.values()),"rows":rows,
          "interpretation":"Development-panel evidence only; paired SE is descriptive across networks and is not a held-out significance claim or leaderboard-rank evidence."})
        rc=0 if payload["public_gate_pass"] else 40
    except Exception as exc:
        payload["error"]={"type":exc.__class__.__name__,"message":str(exc),"traceback":traceback.format_exc()}; rc=41
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k!="rows"},sort_keys=True)); return rc

if __name__=="__main__": raise SystemExit(main())
