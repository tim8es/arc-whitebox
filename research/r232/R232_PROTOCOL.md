# R232 — Dual-resolution Richardson debiasing of V25 source compression

Date: 2026-09-23
Idempotency: `ARC-R232-V25-DRRE-20260923`
Branch: `research/r232-v25-dual-resolution-richardson-20260923`
Queue owner: `global-accuracy-research`

## 0. Frozen decision question

R232 tests exactly one new estimator family:

> **DRRE-V25** — run two deterministic V25 source-compression resolutions and
> cancel the leading rank-truncation bias by a fixed Richardson extrapolation.

This is estimator-level multiresolution debiasing. It is **not** rank selection,
tail gating, fitted blending, residual regression, a new K4 mode, feed-local lambda,
copula, CountSketch, response-aligned D21, Walsh/coset sampling, QMC, source-Hutchinson,
TT/SMV/RAP-K3, or a final scalar Edgeworth/saddlepoint closure.

The immutable history/legacy ledger contains no Richardson, extrapolation,
multilevel, Romberg, jackknife, two-rank debiasing or rank-extrapolation experiment.
Existing rank ladders measured individual ranks; they did not combine two complete
deterministic estimators to estimate the infinite-resolution limit.

## 1. Frozen evidence read before hypothesis selection

Governance:
- `AGENTS.md` blob `6d9c61537a282a7d141af316dd8be438d1015a49`;
- `research/RESEARCH_PROCESS.md` blob
  `bf5a4676d8f36100e2dfdde32d544a39661eba8d`.

Immutable experiment index:
- `research/history.json` blob
  `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`, 194 experiment IDs;
- `research/legacy-ledger.csv` blob
  `040e52efe01efd7280180b7e2d72901b4c2f0532`.

Immediate parent evidence:
- R227 terminal receipt blob
  `17f5b48580c7c6cf76b2966084b80024af04affe`;
- R231 error-tail receipt blob
  `a2cf807ce9617c464e0e60b12f0bbfc17e196cf4`.

R231 establishes that the V25 error is weakly concentrated and that a global raw-MSE
reduction of about 5.76% is required even at the 0.1 scoring floor. R232 therefore
does not select a tail subset.

## 2. Pinned parent

Pinned upstream:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

V25 blob:
`estimators/estimator_v25.py@195373a110215256b759d7c172ba8c923c62e5cc`.

R224/R226 normalized V25 mini-100 parent:
- 100 networks;
- failures 0;
- exact deterministic FLOPs/network `C_H=806303721965`;
- `C_H/B=0.36666448157347986`;
- mean raw final MSE `2.228303490170447e-8`;
- official adjusted score `8.170397440117226e-9`.

Canonical V25 is never edited.

## 3. Mathematical family

Let `m_r(W)` be the complete deterministic V25 prediction with only the nested oldest
source rank changed to `R_OLD2=r`; all other V25 arithmetic and constants are identical.

Production resolutions are frozen:
- high/shipped: `r_H=224`;
- low: `r_L=192`.

Hypothesis: the leading deterministic compression bias of the nested-old source family
has expansion

`m_r = m_infinity + a/r^2 + O(r^-4)`.

The exponent 2 is fixed before any measurement. It is motivated only by squared
orthogonal-projection residual energy; it is not fitted to benchmark error.

The Richardson estimate is

`m_DRRE = m_H + gamma (m_H - m_L)`,

where

`gamma = r_L^2 / (r_H^2-r_L^2)
        = 192^2/(224^2-192^2)
        = 36/13
        = 2.769230769230769...`.

No target, per-network score, output residual or exact-small truth chooses `gamma`.

If the assumed leading-order law has the wrong sign/order, the exact-small gate must
reject the family. There is no coefficient sweep or rescue.

## 4. Production FLOP upper bound

Competition budget:
`B=2^41=2199023255552`.

The R224 parent has an identical measured FLOP count on every one of 100 networks:
`C_H=806303721965`.

The low-rank pass performs the same V25 operation classes with `R_OLD2=192<224`;
every rank-dependent matrix dimension is weakly smaller. Conservatively charge it the
entire high-pass cost anyway:

`C_L <= C_H`.

Output combination for all `16*1024` layer/neuron values is charged as one subtraction,
one scalar multiplication and one addition:

`C_combine = 3*16*1024 = 49152`.

Frozen all-in upper:

`C_DRRE <= 2*C_H + 49152 = 1612607493082`.

