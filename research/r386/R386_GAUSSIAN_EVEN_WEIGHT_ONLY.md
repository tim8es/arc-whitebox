# R386 — Gaussian-even weight-only signed cosine/ridge audit

**Status:** COMPLETE  
**Verdict:** **NARROW_NO_GO_MISSING_WEIGHT_TO_CONTROLLED_COSINE_MEASURE**  
**Mode:** theory/static research only; no benchmark tensors, no estimator/scorer run, no downloads or installs  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `research/r386-gaussian-even-weight-only-20260925`

## 1. Question and result

R380 identified the correct structural escape from its one-hidden-layer odd-part obstruction. For a zero-bias ReLU network `f`, positive homogeneity gives `f(r u)=r f(u)` for `r>=0`, and Gaussian symmetry gives

`E[f(X)] = E[f_even(X)]`, where `f_even(x)=(f(x)+f(-x))/2`.

The question here is deliberately narrower than R380:

> Can the **Gaussian-even projection only** be converted deterministically and directly from the known deep weights `W` into a finite signed cosine/ridge expansion, without evaluating/fitting `(x,f_W(x))` samples, with an explicit finite-width error certificate and all-in Phase-2 cost?

**Answer:** existence/approximation theory says **yes at the function-class level**, and gives a precise conditional finite-width construction once a controlled signed cosine measure is already known. It does **not** supply the required direct `W -> measure/coefficients` algorithm. The missing bridge is now sharper than in R380:

> From the deep weight stack alone, compute a finite-variation vector signed measure `nu_W` (or an equivalent finite coefficient object) representing/approximating `f_even|S^(1023)`, with a computable variation/error bound and bounded construction complexity, without function-sample fitting and without exhaustive activation-region enumeration.

No primary source located proves that bridge for deep ReLU weights, and the known exact white-box decomposition has exponential worst-case activation-pattern cost. Therefore R386 remains a **narrow no-go**, not a claim that even-projection shallow approximation is impossible.

## 2. Dedupe / inherited facts

R386 reread:

