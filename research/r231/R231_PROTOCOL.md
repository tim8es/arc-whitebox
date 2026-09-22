# R231 — V25 mini-100 error-tail and target-frontier audit protocol

Frozen before quantitative analysis.

- Job: R231 / R209-V25-ERROR-TAIL-TARGET-FRONTIER.
- Input: only the exact integrated `research/results/R209-v25-mini100.json` record on `research/control-v2`.
- Integrity gate: verify file SHA256, 100/100 rows, unique network/name identities, per-row target SHA256 presence, fixed shape `[16,1024]`, fixed budget `2**41`, status/failure fields, and agreement of recomputed means with stored aggregates before descriptive conclusions.
- Descriptive outputs: raw final-layer MSE mean, median, quantiles, top-1/5/10/20 share of total raw MSE, and leave-one-out mean sensitivity. Any extra concentration statistic must be computable from the exact row fields and labeled descriptive.
- Score math: use the official Phase-2 per-network formula `mse * max(0.1, C/B)`. Compute the V25 score floor obtained by replacing each row's multiplier with 0.1 while holding its observed raw MSE fixed. Also compute the raw-MSE mean required for the numerical score target `2.1e-9` at the 0.1 floor, and the reduction from observed V25 mean raw MSE.
- Interpretation firewall: the `2.1e-9` target is a cross-panel numerical orientation only, not a comparable-panel result and not a rank claim. All networks share the fixed Phase-2 shape/budget; do not infer structural causality from names or absent features. Raw prediction tensors are unavailable, so no within-network residual decomposition is permitted.
- Recommendation gate: recommend only among global accuracy, compute factor, or a measurable high-error subset, based on the exact concentration and floor arithmetic. Do not propose causal features not present in the record.
- Outputs: a small deterministic script, a derived CSV table, an append-only source-linked report, and a machine-readable receipt.
- Prohibited: estimator execution, paid compute, private/holdout data, submission, competitor code, canonical estimator/result edits, and leaderboard-rank inference.
