# E137 primary-source note — clean improvement paths from the MIT-licensed V25/V29 baseline

Status: **RESEARCH NOTE / NO E137 ESTIMATOR CODE / NO E137 RUN**  
Protocol: `research/E137_PROTOCOL.md`  
Protocol commit: `77c13ded84bb8b5e6bd4a092cd2021b3732a21fe`

## 0. Executive finding

The public 504aldo Phase-2 release is a useful **verified baseline family**, not just an idea dump.

- **V25** is the designated arithmetic/method baseline: factorized K=3 source propagation,
  memoryless K4 regeneration, rank-16 D21 feedback, final-layer trim, old-source
  shared/nested bases, and adaptive lambda.
- **V29** changes the cost implementation, not the arithmetic: the public author reports
  the same raw MSE to four digits while reducing metered compute with Strassen-Winograd
  batching and buffer engineering.
- The public release itself says the V25/V29 closure has reached its raw floor:
  approximately `2.07e-8` on the author's 8-dump float64 reference chain
  (about `1.94e-8` after their stated LB scale conversion), while V29's public LB
  was `2.13e-8` raw at `C/B=0.2526`.
- The major remaining cost is not the Wick/ReLU closure. It is old K3 source machinery:
  V29's own ledger attributes `106.8` of `260.1` steady-state units to the old tier.
- The public dead-end record closes ordinary rank pruning, source dropping, slice-only
  memoryless closure, hub-column truncation, Tucker confinement, adjoint reformulations,
  per-source K4 resurrection, sampling sidecars, precision changes, and pricing polish.

**E137 therefore does not propose another source-age closure or another estimator.**

The one admitted improvement hypothesis is:

> **Old-tier CountSketch contraction patch:** keep the complete V25/V29 source state,
> age gates, ranks, lambda law, K3/K4 arithmetic and dense old-leg formation unchanged,
> but replace only the expensive old-tier factor-space products
> `LA FA^T` and `LP FP^T` by target-free oblivious randomized matrix multiplication
> using a fixed CountSketch on the hub/column axis.

This is a V25/V29 delta, not a standalone estimator. It attacks one measured cost family
without changing the baseline closure.

---

## 1. Primary-source provenance

### 1.1 Public baseline repository — PUBLIC VERIFIED

Repository:

`https://github.com/504aldo/whest-p2-cumulant-k3`

Reviewed public main head:

`18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

The repository is MIT-licensed.

Important reviewed blobs:

| public path | git blob |
|---|---|
| `LICENSE` | `2c843327a87b547245b566f02391295ba71ad26a` |
| `docs/community_post.md` | `aa06c6d24c0bf9f6cb9cfd326c4862d6a4ee3a73` |
| `docs/ablation_table.md` | `ae4ae52ead96feb32cd996cacd9bae8e546e69e4` |
| `docs/findings_log.md` | `09cf41e8826052ceb83109115cae688c03baaaca` |
| `docs/derivation_code_map.md` | `2b7f1e7df1ddf08a3925bbe883ebe0db14942eff` |
| `estimators/estimator_v16b.py` | `e5e2e2dcd1be1b402ee3384147c25d221ace2315` |
| `estimators/estimator_v17.py` | `9c60c5a0bd92729f27bde23eeb619944e71beabe` |
| `estimators/estimator_v18.py` | `71b2bbfd64de3f32a947ea8ee148744d1721a935` |
| `estimators/estimator_v22.py` | `e15f6445acbfb4dd4602b933cd295fee6ba75ed6` |
| `estimators/estimator_v24.py` | `571a2dc49a9f5fb58d48a352ef68aeae0cad6323` |
| `estimators/estimator_v25.py` | `195373a110215256b759d7c172ba8c923c62e5cc` |
| `estimators/estimator_v29.py` | `17df1a073a24f96c4705b04bcf61ef60fa06dd0c` |

### 1.2 Author's AIcrowd disclosure — PUBLIC VERIFIED

Primary forum post:

`https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218`

The post reports the version ladder on one grader, explains which steps affect accuracy
versus cost, gives the V29 family ledger, and lists 25 measured dead ends.

### 1.3 ARC cumulant-propagation reference — PUBLIC VERIFIED

Repository:

`https://github.com/alignment-research-center/mlp_cumulant_propagation`

Reviewed blobs:

- `README.md`: `0665357e37164f1896392fbbd4431a5a4e692871`
- `LICENSE`: `8da0189712dc3d815a88629cac1137c95ef87ed1`

