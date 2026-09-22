#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, statistics, sys
from pathlib import Path

B = 2199023255552
PARENT_MSE = 2.228303490170447e-8
PARENT_SCORE = 8.170397440117225e-9
PARENT_CB = 0.36666448157347986
TARGET_SCORE = 8.129545452916639e-9
EXPECTED_DATASET_SHA = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAMES_SHA = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"

def sha_names(rows):
    names=[r["mlp_name"] for r in rows]
    return hashlib.sha256(json.dumps(names,separators=(",",":")).encode()).hexdigest()

def mean(xs): return sum(xs)/len(xs)
def se(xs):
    return statistics.stdev(xs)/math.sqrt(len(xs)) if len(xs)>1 else 0.0

def recompute_score(row):
    mse=float(row["final_layer_mse"])
    eff=float(row.get("effective_compute",row.get("flops_used",0.0)))
    failed=bool(row.get("budget_exhausted") or row.get("time_exhausted") or
                row.get("residual_wall_time_exhausted") or
                row.get("combined_budget_exhausted") or row.get("traceback"))
    mult=1.0 if failed else max(0.1,eff/B)
    return mse*mult

def main():
    parent=json.loads(Path(sys.argv[1]).read_text())
    cand=json.loads(Path(sys.argv[2]).read_text())
    pr=parent["results"]["per_mlp"]; cr=cand["results"]["per_mlp"]
    if len(pr)!=100 or len(cr)!=100: raise SystemExit(f"row count {len(pr)} {len(cr)}")
    names_match=all((a["mlp_index"],a["mlp_name"])==(b["mlp_index"],b["mlp_name"]) for a,b in zip(pr,cr))
    psha=sha_names(pr); csha=sha_names(cr)
    pds=parent["run_config"]["dataset"]["sha256"]; cds=cand["run_config"]["dataset"]["sha256"]
    rows=[]; deltas=[]; improved=0
    for p,c in zip(pr,cr):
        ps=recompute_score(p); cs=recompute_score(c)
        delta=ps-cs; deltas.append(delta)
        if cs<ps: improved+=1
        rows.append({
          "mlp_index":p["mlp_index"],"mlp_name":p["mlp_name"],
          "parent_final_mse":p["final_layer_mse"],"candidate_final_mse":c["final_layer_mse"],
          "parent_adjusted_reported":p["adjusted_final_layer_score"],
          "candidate_adjusted_reported":c["adjusted_final_layer_score"],
          "parent_adjusted_recomputed":ps,"candidate_adjusted_recomputed":cs,
          "adjusted_delta_parent_minus_candidate":delta,
          "parent_flops":p["flops_used"],"candidate_flops":c["flops_used"],
          "parent_residual_s":p["residual_wall_time_s"],"candidate_residual_s":c["residual_wall_time_s"],
          "parent_failed":bool(p.get("residual_wall_time_exhausted") or p.get("budget_exhausted") or p.get("time_exhausted") or p.get("traceback")),
          "candidate_failed":bool(c.get("residual_wall_time_exhausted") or c.get("budget_exhausted") or c.get("time_exhausted") or c.get("traceback"))
        })
    cmse=mean([float(r["final_layer_mse"]) for r in cr])
    cscore=mean([recompute_score(r) for r in cr])
    cflops=mean([float(r["effective_compute"]) for r in cr])
    ccb=cflops/B
    failures=sum(1 for r in rows if r["candidate_failed"])
    dmean=mean(deltas); dse=se(deltas)
    maxres=max(float(r["residual_wall_time_s"]) for r in cr)
    gates={
      "exact_panel_name_order": names_match and psha==EXPECTED_NAMES_SHA and csha==EXPECTED_NAMES_SHA,
      "dataset_sha_identical": pds==EXPECTED_DATASET_SHA and cds==EXPECTED_DATASET_SHA,
      "candidate_failures_zero": failures==0,
      "candidate_mean_raw_mse_lt_parent": cmse<PARENT_MSE,
      "candidate_mean_adjusted_le_0p995_parent": cscore<=TARGET_SCORE,
      "improves_at_least_55_of_100": improved>=55,
      "paired_delta_mean_gt_2se": dmean>2*dse,
      "candidate_mean_cb_le_parent_plus_1e_5": ccb<=PARENT_CB+1e-5,
      "max_residual_lt_0p4": maxres<0.4
    }
    result={
      "schema":"arc.whitebox.r223.v25_local_feed_result.v1",
      "experiment":"R223","idempotency_key":"ARC-R223-V25-LOCAL-FEED-LAMBDA-20260922",
      "parent":{"mean_mse":PARENT_MSE,"mean_adjusted":PARENT_SCORE,"mean_c_over_b":PARENT_CB,
                "names_sha256":psha,"dataset_sha256":pds},
      "candidate":{"mean_mse":cmse,"mean_adjusted":cscore,"mean_effective_compute":cflops,
                   "mean_c_over_b":ccb,"failures":failures,"max_residual_s":maxres,
                   "names_sha256":csha,"dataset_sha256":cds},
      "paired":{"improved_networks":improved,"delta_mean":dmean,"delta_se":dse,
                "delta_mean_over_se":(dmean/dse if dse else None)},
      "gates":gates,"development_go":all(gates.values()),
      "decision":"R223_DEVELOPMENT_GO_V25_LOCAL_FEED" if all(gates.values()) else "R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED",
      "per_network":rows
    }
    Path(sys.argv[3]).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("R223_RESULT="+json.dumps({k:v for k,v in result.items() if k!="per_network"},sort_keys=True))

if __name__=="__main__": main()
