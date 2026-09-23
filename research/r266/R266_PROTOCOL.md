# R266 Protocol — score-gap sensitivity from frozen evidence

- Job: R266
- Owner: `score-gap-analysis`
- Control dependency gate: R263 COMPLETE and R209 COMPLETE before claim.
- Inputs: completed R263 official snapshot/receipt and existing normalized R209/R223 records only.
- Official per-MLP formula: `score_m = final_mse_m * max(0.1, measured_flops_m / B)`, `B = 2**41`; failed MLPs use multiplier 1.0.
- Strict comparison rule: an official leader gap/rank is computed only if metric, aggregation, and evaluated split/panel match. Otherwise verdict is `NOT_COMPARABLE`.
- Sensitivity rule: because R263 found a split mismatch, any arithmetic against the leaderboard's displayed 2.1e-9 is labeled conditional/display-threshold-only, never an official gap or rank.
- No estimator/benchmark execution, Actions, new dataset access, paid/private/holdout/full access, submission, model change, leaderboard mutation, or canonical-result edit.
- Deliverables: append-only calculation record, report, receipt, commit, then finish R266.
