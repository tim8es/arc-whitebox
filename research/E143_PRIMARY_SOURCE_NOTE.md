# E143 — primary-source research on particle repair, structured clouds, MUB/Kerdock and variance reduction

Status: **PRIMARY-SOURCE RESEARCH COMPLETE / ONE POST-V29 HYPOTHESIS ADMITTED / NO IMPLEMENTATION RUN**

Protocol:
`research/E143_PROTOCOL.md`

Protocol commit:
`493c1989f3e28cd89fe843036e841ef42d826c60`

## 1. Executive result

The primary sources separate three claims that are easy to conflate.

1. **Structured sampling is real.** Kerdock/MUB geometry and moment matching produced
   repeatable variance reductions in Phase 1.
2. **Literal large particle clouds do not scale to Phase 2.** A complete 1024-D
   Kerdock/MUB cloud is already too large for the ordinary dense propagation surface and
   a single float32 cloud buffer crosses the grader's 4 GiB single-array cap.
3. **The surviving post-V29 opportunity is not a sampling estimator.** The only E143
   hypothesis admitted below uses a tiny structured cloud as an *in-flow diagnostic state*
   that repairs V29's D21 birth-feedback channel before later nonlinear propagation.
   V29 remains the estimator backbone.

Full-cloud Kerdock and output-only MC/QMC/control-variate routes are therefore closed
before implementation. One microcloud mechanism remains cost-admissible.

---

## 2. Official problem and Phase-2 restrictions

### 2.1 ARC's objective

**ARC OFFICIAL.**

ARC frames the research program as mechanistic estimation that competes with sampling:

- https://www.alignment.org/blog/competing-with-sampling/
- https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/
- https://www.alignment.org/blog/announcing-the-arc-white-box-estimation-challenge/
- paper: https://arxiv.org/abs/2605.05179
- reference code:
  https://github.com/alignment-research-center/mlp_cumulant_propagation

The reference code implements cumulant propagation rather than particle sampling and
explicitly contains factored K3/K4, Wick/Hermite, diagonal-slice and harmonic
representations.

### 2.2 Current WhestBench contract

**WHEST OFFICIAL.**

Primary contract:

https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/estimator-contract.md

Current Phase-2 limits are:

| quantity | official value |
|---|---:|
| width | 1024 |
| depth | 16 |
| FLOP budget per MLP | (B=2^{41}=2,199,023,255,552) |
| wall cap | 120 s |
| residual wall cap | 400 ms |
| setup cap | 5 s |
| participant-process RAM | 8 GB |

Numerical computation in `predict()` must use FlopScope primitives. The current scoring
compute is pure analytical FLOPs:

https://github.com/AIcrowd/whest-starterkit/blob/main/docs/how-to/manage-flop-budget.md

The grader also caps every individual array at 4 GiB:

https://github.com/AIcrowd/whest-starterkit/blob/main/docs/troubleshooting/faq.md

The official code policy permits shipped precomputed data, but setup is for loading it,
not performing MLP-dependent numerical work:

https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/allowed-code.md

This matters for structured designs: a fixed MLP-independent direction table can be
shipped and loaded, but every weight-dependent particle propagation must be metered.

---

## 3. What structured clouds actually achieved

### 3.1 Complete Kerdock/MUB cubature

**PARTICIPANT PRIMARY — Skye Nygaard.**

Repository:

https://github.com/SkyeNygaard/ARC-Whitebox

Primary README states that the Phase-1 design used

- 128 Kerdock bases plus the coordinate basis;
- 129 bases total in dimension 256;
- antipodal closure;
- 66,048 spherical nodes.

Submission #320802 was graded:

- adjusted score: (1.55	imes10^{-7});
- 50/50 public MLPs;
- zero failures;
- reported 4.2x Monte Carlo.

The fixed 100-network arithmetic ablation held the node set constant:

