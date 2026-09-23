#!/usr/bin/env python3
"""R243 offline verifier for the terminal R242 normalized R223 record.

No estimator, benchmark, network access, or mutation. Inputs are immutable local files.
"""
import argparse, hashlib, json, math
from pathlib import Path

ARTIFACT_ZIP_SHA256="f144bfd2a5a8a82aaa3e600d1f384d68cfe5e525eb7e22e91eb1d7e843763e00"
R240_RECEIPT_SHA256="e75ec5e2641df59887cf38520e9d9f3a449731fa5fcac481398433c4c4ac8bbd"
PARENT_SHA256="f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742"
CANDIDATE_REPORT_SHA256="72821cf9117b484b2cc4fe4affa21e08ece737e86813508d9c1c6d01b02f6710"
OWNER_RESULT_SHA256="52c5da262f442d3a499c2c77885abc91f81d596e10703c1ac582192ffc8dda65"
DATASET_SHA256="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
NAMES_SHA256="18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
PARENT_ID="R209-v25-mini100"
ARTIFACT_ID=10730459690
BUDGET=2**41

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    with open(p,encoding="utf-8") as f: return json.load(f)

def eq(a,b,tol=0.0):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)
    return a==b

def fail(msg):
    raise AssertionError(msg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-dir",required=True)
    ap.add_argument("--r240-receipt",required=True)
    ap.add_argument("--parent-record",required=True)
    ap.add_argument("--candidate-record",required=True)
    ap.add_argument("--r242-receipt",required=True)
    ap.add_argument("--expected-r242-receipt-sha256",required=True)
    args=ap.parse_args()

    root=Path(args.artifact_dir)
    r240=load(args.r240_receipt); parent=load(args.parent_record)
    cand=load(args.candidate_record); r242=load(args.r242_receipt)

    if sha(args.r240_receipt)!=R240_RECEIPT_SHA256: fail("R240 receipt hash")
    if sha(args.parent_record)!=PARENT_SHA256: fail("R209 parent hash")
    if r240.get("r223_attempt6",{}).get("artifact_id")!=ARTIFACT_ID: fail("R240 artifact id")
    if r240.get("r223_attempt6",{}).get("artifact_zip_sha256")!=ARTIFACT_ZIP_SHA256: fail("R240 artifact digest")
    if sha(args.r242_receipt)!=args.expected_r242_receipt_sha256: fail("R242 receipt hash")

    evidence=root/"r223_attempt6_evidence"
    manifest=load(evidence/"sha256.json")
    actual={}
    for p in root.rglob("*"):
        if p.is_file() and p != evidence/"sha256.json":
            rel=p.relative_to(root)
            key=str(rel)
            if key.startswith("r223_attempt6_evidence/"):
                key=key.split("/",1)[1]
            actual[key]=sha(p)
    if not manifest or set(manifest)!=set(actual): fail("artifact manifest coverage")
    bad=[k for k,v in manifest.items() if actual.get(k)!=v]
    if bad: fail("artifact manifest mismatches: "+",".join(bad))
    if manifest.get("candidate-report.json")!=CANDIDATE_REPORT_SHA256: fail("candidate report manifest hash")
    if manifest.get("R223_ATTEMPT6_RESULT.json")!=OWNER_RESULT_SHA256: fail("owner result manifest hash")

    report=load(evidence/"candidate-report.json")
    owner=load(evidence/"R223_ATTEMPT6_RESULT.json")
    if sha(evidence/"candidate-report.json")!=CANDIDATE_REPORT_SHA256: fail("candidate report bytes")
    if sha(evidence/"R223_ATTEMPT6_RESULT.json")!=OWNER_RESULT_SHA256: fail("owner result bytes")

    rr=report["results"]["per_mlp"]; orows=owner["per_network"]
    prows=parent["per_network"]; crows=cand["per_network"]
    if not (len(rr)==len(orows)==len(prows)==len(crows)==100): fail("100-row cardinality")

    panel_expected=parent["panel"]
    if cand.get("panel")!=panel_expected: fail("panel metadata differs from R209")
    if cand.get("parent_id")!=PARENT_ID: fail("parent link")
    src=cand.get("source",{})
    if src.get("artifact_id")!=ARTIFACT_ID: fail("candidate artifact id")
    if src.get("artifact_zip_sha256")!=ARTIFACT_ZIP_SHA256: fail("candidate artifact digest")
    if src.get("dataset_metadata_sha256")!=DATASET_SHA256: fail("candidate dataset hash")

    names=[]
    for i,(a,o,p,c) in enumerate(zip(rr,orows,prows,crows)):
        if a["mlp_index"]!=i or o["mlp_index"]!=i: fail(f"artifact index {i}")
        if not (a["mlp_name"]==o["mlp_name"]==p["name"]==c["name"]): fail(f"name/order {i}")
        names.append(c["name"])
        if c.get("network_id")!=p.get("network_id"): fail(f"network_id {i}")
        if c.get("target_sha256")!=p.get("target_sha256"): fail(f"target_sha256 {i}")
        if c.get("budget_flops")!=BUDGET: fail(f"budget {i}")

        failure=bool(a.get("budget_exhausted") or a.get("time_exhausted") or
                     a.get("residual_wall_time_exhausted") or a.get("combined_budget_exhausted") or
                     a.get("traceback"))
        expected_status="failed" if failure else "ok"
        if c.get("status")!=expected_status: fail(f"status {i}")
        if bool(c.get("failure_reasons")) != failure: fail(f"failure reasons {i}")
        if c.get("final_mse")!=a.get("final_layer_mse"): fail(f"mse {i}")
        if c.get("measured_flops")!=a.get("flops_used"): fail(f"flops {i}")
        if c.get("residual_wall_time_s")!=a.get("residual_wall_time_s"): fail(f"residual {i}")
        if c.get("wall_time_s")!=a.get("wall_time_s"): fail(f"wall time {i}")
        expected_score=a["final_layer_mse"]*max(0.1,a["flops_used"]/BUDGET)
        if not eq(c.get("official_adjusted_score"),expected_score,1e-18): fail(f"score formula {i}")
        if not eq(c.get("official_adjusted_score"),a.get("adjusted_final_layer_score"),1e-18): fail(f"score report {i}")
        if not eq(c.get("official_adjusted_score"),o.get("candidate_adjusted_recomputed"),1e-18): fail(f"score owner {i}")

    names_hash=hashlib.sha256(json.dumps(names,separators=(",",":")).encode()).hexdigest()
    # The frozen name hash is computed by owner tooling; equality of all 100 names/order above is authoritative.
    if owner["candidate"]["names_sha256"]!=NAMES_SHA256: fail("owner names hash")
    if owner.get("decision")!="R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED": fail("owner reject decision")
    if r240.get("verdict")!="R240_INDEPENDENT_DEVELOPMENT_NO_GO": fail("R240 verdict")

    reject_values=[]
    for obj in (cand,r242):
        for k in ("status","scientific_status","terminal_status","verdict","result_status"):
            if isinstance(obj,dict) and k in obj: reject_values.append(obj[k])
        if isinstance(obj,dict) and isinstance(obj.get("source"),dict):
            for k in ("status","scientific_status","terminal_status","verdict","result_status"):
                if k in obj["source"]: reject_values.append(obj["source"][k])
    if "SCIENTIFIC_REJECT" not in reject_values: fail("normalized/R242 SCIENTIFIC_REJECT not explicit")

    out={
      "status":"PASS","rows_checked":100,"parent_id":cand["parent_id"],
      "artifact_id":ARTIFACT_ID,"artifact_zip_sha256":ARTIFACT_ZIP_SHA256,
      "candidate_mean_adjusted":sum(x["official_adjusted_score"] for x in crows)/100,
      "candidate_mean_mse":sum(x["final_mse"] for x in crows)/100,
      "failures":sum(x["status"]!="ok" for x in crows),
      "names_order_checked":True,"network_ids_checked":True,"target_hashes_checked":True,
      "panel_checked":True,"per_row_metrics_checked":True,"scientific_reject_checked":True,
      "diagnostic_names_json_sha256":names_hash
    }
    print(json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
