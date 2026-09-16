#!/usr/bin/env python3
"""Deterministic E091 synthetic/local reproducibility check.

Reads only the committed E091 feature/corpus freeze files. No benchmark/public data.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e091_loo_ridge import (
    RIDGE_LAMBDA,
    build_features,
    direct_loo_predictions,
    press_loo_predictions,
    ridge_fit,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "research" / "E091_CORPUS_MANIFEST.json"
FEATURE_PATH = ROOT / "research" / "E091_FEATURE_FREEZE.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_feature_row(seed: int, cfg: dict) -> np.ndarray:
    width = int(cfg["width"])
    depth = int(cfg["depth"])
    rng = np.random.Generator(np.random.PCG64(seed))
    weights = [
        rng.normal(0.0, 1.0 / math.sqrt(width), (width, width))
        for _ in range(depth)
    ]
    base = rng.normal(0.0, 0.2, (depth, width))
    state_var = np.exp(rng.normal(-0.1, 0.2, (depth, width)))
    state_d3 = rng.normal(0.0, 0.05, (depth, width))
    return build_features(weights, base, state_var, state_d3)


def make_corpus(cfg: dict):
    X = np.stack([make_feature_row(int(seed), cfg) for seed in cfg["row_seeds"]])
    p = int(cfg["p"])
    q = int(cfg["q"])
    coef_rng = np.random.Generator(np.random.PCG64(int(cfg["target_coefficient_seed"])))
    B_true = coef_rng.normal(0.0, 2e-4, (p, q))
    rows = []
    for i, seed in enumerate(cfg["target_noise_seeds"]):
        rng = np.random.Generator(np.random.PCG64(int(seed)))
        eps = rng.normal(0.0, 2e-5, q)
        rows.append(X[i] @ B_true + eps)
    return X, np.stack(rows)


def run_check() -> dict:
    cfg = json.loads(MANIFEST_PATH.read_text())
    if cfg["schema"] != "arc.whitebox.e091.synthetic_corpus.v2":
        raise AssertionError("unexpected E091 corpus schema")
    if cfg["public_or_benchmark_data"] is not False:
        raise AssertionError("E091 local corpus must be synthetic-only")
    if float(cfg["ridge_lambda"]) != RIDGE_LAMBDA:
        raise AssertionError("ridge lambda differs from frozen implementation")

    params = tuple(inspect.signature(build_features).parameters)
    if params != ("weights", "base_prediction", "state_var", "state_d3"):
        raise AssertionError(f"feature API is not target-free: {params}")

    X, Z = make_corpus(cfg)
    press, h, B = press_loo_predictions(X, Z, RIDGE_LAMBDA)
    direct = direct_loo_predictions(X, Z, RIDGE_LAMBDA)

    max_abs = float(np.max(np.abs(press - direct)))
    rel_frob = float(np.linalg.norm(press - direct) / np.linalg.norm(direct))

    delta = np.resize(np.asarray([11.0, -7.0, 5.0, 13.0], dtype=np.float64), Z.shape[1])
    self_target_max = 0.0
    for i in range(X.shape[0]):
        Z2 = Z.copy()
        Z2[i] += delta
        press2, _, _ = press_loo_predictions(X, Z2, RIDGE_LAMBDA)
        self_target_max = max(self_target_max, float(np.max(np.abs(press2[i] - press[i]))))

    X2, Z2 = make_corpus(cfg)
    B2, _ = ridge_fit(X2, Z2, RIDGE_LAMBDA)
    deterministic = {
        "X_bitwise": bool(np.array_equal(X, X2)),
        "Z_bitwise": bool(np.array_equal(Z, Z2)),
        "B_bitwise": bool(np.array_equal(B, B2)),
    }

    result = {
        "schema": "arc.whitebox.e091.local_check.v1",
        "experiment": "E091",
        "corpus_schema": cfg["schema"],
        "corpus_manifest_sha256": sha256(MANIFEST_PATH),
        "feature_freeze_sha256": sha256(FEATURE_PATH),
        "N": int(X.shape[0]),
        "p": int(X.shape[1]),
        "q": int(Z.shape[1]),
        "lambda": RIDGE_LAMBDA,
        "finite": bool(np.isfinite(X).all() and np.isfinite(Z).all() and np.isfinite(press).all()),
        "press_vs_direct_max_abs": max_abs,
        "press_vs_direct_rel_frob": rel_frob,
        "min_h": float(np.min(h)),
        "max_h": float(np.max(h)),
        "min_one_minus_h": float(np.min(1.0 - h)),
        "self_target_perturb_max_abs": self_target_max,
        "feature_api_parameters": list(params),
        "deterministic": deterministic,
        "public_targets_read": False,
        "benchmark_data_read": False,
        "scientific_accuracy_evaluated": False,
    }

    if not result["finite"]:
        raise AssertionError("non-finite E091 local check")
    if max_abs > 1e-12 or rel_frob > 1e-12:
        raise AssertionError("PRESS/direct parity failed")
    if result["min_one_minus_h"] < 1e-6:
        raise AssertionError("leverage denominator gate failed")
    if self_target_max > 1e-12:
        raise AssertionError("self-target invariance failed")
    if not all(deterministic.values()):
        raise AssertionError("deterministic repeat failed")
    return result


if __name__ == "__main__":
    print(json.dumps(run_check(), indent=2, sort_keys=True))