Thus

`C_DRRE/B <= 0.7333289854987015 < 1`.

Against the same V25 parent, raw-MSE break-even for adjusted score is

`rho_break = C_H/C_DRRE = 0.49999998476008567`.

The small falsifier uses a stricter admission gate:

`rho_small <= 0.45`.

At equality the projected adjusted-score ratio is about 0.90, leaving ~10% margin.
If the small exact gate misses 0.45, a mini-100 is forbidden regardless of any other
diagnostic.

This is a complete two-pass estimator bound; no assumption of future pass sharing is
credited.

## 5. Exact-small target-free falsifier

No benchmark dataset, public target, scorer, holdout or submission is used.

### Fixtures

Four deterministic zero-bias ReLU MLPs:
- width `n=9`;
- depth `L=10`;
- Gaussian input `X~N(0,I_9)`;
- network seeds `232900,232901,232902,232903`;
- float32 V25 candidate arithmetic;
- float64 verifier arithmetic.

The first weight matrix has nonzero entries only in its first two input rows, so the
network depends exactly on `(X_0,X_1)`. All nine hidden/output coordinates are active.
Later weights are dense He-normal `9x9`.

This gives an exact 2-D Gaussian verifier without changing V25's square-width interface.

### Homologous ranks

For the small run:
- `R_OLD=8`;
- `R_OLD2,H=7`;
- `R_OLD2,L=6`;
- `AGE_OLD=4`;
- `AGE_OLD2=7`;
- all other V25 constants unchanged.

The ratio `r_H/r_L=7/6=224/192`, so the same frozen `gamma=36/13` applies exactly.

Depth 10 ensures the nested oldest-source path is exercised before the final layer.

### Mandatory ordering

For each fixture:
1. verify the pinned V25 git blob;
2. generate weights;
3. run high-rank V25;
4. run low-rank V25;
5. form/freeze DRRE prediction and hashes;
6. deterministic replay high/low/DRRE;
7. only then construct exact Gaussian truth by angular-sector integration;
8. compare all three predictions to exact truth.

The exact reference must never enter candidate construction.

### Exact reference

Because only two Gaussian input coordinates are active, positive homogeneity gives
`F(R q)=R F(q)` with Rayleigh `R` and uniform angle `q`.

The verifier recursively partitions `[0,2pi)` at every exact preactivation zero.
Within one sector the network is linear in `q=(cos theta,sin theta)`.
It analytically integrates the final sector coefficients and multiplies by

`E[R]=sqrt(pi/2)`.

No Monte Carlo, numerical quadrature, target fit or benchmark value is used.

A hard verifier cap of 200000 sectors is frozen; exceeding it is an integrity failure,
not a reason to change the fixture.

## 6. Frozen gates

Integrity, all mandatory:
1. exact V25 source blob matches;
2. candidate/replay finite;
3. bitwise replay exact for high, low and DRRE arrays;
4. exact verifier finite;
5. final exact sector count <=200000;
6. high and low predictions are non-identical on every fixture;
7. no benchmark/public/public-mini/scorer/holdout/full/submission access.

Scientific, all mandatory:
8. pooled `MSE_DRRE/MSE_high <=0.45`;
9. DRRE beats high-rank V25 on at least 3/4 fixtures;
10. worst per-fixture `MSE_DRRE/MSE_high <=0.80`.

Cost:
11. production bound exactly reconciles to `1612607493082`;
12. `C_DRRE/B <1`;
13. small pooled ratio is below the production adjusted-score break-even with the
    stricter 0.45 margin.

All pass:
**R232_SMALL_GO_DRRE**.

Any failed/unevaluable gate:
**R232_TERMINAL_NO_GO_DRRE**.

No exponent/rank/seed/depth change, weighting, clipping, target fit, rescue or second
small run.

## 7. Authorization after falsifier

The frozen exact-small falsifier is the only run authorized initially, on a confirmed
free standard `ubuntu-24.04` GitHub-hosted runner for this public repository.

Only `R232_SMALL_GO_DRRE` may authorize one same-panel mini-100 candidate evaluation.
Even then:
- exactly one mini-100;
- parent is existing normalized V25 (no parent rerun);
- preserve all 100 candidate rows/failures/measured FLOPs;
- official per-network adjusted-score formula;
- no holdout/submission/paid runner;
- no canonical V25 mutation.

A small NO-GO terminates R232 before candidate creation.
