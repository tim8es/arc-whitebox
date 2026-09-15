from __future__ import annotations

import json
import math
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq

DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
N = 1024
L = 16
R = 8
BUDGET = 2**41
RAW_GATE = 2.45e-8
ADJUSTED_GATE = 2.5e-9
UTIL_GATE = 0.105
RESIDUAL_GATE = 0.400
NEG_RESID_GATE = -1e-6
MARGINAL_REL_GATE = 1e-5


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _prepare(row: dict):
    weights_np = np.asarray(row["weights"], dtype=np.float32).reshape(L, N, N)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(N)
    # Dataset stores h @ w; the column-vector linear operator used below is W = w.T.
    return [fnp.asarray(w.T) for w in weights_np], gt


def _relu_marginals(mean, variance):
    f32 = fnp.float32
    sigma = fnp.sqrt(variance)
    alpha = mean / sigma
    phi = flops.stats.norm.pdf(alpha).astype(f32)
    Phi = flops.stats.norm.cdf(alpha).astype(f32)
    out_mean = (sigma * phi + mean * Phi).astype(f32)
    second = ((variance + mean * mean) * Phi + mean * sigma * phi).astype(f32)
    out_var = (second - out_mean * out_mean).astype(f32)
    return out_mean, out_var


def _step(weight, mean, diag_residual, factor):
    f32 = fnp.float32
    omega = fnp.eye(N, dtype=f32)[:, :R]
    pre_mean = weight @ mean
    a = weight @ factor

    # C Omega for C = W diag(d) W^T + A A^T.
    wt_omega = weight.T @ omega
    y = weight @ (diag_residual[:, None] * wt_omega) + a @ (a.T @ omega)
    gram = (omega.T @ y + (omega.T @ y).T) * 0.5
    evals, evecs = fnp.linalg.eigh(gram)
    pre_factor = y @ (evecs / fnp.sqrt(evals)[None, :])

    diag_cov = (weight * weight) @ diag_residual + fnp.sum(a * a, axis=1)
    pre_diag_residual = diag_cov - fnp.sum(pre_factor * pre_factor, axis=1)

    out_mean, exact_out_var = _relu_marginals(pre_mean, diag_cov)

    # Fixed spherical-radial cubature over xi ~ N(0,I_R).
    scale = math.sqrt(float(R))
    loc = fnp.concatenate(
        [pre_mean[None, :] + scale * pre_factor.T,
         pre_mean[None, :] - scale * pre_factor.T],
        axis=0,
    )
    sigma_eps = fnp.sqrt(pre_diag_residual)[None, :]
    alpha = loc / sigma_eps
    phi = flops.stats.norm.pdf(alpha).astype(f32)
    Phi = flops.stats.norm.cdf(alpha).astype(f32)
    cond_mean = (sigma_eps * phi + loc * Phi).astype(f32)
    cond_avg = fnp.mean(cond_mean, axis=0, keepdims=True)
    centered = (cond_mean - cond_avg) * (1.0 / math.sqrt(2.0 * R))
    small_gram = (centered @ centered.T + (centered @ centered.T).T) * 0.5
    cevals, cevecs = fnp.linalg.eigh(small_gram)
    out_factor = centered.T @ cevecs[:, -R:]
    out_diag_residual = exact_out_var - fnp.sum(out_factor * out_factor, axis=1)

    recon = out_diag_residual + fnp.sum(out_factor * out_factor, axis=1)
    rel_identity = fnp.abs(recon - exact_out_var) / fnp.maximum(fnp.abs(exact_out_var), 1e-30)
    return (
        out_mean,
        out_diag_residual,
        out_factor,
        evals,
        pre_diag_residual,
        out_diag_residual,
        rel_identity,
    )