| propagation | raw final MSE | effective compute | budget used | adjusted |
|---|---:|---:|---:|---:|
| dense | (2.2826	imes10^{-7}) | (2.689	imes10^{11}) | 98.86% | (2.2565646	imes10^{-7}) |
| depth-5 Winograd | (2.2819	imes10^{-7}) | (1.748	imes10^{11}) | 64.27% | (1.4641716	imes10^{-7}) |

Thus the structured node set and the arithmetic implementation are separate effects.

The same repository reports a static limiting-kernel ceiling at the 66,048-node design:

- complete Kerdock is at most 0.0233242% above the best nonnegative mass-one static rule;
- arbitrary signed mass-one weights improve Kerdock-relative risk by at most 6.2940%.

The author's own trust boundary is important: these are static limiting-kernel results,
not lower bounds against adaptive, finite-width, nonlinear or network-dependent
estimators.

Primary evidence labels:

https://github.com/SkyeNygaard/ARC-Whitebox/blob/main/whestbench/claims.csv

### 3.2 MUB geometry, not a missing design point

**PARTICIPANT PRIMARY — ely2sh.**

Forum:

https://discourse.aicrowd.com/t/phase-1-write-up-the-missing-basis-was-not-the-mechanism-submission-327749/18176

The write-up reports an exact ReLU-kernel result: among equal-sized antipodal unions of
orthonormal bases, pairwise mutually unbiased bases minimize the expected quadrature MSE
in the stated infinite-width He-ReLU setting.

Finite-width protected measurements reported:

- missing-basis predicted ratio: 1.00930x;
- lockbox measured ratio: 1.00907x;
- MUB corrected-MSE gain against Haar/randomized-flat/Owen-Sobol controls:
  1.286–1.391x.

This is evidence for structured angular coverage, but it is a constant-factor result,
not evidence that static sampling closes the Phase-2 V29 gap.

---

## 4. Moment matching and classical variance reduction

### 4.1 Antithetic + covariance whitening

**PARTICIPANT PRIMARY — submission #324497.**

Forum:

https://discourse.aicrowd.com/t/phase-1-write-up-variance-reduction-beats-closure-refinement-a-moment-matched-sampling-estimator-submission-324497/18201

On the Phase-1 public split, the author measured:

| estimator | local final MSE |
|---|---:|
| plain MC, n=5,000 | (1.17	imes10^{-5}) |
| antithetic, n=5,000 | (8.81	imes10^{-6}) |
| moment-matched antithetic, n=5,000 | (4.18	imes10^{-6}) |
| moment-matched antithetic, n=10,000 | (2.42	imes10^{-6}) |

The covariance-whitening step produced a further 2.1x final-layer MSE reduction after
antithetic pairing, and about 2.7x on the all-layer metric. Its stated requirement is
(n/2ge d) so the empirical Gram matrix is full rank.

This establishes that exact low-order sample moments can be valuable. It does not imply
that the resulting sampler is competitive with Phase-2 V29.

### 4.2 Phase-2 sampling closure

**504ALDO PRIMARY.**

Pinned release:

https://github.com/504aldo/whest-p2-cumulant-k3/tree/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45

Community write-up:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/community_post.md

Findings:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/findings_log.md

The release reports:

- Phase-2 pure sampling near (1.2	imes10^{-6}) adjusted;
- scrambled Sobol/QMC gives only a constant-factor improvement over iid sampling;
- F62 MC control-variate hybrid at depth 16 needed 33–300x variance reduction while
  the best realizable reduction was about 1.5x;
- the conclusion is that sampling/QMC/ordinary output-CV cannot reach the V29 regime.

Therefore E143 may not propose a pure sampler or an endpoint MC correction.

---

## 5. In-flow particle repair: primary evidence

### 5.1 Graded structured-particle submission

**PARTICIPANT PRIMARY — Andrei Bulzan, Phase-1 submission #327801.**

Repository:

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation

Forum report index:

https://discourse.aicrowd.com/t/phase-1-report-submission-327801/18183

Remote Phase-1 receipt reported by the author's repository:

