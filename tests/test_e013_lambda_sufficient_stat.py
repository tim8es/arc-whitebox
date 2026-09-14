from __future__ import annotations

import flopscope as flops
import numpy as np

from methods.e013_lambda_sufficient_stat import adaptive_lambda_baseline, adaptive_lambda_candidate


def _inputs(n: int = 32):
    rng = np.random.default_rng(20260914)
    w = rng.normal(0.0, 1.0 / np.sqrt(n), size=(n, n)).astype(np.float32)
    ww = w * w
    var_prev = (0.5 + rng.random(n)).astype(np.float32)
    var = (ww @ var_prev + 0.05 * rng.random(n)).astype(np.float32)
    g_prev = (0.008 * var_prev + 0.001 * rng.random(n)).astype(np.float32)
    return ww, g_prev, var_prev, var


def _run(fn, ww, g_prev, var_prev, var):
    with flops.BudgetContext(flop_budget=10_000_000, wall_time_limit_s=5.0) as ctx:
        d_g, lam = fn(ww, g_prev, var_prev, var, lam0=0.009, ref=0.0085, beta=1.0)
    return np.asarray(d_g), float(lam), int(ctx.flops_used)


def test_candidate_preserves_adaptive_lambda_and_dg():
    ww, g_prev, var_prev, var = _inputs()
    base_dg, base_lam, _ = _run(adaptive_lambda_baseline, ww, g_prev, var_prev, var)
    cand_dg, cand_lam, _ = _run(adaptive_lambda_candidate, ww, g_prev, var_prev, var)

    rel_dg = np.linalg.norm(cand_dg - base_dg) / np.linalg.norm(base_dg)
    rel_lam = abs(cand_lam - base_lam) / abs(base_lam)
    assert rel_dg <= 5e-6
    assert rel_lam <= 5e-6


def test_candidate_uses_fewer_metered_flops():
    ww, g_prev, var_prev, var = _inputs()
    _, _, base_flops = _run(adaptive_lambda_baseline, ww, g_prev, var_prev, var)
    _, _, cand_flops = _run(adaptive_lambda_candidate, ww, g_prev, var_prev, var)
    assert cand_flops < base_flops
