# R308 — theory-first estimator scout

Status: **NO_GO — no credible mathematically distinct estimator survives deduplication**

Date: 2026-09-24  
Mode: report-only / no execution  
Branch: `review/r308-theory-scout-20260924`  
Exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Decision

R308 does **not** propose an estimator.

After checking the project's public history and the specified R2xx evidence, I found no candidate that is simultaneously:

1. mathematically distinct from already explored/reserved estimator families;
2. network-agnostic and target-free at construction time;
3. supported by a mechanism-level argument strong enough to justify even a cheap falsifier;
4. plausibly compatible with the Phase-2 production budget `B = 2^41` and residual wall cap `0.4 s`.

Inventing another label inside a closed family would be method fishing. The correct R308 disposition is therefore **evidence-based NO_GO before prototype or falsifier execution**. This does not claim that no better estimator exists; it says that the allowed evidence does not justify one new distinct hypothesis now.

## Evidence that constrains the search

### R209 / R231: the remaining problem is global accuracy, not a tiny tail

The normalized R209 V25 reference has 100/100 valid networks, mean final-layer MSE
`2.228303490170447e-8`, mean adjusted score `8.170397440117225e-9`, and mean measured
cost `806303721965` FLOPs/network.

R231 found weak concentration of error: the worst 10% of networks carry only about
12.47% of total raw-MSE mass and the worst 20% about 23.85%. At the score floor
(`max(0.1,C/B)`), an aggregate raw-MSE reduction of about 5.76% would still be needed
to reach the cited 2.1e-9 numerical orientation. R231 also records that raw prediction
tensors are absent from the R209 archive, so a new residual-direction mechanism cannot be
reconstructed from the current normalized evidence alone.

Consequence for R308: a useful new method should change the central bulk under one fixed
rule; tail-only routing or per-network selection is not a justified new direction.

### R223 / R251 / R261: local K4 and calibration descendants are already occupied

R223 tested a normalized per-neuron K4->K3 feed lambda. Its later independently
normalized same-panel record reports mean final MSE
`2.2284993050902814e-8` and adjusted score `8.171116513490032e-9`, slightly worse
than R209. A new per-neuron/feed-local lambda variant would therefore be a descendant,
not a new family.

