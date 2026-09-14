# E013 Adaptive-lambda sufficient-statistic feasibility protocol

Status: preregistered local diagnostic only.

## Objective

Test an exact-algebra rewrite of V25 adaptive kappa4-regeneration lambda selection that can reduce metered compute without changing the scientific estimator.

Pinned scientific comparator is canonical E007 / upstream V25:
- adjusted final-layer score: 8.17e-09
- raw final-layer MSE: 2.23e-08
- mean compute utilization: 0.36666448
- failures: 0/100

Canonical base: research/bootstrap @ 52eacc67dcc9af4813136ff641ea9b71c36c626f.
Upstream V25: 504aldo/whest-p2-cumulant-k3 @ 18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45, estimator blob 195373a110215256b759d7c172ba8c923c62e5cc.

E010 is canonical DROP. E012 is the independent pair-batched/scheduled joiner-transform lane. E013 must not batch A/P joins, alter source ranks, use Strassen/HK arithmetic, sample sources, change bases, or touch E001-E012 code/ledger.

## Hypothesis

V25 adaptive lambda currently computes

- t_g = WW @ g_prev
- t_v = var - WW @ var_prev
- dG0 = t_g + lam0 * t_v
- rr = mean(dG0) / mean(var)
- lam1 = lam0 * clip(rr/ref, 0.5, 2.0)^beta
- dG = t_g + lam1 * t_v

with WW = W*W.

Only the scalar mean(dG0) is needed before lam1 is chosen. By linearity,

mean(WW @ v) = dot(sum_rows(WW), v) / n.

Therefore rr can be computed from one column-sum vector plus scalar dots, after which the final dG needs only one dense WW matvec:

- c = sum_rows(WW)
- mean_tg = dot(c, g_prev)/n
- mean_tv = mean(var) - dot(c, var_prev)/n
- rr = (mean_tg + lam0*mean_tv)/mean(var)
- lam1 as above
- dG = WW @ (g_prev - lam1*var_prev) + lam1*var

This is mathematically identical in exact arithmetic and changes no closure, rank, state, or randomness.

## Frozen diagnostic

One competition-shape synthetic regeneration kernel only:
- n=1024
- dtype=float32
- seed=20260914
- beta=1.0
- lam0=0.009
- ref=0.0085
- fixed deterministic W, g_prev, var_prev, var generation in the diagnostic script
- seven timing repetitions after one warm-up; median residual time is used only to reduce timing noise

No whest scorer, dataset scorer, holdout, MLP sweep, parameter sweep, tuning, or estimator integration is allowed.

## Local GO gate

All conditions must pass:
1. relative L2 error of final dG <= 5e-6;
2. relative lambda error <= 5e-6;
3. candidate metered FLOPs < baseline metered FLOPs;
4. projected E007 utilization, using 15 adaptive-regeneration applications, is strictly below 0.36666448;
5. projected adjusted score at unchanged raw MSE is strictly below 8.17e-09;
6. median candidate residual overhead <= median baseline residual overhead;
7. no exception/nonfinite output in the fixed diagnostic.

A local GO is only feasibility evidence. Any future full-estimator promotion would still require raw MSE no worse than E007, failures=0/100, adjusted score <8.17e-09 or a proven compute reduction at unchanged score, and no residual-overhead regression.

## Kill rule

If any local GO condition fails, E013 is NO-GO and stops. No alternate reduction order, float64 variant, seed change, beta change, layer sweep, scorer, or holdout is permitted under E013.
