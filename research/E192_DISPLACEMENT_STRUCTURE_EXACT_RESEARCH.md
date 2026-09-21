# E192 ORTHOGONAL RESEARCH — exact displacement-structure class

Date: 2026-09-22  
Branch: `research/e192-displacement-structure-exact-20260922`  
Clean parent: E177 `e1536d36a5e2d641ab3596892847e2fcf41e83ab`  
Mode: **PROTOCOL / PRIMARY-SOURCE RESEARCH ONLY**  
Execution: **NO CODE, NO SCIENTIFIC RUN, NO BENCHMARK, NO BASELINE/LEDGER MUTATION**

## 0. Decision

Exactly one new exact class was investigated:

> **H192 — exact low-displacement-rank (LDR) / Toeplitz-like generator
> representation of the dense matrices used by V29, with exact structured
> multiplication replacing ordinary dense products.**

This class is mathematically exact when the displacement generators are exact:
it changes neither K3/D21 state nor closure equations.

**Desk decision: TERMINAL STRUCTURAL NO-GO for the actual dense random-MLP
law. No owner run is authorized.**

Two independent pre-run obstructions kill the class:

1. for the standard Stein/Toeplitz displacement, an iid continuous Gaussian
   weight matrix has displacement rank `n` almost surely, so the exact compact
   generator degenerates to full size;
2. even granting zero cost to every weight-structured operation, V29 namespaces
   that do not expose the layer weight as the structured operand already sum to
   at least `148.31u > 138.24u`.

Therefore E192 found no admissible exact displacement-structure route to
`<=0.135B`. The falsifier below is retained only as a reproducible certificate
scheme; it must not be run under this protocol because the analytic cost gate
already fails.

## 1. Separation from excluded classes

H192 is not:

- H180 symmetric CP / Waring K3;
- H185 trilinear aggregation or a new bilinear-rank formula;
- low-rank K3, Tucker, TT or source-rank truncation;
- CountSketch, MUB, TensorSketch or any randomized projection;
- sampling, QMC, control variate or stochastic correction;
- AGO / gauge transport;
- final-observable adjoint;
- source-age / old-tier / young-tier compression.

The state and estimator equations are unchanged. The only proposed change is
to represent an **exact dense matrix** by an exact displacement generator and
use the corresponding exact structured linear algebra.

No basis is fitted to targets. No approximate generator truncation is allowed.
Allowing truncation would leave the exact class and is explicitly outside H192.

## 2. Primary-source basis

### 2.1 Kailath–Kung–Morf: displacement rank

T. Kailath, S.-Y. Kung, M. Morf,
*Displacement ranks of matrices and linear equations*,
Journal of Mathematical Analysis and Applications 68(2), 1979, 395–407,
DOI `10.1016/0022-247X(79)90124-0`.

Primary source:
https://doi.org/10.1016/0022-247X(79)90124-0

The paper introduces displacement rank as the measure of closeness to Toeplitz
structure and derives fast exact algorithms when that rank is small.

For the down-shift matrix `Z`, use the Stein displacement

`Delta(A) = A - Z A Z^T`.

If `rank(Delta(A)) = alpha`, write exactly

`Delta(A) = G H^T`, with `G,H in R^(n x alpha)`.

The classical recovery formula gives an exact sum of `alpha` products of
lower/upper triangular Toeplitz matrices. Thus exact low displacement rank is
an algebraic representation, not an approximation.

### 2.2 Exact generator recovery / structured multiplication

E. Kaltofen,
*Analysis of Coppersmith's block Wiedemann algorithm for the parallel solution
of sparse linear systems*, Mathematics of Computation 64, 1995, contains the
standard `phi+(A)=A-ZAZ^T` formulation and the exact Sigma-LU recovery:

`A = sum[j=1..alpha] L(g_j) U(h_j^T)`.

Primary PDF:
https://kaltofen.math.ncsu.edu/bibliography/95/Ka95_mathcomp.pdf

This representation stores `O(alpha*n)` field elements and reduces products
to Toeplitz/polynomial products when `alpha << n`.

### 2.3 Modern exact complexity statement

A. Bostan, C.-P. Jeannerod, C. Mouilleron, E. Schost,
*On Matrices With Displacement Structure: Generalized Operators and Faster
Algorithms*, SIAM J. Matrix Analysis and Applications 38(3), 2017, 733–775,
DOI `10.1137/16M1062855`.

Primary sources:
https://doi.org/10.1137/16M1062855
https://arxiv.org/abs/1703.03734

