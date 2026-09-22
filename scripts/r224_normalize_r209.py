#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, statistics
from pathlib import Path

DATASET="hf://aicrowd/arc-whestbench-public-2026@v2-phase2"
DATASET_SHA="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
BUDGET=2199023255552
R209_RECEIPT="https://github.com/tim8es/arc-whitebox/blob/e1f6dd6a6bc351b8253e255fef424b1931b37de3/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json"

def load(p): return json.loads(Path(p).read_text())
def reasons(x):
 out=[k for k in ("budget_exhausted","time_exhausted","residual_wall_time_exhausted","combined_budget_exhausted") if x.get(k)]
 if x.get("traceback"): out.append("traceback")
 return out
def make(version, report, fps):
 cfg=report["run_config"]; src=report["results"]["per_mlp"]
 if cfg["dataset"]["path"]!=DATASET or cfg["dataset"]["sha256"]!=DATASET_SHA: raise SystemExit(f"{version} dataset mismatch")
 if len(src)!=100 or len(fps["records"])!=100: raise SystemExit("row count mismatch")
 if [x["mlp_name"] for x in src] != [x["mlp_name"] for x in fps["records"]]: raise SystemExit(f"{version} name/order mismatch")
 rows=[]
 for x,f in zip(src,fps["records"]):
  fail=reasons(x); status="failed" if fail else "ok"
  row={"budget_flops":BUDGET,"final_mse":float(x["final_layer_mse"]),"measured_flops":int(x["flops_used"]),"name":x["mlp_name"],"network_id":f["network_id"],"official_adjusted_score":float(x["adjusted_final_layer_score"]),"status":status,"target_sha256":f["target_sha256"],"wall_time_s":float(x["wall_time_s"]),"residual_wall_time_s":float(x["residual_wall_time_s"]),"failure_reasons":fail}
  expected=row["official_adjusted_score"] if status=="failed" else row["final_mse"]*max(0.1,row["measured_flops"]/BUDGET)
  if not math.isclose(expected,row["official_adjusted_score"],rel_tol=1e-9,abs_tol=1e-18): raise SystemExit(f"{version} score mismatch {row['name']}")
  rows.append(row)
 panel={"count":100,"dataset":DATASET,"dtype":"float32","evaluator":"whestbench 0.16.1","meter":"flopscope 0.12.1+np2.4.6","revision":"v2-phase2; metadata SHA256 264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1; all_layer_means raw SHA256 per network","shape":[16,1024],"split":"mini:all-100","stage":"development"}
 artifact={"v25":{"id":10617855153,"zip_sha256":"820bf9368beac10ea537fc018c3c2185bbd310b9542603cbfa8309519c8e3e08","report_sha256":"68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3"},"v29":{"id":10617318650,"zip_sha256":"32c29ac79c5c59b841c88c6c274ed378daf2778a61d4344c7aa0b58f1da11681","report_sha256":"76c496968b9a81dc1eae91e8204969c0dfe9d7f113dd46af0c0e7df82496a78b"}}[version]
 return {"attempt_id":"35544406064","code_commit":"dff3dd65e9d2210e02418cca99e05556f6bf2c75","evidence_level":"R209_ACTIONS_PLUS_R224_PUBLISHED_DATASET_FINGERPRINTS","experiment_id":"R209","hypothesis_id":f"R209-{version.upper()}-ARCHIVE-NORMALIZATION","id":f"R209-{version}-mini100","panel":panel,"parent_id":"R209-v25-mini100" if version=="v29" else None,"per_network":rows,"receipt_url":R209_RECEIPT,"source":{"actions_run_id":35544406064,"artifact_id":artifact["id"],"artifact_zip_sha256":artifact["zip_sha256"],"report_sha256":artifact["report_sha256"],"dataset_metadata_sha256":DATASET_SHA,"r224_fingerprint_actions_run_id":35788780990,"r224_fingerprint_method":fps["canonicalization"],"raw_prediction_tensors_archived":False,"new_estimator_run":False}}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--fingerprints",required=True); ap.add_argument("--v25-report",required=True); ap.add_argument("--v29-report",required=True); ap.add_argument("--out-dir",required=True); args=ap.parse_args()
 fps=load(args.fingerprints)
 if fps["dataset"]["metadata_sha256"]!=DATASET_SHA or fps["dataset"]["target_dtype"]!="float32" or fps["dataset"]["count"]!=100: raise SystemExit("fingerprint dataset gate failed")
 out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
 records={}
 for v,p in (("v25",args.v25_report),("v29",args.v29_report)):
  rec=make(v,load(p),fps); path=out/f"R209-{v}-mini100.json"; path.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n"); records[v]=rec
 summary={}
 for v,rec in records.items():
  rows=rec["per_network"]; scores=[r["official_adjusted_score"] if r["status"]=="failed" else r["final_mse"]*max(0.1,r["measured_flops"]/BUDGET) for r in rows]
  summary[v]={"failures":sum(r["status"]=="failed" for r in rows),"adjusted_score":statistics.mean(scores),"raw_mse":statistics.mean(r["final_mse"] for r in rows),"mean_flops":statistics.mean(r["measured_flops"] for r in rows)}
 print(json.dumps({"status":"PASS","summary":summary},sort_keys=True))
if __name__=="__main__": main()