R251's own report defines **V25-HK4-ROWLOCAL**, a heteroscedastic row-local K4
off-diagonal closure. It was not scientifically measured because its parent-first
runtime was unavailable, but it already occupies the obvious row-local
heteroscedastic-K4 mechanism. (R276 uses a different shorthand for R251; R308 uses
R251's own report as the family identity.)

R261 separately screened removal of V25's online mean-correction rider and rejected the
ablation before execution as an under-motivated calibration/shrinkage move. Global or
local rescaling of existing fitted correction terms is therefore not a genuinely new
R308 family.

### R232 / R238 / R269: extrapolation, recycled bases, and randomized telescopes are not new lanes

R232 froze dual-resolution Richardson debiasing,

[
m_{DRRE}=m_H+gamma(m_H-m_L),qquad
gamma=rac{r_L^2}{r_H^2-r_L^2},
]

with the assumed rank-bias expansion
[
m_r=m_infty+a r^{-2}+O(r^{-4}).
]

Its exact-small attempt became protocol-terminal before an MSE comparison, so DRRE was
not scientifically falsified. It is nevertheless an already-defined estimator family;
a changed rank pair, exponent, or blend would be a descendant, not a new hypothesis.

R238 similarly froze a recycled-start range finder using
(Omega=W_{slice}+Q_p). Its parent executability failed before candidate construction.
The specific accuracy claim remains unevaluated, but recycling/restarting the shared
basis is already an occupied family under the no-descendant constraint.

R265's full-history screen found randomized multilevel debiasing/randomized telescoping
as the only abstractly distinct literature lead. R269 then made the surviving
depth-prefix version concrete:
[
Z=Y_0+rac{B}{p}(Y_1-Y_0),qquad Bsimmathrm{Bernoulli}(p).
]
Although (E_B[Z]=Y_1), its target risk satisfies
[
E_B|Z-t|^2
=|Y_1-t|^2+rac{1-p}{p}|Y_1-Y_0|^2,
]
so it adds expected MSE unless cost reduction compensates. More fundamentally, adjacent
hidden-layer mean vectors are not established as a nested approximation sequence to one
fixed quantity.

This matches the conditions in the primary multilevel literature: Giles (2008) obtains
MLMC efficiency by exploiting a hierarchy of approximations whose level-difference
variance and cost obey favorable decay/growth relations; Rhee & Glynn (2015) obtain
unbiased estimators by randomizing over a convergent approximation sequence under
summability/decay conditions. R269 found no non-duplicative V25 hierarchy with such a
target-free correction-decay law and a committed production cost split.

Primary sources:
- Michael B. Giles, “Multilevel Monte Carlo Path Simulation,” *Operations Research*
  56(3), 607–617 (2008), DOI: https://doi.org/10.1287/opre.1070.0496
- Chang-Han Rhee and Peter W. Glynn, “Unbiased Estimation with Square Root Convergence
  for SDE Models,” *Operations Research* 63(5), 1026–1043 (2015),
  DOI: https://doi.org/10.1287/opre.2015.1404

### R244 / R247 / R248 / R250: structured compression is heavily constrained by direct negative evidence

R244 reserved two dimensions of the fixed residual rank for exact row/column marginals
and applied the remaining low-rank approximation only to the doubly centered remainder.
R276 records its same-panel mini-100 outcome as worse in both MSE and adjusted score.
A different marginal-preserving rank split is therefore a descendant.

R247's 2:4 young-D21 right-factor sparsifier had a plausible static cost ratio
((approx0.883) of R209) but failed its target-free fidelity screen by a large margin:
mean D21 RRMS about 0.372 versus a preregistered 0.012 gate.

R248 tested a rank-1 Kronecker surrogate for young transport. Even the best rank-1
Kronecker oracle had mean transport RRMS about 0.985 versus a 0.012 gate.

R250 tested a rank-1 shared two-channel A/P leg representation. Its oracle downstream
D21-core RRMS was about 1.0 versus a 0.012 mean gate.

These results do not prove every compression impossible, but they eliminate the obvious
“new structured low-rank/sparse transport” variants as genuinely new theory-first
candidates for R308.

## Full-history deduplication conclusion

R265/R276 already inventory the broader project history: residual/control-variate and
orthogonal sampling; QMC/cubature/frame designs; Gaussian/mixture/cumulant/K3/K4,
Edgeworth and saddlepoint closures; polynomial/Hermite/TensorSketch; shared-basis,
DEIM, TT, CP, Kronecker and other low-rank carriers; response-aligned/adjoint/JVP/
boundary-flux methods; calibration/cross-fit/shrinkage; source-age/window/tail
truncations; and arithmetic/fast-matmul transformations.

Against that inventory plus the R2xx work above, the remaining superficially plausible
moves collapse into already occupied families:

- another local fourth-moment/K4 coefficient -> R223/R251/cumulant descendants;
- another residual/output correction -> response-aligned/output-subspace/calibration
  descendants, and the current R209 archive lacks the raw residual tensors needed for a
  new target-free mechanism signal;
- another rank/basis/transport compression -> R244/R247/R248/R250 plus the older
  low-rank history;
- another extrapolation or stochastic hierarchy -> R232/R265/R269;
- another correction toggle/shrinkage -> R261 and prior calibration history.

No remaining candidate has a clean mathematical distinction *and* a pre-existing
target-free reason to expect lower activation-mean error. Therefore R308 stops rather
than laundering an old family through new notation.

## Estimator / assumptions / error mechanism

**Estimator:** none proposed.  
**Formula:** not applicable.  
**Assumptions:** not applicable.  
**Claimed error reduction:** none.

This is deliberate: writing a formula first and then inventing a rationale would violate
the theory-first and deduplication requirements.

## Falsifier and stop/go thresholds

No synthetic falsifier is preregistered or executed because no credible distinct
candidate survived the desk screen. A falsifier without a prior estimator/mechanism would
be an unconstrained search over synthetic fixtures rather than a falsification test.

Re-entry into a future estimator job should require, before any execution:

1. a mathematical estimator map that is not reducible to the families listed above;
2. a target-free mechanism argument tied to a quantity available at inference time;
3. a static all-in production bound below `2^41` FLOPs/network and a credible
   residual-path design below `0.4 s`;
4. fixed synthetic fixtures and numerical GO/STOP thresholds derived from that specific
   mechanism, frozen before execution.

Those are eligibility conditions for a future hypothesis, not R308 experimental gates.

## Compute / access accounting

- estimator implementations: **0**
- estimator executions: **0**
- synthetic falsifier runs: **0**
- benchmark/public-mini runs: **0**
- Actions runs: **0**
- dataset or dependency downloads: **0**
- private/holdout/full accesses: **0**
- paid compute: **0**
- submissions: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- report-only branch artifacts: this report + one JSON receipt

## Final disposition

**R308 = NO_GO_AFTER_DEDUPLICATION.**

The project currently lacks a defensible, mathematically distinct, network-agnostic
estimator hypothesis that can be proposed from the allowed public evidence without
recycling a rejected/reserved descendant. The next scientifically useful input is a new
mechanism-level signal, not another estimator-family rename.
