#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, statistics, sys
from pathlib import Path

B=2199023255552
PARENT_MSE=2.228303490170447e-8
PARENT_SCORE=8.170397440117225e-9
PARENT_FLOPS=806303721965.0
TARGET_SCORE=0.995*PARENT_SCORE
EXPECTED_DATASET_SHA="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAMES_SHA="18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"

def mean(xs): return sum(xs)/len(xs)
def se(xs): return statistics.stdev(xs)/math.sqrt(len(xs)) if len(xs)>1 else 0.0
def names_sha(rows):
    names=[r["mlp_name"] for r in rows]
    return hashlib.sha256(json.dumps(names,separators=(",",":")).encode()).hexdigest()
def failed(r):
    return bool(r.get("error_code") or r.get("budget_exhausted") or r.get("time_exhausted") or
                r.get("residual_wall_time_exhausted") or r.get("combined_budget_exhausted") or
                r.get("traceback"))
def score(r):
    mse=float(r["final_layer_mse"])
    eff=float(r.get("effective_compute",r.get("flops_used",0.0)))
    return mse*(1.0 if failed(r) else max(0.1,eff/B))

def main():
    parent=json.loads(Path(sys.argv[1]).read_text())
    cand=json.loads(Path(sys.argv[2]).read_text())
    norm=json.loads(Path(sys.argv[3]).read_text())
    pr=parent["results"]["per_mlp"]; cr=cand["results"]["per_mlp"]; nr=norm["per_network"]
    if not (len(pr)==len(cr)==len(nr)==100): raise SystemExit("row count mismatch")
    psha=names_sha(pr); csha=names_sha(cr)
    pds=parent["run_config"]["dataset"]["sha256"]; cds=cand["run_config"]["dataset"]["sha256"]
    norm_by_name={r["name"]:r for r in nr}
    rows=[]; deltas=[]; improved=0; target_hashes=[]
    for p,c in zip(pr,cr):
        if (p["mlp_index"],p["mlp_name"])!=(c["mlp_index"],c["mlp_name"]): raise SystemExit("order mismatch")
        nrow=norm_by_name[p["mlp_name"]]
        ps,cs=score(p),score(c); d=ps-cs
        deltas.append(d); improved += int(cs<ps); target_hashes.append(nrow["target_sha256"])
        rows.append({
          "mlp_index":p["mlp_index"],"mlp_name":p["mlp_name"],"network_id":nrow["network_id"],
          "target_sha256":nrow["target_sha256"],
          "parent_final_mse":p["final_layer_mse"],"candidate_final_mse":c["final_layer_mse"],
          "parent_adjusted_reported":p["adjusted_final_layer_score"],
          "candidate_adjusted_reported":c["adjusted_final_layer_score"],
          "parent_adjusted_recomputed":ps,"candidate_adjusted_recomputed":cs,
          "adjusted_delta_parent_minus_candidate":d,
          "parent_flops":p["flops_used"],"candidate_flops":c["flops_used"],
          "parent_residual_s":p["residual_wall_time_s"],"candidate_residual_s":c["residual_wall_time_s"],
          "parent_failed":failed(p),"candidate_failed":failed(c)
        })
    cmse=mean([float(r["final_layer_mse"]) for r in cr])
    cscore=mean([score(r) for r in cr])
    cflops=mean([float(r["effective_compute"]) for r in cr])
    failures=sum(failed(r) for r in cr); maxres=max(float(r["residual_wall_time_s"]) for r in cr)
    dm=mean(deltas); ds=se(deltas)
    panel_ok=(psha==csha==EXPECTED_NAMES_SHA and pds==cds==EXPECTED_DATASET_SHA and
              all(norm_by_name[p["mlp_name"]]["network_id"]==str(p.get("mlp_seed",norm_by_name[p["mlp_name"]]["network_id"])) for p in pr))
    gates={
      "exact_100_panel_identity":panel_ok,
      "candidate_failures_zero":failures==0,
      "candidate_mean_raw_mse_lt_parent":cmse<PARENT_MSE,
      "candidate_mean_adjusted_le_0p995_parent":cscore<=TARGET_SCORE,
      "improves_at_least_55_of_100":improved>=55,
      "paired_delta_mean_gt_2se":dm>2*ds,
      "candidate_mean_flops_le_parent_plus_0p001B":cflops<=PARENT_FLOPS+0.001*B,
      "max_residual_lt_0p4":maxres<0.4
    }
    out={
      "schema":"arc.whitebox.r244.mp_r16_result.v1","experiment":"R244",
      "method":"marginal-preserving Rres factorization, total R_RES=16",
      "parent":{"mean_mse":PARENT_MSE,"mean_adjusted":PARENT_SCORE,"mean_flops":PARENT_FLOPS,
                "names_sha256":psha,"dataset_sha256":pds},
      "candidate":{"mean_mse":cmse,"mean_adjusted":cscore,"mean_effective_compute":cflops,
                   "failures":failures,"max_residual_s":maxres,"names_sha256":csha,"dataset_sha256":cds},
      "paired":{"improved_networks":improved,"delta_mean":dm,"delta_se":ds,
                "delta_mean_over_se":(dm/ds if ds else None)},
      "gates":gates,"development_go":all(gates.values()),
      "decision":"R244_DEVELOPMENT_GO_MP_R16" if all(gates.values()) else "R244_DEVELOPMENT_NO_GO_MP_R16",
      "per_network":rows
    }
    Path(sys.argv[4]).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="per_network"},sort_keys=True))

if __name__=="__main__": main()