| quantity | value |
|---|---:|
| public adjusted | (1.1432995022695342	imes10^{-7}) |
| public final MSE | (2.206820236239082	imes10^{-7}) |
| mean effective compute | 140,703,286,543.49994 |
| public rows | 50/50 |
| complete grader | 100/100, zero failures |

Primary README:

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/README.md

The author's current method description explicitly characterizes the family as structured
quadrature plus **in-flow moment repair**:

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/method/METHOD.md

The documented family:

1. uses balanced Kerdock/Hadamard-like directions;
2. propagates the cloud through the realized ReLU network;
3. preserves pair/orientation structure;
4. repairs early hidden moments while the cloud is still in flow;
5. uses width compression;
6. reconstructs late signed/covariance-sensitive observables.

The important conceptual distinction is that the analytic state is not the final
predictor. It modifies particles *before later ReLUs*, allowing repaired particles to
follow a different nonlinear trajectory.

### 5.2 What particle repair did **not** solve

The same primary repository contains unusually useful negative records.

#### Hidden endpoint denoiser — closed

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/ledger/experiments/hidden_cloud_denoiser_20260728/VERDICT_R1_20260728.md

Measured ratios relative to equal-K32:

- Full: 1.02416;
- Generated: 1.01037.

The denoiser worsened pooled error despite exact endpoint reconstruction. Endpoint hidden
state alone was not a transferable error observable.

#### Final-hidden Rao–Blackwell/PCA Gaussianization — closed

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/ledger/experiments/final_hidden_rao_blackwell_20260729/VERDICT_FINAL_HIDDEN_RAO_BLACKWELL_R1_20260729.md

Final-hidden covariance is strongly concentrated:

- top 8 energy: 0.861 Full / 0.848 Generated;
- top 16: 0.923 / 0.921;
- top 32: 0.965 / 0.965.

Nevertheless the least harmful rank-32 conditional-Gaussian candidate had
candidate/baseline ratios 1.00396 and 1.02005. Low covariance energy does not mean low
non-Gaussian importance.

#### Conditional width reconstruction — cost passes, accuracy fails

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/ledger/experiments/conditional_width_impute_20260729/VERDICT_CONDITIONAL_W200_R1_20260729.md

Projected cost:

- width-200 base: 161.296B;
- reconstruction overhead: 0.095B;
- total: 161.391B.

But the Full loss-recovery statistic was (-0.60051), and the Generated improvement was
reversed. The target-free covariance explained typically below 5% of omitted variance.

#### Rank-8 coupled H2 cloud — strong NO-GO

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/ledger/experiments/coupled_closure_h2_rank8_cloud_20260729/VERDICT_COUPLED_CLOSURE_H2_RANK8_CLOUD_R1_20260729.md

Candidate/direct final MSE ratios:

- Full: 43.3352;
- Generated: 343.6665.

The projected count, 54.753B, passed the experiment's 60B gate. Accuracy, not cost,
killed it. A moment-matched Gaussian connected-quadratic law was not stable under deep
iteration.

#### First-harmonic in-flow residual cloud — real gain, insufficient transfer

https://github.com/AndreiBulzan/arc-whitebox-submission-and-documentation/blob/main/ledger/experiments/coupled_harmonic_residual_cloud_20260729/VERDICT_COUPLED_HARMONIC_RESIDUAL_CLOUD_R1_20260729.md

K24 final results:

| family | direct H1 | coupled harmonic | ratio |
|---|---:|---:|---:|
| Full | (1.1298450	imes10^{-5}) | (7.8737450	imes10^{-6}) | 0.696887 |
| Generated | (1.8589723	imes10^{-6}) | (1.7567986	imes10^{-6}) | 0.945038 |

This removed about 30.3% of Full error but only about 5.5% of Generated error and missed
the preregistered continuation gate. The author's mechanistic conclusion is especially
relevant to E143: the unresolved signal is in basis-varying even and mixed higher angular
harmonics; first-harmonic repair alone is insufficient.

---

## 6. V29 is the correct backbone, not another cloud competitor

**504ALDO PRIMARY.**