They formulate basic structured operations in terms of a matrix of displacement
rank `alpha` and give exact arithmetic costs ranging from classical
`O(alpha^2 M(n))` to `O(alpha^(omega-1) M(n) log n)`, depending on the
operator class. The speedup premise is therefore explicitly **small exact
displacement rank**.

### 2.4 ARC / V29 state to be preserved

Official ARC implementation:
https://github.com/alignment-research-center/mlp_cumulant_propagation

Pinned public V29:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Pinned V29 namespace source:
`estimators/estimator_v29_ns.py@f91df783b83cb5fae0af57a16799c5df81891bd2`

Pinned F86 steady-state log:
`docs/audit_v29_ns_d0.log@a689ef69fd64bed7765cb93ce4910c3fedcbd04a`.

The source-resolution reconciliation frozen later in E187 is:

- total: `260.06u`;
- dense K3: `222.44u`;
- fixed remainder: `37.62u`;
- cap: `138.24u = 0.135B`.

H192 does not mutate that ledger.

## 3. Exact preservation claim

If every substituted matrix `A` is represented by an exact generator
`Delta(A)=GH^T`, the Sigma-LU reconstruction equals the same `A` over the
base field. Therefore structured multiplication computes the same semantic
product `A X` (or `X A`) algebraically.

Consequently H192 does not compress K3:

`same dense matrices -> same A/P/Z/Q/etc. -> same D3/D21 -> same K3 history`.

The exact-information gate is therefore simple:

- no generator truncation;
- no singular-value thresholding;
- no approximate Toeplitz fit;
- no learned displacement operator;
- no target-informed basis.

Any of those would be a different hypothesis.

## 4. Structural lower bound I — Gaussian weights have full Stein displacement rank

Let `Z` be the nilpotent one-step down-shift, so `Z^n=0`, and define

`L(A)=Z A Z^T`,
`Delta=I-L`.

Because `L^n=0`,

`Delta^{-1} = I + L + L^2 + ... + L^(n-1)`.

Hence `Delta` is an invertible linear map on the `n^2`-dimensional matrix
space.

Under the actual idealized MLP law, a weight matrix `W` has iid Gaussian
entries and therefore an absolutely continuous density on `R^(n^2)`.
An invertible linear map preserves absolute continuity, so `Delta(W)` is a
generic absolutely continuous `n x n` matrix.

The determinant polynomial is not identically zero; its zero set has Lebesgue
measure zero. Therefore

`rank(Delta(W)) = n` almost surely.

At Phase-2 width:

`alpha = n = 1024` almost surely.

This is an exact structural obstruction. The compact generator requires
`2*n*alpha = 2*n^2` scalars at full rank and loses the `alpha << n`
premise on which the primary-source fast algorithms depend.

Important finite-precision caveat: the benchmark stores finite floating-point
weights, so "almost surely" is not itself a receipt for one concrete fixture.
A future falsifier would compute the exact rank of the dyadic-float
displacement. This does not rescue the protocol because the independent cost
lower bound below already fails before such a run.

## 5. Structural lower bound II — zero-cost structured-weight oracle still misses the cap

The V29 steady-state family ledger exposes large D21/K3 contractions whose
operands are current cumulant/source state, not the layer weight matrix.

The following namespaces are directly confirmed from the pinned
`estimator_v29_ns.py` implementation to be state/state or factor/state
operations:

| namespace | F86 units | semantic operation |
|---|---:|---|
| `hub` | 54.90 | `LA A^T + LP P^T` fused D21 hub |
| `shared` | 27.91 | old-source inner contractions and trailing `Qc^T` |
| `old_legs` | 27.89 | `Qc F` / `(Qc U) F` leg formation |
| `fb` | 11.45 | V18 feedback thin/state D21 contractions |
| `j_rot` | 9.14 | old-factor/core rotation |
| `j_proj` | 7.50 | `Qn^T Aj/Pj` |
| `j_tier2` | 6.70 | nested tier factor-space operations |
| `j_core` | 2.82 | joined source core formation |
| **lower bound** | **148.31u** | |

These eight namespaces alone give

`C_nonweight_LB = 148.31u`.

Hard cap:

`C_cap = 138.24u`.

Therefore even an impossible oracle that makes **every other operation in V29
free**, including all direct `W @ X`, `X @ W^T`, covariance, thin transport,
range-finder use of weight slices, closure, births and bookkeeping, still has

`148.31u - 138.24u = 10.07u`

of unavoidable cost under a **weight-only** displacement-structure
interpretation.

