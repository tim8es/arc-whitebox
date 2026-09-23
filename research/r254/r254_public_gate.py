#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
R209_ADJ=8.170397440117225e-9
MAX_ADJ=0.95*R209_ADJ
R209_FLOPS=806303721965.0
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--candidate-report",required=True);ap.add_argument("--r209",required=True);ap.add_argument("--identity",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 report=json.loads(Path(a.candidate_report).read_text());base=json.loads(Path(a.r209).read_text())["per_network"];ident=json.loads(Path(a.identity).read_text())
 rows=report["results"]["per_mlp"]
 names=[r["mlp_name"] for r in rows];bn=[r["name"] for r in base]
 cand=[float(r["adjusted_final_layer_score"]) for r in rows];par=[float(r["official_adjusted_score"]) for r in base]
 diffs=[p-c for p,c in zip(par,cand)];mean=sum(diffs)/len(diffs)
 var=sum((x-mean)**2 for x in diffs)/(len(diffs)-1);se=math.sqrt(var/len(diffs))
 mean_adj=float(report["results"]["adjusted_final_layer_score"]);failed=int(report["results"]["n_failed_mlps"])
 mean_flops=sum(float(r["flops_used"]) for r in rows)/len(rows)
 max_res=max(float(r["residual_wall_time_s"]) for r in rows)
 improved=sum(c<p for c,p in zip(cand,par))
 gates={
  "exact_identity":bool(ident["exact_r209_row_order_network_target_identity"]) and len(rows)==100 and names==bn,
  "zero_failures":failed==0,
  "adjusted_le_0p95_r209":mean_adj<=MAX_ADJ,
  "improved_rows_ge_55":improved>=55,
  "paired_gain_gt_2se":mean>2.0*se,
  "mean_flops_le_r209":mean_flops<=R209_FLOPS,
  "max_residual_lt_0p4":max_res<0.4}
 out={"schema":"arc.r254.public_gate.v1","gates":gates,"go":all(gates.values()),"rows":len(rows),
      "mean_adjusted_score":mean_adj,"max_adjusted_score":MAX_ADJ,"improved_rows":improved,
      "paired_mean_gain":mean,"paired_descriptive_se":se,"mean_flops":mean_flops,
      "max_residual_wall_time_s":max_res,"n_failed_mlps":failed,"rank_claim":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,sort_keys=True))
 return 0 if out["go"] else 43
if __name__=="__main__":raise SystemExit(main())