This is the code repository for the paper
"Estimating the expected output of wide random MLPs more efficiently than sampling"
(arXiv:2605.05179). It contains the factorized K3/K4 and Wick/Hermite machinery from
which the public V16b/V25 lineage was derived.

---

## 2. Verified version ladder: what is already closed

All numbers in this section are **PUBLIC VERIFIED** from the public repository/forum unless
explicitly marked otherwise.

| version | exact/public mechanism | raw / C/B on public LB | E137 interpretation |
|---|---|---:|---|
| V16b #329389 | factorized K3; exact algebraic reduction from ~7 to 4 dense units/source-layer | `4.46e-8 / 0.4986` | K3 source content is useful; basic algebraic restructure is already exhausted |
| V17 #329480 | memoryless K4 regeneration: `G_off≈lambda_l C_off`, exact K4 diagonal retained, K4→K3 feed retained | `2.26e-8 / 0.4921` | largest post-V16 accuracy gain; simple per-source K4 resurrection is not needed |
| V18 #329531 | rank-16 D21 feedback into newborn source factors via thin legs | `2.08e-8 / 0.5093` | last large accuracy step in the shipped ladder |
| V19 #329571 | exact final-layer trim: mean needs var diagonal, D3 and K4 diagonal, not full D21/C sandwich | `2.083e-8 / 0.4777` | exact cost cut, no arithmetic loss |
| V22 #329584 | old sources after four transports share rank-384 basis; pre-activation lambda refit in this lineage | `2.12e-8 / 0.3834` | source-age row-space compression works, but only above a sharp rank floor |
| V24 #329633 | oldest sources after seven transports move to rank-224 sub-basis nested inside rank-384 basis | `2.15e-8 / 0.3667` | second cost tier is real; lower ranks hit an accuracy cliff |
| V25 #329644 | adaptive per-MLP lambda from online K4-diagonal/variance ratio | `2.13e-8 / 0.3667` | designated **method baseline**; lambda adaptation is a small score gain, not the raw bottleneck |
| V29 #330093 | same V25 arithmetic, Strassen-Winograd/batched-family and buffer cost engineering | `2.13e-8 / 0.2526` | designated **live cost baseline**; raw parity means any E137 improvement should be measured as a delta from this arithmetic |

### 2.1 V16b — exact 7→4 source-layer restructure

The public derivation rewrites each source's D21 contribution so the M leg need not be
formed/transferred as another dense object. The four D21 pieces reduce to two dense
contractions with right factors A and P, plus thin work:

`D21 = sum_b LA_b A_b^T + LP_b P_b^T + thin_terms`.

The author reports parity with the reference up to float32 rounding and a cost reduction
from about `0.833 B` to about `0.50 B` at identical MSE.

**Closed:** another rearrangement that merely reproduces these same four contractions is
not a new accuracy mechanism.

### 2.2 V17 — K4 memoryless regeneration

The public augmented-K3 probe found

`G_off ≈ lambda_l C_off`

with reported per-layer `R^2≈0.66..0.97`, rising with depth.

Important negative/positive details:

- exact/transported K4 diagonal must remain explicit;
- regenerating the diagonal from `lambda C` was about 15x worse;
- K4→K3 feed carries the gain;
- K4 use-side terms without the feed were harmful;
- adding eight more live low-order modes to the oracle projection changed final MSE only
  from about `2.230e-8` to `2.205e-8`.

**Closed:** simply adding a few extra fitted low-order K4 modes is not a plausible major
raw-accuracy breakthrough.

### 2.3 V18 — D21 feedback

The only V1.6 feedback block reported as material on the regenerated-K4 base was D21
feedback into the birth factors. Rank 16 was enough for the thin feedback path;
rank 32 later proved score-negative at V25/V29 pricing.

**Closed:** "increase feedback rank" is a measured knob, not an open mechanism.

### 2.4 V22/V24 — source-age shared/nested bases

The public release reports a clear source-age law:

- roughly `3n/8` at age 4;
- roughly `n/4` at age 6;
- roughly `7n/32` at age 7;
- one notch lower produces an accuracy cliff.

The important implementation point is that the old-source dense legs are still re-formed
because the D21 update uses Hadamard products. Shared bases reduce transport/contraction
cost but do not eliminate dense old-source work.

**Closed:** rank resweeps, earlier age gates, separate lower-rank bases, and a third tiny
nested tier are already measured or closed by arithmetic.