This is a stronger cost NO-GO than merely observing full displacement rank.

Could H192 instead declare all A/P/Q/state matrices displacement-structured?
Only if their **exact** displacement ranks are small. That does not evade
Section 4: the chain is driven by generic dense Gaussian weights, and even the
first required weight operator already has full Stein displacement rank almost
surely. Moreover arbitrary diagonal Wick/ReLU scalings do not preserve
low Stein displacement rank: for a generic diagonal `D`,
`D - Z D Z^T` is diagonal with generically `n` nonzero entries.

Thus the broad "make every state Toeplitz-like" variant has no exact
closure theorem under the actual MLP law. Allowing rank truncation would be an
approximate compression class, forbidden by E192.

## 6. Potential-cost condition and why it fails

For a hypothetical structured problem with exact ranks `alpha << n`, the
primary literature gives sub-dense exact arithmetic, so displacement structure
is a legitimate exact acceleration class in general.

For this project, however, an admissible class must have a path to:

`C_all_in <= 138.24u = 0.135B`.

Necessary E192 conditions are:

1. exact displacement rank below full rank on every matrix family claimed as
   accelerated;
2. complete namespace coverage sufficient that the **zero-cost complement
   lower bound** is itself `<=138.24u`;
3. metered structured arithmetic plus unchanged remainder `<=138.24u`.

Condition 2 already fails for the natural exact weight-structure method:
`148.31u > 138.24u`.

Condition 1 also fails almost surely for the Gaussian layer weights under the
standard Stein displacement.

Hence there is no credible all-in `<=0.135B` path for H192 without changing
the random-MLP law, learning a new basis/operator, or truncating generators.
Those changes are respectively out of task, gauge/basis-like, or approximate.

## 7. Exactly one falsifier scheme — F192-LDR-CERT

No execution is authorized. If an independent reviewer ever disputes the
analytic obstruction, the only admissible falsifier is:

### Frozen inputs

- one exact-small rational fixture, `n<=8`;
- one production-shape target-free weight/state fixture, `n=1024`;
- standard nilpotent down-shift `Z`;
- Stein displacement `Delta(A)=A-ZAZ^T`;
- no targets, reference means, scorer or benchmark accuracy.

### Checks

1. **Exact identity:** construct an exact generator of `Delta(A)`, reconstruct
   `A` by the Sigma-LU formula, and require exact rational equality on the
   small fixture.
2. **Exact-rank certificate:** treat stored float32/float64 entries as exact
   dyadic rationals and certify the displacement rank of every matrix family
   proposed for acceleration. No numerical SVD threshold may decide rank.
3. **Information preservation:** on small K3 state, replace only the matrix
   product implementation and require exact equality of D3/D21/K3 outputs.
4. **Namespace lower bound:** enumerate every accelerated namespace and sum the
   unchanged complement from the frozen parent ledger.
5. **Static cost projection:** only if the complement lower bound is under cap,
   meter every generator/reconstruction/convolution/add/copy operation and
   project all-in cost.

### GO

E192 could be reconsidered only if all are true:

- exact identity passes;
- every claimed production family has exact `alpha < n`;
- unchanged-complement lower bound `<=138.24u`;
- complete all-in projection `<=138.24u`;
- D3/D21/K3 are exactly preserved;
- no learned operator, truncation, target access or fallback outside the
  frozen ledger.

### NO-GO

Any one of:

- exact `alpha=n` in a required family;
- complement lower bound `>138.24u`;
- any approximate generator/truncation;
- any D3/D21/K3 mismatch;
- all-in cost `>138.24u`.

Under the protocol-only proof above, H192 already satisfies two NO-GO
conditions, so running F192-LDR-CERT would add no decision-relevant evidence.

## 8. Final research decision

**NO ADMISSIBLE NEW CLASS RETAINED FROM THIS SEARCH.**

Displacement-structured exact linear algebra is genuinely orthogonal to H180,
H185, low-rank K3, sketches, sampling/CV, AGO/gauge, final-observable adjoints
and source-tier compression. It also has a clean exact-information story.

It fails this problem for structural reasons:

- standard exact displacement rank of iid Gaussian weights is full almost
  surely;
- the natural weight-structured scope leaves a `148.31u` V29 lower bound,
  already above the `138.24u` cap even under zero-cost-oracle assumptions.

Accordingly E192 is a **protocol-only terminal desk NO-GO**, not a request for
implementation. No scientific run, code execution, benchmark, baseline change,
ledger change, submission or rescue is authorized.
