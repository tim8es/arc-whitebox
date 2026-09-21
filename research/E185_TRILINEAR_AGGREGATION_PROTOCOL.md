# E185 NEW FRONTIER RESEARCH — exact trilinear-aggregation compiler

Date: 2026-09-22  
Branch: `research/e185-trilinear-aggregation-frontier-20260922`  
Parent: E177 audit commit `e1536d36a5e2d641ab3596892847e2fcf41e83ab`  
Mode: **PROTOCOL / PRIMARY-SOURCE RESEARCH ONLY**  
Status: **ONE HYPOTHESIS FROZEN; NO CODE, NO SCIENTIFIC RUN, NO BASELINE/LEDGER MUTATION**

## 0. Scope firewall

E185 is not an H180 rescue and does not use H180 as scientific ancestry.

Explicitly excluded from the E185 candidate:

- H180 symmetric-CP carrier;
- old-source-only compression;
- low-rank K3, Tucker/CP/TT replacement, CountSketch or MUB projection;
- sampling, QMC, control variates or stochastic correction;
- final-observable-only adjoint;
- AGO-only or E178 higher-order gauge;
- source dropping, age-window rescue, lambda fitting, rank/seed sweeps;
- public submission, scorer or leaderboard mutation.

The E185 candidate keeps the **same estimator state and the same K3/D21
arithmetic** as the parent. It changes only the algebraic schedule used to
evaluate dense matrix products.

## 1. Single retained class and hypothesis

### H185 — exact trilinear-aggregation compilation of the V29 dense kernels

Replace Strassen/classical evaluation of the dominant dense matrix products by
a fixed, target-free **bilinear/trilinear aggregation compiler** using Pan-style
aggregation, uniting, canceling and implicit canceling.

The intended object is not a compressed cumulant carrier. For every semantic
matrix product required by the frozen parent, the candidate must return the
same matrix, up to the predeclared floating-point tolerance. All V29 state
objects remain present:

- young-source A/P legs;
- old-source shared-basis state;
- D3 and D21;
- feedback thin legs;
- covariance/K4-regeneration state;
- birth and final-layer formulas.

Therefore the only admissible gain is **arithmetic rank / operation-count
reduction** of the matrix products themselves.

H185 is deliberately high-risk. The primary literature shows that exact
trilinear aggregation can reduce multiplication rank well below Strassen for
finite, feasible base sizes, but also shows that additive complexity and
leading coefficients can erase the theoretical gain in practice. E185 turns
that uncertainty into a hard cost falsifier before any target-bearing run.

## 2. Primary-source evidence

### 2.1 Pan: trilinear aggregation is an exact algebraic algorithm class

Victor Y. Pan, *New Fast Algorithms for Matrix Operations*, SIAM Journal on
Computing 9(2), 1980, DOI `10.1137/0209027`.

Primary claim used here: aggregation, uniting and canceling construct fast
linear noncommutative algorithms for matrix multiplication, improving on the
Strassen family.

Source:
https://doi.org/10.1137/0209027

### 2.2 Pan 1982: exact finite-size algorithm for arbitrary even n

Victor Y. Pan, *Trilinear aggregating with implicit canceling for a new
acceleration of matrix multiplication*, Computers & Mathematics with
Applications 8(1), 1982, pp. 23-34, DOI
`10.1016/0898-1221(82)90037-2`.

The primary-source abstract states an **Exact Computing** algorithm for
arbitrary even `n` using

`
M_even(n)
 = (n+2) * [ 1.75 (n+2) + (n^2 + 4n + 3)/3 ]
`

essential multiplication steps.

At the Phase-2 width `n=1024`:

`
M_even(1024) = 361,857,033
`

essential multiplications.

With the project unit

`
u = 2 n^3 = 2,147,483,648 FLOPs,
`

the multiplication-only count is

`
M_even(1024) / u = 0.1685028118 u
`

per square product before charging additions, copies, coefficient multiplies,
temporary formation, memory traffic and any flopscope-specific overhead.

This number is **not** used as an all-in cost claim. It only proves that there
is a finite-size exact bilinear-rank regime far below one classical `u`, so
the E185 cost target is not ruled out by multiplication rank alone.

Source:
https://doi.org/10.1016/0898-1221(82)90037-2

### 2.3 Modern feasible-size confirmation and the main warning

Oded Schwartz and Eyal Zwecher,
*Towards Faster Feasible Matrix Multiplication by Trilinear Aggregation*,
arXiv:2508.01748, 2025.

The paper reports trilinear-aggregation algorithms with feasible base cases,
including a `<44,44,44;36110>` scheme and improved bounds for base cases
starting at 28. It also emphasizes the practical obstacle relevant to E185:
small multiplication rank does not imply practical superiority because the
leading/additive coefficient can be large; their work explicitly reduces
additive complexity through sparse decomposition.

