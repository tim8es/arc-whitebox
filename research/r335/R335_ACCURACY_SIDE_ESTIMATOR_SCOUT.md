# R335 — targeted accuracy-side estimator theory scout

**Status:** COMPLETE  
**Verdict:** **EVIDENCE_BASED_NO_GO / ALREADY_COVERED_AT_DEEP_REALIZATION**  
**Candidate families admitted for execution:** **0**  
**Branch:** `review/r335-accuracy-side-estimator-scout-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Question

Is there a genuinely unoccupied estimator family that could lower **raw final-layer MSE at fixed Phase-2 compute**, rather than merely reduce FLOPs?

R333 supplies only a prioritization target, not a proven competition gap. Under its explicitly conditional same-panel/same-scorer comparison, replacing every R209 row's compute multiplier by the 0.1 floor while keeping raw MSE fixed still leaves a score floor of `2.228303490170447e-9`. To hit the illustrative rounded `2.10e-9` display threshold at multiplier 0.1 would require mean raw MSE `2.10e-8`, a reduction of `5.757900157515477%` from R209's `2.228303490170447e-8`. R333 also records that the public-50 join is unproven, so this is a research-prioritization target only.

R335 looked for exactly one mathematically distinct accuracy-side mechanism in primary literature. The only survivor not already named in the ledger was a **characteristic-function positive-part propagation** identity. The scalar identity is exact and directly controls mean error, but it does not yield a new feasible deep estimator: exact propagation of the required joint characteristic function through a dense ReLU layer re-enters the already occupied gate/orthant/boundary state of R317/R321/E114-E119; approximate realizations fall back into already occupied sampling, Gaussian/mixture, or low-rank/compression families.

Therefore R335 stops before implementation or falsifier execution.

## Frozen dedupe evidence

The following exact refs were inspected before literature screening.

| ID | Exact branch head / immutable source | Report / protocol blob | Receipt / result blob | Occupied mechanism relevant to R335 |
|---|---|---|---|---|
| R209 | `research/r209-e136-archive-evidence` @ `e1f6dd6a6bc351b8253e255fef424b1931b37de3` | archive receipt `7fec90369227839a9902c7cceb9f3519acb66cb8` | normalized V25 `0183d0570f7c9965e00e8553ffc003c313865232`, SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742` | factorized K3 / memoryless K4 V25 reference |
| R223 | `research/r223-v25-isolated-improvement-20260922` @ `09efbb920313850a4727bd34db9088a46227ce5f` | protocol `1e88341a6320bf91c8f4eff0aa60d8b6a33cf484` | terminal receipt `a2ea83717b979b40e8ec13703c7465e0f50189ba`; normalized result `c8b617c43ff1145977c38e7e1cca6d23985ec392` | feed-local K4→K3 calibration descendant |
| R265 | `research/r265-method-theory-scout-20260923` @ `bc287eed95df49fb41d81d157b15471a5aa73a3d` | report `e9b5df06173bf70a587774f9374042962847d9e2` | receipt `2c0b54df545a50faf215d049f3a3363927fd4eb1` | broad full-history screen; sampling, covariance, cumulant, Hermite/low-rank, boundary, calibration families occupied |
| R276 | `research/r276-v25-accuracy-screen-20260923` @ `a646038b5aceb5428d6583b07525f394f4820c0d` | report `4970614c1ac789b008260d726a2bbd5272116434` | receipt `56f40cc6b109d769e521c9ba0cf363c7683ef5ab` | global accuracy screen; no surviving distinct candidate |
| R308 | `review/r308-theory-scout-20260924` @ `9c3ef5eefe014e7bdb1a11cc8941999048f6654b` | report `e07ddccdf3744c741a571556d7597ac15b460c4b` | receipt `0c4232035690fdc2b609fc33feea7cb9667aa7e5` | broad theory scout; rejects relabeling occupied families |
| R317 | `review/r317-truncated-normal-gate-estimator-20260924` @ `6ede298753b7ebc35765e18479775879769712ff` | report `b134ccb1c77c3d0e70fe70b64b651e6e5dd1f77c` | receipt `81f6adbc9cc64ab5ad3f4aaf230fe035fffa5ea5` | exact truncated-Gaussian / all-mask state; deep representation infeasible without compression |
| R321 | `review/r321-r317-compression-red-team-20260924` @ `774aac4105bfe1a171f40f7272fc4267aae6c2f8` | report `b0b71f4d74596c4744d0353d1654ac5726aeb2bb` | receipt `2c3d9f881d669ee924cecca106611c6c295a7243` | confirms single orthant queries can be polynomial, but no reusable generic dense polynomial-size propagated gate state was found |
| R333 | `review/r333-r209-compute-floor-headroom-20260924` @ `b089c3e24f7ea5499b66f09da27a2be3f9b5d3de` | report `5e2b58a80a647b9f0a8dcc3355a65d8e5a01e4f5` | receipt `3718a7ce748a57db36f08fbd64fd55cabd51c801` | fixed-MSE compute-floor diagnostic; 5.7579% conditional raw-MSE target |
| E036 | `research/e036-price4-covariance-20260915` @ `99ab17d2814ba3ecf05909e03328f1f23a35b5a7` | protocol `fd191c7b88ce8af759bf8467b2db0e052a36d2c0` | result `fc27202a39e5fa825754ea50e11366bb7ef3b1be` | higher-order Price/Gaussian covariance response |
| E038 | `research/e038-conditional-gaussian-cov-20260915` @ `8003377936f1f95c154a35b3d9c2bebfe3b81b14` | protocol `06993b1f3fc0670c1e6f2c08ac36e0a6242994b4` | result `665ad6ee0ef4661a2bdb76eb7cf4f0af1c4988d1` | single-Gaussian full-covariance conditional ReLU closure |
| E038 sampling | `research/e038-sobol-trajectory-qmc-20260915` @ `d528ba57fa4fad854a1c6b20115b65662844c087` | protocol `0ac0ef2aeae8dba6c8a758859284e295c420cba3` | result `26894833cce52efd3f2341b9c29a2754f944bbe6` | Sobol/QMC trajectory sampling |
| E039 | `research/e039-halfspace-gaussian-mixture-20260915` @ `b0d3ffe85b3a2c1128fb190ede149ab11f4a2f88` | protocol `c7d96d16e2e75500277d6892a6f8c9c1ac0f5674` | result `7556cdfda8227bfc0ee1936c2a463d48d9c73d2f` | fixed small half-space Gaussian mixture |
| E104 | `research/e104-haar-radial-raoblackwell-20260918` @ `d8e06c806d18b1ccd1405648cf990e0b32d5762f` | protocol `61d5abb0ce7f773fdc05ee5b0ab787a6f2237930` | result `e896296de3c487a88f522d3fca3182645205ef86` | Haar/radial Rao-Blackwell sampling |
| E111 | `research/e111-late4-gaussian-relu-plugin-cost-20260919` @ `9d0dcc429fc4b62a6607ea28c97fbb44327dbaf2` | protocol `08d1068347da04dc94f8f492b00d1c46021c2e25` | result `61f4e243352fe9d7b505777d2503313700af77f0`; terminal receipt `91d8ce0c2314c5356456e05dc646a6630751788d` | exact-small evidence for Gaussian ReLU closure bias |
| E114 | `research/e114-activation-boundary-flux-20260919` @ `b9f64030f65da9b32fc7718d04fb108ee1a73dab` | protocol `81722ba7d928c68e1d12079d22f10ab75b5ac722` | result `4f5df3f8a3c222b7e18f62ac9774902ded58972a`; receipt `f34ea6f233c954cfcc612be8dcd8949e0f6ccd24` | activation-boundary flux representation |
| E119 | `research/e119-generic-boundary-flux-certificate-20260919` @ `a69e542fa8a53708dd581aac47739fc5d8e36955` | protocol `5f0f9c9a4521fd94ebc0f60fff758a5c58cf107b` | result `b31551896b7138309da1cf17fe651674b1a5a9c5`; receipt `0a38d66197f8f817a3954c99850122714a77cce7` | generic boundary-flux state and omission certificate |

