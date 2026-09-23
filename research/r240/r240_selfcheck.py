#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("r240v",HERE/"r240_verify_r223_attempt6.py")
assert SPEC and SPEC.loader
v=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)

def row(i,mse=1.0,cfrac=0.3,error_code=None):
    return {
        "mlp_index":i,
        "mlp_name":f"synthetic-{i:03d}",
        "final_layer_mse":float(mse),
        "adjusted_final_layer_score":float(mse)*cfrac,
        "effective_compute":float(cfrac*v.BUDGET),
        "flops_used":int(cfrac*v.BUDGET),
        "residual_wall_time_s":0.1,
        "budget_exhausted":False,
        "time_exhausted":False,
        "residual_wall_time_exhausted":False,
        "combined_budget_exhausted":False,
        "error_code":error_code,
        "traceback":None,
    }

def report(rows,ds="synthetic-dataset"):
    return {
        "run_config":{"dataset":{"sha256":ds}},
        "results":{
            "per_mlp":rows,
            "adjusted_final_layer_score":sum(v.official_score(r) for r in rows)/len(rows),
        },
    }

def main():
    out={}

    p=[row(i,1.0,0.3) for i in range(100)]
    c=[row(i,0.8,0.3) for i in range(100)]
    out["identity_100_pass"]=v.row_identity(p,c)
    c_bad=[dict(x) for x in c]
    c_bad[77]["mlp_name"]="wrong"
    out["identity_mutation_rejected"]=not v.row_identity(p,c_bad)

    valid=row(0,mse=2.0,cfrac=0.5)
    out["official_score_valid"]=v.official_score(valid)
    out["official_score_valid_expected"]=1.0
    out["official_score_valid_pass"]=abs(v.official_score(valid)-1.0)<1e-15

    fail=row(0,mse=2.0,cfrac=0.1,error_code="PREDICT_EXCEPTION")
    # Canonical failure multiplier must be 1.0, not the 0.1 floor.
    out["error_code_only_is_failure"]=v.is_failed(fail)
    out["failure_penalty_score"]=v.official_score(fail)
    out["failure_penalty_pass"]=abs(v.official_score(fail)-2.0)<1e-15

    old={
      "EXPECTED_NAMES_SHA":v.EXPECTED_NAMES_SHA,
      "EXPECTED_DATASET_SHA":v.EXPECTED_DATASET_SHA,
      "PARENT_MSE":v.PARENT_MSE,
      "PARENT_SCORE":v.PARENT_SCORE,
      "PARENT_CB":v.PARENT_CB,
      "TARGET_SCORE":v.TARGET_SCORE,
    }
    try:
        v.EXPECTED_NAMES_SHA=v.names_sha(p)
        v.EXPECTED_DATASET_SHA="synthetic-dataset"
        v.PARENT_MSE=1.0
        v.PARENT_SCORE=0.3
        v.PARENT_CB=0.3
        v.TARGET_SCORE=0.299
        gates=v.apply_frozen_gates(
            report(p),report(c),provenance_ok=True,observed_candidate_panel_runs=1
        )
        out["all_frozen_gates_synthetic_pass"]=gates["development_go"]
        out["synthetic_gate_values"]=gates["gates"]
        two_runs=v.apply_frozen_gates(
            report(p),report(c),provenance_ok=True,observed_candidate_panel_runs=2
        )
        out["two_runs_rejected"]=not two_runs["gates"]["only_one_candidate_panel_run"]
        failed_c=[dict(x) for x in c]
        failed_c[0]["error_code"]="PREDICT_EXCEPTION"
        failed_c[0]["adjusted_final_layer_score"]=failed_c[0]["final_layer_mse"]
        fgate=v.apply_frozen_gates(
            report(p),report(failed_c),provenance_ok=True,observed_candidate_panel_runs=1
        )
        out["error_code_failure_breaks_zero_failure_gate"]=not fgate["gates"]["candidate_failures_zero"]
    finally:
        for k,val in old.items(): setattr(v,k,val)

    with tempfile.TemporaryDirectory(prefix="r240-selfcheck-") as td:
        root=Path(td)
        ev=root/"r223_attempt6_evidence"
        ev.mkdir()
        for name in sorted(v.MANDATORY_EVIDENCE):
            (ev/name).write_text("{}\n" if name.endswith(".json") else "0\n",encoding="utf-8")
        manifest={}
        for pth in sorted(ev.iterdir()):
            if pth.name=="sha256.json": continue
            manifest[pth.name]=hashlib.sha256(pth.read_bytes()).hexdigest()
        (ev/"sha256.json").write_text(json.dumps(manifest,sort_keys=True)+"\n",encoding="utf-8")
        good=v.verify_manifest(root)
        out["manifest_complete_pass"]=good["ok"]
        (ev/"run.exit").write_text("tampered\n",encoding="utf-8")
        bad=v.verify_manifest(root)
        out["manifest_tamper_rejected"]=not bad["ok"] and bool(bad["hash_mismatches"])

    required=[
      "identity_100_pass","identity_mutation_rejected","official_score_valid_pass",
      "error_code_only_is_failure","failure_penalty_pass",
      "all_frozen_gates_synthetic_pass","two_runs_rejected",
      "error_code_failure_breaks_zero_failure_gate","manifest_complete_pass",
      "manifest_tamper_rejected",
    ]
    out["required_checks"]=required
    out["pass"]=all(bool(out[k]) for k in required)
    print(json.dumps(out,indent=2,sort_keys=True))
    if not out["pass"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
