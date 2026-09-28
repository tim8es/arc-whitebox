# R396 — source-based cost audit of the missing R385 affine-pair construction

**Status:** COMPLETE  
**Verdict:** **PLAUSIBLE_ALL_IN_FAST_LIN_BUDGET__R385_138.5B_ENVELOPE_UNDERCOUNTS_BOUND_CONSTRUCTION__NO_FLOP_OR_MEMORY_NO_GO__WALL_RESIDUAL_AND_NUMERICAL_SOUNDNESS_UNPROVEN**  
**Mode:** report-only source/algebra audit; no estimator implementation, dataset access, benchmark, scorer, Actions, or submission  
**Branch:** \`research/r396-r385-affine-pair-cost-audit-20260928\`  
**Exact base / parent:** R385 commit \`2ba08cb916cc504f1c38673971c2aa811b2da48c\`  
**R385 report blob:** \`08a04c634f9b489092d4f3636799908cdf51a1a6\`

## 1. Question audited

R385 proposed a multi-shell clipped-GELR certificate whose readout is cheap if a sound affine pair

\[
\ell(x)=a^\top x+\beta
\le f(x)\le
u(x)=c^\top x+\gamma
\]

is already available for every final output coordinate. Its frozen affine-acquisition envelope was

\[
C_{\rm affine,R385}
\le
8Ln^3+64Ln^2
=
138{,}512{,}695{,}296
\]

for \(n=1024,L=16\).

R396 audits the missing part: the actual all-output construction of the
preactivation bounds and affine pair required by Fast-Lin/CROWN, including all
intermediate layers, rather than charging only a small fixed number of matrix
products per network layer.

No accuracy or score-improvement claim is made.

## 2. Primary sources

### Fast-Lin

Tsui-Wei Weng et al., **“Towards Fast Computation of Certified Robustness for
ReLU Networks,”** ICML 2018, PMLR 80:5276–5285.

- paper: https://proceedings.mlr.press/v80/weng18a.html
- PDF: https://proceedings.mlr.press/v80/weng18a/weng18a.pdf
- primary supplement containing the explicit Fast-Lin recurrences and
  Algorithm 1:
  https://proceedings.mlr.press/v80/weng18a/weng18a-supp.pdf

The supplement gives, for unstable ReLU preactivation
\(l<0<u\),

\[
d=\frac{u}{u-l},
\qquad
d z\le \operatorname{ReLU}(z)\le d(z-l),
\]

and shows that the upper and lower Fast-Lin affine bounds share the same
coefficient matrices \(A^{(k)}\). In its notation,

\[
A^{(m-1)}=W^{(m)}D^{(m-1)},
\qquad
A^{(k-1)}=A^{(k)}W^{(k)}D^{(k-1)}.
\]

The supplement explicitly identifies the same-slope property as the reason the
upper and lower bounds can reuse the same \(A,D\) matrices.

### CROWN

Huan Zhang et al., **“Efficient Neural Network Robustness Certification with
General Activation Functions,”** NeurIPS 2018.

- primary paper:
  https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html
- PDF:
  https://proceedings.neurips.cc/paper/2018/file/d04863f100d59b3eb688a11f95b0ae60-Paper.pdf

Definition 3.1 and Theorem 3.2 give sound linear upper/lower activation
relaxations and their backward propagation to explicit affine network-output
bounds. For ReLU, the paper gives the secant upper bound and permits a lower
slope \(a\in[0,1]\); CROWN-Ada chooses \(a=0\) or \(1\) from the preactivation
bounds. The paper states that Fast-Lin is a CROWN special case because Fast-Lin
uses equal upper/lower slopes. It also states the all-layer complexity for an
\(m\)-layer width-\(n\) network with \(n\) outputs as

\[
O(m^2n^3),
\]

because the bounds for every previous layer must be computed before the final
output bound.

### Official Phase-2 accounting

Official starter-kit source pinned by R385 at
\`5eb9aa1455fcb3216af55994bdf25dc242b95797\`:

- rounds:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/rounds.md
- estimator contract:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/estimator-contract.md
- allowed code:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md

Phase 2 is width \(1024\), depth \(16\), budget

\[
B=2^{41}=2{,}199{,}023{,}255{,}552,
\]

8 GB solution-process memory, 120 s per \`predict()\), and a hard 0.4 s residual
wall-time cap. Residual time is plumbing only; meaningful numerical work must be
metered.

Official FlopScope 0.12.1 source pinned by R385 at
\`b599f015b0bc005b1edb6d7a1b10e0814675e693\`:

- matmul cost implementation:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/_flops.py
  blob \`d8103735c03f08ec915b7846bc877ad57d47fa03\`
- direct test of the 2-D formula:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/tests/test_flops_matmul_cost.py
  blob \`1983d1b130abc890de47f1349258bcac63e697c0\`
- production operation weights/dtype rates:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/data/default_weights.json
  blob \`5f7074f76d56b92180c8a1553a3ebe3a4c1d43f5\`

For a 2-D \((m,k)@(k,n)\) product, FlopScope's exact base cost is

\[
2mkn-mn.
\]

The production dtype rate is 1 for float32 and 2 for float64.

### Floating-point soundness caveat

Fast-Lin/CROWN prove real-arithmetic inequalities. They do not by themselves
turn an ordinary floating-point implementation into an outward-rounded formal
certificate. A primary numerical-analysis result for conventional matrix
multiplication gives a componentwise rounding-error form

\[
|\widehat C-C|
\le
\gamma_n |A||B|
\]

under its stated floating-point model; see Fasi, Higham, Lopez, Mary and
Mikaitis, **“Matrix Multiplication in Multiword Arithmetic: Error Analysis and
Application to GPU Tensor Cores,”** SIAM J. Sci. Comput. 45(1), 2023:
https://nhigham.com/wp-content/uploads/2023/02/fhlm23.pdf

R396 does not assume that the current FlopScope matmul execution path has
already been wrapped in such an outward-error certificate.

## 3. Network and box model

The audited generic Phase-2 network is bias-free:

\[
h^{(0)}=x,\qquad
z^{(r)}=W^{(r)}h^{(r-1)},\qquad
h^{(r)}=\operatorname{ReLU}(z^{(r)}),
\]

with

\[
W^{(r)}\in\mathbb R^{1024\times1024},
\qquad r=1,\ldots,16.
\]

R385 needs the final 1024 output coordinates. The contract still requires a
finite \((16,1024)\) return array, but the competition score uses the final
layer; this audit counts the bound construction needed for the R385 final-row
certificate.

For the unit box

\[
K_1=[-1,1]^{1024},
\]

construct preactivation bounds

\[
l^{(r)}\le z^{(r)}(x)\le u^{(r)}
\]

for all 1024 neurons of every layer.

For an unstable ReLU, Fast-Lin uses

\[
d_i^{(r)}
=
\frac{u_i^{(r)}}{u_i^{(r)}-l_i^{(r)}}.
\]

For stable-positive neurons set \(d=1\), and for stable-negative set \(d=0\).

For a target layer \(t\), all 1024 preactivations can be propagated together as
an \(n\times n\) coefficient matrix. The Fast-Lin recurrence is exactly the
matrix form above. The upper/lower constants differ, but the coefficient
matrix is shared.

At the final layer, after the affine pair for \(z^{(16)}\) is available, the
final ReLU is handled rowwise with the same scalar relaxation. This requires
only row scaling and intercept updates, not another dense GEMM.

## 4. Why one unit-box pass is reusable for every R385 shell

This point is favorable to R385.

For a bias-free ReLU network,

\[
f(Rx)=R f(x),\qquad R>0.
\]

The true preactivation bounds scale as

\[
l^{(r)}(R)=R\,l^{(r)}(1),
\qquad
u^{(r)}(R)=R\,u^{(r)}(1).
\]

Hence for every unstable neuron

\[
\frac{u(R)}{u(R)-l(R)}
=
\frac{u(1)}{u(1)-l(1)}.
\]

The stable/unstable sign classes are also invariant under positive scaling.
CROWN-Ada's comparison \(u\ge|l|\) is scale-invariant as well.

Therefore the relaxation slopes and affine coefficient matrices are
independent of shell radius, while affine intercepts scale linearly with \(R\):

\[
\ell_R(x)=a^\top x+R\beta,
\qquad
u_R(x)=c^\top x+R\gamma.
\]

So **the \(K\) nested shells do not require \(K\) Fast-Lin/CROWN bound
constructions**. One unit-box construction is enough; only the R385 Gaussian
readout scales with \(K\).

This conclusion depends critically on the actual Phase-2 zero-bias,
positively-homogeneous architecture. It would not hold unchanged with
nonzero biases or nonhomogeneous activations.

## 5. Exact dominant Fast-Lin cost

Set

\[
n=1024,\qquad L=16.
\]

FlopScope charges one dense square float32 GEMM

\[
G(n)=2n^3-n^2.
\]

Thus

\[
\boxed{
G(1024)=2{,}146{,}435{,}072.
}
\]

To obtain all preactivation bounds sequentially, target layer \(t\) needs
\(t-1\) dense coefficient products back to the input. Therefore the exact
number of all-output GEMMs is

\[
\sum_{t=1}^{16}(t-1)
=
\frac{16\cdot15}{2}
=
\boxed{120}.
\]

The **exact FlopScope float32 GEMM component** is therefore

\[
\boxed{
C_{\rm GEMM,FastLin}
=
120(2n^3-n^2)
=
257{,}572{,}208{,}640.
}
\]

This number alone already exceeds R385's entire frozen affine envelope
\(138{,}512{,}695{,}296\). Therefore the R385/R376 “at most four dense products
per network layer” envelope is not a valid accounting of a full all-layer
Fast-Lin construction.

It undercounts even before sign masks, slopes, intercept corrections, row
norms, the tail Lipschitz bound, or Gaussian readout are charged.

## 6. Non-GEMM Fast-Lin arithmetic

A concrete vectorized float32 schedule can avoid materializing the full
Fast-Lin \(T,H\) tensors.

For each saved \(A\) at one target-layer/backward-layer pair, let
\(s^{(r)}\) be \(l^{(r)}\) on unstable neurons and zero elsewhere. The upper
and lower intercept corrections can be accumulated as row reductions of

\[
\max(A,0)\odot s^{(r)}
\quad\text{and}\quad
\min(A,0)\odot s^{(r)}.
\]

With FlopScope's production weights
\(\texttt{maximum}=\texttt{minimum}=\texttt{multiply}=\texttt{sum}
=\texttt{add}=1\), one such pair costs at most

\[
6n^2
\]

billed float32 scalar operations: two pointwise sign clips, two products, two
row reductions, and two vector accumulations (the reduction off-by-one and
vector adds cancel in this upper expression).

There are 120 such target/backward pairs, so

\[
C_{\rm intercept}
\le
720n^2
=
754{,}974{,}720.
\]

Other explicitly counted terms are only \(O(Ln^2)\):

- 15 cached \(W D\) column/row scalings:
  \(15n^2=15{,}728{,}640\);
- layerwise row-\(\ell_1\) optimization over the centered box:
  \(16(2n^2+n)=33{,}570{,}816\);
- final-ReLU coefficient row scaling:
  \(n^2=1{,}048{,}576\);
- slope/sign-class construction is \(O(Ln)\), below one million operations for
  this shape even under a conservative vectorized \`where\` spelling.

Using the exact terms above plus a conservative sub-million reserve for slope
construction gives

\[
\boxed{
C_{\rm FastLin,affine}
<
258.5\times10^9
\quad\text{float32 billed FLOPs}.
}
\]

A more literal spelling of the same schedule before the sub-million reserve is
about \(258.378\times10^9\).

This is an **auditable static construction count**, not a measured FlopScope
trace.

## 7. Certified tail-Lipschitz cost

R385 also needs a sound coordinate constant

\[
f_j(x)\le\Lambda_j\|x\|_2.
\]

A cheap, sound but potentially loose choice follows from ReLU being
1-Lipschitz and

\[
\|W\|_2\le\|W\|_F:
\]

\[
\boxed{
\Lambda_j
=
\|W^{(16)}_{j,:}\|_2
\prod_{r=1}^{15}\|W^{(r)}\|_F.
}
\]

This requires no SVD.

A direct float32 schedule costs:

- each of 15 full Frobenius norms: \(2n^2\) operations
  (square, reduction, sqrt);
- all 1024 final-row 2-norms together: \(2n^2\);
- 14 scalar products plus 1024 final row scalings.

Thus

\[
\boxed{
C_{\Lambda}
=
32n^2+14+n
=
33{,}555{,}470.
}
\]

This is negligible next to coefficient propagation. It may be too loose for a
useful certificate; R396 makes no accuracy claim.

Using Fast-Lip instead could tighten the tail but adds another nontrivial bound
propagation and is not required to establish budget plausibility.

## 8. R385 Gaussian readout

R385 already derived the vectorized shell readout envelope

\[
C_{\rm read}(K)
\le
4{,}209{,}664+184{,}462K.
\]

For \(K=64\),

\[
\boxed{
C_{\rm read}(64)
\le
16{,}015{,}232.
}
\]

This includes its float64 normal-PDF/CDF billing.

Combining the Fast-Lin construction, the cheap certified tail constant, and
\(K=64\) readout gives approximately

\[
\boxed{
C_{\rm all,FastLin,K64}
\lesssim
258.55\times10^9.
}
\]

Using the literal counted schedule before the small slope reserve gives
\(258{,}427{,}298{,}702\) FLOPs.

Relative to the Phase-2 hard budget,

\[
\boxed{
C_{\rm all}/2^{41}
\approx0.11752.
}
\]

So it is only about 11.75% of the hard FLOP budget, leaving about
\(1.94\times10^{12}\) FLOPs of headroom.

However,

\[
0.11752>0.1.
\]

Therefore a full Fast-Lin R385 implementation does **not** have a source-based
path to the scorer's 0.1 compute floor under this construction. That corrects
the earlier R385/R376 cost premise.

This is a compute-accounting statement, not a score statement.

## 9. Adaptive CROWN alternative

CROWN permits different upper/lower slopes. Its own paper states that Fast-Lin
is the equal-slope special case and that general CROWN has
\(O(L^2n^3)\) all-layer cost.

For a straightforward all-output adaptive implementation, upper and lower
coefficient matrices must be propagated separately.

The exact dense-GEMM core becomes

\[
\boxed{
2\cdot120=240\ \text{square GEMMs},
}
\]

hence

\[
\boxed{
C_{\rm GEMM,CROWN}
=
240(2n^3-n^2)
=
515{,}144{,}417{,}280.
}
\]

Sign-dependent slope selection and intercept accumulation add \(O(L^2n^2)\),
not another cubic term. A conservative vectorized float32 envelope below
\(3\times10^9\) operations covers these pointwise/reduction terms for 240
upper/lower backward paths at this shape.

Including the same cheap tail bound and \(K=64\) readout therefore leaves a
straightforward adaptive-CROWN construction around

\[
\boxed{
C_{\rm all,CROWN,K64}
<5.19\times10^{11}
<2^{41}.
}
\]

That is below roughly 24% of the hard Phase-2 FLOP budget, but well above the
0.1 score-floor compute threshold.

No claim is made that this more expensive adaptive relaxation produces a
sufficiently tighter GELR interval.

## 10. Float64 sensitivity

FlopScope's production dtype rate is 2 for float64.

If the affine construction is promoted wholesale from float32 to float64, its
metered acquisition cost is approximately doubled.

For the Fast-Lin schedule above plus the already-float64 \(K=64\) readout,

\[
C_{\rm all,FastLin64,K64}
\approx
5.17\times10^{11},
\]

about 23.5% of \(2^{41}\).

A straightforward adaptive-CROWN float64 construction is roughly
\(1.04\times10^{12}\), about 47% of \(2^{41}\), before any extra
outward-rounding/error-bound machinery.

Thus even float64 does not create a FLOP-budget NO-GO.

But float64 by itself is **not a proof of outward soundness**.

## 11. Memory

A memory-feasible Fast-Lin schedule exists without storing \(T,H\) as dense
matrices.

For float32:

- 16 supplied weight matrices:
  \(16n^2\cdot4=67{,}108{,}864\) bytes = 64 MiB;
- 15 cached \(W D\) matrices:
  \(15n^2\cdot4=62{,}914{,}560\) bytes = 60 MiB;
- up to 16 saved \(A\) matrices:
  \(16n^2\cdot4=67{,}108{,}864\) bytes = 64 MiB;
- four dense work arrays:
  \(4n^2\cdot4=16{,}777{,}216\) bytes = 16 MiB.

The matrix subtotal is

\[
\boxed{
213{,}909{,}504\ {\rm bytes}
=
204\ {\rm MiB}.
}
\]

R385's \(K=64\) ten-array float64 shell-work example adds only

\[
5{,}242{,}880\ {\rm bytes}
\approx5\ {\rm MiB}.
\]

Vectors, interval endpoints, masks, and the final \((16,1024)\) output are
small compared with the dense matrices.

Even if the coefficient/cache/work matrices are float64 while supplied weights
remain float32, the same schedule is only about 344 MiB before the shell
workspace.

Therefore

\[
\boxed{\text{8 GB memory: PASS by static accounting.}}
\]

This is resident-array accounting, not measured peak RSS.

## 12. Wall and residual gates

### 120 s wall

The primary Fast-Lin paper reports practical execution on networks up to seven
layers and more than 10,000 neurons, but that hardware/software result cannot
be converted into a Phase-2 grader timing guarantee.

R396 has no authorized timing run and no exact grader throughput measurement
for 120 sequential 1024-square FlopScope GEMMs.

Therefore

\[
\boxed{\text{120 s wall: UNKNOWN, not certified.}}
\]

There is no source-based proof of failure either.

### 0.4 s residual

The implementation can put every meaningful numerical operation—GEMMs,
pointwise sign/slope work, reductions, norms, Gaussian PDF/CDF, and shell
readout—inside FlopScope. Python need only orchestrate 16 target layers and
their bounded backward loops.

That makes the residual requirement plausible, but residual time is a
machine/runtime measurement, not a FLOP formula.

Therefore

\[
\boxed{\text{0.4 s residual: UNKNOWN, not certified.}}
\]

No unmetered numerical arithmetic is assumed.

## 13. Numerical soundness is a separate implementation gate

The mathematical Fast-Lin/CROWN recurrences are sound over real arithmetic.

For R385, however, the word “certificate” requires the implemented
\(\ell,u\) to remain outward bounds after floating-point rounding.

Neither R385 nor the primary Fast-Lin/CROWN papers provide a FlopScope-specific
rounding proof.

A production implementation therefore needs one of:

1. a verified outward-rounding path; or
2. explicit accumulated rounding-error inflation for every coefficient and
   intercept operation, with assumptions matched to the actual FlopScope
   arithmetic.

The standard componentwise matrix-product error theorem shows such inflation
is mathematically possible in principle, but R396 has not established the
exact FlopScope execution/rounding semantics required to turn that theorem
into a complete implementation proof.

So:

\[
\boxed{\text{finite-precision certificate soundness: OPEN IMPLEMENTATION GATE.}}
\]

This is not a FLOP-budget NO-GO.

## 14. What is exact, what is assumed, what is unknown

### Exact / source-backed

- Phase-2 shape: \(1024\times16\).
- hard FLOP budget: \(2^{41}=2{,}199{,}023{,}255{,}552\).
- memory cap: 8 GB.
- wall cap: 120 s.
- residual cap: 0.4 s.
- FlopScope square-matmul cost:
  \(2n^3-n^2=2{,}146{,}435{,}072\) at \(n=1024\), before dtype rate.
- Fast-Lin same-slope upper/lower coefficient reuse.
- all-layer Fast-Lin coefficient chain requires 120 square GEMMs for the
  explicit construction above.
- exact float32 GEMM component:
  \(257{,}572{,}208{,}640\).
- adaptive upper/lower CROWN explicit construction has 240 square-GEMM core:
  \(515{,}144{,}417{,}280\).
- shell radii do not multiply affine acquisition for this bias-free homogeneous
  architecture.
- 8 GB is not close under the streaming/cache schedules above.

### Explicit implementation assumptions

- dense all-output propagation uses the classical FlopScope matmul primitive;
- float32 coefficient path unless otherwise stated;
- \(T,H\) are streamed as masked row reductions rather than persisted as
  \(n\times n\) matrices for every layer;
- tail \(\Lambda_j\) uses the cheap Frobenius/operator-norm inequality;
- R385's \(K=64\) readout envelope is retained;
- no hidden extra algorithm such as LP solving, activation-region enumeration,
  or Fast-Lip is inserted.

### Unknown without execution / additional source contract

- actual wall time;
- actual residual wall time;
- peak RSS including Python/FlopScope runtime overhead;
- exact operation log of a concrete implementation;
- whether float32 or float64 coefficient propagation is numerically adequate;
- a complete outward-rounding/error-inflation implementation proof;
- actual interval tightness on the generated or Mini networks;
- any actual score.

## 15. Decision

### R385's original affine-cost claim

\[
\boxed{\text{FAIL / MATERIAL UNDERCOUNT}}
\]

The frozen \(138.513\)B envelope cannot cover a full source-faithful all-layer
Fast-Lin construction, because the exact float32 dense-GEMM component alone is

\[
257.572\ {\rm B}.
\]

The reason is structural: preactivation bounds for every preceding layer must
be constructed, producing the triangular \(1+\cdots+15=120\) all-output
matrix-product count. This is exactly the dependency pattern described in the
Fast-Lin algorithm and the CROWN \(O(L^2n^3)\) complexity discussion.

### Does this produce a Phase-2 hard-budget NO-GO?

\[
\boxed{\text{NO}}
\]

A source-faithful Fast-Lin special-case affine pair remains **plausibly inside
the hard Phase-2 budget**:

- float32 all-in static construction with \(K=64\): about
  \(2.585\times10^{11}\) FLOPs, \(\approx11.75\%\) of \(2^{41}\);
- float64 version: about \(5.17\times10^{11}\), \(\approx23.5\%\);
- memory: hundreds of MiB, not GB.

A straightforward adaptive CROWN construction is also below the hard FLOP
budget, though substantially more expensive.

### Is R385 ready to claim a complete executable certificate?

\[
\boxed{\text{NOT YET}}
\]

Two gates remain unresolved without implementation measurement/proof:

1. 120 s wall and 0.4 s residual timing;
2. finite-precision outward soundness of the affine bounds.

And R396 makes **no score claim**. Being inside the hard compute/memory budget
does not establish that the certificate is tight enough to improve any score.

## 16. Execution accounting

- R391 implementation continued: **NO — superseded by R395**
- estimator code created: **NO**
- project code executed: **NO**
- estimator runs: **0**
- synthetic runs: **0**
- Mini/public/private/holdout/full dataset access: **0**
- benchmark/scorer runs: **0**
- Actions runs: **0**
- downloads / installs / fetch-clones: **0**
- submissions: **0**
- main edits: **0**
- R320 edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**

Tooling disclosure: one accidental local no-op shell invocation (\`true\`) was
issued during desk arithmetic. It did not inspect repository files, execute
project code, access data, install/download anything, or produce a scientific
measurement.
