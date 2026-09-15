from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import statistics
import tempfile
import time
import urllib.request
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench

from methods.e019_final_saddlepoint import (
    GL_NODES,
    GL_WEIGHTS,
    NEWTON_ITERS,
    gaussian_relu_mean,
    saddlepoint_relu_mean,
)

IDEMPOTENCY_KEY = "ARC-E019-IMPLEMENT-20250915"
UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
V25_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/estimators/estimator_v25.py"
)
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
SMOKE_INDICES = (0, 1, 2, 3)
VALID_INDICES = (4, 5, 6, 7)
N = 1024
FLOP_BUDGET = 2**41
E007_RAW = 2.23e-8
E007_UTIL = 0.36666448
GAUSSIAN_ERROR_GATE = 1e-6
NORMALIZED_RESIDUAL_GATE = 1e-5
VALID_RATIO_GATE = 0.99
DUMP_RATIO_GATE = 1.02
UTIL_GATE = 0.3670
RESIDUAL_PROXY_GATE_S = 0.005
ADJUSTED_GATE = 8.11e-9
PROXY_REPS = 7


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity


def _load_exact_v25():
    with urllib.request.urlopen(V25_URL, timeout=30) as response:  # noqa: S310
        data = response.read()
    blob = _git_blob_sha(data)
    if blob != EXPECTED_V25_BLOB:
        raise RuntimeError(f"V25 blob mismatch: {blob} != {EXPECTED_V25_BLOB}")

    # Freeze exact V25 defaults explicitly; V17_DEBUG is observational only.
    frozen_env = {
        "V17_DEBUG": "1",
        "V17_NO_REGEN": "0",
        "V17_NO_FEED": "0",
        "V17_NO_WK431": "0",
        "V18_NO_FB": "0",
        "V19_FULL_LAST": "0",
        "V19_NO_SRC_LAST": "0",
        "V21_NO_CONFINE": "0",
        "V21_AGE_OLD": "4",
        "V21_R_OLD": "384",
        "V21_QPASS": "1",
        "V24_AGE_OLD2": "7",
        "V24_R_OLD2": "224",
        "V25_BETA": "1.0",
        "V17_LAM_SCALE": "0.95",
        "V17_NO_CORR": "1",
    }
    os.environ.update(frozen_env)

    tmp = tempfile.NamedTemporaryFile(mode="wb", suffix="_estimator_v25.py", delete=False)
    try:
        tmp.write(data)
        tmp.close()
        spec = importlib.util.spec_from_file_location("e019_exact_v25", tmp.name)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import exact V25 module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, blob
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def _mse(prediction: np.ndarray, target: np.ndarray) -> float:
    delta = np.asarray(prediction, dtype=np.float64) - np.asarray(target, dtype=np.float64)
    return float(np.mean(delta * delta))


def _run_one(module, dataset, index: int) -> dict[str, object]:
    mlp = whestbench.mlp_at(dataset, index)
    target = np.asarray(dataset[index]["final_means"], dtype=np.float64).reshape(-1)
    estimator = module.Estimator()
    module.DEBUG.clear()

    start = time.perf_counter()
    baseline_all = np.asarray(estimator.predict(mlp, FLOP_BUDGET), dtype=np.float64)
    wall_s = time.perf_counter() - start
    if baseline_all.ndim != 2 or baseline_all.shape[0] < 2:
        raise RuntimeError(f"unexpected V25 output shape: {baseline_all.shape}")
    if not module.DEBUG:
        raise RuntimeError("V25 DEBUG did not capture teacher state")
    state = module.DEBUG[-1]
    final_layer = len(mlp.weights) - 1
    if int(state["layer"]) != final_layer:
        raise RuntimeError(f"unexpected final DEBUG layer {state['layer']} != {final_layer}")

    # Reconstruct the exact V25 final preactivation mean from the exact V25
    # penultimate emitted row and final weight, matching V25's float32 linear step.
    prev_mean = np.asarray(baseline_all[-2], dtype=np.float32)
    final_weight = np.asarray(mlp.weights[-1], dtype=np.float32)
    kappa1 = np.asarray(final_weight.T @ prev_mean, dtype=np.float64)
    kappa2 = np.asarray(state["var"], dtype=np.float64)
    kappa3 = np.asarray(state["D3"], dtype=np.float64)
    # V25 final univariate program consumes g4row = METRIC_C * dG, METRIC_C = 2.
    kappa4 = np.asarray(state["dG"], dtype=np.float64) * float(module.METRIC_C)

    result = saddlepoint_relu_mean(kappa1, kappa2, kappa3, kappa4)
    baseline = np.asarray(baseline_all[-1], dtype=np.float64)
    candidate = np.asarray(result.mean, dtype=np.float64)
    baseline_mse = _mse(baseline, target)
    candidate_mse = _mse(candidate, target)
    ratio = candidate_mse / baseline_mse

    return {
        "index": index,
        "subset": "smoke" if index in SMOKE_INDICES else "validation",
        "baseline_mse": baseline_mse,
        "candidate_mse": candidate_mse,
        "mse_ratio": ratio,
        "min_kpp": result.min_kpp,
        "max_normalized_residual": result.max_normalized_residual,
        "finite_positive_kpp": result.finite_positive_kpp,
        "candidate_finite": bool(np.all(np.isfinite(candidate))),
        "teacher_finite": bool(
            np.all(np.isfinite(kappa1))
            and np.all(np.isfinite(kappa2))
            and np.all(np.isfinite(kappa3))
            and np.all(np.isfinite(kappa4))
        ),
        "v25_wall_s": wall_s,
    }


