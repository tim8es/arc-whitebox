# E137-H137 Stage-A execution protocol — pinned-V25 old-tier CountSketch falsifier

Idempotency key: `ARC-E137-H137-STAGEA-COUNTSKETCH-S512-20260921`

Status at freeze: **ONE TARGET-FREE ACTIONS RUN AUTHORIZED AFTER CODE**.

This is the successor execution protocol required by the note-only E137 scout protocol.
It does not change H137. It operationalizes the already-selected first point.

## Frozen baseline

Public repository:
`504aldo/whest-p2-cumulant-k3`

Pinned public head:
`18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Pinned V25 file:
`estimators/estimator_v25.py`

Pinned V25 git blob:
`195373a110215256b759d7c172ba8c923c62e5cc`

The executable must verify the vendored file's SHA-1 git blob identity before import.

No V25 constant, rank, age gate, lambda rule, source birth, D3/D21 formula, K4 rule,
feedback rank, or final-layer trim may change.

## Frozen H137 patch

Sketch width:

`s=512`.

Patch only the old-tier factor-space D21 contractions

`sum_k LA_k FA_k^T + LP_k FP_k^T`

and the analogous nested-tier contractions before the existing `U^T` and `Qc^T`
lifts.

Use one balanced CountSketch over the hub-column axis `j=0..1023`:

1. construct a PCG64 permutation of 1024 columns;
2. pair the permuted columns into exactly 512 buckets;
3. draw one independent Rademacher sign per original column;
4. freeze hash/sign from seed
   `137512000 + layer_index`;
5. use the same layer sketch for LA/FA and LP/FP and for both old tiers.

For an operand `X[...,j]`, the sketch is the signed sum of the two columns assigned to
each bucket.

The candidate product is

`(X S)(Y S)^T`.

The baseline product remains exact and is still used by V25 state evolution in Stage A.
The sketched product is side-channel diagnostic only, so Stage A does not contaminate
later exact baseline states with approximation error.

## Frozen target-free corpus

Synthetic official-shape only; no benchmark data or final means.

- width: `1024`
- depth: `16`
- zero bias
- weights: iid PCG64 normal, float32, scale `sqrt(2/1024)`
- MLP seeds: `137200,137201`
- whestbench MLP seed field: `0`
- estimator setup seed: `137137`
- budget argument: `2^41`.

The weights are not selected from any error result.

## D21 error observable

At each non-final layer where `ka>0`, construct:

- exact total old-tier factor-space inner contribution after tier-2 lift;
- H137 sketched version using the frozen CountSketch;
- exact and sketched old-tier D21 after the existing right multiplication by `Qc^T`.

Because `Qc` is orthonormal, the two Frobenius relative errors should agree up to
floating-point noise; record both as an integrity check.

For layer `l` define

`eps_l = ||D21_old_sketch-D21_old_exact||_F / max(||D21_old_exact||_F,2^-100)`.

Primary pooled gate:

`eps_pool = sqrt(sum_l ||error_l||_F^2 / sum_l ||exact_l||_F^2) <= 0.022`

over both frozen MLPs and every measured old-tier layer.

Also record max per-layer relative error diagnostically. No per-layer threshold is added
post hoc.

## Full all-in cost proof

Competition hard budget:

`B=2^41=2,199,023,255,552 FLOPs`.

The pinned V25 public baseline has reported `C/B=0.3667`; however Stage A must compute
its own candidate upper from exact operation shapes.

For every patched exact old-tier contraction of shape

`X: (k,n,n), Y:(k,q,n) -> (n,q)`

charge baseline product

`F_exact = 2*k*n*q*n`.

Charge H137:

- sketch X: `3*k*n*n` scalar ops upper;
- sketch Y: `3*k*q*n` scalar ops upper;
- sketched contraction: `2*k*n*q*s`.

The factor 3 per input element covers signed multiply, bucket addition, and bookkeeping
conservatively.

All other V25 operations retain the **measured full baseline flopscope count** from the
unchanged exact execution.

Candidate all-in projected FLOPs:

`F_H137 = F_V25_measured - sum F_exact_patched + sum F_H137_patched`.

Required gates:

1. `F_H137 < F_V25_measured`;
2. `F_H137 <= B`.

Also record utilization and savings. This is a full all-in candidate projection because
only the explicitly billed old-tier product family changes.

## Determinism / firewall

Two complete diagnostic passes must produce bitwise-identical JSON before metadata hashes.

The candidate/harness may access:

- synthetic weights;
- V25 code;
- internal V25 D21 operands/state;
- flopscope counters.

It may not access:

- benchmark/public MLP weights;
- final means;
- exact output targets;
- scorer;
- holdout/full;
- any post-hoc final-output error.

## Frozen GO/NO-GO

GO requires all:

- pinned V25 blob identity match;
- finite exact/sketched states;
- at least one old-tier measurement on each frozen MLP;
- pooled relative D21 error `<=0.022`;
- candidate projected full all-in FLOPs strictly below measured V25;
- candidate projected full all-in FLOPs `<=2^41`;
- factor-space vs lifted-D21 relative-error agreement `<=1e-5`;
- deterministic replay bitwise exact;
- no target/reference/scorer access.

Any failed or unevaluable gate:

**TERMINAL NO-GO / CLOSE H137 COUNTSKETCH S=512.**

No sketch-width sweep, seed replacement, alternate hash, added averaging, rescue, or rerun.

A GO authorizes only a separately frozen final-MSE validation. This Stage-A run itself
must not perform final-MSE validation.
