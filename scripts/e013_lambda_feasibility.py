from __future__ import annotations

import json
import statistics

import flopscope as flops
import numpy as np

from methods.e013_lambda_sufficient_stat import (
    adaptive_lambda_baseline,
    adaptive_lambda_candidate,
)

N = 1024
SEED = 20260914
LAM0 = 0.009
REF = 0.0085
BETA = 1.0
REPETITIONS = 7
FLOP_BUDGET = 2**41
E007_UTIL = 0.36666448
E007_ADJUSTED = 8.17e-09
APPLICATIONS = 15
DG_ERROR_GATE = 5e-6
LAMBDA_ERROR_GATE = 5e-6


def _inputs():
    rng = np.random.default_rng(SEED)
    w = rng.normal(0.0, 1.0 / np.sqrt(N), size=(N, N)).astype(np.float32)
    ww = w * w
    var_prev = (0.5 + rng.random(N)).astype(np.float32)
    var = (ww @ var_prev + 0.05 * rng.random(N)).astype(np.float32)
    g_prev = (0.008 * var_prev + 0.001 * rng.random(N)).astype(np.float32)
    return ww, g_prev, var_prev, var


def _measure(fn, ww, g_prev, var_prev, var):
    with flops.BudgetContext(flop_budget=FLOP_BUDGET, wall_time_limit_s=60.0) as ctx:
        d_g, lam = fn(
            ww,
            g_prev,
            var_prev,
            var,
            lam0=LAM0,
            ref=REF,
            beta=BETA,
        )
    return np.asarray(d_g).copy(), float(lam), ctx


def _finite(d_g, lam) -> bool:
    return bool(np.all(np.isfinite(d_g)) and np.isfinite(lam))


def main() -> int:
    ww, g_prev, var_prev, var = _inputs()

    # Fixed one-call warm-up for each exact operation schedule; excluded from metrics.
    _measure(adaptive_lambda_baseline, ww, g_prev, var_prev, var)
    _measure(adaptive_lambda_candidate, ww, g_prev, var_prev, var)

    baseline_runs = []
    candidate_runs = []
    for _ in range(REPETITIONS):
        baseline_runs.append(_measure(adaptive_lambda_baseline, ww, g_prev, var_prev, var))
        candidate_runs.append(_measure(adaptive_lambda_candidate, ww, g_prev, var_prev, var))

    base_dg, base_lam, base_ctx = baseline_runs[0]
    cand_dg, cand_lam, cand_ctx = candidate_runs[0]

    dg_rel_error = float(np.linalg.norm(cand_dg - base_dg) / np.linalg.norm(base_dg))
    lambda_rel_error = float(abs(cand_lam - base_lam) / abs(base_lam))
    baseline_flops = int(base_ctx.flops_used)
    candidate_flops = int(cand_ctx.flops_used)
    saved_per_application = baseline_flops - candidate_flops
    projected_saved = saved_per_application * APPLICATIONS
    projected_util = E007_UTIL - projected_saved / FLOP_BUDGET
    projected_adjusted = E007_ADJUSTED * projected_util / E007_UTIL

    baseline_residuals = [float(run[2].residual_wall_time_s) for run in baseline_runs]
    candidate_residuals = [float(run[2].residual_wall_time_s) for run in candidate_runs]
    baseline_residual_median = float(statistics.median(baseline_residuals))
    candidate_residual_median = float(statistics.median(candidate_residuals))
    residual_ratio = (
        candidate_residual_median / baseline_residual_median
        if baseline_residual_median > 0.0
        else float("inf")
    )
    finite = all(_finite(run[0], run[1]) for run in baseline_runs + candidate_runs)

    gates = {
        "dg_quality": dg_rel_error <= DG_ERROR_GATE,
        "lambda_quality": lambda_rel_error <= LAMBDA_ERROR_GATE,
        "metered_compute": candidate_flops < baseline_flops,
        "projected_utilization": projected_util < E007_UTIL,
        "projected_adjusted": projected_adjusted < E007_ADJUSTED,
        "residual_overhead": candidate_residual_median <= baseline_residual_median,
        "finite": finite,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"

    result = {
        "experiment": "E013",
        "scope": "single synthetic V25 adaptive-lambda kernel; no whest scorer",
        "n": N,
        "seed": SEED,
        "beta": BETA,
        "lam0": LAM0,
        "ref": REF,
        "repetitions": REPETITIONS,
        "baseline_flops": baseline_flops,
        "candidate_flops": candidate_flops,
        "saved_flops_per_application": saved_per_application,
        "flop_ratio": candidate_flops / baseline_flops,
        "dg_relative_l2_error": dg_rel_error,
        "lambda_relative_error": lambda_rel_error,
        "baseline_lambda": base_lam,
        "candidate_lambda": cand_lam,
        "baseline_residual_s_median": baseline_residual_median,
        "candidate_residual_s_median": candidate_residual_median,
        "residual_ratio": residual_ratio,
        "baseline_residual_s_all": baseline_residuals,
        "candidate_residual_s_all": candidate_residuals,
        "applications_for_projection": APPLICATIONS,
        "projected_saved_flops_per_mlp": projected_saved,
        "e007_utilization": E007_UTIL,
        "projected_utilization": projected_util,
        "e007_adjusted": E007_ADJUSTED,
        "projected_adjusted_at_unchanged_raw": projected_adjusted,
        "finite": finite,
        "gates": gates,
        "decision": decision,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"DECISION={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