Primary source:
https://arxiv.org/abs/2508.01748

### 2.4 Numerical stability is possible in the class, not automatic here

Demmel, Dumitriu, Holtz and Kleinberg,
*Fast matrix multiplication is stable*, arXiv:math/0603207.

They prove normwise stability for a broad class of recursive fast matrix
multiplication algorithms and show that fast multiplication is not
fundamentally incompatible with numerical stability.

This does **not** certify Pan-TA inside V29 at float32. E185 therefore has an
explicit D21/K3 numerical identity gate rather than assuming stability.

Primary source:
https://arxiv.org/abs/math/0603207

### 2.5 ARC/V29 primary implementation evidence

ARC cumulant propagation:

- Wu et al., *Estimating the expected output of wide random MLPs more
  efficiently than sampling*, arXiv:2605.05179.
- reference implementation:
  `alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

Public V29:

- `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- `docs/findings_log.md`, F86;
- `estimators/estimator_v29.py`.

F86 reports steady-state `260.1u` and the grouped anatomy:

- K3 young: `115.6u`;
- K3 old: `106.8u`;
- K3 thin/elementwise: `24.8u`;
- covariance: `7.1u`;
- closure + birth: `5.7u`.

It also states that the young dense tier is already deeply Strassen-priced and
that ordinary pricing polish is not enough. H185 is outside that rejected
class: it changes the bilinear algorithm/tensor rank of the products, not the
Strassen recursion depth of the same bilinear scheme.

## 3. Exact information lower bound

The central H185 distinction is that no cumulant information is discarded.

For width `n`, an arbitrary off-diagonal D21 slice contains exactly

`
N_D21 = n(n-1)
`

independent scalar coordinates before imposing any additional model-specific
structure.

At `n=1024`:

`
N_D21 = 1,047,552.
`

Likewise, a generic fully symmetric order-3 tensor over `n` coordinates has

`
N_sym3 = C(n+2,3)
`

independent scalar coordinates, which at `n=1024` is

`
N_sym3 = 179,481,600.
`

These are algebraic information dimensions, not empirical compression claims.

Consequences for E185:

1. any method claiming exact recovery of arbitrary D21 from fewer than
   `n(n-1)` unconstrained field degrees requires extra structural assumptions;
2. any generic exact K3 compression below `C(n+2,3)` degrees requires a
   restricted tensor family;
3. H185 makes neither assumption: it leaves the V29 factorized K3 state
   untouched and only changes how its required matrix products are evaluated.

Thus H185 preserves the parent information class by construction. A future
implementation that drops, projects, quantizes-to-loss, truncates, sketches or
re-fits state is **not H185**.

## 4. Cost wall and exact cap arithmetic

Phase-2 budget:

`
B = 2^41 = 2,199,023,255,552 FLOPs.
`

Hard project cap:

`
floor(0.135 B) = 296,868,139,499 FLOPs.
`

In F86 units, because `B = 1024u`, the cap is

`
138.24u.
`

The F86 parent is reported at `260.1u`, so the ledger-scale reduction required
from that parent is

`
260.1u - 138.24u = 121.86u.
`

The source ledger is reported to one decimal place, so `121.86u` is a frozen
planning requirement from F86, not a claim of more precision than the source
measurement.

For an intentionally conservative feasibility envelope, retain unchanged the
same `37.6u` remainder used in E180:

`
24.8u thin/elementwise
+ 7.1u covariance
+ 5.7u closure/birth
= 37.6u.
`

Then the transformed dense K3 block has at most

`
138.24u - 37.6u = 100.64u
`

available.

Against the modeled dense K3 bill

`
115.6u + 106.8u = 222.4u,
`

the **necessary average transformed-cost ratio** is

`
r_required <= 100.64 / 222.4
           = 0.4525179856.
`

That is the central E185 cost lower-bound constraint: any compiler whose
all-in transformed dense-kernel bill is more than `45.2518%` of the frozen
modeled bill cannot cross `0.135B`, even before optional integration overhead.

E185 therefore freezes a stricter mechanism gate of

`
r_bundle <= 0.42
`

to reserve roughly `7.23u` of integration headroom relative to the cap model.

The Pan multiplication-only number `0.1685u` shows why `0.42` is not
algebraically absurd; the additive/temporary cost is exactly what the
falsifier must measure.

## 5. Why D21/K3 can be preserved

Every dominant V29 K3 operation ultimately consumes ordinary matrix products:
linear transport of source legs, hub contractions, old-leg reconstruction,
factor rotations/projections and related covariance products.

A bilinear fast matrix multiplication algorithm computes the same map

`
(A, B) -> AB
`

using different linear combinations and fewer scalar product terms.

Therefore, if each substituted product passes the numerical identity gate,
all downstream deterministic functions receive the same state:

