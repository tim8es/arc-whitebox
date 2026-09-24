# R376 — new estimator frontier after R374

**Status:** COMPLETE  
**Verdict:** **TERMINAL_NO_GO_GLOBAL_AFFINE_GAUSSIAN_RELAXATION_CANNOT_CLEAR_FIXED_TARGET_GATE_WITH_AVAILABLE_LOCAL_EVIDENCE**  
**Mode:** independent report-only theory/method scout; no estimator/benchmark execution  
**Branch:** `research/r376-new-estimator-frontier-20260924`  
**Exact branch base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## 1. Scope and live evidence

R376 starts after the corrected R374 result and asks for at most one genuinely distinct estimator direction that could plausibly beat the strongest same-panel internal parent, not merely a mathematically attractive representation.

Read before candidate selection:

- live `research/history.json`
  - Git blob SHA-1: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
  - E100–E193 IDs: **94**
  - E100–E193 artifact records: **468**
- live consolidated R320
  - branch: `review/r320-sidecar-research-traceability-20260924`
  - head: `a6aa948c6fdd2cc97cb721623a6259d01e30e761`
  - report blob: `669af011e82b6549530e442a30d3a5e92d23ec4f`
  - receipt blob: `a47466aaed0854bea3d60ca20354b4499b9cc0d1`
- corrected/final R374
  - branch: `review/r374-next-distinct-estimator-frontier-20260924`
  - head: `659ab891e1e7a27f0edadb8768b1e094420247ac`
  - report blob: `bcf7b9369628e85cff7fb0585a27e895f99a12a7`
  - receipt blob: `34e304d510309494e4f3a4fb43c6d8400a1e9855`
  - verdict: `TERMINAL_NO_GO_NO_FINITE_RELU_CLOSED_LIFT_ZONOID_PROPAGATION_THEOREM`

R376 does not reinterpret any historical NO-GO as a universal impossibility theorem.

## 2. Strongest confirmed same-panel parent

The comparison parent remains **R209 V25**:

- normalized artifact: `research/results/R209-v25-mini100.json`
- Git blob SHA-1: `0183d0570f7c9965e00e8553ffc003c313865232`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- panel: `v2-phase2 mini:all-100`
- rows: 100
- failures: 0/100
- mean raw final-layer MSE: `2.22830349017044681e-8`
- mean adjusted score: `8.170397440117225e-9` (the stored normalized record differs only in last decimal serialization in some sidecars)
- measured FLOPs/network: `806303721965`

R376 makes no leaderboard-rank or rounded-UI gap inference.

## 3. Dedupe

The candidate search excludes all occupied/closed families in the user request and the live history/R320/R374 chain:

- sampling / Monte Carlo residuals
- cubature / sigma-point / frame / deterministic particle methods
- QMC / Sobol / spherical designs
- control variates / Stein / JVP
- antithetic / Haar / radial Rao–Blackwell
- conditional Gaussian / halfspace / orthant / mask-conditioned state
- cumulant K3/K4 / Edgeworth / higher moments
- Hermite / polynomial chaos
- TT / CP / Tucker / CountSketch / TensorSketch
- characteristic-function / Hilbert-transform propagation
- activation-boundary / boundary-flux / explicit activation-region geometry
- displacement-structure arithmetic
- response-aligned / adjoint / observable corrections
- source-age / window / tail compression
- randomized multilevel / telescope
- H185 exact-fast-arithmetic line
- R366 white-box shallow-ridge flattening and sampled-regression descendants
- R374 lift-zonoid support propagation and close stop-loss/distribution-state variants

Direct repository/history search over E100–E193 found zero occurrences of:
`CROWN`, `DeepPoly`, `Fast-Lin`, `linear bound`, `affine bound`, `interval bound`, or `convex relaxation`.

Exactly one unoccupied class was therefore screened.

## 4. One candidate: GELR

### Gaussian-Expected Linear Relaxation (GELR)

For each fixed Phase-2 network and each final output coordinate (f_j(x)), use a **single global affine verification relaxation** on a symmetric input box rather than propagating a distributional moment/spectral state.

Let

[
K_R=[-R,R]^n,qquad n=1024,
]

and let CROWN/Fast-Lin style verification produce valid affine bounds

