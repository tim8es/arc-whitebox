from __future__ import annotations

import flopscope.numpy as fnp


def _updated_lambda(rr, *, lam0: float, ref: float, beta: float):
    ratio = fnp.clip(rr / ref, 0.5, 2.0)
    return lam0 * fnp.power(ratio, beta)


def adaptive_lambda_baseline(
    ww,
    g_prev,
    var_prev,
    var,
    *,
    lam0: float,
    ref: float,
    beta: float,
):
    """Faithful V25 adaptive-lambda regeneration block."""
    t_g = fnp.matmul(ww, g_prev)
    t_v = fnp.subtract(var, fnp.matmul(ww, var_prev))
    d_g0 = fnp.add(t_g, fnp.multiply(t_v, lam0))
    rr = fnp.mean(d_g0) / fnp.mean(var)
    lam = _updated_lambda(rr, lam0=lam0, ref=ref, beta=beta)
    d_g = fnp.add(t_g, fnp.multiply(t_v, lam))
    return d_g, lam


def adaptive_lambda_candidate(
    ww,
    g_prev,
    var_prev,
    var,
    *,
    lam0: float,
    ref: float,
    beta: float,
):
    """Exact-algebra adaptive lambda using scalar sufficient statistics before final dG."""
    n = int(g_prev.shape[0])
    colsum = fnp.sum(ww, axis=0)
    mean_var = fnp.mean(var)
    mean_tg = fnp.sum(fnp.multiply(colsum, g_prev)) / n
    mean_tv = mean_var - fnp.sum(fnp.multiply(colsum, var_prev)) / n
    rr = (mean_tg + lam0 * mean_tv) / mean_var
    lam = _updated_lambda(rr, lam0=lam0, ref=ref, beta=beta)

    combined = fnp.subtract(g_prev, fnp.multiply(var_prev, lam))
    d_g = fnp.add(fnp.matmul(ww, combined), fnp.multiply(var, lam))
    return d_g, lam