This dedupe also enforces the brief's exclusions: no repackaging of Gaussian covariance, small mixtures, cumulants, feed/control calibration, boundary expansion, MLMC/prefix telescopes, or sampling/QMC variants.

## Exactly one literature mechanism screened: characteristic-function positive-part propagation

### Primary sources

1. Iosif Pinelis, **“Characteristic function of the positive part of a random variable and related results, with applications,”** *Statistics & Probability Letters* 106 (2015), 281–286. DOI: https://doi.org/10.1016/j.spl.2015.07.031
2. Iosif Pinelis, **“Positive-part moments via characteristic functions, and more general expressions,”** *Journal of Theoretical Probability* 31 (2018), 527–555. DOI: https://doi.org/10.1007/s10959-016-0709-1 ; author preprint: https://arxiv.org/abs/1603.07365

These are primary mathematical papers. Pinelis gives exact integral representations of the positive part and its moments in terms of the characteristic function.

### Exact scalar formula

For a real random variable (X) with finite first absolute moment and characteristic function

[
phi_X(t)=mathbb E[e^{itX}],
]

the standard (p=1) absolute-moment identity gives

[
mathbb E|X|
=
rac{2}{pi}
int_0^infty
rac{1-operatorname{Re}phi_X(t)}{t^2},dt.
]

