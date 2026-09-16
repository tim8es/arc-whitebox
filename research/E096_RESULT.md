# E096 Result — valid V29 matmul callsite attribution

Branch: `research/e096-v29-matmul-callsite-attribution-20260917`

Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Protocol commit: `26ba3d773d18e7c75a22165f3362e08eddaddfa3`

Implementation/workflow commit: `fd5ac3663bdaa17d5e03eda12e008798df9b01d8`

## Frozen Stage-A evidence

- workflow run: `35159279946`
- job: `105006016823`
- artifact: `e096-attribution`, ID `10472670308`
- artifact SHA256: `cf8f2959f7e0353062ceab5af33fa653b8605221fdcb334ffafb53535489c01c`
- upstream V29 blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- width/depth/seed: `1024 / 16 / 96096`
- budget: `2^41`

Integrity gates all passed:

- finite output: `true`
- exact E051 FLOP reproduction: `predict_flops=587262754287`, drift `0.0`
- utilization: `0.26705618178630175`
- intercepted matmul calls: `1085`
- independently estimated intercepted matmul arithmetic: `535480902656`
- matmul coverage vs billed prediction FLOPs: `0.9118250710555129`
- aggregation reconciled exactly.

## Dominant measured callsites

Top source lines by independently estimated arithmetic:

1. `prod`, upstream line 609 — `fnp.matmul(L_, swapaxes(R_), out=T)` then source/batch reduction: `124898099200` estimated FLOPs (`21.27%` of total billed prediction FLOPs).
2. `mm`, line 519 — generic source-family batched transport: `56983879680` (`9.70%`).
3. `hub`, line 581 — `sum_k X_k Y_k^T` source-family hub contraction: `49120497664` (`8.36%`).

Top three together: `231002476544`, only `39.335455%` of total billed prediction FLOPs.

Target `util<=0.135` requires saving approximately `290394614787.48` FLOPs from E051. If **only** these top three lines changed, the required saving would be `125.7106%` of their entire measured arithmetic. Therefore no mechanism restricted to those three callsites can meet the compute target by itself.

Seven Strassen fused-leaf lines each contribute `21.500315648B` estimated arithmetic, but E093 already proves deeper leaf recursion cannot close the target and may not be rescued.

The old/shared-basis block also exposes repeated rank-384 products around lines 906–982 (roughly `8.05B` per listed callsite) plus D21 contraction. These are part of the same source-heavy family ledger rather than a separate single-callsite cure.

## Interpretation / portfolio relation

The measured dominant semantics are source-family transport and source-summed bilinear contractions. This materially supports, rather than competes with, E094's independently occupied **joint young+old source-axis compression** hypothesis. E094 is therefore the correct active compute lane; opening another source-compression experiment from E096 would be duplication.

E095 is materially disjoint: it replaces the expensive V29 family with a covariance + target-free projected sampling estimator and attacks the accuracy/compute trade-off from a different architecture.

## Decision

`E096 = COMPLETE / VALID ATTRIBUTION`.

No estimator modification is authorized under E096. The evidence says the next independent work should not be another local GEMM micro-optimization. Compute work should continue in the already occupied E094 cross-family compression lane, while an independent lane should attack the remaining raw-MSE gap with a materially distinct accuracy mechanism.

No public/public-mini dataset, official scorer, holdout/full split, benchmark labels, fitting/tuning/sweep, canonical mutation, ledger mutation, merge, or scientific rerun was performed.
