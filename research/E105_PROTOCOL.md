# E105 — target-free two-Haar-block production risk certificate

Idempotency key: `ARC-E105-TWO-HAAR-RISK-20260919`

Status: protocol-first; no implementation or measurement at this commit.

## Provenance

- Branch: `research/e105-two-haar-risk-cert-20260919`
- Direct canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Parent scientific frontier: authoritative E104 Haar radial Rao-Blackwellization on
  `research/e104-haar-radial-raoblackwell-20260918`.
- E091/E098/E099 are excluded by owner instruction.

## Frozen question

E104 production implementation, shape and compute have already been independently verified.
The remaining uncertainty is the absolute final-layer stochastic risk of the two-Haar-block
E104 estimator.

For one fixed zero-bias production-shape network let `B1` and `B2` be the final-layer
means from the two independent Haar blocks already present inside the frozen E104
4096-trajectory estimate, where each block includes both antipodes and the analytic
`E[chi_1024]` radius.

The production estimate is

`M = (B1 + B2) / 2`.

Because the two blocks are iid, unbiased block estimators,

`E[(B1_j - B2_j)^2 / 4] = Var(M_j)`.

Therefore

`Rhat = mean_j((B1_j - B2_j)^2) / 4`

is a target-free unbiased estimator of the raw final-layer coordinate MSE caused by
direction randomness of the frozen two-block E104 estimate on the fixed network.

This is a certificate/measurement only. It does not modify the E104 estimator law.

## Frozen production shape

- width: 1024
- depth: 16
- total trajectories: 4096
- positive trajectories: 2048 = exactly two independent 1024-column Haar blocks
- antithetic endpoints: exact +/-
- analytic radius: `E[chi_1024]`
- weight seed: 104104
- direction seed: 104105
- weights: iid float32 `N(0,2/width)`, zero bias
- propagation: float32 dense linear + ReLU
- layer output means: float64
- budget: `2**41`

All Gaussian draws used to construct Haar matrices must be generated through
`flopscope.numpy.random` inside the budget context so the production estimator path has
complete billed RNG accounting.

## Focused TDD

Before the production diagnostic, tests must verify:

1. the block-risk identity numerically on iid synthetic block estimates;
2. exact re-composition `(B1+B2)/2` of the two equal-size block mean;
3. the billed Haar sampler has exact antithetic pairs and deterministic replay;
4. source inspection contains no benchmark/public/scorer/holdout access.

## Exactly one bounded production diagnostic

One GitHub Actions run after GREEN. It may execute the frozen estimator twice inside the
same job solely to verify deterministic replay. No workflow rerun.

Record:

- target-free raw-MSE risk estimate `Rhat`;
- adjusted-risk proxy `Rhat * max(0.1, utilization)`;
- fully billed FLOPs and utilization;
- wall time;
- final prediction hash and replay equality;
- block-mean hashes and block re-composition error;
- exact antithetic-pair error;
- finite status;
- immutable artifact digest/ID in the terminal receipt.

No public/public-mini, scorer, holdout/full, benchmark target, tuning, sweep, seed/rank/sample
variation, rescue, canonical mutation, or ledger mutation.

## Frozen gates

All gates must pass for E105 GO:

1. `Rhat <= 1.89e-8`;
2. adjusted-risk proxy `< 2.5e-9`;
3. measured utilization `<= 0.14`;
4. exact accounting reconciliation;
5. finite prediction and block means;
6. deterministic replay max absolute prediction difference `== 0`;
7. deterministic replay raw-risk difference `== 0`;
8. exact antithetic pair max abs `== 0`;
9. block re-composition max abs `<= 1e-12`;
10. no benchmark targets/public/scorer/holdout/full access.

Any failed or unevaluable scientific gate => terminal NO-GO / DROP E105 with no rerun or rescue.
