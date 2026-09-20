# E140 protocol — primary-source post-V29 research

Idempotency key: `ARC-E140-PRIMARY-SOURCE-POST-V29-20260921`

Status at freeze: **PRIMARY-SOURCE RESEARCH ONLY / NO E140 SCIENTIFIC RUN AUTHORIZED**.

Branch:
`research/e140-primary-source-post-v29-20260921`

Parent:
`research/e137-mit-v25-v29-improvement-scout-20260921`

## Goal

Read the official ARC cumulant-propagation sources and the public 504aldo V29 release,
separate established facts from open questions, and admit at most one genuinely new,
falsifiable post-V29 hypothesis.

This is not a version-summary task. The note must contain a new algebraic derivation or
a primary-source-backed terminal UNKNOWN/NO-GO.

## Evidence policy

Priority:

1. ARC official paper/code/blog;
2. 504aldo public source code, derivation map, community post, and raw findings log;
3. local `arc-whitebox` receipts only for overlap/exclusion.

Every substantive claim must be labeled:

- **ARC PRIMARY**;
- **504ALDO PRIMARY**;
- **LOCAL VERIFIED**;
- **DERIVATION**;
- **HYPOTHESIS**;
- **UNKNOWN**.

## Mandatory post-V29 exclusions

Do not relabel as new:

- V16b/V17/V18/V19/V22/V24/V25/V26-V29;
- source dropping/windowing;
- slice-only/A716/memoryless D21 closure;
- CP/hub-column caps;
- symmetric Tucker/shared-row-basis retuning;
- Gaussian/scale mixtures;
- output correction/control variates;
- higher feedback/residual rank;
- precision/Strassen/pricing polish;
- adjoint-only final sensitivity;
- E132/E134/E135;
- E137 H137 CountSketch final-product patch;
- E124 pair-tree or E127 hypergraph/cluster rescue.

## Hypothesis admission gates

A hypothesis is admissible only if it:

1. carries fully off-diagonal quenched order-3 information;
2. is not a compression already killed by 504aldo F65/F66/F71/F76/F78/F82/F88;
3. has an algebraically closed transport rule under dense linear maps and the multiplicative
   Wick scaling of the carried K3 term;
4. exposes D3/D21 without reconstructing an n^3 tensor;
5. has a credible production path at utilization <= 0.135;
6. has a target-free exact-small falsifier;
7. does not require benchmark targets, fitted final errors, or a sweep to select the mechanism.

If no candidate passes all seven by inspection, E140 must end
`UNKNOWN_NO_ADMISSIBLE_POST_V29_HYPOTHESIS`.

## Frozen candidate class

The only candidate allowed for E140 research is a **symmetric matrix-vector K3 response
mode** representation:

[
K_{ijk}approxsum_{a=1}^{m}rac{
R^{(a)}_{ij}v^{(a)}_k+
R^{(a)}_{ik}v^{(a)}_j+
R^{(a)}_{jk}v^{(a)}_i}{3},
qquad R^{(a)}=R^{(a)T}.
]

The research note must prove or refute the following before admitting it:

- closure under `K -> (W,W,W)K`;
- closure under coordinatewise Wick scaling `K -> (d,d,d)K`;
- direct formulas for D3 and D21;
- distinction from symmetric Tucker and slice-only closures;
- production cost plausibility for the frozen first point `m=4`.

No other E140 mechanism may be substituted if this candidate fails. Failure means
UNKNOWN/NO-GO, not a rescue hypothesis.

## Frozen successor falsifier — protocol only

No run is authorized by this commit. If a later message explicitly authorizes execution,
the first and only Stage-A falsifier is:

- representation rank: `m=4`;
- exact reference: ARC K=3 simple full/factored state on synthetic small dense fixtures,
  never competition targets;
- fixture A: width 32, depth 8, zero bias, deterministic He-Gaussian weights, seed 140032;
- fixture B: width 16, depth 8, deterministic dense adversarial rotation/diagonal-gain
  construction, seed 140016;
- after every nonlinear birth, materialize K3 only on the small fixture, take the top-4
  SVD of the mode-3 unfolding K_(12),3, reshape each left singular vector to a symmetric
  matrix R_a (the unfolding columns are vectorized symmetric slices), then orthogonally
  symmetrize the resulting sum_a R_a tensor v_a. Because the exact K3 is symmetric,
  this symmetrization cannot increase Frobenius error;
- propagate the rank-4 candidate through the next linear/Wick step using only the closed
  response-mode formulas;
- compare candidate D3/D21 to exact K3 D3/D21 before the next nonlinear update.

Target-free GO gates:

1. exact linear-transport closure identity <= `1e-12` in float64;
2. exact Wick-scaling closure identity <= `1e-12`;
3. finite and deterministic replay;
4. pooled D21 relative RMS <= `0.022` on both fixtures;
5. no layer D21 relative RMS > `0.03`;
6. D3 relative RMS <= `0.022`;
7. production arithmetic upper bound, including four symmetric matrix transports,
   vectors, D3/D21 extraction, covariance/closure, birth-mode construction and
   recompression, <= `0.135 * 2^41` FLOPs;
8. production recompression may not materialize an `n^3` tensor or perform an
   `O(n^3 m)` dense SVD.

Any failed/unevaluable gate => terminal NO-GO for H140 rank-4 SMV. No rank sweep, rescue,
seed replacement, public/scorer/holdout/full run, or target read.

## Repository firewall

This E140 research lane may create only protocol/note/receipt artifacts unless execution
is separately authorized.

No canonical/ledger mutation.