Since (X_+=(X+|X|)/2),

[
oxed{
mathbb E[X_+]
=
rac{mathbb E[X]}{2}
+
rac{1}{pi}
int_0^infty
rac{1-operatorname{Re}phi_X(t)}{t^2},dt
}
]

is an exact ReLU-mean formula.

For layer (ell), previous activation vector (H_ell), and next-row (w_j),

[
Z_j=w_j^	op H_ell,qquad
phi_{Z_j}(t)=Phi_{H_ell}(t w_j),
]

where (Phi_{H_ell}(u)=mathbb E[e^{iu^	op H_ell}]) is the **joint** characteristic function. Therefore

[
oxed{
m_{ell+1,j}
=
rac{w_j^	op m_ell}{2}
+
rac{1}{pi}
int_0^infty
rac{1-operatorname{Re}Phi_{H_ell}(t w_j)}{t^2},dt
}
]

for the bias-free network.

This is not a variance-reduction statement. If the required joint-CF values are exact, the neuron mean is exact. If they are approximated with controlled error, the mean error is controlled directly.

### Controlled-error form

For a finite integration window ([delta,T]), quadrature (Q), approximate mean (widehatmu), and approximate joint CF (widehatPhi), one can decompose

[
|widehat m_j-m_j|
le
rac12|widehatmu_j-mu_j|
+
arepsilon_{m small}
+
arepsilon_{m tail}
+
arepsilon_{m quad}
+
rac1pi
int_delta^T
rac{|widehatPhi(tw_j)-Phi(tw_j)|}{t^2},dt.
]

Thus a uniform or integrable CF error certificate becomes a direct mean-error certificate. Squaring and averaging over output neurons gives a direct route to raw final-layer MSE control.

### Why it could, in principle, attack the R333 accuracy target

The formula is global: every output neuron receives the same estimator rule, with no tail routing or per-network tuning. A sufficiently accurate joint-CF state would correct the non-Gaussian positive-part mean itself rather than only changing compute or sampling variance. In principle this is the right type of mechanism for the broad central-bulk error emphasized by the R276/R308 screens.

The problem is not the scalar identity. The problem is the deep state needed to evaluate it.

## Deep propagation obstruction

To use the formula at layer (ell+2), one needs the joint characteristic function of

[
H_{ell+1}=operatorname{ReLU}(Z),qquad Z=W_{ell+1}H_ell,
]

at the future row-ray arguments.

For a generic vector (Z), an exact partition by activation mask gives

[
Phi_{operatorname{ReLU}(Z)}(u)
=
sum_{Asubseteq{1,ldots,n}}
int_{mathcal O_A}
exp!left(i,u_A^	op z_Aight)
,dP_Z(z),
]

where (mathcal O_A) is the sign orthant with active set (A).

That identity exposes the same persistent-state problem as R317/R321:

- an explicit exact realization has up to (2^n) gate regions;
- at (n=1024), explicit mask state is impossible;
- knowing finitely many scalar/marginal characteristic functions does not determine the required joint nonlinear transform;
- a finite set of row-ray CF values is not closed under the componentwise ReLU followed by another generic dense matrix.