def _predict(weights):
    f32 = fnp.float32
    mean = fnp.zeros((N,), dtype=f32)
    diag_residual = fnp.ones((N,), dtype=f32)
    factor = fnp.zeros((N, R), dtype=f32)
    means = []
    evals_all = []
    pre_resids = []
    post_resids = []
    identity = []
    for weight in weights:
        (
            mean,
            diag_residual,
            factor,
            evals,
            pre_r,
            post_r,
            rel_id,
        ) = _step(weight, mean, diag_residual, factor)
        means.append(mean)
        evals_all.append(evals)
        pre_resids.append(pre_r)
        post_resids.append(post_r)
        identity.append(rel_id)
    return (
        fnp.stack(means, axis=0),
        fnp.stack(evals_all, axis=0),
        fnp.stack(pre_resids, axis=0),
        fnp.stack(post_resids, axis=0),
        fnp.stack(identity, axis=0),
    )


def _metered(weights):
    t0 = time.perf_counter()
    with flops.BudgetContext(flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True) as ctx:
        pred, evals, pre_r, post_r, ident = _predict(weights)
        used = float(ctx.flops_used)
    wall = time.perf_counter() - t0
    return (
        np.asarray(pred, dtype=np.float64),
        np.asarray(evals, dtype=np.float64),
        np.asarray(pre_r, dtype=np.float64),
        np.asarray(post_r, dtype=np.float64),
        np.asarray(ident, dtype=np.float64),
        used,
        float(ctx.residual_wall_time_s),
        wall,
    )


def _repeat(weights):
    with flops.BudgetContext(flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True):
        pred, _, _, _, _ = _predict(weights)
    return np.asarray(pred, dtype=np.float64)


def main() -> None:
    row = _load_row0()
    weights, gt = _prepare(row)
    pred, evals, pre_r, post_r, ident, used, residual, wall = _metered(weights)
    repeat = _repeat(weights)

    final_mse = float(np.mean((pred[-1] - gt) ** 2))
    util = used / BUDGET
    adjusted = final_mse * max(0.1, util)
    min_gram_eval = float(np.min(evals))
    min_pre_resid = float(np.min(pre_r))
    min_post_resid = float(np.min(post_r))
    max_identity_rel = float(np.max(ident))
    det_max_abs = float(np.max(np.abs(pred - repeat)))
    finite = bool(
        np.isfinite(pred).all()
        and np.isfinite(evals).all()
        and np.isfinite(pre_r).all()
        and np.isfinite(post_r).all()
    )

    source = Path("scripts/run_e030_conditional_gaussian.py").read_text(encoding="utf-8").lower()
    forbidden = ("clip(", "pinv(", "lstsq(", "jitter", "fallback", "power iteration")
    scope_ok = R == 8 and all(tok not in source for tok in forbidden)

    gates = {
        "raw_le_2.45e-8": final_mse <= RAW_GATE,
        "adjusted_lt_2.5e-9": adjusted < ADJUSTED_GATE,
        "util_le_0.105": util <= UTIL_GATE,
        "residual_lt_0.400": residual < RESIDUAL_GATE,
        "gram_positive": min_gram_eval > 0.0,
        "diag_residual_ge_-1e-6": min(min_pre_resid, min_post_resid) >= NEG_RESID_GATE,
        "marginal_identity": max_identity_rel <= MARGINAL_REL_GATE,
        "finite": finite,
        "deterministic": det_max_abs == 0.0,
        "scope": scope_ok,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "final_mse": final_mse,
        "flops": used,
        "utilization": util,
        "adjusted_proxy": adjusted,
        "residual_s": residual,
        "wall_s": wall,
        "min_gram_eigenvalue": min_gram_eval,
        "min_pre_diag_residual": min_pre_resid,
        "min_post_diag_residual": min_post_resid,
        "max_marginal_identity_rel": max_identity_rel,
        "det_max_abs": det_max_abs,
        "finite": finite,
        "scope_ok": scope_ok,
        "gates": gates,
        "decision": decision,
    }
    print("E030_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e030_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
