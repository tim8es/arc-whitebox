# E103 Result — production-shape implementation GO only

Idempotency key: `ARC-E103-ORTHOGONAL-ANTITHETIC-PRODUCTION-SHAPE-20260918`

## Provenance

- Branch: `research/e103-orthogonal-antithetic-production-shape-20260918`.
- Direct canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Protocol commit: `4cefae2b96a9628981306204eeede77c90250114`.
- Implementation commit: `c20f7d09229683f70701c376540c85b08ed236fc`.
- Focused tests commit: `f26cae27367c9e927ca5b4ad20a6bf2311099c46`.
- Focused workflow commit: `58b11b8d9ceb8d35ec37f2504ed6a5023dc1f330`.
- Focused run/job: `35287177161 / 105421990554`, success.
- Production driver commit: `b71109cc178a52cb0692b4fd0025244659cdfd24`.
- Sole production workflow commit: `868e31d4a6c0c438eccae185b04bb25d81186f09`.

## Sole production-shape evidence

- run: `35287256818`
- job: `105422236549`
- conclusion: success
- artifact: `e103-production-shape`
- artifact ID: `10525181002`
- artifact ZIP SHA256:
  `2141c794724b30e706822f1b1a04d61a73bb7d979db04d7c078933e73099630f`
- artifact size: `803` bytes.

Frozen shape/mechanism:

- width/depth: `1024 / 16`
- trajectories: `4096`
- synthetic weight seed: `103103`
- sampling/setup seed: `103104`
- exact E100 Haar-QR + independent chi-radius positive samples with antithetic negatives
- float32 dense ReLU propagation, float64 layer-mean reductions
- no targets, public data, scorer, holdout, full split, fitting, V29 or covariance state.

Measured:

- output shape: `(16,1024)`
- finite: true
- max absolute prediction: `5.608154855319299`
- flopscope all-in FLOPs: `149047446192`
- measured utilization: `0.0677789313122048`
- E100 analytic estimate: `140319042219` FLOPs / `0.06380971272801617`
- measured minus analytic: `8728403973` FLOPs
- wall time: `1.9422758040000048 s`
- exact antithetic pair max abs: `0.0`
- input variance: `0.9986440860698316`
- input fourth moment: `2.9873390141472815`.

All frozen gates passed, including measured utilization `<=0.12` and `<=0.135`.

## Decision

**E103 = PRODUCTION-SHAPE IMPLEMENTATION GO ONLY.**

This closes the E100 packaging/cost uncertainty: the mechanism is executable at
actual Phase-2 shape and has substantial measured compute slack.

It does **not** establish raw final-layer MSE `<=1.89e-8`; no target was read.
The dominant unresolved question is now absolute estimator variance/error, not
production compute.

No public/public-mini, official scorer, holdout/full, benchmark target, tuning,
rerun, canonical mutation, ledger mutation, or merge occurred.