### 2.5 V25 — adaptive lambda

The public rule scales the baseline per-layer lambda using the online ratio of mean
transported K4 diagonal to mean variance. It removed much of the per-MLP spread of fitted
lambdas but changed public score only about 1%.

**Closed:** lambda-table polishing is not the missing top-tier mechanism.

### 2.6 V29 — cost-only delta

The public author states V26–V29 change no estimator arithmetic. V29 uses:

- Strassen-Winograd block recursion in ordinary flopscope operations;
- batched product families;
- persistent output buffers to satisfy residual-time limits;
- folding of the last remaining dense products into existing families.

Reported V29 public result:

- raw: `2.13e-8`;
- `C/B=0.2526`;
- adjusted: `5.40e-9`.

The public release also records an unresolved fair-accounting question around the Strassen
expression. Therefore E137 treats:

- **V25** as the clean method/fallback baseline;
- **V29** as the measured live cost baseline.

---

## 3. Public dead ends: do not recycle

All rows below are **PUBLIC VERIFIED** measurements/arithmetic closures from the release.

| # | closed idea | primary-source result / reason |
|---:|---|---|
| 1 | drop/window old sources | W=4 about `1.02e-6`; every source matters |
| 2 | memoryless old-source tensor supported only on D3/D21 slices | about `9.1e-7`; fully off-diagonal K3 is needed to regenerate next-layer D21 |
| 3 | Phase-1 A716/slice-response closure at Phase-2 shape | about `9.8e-7`; fitted correction barely helps |
| 4 | Gaussian scale-mixture closure | about `2.33e-6` |
| 5 | capped hub columns / atom truncation | 4n columns leave D21 relative error up to ~0.39; even 8n leaves ~0.03–0.14 |
| 6 | symmetric Tucker confinement of all three K3 legs | catastrophic at R=512/256; P is full-rank at birth |
| 7 | separate per-source rank ladder | ~17x accuracy loss for ~1.8x compute saving |
| 8 | shared basis below measured age/rank law | +22%, +96%, 3x-type cliffs depending gate/rank |
| 9 | per-source K4 legs / full augmented K3 | structural cost floor at or above ~0.95B |
| 10 | learned/online output correction | final cheap features correlate <0.09 with residual; ~1.01x on regen base |
| 11 | K2 plus marginal skew/kurtosis/Mehler patches | floor around `4–5e-6`; misses cross-neuron K3 |
| 12 | MC control-variate hybrids | needed 33–300x VR; best reported ~1.5x |
| 13 | symmetric-tensor contraction algorithms | wrong algebraic object; V16b hot ops are nonsymmetric matmuls |
| 14 | accounting tags/dtype tricks | flopscope billing already tight |
| 15 | float32→float64 hot path | ~+0.004%, noise |
| 16 | larger residual/feedback ranks, extra range-finder pass | 1–3% raw gain for 3–8% cost; score-negative |
| 17 | exact (2,1,1) K4 core | ~9% raw gain at 0.5–1.0B extra-class cost |
| 18 | Tucker core of merged old tier | only cheaper below rank ~150, below the measured accuracy cliff |
| 19 | hub-side merge | same CP/column-flatness obstruction as #5 |
| 20 | adjoint/backward final-mean sensitivity to D21 | still requires one dense contraction per source/layer and linearizes material feedback |
| 21 | exact factor-space Hadamard product | Khatri-Rao rank `r^2`; exact multiplicative closure is the central cost wall |
| 22 | Phase-1 sampling/QMC/preintegration/Stein families | pure sampling around `1.2e-6` adjusted at Phase-2 shape |
| 23 | pricing polish after V29 | <=4% on paper; residual-time cap makes it ~0% shippable in the reported implementation |
| 24 | repeated literature triage | no usable quenched cross-neuron >=3-order propagation mechanism found |
| 25 | repackaging the same leg expansion | public conclusion: V29 is at its raw floor and no inspected leg-based compression reaches ~0.15B |

### What #21 does **not** close

The public argument closes **exact low-rank factorization** of the Hadamard/Khatri-Rao
feature map.

It does not report a test of an **oblivious randomized matrix-product sketch applied only
to the already-formed old-tier contraction axis**.

That distinction is the opening used by the E137 hypothesis below.

---

## 4. Gates that remain open

### 4.1 Accuracy gates

