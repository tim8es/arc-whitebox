# E018 — unbiased importance-sampled old-D21 contractions

Status: preregistered implementation diagnostic.

Idempotency key: `ARC-E018-IMPLEMENT-20250915`.

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Scope

E018 is a development-only diagnostic. It must not run the official scorer, touch holdout data, mutate `research/ledger.csv`, modify canonical `research/bootstrap`, or change E017.

Scientific ancestor: exact public V25 from `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, estimator blob `195373a110215256b759d7c172ba8c923c62e5cc`.

Canonical comparator E007: raw final-layer MSE `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

## Frozen mechanism

For each frozen old-source D21 contraction, sample the contraction-row index with replacement and apply inverse-probability weighting. The exact sum is unchanged in expectation.

Sample count is fixed at `384`.

Sampling is **with replacement**.

The sampling distribution is computed once per diagnostic contraction from the stacked AP/AA/PP row energy. For row index `j`,

`score_j = sqrt(sum(AP[...,j]^2 + AA[...,j]^2 + PP[...,j]^2))`,

and `p_j = score_j / sum(score)`.

If the entire score vector is exactly zero, use the mathematically equivalent uniform distribution. No clipping, floor, alternate distribution, adaptive sample count, redraw rule, averaging of independent sketches, or probability sweep is permitted.

Seed rule is frozen as

`18018 + 1000*dump_index + 32*layer + source_index`.

## Frozen data and targets

- Public Phase-2 `mini` only.
- Dump/MLP indices exactly `4,5,6,7`.
- Layers exactly `8..14`.
- All currently confined old sources at those layers.
- No target `final_means`, teacher forcing, fitting, regression, or reference-output use.
- Estimator output is not modified; instrumentation is read-only.

Primary diagnostic target is the exact old-tier D21 contraction contribution exposed by V25 `_dslices`, compared against the importance-sampled estimate on identical state.

## Frozen quantitative path

Memo cost accounting is frozen:

- old-leg/shared family: `55.8 / 260.1` units;
- sampled-row fraction: `384 / 1024 = 0.375`;
- ideal sampled family cost: `20.925` units;
- fixed overhead allowance: `4.0` units;
- allowed family cost: `24.925` units;
- target family ratio: `24.925 / 55.8 = 0.4466845878`;
- net chain saving: `(55.8 - 24.925) / 260.1 = 0.1187043445`;
- projected utilization from E007: `0.32313981`;
- projected adjusted score at unchanged E007 raw: approximately `7.2060e-09`.

## GO gates

All must pass:

1. Aggregate old-D21 relative RMS over all frozen samples `<= 0.015`.
2. Every recorded dump/layer/source old-D21 relative RMS `<= 0.022`.
3. Targeted-family projected billed-cost ratio `<= 0.4466845878` under the frozen arithmetic accounting above.
4. Conservative projected whole-estimator utilization `<= 0.325`.
5. Projected adjusted score using E007 raw `<= 7.25e-09` and strictly `< 8.17e-09`.
6. All sampled estimates finite and deterministic for the frozen seed rule.
7. No new persistent `n x n` state; only sampled indices/probabilities/weights and sampled factor slices.
8. Focused diagnostic wall time must complete without residual-exhaustion behavior; no official 400 ms scorer budget is invoked in E018.

Any eventual end-to-end promotion remains separately required to keep raw final-layer MSE `<=2.23e-08`, failures `0/100`, and must not use compute savings to mask raw-accuracy regression.

## Kill rule

Failure of any gate is `NO-GO / DROP E018`.

No rescue under E018 by changing sample count, switching distributions, probability clipping/flooring, multiple-sketch averaging, changing seeds, layer window, dump subset, old-source eligibility, teacher forcing, target fitting, holdout access, or running the official scorer.