[
ell_j(x)=a_j^	op x+eta_j
le f_j(x)le
u_j(x)=c_j^	op x+gamma_j
quadorall xin K_R.
]

The Phase-2 network is zero-bias and applies ReLU after every dense layer, so

[
f_j(x)ge0,qquad f_j(0)=0,
]

and the whole network is positively homogeneous for nonnegative scalar input scaling.

For (Xsim N(0,I_n)), define

[
p_R=P(Xin K_R)=left(2Phi(R)-1ight)^n,qquad q_R=1-p_R.
]

Because (K_R) and the Gaussian density are centrally symmetric,

[
E[X,1_{{Xin K_R}}]=0.
]

Therefore

[
p_Reta_j
le
E[f_j(X)1_{K_R}]
le
p_Rgamma_j.
]

At (x=0), any valid affine lower bound has (eta_jle0). Since the true output is nonnegative, the best target-free lower expectation from a **single global affine lower bound** is therefore exactly

[
L_j(R)=0.
]

For the tail, take any certified coordinate Lipschitz constant (Lambda_j) satisfying

[
f_j(x)leLambda_j|x|_2.
]

Cauchy–Schwarz gives

[
E[f_j(X)1_{K_R^c}]
le
Lambda_jsqrt{nq_R}.
]

Hence a fully deterministic fixed-network upper bound is

[
U_j(R)=p_Rgamma_j+Lambda_jsqrt{nq_R}.
]

The GELR estimator is the interval midpoint

[
oxed{hatmu_j(R)=rac{U_j(R)}2}
]

with certified fixed-target error

[
oxed{|hatmu_j-mu_j|le h_j(R)=rac{U_j(R)}2}.
]

This is target-free: only the supplied network weights, fixed (R), and Gaussian input law enter construction.

It is not unbiased; it is a deterministic certified-error estimator.

## 5. Primary sources

### Fast-Lin

Tsui-Wei Weng, Huan Zhang, Hongge Chen, Zhao Song, Cho-Jui Hsieh, Luca Daniel, Duane Boning, Inderjit Dhillon,  
**“Towards Fast Computation of Certified Robustness for ReLU Networks,”** ICML 2018, PMLR 80:5276–5285.

Primary source:
https://proceedings.mlr.press/v80/weng18a.html

The paper derives efficient certified network output bounds from layerwise linear upper/lower bounds on ReLU.

### CROWN

Huan Zhang, Tsui-Wei Weng, Pin-Yu Chen, Cho-Jui Hsieh, Luca Daniel,  
**“Efficient Neural Network Robustness Certification with General Activation Functions,”** NeurIPS 2018.

Primary source:
https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html

CROWN generalizes efficient linear/quadratic activation relaxations and adaptive bound selection.

R376 uses these sources only for the existence of sound polynomial-time global affine relaxations. The Gaussian-expectation conversion and the structural lower bound below are derived directly.

## 6. Fixed Phase-2 scorer correctness

This candidate is evaluated against the **fixed network target means**, not a population-over-weights mean.

For network (i), define

[
H_i^2(R)
=
rac1{1024}sum_{j=1}^{1024} h_{ij}(R)^2.
]

The actual fixed-target final-layer MSE obeys

[
operatorname{MSE}_{i,mathrm{final}}le H_i^2.
]

Let (C_i) be the all-in candidate FLOPs. Then a sufficient same-panel GO condition over the exact R209 Mini-100 panel is

[
oxed{
rac1{100}sum_{i=1}^{100}
H_i^2
maxleft(0.1,rac{C_i}{2^{41}}ight)
<
8.170397440117225	imes10^{-9}.
}
]

This is the only score-comparison gate used by R376.

## 7. Structural certificate floor

The fatal issue is not CROWN implementation quality. It holds for **any single global affine upper bound** on (K_R).

Define

[
M_j=sup_{|v|_2=1} f_j(v).
]

Because the box contains (Rv) and (-Rv) for every unit vector (v), validity of (u_j) gives, for a maximizing direction,

[
2gamma_j
ge
f_j(Rv)+f_j(-Rv)
ge
R M_j,
]

so

[
gamma_jgerac{R M_j}{2}.
]

Also every valid Lipschitz constant satisfies

