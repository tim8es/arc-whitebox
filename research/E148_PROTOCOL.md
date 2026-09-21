# E148 protocol — one target-free GSTT-K3 falsifier

Idempotency key: `ARC-E148-GLOBAL-SEED-TT-K3-20260921`.

Status at freeze:

**PROTOCOL ONLY / ONE FUTURE TARGET-FREE FALSIFIER DEFINED / NO RUN ARMED OR LAUNCHED.**

Branch:

`research/e148-global-seed-tt-k3-20260921`.

Primary-source note:

`research/E148_PRIMARY_SOURCE_NOTE.md`.

Parent:

`research/e147-response-projected-k3-estimator-20260921@daf997a9b1204f7916e9f5b78eba3aa6ff113d49`.

## 1. Hypothesis

**H148 — GSTT-K3.**

A global open-core tensor-train representation of the ordered K3 source seed can replace both the V29 young and old per-source carriers while preserving the V18/V19-class D21 interface accurately enough to justify later production work.

Frozen representation:

[
\hat S_{ijk}
=
\sum_{a=1}^{r}\sum_{b=1}^{r}
U_{ia}G_{ajb}V_{kb},
qquad
\hat K=\operatorname{Sym}(\hat S).
]

Production rank:

[
r=40.
]

Small-width homologous rank:

[
r(n)=\min\left(n,\max\left(4,\left\lceil5n/128\right\rceil\right)\right).
]

No rank sweep, alternate rank, post-result basis change or rescue is allowed.

## 2. Non-overlap firewall

H148 is not:

- E142: no old-tier residual response action;
- E145: no integration into a preserved V29 source carrier;
- H143/E146: no particle/MUB cloud and no residual injection;
- E147: no backward response basis and no `q x q x r` projected K3 action core;
- H140: no rank-4 symmetric-matrix-vector decomposition and no full-tensor SVD recompression;
- H137: no CountSketch contraction patch;
- V21/V24: no source-age shared/nested basis;
- V29 F46: no compression of all three tensor modes;
- V29 F76/F88: no capped CP-column/hub-side merge.

Any implementation that reduces to one of these classes fails ancestry before the scientific run.

## 3. Pinned sources

Public V29:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

V29 estimator blob:

`17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.

Official ARC implementation:

`alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

The falsifier must verify these identities before importing reference algebra.

No benchmark dataset or target is permitted.

## 4. Frozen candidate construction

### 4.1 State

At every non-final layer retain:

- mean/covariance and the low-order V18/V19-style closure state;
- `U in R^(n x r)`, orthonormal;
- `V in R^(n x r)`, orthonormal;
- open core `G in R^(r x n x r)`;
- target-free projection-error certificate scalars;
- only the thin D21-feedback state required by the same closure.

No per-source dense K3 `A/P` stack may survive after a newborn has been inserted into the global core.

A transient newborn factor may exist only during that layer's insertion and must be released before the next linear transport.

### 4.2 Linear/Wick transport

Use exactly:

[
U\leftarrow WU,quad
V\leftarrow WV,quad
G_{ajb}\leftarrow\sum_t W_{jt}G_{atb},
]

with the same coordinatewise Wick factor applied once to each physical mode.

Thin QR canonicalizes `U,V`; the resulting `r x r` factors are absorbed into `G`.

### 4.3 D21/D3 readout

Compute the three ordered-seed orientations:

[
D21_{ic}
=
\frac13(S_{iic}+S_{ici}+S_{cii}).
]

No dense K3 tensor, Khatri--Rao `n x r^2` transport leg or per-source D21 hub may be materialized by the candidate.

Compute `D3_i=S_{iii}`.

These candidate D21/D3 values feed the same frozen nonlinear closure and D21-feedback birth logic.

### 4.4 Newborn insertion

Every K3 birth atom must first be expressed in the public/ARC canonical ordered form with the identity-born middle leg:

[
B_{ijk}=\sum_t A_{it}\delta_{jt}Y_{kt}.
]

For fixed new bases,

[
G^{birth}_{ajb}
=(U^TA)_{aj}(V^TY)_{bj}.
]

If any required birth atom cannot be represented this way without an unbilled dense operation, the falsifier is an immediate NO-GO.

