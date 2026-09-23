#!/usr/bin/env python3
"""Conditional exact R209 public mini-100 identity gate for R254."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from datasets import load_dataset
from huggingface_hub import hf_hub_download
DATASET="aicrowd/arc-whestbench-public-2026";REVISION="v2-phase2";SPLIT="mini"
META_SHA="264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--r209",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 r209=json.loads(Path(a.r209).read_text()); expected=r209["per_network"]
 meta=Path(hf_hub_download(DATASET,"metadata.json",repo_type="dataset",revision=REVISION))
 if sha(meta.read_bytes())!=META_SHA:raise RuntimeError("dataset metadata hash mismatch")
 ds=load_dataset(DATASET,revision=REVISION,split=SPLIT,streaming=True)
 ds=ds.select_columns(["mlp_name","mlp_seed","all_layer_means"]).with_format("numpy")
 live=[]
 for i,row in enumerate(ds):
  t=np.ascontiguousarray(np.asarray(row["all_layer_means"]),dtype=np.float32)
  if t.shape!=(16,1024):raise RuntimeError(f"target shape row {i}: {t.shape}")
  live.append({"name":str(row["mlp_name"]),"network_id":str(int(row["mlp_seed"])),"target_sha256":sha(t.tobytes())})
 if len(live)!=100 or len(expected)!=100:raise RuntimeError("row count")
 exp=[{"name":str(x["name"]),"network_id":str(x["network_id"]),"target_sha256":str(x["target_sha256"])} for x in expected]
 ok=live==exp
 out={"schema":"arc.r254.public_identity.v1","metadata_sha256":META_SHA,"rows":len(live),
      "exact_r209_row_order_network_target_identity":ok,
      "live_sequence_sha256":sha(json.dumps(live,separators=(",",":"),sort_keys=True).encode()),
      "expected_sequence_sha256":sha(json.dumps(exp,separators=(",",":"),sort_keys=True).encode())}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out,sort_keys=True))
 return 0 if ok else 42
if __name__=="__main__":raise SystemExit(main())
