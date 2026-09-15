# E046 Protocol — network-specific harmonic defect control

Status: PREREGISTERED / NOT RUN
Owner token: `ARC-E046-AUTHORIZE-NOW-20260916`
Date: 2026-09-16
Base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
Branch: `research/e046-harmonic-defect-control-20260916`

## Hypothesis

The dominant deterministic closure error after matching Gaussian first/second moments contains a network-specific angular component whose first practically useful unresolved contribution is degree 6. A fixed, low-rank degree-6 harmonic carrier can reduce final-layer bias materially without the source stacks/replay/checkpoint machinery of E041–E044 or the signed sigma ensemble of E045.

E046 tests **only** this mechanism. It does not propagate connected cumulant diagrams and does not combine with sampling/QMC, K3 carriers, checkpoint replay, source selection, signed weights, or adaptive blending.

## Why A, not B

Candidate A — network-specific harmonic defect control — has a direct bounded falsifier: if a fixed rank-64 degree-6 carrier does not lower the final-layer error while staying below the cost gate, the hypothesis is rejected. Its state and FLOPs are bounded by fixed dense projections.

Candidate B — connected-diagram dynamic programming for finite-width ReLU cumulants — is not E046 because its diagram state, contraction bookkeeping, and truncation rules introduce substantially higher implementation and FLOP risk. It remains untested here.

## Frozen representation

At each hidden layer, E046 maintains:

1. the same Gaussian mean/covariance state `(mu, cov)` as the vendored covariance baseline;
2. exactly `HARMONIC_RANK = 64` network-specific response directions;
3. exactly one degree-6 defect coefficient per response direction.

No degree other than 6 is represented. No rank adaptation is allowed.

### Response directions

For a width `n=1024` layer, build a fixed `n x 64` Walsh sign matrix using columns 0..63 of the Sylvester-Hadamard construction, normalized by `1/sqrt(n)`. For each layer after the first, map these response directions through the **next layer weight matrix only**, then orthonormalize with a thin QR. Canonicalize each QR column sign by requiring the largest-absolute entry to be non-negative; ties use the lowest index. The final hidden layer uses the normalized Walsh directions directly because there is no next hidden weight.

These directions depend only on network weights and fixed constants, never on truth labels, public-mini outputs, or measured residuals.

### Degree-6 defect coordinate

Let centered activation be `x - mu`. For every frozen response direction `q_r`, define the normalized scalar projection

`u_r = q_r^T (x - mu) / sqrt(q_r^T cov q_r + EPS)`.

The carried defect is the probabilists' sixth Hermite residual

`d_r = E[He6(u_r)]`, where `He6(t)=t^6 - 15 t^4 + 45 t^2 - 15`.

Gaussian closure has `d_r = 0`. E046 estimates the post-ReLU degree-6 response defect deterministically from the previous layer's rank-64 defect carrier and local Gaussian moments using the fixed response-direction projection below; it never constructs or stores a full sixth-order tensor.

### Fixed local projection rule

For each response direction, use exactly `GH_ORDER = 12` deterministic Gauss-Hermite nodes for the one-dimensional standardized response coordinate. The remaining orthogonal degrees of freedom are represented only through the Gaussian mean/covariance state. The 12-node rule is used to compute two quantities for the local ReLU map along each response coordinate:

- the Gaussian mean contribution;
- the degree-6 response coefficient, obtained by projection onto `He6`.

The previous layer's `d_r` enters only linearly through that fixed degree-6 coefficient. Cross-products `d_r d_s`, higher-degree generated terms, and degree-6-to-degree-6 connected diagrams are explicitly discarded.

The corrected neuron mean is the Gaussian closure mean plus the rank-64 response reconstruction of these linear degree-6 defects. The covariance update remains the vendored Gaussian covariance update; E046 does not alter off-diagonal covariance through the harmonic carrier.

## Frozen constants

- `WIDTH_EXPECTED = 1024`
- `DEPTH_EXPECTED = 16`
- `HARMONIC_DEGREE = 6`
- `HARMONIC_RANK = 64`
- `GH_ORDER = 12`
- `EPS = 1e-12`
- Walsh columns: exactly `0..63`
- QR: unpivoted thin QR
- sign canonicalization: max-absolute pivot non-negative, lowest-index tie
- no clipping of harmonic coefficients
- no damping or learned scalar
- no adaptive rank/order/degree
- no stochastic sampling
- no data-dependent fitting

## Accounting

All MLP-dependent arithmetic, including response construction, next-weight projection, QR preparation arithmetic represented in the estimator, local Gauss-Hermite projections, harmonic reconstruction, Gaussian covariance propagation, and final prediction arithmetic, must execute under the FLOP budget context.

The practical cost gate is utilization `<= 0.125`; this is intentionally stricter than the project's historical `0.14` ceiling.

## Focused RED tests

Before production implementation, tests must fail because `methods.e046_harmonic_defect_control` does not exist. Tests freeze:

1. constants above;
2. deterministic Walsh geometry and orthonormality;
3. deterministic sign canonicalization;
4. `He6` normalization under the fixed 12-node rule (`E[He6(Z)] = 0` and `E[He6(Z)^2] = 6!` within numerical tolerance);
5. zero-defect identity: with all `d_r=0`, harmonic correction is exactly zero;
6. linearity: doubling a synthetic defect carrier doubles the reconstructed correction;
7. no degree/rank adaptation.

RED must be confirmed in CI with no public-mini access.

## Frozen diagnostic

After focused GREEN, run exactly one diagnostic on:

- dataset: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini`
- index: `0`
- budget: `2**41`

No other public example may be touched before or after this diagnostic within E046.

The diagnostic performs one billed prediction plus one identical deterministic repeat only for the deterministic gate. It does not inspect any holdout/full split and does not invoke the official scorer.

## Quantitative GO gates

All must pass simultaneously:

- raw final-layer MSE `<= 1.89e-08`
- adjusted proxy `< 2.5e-09`
- utilization `<= 0.125`
- failures `== 0`
- estimator residual wall time `< 0.400 s` as measured by the project diagnostic convention
- all final outputs finite
- deterministic repeat max absolute difference `== 0`
- harmonic rank observed `== 64`
- harmonic degree observed `== 6`
- Gauss-Hermite order observed `== 12`

## Minimal falsifier

Any one of the following falsifies E046:

- a focused invariant cannot be implemented without violating the frozen representation;
- the single public-mini diagnostic violates any GO gate;
- non-finite harmonic state occurs;
- the fixed degree-6 correction requires clipping, damping, tuning, adaptive rank/order, or a rerun to remain stable.

## Kill rule

On the first failed gate or protocol-hard failure: **terminal NO-GO / DROP**. No rescue, rerun, hyperparameter change, clipping, damping, alternate constants, holdout, full split, sweep, official scorer, or reuse of the public-mini example is permitted under E046.

After terminal closure, a subsequent experiment may use the next free ID only as a new protocol-first lane from the then-authorized canonical base.

## Repository controls

- Do not mutate `research/bootstrap`.
- Do not mutate `research/ledger.csv`.
- Do not merge E046.
- The first E046 commit contains only this file.