[
Lambda_jge M_j.
]

Positive homogeneity and the polar decomposition (X=|X|_2Theta) yield

[
mu_j
=
E|X|_2;E f_j(Theta)
le
E|X|_2,M_j.
]

For (n=1024),

[
ar r:=E|X|_2
=
sqrt2,
rac{Gamma(512.5)}{Gamma(512)}
approx31.992188454829048.
]

Therefore every GELR certificate obeys

[
h_j(R)
ge
c(R),mu_j,
]

where

[
oxed{
c(R)=
rac{
p_R R+2sqrt{nq_R}
}{
4ar r
}.
}
]

A one-dimensional deterministic minimization of this explicit scalar function gives

- (Rapprox5.546)
- (p_Rapprox0.9999700710959285)
- (q_Rapprox2.992890407149673	imes10^{-5})
- (oxed{c_* approx0.04607344105297431})

Thus even the best possible single-global-affine GELR certificate has an unavoidable error-radius floor of about **4.607% of the true mean amplitude coordinatewise**.

This lower bound does not depend on the particular CROWN slope heuristic. Tightening CROWN within the same single-global-affine family cannot remove it.

Escaping it by partitioning the input domain into multiple local affine regions becomes branch/subdivision/activation-geometry territory, which R376 explicitly excludes.

## 8. Exact necessary same-panel condition

If the implementation remains below the scorer floor (C_i/Ble0.1), then beating R209 requires

[
rac1{100}sum_i H_i^2
<
8.170397440117225	imes10^{-8}.
]

Let

[
T^2
=
rac1{100cdot1024}
sum_{i,j}mu_{ij}^2
]

be the exact Mini-100 RMS-squared of the final target mean vectors.

The structural floor implies

[
rac1{100}sum_iH_i^2
ge c_*^2 T^2.
]

Therefore **a necessary condition even before implementation** is

[
oxed{
T^2
<
3.848946586479219	imes10^{-5},
}
]

equivalently

[
oxed{
T<0.00620398790011652.
}
]

For the stricter goal of certifiably beating R209 raw MSE itself, the corresponding necessary target RMS is

[
T<0.00323993666765405.
]

R376 does not assume that the actual public Mini-100 target RMS is above or below these thresholds.

## 9. Local-data audit

The required exact fixed-panel target amplitude is not available in the repository-local evidence.

Main-tree search at exact main head `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5` found **zero** committed:

- `.parquet`
- `.npz`
- `.npy`
- dataset/mini-100 payload files.

R224 did recover immutable Mini-100 identity/fingerprint evidence:

- branch: `review/r224-r209-mini100-fingerprints-20260922`
- receipt blob: `9865e9cdccfadc62a67e380714ad9df8000153e9`
- fingerprint blob: `9ecde34282c3fbef51ff3b11d4ec439012b3c52d`
- 100 exact `mlp_seed/network_id` values
- 100 target SHA-256 values
- target dtype float32
- target shape `[16,1024]`

But those files contain **hashes, not the target arrays**.

The published dataset is identified as external
`aicrowd/arc-whestbench-public-2026@v2-phase2`.
R376 does not download it.

Therefore the exact quantity (T) required by the fixed-scorer admission gate cannot be computed locally in this task.

## 10. Phase-2 compute / memory / time accounting

Official Phase-2 constants already pinned in the project:

- width (n=1024)
- depth (L=16)
- FLOP budget (B=2^{41}=2,199,023,255,552)
- score multiplier floor (0.1)
- wall limit 120 s
- residual wall limit 0.4 s
- solution-process memory 8 GB

Official source blobs:

- scoring: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- generation: `38397fae458acfd46b5642866481672c7fce6f2d`
- rounds: `c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890`
- memory changelog: `fb2e2ababe42c7764fad4b99681445b65c75f7ad`

### Frozen implementation envelope

A matrix-parallel Fast-Lin/CROWN implementation for all 1024 outputs can maintain upper/lower coefficient matrices and preactivation intervals.

R376 freezes the following **maximum admissible implementation envelope**, not a measured FlopScope result:

- at most 4 dense (1024	imes1024) matrix products per network layer;
- charge each at (2n^3) scalar FLOPs;
- reserve an additional (64n^2) scalar ops per layer for sign splits, slopes, interval vectors, norm/tail bookkeeping.

