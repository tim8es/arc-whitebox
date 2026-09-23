# R300 — binary32 coordinate-energy consistency fix

## Scope

Owner: `r300-binary32-energy-consistency-fix-r269`  
Run: `R300-binary32-energy-consistency-fix-20260924`  
Control claim: revision 442, commit `85a6af9b3ec125a56a12463c2c9b7303a563ed70`  
Control start: revision 443, commit `65f920c7bd1aa9d389a285f621eff546545c178e`

This is an append-only supplement. The branch starts from immutable R299 receipt commit
`436514b36846c0e96a5e287fe07cbef8ed327507`. Historical R298/R299 files are not
modified.

## Defect reproduced

R299 formed coordinate corrected residuals as `binary32(r-d)`. That is not equivalent
to the frozen R298 path:

```
pred_corr       = binary32(pred + d)
corrected_resid = binary32(target - pred_corr)
```

The required float32 counterexample was reproduced without repository/data I/O:

- `pred = target = 1.0`
- `d = binary32(1e-8) = 9.99999993922529e-09`
- stored baseline `r = binary32(target-pred) = 0`
- old R299 expression: `binary32(r-d) = -9.99999993922529e-09` (non-zero)
- frozen R298 path: `pred_corr = binary32(1+d) = 1.0`, therefore
  `corrected_resid = binary32(1-pred_corr) = 0`

## Frozen R300 correction

`B_k` is unchanged and is computed from the stored canonical binary32 baseline
residual:

`B_k = fsum_i residual[i,k]^2`.

`C_k` now consumes the exact corrected-residual vectors already produced by the R298
per-network path:

`C_k = fsum_i corrected_residual[i,k]^2`,

where each corrected residual is exactly
`binary32(target - binary32(pred + d))`.

The R299 weighting, B=0/null semantics, finite-coordinate count, negative-explained
count, weighted global fraction, type-7 p10/p25/p50/p75/p90 quantiles, and no-tuning
rule are unchanged. The analyzer also fail-closes unless coordinate `sum_C` agrees
with the same corrected-residual energy aggregated by the R298 path within
`rel_tol=1e-15`.

## Artifacts

- `research/r300/r300_capture_analyzer.py`
  - Git blob: `2b99b8aefbe016092a3d01ea69a9609170cd2bd1`
  - SHA256: `a4c0808535f5a3a7d14a27a5fbc7d26d25400e74b0b238edb22e017677365315`
- `research/r300/r300_capture_analyzer_selfcheck.py`
  - Git blob: `8a80ec16952117a0cdd730a61ae0c9c431b4c7df`
  - SHA256: `d2054223b7876912fc7d3c842f9f15fa1876ad71180e68cf297dd345ea2a45b6`

Code commits:
- analyzer: `c6bd5538e2dcc5832a5fd641d6b128b7ad30f047`
- self-check: `e1749ed6314de15aac380f9bb06148e7e025b406`

Comparison against the immutable R299 base is exactly two added R300 files and zero
R298/R299 modifications.

## Synthetic checks

The committed self-check contains 21 substantive checks (plus the final aggregate
`pass` field), including all inherited R298/R299 integrity/energy checks and two new
R300 regressions:

1. `binary32_pred_target_counterexample` catches the `pred=target=1,d≈1e-8`
   mismatch above.
2. `aggregate_coordinate_C_matches_corrected_mse_path` verifies coordinate `sum_C`
   against the corrected EVAL MSE aggregate.

The available local numerical scratch runtime, with no repository or data-file access,
passed both R300 delta semantics:
- counterexample: PASS;
- 50x1024 synthetic aggregate consistency: PASS, coordinate `sum_C`,
  direct corrected-residual energy, and corrected-MSE-derived energy all
  `156.98132407423532`.

The full committed 21-check integration self-check was **not executed**: this session
has no repository checkout/command runner, and the task explicitly forbids cloning or
downloading to materialize one. No Actions were used.

## Prohibited-work accounting

Real capture vectors inspected: 0. Benchmark/estimator runs: 0. Actions runs: 0.
Data/dependency downloads or installs: 0. Paid resources: none. PR #36 edits: 0.
Holdout/private/full access: 0. Submissions: 0. Leaderboard/canonical edits: 0.
R296 was not claimed or modified.

## Decision

`BINARY32_CONSISTENCY_FIX_PREPARED_DELTA_TESTED_NO_REAL_CAPTURE`.

The arithmetic inconsistency is corrected append-only before any real capture is
inspected. Remaining execution evidence is limited to the explicitly unavailable
full committed self-check; the new numerical delta semantics were exercised
synthetically and passed.
