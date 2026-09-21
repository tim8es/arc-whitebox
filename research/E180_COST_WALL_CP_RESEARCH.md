# E180 COST-WALL RESEARCH — rank-3n symmetric-CP carrier for inherited K3

Date: 2026-09-21  
Branch: `research/e180-cost-wall-cp-20260921`  
Parent research commit: E177 `e1536d36a5e2d641ab3596892847e2fcf41e83ab`  
Status: **DESK RESEARCH ONLY — NO CODE/EXPERIMENT RUN, NO BASELINE/LEDGER MUTATION**

## 0. Scope and decision

E180 asks one question only: after E177 showed that deleting the entire V29 old-source
tier still leaves about `153 u = 0.1494 B`, what single change of representation could
plausibly preserve V29-class K3 accuracy while crossing the hard `0.135 B` cost cap?

Exactly one hypothesis is retained:

> **H180 — replace the per-source inherited K3 history (including the dense young A/P
> stack) by one target-free symmetric CP carrier of fixed rank `R = 3n = 3072`,
> reprojected after each ReLU; obtain the required D3/D21 slices directly from that
> aggregate carrier.**

This is not another old-tier compression. It removes the source-age representation itself.
It is also not E176: no AGO gauge, no gain-only covariance closure, and no E176 code or
scientific conclusion is reused.

The hypothesis is **admissible but unproven**. Public evidence establishes that rank-`3n`
CP can carry inherited third-cumulant signal at this shape, but does **not** establish
V29-level final MSE. That is the point of the future owner-run gate below.

## 1. Frozen numbers inherited from E177 / public V29

Budget:

`B = 2^41 = 2,199,023,255,552 FLOPs`.

One F86 unit is:

`u = 2 n^3 = 2^31 = 2,147,483,648 FLOPs`

for `n = 1024`, so `B = 1024 u`.

Hard cap:

`0.135 B = 138.24 u = 296,868,139,499.52 FLOPs`.

Pinned public V29 F86 anatomy (steady-state total about `260.1u`):

| family | units |
|---|---:|
| young K3 transport + hub | 115.6 |
| old K3 | 106.8 |
| K3 thin / elementwise | 24.8 |
| covariance | 7.1 |
| closure + birth | 5.7 |

Deleting the whole old tier leaves about:

`C_no-old = 153.0u = 0.1494140625 B`.

Therefore the **hard lower bound on the saving E180 must create outside the old tier** is:

`Delta_C_min = 153.0 - 138.24 = 14.76u = 31,696,858,644.48 FLOPs`.

Any proposal that cannot remove at least `14.76u` from the non-old path is a cost NO-GO
without an accuracy experiment.

## 2. Why the obvious alternatives are excluded

The public 504aldo findings already measured the nearest variants.

- **Compress the young source tier in the same shared-basis form:** measured age-1/2/3
  sources need very high rank. In F66/F72, young sources are explicitly the non-low-rank
  regime; at age 3, rank 384 incurs about +8.4% raw in the lean ladder, and at age 2
  even rank 512 costs about +8.3%. This does not supply the required cost cut safely.
- **Drop sources / window history:** F66 reports every source important; even dropping
  late cheap births causes multi-x MSE damage.
- **Symmetric-tensor fast contraction as an exact V29 refactor:** F67 closes this by
  inspection because V29's dominant operations are non-symmetric A/P transports and
  asymmetric D21 contractions, not one dense symmetric order-3 contraction.
- **Another old-source tier:** E177/F86 already proves the zero-cost-old limit is still
  above cap.
- **E176 AGO/gain-only closure:** explicitly out of scope and scientifically a different
  estimator family.

Thus a viable component has to change the *carrier of inherited K3 information*, not add
one more age/rank threshold to the existing source stack.

## 3. Official equations that make CP a legitimate carrier

The ARC paper (Wu et al., arXiv:2605.05179, Eq. 15 / S.4.3) factorizes a symmetric
third-order tensor as:

