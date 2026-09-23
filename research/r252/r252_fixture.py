#!/usr/bin/env python3
"""Frozen R252-BLOCK2-252001 target-free production-shape fixture.

Research harness only. Numerical truth here is not participant estimator work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

WIDTH = 1024
DEPTH = 16
SEED = 252001
FIXTURE_ID = "R252-BLOCK2-252001"

LIB = np.array(
    [
        [[1.0, 0.5], [-0.25, 1.0]],
        [[1.0, -0.25], [0.5, 1.0]],
        [[0.75, 0.5], [-0.25, 1.0]],
        [[1.0, 0.25], [-0.5, 0.75]],
        [[0.75, -0.25], [0.5, 1.0]],
        [[1.0, 0.5], [-0.5, 0.75]],
    ],
    dtype=np.float32,
)

EXPECTED_LAYER_SHA256 = [
    "e362f0d299ce358fd1dadfe5f6a5f1a5fe527070ea29bc5c31642a7dbc9a7687",
    "5b1babad28b93d22d44f7db0c0b62732554f522c5f9d90f728c990a0f73891fa",
    "c60d1c743681b8cd088dd57c479f2edcb0d4bd93b7cb5d53760b0736a78e9cfa",
    "fe3b0d41558dc098b85c52fba324b9e15db228860cd6115136c37aa60788a78a",
    "5baa5a18e324b74a44a010644fd2a2882c50dc3d3043fe1f168962e283aee79b",
    "154853f59eb55d067bf38f2e24b786c9fbd323db96f3efaeb3902aeb49c17d0a",
    "e362f0d299ce358fd1dadfe5f6a5f1a5fe527070ea29bc5c31642a7dbc9a7687",
    "5b1babad28b93d22d44f7db0c0b62732554f522c5f9d90f728c990a0f73891fa",
    "c60d1c743681b8cd088dd57c479f2edcb0d4bd93b7cb5d53760b0736a78e9cfa",
    "fe3b0d41558dc098b85c52fba324b9e15db228860cd6115136c37aa60788a78a",
    "5baa5a18e324b74a44a010644fd2a2882c50dc3d3043fe1f168962e283aee79b",
    "154853f59eb55d067bf38f2e24b786c9fbd323db96f3efaeb3902aeb49c17d0a",
    "e362f0d299ce358fd1dadfe5f6a5f1a5fe527070ea29bc5c31642a7dbc9a7687",
    "5b1babad28b93d22d44f7db0c0b62732554f522c5f9d90f728c990a0f73891fa",
    "c60d1c743681b8cd088dd57c479f2edcb0d4bd93b7cb5d53760b0736a78e9cfa",
    "fe3b0d41558dc098b85c52fba324b9e15db228860cd6115136c37aa60788a78a",
]
EXPECTED_WEIGHTS_SHA256 = "1ed998cad7f2ba4c8259f70a241913359ac49b7b0252d91a0c578539893ddfb0"
EXPECTED_TRUTH_SHA256 = "0803ca4d381ad13ab0842fcd4775a3e4b1ad2f1409f517d196ac89073c479946"


def block_index(layer: int, block: int) -> int:
    return (SEED + 17 * layer + 29 * block + 7 * layer * block) % len(LIB)


def build_weights() -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for layer in range(DEPTH):
        w = np.zeros((WIDTH, WIDTH), dtype=np.float32)
        for block in range(WIDTH // 2):
            i = 2 * block
            w[i : i + 2, i : i + 2] = LIB[block_index(layer, block)]
        out.append(w)
    return out


def _roots_in_interval(row: np.ndarray, lo: float, hi: float) -> list[float]:
    a = float(row[0])
    b = float(row[1])
    if abs(a) + abs(b) < 1.0e-30:
        return []
    base = math.atan2(-a, b)
    k0 = math.floor((lo - base) / math.pi) - 1
    k1 = math.ceil((hi - base) / math.pi) + 1
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1.0e-14 < x < hi - 1.0e-14:
            roots.append(x)
    return roots


def _propagate_regions(
    regions: list[tuple[float, float, np.ndarray]], weight: np.ndarray
) -> list[tuple[float, float, np.ndarray]]:
    # Parent uses W = weight.T and preactivation = W @ state.
    W = weight.T.astype(np.float64)
    out: list[tuple[float, float, np.ndarray]] = []
    for lo, hi, A in regions:
        M = W @ A
        cuts = [lo, hi]
        for row in M:
            cuts.extend(_roots_in_interval(row, lo, hi))
        cuts.sort()
        unique = [cuts[0]]
        for x in cuts[1:]:
            if x - unique[-1] > 1.0e-13:
                unique.append(x)
        for a, b in zip(unique[:-1], unique[1:]):
            mid = 0.5 * (a + b)
            u = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
            A2 = M.copy()
            A2[(M @ u) <= 0.0, :] = 0.0
            out.append((a, b, A2))
    merged: list[tuple[float, float, np.ndarray]] = []
    for reg in out:
        if (
            merged
            and abs(merged[-1][1] - reg[0]) < 1.0e-12
            and np.array_equal(merged[-1][2], reg[2])
        ):
            merged[-1] = (merged[-1][0], reg[1], reg[2])
        else:
            merged.append(reg)
    return merged


def _mean_regions(regions: list[tuple[float, float, np.ndarray]]) -> np.ndarray:
    integ = np.zeros(2, dtype=np.float64)
    for lo, hi, A in regions:
        trig_int = np.array(
            [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
            dtype=np.float64,
        )
        integ += A @ trig_int
    radial_mean = math.sqrt(math.pi / 2.0)
    return integ * (radial_mean / (2.0 * math.pi))


def exact_truth() -> tuple[np.ndarray, np.ndarray]:
    truth = np.empty((DEPTH, WIDTH), dtype=np.float64)
    region_counts = np.empty((DEPTH, WIDTH // 2), dtype=np.int16)
    for block in range(WIDTH // 2):
        regions = [(0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))]
        for layer in range(DEPTH):
            regions = _propagate_regions(regions, LIB[block_index(layer, block)])
            truth[layer, 2 * block : 2 * block + 2] = _mean_regions(regions)
            region_counts[layer, block] = len(regions)
    return truth, region_counts


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest(weights: list[np.ndarray], truth: np.ndarray, counts: np.ndarray) -> dict:
    layer_hashes = []
    agg = hashlib.sha256()
    for w in weights:
        raw = w.astype("<f4", copy=False).tobytes(order="C")
        layer_hashes.append(sha256_bytes(raw))
        agg.update(raw)
    truth_raw = truth.astype("<f8", copy=False).tobytes(order="C")
    manifest = {
        "schema": "arc.r252.fixture.v1",
        "fixture_id": FIXTURE_ID,
        "seed": SEED,
        "width": WIDTH,
        "depth": DEPTH,
        "weight_dtype": "float32-le",
        "truth_dtype": "float64-le",
        "layer_weight_sha256": layer_hashes,
        "weights_concat_sha256": agg.hexdigest(),
        "truth_sha256": sha256_bytes(truth_raw),
        "truth_shape": list(truth.shape),
        "truth_min": float(np.min(truth)),
        "truth_max": float(np.max(truth)),
        "region_count_min": int(np.min(counts)),
        "region_count_max": int(np.max(counts)),
        "construction": "512 independent deterministic 2x2 dyadic blocks per layer",
        "truth_method": "analytic angular piecewise-linear integration times Rayleigh radial mean",
    }
    if layer_hashes != EXPECTED_LAYER_SHA256:
        raise RuntimeError("layer hash mismatch")
    if manifest["weights_concat_sha256"] != EXPECTED_WEIGHTS_SHA256:
        raise RuntimeError("aggregate weight hash mismatch")
    if manifest["truth_sha256"] != EXPECTED_TRUTH_SHA256:
        raise RuntimeError("truth hash mismatch")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    weights = build_weights()
    truth, counts = exact_truth()
    manifest = build_manifest(weights, truth, counts)
    np.savez_compressed(
        out / "R252_BLOCK2_252001.npz",
        weights=np.stack(weights),
        truth=truth,
        region_counts=counts,
    )
    (out / "R252_FIXTURE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