Public V29 headline:

- raw final-layer MSE: (2.13	imes10^{-8});
- (C/B=0.2526);
- adjusted: (5.40	imes10^{-9}).

V29 already carries the hard nonlocal object: quenched cross-neuron K3. The public release
also establishes:

- D3/D21 are the interface consumed by the ReLU update;
- a memoryless slice-only D21 state is not closed;
- the D21 feedback rank-16 channel matters;
- cheap covariance plus marginal skew/kurtosis is capped around (4)–(5	imes10^{-6});
- online/output corrections and MC CVs are not the residual;
- the public D21 fit gives an approximate extra-error law
  [
  Delta {m MSE}approx 4.2	imes10^{-6}epsilon_{21}^2,
  ]
  and about (epsilon_{21}le2.2%) is needed to stay within 10% of the
  (2.1	imes10^{-8}) raw regime.

Primary source:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/community_post.md

This suggests the only useful particle role is to measure a small, weight-specific
**in-flow residual that V29's analytic state can consume**, rather than replacing V29.

---

## 7. Phase-2 kill: complete Kerdock/MUB particle propagation

### 7.1 Node count

**DERIVATION from the standard complete real Kerdock/MUB family.**

At (d=256), the primary Kerdock release uses (d/2+1=129) bases. At
Phase-2 (d=1024), the corresponding complete real family has

[
B_{m MUB}=1024/2+1=513
]

bases. Carrying every direction and its antipode gives

[
N_{m full}=2(513)(1024)=1,050,624.
]

### 7.2 Ordinary dense-propagation cost

One generic dense post-ReLU transport of all nodes costs

[
2N_{m full}d^2
=
2(1,050,624)(1024)^2
=
2,203,318,222,848.
]

Since

[
B=2,199,023,255,552,
]

one ordinary dense layer is already

[
1.001953125B.
]

A literal full-cloud implementation using ordinary dense propagation is therefore
**terminally over budget before the remaining layers are considered**.

This is intentionally scoped to literal dense particle propagation. The Phase-1 Kerdock
submission demonstrates that exact fast arithmetic can reduce a dense implementation's
charged cost. E143 does not claim a universal lower bound against every possible fast
matrix multiplication algorithm. It closes the literal complete-cloud mechanism relevant
to in-flow repair unless a separately proved sub-budget deep propagation surface is
provided.

### 7.3 Single-array restriction

A single float32 (N_{m full}	imes1024) particle array occupies

[
1,050,624	imes1024	imes4
=
4,303,355,904 {m bytes}
=
4.0078125 {m GiB}.
]

That exceeds the official 4 GiB single-array guard. Chunking can repair the array issue,
but not the ordinary dense FLOP calculation above.

**Decision:** no E143 implementation of the complete Kerdock/MUB cloud.

---

## 8. Why ordinary variance reduction is not the successor

The primary records close the obvious alternatives:

| mechanism | evidence | E143 decision |
|---|---|---|
| full static Kerdock/MUB cloud | Phase-1 strong, Phase-2 literal cost > budget | closed at cost preflight |
| iid/antithetic/QMC output estimator | Phase-2 (sim1.2e-6) adjusted vs V29 (5.4e-9) | closed |
| analytic + MC output CV | F62 needs 33–300x, best ~1.5x | closed |
| endpoint hidden denoiser | ratios 1.024/1.010 | closed |
| final-hidden conditional Gaussianization | ratios 1.004/1.020 | closed |
| Gaussian H2 in-flow closure | 43x/344x worse | closed |
| first-harmonic in-flow repair | 30% Full gain, ~5.5% Generated gain | mechanism real, insufficient by itself |
| another V29 marginal skew/kurtosis patch | public F60 | closed |

What remains open is a **small structured cloud that measures the mixed nonlinear D21
residual and injects it into V29 before future K3 births**.

---

## 9. H143 — MUB128 in-flow D21 birth-feedback repair

Classification: **HYPOTHESIS / ADMITTED FOR A FUTURE TARGET-FREE FALSIFIER / UNEXECUTED**.

