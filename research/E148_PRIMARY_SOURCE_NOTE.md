# E148 — leader-gap primary-source research: global open-core TT K3

Status: **PRIMARY-SOURCE RESEARCH / NEW ESTIMATOR CLASS ADMITTED FOR ONE TARGET-FREE FALSIFIER / NO IMPLEMENTATION OR RUN.**

Branch: `research/e148-global-seed-tt-k3-20260921`.

Parent: `research/e147-response-projected-k3-estimator-20260921@daf997a9b1204f7916e9f5b78eba3aa6ff113d49`.

E148 is not an E142/E145/H143 rescue. It starts from the published V29 cost wall and asks for a different representation of the complete K3 source sum.

## 1. Primary sources pinned

### Public V29

Repository:

https://github.com/504aldo/whest-p2-cumulant-k3

Pinned commit:

`18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Primary files:

- community write-up:
  https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/community_post.md
- V29 estimator:
  https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v29.py
- V29 namespace ledger:
  https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/audit_v29_ns_d0.log
- claims/evidence:
  https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/claims_evidence.md

Pinned V29 blob in E136: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.

The published ladder gives raw final-layer MSE:

- V18: `2.08e-8`;
- V19: `2.083e-8`;
- V22: `2.12e-8`;
- V24: `2.15e-8`;
- V25/V29 arithmetic: `2.13e-8`.

V26--V29 are cost engineering at fixed estimator arithmetic.

The published steady-state V29 ledger is `260.06` units, with one unit
`2 n^3 = 2^31` FLOPs at `n=1024`:

| family | units |
|---|---:|
| K3 young dense sources | 115.61 |
| K3 old shared-basis tier | 106.83 |
| K3 thin / elementwise | 24.78 |
| covariance | 7.10 |
| birth / closure | 5.71 |
| other | 0.03 |
| total | 260.06 |

The public write-up explicitly states the decisive wall: deleting the whole old tier still leaves about `153` units, `~0.150 B`, and therefore the leaders cannot be explained by old-tier compression alone.

The same write-up gives the structural interface:

- the ReLU update reads K3 through `D3_i = K_iii` and `D21_ic = K_iic`;
- V16b rewrites each source D21 contribution as two dense contractions plus thin terms;
- every source is born from factored hub blocks with an identity-born/shared `P` leg;
- the Khatri--Rao/Hadamard rank explosion is the reason their shared-basis representation cannot remain entirely in factor space;
- a full symmetric Tucker confinement of all three legs was measured bad because the `P` leg is born as the identity.

### Official ARC

Paper:

https://arxiv.org/abs/2605.05179

Official code:

https://github.com/alignment-research-center/mlp_cumulant_propagation

Pinned code commit used by this project:

`93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

Official explanatory posts:

- https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/
- https://www.alignment.org/blog/mechanistic-estimation-for-expectations-of-random-products/

Relevant primary-source facts:

1. ARC's factorized K3 stores a symmetric third cumulant as a symmetrized sum of factored atoms rather than materializing the `n^3` tensor.
2. The factorized representation is preserved through the linear/Wick steps.
3. Non-discrete diagonal slices admit `Theta(n)`-factor representations.
4. ARC describes the general estimator pattern as deduction followed by projection: keep the representation that is useful for the downstream observable rather than every intermediate term.
5. The official code's `FactoredTensor` makes the ordered factor seed explicit before symmetrization.

These facts motivate projecting the **global ordered seed sum**, not separately compressing old source legs.

## 2. Closed paths that E148 does not reopen

### E142 / E145

E142 proved an exact response statistic only for the old-D21 contraction interface.

E145 then proved the integration obstruction:

`V29 non-old floor ~= 153.23 units = 0.14964 B > 0.135 B`.

Therefore E148 may not keep the V29 young-source carrier and merely replace the old tier.

### H143

H143 adds a particle residual to V29 while retaining the V29 K3 carrier. That cannot solve the `0.135 B` leader-gap objective because the host itself is already above the cap.

E148 uses no particle cloud, MUB/Kerdock nodes, empirical moments or output correction.

### Public V29 dead ends

E148 does not use:

- source windowing;
- slice-only/memoryless K3 closure;
- capped CP columns;
- symmetric Tucker compression of all three modes;
- per-source rank ladders;
- lower old-tier shared ranks;
- hub-side source merge;
- adjoint-only final-mean sensitivity;
- old-tier-only response compression.

## 3. Unused representation identity

### 3.1 Ordered seed rather than source list

Write the conceptual symmetric K3 state as

[
K = \operatorname{Sym}(S),
]

where the ordered seed is

[
S_{ijk}
 = \sum_s \sum_t
 A^{(s)}_{it} P^{(s)}_{jt} Y^{(s)}_{kt}
]

plus the corresponding public thin/feed atoms in the same canonical orientation.

Public V29 transports each source's dense `A_s` and `P_s` legs separately and only merges them at D21 contraction time.