def _gaussian_limit_error() -> float:
    mu = np.asarray([-3.0, -1.0, -0.25, 0.0, 0.5, 1.5, 3.0], dtype=np.float64)
    var = np.asarray([0.25, 1.0, 0.5, 4.0, 1.5, 2.0, 9.0], dtype=np.float64)
    zero = np.zeros_like(mu)
    candidate = saddlepoint_relu_mean(mu, var, zero, zero).mean
    exact = gaussian_relu_mean(mu, var)
    return float(np.max(np.abs(candidate - exact)))


def _proxy_once(seed: int) -> tuple[int, float]:
    rng = np.random.default_rng(seed)
    mu_np = rng.normal(0.0, 0.7, N).astype(np.float32)
    var_np = np.exp(rng.normal(0.0, 0.2, N)).astype(np.float32)
    sigma_np = np.sqrt(var_np)
    k3_np = (rng.normal(0.0, 0.02, N) * sigma_np**3).astype(np.float32)
    k4_np = (rng.normal(0.005, 0.005, N) * sigma_np**4).astype(np.float32)

    mu = fnp.asarray(mu_np)
    var = fnp.asarray(var_np)
    k3 = fnp.asarray(k3_np)
    k4 = fnp.asarray(k4_np)
    nodes = fnp.asarray(GL_NODES.astype(np.float32)).reshape((1, 32))
    weights = fnp.asarray(GL_WEIGHTS.astype(np.float32)).reshape((1, 32))
    phi_nodes = fnp.asarray(
        (np.exp(-0.5 * GL_NODES * GL_NODES) / math.sqrt(2.0 * math.pi)).astype(np.float32)
    ).reshape((1, 32))
    ones_col = fnp.ones((N, 1), dtype=fnp.float32)

    with flops.BudgetContext(flop_budget=10_000_000_000, wall_time_limit_s=30.0) as ctx:
        sigma = fnp.sqrt(var)
        alpha = mu / sigma
        phi_alpha = flops.stats.norm.pdf(alpha).astype(fnp.float32)
        Phi_alpha = flops.stats.norm.cdf(alpha).astype(fnp.float32)
        gaussian = sigma * phi_alpha + mu * Phi_alpha

        s2 = sigma * sigma
        c3 = k3 / (s2 * sigma)
        c4 = k4 / (s2 * s2)
        c3c = fnp.reshape(c3, (-1, 1))
        c4c = fnp.reshape(c4, (-1, 1))
        t = ones_col * nodes
        for _ in range(NEWTON_ITERS):
            t2 = t * t
            t3 = t2 * t
            kp = t + c3c * t2 * 0.5 + c4c * t3 * (1.0 / 6.0)
            kpp = 1.0 + c3c * t + c4c * t2 * 0.5
            t = t - (kp - nodes) / kpp

        t2 = t * t
        t3 = t2 * t
        t4 = t2 * t2
        kpp = 1.0 + c3c * t + c4c * t2 * 0.5
        K = t2 * 0.5 + c3c * t3 * (1.0 / 6.0) + c4c * t4 * (1.0 / 24.0)
        density = fnp.exp(K - t * nodes) / fnp.sqrt(kpp * (2.0 * math.pi))
        z = fnp.reshape(mu, (-1, 1)) + fnp.reshape(sigma, (-1, 1)) * nodes
        relu_z = fnp.maximum(z, 0.0)
        correction = fnp.sum(weights * relu_z * (density - phi_nodes), axis=1)
        _candidate = gaussian + correction

    return int(ctx.flops_used), float(ctx.residual_wall_time_s)


