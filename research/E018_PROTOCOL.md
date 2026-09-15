# E018 — unbiased importance-sampled old-D21 contractions

Status: frozen implementation diagnostic.

Idempotency key: `ARC-E018-START-NOW-20250915`.

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Scope

E018 is development-only. It must not run the official scorer, touch holdout data, mutate `research/ledger.csv`, modify canonical `research/bootstrap`, or change E017.

Scientific ancestor: public V25 from `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, estimator blob `195373a110215256b759d7c172ba8c923c62e5cc`.

Canonical comparator E007: raw final-layer MSE `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

## Frozen mechanism

For each frozen old-source D21 contraction, sample contraction-row index `j` with replacement and apply inverse-probability weighting. Sample count is exactly `384`.

For each row index `j`, the sampling score is

`score_j = sqrt(sum(AP[...,j]^2 + AA[...,j]^2 + PP[...,j]^2))`,

and `p_j = score_j / sum(score)`.

If all scores are exactly zero, the distribution is uniform. No clipping, flooring, alternate distribution, adaptive count, redraw rule, multi-sketch averaging, tuning, or sweep is permitted.

Seed rule:

`18018 + 1000*dump_index + 32*layer + source_index`.

## Frozen data

- public Phase-2 `mini` only;
- dump indices exactly `4,5,6,7`;
- V25 layers exactly `8..14` using the estimator's zero-based `li` numbering;
- all confined old sources at those layers;
- no target `final_means`, teacher forcing, fitting, regression, reference-output use, scorer, or holdout;
- estimator output is unchanged; instrumentation is read-only.

## Frozen cost accounting

- old-leg/shared family: `55.8 / 260.1` units;
- sampled fraction: `384 / 1024 = 0.375`;
- sampled family cost: `20.925` units;
- fixed overhead allowance: `4.0` units;
- allowed family cost: `24.925` units;
- family ratio: `24.925 / 55.8 = 0.4466845878`;
- net chain saving: `(55.8 - 24.925) / 260.1 = 0.1187043445`;
- projected utilization from E007: `0.32313981`;
- projected adjusted score at unchanged E007 raw: `~7.2060e-09`.

## GO gates

All must pass:

1. Mean per-record old-D21 relative RMS `<= 0.015`.
2. Worst per-record old-D21 relative RMS `<= 0.022`.
3. Targeted-family projected billed-cost ratio `<= 0.4467`.
4. Conservative projected whole-estimator utilization `<= 0.325`.
5. Projected adjusted score using E007 raw `<= 7.25e-09` and strictly `< 8.17e-09`.
6. All sampled estimates finite and deterministic under the frozen seed rule.
7. All frozen dump/layer pairs are observed and no new persistent candidate `n x n` state is introduced.
8. The local diagnostic completes without residual-exhaustion behavior; no official 400 ms scorer budget is invoked.

Failure of any gate is `NO-GO / DROP E018`.

No rescue under E018 by changing sample count, distribution, probabilities, clipping/flooring, seeds, layers, dump subset, eligibility, teacher forcing, fitting, holdout access, scorer execution, or tuning/sweep.