Thus

[
C_{m GELR,max}
=
8Ln^3+64Ln^2
=
138,512,695,296
]

FLOPs, i.e.

[
oxed{
C_{m GELR,max}/B=0.06298828125<0.1.
}
]

So the candidate has a static path to remain at the scorer floor if the implementation fits this schedule.

Any implementation exceeding this frozen envelope fails R376's cost gate and cannot claim the floor-based threshold above.

### Memory

A conservative resident-memory allocation:

- 16 input weight matrices float32:
  (16cdot1024^2cdot4=67,108,864) bytes;
- up to 8 (1024	imes1024) float64 coefficient/work matrices:
  (67,108,864) bytes;
- vectors, slopes, interval endpoints, output rows and bookkeeping: reserve <64 MiB.

Frozen memory budget:

[
oxed{M_{m GELR,max}=256 {m MiB}<8 {m GB}.}
]

### Time

The primary literature establishes polynomial-time bound propagation and practical CPU execution on much larger-neuron verification examples, but R376 has **no measured WhestBench timing**.

Therefore:

- 120 s wall limit: **not measured**
- 0.4 s residual limit: **not measured**

This is a secondary pre-run gate. R376 does not execute a timing test because the stronger fixed-target accuracy-admission gate is already unresolved/failed.

## 11. Cheapest preregistered falsifier

### F376-GELR-ADMISSION

No estimator run is allowed before this gate.

**Inputs allowed:**
- already-local exact Mini-100 target vectors or an already-local immutable summary sufficient to compute (T);
- no download;
- no private/holdout/full data.

**Step 1 — exact data-presence check**

Compute

[
T^2
=
rac1{100cdot1024}
sum_{i,j}mu_{ij}^2.
]

**Immediate NO-GO if**

[
Tge0.00620398790011652.
]

That follows from the structural certificate floor and is independent of CROWN implementation details.

**If and only if the target-amplitude gate passes**, freeze one implementation and run one target-free production-shape cost/timing falsifier:

- exact FlopScope cost (le138,512,695,296);
- peak memory (le256) MiB for candidate-owned state;
- wall (le120) s;
- residual (le0.4) s;
- no targets read by estimator construction.

Only after those pass would one same-panel Mini-100 scorer run be scientifically justified.

## 12. Why no prototype or Mini-100 run occurs

The candidate does not clear the mandatory scorer-level admission gate with the evidence already local.

The exact missing datum is:

> **the RMS of the actual 100 public Mini-100 final target mean vectors, or equivalently the raw locally accessible target arrays needed to compute it.**

R224 preserves only SHA fingerprints.

Downloading the public dataset would violate the R376 instruction.

There is also no primary-source theorem implying that the **fixed deployed Mini-100 panel** satisfies
(T<0.00620398790011652); a population-over-random-weights statement would not answer the scorer target requested here.

Therefore R376 stops before estimator code, synthetic execution, or official Mini-100 execution.

## 13. Scientific verdict

**TERMINAL_NO_GO_GLOBAL_AFFINE_GAUSSIAN_RELAXATION_CANNOT_CLEAR_FIXED_TARGET_GATE_WITH_AVAILABLE_LOCAL_EVIDENCE.**

GELR is genuinely distinct from the excluded estimator families and has:

- a precise target-free estimator;
- a rigorous error interval for each fixed network;
- a static sub-floor FLOP/memory path;
- an exact same-panel scorer inequality.

But a structural theorem shows that any single-global-affine version carries at least a (4.607%) relative certificate radius against the true mean amplitude.

Consequently it can only beat R209 at the scorer floor if the actual Mini-100 final target RMS is below (0.00620398790011652).

That exact fixed-panel datum is not present locally; only target hashes are persisted.

No method run is scientifically authorized from the available evidence.

## 14. Execution accounting

- estimator code created: **NO**
- estimator implementation: **NO**
- estimator runs: **0**
- synthetic runs: **0**
- Mini-100 runs: **0**
- benchmark/scorer runs: **0**
- Actions runs: **0**
- downloads: **0**
- dependency installs: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submissions: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- historical verdicts changed: **NO**
