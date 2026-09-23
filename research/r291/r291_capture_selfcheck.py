#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, struct, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("r291_capture",HERE/"r291_capture_harness.py"); assert SPEC and SPEC.loader
h=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(h)
class FakeDType:
    byteorder="="
    def __str__(self): return "float32"
class FakeArray:
    dtype=FakeDType()
    def __init__(self,raw,shape): self._raw=bytes(raw); self.shape=shape
    def tobytes(self,order="C"): assert order=="C"; return self._raw
def rep(v,n): return struct.pack("<f",v)*n
def sha(b): return hashlib.sha256(b).hexdigest()
def mse(p,t):
    s=0.0;n=0
    for (a,),(b,) in zip(struct.iter_unpack("<f",p),struct.iter_unpack("<f",t)):
        d=a-b;s+=d*d;n+=1
    return s/n
def main():
    out={}
    with tempfile.TemporaryDirectory(prefix="r291-selfcheck-") as td:
        root=Path(td); names=[f"synthetic-{i:03d}" for i in range(h.ROWS)]
        oldn,oldm=h.EXPECTED_NAME_ORDER_SHA256,h.EXPECTED_DATASET_METADATA_SHA256
        h.EXPECTED_NAME_ORDER_SHA256=sha(json.dumps(names,separators=(",",":")).encode()); h.EXPECTED_DATASET_METADATA_SHA256="synthetic-metadata"
        recs=[]; inputs=[]
        for i,name in enumerate(names):
            target=rep((i+1)/256.0,h.WIDTH); pred=b"\0"*h.VECTOR_BYTES if i==17 else rep(i/256.0,h.WIDTH); all_t=b"\0"*((h.DEPTH-1)*h.VECTOR_BYTES)+target
            recs.append({"scorer_mlp_index":i,"mlp_name":name,"network_id":str(10000+i),"r224_target_all_sha256":sha(all_t)}); inputs.append((pred,target,all_t))
        panel={"source":{"dataset":{"metadata_sha256":"synthetic-metadata"}},"records":recs}; pp=root/"panel.json"; pp.write_text(json.dumps(panel)+"\n")
        cap=root/"capture"; s=h.CaptureSession(cap,pp,{"r291_run_id":"synthetic","r291_workflow_run_id":"none","r291_capture_code_commit":"0"*40,"r291_capture_code_blob":"0"*40})
        before=[];after=[];preserved=True
        for i,(p,t,a) in enumerate(inputs):
            po,to,ao=FakeArray(p,(h.WIDTH,)),FakeArray(t,(h.WIDTH,)),FakeArray(a,(h.DEPTH,h.WIDTH)); bp,bt=po.tobytes(),to.tobytes();before.append(mse(bp,bt))
            s.safe_capture(scorer_mlp_index=i,mlp_name=names[i],final_pred=po,final_target=to,all_target=ao,budget_exhausted=False,time_exhausted=False,residual_wall_time_exhausted=False,combined_budget_exhausted=False,error_code="SYNTHETIC_EXCEPTION" if i==17 else None,flops_used=0 if i==17 else 123,effective_compute=0.0 if i==17 else 123.0)
            preserved &= bp==po.tobytes() and bt==to.tobytes();after.append(mse(po.tobytes(),to.tobytes()))
        report=root/"report.json";report.write_text('{"synthetic":true}\n'); sealed=h.seal_staged_capture(cap,report); man=json.loads((cap/"manifest.json").read_text()); vec=(cap/"vectors.f32le").read_bytes()
        out.update(serialization_sealed=man["status"]=="SEALED",rows_100=len(man["records"])==100,raw_payload_exact=len(vec)==1228800,storage_bound=sealed["uncompressed_bytes"]<=h.UNCOMPRESSED_MAX_BYTES,fit_eval_50_50=sum(r["split_role"]=="FIT" for r in man["records"])==50 and sum(r["split_role"]=="EVAL" for r in man["records"])==50,failure_zero_row_preserved=man["records"][17]["scored_prediction_zeroed"] and vec[17*h.RECORD_BYTES:17*h.RECORD_BYTES+h.VECTOR_BYTES]==b"\0"*h.VECTOR_BYTES,scorer_inputs_unchanged=preserved,synthetic_scorer_outputs_unchanged=before==after,target_all_hash_verified=all(r["r224_target_all_sha256_expected"]==r["r224_target_all_sha256_observed"] for r in man["records"]))
        first=vec[:h.RECORD_BYTES]; p=first[:h.VECTOR_BYTES];t=first[h.VECTOR_BYTES:2*h.VECTOR_BYTES];r=first[2*h.VECTOR_BYTES:];out["residual_exact"]=r==h._residual_f32le(t,p);out["record_hash_exact"]=sha(first)==man["records"][0]["record_payload_sha256"]
        bad=root/"bad";b=h.CaptureSession(bad,pp,{"r291_run_id":"bad","r291_workflow_run_id":"none","r291_capture_code_commit":"0"*40,"r291_capture_code_blob":"0"*40}); sentinel={"score":7.25}
        b.safe_capture(scorer_mlp_index=0,mlp_name=names[0],final_pred=FakeArray(b"\0"*16,(4,)),final_target=FakeArray(inputs[0][1],(h.WIDTH,)),all_target=FakeArray(inputs[0][2],(h.DEPTH,h.WIDTH)),budget_exhausted=False,time_exhausted=False,residual_wall_time_exhausted=False,combined_budget_exhausted=False,error_code=None,flops_used=1,effective_compute=1.0)
        out["capture_error_isolated"]=b.disabled and (bad/"capture_error.txt").exists() and sentinel=={"score":7.25}
        patch=(HERE/"R291_WHESTBENCH_0_16_1_INTEGRATION.patch").read_text(); removed=[x for x in patch.splitlines() if x.startswith("-") and not x.startswith("---")];added=[x[1:] for x in patch.splitlines() if x.startswith("+") and not x.startswith("+++")];crit=re.compile(r"^\s*(predictions|pred_np|final_pred|final_target|final_layer_mse|all_layers_mse|adjusted_final_layer_score|flops_used|effective_compute|budget_exhausted|time_exhausted|residual_wall_time_exhausted|combined_budget_exhausted)\s*=")
        out["patch_deletes_no_scorer_code"]=not removed;out["patch_assigns_no_scorer_state"]=not any(crit.search(x) and not x.rstrip().endswith(",") for x in added);out["patch_has_two_pre_mse_calls"]=patch.count("r291_capture.safe_capture(")==2;out["patch_no_return_change"]="return {" not in "\n".join(added)
        h.EXPECTED_NAME_ORDER_SHA256,h.EXPECTED_DATASET_METADATA_SHA256=oldn,oldm
    required=list(out); out["pass"]=all(bool(out[k]) for k in required);out["required_checks"]=required; print(json.dumps(out,indent=2,sort_keys=True)); raise SystemExit(0 if out["pass"] else 1)
if __name__=="__main__": main()