**PUBLIC VERIFIED:** V25/V29's shipped closure sits near its own K3 + memoryless-K4 floor.

- V25/V29 public raw: about `2.13e-8`.
- author's float64 same-closure local floor: about `2.07e-8`.
- public author converts that to roughly `1.94e-8` on their LB scale.
- reported leaders on 2026-09-10 reached about `1.71–1.79e-8`.

Therefore a top raw-accuracy improvement requires information **outside** the shipped
K3 + memoryless-K4 closure. E137 does not claim to solve that accuracy gap.

For a **cost-only clean improvement**, the relevant accuracy gate is instead preservation
of the verified V25/V29 arithmetic.

The public release gives a useful internal proxy:

`extra final MSE ≈ 4.2e-6 * epsilon_D21^2`

and says keeping extra error within ~10% of a `2.1e-8` base needs roughly

`epsilon_D21 <= 2.2%`.

This is a fitted empirical law, not a theorem, but it is the best primary-source gate for
an internal D21 approximation.

### 4.2 Cost gates

V29's public steady-state ledger, one unit = `2n^3` FLOPs:

- young K3: `115.6 u`;
- old K3: `106.8 u`;
- thin/elementwise K3: `24.8 u`;
- covariance: `7.1 u`;
- closure + birth: `5.7 u`;
- total: about `260.1 u = 0.254B` in the namespace audit
  (suite headline `0.2526B`).

The public author emphasizes:

`V29 minus old tier ≈ 153 u ≈ 0.150B`.

This is the remaining cost question. Ordinary rank/basis/source deletion is closed.
A real cost improvement must reduce the old tier **without deleting its information**.

Additional deployment gates:

- residual wall time <400 ms/MLP;
- no setup/import bloat;
- float64 is billed at 2x;
- any V29/Strassen composition inherits the disclosed accounting-rule uncertainty.

---

## 5. E132–E135 overlap audit

### E132 — LOCAL VERIFIED SCOPE

Branch:
`research/e132-layer-born-source-age-d21-20260920`.

E132 is a source-age D21 transport used to build an unbiased cubic-Hermite correction.

**E137 hypothesis is disjoint:** it does not construct a new D21 state, source-age basis,
Hermite control, pilot/evaluation split, or output correction. It only changes how an
already-existing V25/V29 old-tier matrix contraction is evaluated.

### E134 — LOCAL VERIFIED SCOPE

Branch:
`research/e134-source-k3-direct-closure-20260920`.

E134 is a direct source-age full-K3 distributional closure with cubic cores and a final
Edgeworth materialization.

**E137 hypothesis is disjoint:** no new K3 representation, source birth law, cubic core,
Edgeworth term, or source-age schedule is introduced.

### E135 — scope exclusion

No `e135` branch was present in the repository branch inventory at review time.
Per the frozen E137 protocol, Parseval/orthogonal-source residual certificates,
transport-residual norms and deterministic truncation-bound rescue are excluded.

**E137 hypothesis is disjoint:** it is an internal randomized matrix multiplication
patch with a direct candidate-vs-baseline D21 falsifier, not a residual certificate.

---

## 6. One new admitted hypothesis

# H137 — old-tier CountSketch contraction patch

Classification: **HYPOTHESIS**

### 6.1 Baseline-native delta

Do not change:

- V25/V29 K3 source births;
- D3/D21 formulas;
- V17 K4 regeneration;
- V18 D21 feedback;
- V19 trim;
- V22 rank-384 shared basis;
- V24 rank-224 nested basis;
- V25 adaptive lambda;
- young-source arithmetic;
- old-leg formation.

Change exactly one operation family:

For an old source in the shared basis, V25/V29 forms contractions of the type

`LA FA^T` and `LP FP^T`

before the common trailing multiplication by `Qc^T`.

Here:

- `LA,LP in R^(n x n)`;
- `FA,FP in R^(r x n)`;
- exact product costs scale as `O(n^2 r)`.

Replace only that product by randomized matrix multiplication:

`X Y^T ≈ (X S)(Y S)^T`

where `S in R^(n x s)` is a fixed target-free CountSketch:
each original hub column hashes to one of `s` buckets with one deterministic
Rademacher sign.

For a fresh random CountSketch,

`E_S[(X S)(Y S)^T] = X Y^T`.

The sketch is therefore not a top-column truncation: **every hub column contributes**.

### 6.2 Why this is not a closed V25/V29 dead end

It is not #5/#19 hub-column truncation:

