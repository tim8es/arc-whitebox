# R233 V25 output-preserving counted-FLOP audit

Status: TERMINAL PRE-MINI NO-GO (materiality gate)
Run ID: R233-v25-onehot-wick-cse-20260923

## Question

Can pinned public V25 be made cheaper without changing estimator outputs by removing an
algebraically redundant source-level computation, with a counted-FLOP reduction large
enough to justify one bounded mini-100?

## Pinned evidence

V25 source:
- repository: 504aldo/whest-p2-cumulant-k3
- commit: 18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45
- file: estimators/estimator_v25.py
- git blob: 195373a110215256b759d7c172ba8c923c62e5cc
- source SHA256 measured by the fixture:
  c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20

R209 V25:
- normalized record SHA256:
  f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742
- counted FLOPs per MLP: 806,303,721,965
- mean adjusted score: 8.170397440117225e-9
- shape: [16,1024]
- budget: 2**41
- failures: 0/100

R231 showed that compute-only savings at fixed raw MSE eventually hit a 0.1-factor score
floor of 2.228303490170447e-9, so a micro-optimization needs material counted savings to
matter.

## Frozen optimization: ONEHOT-WICK-ROW-SELECT

In pinned V25, _term_prog constructs SL2, SR2, and SL1 with exactly one nonzero per row:

    SL2[t, wl] = coef
    SR2[t, wr] = 1
    SL1[t, wl] = coef

but predict() evaluates those sparse coefficient maps as dense matrix multiplies:

    WL2 = SL2 @ WT
    WR2 = SR2 @ WT
    WL1 = SL1 @ WT

The frozen rewrite is:

    WL2 = take(WT, wl2_idx, axis=0) * sl2_coef[:, None]
    WR2 = take(WT, wr2_idx, axis=0)
    WL1 = take(WT, wl1_idx, axis=0) * sl1_coef[:, None]

For a row s with one nonzero s[j]=c,

    s @ WT = c * WT[j,:]

so the rewrite changes only how the same values are formed.

This is separate from R232: no estimator-family, state, approximation, closure, source
rank, fitted coefficient, or target-facing logic changes.

## Source-level structural proof

Pinned source construction at lines 384-399 assigns one and only one entry per row of
SL2, SR2, and SL1. The suite-relevant term counts reconstructed from the exact source are:

| mode | d2 terms | d1 terms |
|---|---:|---:|
| 0 | 6 | 4 |
| 1 | 52 | 14 |

Suite scheduling is:
- layer 0: mode 0, d2+d1;
- layers 1..14: mode 1, d2+d1;
- layer 15: trimmed mode 1, d1 only.

## Independent micro-fixture

Exactly one micro-fixture ran on standard ubuntu-24.04 GitHub Actions in this public
repository:
- workflow run: 35799879085
- job: 106987553512
- trigger commit: 357e1302b826f9debc8e547fc1c57c384d7affff
- Python: 3.11.16
- flopscope: 0.12.1+np2.4.6
- fixture width: n=8
- estimator executed: false
- target data used: false
- mini-100: false

The fixture statically parsed constants from the pinned V25 source; it did not import or
execute the estimator.

Results:

| mode | baseline FLOPs | candidate FLOPs | saving | WL2 exact | WR2 exact | WL1 exact |
|---|---:|---:|---:|---|---|---|
| 0 | 5,248 | 592 | 4,656 | bitwise | bitwise | bitwise |
| 1 | 38,704 | 4,304 | 34,400 | bitwise | bitwise | bitwise |

For both modes the measured FLOPs exactly equal the preregistered analytic formulas.

Therefore:
- Identity gate: GO.
- Counted-FLOP gate: GO.

The artifact ZIP is ID 10725706577, SHA256
43afd7fe7d6d2896cba0b2fa5c514ec3097469b13d541d5c896b8e9ba8abf184.

## Production cost proof

The official flopscope float32 pricing used by the frozen model is:
- matmul (M,K)@(K,N): M*N*(2*K-1)
- take/fancy gather: 4*N
- elementwise multiply: N

V25 has K=21 Wick-pair columns, so:
- one dense SL/SR transform costs 41*T*n;
- SL row-select costs 5*T*n;
- SR row-select costs 4*T*n.

Thus:
- d2 pair saving (WL2+WR2): 73*T*n;
- d1 saving (WL1): 36*T*n.

Applying the exact suite schedule gives:
- layer 0 saving: 595,968 FLOPs;
- each layer 1..14 saving: 4,403,200 FLOPs;
- layer 15 saving: 516,096 FLOPs;
- total: 62,756,864 FLOPs per MLP.

Against the pinned V25 count:

    62,756,864 / 806,303,721,965
    = 7.783278470680822e-5
    = 0.007783278470680822%

Projected count becomes 806,240,965,101 FLOPs and C/B moves only from
0.36666448157347986 to 0.3666359430558259.

Holding raw MSE fixed, the projected mean adjusted score is
8.169761515332299e-9, an absolute reduction of only 6.359247849260651e-13.

## Frozen meaningful gate

The preregistered materiality threshold was a reduction of at least 0.1% of pinned V25:

    required >= 806,303,722 FLOPs/MLP

Observed/proved projection:

    62,756,864 FLOPs/MLP

The candidate reaches only 7.7833% of the already modest threshold and misses it by a
factor of about 12.85.

Therefore:
- Meaningful gate: NO-GO.
- Public mini-100 authorization: DENIED by frozen protocol.
- No candidate estimator was created or run.

## Decision

TERMINAL PRE-MINI NO-GO.

ONEHOT-WICK-ROW-SELECT is a real, output-preserving counted-FLOP optimization. Its local
transform savings are large, and the fixture proves bitwise identity and exact flopscope
cost reduction. However those transforms are too small a fraction of V25's total cost:
the full projected reduction is only 0.00778%.

The correct conclusion is not that no exact micro-optimization exists; one does. The
conclusion is that this source-level reduction cannot approach a meaningful V25 score
frontier and therefore does not justify a mini-100.

No rescue optimization is introduced after this result.

## Sources

[S1] Exact upstream V25 source:
https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v25.py

[S2] Official flopscope operation cost reference:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/flopscope-primer.md

[S3] R226-integrated V25 normalized record:
https://github.com/tim8es/arc-whitebox/blob/20fafab5471e6ed227562c651179dd2ef331ea22/research/results/R209-v25-mini100.json

[S4] R231 V25 tail/frontier receipt:
https://github.com/tim8es/arc-whitebox/blob/f36d8011fe1cf8eadf87e0751a18ca9555f9408f/research/r231/R231_V25_ERROR_TAIL_RECEIPT.json

[S5] R233 Actions fixture run:
https://github.com/tim8es/arc-whitebox/actions/runs/35799879085

## Constraints confirmed

No canonical estimator edit. No estimator execution. No mini-100. No paid compute.
No private/holdout data. No submission. No R232 estimator-family work. Exactly one
isolated micro-fixture run.
