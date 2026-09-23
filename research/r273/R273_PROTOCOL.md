# R273 Protocol — R209 V25 error concentration audit

- Job: R273
- Owner: `score-gap-independent-audit`
- Dependencies: R209 COMPLETE, R270 COMPLETE.
- Control baseline observed: live revision 332; claim published at revision 333.
- Inputs: only immutable `research/results/R209-v25-mini100.json` and the official Phase-2 scoring source.
- Row check: verify for every row that `official_adjusted_score = final_mse * max(0.1, measured_flops / budget_flops)` for successful rows, preserving official failure semantics if any failures exist.
- Descriptive statistics: n, failures, mean, sample SD, SE, and fixed quantiles (p05, p10, p25, p50, p75, p90, p95) for adjusted score and final MSE.
- Concentration: share of total adjusted score contributed by the worst 10 and worst 25 networks, ranked by adjusted score; also report max share and top-k thresholds.
- Cost-vs-MSE variation: quantify across-network variability of the compute multiplier and of raw MSE, and determine which can explain adjusted-score dispersion.
- Interpretation: development evidence only; classify whether error is broad-based or dominated by a few outliers and state implications for global research only. No per-network selection, tuning, leaderboard comparison, or rank claim.
- Forbidden: estimator/benchmark execution, Actions, new competition data, paid/private/holdout/full access, tuning, submission, model/leaderboard/canonical edits.
- Deliverables: append-only calculations, short report, receipt with hashes/commit, then finish R273.