### 9.1 Mechanism

Keep V29 unchanged as the main analytic state.

Add only (N=128) structured particles:

- 64 fixed directions selected from 64 distinct bases of a pinned 1024-D real Kerdock/MUB
  construction;
- one deterministic line per basis under a frozen ordering;
- include each antipode, giving 128 total particles;
- the node table is MLP-independent and may be shipped/preloaded under the official
  setup rules.

The particle cloud is not used as the final estimator.

At every nonfinal layer:

1. propagate the 128 particles through the actual dense weight matrix;
2. before ReLU, affine-match each particle coordinate to V29's own target-free
   preactivation mean and variance:
   [
   z^{*}_{rj}
   =
   mu_j+
   sqrt{rac{v_j}{widehat v_j}}
   (z_{rj}-widehatmu_j),
   ]
   with the exact zero-sample-variance fallback (z^{*}_{rj}=mu_j);
3. apply ReLU;
4. form the cloud's post-ReLU D21 slice
   [
   widehat D21^{m cloud}_{ij}
   =
   rac1Nsum_r
   (h_{ri}-ar h_i)^2(h_{rj}-ar h_j);
   ]
5. take the residual against V29's analytic D21;
6. feed only a frozen rank-16 projection of that residual into the **existing V18/V29
   D21 birth-feedback channel** for the next K3 birth.

The current-layer analytic V29 D21, covariance, full source carrier and final output
remain analytic. The cloud modifies only future birth feedback.

### 9.2 Why this is not a renamed closed lane

- not pure sampling: final output is still V29;
- not F62 output CV: the residual is injected before later nonlinear births;
- not first-harmonic repair: the measured object is the mixed third-order D21 slice;
- not slice-only closure: V29 still transports its full off-diagonal K3 source state;
- not E140 SMV: no replacement K3 representation;
- not H137 CountSketch: no approximation of old-tier contractions;
- not E132/E134 source-age transport: particle residual is an independent side state;
- no target fit or final-MSE calibration coefficient.

The hypothesis is motivated by two independent primary observations:

1. the particle-repair literature shows that changing the in-flow state before later
   ReLUs is categorically different from endpoint denoising;
2. V29 identifies D21 as the expensive accuracy-critical interface and already has a
   fixed rank-16 feedback path that can consume a correction.

---

## 10. Phase-2 cost admission for H143

This is a conservative pre-implementation upper, using ordinary dense float32 particle
propagation.

Frozen:

[
N=128,quad n=1024,quad L=16,quad r=16.
]

### Particle propagation

[
C_{m prop}
=
2Nn^2L
=
4,294,967,296.
]

### Empirical D21 contractions

Charge a full (n	imes n) contraction on every layer, even though the final correction
is not needed after the last layer:

[
C_{m D21}
=
2Nn^2L
=
4,294,967,296.
]

### Mean/variance repair

Conservative (12NnL):

[
C_{m repair}
=
25,165,824.
]

### Rank-16 residual projection/injection

Charge two (n	imes n) by (n	imes16)-class operations on each of 15 nonfinal
transitions:

[
C_{m proj}
=
4n^2r(15)
=
1,006,632,960.
]

### Total incremental upper

[
oxed{
C_{m H143,add}
=
9,621,733,376
=
0.0043754578B.
}
]

V29 uses (0.2526B). The combined arithmetic projection is

[
oxed{
C/Ble0.2569754578.
}
]

This is safely below the official (1.0B) Phase-2 hard budget. The 128x1024 float32
particle state is only 0.5 MiB; even with several work buffers and one 1024x1024 D21
matrix, the incremental memory is negligible relative to the 8 GB process cap and 4 GiB
single-array cap.

### Adjusted-score break-even

Because V29 is above the 0.1 score floor, the extra computation must buy raw error.

The relative compute multiplier is

[
rac{0.2569754578}{0.2526}
=
1.0173216855.
]

Therefore H143 improves adjusted score only if