### 4.5 Deterministic basis update

No random seed is used for the compression basis.

At layer `l`, form the newborn outer-factor range sketches from a fixed slice of the already-known next weight matrix, using the same deterministic column ordering for both fixtures.

The sketch width equals the frozen `r(n)`.

Concatenate:

- the old `U` or `V` basis;
- the corresponding newborn factor sketches.

Take a thin SVD/QR, keep exactly `r(n)` columns, and canonicalize every column sign by making its largest-magnitude entry positive, breaking ties by smallest row index.

No oversampling parameter, power-iteration count or alternative sketch is allowed.

The implementation protocol must freeze the exact slice indices before the run arm is created.

## 5. Target-free projection certificate

For orthonormal outer bases:

[
\|\hat S\|_F^2=\sum_j\|G_j\|_F^2.
]

For a basis replacement `U,V -> U',V'`, define

[
M=U'^TU,qquad N=V'^TV.
]

The old-state retained norm is

[
R_{old}^2
=
\sum_j\|M G_j N^T\|_F^2.
]

The old-state projection loss is therefore computable from candidate state only.

For every newborn outer factor, compute exact Frobenius projection residuals from

[
\|(I-UU^T)A\|_F^2
=
\|A\|_F^2-\|U^TA\|_F^2
]

and analogously for `Y`.

Use triangle/submultiplicative bounds on the ordered CP atoms to obtain a per-layer seed residual increment.

Symmetrization is norm-nonexpansive, so

[
\|K-\hat K\|_F
\le
\|S-\hat S\|_F.
]

D21 is an entry-selection operator, hence

[
\|D21(K)-D21(\hat K)\|_F
\le
\|S-\hat S\|_F.
]

The candidate must compute this bound without exact K3/D21 reference access.

A recursively propagated certificate may use only deterministic matrix-norm bounds computed from candidate weights/state. If its denominator becomes non-positive or the bound becomes non-finite, the certificate gate fails.

The exact-small verifier may test containment only after candidate freeze.

## 6. Exactly one falsifier execution

One future workflow execution may contain both frozen fixtures and deterministic replay.

It is still **one scientific run**.

No second run is permitted under H148.

### Fixture A — dense He

- width/input: 32;
- depth: 8 ReLU layers;
- zero bias;
- deterministic He-Gaussian weights;
- network seed: `148032`;
- `r=4`;
- float64 exact-small arithmetic.

### Fixture B — adversarial rotated

- width/input: 16;
- depth: 8;
- zero bias;
- deterministic dense QR rotation / diagonal gain / QR rotation weights;
- network seed: `148016`;
- gains frozen before execution;
- `r=4`;
- float64 exact-small arithmetic.

The adversarial fixture must rotate coordinates every layer so an axis-aligned compression cannot pass accidentally.

No fixture replacement is allowed.

## 7. Candidate-before-reference ordering

Mandatory order inside the single run:

1. verify pinned source commits/blobs;
2. construct both synthetic weight sets;
3. run GSTT-K3 candidate on both fixtures;
4. deterministic replay candidate and freeze:
   - all layer means;
   - U/V/core hashes;
   - D3/D21;
   - projection certificates;
   - operation-class ledger;
5. only then construct the exact-small reference;
6. compare candidate with reference;
7. write one immutable result receipt.

The candidate module must not import the exact-reference module.

The reference must not write into candidate state.

## 8. Exact-small reference

Verifier-only reference:

- same low-order and V18/V19-class nonlinear closure used by the candidate;
- exact ordered K3 source sum with no TT truncation;
- exact symmetrized D3/D21;
- dense K3 materialization is allowed only at 32D/16D for independent cross-checks.

The reference is not a benchmark target and must not use any public MLP/reference mean.

## 9. Frozen scientific gates

All gates must pass on **both** fixtures.

### Integrity

1. finite candidate/reference state;
2. bitwise deterministic candidate replay;
3. pinned source identities exact;
4. no benchmark/public/public-mini/scorer/holdout/full/submission access;
5. no target/reference data enters candidate construction;
6. no forbidden ancestry/mechanism.

### Representation identities