The candidate therefore has no new polynomial-size deep recurrence.

## Exhaustive realization check

Every obvious way to make the scalar identity executable falls into an already occupied family:

1. **Estimate (Phi(tw_j)) from input samples.**  
   This is a sampling estimator / QMC variant, occupied by E038-Sobol, E104 and the broader sampling history.

2. **Approximate (H_ell) by one Gaussian and evaluate its CF.**  
   This is E038 single-Gaussian covariance closure; E111 already isolates the resulting post-ReLU representation bias.

3. **Approximate the joint law by a fixed small mixture and sum component CFs.**  
   This is E039 / small-mixture closure.

4. **Compress the joint CF in TT/CP/low-rank/basis/random-feature form.**  
   This is a low-rank/compression descendant already closed as a family by R265/R276/R308 unless a new theorem supplies a generic dense error/state bound.

5. **Evaluate the exact ReLU transform by sign masks, truncated pieces, or activation-boundary integrals.**  
   This is R317/R321 and E114-E119.

So the apparently new Fourier/CF identity does not produce a genuinely unoccupied **deep estimator family** under the project's novelty rule.

## Complexity and Phase-2 feasibility

If an exact joint-CF oracle existed, (K) scalar quadrature nodes per neuron would make the final scalar integrations cheap: roughly (O(L n K)) scalar CF queries plus quadrature.

But there is no such oracle. The cost-dominating operation is updating or querying the **joint** CF after a generic dense ReLU layer.

Known realizations above either:

- carry exponential mask state;
- use stochastic samples;
- collapse to Gaussian/small-mixture approximations;
- or require low-rank/tensor compression without a new generic error theorem.

Therefore R335 cannot derive an honest all-in bound below

[
2^{41}=2{,}199{,}023{,}255{,}552
]

FLOPs, nor a credible residual path below (0.4) s, for width 1024 / depth 16.

A scalar quadrature cost estimate would be misleading because it assumes away the unsolved joint-state update.

## Preregistered target-free falsifier / re-entry gate

No falsifier is executed in R335.

If a future source supplies a **concrete polynomial-size joint-CF closure** that is not sampling, Gaussian/mixture, low-rank relabeling, or explicit mask/boundary enumeration, the first allowed test should be a cheap exact-small target-free fixture:

- generic dense zero-bias ReLU network;
- width 8, depth 4;
- one frozen global configuration;
- exact/high-precision synthetic mean reference only, no contest/public/private targets;
- matched V25-style parent on the same fixture.

Preregistered GO requires **all** of:

1. candidate raw mean-vector MSE (le 0.94	imes) parent raw MSE (a 6% reduction, deliberately just stricter than R333's conditional 5.7579% prioritization target);
2. median per-neuron squared error does not worsen, preventing a tail-only win;
3. a static production extrapolation below (2^{41}) FLOPs/network;
4. an implementation design with no unmetered state operation whose width-1024 residual path lacks a credible (<0.4) s bound;
5. no fallback to the occupied families listed above.

Failure of any gate is NO_GO.

This falsifier is only a re-entry condition. R335 has no concrete non-duplicate closure to test now.

## Decision

**EVIDENCE_BASED_NO_GO / ALREADY_COVERED_AT_DEEP_REALIZATION.**

The positive-part characteristic-function identity is mathematically valid and, at the scalar level, new relative to the project's named mechanisms. It is also accuracy-side: its approximation error directly bounds neuron-mean error and hence raw MSE.

But it does **not** survive the deep-estimator novelty/cost gate. The required joint-CF propagation through generic dense ReLU layers either becomes the already-audited gate/orthant/boundary representation, or is made tractable only by sampling, Gaussian/mixture closure, or low-rank compression already occupied in the ledger.

R335 therefore admits **0 estimator ideas for execution** and makes no claim about any leaderboard participant's method.

## Execution accounting

- code created: **NO**
- estimator implementation: **NO**
- synthetic benchmark/falsifier run: **NO**
- contest benchmark run: **NO**
- dataset/dependency download: **NO**
- GitHub Actions: **NO**
- paid compute: **NO**
- private/holdout/full access: **NO**
- competition submission: **NO**
- participant-method inference from rank/score: **NO**
- main/PR/control/queue edit: **NO**