E148 instead merges **all source ages immediately** into one low-rank representation of `S`.

### 3.2 Open-core TT / two-mode Tucker form

Freeze rank `r`.

Represent the ordered seed as

[
\hat S_{ijk}
 =
 \sum_{a=1}^{r}\sum_{b=1}^{r}
 U_{ia} G_{ajb} V_{kb},
]

with

- `U in R^(n x r)`;
- `V in R^(n x r)`;
- `G in R^(r x n x r)`.

This is an order-3 tensor train with the middle physical mode left **uncompressed**.

That uncompressed middle mode is the point.

It is not the symmetric Tucker experiment in V29 F46:

- F46 compressed all three neuron modes;
- E148 compresses only the two outer modes and leaves the repeated-index/D21 mode at full width `n`.

It is also not E147:

- E147 stores a response-projected `q x q x r` K3 action core and obtains bases by backward response pullback;
- E148 stores the global ordered source seed with a full physical middle mode `r x n x r`;
- E148 has no backward pass and no downstream response basis.

### 3.3 Exact linear/Wick closure of the representation

For one linear map `W` applied to all three K3 modes:

[
U' = WU,qquad
V' = WV,
]

and

[
G'_{a j b}
 = \sum_t W_{jt}G_{a t b}.
]

Therefore linear K3 transport is closed in the open-core TT representation.

Coordinatewise Wick scaling by `d` is also closed:

[
U_{ia}\leftarrow d_i U_{ia},quad
V_{ib}\leftarrow d_i V_{ib},quad
G_{aib}\leftarrow d_i G_{aib}.
]

No source-age list is needed for transport.

### 3.4 Exact D21/D3 extraction from an exact ordered seed TT

For a symmetric tensor defined by `K = Sym(S)`,

[
D21_{ic}
 = \frac13
   \left(
      S_{iic}+S_{ici}+S_{cii}
   \right).
]

The three terms are:

[
S_{iic}
 = \sum_b
   \left(\sum_a U_{ia}G_{aib}\right)V_{cb},
]

[
S_{cii}
 = \sum_a
   U_{ca}
   \left(\sum_b G_{aib}V_{ib}\right),
]

and

[
S_{ici}
 = \sum_{a,b} U_{ia}G_{acb}V_{ib}.
]

The first and third orientations reduce to ordinary `n x r` by `r x n` products after `O(n r^2)` contractions.

Only `S_ici` pays the `O(n^2 r^2)` open-core contraction.

Thus the V29 Khatri--Rao wall is avoided: E148 never forms a dense Hadamard leg and never expands an `r^2` Khatri--Rao basis into an `n x r^2` transported factor.

The diagonal is

[
D3_i=S_{iii},
]

so it is obtained from the same core in `O(n r^2)`.

### 3.5 Cheap newborn insertion is specific to the public/ARC factorization

The public/ARC K3 birth atoms have a canonical identity-born middle leg.

For a newborn ordered atom

[
B_{ijk}
 = \sum_t A_{it}\,\delta_{jt}\,Y_{kt},
]

its projection into fixed outer bases is

[
G^{birth}_{a j b}
 =
 (U^T A)_{a j}
 (V^T Y)_{b j}.
]

There is no `n^3` tensor and no `n^2 r^2` birth contraction.

The two outer projections cost `O(n^2 r)`; core assembly costs `O(n r^2)`.

This identity is the concrete opening not used by V29: keep the identity-born mode as the **physical TT core index** instead of compressing/reforming it as a source leg.

Any public birth term that cannot be put in this canonical identity-middle form is a protocol failure unless it is explicitly billed in the retained low-order allowance. The falsifier must audit this before scoring accuracy.

## 4. Rank is budget-derived, not tuned

Production shape:

- `n=1024`;
- depth `16`;
- 15 non-final K3 transitions.

Competition budget:

[
B=2^{41}=2,199,023,255,552.
]

Project cap:

[
\lfloor0.135B\rfloor
=296,868,139,499.
]

One V29 unit is `2 n^3 = 2,147,483,648` FLOPs.

E148 freezes `r=40`.

This is not an accuracy sweep. Under the complete conservative ledger below:

- `r=40` is below the cap with explicit certificate/helper reserves;
- the next multiple of eight, `r=48`, would be about `144.85` units = `0.14145 B`, already over the cap.

Small-width homologous rank:

[
r(n)=\min\left(n,\max\left(4,\left\lceil\frac{5n}{128}\right\rceil\right)\right).
]

Therefore:

- 16D -> 4;
- 32D -> 4;
- 1024D -> 40.

No rank sweep is allowed.

## 5. Complete pre-code production upper

This is a deliberately conservative estimator-level upper, not a module-only number.

### A. Retained low-order/public-style arithmetic

Retain the same conservative non-source allowance used by E147:

[
38.00\text{ units}
=81,604,378,624\text{ FLOPs}.
]

