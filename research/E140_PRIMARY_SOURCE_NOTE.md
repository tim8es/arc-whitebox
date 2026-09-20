# E140 — what is actually open after V29, and one new falsifiable representation

Status: **PRIMARY-SOURCE RESEARCH COMPLETE / H140 ADMITTED FOR ONE TARGET-FREE FALSIFIER / NO RUN YET**

Protocol: \`research/E140_PROTOCOL.md\`  
Protocol commit: \`308ade13e061f7313f8d0bec20d051649479a089\`

This note is deliberately not a version overview. The research contribution is Section 4:
a new algebraic carrier for quenched K3 whose transport and D3/D21 readout are derived
below. Its only unresolved question is rank growth at nonlinear births, which is frozen
as a one-shot falsifier.

---

## 1. Primary-source set

### ARC PRIMARY

1. ARC challenge announcement  
   https://www.alignment.org/blog/announcing-the-arc-white-box-estimation-challenge/

   ARC states that the challenge estimates the expected output of a fixed random ReLU MLP
   under Gaussian input, under explicit computational constraints, and says the existing
   wide-network methods break down as depth grows.

2. ARC overview of the MLP method  
   https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/

   ARC describes cumulant propagation as an approximate-distribution method and emphasizes
   that the specific higher-order details are essential for beating sampling.

3. ARC paper  
   https://arxiv.org/abs/2605.05179

   The public 504aldo re-read of S.4.3/S.8.5/App. C/D/J is consistent with the reference
   code: the factorized K3 representation grows by appending factors/sources and the
   published cost is \(O(n^3L^2)\). The paper does not provide a depth-independent error
   theorem for the competition regime.

4. ARC reference implementation  
   https://github.com/alignment-research-center/mlp_cumulant_propagation

   Reviewed blobs:

   - \`README.md\`: \`0665357e37164f1896392fbbd4431a5a4e692871\`
   - \`src/mlp_kprop/factor_k3.py\`: \`ed7cddd91fcf3a744a02aacfba6f24f9f743c82a\`
   - \`src/mlp_kprop/wick.py\`: \`2947a40c33fac64441dbc5b180bfe6a865cca452\`

   The reference \`FactoredTensor\` stores

   \[
   T=\operatorname{Sym}\sum_r A_{1,:,r}\otimes A_{2,:,r}\otimes A_{3,:,r}.
   \]

   Linear transport applies the same dense \(W\) to every factor. The diagonal-slice
   routine explicitly multiplies factors inside repeated-index blocks before contracting;
   for K3 this is the Hadamard/multiplicative structure that later dominates the
   competition cost.

### 504ALDO PRIMARY

Pinned repository:

https://github.com/504aldo/whest-p2-cumulant-k3/tree/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45

Reviewed public blobs:

- \`docs/community_post.md\`: \`aa06c6d24c0bf9f6cb9cfd326c4862d6a4ee3a73\`
- \`docs/findings_log.md\`: \`09cf41e8826052ceb83109115cae688c03baaaca\`
- \`docs/derivation_code_map.md\`: \`2b7f1e7df1ddf08a3925bbe883ebe0db14942eff\`
- \`estimators/estimator_v29.py\`: \`17df1a073a24f96c4705b04bcf61ef60fa06dd0c\`

Community post:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/community_post.md

Raw findings:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/findings_log.md

V29:

https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v29.py

---

## 2. What is established, not open

### 2.1 The useful K3 information is not a marginal/slice-only state

**504ALDO PRIMARY — F65/F82.**

Two independently implemented memoryless slice closures land near the same floor:

- F65 pure D3/D21 slice state: about \(9.1\times10^{-7}\) raw;
- F82 A716-style merged response closure: about \(9.8\times10^{-7}\) raw.

Feeding exact D3/D21 into the collapsed chain recovers the exact K3-chain result, so D3
and D21 are the complete *interface* to the next nonlinear step, but they are not a
closed state: the fully off-diagonal K3 content is needed to regenerate the next layer's
D21.

Therefore "store only the interface" is closed.

### 2.2 Per-source K3 content cannot be removed by the measured ordinary compressions

**504ALDO PRIMARY — F61/F66/F71/F72/F73/F76/F88.**

Established negatives:

- old-source dropping/windowing destroys accuracy;
- CP/hub-column importance is too flat;
- symmetric Tucker/shared-row compression has a sharp rank floor;
- the identity-born \(P\) leg prevents the low symmetric-Tucker ranks suggested by a
  one-shot D21 proxy;
- exact multiplicative closure of a row basis produces the Khatri-Rao/\(r^2\) wall;
- adjoint-only final sensitivity does not remove the source transports and linearizes a
  material feedback path.

The measured age law is approximately:

\[
r/n\approx 3/8\quad\text{at age 4},\qquad
r/n\approx 7/32\quad\text{at age 7},
\]

with a cliff one notch below.

Therefore another source-age rank schedule is not open.

### 2.3 V29 is a cost implementation of the V25 arithmetic, not a new closure

**504ALDO PRIMARY — F79/F80/F81/F88.**

The public ladder reports essentially unchanged raw error from V25 through V29 while
Strassen/buffer engineering reduces the multiplier to about \(0.2526B\).

The public author's same-closure floor is about \(2.07\times10^{-8}\) on the local
8-dump reference chain. F88 reports float32→float64 as null and larger D21-feedback rank
as score-negative.

Therefore V29's missing raw accuracy is not a precision or obvious rank knob.

### 2.4 The dominant V29 cost is the representation, not remaining pricing polish

**504ALDO PRIMARY — F86.**

Steady V29 ledger, unit \(=2n^3\), \(B=1024\) units:

\[
\begin{array}{lr}
\text{young K3} & 115.6\\
\text{old K3} & 106.8\\
\text{thin/elementwise K3} & 24.8\\
\text{covariance} & 7.1\\
\text{closure+birth} & 5.7
\end{array}
\]

Total about \(260.1\) units.

The old tier alone is \(106.8\) units, but deleting it leaves about \(153.2\) units
(\(0.1496B\)). That is already above this project's \(0.135B\) production cap.

**DERIVATION:** any E140 mechanism that only patches V29's old tier is therefore
inadmissible for the project target even at zero patch cost.

This closes an E137-style "cheaper old contraction only" direction for E140.

### 2.5 E137 H137 did not scientifically test CountSketch

**LOCAL VERIFIED.**

E137-H137's sole Actions run failed at import
(\`ModuleNotFoundError: No module named 'methods'\`) before D21, cost, or deterministic
scientific gates were evaluated. Its frozen protocol nevertheless makes that experiment
identity terminal.

E140 does not rescue it. The new representation below changes the K3 carrier itself and
has no CountSketch final-product patch.

### 2.6 Norm-only certification is not the missing representation

**LOCAL VERIFIED — E135.**

E135 proved that an observable Parseval residual norm loses the orientation needed for a
tight deterministic downstream bound on arbitrary dense weights. An orientation-aware
certificate reconstructs source-like state.

E140 therefore seeks a smaller *state representation*, not another certificate.

---

## 3. What is genuinely open after V29

The primary sources leave a narrower frontier than "better K3 compression."

### Open A — a different quenched order-3 carrier

**504ALDO PRIMARY — F76/F77/F86/F88.**

The public author concludes that the \(0.15\)–\(0.21B\) frontier cannot be an ordinary
compression of the per-source hub representation. F77 observes that the leaderboard cost
drops are consistent with chains dominated by symmetric \(n\times n\) operations, while
F78/F82 kill two obvious symmetric-state interpretations: scale mixtures and A716/slice
closures.

What is still open is a state that:

1. carries fully off-diagonal quenched K3 information;
2. is built from a small number of full symmetric matrices rather than many source legs;
3. is closed under dense transport;
4. exposes D21 without reconstructing K3.

No such representation is supplied by the ARC paper or the 504aldo release.

### Open B — raw information beyond V29's K3 + memoryless-K4 closure

**504ALDO PRIMARY — F75/F88.**

The V29 arithmetic floor remains above the best public raw errors reported in F88.
The only explicitly untested V29-local K4 regeneration refinement is stated by the author
to have an oracle ceiling of only about 1%.

Therefore a material raw improvement is expected to require a different expansion, not a
table/rank polish.

### Open C — depth-uniform theory

**ARC PRIMARY / 504ALDO PRIMARY — ARC paper Sec. 7.3 as recorded in F74.**

The depth dependence of the cumulant approximation remains theoretically open. This is a
real theory question but not, by itself, a production estimator.

---

## 4. New algebraic observation

### 4.1 Symmetric matrix-vector separation

**DERIVATION.**

Represent a symmetric third-order tensor as

\[
\boxed{
K_{ijk}
\approx
\sum_{a=1}^{m}
\frac{
R^{(a)}_{ij}v^{(a)}_k+
R^{(a)}_{ik}v^{(a)}_j+
R^{(a)}_{jk}v^{(a)}_i
}{3}
}
\]

with each \(R^{(a)}\in\mathbb R^{n\times n}\) symmetric and
\(v^{(a)}\in\mathbb R^n\).

Call this an **SMV K3 state**.

This is not CP/hub rank: each mode contains a *full symmetric matrix*.
It is not symmetric Tucker: there is no shared low-dimensional neuron basis \(Q\).
It is not a slice state: \(R^{(a)}\) contains fully off-diagonal information.

### 4.2 Exact closure under dense linear transport

Let

\[
K' = K\times_1 W\times_2 W\times_3 W.
\]

For one SMV mode,

\[
\operatorname{Sym}(R\otimes v)
\mapsto
\operatorname{Sym}\big((WRW^\top)\otimes(Wv)\big).
\]

Therefore

\[
\boxed{
R_a' = W R_a W^\top,\qquad
v_a'=Wv_a
}
\]

is an **exact transport identity** for the represented tensor.

No source age, hub columns, dense \(A/P\) legs, or Khatri-Rao multiplication appears.

### 4.3 Exact closure under the carried K3 Wick scaling

The all-distinct carried K3 term in ARC's simple factorized nonlinearity is multiplied by
the first Wick coefficient on each tensor index. Let \(D=\operatorname{diag}(w_1)\).

Then

\[
K' = K\times_1D\times_2D\times_3D
\]

preserves the SMV form exactly:

\[
\boxed{
R_a'=D R_a D,\qquad
v_a'=Dv_a.
}
\]

Thus linear transport and multiplicative Wick transport do **not** grow SMV rank.

This is the key distinction from the source stack: rank growth can occur only when the
nonlinearity injects new K3 birth content.

### 4.4 D3 and D21 are direct \(O(mn^2)\) readouts

For one mode,

\[
K_{iic}
=
\frac{R_{ii}v_c+2R_{ic}v_i}{3}.
\]

Hence

\[
\boxed{
D21_{ic}
=
\sum_a
\frac{R^{(a)}_{ii}v^{(a)}_c+
2R^{(a)}_{ic}v^{(a)}_i}{3}
}
\]

and

\[
\boxed{
D3_i = K_{iii}
= \sum_a R^{(a)}_{ii}v^{(a)}_i.
}
\]

So the exact interface used by the ReLU update is available without materializing an
\(n^3\) tensor and without a Hadamard-then-matmul source contraction.

### 4.5 The only unresolved mathematical question is birth separation rank

ARC's reference \`factor_k3.py\` shows that each ReLU injects new factored K3 content,
including two-leg path terms with an identity middle factor. In the source
representation this appends \(O(n)\) columns per layer.

For SMV, the same birth tensor can always be represented with at most \(O(n)\) modes,
but that is useless. The research question is whether the **best matrix-vector separation
rank of the accumulated birth content is small**, e.g. \(m=4\), after the actual
Wick/covariance weighting.

Nothing in the primary sources measures this rank.

F76's flat CP-column spectrum is negative evidence but not a proof: CP/hub rank and
matrix-vector separation rank are different matricizations. F66's shared-row rank is also
a different object because SMV matrices remain full-rank in neuron space.

Therefore this question is genuinely unmeasured rather than already closed.

---

## 5. H140 — four symmetric K3 response modes

Classification: **HYPOTHESIS / NOT YET VERIFIED**

> At Phase-2 He-ReLU shape, the accumulated quenched K3 state relevant to D3/D21 can be
> approximated after each nonlinear birth by \(m=4\) symmetric matrix-vector modes with
> <=2.2% D21 relative RMS error, while linear/Wick transport of those modes is exact.

Why \(m=4\):

- it is a single frozen point, not a rank sweep;
- 504aldo F77's public cost anatomy specifically points toward a small number of symmetric
  \(n\times n\) response objects as the only cost class consistent with the low-multiplier
  frontier;
- four full matrices are qualitatively richer than four CP atoms or four slice modes.

### Production arithmetic plausibility

**DERIVATION, conservative upper before birth compression.**

504aldo F77 measures an ordinary symmetric sandwich at \(1.5\) units in the pre-Strassen
ledger. Using that conservative price:

\[
4\text{ modes}\times16\text{ layers}\times1.5
=96\text{ units}.
\]

A vector transport/readout is \(n^2\)-class and negligible on the \(2n^3\) unit scale.

Using the public covariance/closure scale as a conservative allowance:

\[
96 + 22.5 + 5.7 = 124.2\text{ units}
=0.1213B.
\]

The project cap is

\[
0.135B = 138.24\text{ units}.
\]

So about \(14\) units remain for SMV birth construction/recompression before invoking any
V29 Strassen discount.

This is not a production proof. It is enough to make \(m=4\) a cost-admissible falsifier.
If birth recompression needs an \(n^3\) materialization/SVD or more than the remaining
allowance, H140 is terminally dead even if the small fixture is accurate.

---

## 6. Frozen falsifier

No E140 code/run is authorized by this research note. The executable protocol is already
frozen in \`research/E140_PROTOCOL.md\`.

### Fixture/reference

Two target-free exact-small fixtures:

- A: width 32, depth 8, He-Gaussian dense weights, seed 140032;
- B: width 16, depth 8, deterministic adversarial dense rotation/gain fixture, seed 140016.

Reference is ARC K=3-simple K3 state, not competition final means.

At small width it is legal to materialize the exact K3 tensor solely to compute the
**best possible rank-4 SMV approximation** after each nonlinear birth. This deliberately
gives H140 an oracle *within its representation class* while remaining target-free.

The candidate then uses only SMV formulas for the following linear/Wick transport and
D3/D21 readout.

### Frozen gates

\[
\epsilon_{21}
=
\frac{\|\widehat{D21}-D21\|_F}{\|D21\|_F}.
\]

GO requires all of:

1. linear SMV transport identity max abs <= \(10^{-12}\);
2. Wick-scaling identity max abs <= \(10^{-12}\);
3. deterministic finite replay;
4. pooled \(\epsilon_{21}\le0.022\) on each fixture;
5. no layer \(\epsilon_{21}>0.03\);
6. D3 relative RMS <= \(0.022\);
7. complete production arithmetic upper <= \(0.135B\);
8. production birth/recompression does not materialize \(n^3\) state or use a dense
   \(O(n^3m)\) SVD.

Any failure is terminal NO-GO for rank-4 SMV. No rank-8 rescue, no seed change, no target
read, no public/scorer/holdout/full run.

---

## 7. Why H140 is not a renamed closed lane

| closed lane | why H140 differs |
|---|---|
| F65/F82 slice closure | H140 carries full symmetric matrices and therefore fully off-diagonal K3 content |
| F66/F72/F73 shared row basis | H140 does not project neuron rows into a shared \(Q\) |
| F76 CP/hub cap | one H140 mode is a full \(n\times n\) matrix times a vector, not one hub atom |
| F78 Gaussian mixture | no latent scale/Gaussian-mixture assumption |
| F88 Tucker core | no \(r\times r\times r\) core and no \(n\times r\) basis on all modes |
| F88 adjoint | H140 is a forward K3 state and retains nonlinear feedback |
| E135 certificate | H140 is an estimator state, not an error bound |
| E137 H137 | no CountSketch and no patch to V25/V29 old-tier products |
| E124/E127 | no pair-tree or sparse hypergraph closure |

---

## 8. Decision

### What is proved by this E140 research

**DERIVATION:**

The SMV carrier has three exact properties:

\[
\operatorname{SMV}(R,v)
\xrightarrow{W^{\otimes3}}
\operatorname{SMV}(WRW^\top,Wv),
\]

\[
\operatorname{SMV}(R,v)
\xrightarrow{D^{\otimes3}}
\operatorname{SMV}(DRD,Dv),
\]

and

\[
D21_{ic}
=
\sum_a\frac{R^{(a)}_{ii}v^{(a)}_c+2R^{(a)}_{ic}v^{(a)}_i}{3}.
\]

Therefore it attacks exactly the public F67/F86 cost wall: it never has to re-form
source legs merely to take their Hadamard products.

### What remains UNKNOWN

Whether ReLU-born K3 content has matrix-vector separation rank <=4 at the fidelity the
chain needs.

No primary source measures that quantity.

### E140 status

\[
\boxed{\text{H140 ADMITTED FOR ONE TARGET-FREE SMALL FALSIFIER}}
\]

This is not a GO claim and not a claimed leaderboard mechanism.

No E140 estimator code, workflow, Actions run, public run, scorer, holdout/full execution,
target fitting, sweep, canonical mutation, or ledger mutation occurred.