`T[i1,i2,i3] = (1/6) * sum_{sigma in S3} sum_{j=1..J}
A[i_sigma(1),j] B[i_sigma(2),j] C[i_sigma(3),j]`, with `J = O(n)`.

The pinned official implementation expresses the same object as `FactoredTensor`.
Its `contract_W` maps every factor through the linear layer:

`(A, B, C) -> (W A, W B, W C)`.

The implementation also computes repeated-index slices from the factors and has a
`from_dstensor` bridge for the `(3)` and `(2,1)` slices. So an aggregate factored
carrier is not foreign to the official mathematics; it is the native K=3 representation.

H180 specializes the carrier to a **symmetric CP/Waring form**:

`T_inh ~= sum_{q=1..R} lambda_q * u_q tensor u_q tensor u_q`, with `R = 3n`.

Because a linear MLP layer applies the same `W` on each tensor index,

`u_q -> W u_q`

preserves this symmetric CP form exactly through the linear step. The repeated slices
needed by the K3 closure are available without an `n^3` tensor:

`D3[i] = sum_q lambda_q * u[i,q]^3`

`D21[i,c] = sum_q lambda_q * u[i,q]^2 * u[c,q]`

(up to the official slice-normalization convention, which the future implementation must
match exactly).

The approximation is only in the **post-ReLU reprojection back to fixed rank R**. No
target/ground-truth quantity is permitted in that projection.

## 4. Public implementation evidence for the one hypothesis

A separate public Phase-2 write-up by Jigon Yoo / yujigon describes
`estimator_v6.py`, a zero-fitted-constant, zero-sampling inherited-third-cumulant CP
channel.

Relevant published measurements:

- a weight-only tensor-norm CP construction at **rank 3072 = 3n** cleared its
  preregistered skew-correlation gate: `corr = 0.7398 > 0.70`;
- the exact one-source-age construction in that work reached only `0.6299` and failed
  the same gate;
- the shipped point was rank `4608 = 4.5n`, selected by its own 10% compute ceiling:
  `4608 -> 9.8894% B`, while `4704 -> 10.0093% B`;
- the published estimator used zero fitted constants and zero sampling;
- on its own (much cheaper and less accurate) closure family, v6's final MSE was about
  `1.13e-6` on the preregistered 32-network corpus and `1.066e-6` on the official
  public split.

The last number is **not** evidence that CP alone has V29 accuracy. The useful evidence
for E180 is narrower: an inherited joint K3 signal can be carried at rank `O(n)`
without source-age history, and `3n` is a publicly measured nontrivial rank point.

The forum PDF says the packaged bundle contains `estimator_v6.py`; the forum surface
audited in E180 exposes the write-up, not an independently pinned Git blob for that file.
Therefore E180 does not claim line-by-line provenance for yujigon's implementation.
The future owner must either recover that public bundle or derive the target-free
weight-only projection independently and document equivalence before using it.

## 5. Cost feasibility of R = 3n

The cost model below is deliberately conservative and keeps all non-young F86 groups
(`24.8 + 7.1 + 5.7 = 37.6u`) even though a clean CP port may make some thin/source
work unnecessary.

For a symmetric CP matrix `U` of shape `n x R` with `R = rho*n`:

1. one linear transport `W @ U` costs classically about `rho*u`;
2. a full D21 extraction can be written as
   `(U*U) @ U.T` (with column weights folded in), also about `rho*u`;
3. D3 and elementwise scaling are lower-order relative to `u`.

For depth 16, inherited K3 is transported across at most 15 later layers. V29's exact
final-layer trim does not require D21 at the final layer, so plan for 15 transports and
14 full D21 extractions:

`C_CP_core(rho) ~= (15 + 14) * rho * u = 29*rho*u`.

At the frozen public rank `rho = 3`:

`C_CP_core(3) ~= 87u`.

