# R352 — tensorized / low-rank Hermite-chaos frontier audit

**Status:** COMPLETE  
**Verdict:** **EVIDENCE_BASED_NO_GO_NO_CERTIFIED_LOW_RANK_TT_HERMITE_PATH**  
**Measurement classification:** **THEORY / PRIMARY-SOURCE DESK AUDIT ONLY — NO NEW ESTIMATOR MEASUREMENT**

Exact base:
`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

Branch:
`review/r352-tensorized-hermite-frontier-20260924`

R352 investigates only the opening explicitly left by R347: a genuinely tensorized / low-rank Hermite-polynomial-chaos state. It does **not** repeat E115 dense total-degree chaos, relabel K3 tensor compression, or run a candidate.

## 1. Dedupe boundary

### E115 / R347 — dense Hermite chaos is closed, tensorized chaos was left open

E115:
- branch `research/e115-hermite-chaos-certified-tail-20260919`
- live head `85552f57c263be172fdceae25fffe278be065680`
- protocol `research/E115_PROTOCOL.md`, blob `a63ac3cdedc6bf8a4948c22b8b907a1333f84f70`
- receipt `research/E115_RESULT_RECEIPT.json`, blob `1f4c10bba845238bd07055c2f423a92c0cdb612a`
- verdict `TERMINAL_NO_GO_DENSE_TOTAL_DEGREE_HERMITE_CHAOS`.

E115's dense total-degree degree-2 basis has 525,825 coefficients and already costs
`2,205,469,900,800` FLOPs for only two favorable late dense transports, above `2^41=2,199,023,255,552`.

R347:
- branch `review/r347-hermite-spectral-mean-estimator-scout-20260924`
- head `53070953bc502b8847f57e235b5ec5e57acf909e`
- report blob `e2d31a3b097904b15de27540ae9af019912324ff`
- receipt blob `9d318ea7e2d9c9727ba9c92f1bc0778d2439cf5a`
- verdict `ALREADY_COVERED`.

R347 explicitly preserves one opening: E115 does **not** rule out a separately specified low-rank/tensorized chaos representation with its own rank-growth/error certificate. R352 addresses exactly that opening.

### Broad prior inventories

The following reports already classify generic labels such as Hermite/chaos, TensorSketch, TT, CP, Tucker/Kronecker and low-rank carriers as heavily occupied, so novelty requires a concrete new state rather than a renamed compression:
- R265 @ `bc287eed95df49fb41d81d157b15471a5aa73a3d`, report blob `e9b5df06173bf70a587774f9374042962847d9e2`;
- R276 @ `a646038b5aceb5428d6583b07525f394f4820c0d`, report blob `4970614c1ac789b008260d726a2bbd5272116434`;
- R308 @ `9c3ef5eefe014e7bdb1a11cc8941999048f6654b`, report blob `e07ddccdf3744c741a571556d7597ac15b460c4b`.

### R317/R321

R317/R321 concern persistent gate-/orthant-conditioned non-Gaussian state:
- R317 head `6ede298753b7ebc35765e18479775879769712ff`;
- R321 head `774aac4105bfe1a171f40f7272fc4267aae6c2f8`.

R321 correctly establishes that one Gaussian orthant query is not inherently exponential. Their blocker is a reusable polynomial-size non-Gaussian state through repeated generic dense ReLU transforms. R352's Hermite coefficient tensor is a different representation, so it is not deduped merely because both avoid a single-Gaussian closure. But it must solve the same composition problem with an explicit rank/error/cost certificate.

### R335/R338

Corrected R335:
- branch `review/r335-accuracy-side-estimator-scout-20260924`
- head `1e233a439b81708353513998898e9f7cfd10caf2`
- corrected report blob `32fcd8e7c43c712aa81b2c0e2f3487f3911d9c23`
- corrected receipt blob `4e7d9523f1b08580358b9f2340f076977e611573`
- verdict `EVIDENCE_BASED_FEASIBILITY_NO_GO`.

That lane propagates characteristic functions / Hilbert-transform information. R352 instead stores Gaussian-Hermite PCE coefficients, so it is not a CF relabel.

### H180 / TT / CP / polynomial-sketch lanes

R352 does **not** reopen these tensor-compression experiments:

1. **E181 H180 symmetric-CP K3 carrier**
   - branch `research/e181-h180-symmetric-cp-carrier-cleanroom-20260921`
   - head `42a85188ebf23f0d0626f81f52b39449150c22d2`
   - protocol blob `555c02b5e3b3cfa1b4782bbb662610a95064cf88`
   - receipt blob `4fa4df934c6a255bfbafd1f8aa16b393ecbc7a6e`
   - production cost passed at rank 3072, but the target-free structural D21 gate failed badly (`0.2626` then `0.4170` relative RMS versus a `0.015` gate).

2. **E148 GSTT-K3 open-core tensor train**
   - branch `research/e148-global-seed-tt-k3-20260921`
   - head `d79eb8e670fbb8ff007283d9ed1eab6dd53a8b35`
   - primary-source note blob `a7a7a8b375eacbe7406f13b78e895f9c693ed4bc`
   - terminal receipt blob `1be554a39bc4ac62a8fdf6d29dcbfa758b84323f`
   - rank-40 production cost upper passed (`256,014,155,776` FLOPs), but the homologous structural carrier lost about 95–99% of D21/D3 norm and closed `GSTT-K3`.

3. **E008 TensorSketch polynomial diagnostic**
   - historical branch `research/e008-polynomial-sketch` @ `d33c546b8ed1495da4a97bb2b1ec84406ca6e333`;
   - persisted result `research/E008_RESULT.md`, blob `dc33cd36b83a4b3c6fbb258b3bd56e438ef6c68b` in later historical lineage;
   - degree-2 TensorSketch old-source reconstruction errors remained orders of magnitude above the required scale.

4. **Tucker / CountSketch / TensorSketch labels**
   are already part of the prior compression inventory; the public V29 symmetric-Tucker attempt is also recorded as a closed K3-carrier direction in E148's primary-source note.

These are neuron/K3/source-carrier or sketch representations. The R352 candidate below is instead a tensor train over the **1024 original Gaussian input coordinates of a Wiener/Hermite PCE**. That is the distinct remaining family.

## 2. Primary sources used

Only primary papers/source are used for the tensor/Hermite claims:

1. **I. V. Oseledets (2011), “Tensor-Train Decomposition,” SIAM J. Sci. Comput. 33(5), 2295–2317.**  
   DOI: https://doi.org/10.1137/090752286  
   Primary SIAM page: https://epubs.siam.org/doi/10.1137/090752286  
   Relevant facts: TT ranks are ranks of unfolding matrices; TT-SVD/rounding has a Frobenius error controlled by unfolding truncation errors; elementwise/Hadamard products multiply TT ranks; standard dense TT-SVD/rounding has complexity \(O(d\,m\,r^3)\) for dimension count \(d\), local mode size bounded by \(m\), and TT ranks bounded by \(r\).

2. **I. Oseledets and E. Tyrtyshnikov (2010), “TT-cross approximation for multidimensional arrays,” Linear Algebra Appl. 432(1), 70–88.**  
   DOI: https://doi.org/10.1016/j.laa.2009.07.024  
   Primary publisher page: https://www.sciencedirect.com/science/article/pii/S0024379509003747  
   Relevant fact: TT-cross can recover/approximate low-rank tensors from selected entries, but its error depends on closeness to low rank and the chosen crosses.

3. **S. Dolgov, B. Khoromskij, A. Litvinenko, H. Matthies (2015), “Polynomial Chaos Expansion of Random Coefficients and the Solution of Stochastic Partial Differential Equations in the Tensor Train Format,” SIAM/ASA J. Uncertainty Quantification 3, 1109–1135.**  
   DOI: https://doi.org/10.1137/140972536  
   Primary SIAM page: https://epubs.siam.org/doi/10.1137/140972536  
   Author manuscript: https://arxiv.org/abs/1503.03210  
   Relevant facts:
   - tensor-product PCE coefficients can be stored in TT/block-TT;
   - storage is `O(M p r^2)`;
   - multiple coefficient tensors can share a block-TT representation;
   - block TT-cross can adapt ranks and has its own algorithm-specific complexity rather than the generic standard-rounding expression used below;
   - crucially, the paper states that `r` is **data-dependent** and that theoretical rank estimates were still under development. Its favorable rank behavior is problem-specific numerical evidence, not a theorem for generic dense ReLU compositions.

4. **S. Goel, S. Karmalkar, A. Klivans (NeurIPS 2019), “Time/Accuracy Tradeoffs for Learning a ReLU with respect to Gaussian Marginals.”**  
   Primary proceedings PDF: https://proceedings.neurips.cc/paper_files/paper/2019/file/067a26d87265ea39030f5bd82408ce7c-Paper.pdf  
   Relevant facts: normalized probabilists' Hermites form the Gaussian orthonormal basis; Claim 1 gives exact univariate ReLU Hermite coefficients; Claim 2 expands a Gaussian ridge ReLU in products of univariate Hermites.

No secondary literature claim is required for the R352 decision.

## 3. Concrete candidate: block-TT tensor-product Hermite/PCE state

Let the original network input be

\[
\xi\sim N(0,I_d),\qquad d=1024.
\]

For layer \(\ell\), represent the full vector-valued activation function

\[
h_\ell(\xi)\in\mathbb R^n,\qquad n=1024,
\]

by its tensor-product normalized-Hermite coefficients, truncated to coordinate degree \(\le p\), stored as one block tensor train:

\[
h_\ell(\xi)
\approx
\sum_{\alpha\in\{0,\ldots,p\}^d}
C_\ell[\alpha,:]\prod_{k=1}^d\bar H_{\alpha_k}(\xi_k).
\]

The output/neuron index is the block dimension. The final mean is simply the zero multi-index coefficient:

\[
\mathbb E[h_\ell(\xi)] = C_\ell[0,\ldots,0,:].
\]

This is a real distinct representation: it is not E115's explicit dense total-degree coefficient table and not a K3 cumulant carrier.

### Dense affine mixing

For zero bias,

\[
z_{\ell+1}(\xi)=W_\ell h_\ell(\xi).
\]

In a block TT this is a linear transform of the output block. It does not, by itself, require increasing latent TT ranks. A bias is only a constant-Hermite contribution and does not alter the basic conclusion.

### ReLU

The nonlinear update

\[
h_{\ell+1}(\xi)=\operatorname{ReLU}(z_{\ell+1}(\xi))
\]

is the hard step.

Two source-backed TT routes exist:

1. approximate ReLU by a polynomial and evaluate products in TT algebra; Oseledets' Hadamard-product rule multiplies exact TT ranks, so rounding/recompression is mandatory;
2. treat the coefficient/function as a black box and use block TT-cross as in Dolgov et al.; ranks are then adaptive/data-dependent.

Neither source supplies a generic rank theorem for repeated generic dense ReLU composition.

## 4. Exact first-layer TT-rank certificate

R352 can do more than merely say “rank is unknown”: already the **first generic dense ReLU layer** has a strong exact-rank requirement in a shared-coordinate block PCE.

Normalize one first-layer row \(a_i\) so \(\|a_i\|_2=1\):

\[
f_i(\xi)=\operatorname{ReLU}(a_i^\top\xi).
\]

Let \(c_k\) be the normalized-Hermite coefficients of univariate ReLU. For even truncation degree \(p\), \(c_p\ne0\), and the degree-\(p\) coefficient slice is

\[
C_i[\alpha]
=
c_p\sqrt{\frac{p!}{\alpha!}}
\prod_{q=1}^d a_{iq}^{\alpha_q},
\qquad |\alpha|=p.
\]

Take any split of latent coordinates \(S|T\), with \(|S|=s\), and place the neuron/output index on the \(T\) side. Split \(\alpha=(\beta,\gamma)\). For every \(j=0,\ldots,p\), restrict the unfolding to

\[
|\beta|=j,\qquad |\gamma|=p-j.
\]

Because output label \(i\) remains in the column index, the row rank of this degree block for generic dense row directions is

\[
\min\left(n,\binom{s+j-1}{j}\right).
\]

Different \(j\) occupy disjoint left- and right-degree sectors, so their ranks add. Hence the exact unfolding rank obeys

\[
r_S
\ge
\sum_{j=0}^{p}
\min\left(n,\binom{s+j-1}{j}\right).
\]

For \(n=1024\), \(s=512\), and \(p\ge2\):

- \(j=0\): rank 1;
- \(j=1\): rank 512;
- every \(j\ge2\): \(\binom{511+j}{j}\ge\binom{513}{2}>1024\), so generic rank contribution is 1024.

Therefore

\[
\boxed{r_{512}\ge 1024p-511.}
\]

This is an exact **generic-dense block-PCE unfolding-rank** statement, not an empirical rank fit.

The location of the output mode cannot avoid all such cuts: wherever that mode is placed in a TT ordering, at least one side contains at least 512 of the 1024 latent coordinates without the output mode; transposing the corresponding unfolding leaves the same matrix rank.

### Scalar carrier comparison

For one generic ridge neuron alone, the analogous two-block Hermite addition formula gives exact bond rank \(p+1\) for even \(p\). The shared 1024-neuron block carrier is much harder: generic row directions make the degree sectors span many independent left polynomials, yielding the \(1024p-511\) bound above.

This argument applies to **exact** coefficient representation. It does not say a low-error approximate TT must have exactly that rank; approximate rank depends on singular-value decay, addressed below.

## 5. Rigorous propagated final-mean error envelope

Use the normalized vector \(L^2\) error

\[
e_\ell
=
\left(
\frac1n\mathbb E\|h_\ell-\tilde h_\ell\|_2^2
\right)^{1/2}.
\]

Let \(\tau_{\ell+1}\) be the normalized \(L^2\) error introduced by the layer-\(\ell+1\) TT/PCE reprojection after applying ReLU to the approximate preactivation.

Because ReLU is 1-Lipschitz,

\[
e_{\ell+1}
\le
\|W_\ell\|_2 e_\ell+\tau_{\ell+1}.
\]

Therefore

\[
e_L
\le
\sum_{k=1}^L
\tau_k
\prod_{j=k}^{L-1}\|W_j\|_2
\]

(with the empty product equal to 1 for the last layer).

By Jensen,

\[
\frac1n
\left\|
\mathbb E[h_L]-\mathbb E[\tilde h_L]
\right\|_2^2
\le e_L^2.
\]

This is a rigorous route from per-layer function-space approximation error to final-mean MSE.

The problem is not validity of the inequality. The blocker is obtaining source-backed \(\tau_\ell\) and rank bounds small enough to satisfy it for generic dense depth-16 networks.

## 6. Exact ReLU Hermite tail: optimistic first-layer certificate already forces huge degree

From Goel–Karmalkar–Klivans Claim 1 and the probabilists' Hermite values at zero, for \(m\ge1\),

\[
c_{2m}^2
=
\frac{1}{2\pi}
\frac{\binom{2m}{m}}{4^m(2m-1)^2},
\]

while \(c_{2m+1}=0\) for \(m\ge1\), \(c_0=1/\sqrt{2\pi}\), and \(c_1=1/2\).

Parseval gives the optimal Gaussian \(L^2\) error of the degree-\(2M\) orthogonal polynomial projection:

\[
T_{2M}
=
\sum_{m=M+1}^{\infty}c_{2m}^2.
\]

R352 evaluated this deterministic series by the stable recurrence

\[
a_0=1,\qquad
a_m=a_{m-1}\frac{2m-1}{2m},\qquad
c_{2m}^2=\frac{a_m}{2\pi(2m-1)^2}.
\]

Checks:
- after degree 2:  
  `T_2 = 0.0112675853621569963466743549412284569...`, matching E115's persisted `0.011267585362156995`;
- at degree 214:  
  `T_214 = 1.34927769247715525935054914194184098e-5`;
- at degree 17,116:  
  `T_17116 = 1.89027113678643304205007617948592579e-8`;
- at degree 17,118:  
  `T_17118 = 1.88993987446720191639112151744281044e-8`.

Thus the **minimum even degree** whose standardized single-ReLU orthogonal-projection \(L^2\) error is at or below the E115 raw target scale `1.89e-8` is

\[
\boxed{p=17,118}.
\]

Interpretation boundary: this is a **sufficient generic function-space certificate scale**, not a theorem that final mean estimation inherently requires degree 17,118. Final means can be less sensitive than full \(L^2\) function error. But without an output-specific sensitivity theorem, the Lipschitz/Jensen envelope above is the defensible target-free propagated bound. Even in the unrealistically favorable case of zero later truncation error and no downstream amplification, its first-layer error budget already requires this degree.

## 7. Rank, memory and FLOP implications at width 1024 / depth 16

### Exact shared block TT at the certificate degree

At \(p=17,118\),

\[
r_{512}\ge 17,528,321,
\qquad
r_{511}\ge17,528,320.
\]

A standard dense TT core adjacent to this bond, with local polynomial mode size \(p+1=17,119\), contains at least

\[
17,528,320\times17,119\times17,528,321
=
5,259,676,132,688,775,680
\]

floating coefficients.

That single core would occupy approximately:
- **21.04 exabytes decimal** at float32;
- **42.04 exabytes decimal** at float64.

This is one core of the first-layer block coefficient tensor, before any depth-16 propagation.

### A much smaller degree is still unattractive

At \(p=214\):
- ReLU \(L^2\) tail is `1.3492776924771553e-5`; the ratio of the stated \(T_{214}\) to the stated certificate scale `1.89e-8` is **713.9035409932038409…×**. This is a function-space certificate ratio, **not** an exact competition-score gap;
- exact generic block bond rank is at least `218,625`;
- neighboring rank is at least `218,624`;
- one standard dense TT core has `10,276,284,480,000` coefficients;
- float32 footprint is **41.105 TB decimal** (about 37.38 TiB).

So even a degree whose local ReLU truncation error is still about three orders of magnitude above target already makes the exact standard block-TT carrier physically large.

### Generic TT arithmetic scale

Oseledets (2011) gives the standard dense TT-SVD/rounding complexity

\[
O(d\,m\,r^3),
\]

where \(d\) is the number of tensor modes, \(m\) bounds the local mode size, and \(r\) bounds the TT ranks. For this PCE scaling illustration, substitute \(d=1024\) and \(m=p+1\), together with the exact generic block-rank bound. This yields only an **illustrative standard-rounding operation-count scale**, not an exact runtime or FlopScope lower bound:

- \(p=2,\ r\ge1537\):  
  \(d(p+1)r^3 \approx 1.1154\times10^{13}\), about **5.07× \(2^{41}\)**;
- \(p=214,\ r\ge218625\):  
  scale \(\approx2.3006\times10^{21}\), about **1.046×10^9 \(2^{41}\)**;
- \(p=17118,\ r\ge17,528,321\):  
  scale \(\approx9.4406\times10^{28}\), about **4.29×10^16 \(2^{41}\)**.

These are not claimed as contest-billed FLOPs or universal runtime lower bounds: the asymptotic expression is a standard dense TT-SVD/rounding scale, its constant and implementation details are not a FlopScope ledger, and the substituted rank is an exact-representation bound rather than an approximate-rank necessity result. They show only that the standard dense-core exact-rank rounding path has no credible Phase-2 cost path at these scales.

A specially structured sparse TT could store the first ridge layer more compactly than dense TT cores. That does **not** rescue R352: such a sparse automaton-like representation is not the Dolgov/Oseledets low-rank block-TT computation model after generic neuron mixing and repeated ReLU, and no primary source located here gives its depth-16 rank-growth, truncation-error, and production-cost theorem.

## 8. Could approximate TT / block TT-cross rescue the exact-rank wall?

This is the only plausible escape.

Oseledets' TT-SVD framework controls tensor approximation error by discarded unfolding singular values. Dolgov et al. use block TT-cross to adapt ranks from sampled tensor values.

But the required theorem is missing:

1. Dolgov et al. explicitly call TT rank **data-dependent** and state that theoretical estimates were under development.
2. TT-cross quality depends on the target being close to a low-rank tensor and on cross selection; Oseledets–Tyrtyshnikov do not prove low ranks for generic deep dense ReLU PCEs.
3. ReLU is non-smooth. Nothing in the cited PDE experiments implies a rank-decay bound for a 16-layer generic dense ReLU composition.
4. Polynomial evaluation inside TT is not free: Oseledets shows Hadamard-product ranks multiply before rounding.
5. A per-layer TT truncation tolerance alone is insufficient: R352 needs the weighted propagated sum \(\sum_k\tau_k\prod_{j>k}\|W_j\|_2\) below the final-mean tolerance.
6. No primary source located supplies, for this network class, all of:
   - a shared block-TT rank bound \(r(p,\ell)\);
   - computable per-layer \(L^2\) truncation residuals under ReLU;
   - a depth-16 propagated final-mean MSE certificate;
   - a resulting all-in \(<2^{41}\) FLOP and credible residual-time path.

Therefore choosing a small rank such as 16, 32, 64, or 128 would be an empirical hyperparameter guess. Under R352's no-run protocol there is no evidence-based way to certify one.

## 9. Decision

The low-rank/tensorized Hermite possibility is now narrowed to a concrete object rather than dismissed by analogy:

> **Block-TT tensor-product Hermite/PCE over the original Gaussian coordinates, with affine mixing on the output block and rank-controlled ReLU reprojection.**

It is mathematically coherent and distinct from E115, E148/E181 and R317/R335.

However, **no specific rank/error/cost path survives the desk gate**:

- exact block TT has a provable large first-layer rank for generic dense weights;
- the generic \(L^2\)-to-final-mean certificate requires very high Hermite degree even before depth amplification;
- standard dense-core TT storage/rounding at those ranks is far beyond Phase-2 scale;
- low-rank approximation/TT-cross could only help if unfolding spectra decay rapidly, but no primary theorem establishes that for generic dense depth-16 ReLU PCEs or converts the adaptive TT residual into the required final-mean MSE and contest cost bounds.

Therefore:

**R352 = EVIDENCE_BASED_NO_GO_NO_CERTIFIED_LOW_RANK_TT_HERMITE_PATH.**

This is **not** a universal impossibility theorem for tensorized Hermite methods. It says the unclosed R347 lane does not currently contain an auditable candidate that simultaneously has a source-backed rank bound, propagated final-mean error bound, and production cost path.

### Re-entry condition

A future non-duplicate task would need, before implementation:

1. a common-coordinate or composably adaptive-coordinate tensorized Hermite state;
2. a theorem or exact certificate bounding approximate TT ranks through generic dense affine mixing + ReLU;
3. computable per-layer \(L^2\) truncation residuals;
4. a rigorous composition of those residuals into final-mean MSE;
5. an all-in width-1024/depth-16 cost/memory/residual bound below the Phase-2 envelope.

Without those items, a rank choice would be experiment-driven method fishing rather than a theory-admitted R352 successor.



## R364 append-only correction from R361 independent review

R364 preserves the original R352 commit `4e46b2bd8d04c15270b40872101555b6ac77f3e7`, report blob `6f25841331f0199bd6ee7966a4bda796d79d2c59`, and receipt blob `432737e41f2b3576d1b5192a01a177c799c58d3b` as immutable history and applies only the three nonmaterial corrections identified by completed R361 (`review/r361-r352-independent-math-redteam-20260924` @ `4a99ea885d0a66141af823cd308770d66b8f8245`; report blob `d4797eb6075f84731679eab15a4f343c98d8f478`; receipt blob `f1c0951a382a195a367c01cddc850a9c55537aec`).

1. **Complexity source:** standard dense TT-SVD/rounding `O(d*m*r^3)` is attributed to Oseledets 2011. Dolgov et al. remains the source for PCE-in-TT storage, block-TT-cross/adaptive ranks, and the explicit data-dependent-rank caveat. The substituted scales remain illustrative and are not exact FlopScope/runtime lower bounds.
2. **Exact large integers:** the current JSON receipt stores the p=17,118 dense-core exact counts as decimal strings verified by exact multiplication:
   - entries: `5259676132688775680`;
   - float32 bytes: `21038704530755102720`;
   - float64 bytes: `42077409061510205440`.
   The original rounded JSON numeric values are retained only inside the correction history as superseded values.
3. **p=214 ratio:** current value is `713.9035409932038409...`, defined only as the ratio of the stated `T214` to the stated `1.89e-8` function-space certificate scale. It is not a competition-score gap.

No other R352 mathematical claim, historical verdict, candidate definition, rank statement, error-envelope qualification, or execution accounting is changed.

## 10. Execution accounting

- new estimator implementation: **NO**
- synthetic run: **NO**
- official/public benchmark run: **NO**
- dataset/dependency download: **NO**
- GitHub Actions: **NO**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submission: **NO**
- leaderboard access/edit: **NO**
- R320 edit: **NO**
- PR/main/control/queue edit: **NO**
- historical verdicts changed: **NO**
- R352 branch artifacts: exactly report + JSON receipt