It covers the V29 grouped K3 thin/elementwise, covariance, birth/closure and other classes even where E148 may later remove some of them.

### B. Open-core TT transport

Per transition bill

[
2n^2r^2+4n^2r+4nr^3.
]

Across 15 transitions at `r=40`:

[
56,780,390,400
=26.4404296875\text{ units}.
]

### C. Full symmetric D21/D3 readout from the ordered seed

Bill all three orientations:

[
2n^2r^2+4n^2r+4nr^2
]

per transition.

Across 15:

[
52,946,534,400
=24.6551513671875\text{ units}.
]

### D. Newborn projection/insertion

Bill

[
4n^2r+2nr^2
]

per transition.

Across 15:

[
2,565,734,400
=1.19476318359375\text{ units}.
]

### E. Deterministic global-basis update

The frozen falsifier/production design uses a weight-slice range sketch of the newborn outer factors, followed by thin QR/SVD with canonical signs.

Conservative bill:

[
4n^2r+8nr^2+8nr^3
]

per transition.

Across 15:

[
10,577,510,400
=4.925537109375\text{ units}.
]

### F. Projection-error certificate reserve

Freeze:

[
12\text{ units}
=25,769,803,776\text{ FLOPs}.
]

This must cover:

- exact outer-factor residual norms;
- old-core reprojection residual contractions;
- D21 norm/certificate reductions;
- floating-point envelopes.

Exceeding the reserve is a cost failure.

### G. Helpers/materialization/accounting reserve

Freeze another:

[
12\text{ units}
=25,769,803,776\text{ FLOPs}.
]

This covers finite checks, clears/copies, sign canonicalization, output assembly, bookkeeping-visible array work and any otherwise unnamed operation class.

### Total

[
C_{E148}^{upper}
=256,014,155,776\text{ FLOPs}
=119.21588134765625\text{ units}
=0.11642175912857056B.
]

Slack to the `0.135B` cap:

[
40,853,983,723\text{ FLOPs}
=19.02411865234375\text{ units}.
]

Pre-code cost admission: **PASS**.

This is the first reason to test the class: unlike old-tier-only compression, its cost removes both the young and old per-source `n^3` families.

## 6. Why this class could beat raw 2.13e-8

This is an admission argument, not a final-MSE claim.

The public ladder already contains a lower-raw arithmetic point before source-age compression:

- V19 raw: `2.083e-8`;
- V25/V29 arithmetic raw: `2.13e-8`.

The difference is about `2.21%` of V29 raw.

V29 reports that every source matters and that the old shared/nested compression is an accuracy/cost tradeoff. E148's purpose is not to invent another correction; it is to represent the **global V18/V19-class K3 source sum** at a cost low enough to avoid V22/V24 age truncation entirely.

If a fixed-rank global open-core TT preserves the D21 interface closely enough across depth, then the public ladder shows that a sub-`2.13e-8` arithmetic regime already exists.

That does not prove the TT rank is sufficient. The one exact-small falsifier is specifically designed to kill this possibility before any target-bearing work.

## 7. Target-free certificate identity

Let `S` be the exact ordered seed and `Shat` the open-core approximation.

Because symmetrization is an orthogonal averaging operator,

[
\|\operatorname{Sym}(S-Shat)\|_F
\le \|S-Shat\|_F.
]

Because D21 selects entries of the symmetric tensor,

[
\|D21(K)-D21(Khat)\|_F
\le \|K-Khat\|_F
\le \|S-Shat\|_F.
]

For orthonormal `U,V` and core `G`,

[
\|Shat\|_F^2=\sum_j\|G_j\|_F^2.
]

When changing outer bases to `U',V'`, let

[
M=U'^T U,qquad N=V'^T V.
]

The exactly retained old-core norm is

[
\sum_j\|M G_j N^T\|_F^2,
]

so the old-state outer-projection loss is computable from the TT cores without materializing an `n^3` tensor.

For a newborn CP atom, the outer projection residual is bounded from the exact factor norms

[
\|(I-UU^T)A\|_F,qquad
\|(I-VV^T)Y\|_F,
]

which are computable from `||A||_F^2-||U^T A||_F^2` and the analogous expression for `Y`.

The protocol uses these as a target-free per-projection residual certificate. It does **not** claim in advance that the recursively propagated bound will be tight enough; looseness is a falsifier failure.

## 8. Research decision

Admit exactly one new class:

**GSTT-K3 — Global Seed Tensor-Train K3, rank 40 at production shape.**

The concrete unused identity is:

> merge all source ages in the ordered factor seed, leave the identity-born/repeated-index mode physically uncompressed, transport one `r x n x r` open core, and recover the symmetric D21 through the three seed orientations.

This directly attacks the V29 young+old `n^3` families rather than compressing only the old tier.

No claim is made that rank 40 is accurate enough.

No implementation, workflow, scientific run, public target, public mini, scorer, holdout, full suite, submission, canonical mutation or ledger mutation is part of E148 research.