Keeping the conservative fixed remainder:

`C_plan_before_reprojection ~= 37.6u + 87u = 124.6u = 0.1216796875 B`.

That leaves only:

`138.24u - 124.6u = 13.64u`

or about `29.29e9 FLOPs` for **all** reprojection, construction, normalization,
bookkeeping and integration overhead before the hard cap is hit.

This yields a useful rank ceiling under the same classical accounting:

`37.6 + 29*rho <= 138.24`

so

`rho <= 3.4703`.

Therefore the public `3n` point is admissible; the public `4.5n` point is not. At
`4.5n`, the same full-D21 carrier would already be roughly:

`37.6 + 29*4.5 = 168.1u ~= 0.1642 B`

before reprojection overhead.

Important accounting note: V29 explicitly uses Strassen-Winograd for several dense
families, so these classical counts are a **planning envelope, not a metered receipt**.
The future owner must use flopscope for the actual decision. The hard lower-bound result
from Section 1 (`>=14.76u` saving required) is independent of this implementation model.

## 6. Why this is the single retained cost/accuracy hypothesis

H180 is the only candidate retained because it attacks the exact block E177 says must
change: the dense young K3 source machinery (`115.6u`) and, simultaneously, the need
for a separate old-source history.

It also has a mechanistic accuracy argument that the cheaper alternatives lack:

- it keeps a joint inherited third-cumulant object rather than only marginal skew;
- it can reconstruct D21, the slice public V29 ablations identify as the high-leverage
  path to final-mean accuracy;
- rank `3n` has independent public evidence of carrying accumulated skew better than
  a source-age construction in another target-free closure;
- the official K=3 equations already support factorized third-cumulant transport.

The central risk is equally clear: V29 operates near `2e-8`, roughly two orders of
magnitude below the public CP estimator's own closure error. A rank that is adequate for
marginal skew correlation may still destroy the small D21 remainder V29 needs. E180
therefore assigns **no scientific GO** from desk evidence.

## 7. Frozen protocol sketch for a future owner-run

This is a sketch only. E180 does not authorize a run.

### Candidate

One candidate only: `R = 3072` symmetric inherited-K3 CP carrier.

- Start from the clean V29-compatible line selected by the owner.
- Remove the per-source inherited K3 A/P age history from the candidate path.
- Preserve V29 covariance equations, ReLU Wick/Hermite coefficients, K4-regeneration
  logic, mean formula, and final-layer trim.
- Merge each newborn K3 contribution into the aggregate inherited tensor, then perform
  one deterministic target-free rank-`3072` reprojection.
- No rank sweep, no age gate, no second CP rank, no AGO, no coefficient fitting, no
  reference-informed projection, no post-result rescue.
- Projection inputs may use estimator state and weights only.
- Parent and candidate must use identical weights/fixtures and separate reference seed(s).

### Pre-run source/protocol freeze

Before any scientific result exists, commit:

1. exact source ancestry and pinned dependency versions;
2. exact CP projection equations and normalization conventions;
3. a proof/check that D3/D21 extracted from an uncompressed CP tensor match the
   official `FactoredTensor` slice convention;
4. an all-in symbolic FLOP ledger with named namespaces;
5. the rank `R = 3072` and all gates below.

### Cheap structural gate before ground truth

On the pinned fixture, freeze parent V29 D21/D3 vectors before exposing the candidate to
any reference targets.

Required structural condition:

`RMS(D21_CP - D21_parent) / RMS(D21_parent) <= 0.015`

over the non-final layers, with finite vectors and deterministic replay.

The `1.5%` threshold is taken from the public F72 observation that about 1.5% D21 RMS
confinement error corresponded to about `7e-10` added MSE on that chain. It is a
screening threshold, not a theorem.

If this gate fails, stop: **NO-GO; do not buy a ground-truth run.**

### Cost gate