7. open-core linear transport versus dense transport relative error `<=1e-12` before truncation;
8. Wick scaling identity relative error `<=1e-12`;
9. D21 three-orientation readout versus direct `Sym(S)` D21 relative error `<=1e-12` before truncation;
10. D3 readout relative error `<=1e-12` before truncation;
11. every required newborn atom passes the identity-middle canonicalization audit.

### Deep approximation

12. pooled D21 relative RMS error over non-final layers `<=0.010`;
13. no layer D21 relative RMS error `>0.015`;
14. pooled D3 relative RMS error `<=0.010`;
15. define the target-free K3 correction scale
    [
    \Delta\mu_{K3}
    =
    \mu_{exact,K3}-\mu_{same\ closure\ with\ K3\ zeroed}.
    ]
    The final candidate-vs-exact mean RMS must satisfy
    [
    \frac{\|\mu_{cand}-\mu_{exact,K3}\|_2}
         {\|\Delta\mu_{K3}\|_2}
    \le0.10.
    ]
    If the denominator is numerically zero, the fixture fails rather than changing the metric.

The 1% D21 gate is intentionally stricter than the public V29 2.2% rule-of-thumb threshold. It is an admission criterion for attempting to recover the public V18/V19 raw regime, not a prediction of benchmark MSE.

### Certificate

16. candidate-computed absolute D21 bound contains every exact-small layer error;
17. all certificate values finite;
18. candidate certificate construction reads no exact reference;
19. certificate operation class fits inside the frozen 12-unit production reserve.

### Cost

20. executable operation classes reconcile to the frozen production formula;
21. no per-source dense K3 carrier survives between layers;
22. no `n^3` K3 tensor or `n x r^2` transported Khatri--Rao leg is required in production;
23. production upper `<=296,868,139,499` FLOPs.

Any failed or unevaluable gate:

**E148 TERMINAL NO-GO / CLOSE GSTT-K3.**

No rank sweep, sketch-width sweep, alternate basis, power-iteration rescue, seed replacement, layer selection, shrinkage, target fit or second run.

## 10. Frozen production ledger

At `n=1024, depth=16, r=40`:

| class | FLOPs | units |
|---|---:|---:|
| retained low-order/public-style allowance | 81,604,378,624 | 38.0000000000 |
| open-core TT transport | 56,780,390,400 | 26.4404296875 |
| three-orientation D21/D3 | 52,946,534,400 | 24.6551513672 |
| newborn projection/insertion | 2,565,734,400 | 1.1947631836 |
| deterministic basis update | 10,577,510,400 | 4.9255371094 |
| certificate reserve | 25,769,803,776 | 12.0000000000 |
| helper/materialization reserve | 25,769,803,776 | 12.0000000000 |
| **total** | **256,014,155,776** | **119.2158813477** |

[
C/B=0.11642175912857056.
]

Hard cap:

[
296,868,139,499\text{ FLOPs}.
]

Slack:

[
40,853,983,723\text{ FLOPs}.
]

The next rank multiple `r=48` under the same formula is approximately `144.85` units = `0.14145B` and is inadmissible. Rank 40 is therefore budget-derived rather than selected by accuracy.

Any unlisted operation class must fit the helper reserve or the run fails cost reconciliation.

## 11. Run/public authorization

This protocol itself launches **zero** runs.

After a candidate implementation and static ancestry/firewall review, it may arm exactly one target-free exact-small falsifier matching Sections 6--10.

Even if that falsifier GOes:

- no public target;
- no public mini;
- no official scorer;
- no holdout;
- no full suite;
- no submission;
- no 1024x16 physical owner run

is authorized by this protocol.

A GO would only justify a new successor protocol and independent verifier reservation.

## 12. Freeze decision

E148 admits GSTT-K3 for exactly one future target-free falsifier because:

- it removes both V29 young and old per-source transport families;
- it exploits the identity-born middle leg rather than compressing it;
- D21 remains directly readable from the global seed;
- its conservative production upper is `0.11642B < 0.135B`;
- the public ladder contains a pre-age-compression raw regime below `2.13e-8`;
- whether rank 40 can preserve that regime is unknown and is the sole scientific question of the falsifier.

No target-bearing evidence has been used to construct or execute a candidate under E148.