def _measure_proxy() -> dict[str, object]:
    _proxy_once(1900)
    rows = [_proxy_once(1910 + i) for i in range(PROXY_REPS)]
    flops_used = [r[0] for r in rows]
    residual = [r[1] for r in rows]
    if len(set(flops_used)) != 1:
        raise RuntimeError(f"proxy FLOPs are not deterministic: {flops_used}")
    return {
        "extra_flops": flops_used[0],
        "residual_s_all": residual,
        "residual_s_median": statistics.median(residual),
    }


def main() -> int:
    started = time.perf_counter()
    module, blob = _load_exact_v25()
    dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)

    rows: list[dict[str, object]] = []
    for index in (*SMOKE_INDICES, *VALID_INDICES):
        row = _run_one(module, dataset, index)
        rows.append(row)
        print("E019_ROW=" + json.dumps(row, sort_keys=True), flush=True)

    smoke = [r for r in rows if r["subset"] == "smoke"]
    validation = [r for r in rows if r["subset"] == "validation"]
    baseline_validation_mse = float(np.mean([float(r["baseline_mse"]) for r in validation]))
    candidate_validation_mse = float(np.mean([float(r["candidate_mse"]) for r in validation]))
    validation_ratio = candidate_validation_mse / baseline_validation_mse
    worst_validation_ratio = float(max(float(r["mse_ratio"]) for r in validation))

    gaussian_error = _gaussian_limit_error()
    global_min_kpp = float(min(float(r["min_kpp"]) for r in rows))
    global_max_residual = float(max(float(r["max_normalized_residual"]) for r in rows))
    all_finite_positive = all(bool(r["finite_positive_kpp"]) for r in rows)
    all_candidate_finite = all(bool(r["candidate_finite"]) for r in rows)
    all_teacher_finite = all(bool(r["teacher_finite"]) for r in rows)

    proxy = _measure_proxy()
    projected_util = E007_UTIL + int(proxy["extra_flops"]) / FLOP_BUDGET
    projected_raw = E007_RAW * validation_ratio
    projected_adjusted = projected_raw * projected_util

    gates = {
        "gaussian_limit": gaussian_error <= GAUSSIAN_ERROR_GATE,
        "finite_positive_kpp": all_finite_positive and all_candidate_finite and all_teacher_finite,
        "normalized_newton_residual": global_max_residual <= NORMALIZED_RESIDUAL_GATE,
        "validation_mse_ratio": validation_ratio <= VALID_RATIO_GATE,
        "no_dump_regression_gt_2pct": worst_validation_ratio <= DUMP_RATIO_GATE,
        "projected_util": projected_util <= UTIL_GATE,
        "residual_proxy": float(proxy["residual_s_median"]) <= RESIDUAL_PROXY_GATE_S,
        "projected_adjusted": projected_adjusted <= ADJUSTED_GATE,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"

    result = {
        "idempotency_key": IDEMPOTENCY_KEY,
        "decision": decision,
        "v25": {
            "commit": UPSTREAM_COMMIT,
            "expected_blob": EXPECTED_V25_BLOB,
            "observed_blob": blob,
        },
        "dataset": {"name": DATASET, "revision": REVISION, "split": SPLIT},
        "smoke_indices": list(SMOKE_INDICES),
        "validation_indices": list(VALID_INDICES),
        "newton_iterations": NEWTON_ITERS,
        "quadrature_nodes": 32,
        "quadrature_interval": [-8.0, 8.0],
        "gaussian_limit_max_abs_error": gaussian_error,
        "global_min_kpp": global_min_kpp,
        "global_max_normalized_residual": global_max_residual,
        "baseline_validation_mse": baseline_validation_mse,
        "candidate_validation_mse": candidate_validation_mse,
        "validation_mse_ratio": validation_ratio,
        "validation_raw_gain": 1.0 - validation_ratio,
        "worst_validation_dump_ratio": worst_validation_ratio,
        "proxy": proxy,
        "projected_util": projected_util,
        "projected_raw": projected_raw,
        "projected_adjusted": projected_adjusted,
        "gates": gates,
        "rows": rows,
        "smoke_baseline_mse_mean": float(np.mean([float(r["baseline_mse"]) for r in smoke])),
        "smoke_candidate_mse_mean": float(np.mean([float(r["candidate_mse"]) for r in smoke])),
        "total_wall_s": time.perf_counter() - started,
    }
    print("E019_RESULT=" + json.dumps(result, sort_keys=True), flush=True)
    print(f"DECISION={decision}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