- those methods delete columns based on importance;
- CountSketch mixes all columns into buckets and is unbiased over the sketch law.

It is not #18 Tucker:

- no K3 tensor core is introduced;
- the V22/V24 bases/ranks remain unchanged.

It is not #21 exact Khatri-Rao factorization:

- #21 says the exact Hadamard feature rank is `r^2`;
- H137 accepts a controlled randomized approximation only in the final matrix product.

It is not E033 source-axis Hutchinson:

- E033 mixes source identities as the persistent representation;
- H137 preserves every V25/V29 source exactly through transport and sketches only the
  already-existing hub-column contraction of old sources.

It is not E132–E135 for the reasons in section 5.

### 6.3 Why it could improve the verified baseline

**PUBLIC VERIFIED:** V29's `shared` contraction family alone is about `27.9 u`
(`10.7%` of total compute), separate from another `27.9 u` used to form old dense legs.

**INFERENCE:** if CountSketch can reduce the old-tier contraction family materially while
holding D21 error below the public ~2.2% gate, it gives a direct adjusted-score improvement
without asking for a new closure.

A conservative first sketch size can be large enough that this is a matrix-product
compression rather than a severe rank truncation. For example, with the tier-1
`r=384`, `s=512<n=1024` still leaves the output's full rank-r capacity available while
reducing the contracted hub dimension from 1024 to 512.

The exact production savings must be measured under flopscope; E137 does **not** claim a
numerical C/B before that measurement.

### 6.4 Failure mode

CountSketch variance may inject too much D21 error, especially because V29 repeatedly
feeds D21 back into new source births. If the old-tier product has high stable rank, an
`s<n` sketch may fail the 2.2% internal gate even though it is unbiased in expectation.

That would be a clean terminal NO-GO for H137.

---

## 7. Successor falsifier sketch — no code authorized by E137

A successor experiment should be a **patch test against the pinned public V25 baseline**,
not a new estimator.

### Stage A — target-free algebraic gate

Freeze before code:

- public baseline blob:
  `estimator_v25.py@195373a110215256b759d7c172ba8c923c62e5cc`;
- one CountSketch width, suggested first point `s=512`;
- deterministic hash/sign seed rule depending only on experiment id and layer;
- patch only old-tier `LA FA^T` / `LP FP^T` products;
- all V25 constants/ranks unchanged.

On frozen public-weight MLPs, record exact V25 old-tier D21 contribution before target
materialization and the sketched contribution.

Required target-free GO gates should include:

1. deterministic replay;
2. no target/reference access during sketch construction;
3. finite predictions/state;
4. pooled old-tier D21 relative RMS error `<=2.2%`;
5. no individual late layer with catastrophic D21 error;
6. measured flopscope compute strictly below pinned V25 on the same MLPs;
7. residual-time headroom remains below the grader cap.

Failure closes H137 without reading final target means.

### Stage B — only after Stage A GO

A separately frozen validation may compare final outputs with the same public references
used by the public baseline release.

The clean-improvement criterion should be:

- raw MSE no worse than the pinned V25/V29 baseline by a preregistered small tolerance;
- adjusted score strictly lower;
- zero failures;
- no parameter sweep after target readout.

If the patch does not beat V25 first, do not compose it with V29 Strassen engineering.

---

## 8. Final E137 conclusion

### Closed

The following should not be re-proposed as "new":

- V16b algebraic source contraction rewrite;
- V17 memoryless K4 regeneration;
- V18 D21 feedback;
- V19 last-layer trim;
- V22/V24 source-age rank retuning/nesting;
- V25 lambda tuning;
- V29 pricing/buffer-only engineering;
- the 25 public dead-end classes in section 3;
- E132 source-age D21/Hermite;
- E134 source-age direct K3;
- E135 residual/certificate rescue classes.

### Open

Two distinct problems remain:

1. **raw accuracy:** content beyond K3 + memoryless K4;
2. **cost at fixed V25/V29 arithmetic:** old-tier contractions/leg work without information
   deletion.

E137 selects only problem 2.

### Selected hypothesis

**H137: old-tier CountSketch contraction patch.**

It is intentionally modest: a clean, falsifiable delta over a verified public baseline.
It does not claim to explain the leaderboard leaders and does not introduce an independent
estimator family.

No E137 estimator code, workflow, Actions run, public run, scorer, holdout/full execution,
canonical mutation, ledger mutation, tuning, or sweep occurred.
