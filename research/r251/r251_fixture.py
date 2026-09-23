#!/usr/bin/env python3
"""Reconstruct the frozen R251 production-shaped target-free fixture exactly."""
from __future__ import annotations
import argparse, hashlib, json, pathlib
import numpy as np

WIDTH=1024
DEPTH=16
SEED=251001
EXPECTED_LAYER_SHA256=["b873f8ed174a1347ad92e1550ecaea4a9144bf381f4e052a09b641366f94df83","ecc5b274d92c9fcdf2032e3c14f5409f39274fa28e78cc8a244e0e91d233884c","f69144ec33b5f89307d658728e4682a15490d42d749fda2a99e94cacddd4505a","e016abbcf1db863eb715b91360f091080fcc3c976d12097b408f203cbb290fdf","d826a99c66866357717e12de73dd425e911558acb52d1c38ca65dba724b36453","a924d761a936ac62e31565fb796ed1c3be353ee9c7b58fe269296bafdf60dec5","29657f0a3390d94162480a69503cdcbc87a1efcce8743675f65132c0544e6bd3","217ba760b23f545c868b3e58cfbe595f911c52f597fb0df3796ee5d8bba1cad0","ad5b8638fee1cb8c9d1fbe17a90e69f3a4a60925c0300f2e9b2c18e20967a3da","3fea42b9b36230c6bc6d2fe0f44743c716838f64d9772135c8b51482c88ec21e","979579e0fe092b6ea3aef2e31e08b86fcbe50f928ae977bd8feb96a1d4abc1d7","0be2bea3f17f17cf2bb7b966d78a0726c49611da7088a32fbdbbd5386f532878","f360375aa83d14d38f97dbb42733bea715158b2df789211745d14f8af46dc1fa","406909107437a0d614ebf9b4472a143a68a5078d150dcee571d16a10878b7be3","a9261f622359fc04451f6ed806d3738405050e91b86b603311646afdfa39f59c","86c62598613a17031a87797faefb62a16bb1e367474fb52d9d6fd00aaaf11b4a"]
EXPECTED_CONCAT_SHA256="3b94abf468e6d829c5caf55096cbb13946a3ed042a92815eb718c5c8c501ff1a"
EXPECTED_TRUTH_SHA256="8e326c2c124ac70b41afb64ada24317430bb18c0a459428044094b1d954b0876"

def build():
    idx=np.arange(WIDTH,dtype=np.int64)
    weights=[]
    truth=np.empty((DEPTH,WIDTH),dtype=np.float64)
    coef=np.ones(WIDTH,dtype=np.float64)
    phi0=0.3989422804014327  # frozen 1/sqrt(2*pi); no runtime math.*
    agg=hashlib.sha256()
    got=[]
    for l in range(DEPTH):
        a=2*l+1
        b=(SEED+37*l)%WIDTH
        p=(a*idx+b)%WIDTH
        q=((idx+3*l)%9)-4
        scale=(1.0+q.astype(np.float64)/64.0).astype(np.float32)
        w=np.zeros((WIDTH,WIDTH),dtype=np.float32)
        w[idx,p]=scale
        raw=w.tobytes(order="C")
        got.append(hashlib.sha256(raw).hexdigest())
        agg.update(raw)
        weights.append(w)
        nc=np.empty_like(coef)
        nc[p]=coef*scale.astype(np.float64)
        coef=nc
        truth[l]=coef*phi0
    assert got==EXPECTED_LAYER_SHA256, (got,EXPECTED_LAYER_SHA256)
    assert agg.hexdigest()==EXPECTED_CONCAT_SHA256
    assert hashlib.sha256(truth.astype("<f8").tobytes(order="C")).hexdigest()==EXPECTED_TRUTH_SHA256
    return weights,truth

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=pathlib.Path)
    args=ap.parse_args()
    weights,truth=build()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        np.savez(args.out,truth=truth,**{f"w{i:02d}":w for i,w in enumerate(weights)})
    print(json.dumps({"layer_sha256":EXPECTED_LAYER_SHA256,"dense_concat_sha256":EXPECTED_CONCAT_SHA256,"truth_sha256":EXPECTED_TRUTH_SHA256},sort_keys=True))

if __name__=="__main__":
    main()
