# E031 — deterministic source-axis moment closure

Idempotency key: `ARC-CONTINUE-LEAD-20260915`

Status: preregistered; protocol-only first commit.

## Provenance

- Branch: `research/e031-source-axis-moment-closure-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Exact reference estimator: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Public Phase-2 mini: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- Frozen diagnostic index: `0` only
- Width/depth: `1024 x 16`
- Budget: `B = 2**41 = 2,199,023,255,552`

E029 and E030 are terminal NO-GO. E031 does not use E029 angular cubature, E030 latent-Gaussian/Nyström state, E018 importance/HT source sampling, or E008 spatial TensorSketch.

## Hypothesis

The expensive K3 chain preserves one dense A/P pair per historical source. The source count is at most 15, but old-source cost is approximately linear in that count. Instead of selecting sources or sketching spatial Hadamard products, E031 tests whether the *source-index dependence itself* is low-dimensional.

For every live source stack at a D21 evaluation,

`A in R^(k x n x n), P in R^(k x n x n)`, 

replace the source axis by a deterministic degree-2 age basis (`q = 3`): constant, centered linear age, centered quadratic age. The basis is orthonormalized by QR. Every source remains represented through the three aggregate coefficients; there is no source sampling, importance weighting, dropping, random sign sketch, or source-specific tuning.

This experiment is deliberately staged as a **representation preflight**. It must demonstrate both enough source-axis fidelity and a compute path compatible with a winning score before any estimator rewrite is justified.

## Frozen basis

For a live source count `k`, define normalized source coordinate

`x_s = 0` for `k=1`, otherwise `x_s = 2*s/(k-1)-1`, `s=0,...,k-1`.

Construct columns `[1, x, x^2]`, truncated to `q=min(3,k)`, and obtain `Q` from ordinary reduced QR. Projection is `Pi = Q Q^T`. No alternate polynomial family, rank, age weighting, centering rule, random rotation, or sweep is allowed.

## Frozen scientific fidelity diagnostic

Use exact V25 on public mini index 0 and instrument `_dslices` without changing the estimator output trajectory. At every D21-capable call, compute the joint source Gram

`G_st = <A_s,A_t>_F + <P_s,P_t>_F`.

The source-axis projection loss is

`eps = sqrt(max(0, (tr(G) - tr(Pi G)) / tr(G)))`.

Record energy-weighted aggregate RMS and worst-layer RMS. The diagnostic must not replace A/P inside V25, so this measurement does not create a second estimator trajectory or tune against the target.

Fidelity gates are frozen at:

1. aggregate source-axis RMS `<= 0.010`;
2. worst D21-layer RMS `<= 0.022`.

The 2.2% worst-layer threshold is aligned with the existing D21 fidelity boundary used in the upstream cost/accuracy anatomy; E031 uses the stricter 1.0% aggregate requirement because the target is materially beyond E021.

## Frozen compute preflight

The diagnostic also computes an optimistic lower-bound utilization from the verified V29/V25 anatomy. Frozen constants:

- current exact-chain steady anatomy: `260.1 u`, where `u=2*n^3`;
- old K3 tier: `106.8 u`;
- non-old floor after deleting the whole old tier: `153.3 u` (`260.1 - 106.8`);
- target utilization: `<=0.14`, equivalently `<=143.36 u` at `B=1024u`.

A source-axis closure cannot be competitive if it only removes old-tier work, because the optimistic zero-cost-old-tier floor is `153.3/1024 = 0.14970703125`.

Therefore E031 requires a second, exact-op-stream path: at least `9.94 u` of the remaining non-old work must be removable or repriced *without changing estimator mathematics*. For the preflight, only already established exact algebraic opportunities may count: dead-zero lanes and mathematically exact operator fusion/elision. No Strassen approximation/reordering is credited, no E014 joiner retry is credited, and no speculative savings are counted.

The script must report:

- zero-old-tier floor utilization;
- required additional exact saving to reach 0.14;
- explicitly proven additional exact savings found in the inspected reference path;
- projected optimistic utilization after those proven savings.

Compute gate: projected optimistic utilization `<=0.14`. If the script cannot prove enough exact saving, E031 is NO-GO regardless of fidelity.

## Competitive gate

Even if both preflight gates pass, a later full candidate is allowed only if its fixed arithmetic predicts a score path to:

- adjusted `<2.5e-09`;
- raw final-layer MSE `<=1.89e-08`;
- utilization `<=0.14`;
- failures `0` and residual `<0.400 s`.

The preflight itself does **not** claim these score metrics; it determines whether implementing the representation is rational.

## Focused tests

Before the scientific diagnostic, tests must verify:

1. deterministic basis shape and orthonormality for `k=1..15`;
2. exact projection of synthetic source stacks whose source dependence is polynomial of degree <=2;
3. Gram-based residual-energy formula agrees with direct projection on a small synthetic tensor;
4. frozen compute arithmetic gives zero-old-tier floor `153.3/1024` and required saving `9.94 u` to reach 0.14 within numerical tolerance;
5. no random/importance/HT/source-drop code path.

## Exactly one bounded local diagnostic

One public-mini index-0 diagnostic only, plus ordinary focused unit tests. The V25 prediction itself remains unchanged; only source-axis Gram statistics and exact cost-accounting evidence are observed.

No official scorer, holdout, second mini index, tuning, rank sweep, alternate basis, rescue, or canonical mutation.

## Decision rule

All of the following must pass to justify a subsequent E031 full-candidate implementation:

1. aggregate source-axis RMS `<=0.010`;
2. worst-layer RMS `<=0.022`;
3. projected optimistic utilization `<=0.14` using only proven exact savings;
4. finite deterministic diagnostics and exact frozen scope.

Any failed or unevaluable gate => **NO-GO / DROP E031**. No rescue under E031. A failure at preflight means no estimator rewrite and no scorer.