- R366 report, blob `f2c512a04c1eb9b0d179cd04a5563e34a6f109aa`;
- R373 receipt, blob `f324c56a35b8c6f4144110593f52e7b346eb6d4e`;
- R375 report, blob `45b69554fd53b9323b894fb391b5b9c334285c22`;
- R380 report, blob `5f9bd8b15936947ea0de67377fb950c6aebd5c49`;
- `research/history.json` on exact main, blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`.

Repository search on main found no prior artifact matching `cosine transform`, `Gaussian-even`, `signed cosine`, `ridgelet`, or `R386`. R386 therefore does not reopen sampled regression, QMC/cubature, Hermite/TT, characteristic-function, or activation-boundary families.

Inherited corrections are preserved:

1. R366's analytic readout for an existing shallow surrogate is valid.
2. R373: a population-mean certificate does **not** prove error to the fixed baked Mini target.
3. R375: a future frozen target-free candidate could later be evaluated directly against public Mini labels, but that is a separate development measurement.
4. R380: `g(x)-g(-x)=ABx` blocks general whole-function one-hidden bias-free approximation, but the odd mismatch integrates to zero under centered Gaussian input.

## 3. Exact Gaussian-even reduction

Let input dimension `d=1024`, `X~N(0,I_d)`, and write

`X = R U`,

where `U` is uniform on `S^(d-1)`, `R=||X||_2`, and `R` and `U` are independent.

A zero-bias ReLU network is positively 1-homogeneous, so

`f(X)=R f(U)`.

Define

`h(U)=f_even(U)=(f(U)+f(-U))/2`.

Because `U` and `-U` have the same law,

`E[f(X)] = E[R] E_U[h(U)]`.

For `d=1024`,

`E[R] = sqrt(2) Gamma((d+1)/2)/Gamma(d/2) ≈ 31.9921884548`,

and `E[R^2]=d=1024`.

Thus the population-mean problem can be reduced exactly to integration of the continuous even function `h` on the sphere. This removes R380's nonlinear odd component from the mean problem.

## 4. Signed cosine representation: what existence theory actually gives

For an even finite signed measure `nu` on projective space / the sphere, define the cosine transform

`H nu(x) = integral |<u,x>| d nu(u)`.

Breiding et al., *The zonoid algebra, generalized mixed volumes, and random determinants*, Advances in Mathematics 2022, Definition 2.25 and Theorem 2.26, prove that the cosine transform on signed even measures is injective and that its image is dense in the continuous even functions.

Primary source: https://doi.org/10.1016/j.aim.2022.108361

Therefore for each continuous even scalar component `h_k` and every `epsilon>0`, there exists a signed measure `nu_{k,epsilon}` such that `H nu_{k,epsilon}` approximates `h_k` uniformly. Finite atomic measures can in turn approximate such integral representations.

This is an **existence/density statement**. It does not provide:

- `nu` from deep weights;
- a bound on `||nu||_TV` in terms of the deep weights/path norms;
- a numerical `epsilon -> m` constant for arbitrary `h`;
- construction FLOPs/workspace.

The distinction is decisive because the inverse cosine transform is not a bounded inverse from all continuous even functions to finite signed measures: Theorem 2.26 states dense image, not surjectivity onto all of `C(P^(d-1))`.

## 5. Conditional constructive transform if a controlled measure were already available

This section isolates exactly what would become constructive **after** the missing `W -> nu` step.

Suppose the vector even projection has a finite-vector-measure representation

`h(x)= integral |<u,x>| d nu(u)`,

where the polar decomposition of `nu` has total variation `V=||nu||_TV<infinity`.

For a finite atomic approximation

`nu_r = sum_{j=1}^r a_j delta_{u_j}`, `u_j in S^(d-1)`, `a_j in R^1024`,

define

`h_r(x)=sum_j a_j |u_j^T x|`.

Using

`|t| = ReLU(t)+ReLU(-t)`,

this is exactly a bias-free one-hidden ReLU network with **2r hidden units**:

`h_r(x)=sum_j a_j ReLU(u_j^T x)+sum_j a_j ReLU(-u_j^T x)`.

Hence a finite signed cosine expansion immediately supplies the requested `(A,B)` by pairing every direction `u_j` with `-u_j` and duplicating output coefficient `a_j`.

### Analytic Gaussian readout

For unit `u_j`,

`E|u_j^T X| = sqrt(2/pi)`.

Therefore

`E[h_r(X)] = sqrt(2/pi) sum_j a_j`.

For non-unit directions the term is `sqrt(2/pi) a_j ||u_j||_2`.

No independence between ridge activations is required.

## 6. A real finite-r certificate — conditional on controlled variation

The missing algorithm should not be confused with the finite-width sparsification step. Once a finite-variation measure is known, standard Hilbert-space sparsification gives an explicit rate.

Take the Hilbert space `L2(S^(d-1);R^1024)`. For unit `u`,

`|| |u^T(.)| ||_L2^2 = E_U[(u^T U)^2] = 1/d`.

Applying the Maurey/Jones/Barron empirical-method argument to the polar decomposition of a vector signed measure yields existence of an `r`-atom deterministic expansion satisfying

`||H nu - H nu_r||_L2(S)^2 <= V^2/(r d)`.

A modern primary approximation source stating the corresponding variation-space `m^(-1/2)` Hilbert bound is Siegel et al., *Optimal Approximation of Zonoids and Uniform Approximation by Shallow Neural Networks*, Constructive Approximation (2025).

Primary source: https://doi.org/10.1007/s00365-025-09712-9

That paper also proves, for a **given** probability measure in the absolute-value/zonoid setting, a stronger uniform finite-support rate

`sup_x |H tau(x)-H tau_r(x)| <= C(d) r^(-1/2-3/(2d))`,

but `C(d)` is dimension-dependent and the theorem starts from the measure `tau`; it does not recover `tau` from a deep network.

For the Hilbert certificate above, Gaussian homogeneity gives

`E||h(X)-h_r(X)||^2 = d ||h-h_r||_L2(S)^2 <= V^2/r`.

Therefore Jensen gives the vector population-mean certificate

`||E f(X)-E h_r(X)||_2^2 <= V^2/r`.

Dividing by 1024 output coordinates,

`MSE_population_mean <= V^2/(1024 r)`.

This is a concrete finite-`r` certificate **if** a representation with known `V` is already available.

It does not solve R386 because neither `nu_W` nor a usable `V(W)` is supplied by the density theorem.

## 7. Why the published constructive harmonic/ridgelet routes do not fill the gap

### 7.1 Mhaskar zonal-function construction

H. N. Mhaskar, *Function approximation with zonal function networks with activation functions analogous to the rectified linear unit functions*, Journal of Complexity 51 (2019), studies networks built from `|x dot x_j|`-type zonal atoms and proves approximation rates for smoothness classes.

Primary source: https://doi.org/10.1016/j.jco.2018.09.002

Crucially for R386, the paper's centers may be target-independent but the coefficients are **linear combinations of training data**. Applying the construction by evaluating `f_W` on a deterministic sphere set is still a function-sample/cubature fit. It is not a direct algebraic map from deep weights to coefficients.

### 7.2 Sonoda–Murata ridgelet reconstruction

Sonoda and Murata, *Neural network with unbounded activation functions is universal approximator*, Applied and Computational Harmonic Analysis 43(2), 2017, derive reconstruction formulas using ridgelet/Radon/Fourier machinery and note that a network can be obtained by discretizing the ridgelet transform under their admissibility conditions.

Primary source: https://doi.org/10.1016/j.acha.2015.12.005

This is constructive from a **target function / its transform**, not from the parameter list of an arbitrary deep ReLU network. To use it weight-only, one still needs to compute the required Radon/ridgelet transform of the deep CPWL function from `W`. No cited theorem bounds that operation for the ARC architecture.

### 7.3 Exact CPWL white-box route

Villani and Schoots, *Any ReLU Network Is Shallow*, ECAI 2025 proceedings, give an exact algorithm from a deep ReLU network to all local linear models and an exact three-hidden-layer representation.

Primary source: https://journals.sagepub.com/doi/10.3233/FAIA251170

Their algorithm searches activation patterns and has stated worst-case complexity

`O(2^(sum_l n_l))`.

For ARC, `sum_l n_l=16*1024=16384`, so the unreduced pattern space is `2^16384`. This is a genuine weight-only path to a full polyhedral description, after which one could in principle attempt spherical/Radon/cosine integration region by region. It is not Phase-2 feasible and supplies no polynomial ARC-scale bound.

Therefore the available choices are:

1. **function evaluations/training data** -> coefficients: constructive but disallowed sampled/cubature fitting;
2. **activation-region enumeration** -> exact CPWL description -> transforms: weight-only but no viable cost bound;
3. **cosine/ridge density theorem**: existence, but no coefficient recovery algorithm.

No fourth primary-source bridge was found.

## 8. Depth-separation warning: density does not imply affordable width

Eldan and Shamir, *The Power of Depth for Feedforward Neural Networks*, COLT 2016, prove an approximately radial (hence essentially even) function representable by a small deeper network for which a two-layer approximant requires exponential width for constant accuracy.

Primary source: https://proceedings.mlr.press/v49/eldan16.html

This theorem is not an ARC-instance lower bound and its network/function assumptions should not be transferred mechanically to the exact zero-bias ARC ensemble. It does, however, rule out the inference “even + continuous + deep-network-generated => automatically efficient shallow approximation.” A usable ARC theorem must control the relevant cosine/variation norm or width from the actual weight structure.

## 9. Phase-2 resource bound

Official current Phase-2 documentation fixes:

- input/output width: `1024`;
- depth: `16`;
- per-MLP FLOP budget: `B=2^41=2,199,023,255,552`;
- score-floor threshold: `0.1B`, i.e. integer `F<=219,902,325,555`;
- per-`predict()` wall cap: `120 s`;
- residual wall cap: `0.4 s`;
- solution-process memory limit: `8 GB`;
- grading-server single-array cap: `4 GiB = 4,294,967,296 bytes`.

First-party sources:

- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/getting-started/stage-3-run-local.md
- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/score-report-fields.md
- https://github.com/AIcrowd/whestbench/blob/main/CHANGELOG.md
- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/troubleshooting/common-participant-errors.md

### Explicit paired-ReLU storage

An `r`-atom signed cosine expansion becomes `m=2r` ReLU units.

With float32 coefficients:

- `A`: `1024 x 2r` -> `8192r` bytes;
- `B`: `2r x 1024` -> `8192r` bytes;
- total explicit `A+B`: `16384r` bytes.

The 4-GiB single-array cap alone gives

`r <= 524,288`

for either dense `A` or `B`. At that value `A+B` already occupies exactly 8 GiB, leaving no memory for the original ~64 MiB weight stack, output, runtime, or construction workspace. Thus actual feasible `r` is strictly smaller. If the documented “8 GB” process limit is enforced as decimal rather than binary capacity, the coefficient-only total ceiling is smaller still; R386 does not assume an undocumented byte interpretation.

### Direct cosine storage/readout

If an estimator stores the `r` unit directions and vector coefficients directly, without physically duplicating `+u/-u`, the two dense float32 matrices cost

`8192r` bytes total.

The analytic readout needs only the coefficient sum for unit directions; if norms must be computed, leading work is about

`2*1024*r + 2*1024*r = 4096r`

scalar FLOPs for direction norms plus vector accumulation, before construction/certification overhead.

Readout-only, the 10%-budget floor would allow roughly

`r <= floor(219,902,325,555 / 4096) = 53,687,091`,

so memory binds far earlier than readout FLOPs.

For the explicit paired `A,B` form, leading generic readout accounting is about `8192r` FLOPs, giving a readout-only floor ceiling `r<=26,843,545`; again memory binds first.

**But neither number is an all-in candidate bound.** The unknown term is the cost/workspace of `W -> nu -> {a_j,u_j}` plus certification. With no such algorithm, `C_transform` is unbounded/UNKNOWN and Phase-2 feasibility is not established.

## 10. Population certificate is not a Mini certificate

The conditional bound

`MSE_population_mean <= V^2/(1024 r)`

is about `E[f(X)]`.

R373 already established that the fixed Phase-2 Mini target is a baked `N=1e9` Monte-Carlo target, not the exact mathematical population mean. Therefore this certificate alone does **not** prove Mini scorer improvement.

R375 supplies the correct separation: if a target-free `W -> coefficients` candidate is ever frozen, a later separately authorized public-development run can score its predictions directly against the fixed Mini labels. R386 neither accesses those labels nor performs that measurement.

## 11. Exact missing theorem / algorithm

A sufficient re-entry theorem would have to state, for every supplied ARC deep zero-bias weight stack `W` (or for the explicitly defined He-Gaussian ARC ensemble with a quantified success event), an algorithm

`C(W,epsilon) -> {(a_j,u_j)}_(j=1)^r`

such that:

1. **weight-only:** it reads `W` and fixed constants only; no `f_W(x_q)` evaluation set is used to fit coefficients;
2. **even target:** `h_W(u)=(f_W(u)+f_W(-u))/2`;
3. **finite error:** it proves, for example,
   `||h_W - sum_j a_j |u_j dot .|||_L2(S) <= epsilon`;
4. **controlled variation/width:** it gives explicit `V(W)` and `r(W,epsilon)` (or a direct width bound), not only density;
5. **bounded construction:** it gives explicit FLOPs, peak single-array size, process memory, wall and residual-time complexity;
6. **ARC feasibility:** those bounds fit `2^41`, 8 GB, 4 GiB/array, 120 s and 0.4 s.

The primary literature checked proves pieces after assuming a target function or a cosine measure. It does not prove this composition from deep weights.

## 12. Cheapest falsifier for any proposed bridge

The cheapest falsifier is static, exact, target-free, and requires no benchmark data.

Use a small symbolic zero-bias deep ReLU fixture, e.g. input dimension 2 or 3 and depth 3, chosen so that depth creates several activation cones. Because the fixture is tiny, independently enumerate its exact conical linear regions and compute the even restriction on the unit circle/sphere.

A proposed `W -> coefficients` algorithm must, **without querying fitted `f_W(x_q)` samples**:

1. emit its signed atoms `(a_j,u_j)`;
2. emit `r`, claimed `V`, and exact operation/workspace formulas;
3. verify its claimed sphere `L2`/uniform error against the exact conical reference;
4. verify the analytic mean `sqrt(2/pi) sum_j a_j`;
5. symbolically extrapolate its complexity formula to `d=1024,L=16`.

Immediate NO-GO if coefficient recovery secretly requires a target evaluation grid, if exact recovery requires unbounded activation-pattern enumeration, if `V(W)` is absent, or if `r/C_transform/workspace` cannot be bounded before Mini access.

This falsifier targets exactly the missing bridge rather than retesting cosine-transform density.

## 13. Verdict

R386 narrows R380's open point substantially.

- **Existence/density:** YES. Signed cosine transforms are dense in continuous even spherical functions.
- **Finite-r sparsification given a controlled measure:** YES. A finite-variation representation admits an `O(V/sqrt(r d))` sphere-`L2` finite-atom existence bound, yielding a conditional Gaussian population-mean certificate.
- **Analytic readout:** YES. `E|u^T X|=sqrt(2/pi)||u||`.
- **Direct deterministic deep-weight -> controlled measure/coefficients:** **NOT ESTABLISHED**.
- **All-in Phase-2 construction cost:** **NOT ESTABLISHED**.
- **Mini improvement from population certificate:** **NO**.

**Final verdict: `NARROW_NO_GO_MISSING_WEIGHT_TO_CONTROLLED_COSINE_MEASURE`.**

The result is intentionally narrower than “no shallow even approximation exists.” The exact missing proof is a bounded-complexity, weight-only recovery of a finite-variation signed cosine/ridge representation (or equivalent coefficients) from the deep ARC weights.

## 14. Execution accounting

- Mini/public/private/holdout/full benchmark tensors accessed or downloaded: **0**
- estimator/benchmark/scorer/synthetic numerical runs: **0**
- dependency installs: **0**
- GitHub Actions: **0**
- submissions: **0**
- paid resources: **0**
- R320/main/PR/control/queue edits: **0**
- R386 artifact: **this cited Markdown report only**
