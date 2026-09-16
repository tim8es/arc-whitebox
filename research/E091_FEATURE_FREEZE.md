# E091 feature freeze v1

Status: FROZEN BEFORE THE E091 EVIDENCE-GENERATING SYNTHETIC TARGET RUN.

This file defines the only feature map authorized for the E091 local reproducibility check.
It is target-free: its inputs are `weights`, `base_prediction`, `state_var`, and `state_d3`.
No target, residual, scorer output, public label, holdout label, corpus membership decision,
or fitted normalization may enter feature construction.

For last-layer weight matrix `W`, flattened base prediction `b`, state variance `v`, and
third-diagonal state `d3`, the feature vector `x in R^12` is exactly:

1. `1`
2. `mean(b)`
3. `std(b)` with NumPy population convention (`ddof=0`)
4. `mean(abs(b))`
5. `sqrt(mean(b*b))`
6. `mean(W)`
7. `std(W)` with `ddof=0`
8. `mean(abs(W))`
9. `sqrt(mean(W*W))`
10. `mean(v)`
11. `std(v)` with `ddof=0`
12. `mean(abs(d3))`

All inputs are converted to float64 before these reductions. No centering, standardization,
whitening, clipping, rank selection, feature selection, learned transform, or target-dependent
preprocessing is allowed.

Ridge regularization is frozen to `lambda = 1.0`.

Deploy-time correction for a later authorized implementation would be `x @ B_frozen`.
This freeze authorizes only the disjoint synthetic/local reproducibility check; it does not
authorize public, scorer, holdout, full, or scientific accuracy evaluation.
