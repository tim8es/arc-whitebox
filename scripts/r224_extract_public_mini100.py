#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from datasets import load_dataset
from huggingface_hub import hf_hub_download

DATASET="aicrowd/arc-whestbench-public-2026"
REVISION="v2-phase2"
SPLIT="mini"
EXPECTED_METADATA_SHA="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAME_SHA="18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
FIRST5=[
 ("logan-fitzgerald","6319981554997072999","713d7f4b5f8dc36c53763046e57b25793c4d44e8d93f82174589be132e45af82"),
 ("william-graves","2392109381927064353","94aceb2899414d669f70fc28116ea77c1709d65c1264892ed7e68b0add73cfc4"),
 ("raymond-barnes","4030325997523501402","5f0c2d71ebe42446124e2bc481f966b7836e4295c1a6e30ba49bc49c53edcd34"),
 ("steven-rice","6959524404880716684","c119d75f202a5aff3182f13653924915626797844fcc3e48a3df3886e8410d1b"),
 ("sarah-kelley","3958198382245770826","aceb6cb1873b1b5ad81156a61a30f78139d3824a10670fba990052d5884e93a9"),
]
def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--expected-names",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); args=ap.parse_args()
 expected=json.loads(args.expected_names.read_text())
 meta=Path(hf_hub_download(DATASET,"metadata.json",repo_type="dataset",revision=REVISION))
 meta_sha=sha_bytes(meta.read_bytes())
 if meta_sha!=EXPECTED_METADATA_SHA: raise SystemExit(f"metadata sha mismatch {meta_sha}")
 info=Path(hf_hub_download(DATASET,"prepared/mini/dataset_info.json",repo_type="dataset",revision=REVISION))
 info_obj=json.loads(info.read_text())
 feat=info_obj["features"]
 if feat["mlp_seed"]["dtype"]!="int64": raise SystemExit("mlp_seed dtype mismatch")
 if feat["all_layer_means"]["dtype"]!="float32" or feat["all_layer_means"]["shape"]!=[16,1024]: raise SystemExit("target schema mismatch")
 ds=load_dataset(DATASET,revision=REVISION,split=SPLIT,streaming=True)
 ds=ds.select_columns(["mlp_id","mlp_name","mlp_seed","all_layer_means"]).with_format("numpy")
 records=[]
 for i,row in enumerate(ds):
  target=np.asarray(row["all_layer_means"])
  if target.dtype!=np.float32 or target.shape!=(16,1024): raise SystemExit(f"target dtype/shape mismatch row {i}: {target.dtype} {target.shape}")
  target=np.ascontiguousarray(target,dtype=np.float32)
  records.append({"mlp_index":i,"mlp_id":int(row["mlp_id"]),"mlp_name":str(row["mlp_name"]),"mlp_seed":str(int(row["mlp_seed"])),"network_id":str(int(row["mlp_seed"])),"target_sha256":sha_bytes(target.tobytes()),"target_dtype":str(target.dtype),"target_shape":[16,1024]})
 if len(records)!=100: raise SystemExit(f"row count {len(records)}")
 names=[r["mlp_name"] for r in records]
 if names!=expected: raise SystemExit("100-name/order mismatch vs R209")
 name_sha=sha_bytes(json.dumps(names,separators=(",",":")).encode())
 if name_sha!=EXPECTED_NAME_SHA: raise SystemExit(f"name hash mismatch {name_sha}")
 if len({r["network_id"] for r in records})!=100: raise SystemExit("network_id not unique")
 if len({r["target_sha256"] for r in records})!=100: raise SystemExit("target hashes not unique")
 for i,(name,nid,th) in enumerate(FIRST5):
  r=records[i]
  if (r["mlp_name"],r["network_id"],r["target_sha256"])!=(name,nid,th): raise SystemExit(f"first5 control mismatch row {i}: {r}")
 out={"schema":"arc.whitebox.r224.mini100_fingerprints.v1","dataset":{"repo":DATASET,"revision":REVISION,"split":SPLIT,"metadata_sha256":meta_sha,"dataset_info_sha256":sha_bytes(info.read_bytes()),"count":100,"target_dtype":"float32","target_shape":[16,1024]},"canonicalization":{"network_id":"decimal exact int64 mlp_seed","target_sha256":"SHA256 C-contiguous raw float32 all_layer_means bytes","name_order_sha256":name_sha},"first5_controls_verified":True,"records":records}
 args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":"PASS","rows":len(records),"metadata_sha256":meta_sha,"name_order_sha256":name_sha,"out":str(args.out)},sort_keys=True))
if __name__=="__main__": main()