[
rac{{m MSE}_{143}}{{m MSE}_{V29}}
<
rac{0.2526}{0.2569754578}
=
0.9829732465.
]

It must reduce V29 raw MSE by at least

[
oxed{1.7027%}.
]

At public V29 raw (2.13	imes10^{-8}), the break-even raw level is approximately

[
oxed{2.09373	imes10^{-8}}.
]

This is an admission threshold, not a prediction.

### Is a 1.7% raw gain mechanically impossible?

**No.**

The public V29 D21 relation

[
Delta{m MSE}approx4.2	imes10^{-6}epsilon_{21}^2
]

assigns about (2.03	imes10^{-9}) of potential error at
(epsilon_{21}=0.022), roughly 9.5% of (2.13	imes10^{-8}).

That does **not** imply V29 actually has exactly 2.2% D21 error or that H143 can recover
this amount. It only means the 1.7% adjusted-score break-even is not ruled out by the
published D21 error scale. A target-free D21 falsifier can therefore decide the mechanism
before any final-MSE experiment.

---

## 11. Frozen successor falsifier sketch

No implementation is authorized by E143 itself.

A future successor protocol should freeze exactly one point: H143 MUB128 / rank16.

Use only synthetic/reference internal states, never benchmark output targets.

### Fixtures

At least two independent small dense fixture families:

1. He-Gaussian width 32, depth 8;
2. adversarial dense rotation/gain width 32, depth 8.

Reference: exact-small ARC K3/D21 transport or an independently verified exact tensor
reference at these small widths.

### Observable

For every nonfinal layer compare the D21 quantity actually entering the birth-feedback
channel:

[
epsilon_0
=
rac{|D21_{m V29}-D21_{m exact}|_F}
{|D21_{m exact}|_F},
]

[
epsilon_1
=
rac{|D21_{m V29+repair}-D21_{m exact}|_F}
{|D21_{m exact}|_F}.
]

### Binary admission gate for any later final-MSE validation

All must pass:

1. deterministic fixed MUB128 construction;
2. no target/reference values enter the construction or coefficient;
3. finite replay;
4. pooled (epsilon_1/epsilon_0le0.90) on **each** fixture family;
5. no layer worsens by more than 5%;
6. correction is applied only through the frozen rank-16 birth-feedback path;
7. full production operation ledger, including cloud generation/load, moment repair,
   D21 formation, projection, data movement and reductions, remains below the
   (0.2569754578B) upper or an explicitly tighter measured value;
8. official 4 GiB/8 GB/400 ms/120 s restrictions are satisfied.

Failure closes H143. No particle-count sweep, MUB subset sweep, repair shrinkage,
layer selection, target fitting or output blend.

Only a target-free GO would justify a separately frozen final-MSE validation.

---

## 12. Decision

### Closed before implementation

**TERMINAL for E143 research scope:**

- complete 1024-D Kerdock/MUB particle cloud under literal dense deep propagation;
- standalone static particle sampling;
- ordinary QMC/antithetic/moment-matched sampling as a V29 competitor;
- output-only MC/control-variate hybrids;
- endpoint hidden denoisers;
- final-hidden Gaussian/PCA Rao–Blackwellization;
- first-harmonic-only in-flow repair;
- another low-order Gaussian/marginal closure.

### One admitted hypothesis

[
oxed{	extbf{H143: MUB128 in-flow D21 birth-feedback repair on top of V29}}
]

It is admitted because:

- it changes the nonlinear trajectory, not the endpoint;
- it measures the cross-neuron D21 object that V29 identifies as accuracy-critical;
- it retains V29's full K3 carrier;
- it is target-free by construction;
- it is disjoint from E140/H137/source-age lanes;
- conservative Phase-2 arithmetic projects to (C/Ble0.25698);
- its adjusted-score break-even is explicit: at least 1.7027% raw reduction;
- that break-even is not analytically excluded by the published D21 error scale;
- a small exact target-free falsifier can kill it before production implementation.

**No E143 executable code or scientific run occurred.**