`
same A/P/Z/etc.
 -> same D3/D21
 -> same nonlinear births
 -> same K3 history
 -> same K4 regeneration inputs
 -> same final mean
`

up to the frozen floating-point tolerance.

No statistical closure is changed. This is the key reason H185 can preserve
D21/K3 information while attacking a cost wall that representation-compression
methods cannot cross safely.

## 6. Exactly one future falsifier

No code or run is authorized by this artifact.

A future owner may implement **one** target-free mechanism falsifier,
`F185-TA-BUNDLE`, and nothing else before a new authorization.

### Frozen bundle

Use one deterministic synthetic production-shape bundle:

- `n=1024`;
- one fixed PRNG seed, frozen before execution;
- dense matrices with the exact shapes/dtypes of the V29 semantic hot-path
  products selected from:
  - young transport;
  - hub contraction;
  - old-leg reconstruction/shared contraction;
  - join projection/rotation where shape-compatible;
- both parent and candidate consume byte-identical inputs;
- no benchmark targets, no MLP reference means, no scorer.

The candidate is one fixed trilinear-aggregation compilation. No alternate
base case, no recursion-depth sweep, no coefficient search after results.

### Outputs

The falsifier must save:

1. every parent and candidate product output;
2. D3 and D21 obtained by feeding those products through the same frozen V29
   slice algebra;
3. a complete flopscope namespace ledger including additions, coefficient
   multiplies, copies and temporary formation;
4. peak residual time for the bundle;
5. deterministic replay hashes.

### Hard GO gates

All must pass in the sole falsifier:

**A. Algebra / information**

- exact-small symbolic/rational decomposition check: exact equality;
- production float64 product relative Frobenius error `<= 2e-12`;
- D3 relative RMS error `<= 2e-12`;
- D21 off-diagonal relative RMS error `<= 2e-12`;
- deterministic replay: identical hashes.

Any failure: terminal `NO_GO_IDENTITY`.

**B. Cost**

Let `C_parent_bundle` include the same semantic products under the frozen V29
implementation and `C_TA_bundle` include every candidate operation.

Require:

`
C_TA_bundle / C_parent_bundle <= 0.42.
`

Also project the exact measured namespace replacement back onto the frozen F86
ledger and require:

`
C_projected_all_in / B <= 0.135.
`

Either failure: terminal `NO_GO_COST`.

**C. Runtime**

The compiler may not buy billed FLOPs by violating the benchmark residual-time
constraint. The projected integrated implementation must retain a path to
`<= 0.400 s` residual; if the production-shaped bundle alone consumes the
available residual margin implied by the parent measurement, record terminal
`NO_GO_RUNTIME`.

No target-bearing accuracy run is allowed merely because A-C pass; it requires
a separate owner authorization.

## 7. Why this is not ordinary “better engineering”

F86 already rejected a much narrower proposition: deepen Strassen on remaining
lone products. That saved only about `7-10u` and increased residual time.

H185 changes the algebraic multiplication scheme itself.

Pan-style trilinear aggregation can lower bilinear multiplication rank by a
constant factor that is unavailable to “one more Strassen level.” The modern
2025 work confirms this remains a live finite-base algorithmic class while
simultaneously warning that additive complexity is the deciding practical
quantity.

So E185 is falsifiable in exactly the right way:

- if additive/copy overhead leaves `r_bundle > 0.42`, kill it without touching
  benchmark targets;
- if numerical rearrangement corrupts D21 at `2e-12`, kill it;
- only if exact K3 information is retained and the all-in cost model crosses
  `0.135B` does the class deserve an integration experiment.

## 8. Protocol invariants for any successor

A future E185 implementation must freeze before its sole falsifier:

- exact Pan/TA decomposition or generated bilinear coefficient tables;
- all base cases and recursion/blocking decisions;
- shape coverage and fallback policy;
- full cost namespace map;
- floating-point error norms and thresholds;
- source ancestry and hashes.

Forbidden after the run:

- changing a base case;
- selecting a different TA formula;
- dropping “expensive” matrix products;
- rank/source compression;
- switching to approximate matrix multiplication;
- loosening the D21 tolerance;
- rerunning on another seed.

## 9. Research decision

**E185 desk decision: ADMISSIBLE / PROTOCOL-WORTHY, NOT SCIENTIFIC GO.**

The hypothesis is:

> **Keep the full V29 D21/K3 information and cross-source state unchanged, but
> compile its dense matrix products with exact trilinear-aggregation algorithms
> whose all-in measured bundle cost is at most 42% of the frozen parent bundle.**

This class is orthogonal to H180 and to the excluded statistical/compression
lanes. It has primary-source evidence for finite-size exact multiplication rank
well below Strassen, and it has a hard failure mode: additive complexity,
temporary formation or numerical error can immediately make it useless.

No code was created or executed, no scientific experiment was run, and no
baseline, canonical ledger, scorer, submission or leaderboard state was
modified.
