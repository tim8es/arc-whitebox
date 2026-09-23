#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

WIDTH = 1024
DEPTH = 16
SEED = 252001
PHI0 = 0.3989422804014327

EXPECTED_LAYER_SHA256 = [
    "dae5fc841d3ae8801b8e17f0542c73af73b96f1dd2c58f5d7ce5d6f3f806ce79",
    "a58a2305a12618ea645d649e40383e5a893375cbafc8ca94435fc3d5708036cd",
    "d4df7c5c649e380e3150aad9a9bce819877650dbbd0a079db83d53a62cf4dbef",
    "34047f41bcd430b98b29a02198c1166b74312619811ad9bef2d8f88a9dba5544",
    "a40a635c18dc9fd54765ba31f511d8f2e07b5d2890264f1d45af68722c302f1b",
    "1e29f8b3e7ef3baef3c2768d20e8be90c0741c9c9907ea3738648f4c75a12157",
    "53090fae9f190e54c84cabee7ecc9c66cf506e08f59539f947287ca3d3aaf820",
    "63f2e8a75eb45d820fc70c83ed3e921ff3f69eb7b514d0175e786126a4d92b45",
    "aba44c40d884da3756999de4ee97d05580bab6ff2f210dd83949befc00479e45",
    "76dff38f3497c15f99cdb11df53378441c6f4d05644530387848547eddd1ea05",
    "4fccf3d8a2980c699e855a6b45e0c42c7763a8cba31f56e99277cc1c13c80581",
    "fbe7a64b3dc6e94ec49ea25caf41dc83e4a5c77994780f8d7ebbd630418a685e",
    "9599ac0719278ec13f7ffd332966bf3c7ab44c0fb12bc2ab0dcf59d903d1caca",
    "1a8bad0dc8ce503ced7cec5645082a9bca8423c0e378c174eb3c5c06070eaa11",
    "7c6ee18750f3adefce869b59b907e6a7f154e39319b313e26df57ca0854029dd",
    "e8884bf05efc729ccbb738c756a4b77396281efe68ee6e12bb3555016b829e47",
]
EXPECTED_CONCAT_SHA256 = "de5fcc26bb7eaf45f29175cb292f27091b6b13ab6a4f3dc095be96cf402a8d4e"
EXPECTED_TRUTH_SHA256 = "623f35aaf0a3a9dfc7f9955ea0c45d02b118fc0fa20579f0747116b838d54450"

def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def build_fixture() -> tuple[list[np.ndarray], np.ndarray]:
    idx = np.arange(WIDTH, dtype=np.int64)
    cols = idx
    weights: list[np.ndarray] = []
    w0 = np.zeros((WIDTH, WIDTH), dtype=np.float32)
    w0[idx, cols] = np.float32(0.8)
    w0[(idx + 17) % WIDTH, cols] = np.float32(0.6)
    weights.append(w0)
    for layer in range(1, DEPTH):
        stride = 2 * ((37 * layer + 13) % 511) + 1
        q = ((idx * (2 * layer + 3) + SEED + 97 * layer) % 25) - 12
        scale = (1.0 + q.astype(np.float64) / 512.0).astype(np.float32)
        w = np.zeros((WIDTH, WIDTH), dtype=np.float32)
        w[idx, cols] = np.float32(0.625) * scale
        w[(idx + stride) % WIDTH, cols] = np.float32(0.375) * scale
        weights.append(w)
    truth = np.empty((DEPTH, WIDTH), dtype=np.float64)
    w0_64 = weights[0].astype(np.float64)
    mu = PHI0 * np.sqrt(np.sum(w0_64 * w0_64, axis=0))
    truth[0] = mu
    for layer in range(1, DEPTH):
        mu = weights[layer].astype(np.float64).T @ mu
        truth[layer] = mu
    layer_hashes = [_sha(np.ascontiguousarray(w).tobytes(order="C")) for w in weights]
    if layer_hashes != EXPECTED_LAYER_SHA256:
        raise RuntimeError(f"layer hashes mismatch: {layer_hashes}")
    agg = hashlib.sha256()
    for w in weights:
        agg.update(np.ascontiguousarray(w).tobytes(order="C"))
    if agg.hexdigest() != EXPECTED_CONCAT_SHA256:
        raise RuntimeError(f"concat hash mismatch: {agg.hexdigest()}")
    truth_le = np.ascontiguousarray(truth.astype("<f8", copy=False))
    if _sha(truth_le.tobytes(order="C")) != EXPECTED_TRUTH_SHA256:
        raise RuntimeError("truth hash mismatch")
    return weights, truth

def write_bytes(out_dir: Path, weights: list[np.ndarray], truth: np.ndarray) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    wpath = out_dir / "R252_FIXTURE_WEIGHTS.f32le.bin"
    tpath = out_dir / "R252_FIXTURE_TRUTH.f64le.bin"
    with wpath.open("wb") as f:
        for w in weights:
            f.write(np.ascontiguousarray(w.astype("<f4", copy=False)).tobytes(order="C"))
    tpath.write_bytes(np.ascontiguousarray(truth.astype("<f8", copy=False)).tobytes(order="C"))
    return {
        "weights_path": str(wpath),
        "weights_sha256": _sha(wpath.read_bytes()),
        "truth_path": str(tpath),
        "truth_sha256": _sha(tpath.read_bytes()),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    w1, t1 = build_fixture()
    w2, t2 = build_fixture()
    replay_equal = all(np.array_equal(a, b) for a, b in zip(w1, w2)) and np.array_equal(t1, t2)
    if not replay_equal:
        raise RuntimeError("fixture replay mismatch")
    payload = {
        "schema": "arc.whitebox.r252.fixture_replay.v1",
        "seed": SEED,
        "width": WIDTH,
        "depth": DEPTH,
        "dtype": "float32",
        "layer_sha256": EXPECTED_LAYER_SHA256,
        "dense_concat_sha256": EXPECTED_CONCAT_SHA256,
        "truth_sha256": EXPECTED_TRUTH_SHA256,
        "replay_byte_identical": True,
        "truth_min": float(np.min(t1)),
        "truth_max": float(np.max(t1)),
        "truth_final_mean": float(np.mean(t1[-1])),
    }
    if args.out_dir:
        payload["retained_bytes"] = write_bytes(args.out_dir, w1, t1)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
