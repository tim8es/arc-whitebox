# Research-owner portfolio receipt — E112 / E113

Receipt key: `ARC-OWNER-PORTFOLIO-E112-E113-20260919`

Archive branch: `research/owner-portfolio-e112-e113-20260919`

Canonical reference: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

## Portfolio mandate

At most two new, truly disjoint post-E111 hypotheses were allowed. Both were required to be:

- protocol-first;
- target-free;
- exact-small-width verified;
- cost-admitted below utilization `0.13`;
- executed exactly once locally/synthetically;
- immutable-artifact backed;
- no rescue/rerun;
- no reopening of E104-E111.

Exactly two hypotheses were opened: E112 and E113.

## E112 — fourth-order Edgeworth scalar closure

Branch/head:

`research/e112-edgeworth4-relu-plugin-20260919@58c4f203990d3336a41d060a5a9d7bbf05e0ad58`

Mechanism:

- deterministic scalar marginal closure;
- exact mean, variance, skewness and excess kurtosis;
- frozen fourth-order Edgeworth positive-part correction;
- no sampler/control/fitted target.

Frozen exact gate:

- input dimension 2;
- width 8;
- depth 4;
- seed 112112;
- exact angular sector integration;
- analytic Rayleigh moments through order 4;
- no Monte Carlo/quadrature.

Execution:

- run `35455219121`
- job `105929179847`
- artifact ID `10588046582`
- ZIP SHA256 `406132e2cd2ec7a50b103b67866e62269795329333370caf4c93920df6909a1b`
- JSON SHA256 `619009f2eee0f228af9db1c9f10ec1992d9da0e2d119c15c94c4d01ad07b5a7d`
- deterministic replay max abs `0.0`

Measured final-layer bias:

- plain Gaussian bias MSE: `4.3282315571962346e-03`
- E112 bias MSE: `3.0035784800557875e-04`
- E112/Gaussian: `0.06939505061973768`
- relative Gaussian-bias removal: `93.06049493802623%`
- E112 / raw target `1.89e-8`: `15891.9496299248x`

Pooled all-layer bias MSE:

`2.267547225071582e-04`.

Cost admission:

- all-in upper FLOPs `149720512434`
- utilization `0.06808500640272541`
- cost gate PASS.

Verdict:

**TERMINAL NO-GO / DROP E112**.

The mechanism is a large relative improvement but misses the absolute target by four orders of magnitude. No production gate is authorized.

## E113 — top-4 actual-gate-conditioned Gaussian closure

Branch/head:

`research/e113-top4-gate-conditioned-plugin-20260919@b94cceb787715bafe3736d77798b1a4afeffc4a7`

Mechanism:

- deterministic structural conditional closure;
- each output uses the actual four-bit upstream gate state from its four largest-|weight| parents;
- 16 exact gate states;
- no fitted latent mixture, sampler, or control variate.

Frozen exact gate:

- input dimension 2;
- width 8;
- depth 4;
- seed 113113;
- exact angular sectors and exact gate-state probabilities/moments;
- no Monte Carlo/quadrature.

Execution:

- run `35455222505`
- job `105929188669`
- artifact ID `10587877752`
- ZIP SHA256 `67b1f603eb680825aef96ff4e031ad04be9302e2fd11ed974250685f5a3b7a32`
- JSON SHA256 `c576acd35e02c16c2e2856681327c13c617a77a69fa349ae0430efeb3ce5182d`
- deterministic replay max abs `0.0`
- maximum state-probability closure error `2.220446049250313e-16`

Measured final-layer bias:

- unconditional Gaussian bias MSE: `3.250972934646355e-02`
- E113 bias MSE: `2.5704565401863883e-03`
- E113/Gaussian: `0.07906730052386626`
- relative Gaussian-bias removal: `92.09326994761337%`
- E113 / raw target: `136002.99154425334x`

Pooled all-layer bias MSE:

`1.3039198341694728e-03`.

Cost admission:

- all-in upper FLOPs `151720512434`
- utilization `0.06899450110449834`
- cost gate PASS.

Verdict:

**TERMINAL NO-GO / DROP E113**.

Actual hidden-gate conditioning is informative but nowhere near the absolute accuracy required. No production gate is authorized.

## Portfolio comparison

Both hypotheses pass integrity and cost admission and both materially improve their own frozen unconditional-Gaussian baselines.

Neither satisfies the preregistered absolute small-exact gate.

Therefore:

- **strongest surviving mechanism: NONE**
- **production promotion from this portfolio: NOT AUTHORIZED**
- **competition GO: false**

For information only, E112 is the stronger failed hypothesis by normalized final bias ratio (`0.06940` vs `0.07907`) and has the smaller exact final bias on its own frozen instance. This does **not** make E112 a survivor and does not authorize a rescue or production run.

## Next production gate

Because there is no survivor, there is no E112/E113 production gate to execute.

The next production gate is defined only as a **frontier admission template** for a future new mechanism ID (E114+); it is not an authorization to create or run that mechanism in this receipt.

A future mechanism may enter production only after all of the following are frozen and passed:

1. direct/disjoint mechanism identity; no E104-E113 rescue;
2. exact small-width reference at width <=8, depth <=4;
3. final-layer deterministic closure bias MSE `<=1.89e-8`;
4. pooled all-layer deterministic closure bias MSE `<=1.89e-8`;
5. pre-code complete all-in production upper utilization `<=0.13`;
6. deterministic replay and independent verifier PASS.

Only then may one production-shaped synthetic gate run, frozen to:

- width `1024`;
- depth `16`;
- existing E104 trajectory law unless the new mechanism mathematically requires no trajectories;
- no public/public-mini/scorer/holdout/full targets;
- no tuning/sweep/rerun;
- complete measured FLOP ledger;
- target-free final-layer stochastic-risk estimator when the production mechanism remains randomized.

Until a new exact-small-width survivor exists, **production execution is blocked by scientific admission, not by compute**.

## Integrity

- E112 scientific runs: exactly one.
- E113 scientific runs: exactly one.
- public/public-mini/scorer/holdout/full: none.
- canonical mutation: none.
- ledger mutation: none.
- merge: none.
- E104-E111 reopened: no.