Meter the complete candidate, including CP birth/reprojection, transport, D21 extraction,
normalization, covariance/K4 paths, setup charged by the benchmark, and any fallback.

Required:

`C_candidate / B <= 0.135`.

Additionally, the measured implementation must demonstrate at least the E177-required
non-old saving:

`C_no-old-parent - C_candidate >= 14.76u`.

If either fails: **terminal COST NO-GO**.

### Accuracy gate

Use one pinned target-free public/local-mini evaluation, not a submission/leaderboard
run. Retain immutable parent/candidate/reference vectors and paired per-MLP final MSE.

Define:

`r = mean(MSE_candidate) / mean(MSE_parent_V29)`.

**E180 GO iff all of the following are true:**

1. source/firewall/replay checks pass;
2. D21 structural RMS ratio `<= 0.015`;
3. all-in `C/B <= 0.135`;
4. non-old saving `>= 14.76u`;
5. `r <= 1.02`; and
6. the one-sided 95% upper confidence bound for the paired relative degradation is
   also `<= +2%`.

Anything else is **E180 NO-GO**. No rank increase, alternate projection, source-age
hybrid, or AGO rescue is authorized by the same run.

For the broader E177 frontier, record separately whether the candidate also reaches
`mean raw final MSE < 2.0e-8`; that is a stronger frontier-readiness condition, not a
license to weaken the E180 cost/accuracy gate.

## 8. Sources

### Local ancestry

- `research/E177_PRIMARY_SOURCE_AUDIT.md`, commit
  `e1536d36a5e2d641ab3596892847e2fcf41e83ab`.
- E176 was read only to enforce separation; it is not scientific ancestry for H180.

### Official ARC equations / implementation

- Wu, Lecomte, Winer, Robinson, Hilton, Christiano,
  *Estimating the expected output of wide random MLPs more efficiently than sampling*,
  arXiv:2605.05179. Eq. 15 / S.4.3 gives the K=3 factorization.
  https://arxiv.org/abs/2605.05179
- ARC reference implementation:
  `alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`
  - `src/mlp_kprop/factor_k3.py`
  - audited methods: `FactoredTensor.contract_W`,
    `FactoredTensor.get_dslice`, `FactoredTensor.from_dstensor`.

### Public V29 implementation and cost audit

- `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
  - `estimators/estimator_v29.py`
  - `docs/findings_log.md` (especially F66, F67, F72, F86, F88)
- Public write-up:
  https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

### Independent public CP evidence

- Jigon Yoo / yujigon, Phase-2 write-up for submission #330001,
  *Zero fitted constants, measured: what the 64 calibration numbers in a ReLU-MLP mean
  propagator are actually absorbing*, 2026-09-06.
  Forum:
  https://discourse.aicrowd.com/t/phase-2-write-up-zero-fitted-constants-measured-what-the-64-calibration-numbers-in-a-relu-mlp-mean-propagator-are-actually-absorbing-submission-330001/18216
  PDF:
  https://discourse.aicrowd.com/uploads/short-url/1d5TivH5DHlI7hYMiOQ9s4dcds9.pdf
  Relevant sections: 5–6, especially rank `3n` and `4.5n` inherited-CP measurements.

## 9. E180 conclusion

**Research decision: PROTOCOL-WORTHY, NOT SCIENTIFIC GO.**

The cost wall cannot be closed by old-tier work alone; at least `14.76u` must disappear
from the non-old path. A fixed rank-`3n` aggregate symmetric CP carrier is the one
admissible mechanism found in this audit that changes that path at the correct scale,
has an official mathematical home in factorized K3, and has independent public evidence
for inherited-cumulant transport at rank `O(n)`.

The estimate is tight enough to be falsifiable: with the conservative V29 remainder,
rank `3n` has only `13.64u` of classical-accounting headroom for reprojection and
integration. If the actual metered implementation cannot stay under `0.135B`, or if
its D21 error exceeds 1.5%, the idea should die before a costly accuracy run.
