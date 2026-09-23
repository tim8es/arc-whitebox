#!/usr/bin/env python3
"""Frozen R254 production-shape target-free fixture.

Truth uses only fixed-order scalar path products.  No matrix-vector product,
BLAS reduction, Monte Carlo, target data, or backend-dependent reduction is used.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=1024
DEPTH=16
SEED=254001
PHI0=0.3989422804014327
EXPECTED_LAYER_SHA256=[
"f967edbc05dac342f959a957861ef9ddcd6842c31ea757599a5dd95ce9c4f70b",
"883f3edffeef5b303093ef5a4eef306a0e5bf728bfbc5c0092f91442275d4657",
"c68d1c2fd74b68a2d87f9064987ad5d0724389fca3842c3b16578af87650f19d",
"5bee5c4349353741cebb3dde20b32540d8aa83a95fb32cb5cf93524db9942879",
"3fcf3ee044c57359c8afe64835de40c752798a4c48bda4639d701c01c62ba901",
"0209e90b30d1c7b1819b6f0ed9154a61543a643f79ceb5cc52edf17696eb1330",
"eae245458b64c0ba82ee39e57d52ab0998608cfd8d3a9739de172b2e198b42d3",
"44c7062c264876b65e9dda5b0557a7160f7a7fca0751ca2a06a808ccad0980d1",
"d31ed6404013282dbdc9bde6f53553997345e21c25c4032fa0d9bd7c568b5e82",
"c051a5bcd0a22fc48349503e62b578d45a72d18293ba6df21739010946808563",
"b5a013b3b8f432c9b6e574b4d2401526edab62eac8618a969ee4a323ca5d98c7",
"26ab4bdd95997d69c2988efce336023389552c7dcf7d21e4a3f933570e9c5dd3",
"7350018cede1682fb1de9d111b1da3d33bca61bf379b6c8e51bfc0273b3f3145",
"a4efe4d3c1b763913b905de694374751d9be7bb14e361a820935f9286bfac121",
"27711af88771293e4061f8ba8c1d71fc7450b909e4c370026277f616a894e51b",
"a8849df2c45e9e65e214a5b97c68ee7cc8248e5e3f333594aae98b201eabd854"]
EXPECTED_WEIGHTS_SHA256="199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0"
EXPECTED_TRUTH_SHA256="58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d"

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def params(layer:int,col:int)->tuple[int,np.float32]:
    row=((2*layer+1)*col + (37*layer+SEED)%WIDTH) % WIDTH
    q=(col*(2*layer+5)+SEED+97*layer)%513
    s=np.float32((768+q)/1024.0)
    if layer==0 and ((17*col+SEED)%7==0):
        s=np.float32(-s)
    return row,s

def build_primary()->tuple[list[np.ndarray],np.ndarray]:
    weights=[]
    truth=np.empty((DEPTH,WIDTH),dtype=np.float64)
    for layer in range(DEPTH):
        w=np.zeros((WIDTH,WIDTH),dtype=np.float32)
        for col in range(WIDTH):
            row,s=params(layer,col)
            w[row,col]=s
            if layer==0:
                truth[layer,col]=abs(float(s))*PHI0
            else:
                truth[layer,col]=float(s)*truth[layer-1,row]
        weights.append(w)
    return weights,truth

def build_independent_hashes()->dict:
    # Independent flat-buffer implementation: no call to build_primary/params.
    h=hashlib.sha256(); layer_hash=[]; prev=None; truths=[]
    for layer in range(DEPTH):
        flat=np.zeros(WIDTH*WIDTH,dtype="<f4")
        cur=np.empty(WIDTH,dtype="<f8")
        a=2*layer+1; b=(37*layer+SEED)%WIDTH
        for col in range(WIDTH):
            row=(a*col+b)&1023
            q=(col*(2*layer+5)+SEED+97*layer)%513
            val=(768+q)/1024.0
            if layer==0 and ((17*col+SEED)%7==0): val=-val
            f=np.float32(val)
            flat[row*WIDTH+col]=f
            cur[col]=abs(float(f))*PHI0 if layer==0 else float(f)*prev[row]
        raw=flat.tobytes(order="C"); h.update(raw); layer_hash.append(sha(raw))
        truths.append(cur); prev=cur
    truth=np.stack(truths)
    return {"layer_sha256":layer_hash,"weights_concat_sha256":h.hexdigest(),
            "truth_sha256":sha(np.asarray(truth,dtype="<f8").tobytes(order="C"))}

def build_manifest()->tuple[list[np.ndarray],np.ndarray,dict]:
    weights,truth=build_primary()
    layer=[sha(np.asarray(w,dtype="<f4").tobytes(order="C")) for w in weights]
    agg=hashlib.sha256()
    for w in weights: agg.update(np.asarray(w,dtype="<f4").tobytes(order="C"))
    got={"layer_sha256":layer,"weights_concat_sha256":agg.hexdigest(),
         "truth_sha256":sha(np.asarray(truth,dtype="<f8").tobytes(order="C"))}
    replay=build_independent_hashes()
    if got!=replay: raise RuntimeError(f"independent replay mismatch: {got} != {replay}")
    if layer!=EXPECTED_LAYER_SHA256: raise RuntimeError("layer hash mismatch")
    if got["weights_concat_sha256"]!=EXPECTED_WEIGHTS_SHA256: raise RuntimeError("weight concat hash mismatch")
    if got["truth_sha256"]!=EXPECTED_TRUTH_SHA256: raise RuntimeError("truth hash mismatch")
    return weights,truth,{**got,"independent_replay":replay,"replay_equal":True}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-dir",type=Path,required=True); args=ap.parse_args()
    _,truth,m=build_manifest()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    m.update({"fixture_id":"R254-MONOMIAL-PATH-254001","seed":SEED,"width":WIDTH,"depth":DEPTH,
              "truth_min":float(truth.min()),"truth_max":float(truth.max())})
    (args.out_dir/"R254_FIXTURE_RUNTIME_MANIFEST.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
    print(json.dumps(m,sort_keys=True))
if __name__=="__main__": main()
