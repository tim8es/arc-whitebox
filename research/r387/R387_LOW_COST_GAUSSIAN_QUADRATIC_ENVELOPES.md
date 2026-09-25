# R387 — low-cost Gaussian quadratic envelopes for Phase 2

**Status:** COMPLETE  
**Verdict:** **NO_GO_NO_SOUND_LOW_COST_QGME_CERTIFICATE_CLOSES_CONSTRUCTION_PLUS_2048_OBJECTIVE_PLUS_RUNTIME_GATES**  
**Branch:** `research/r387-qgme-cheap-certificates-20260925`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Parent method audited:** R381 QGME-SDP, report blob `a0238ea75703aa05341c463bcbdc7e0e361cbf27`  
**Mode:** static mathematics/source audit only. No code, solver, synthetic, benchmark, scorer, Actions, download, install, or submission run.

## 1. Narrow question and fixed Phase-2 contract

R381 established a sound route from a certified quadratic input envelope to an analytic Gaussian-mean interval, but stopped because a generic SDP did not have a Phase-2-feasible 1024-output solve.

R387 tests only four proposed escapes:

1. diagonal PSD certificates;
2. disjoint/block-diagonal or bounded-factor-width PSD certificates;
3. low-rank-plus-diagonal PSD certificates;
4. shared/cached work across the 1024 lower and 1024 upper objectives.

No other estimator family is reopened.

The current official Phase-2 contract is:

- width (n=1024);
- depth (L=16);
- per-MLP budget
  [
  B=2^{41}=2,199,023,255,552;
  ]
- score multiplier (max(0.1,F/B));
- per-`predict()` wall cap 120 s;
- residual cap 0.4 s;
- solution-process memory cap 8 GB.

Official sources:

- AIcrowd scoring model, blob `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`:  
  https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md
- AIcrowd rounds, blob `2aaf38a54b5d6ed83ce2604870dcac59e62cee59`:  
  https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/rounds.md
- AIcrowd allowed code, blob `525276e8e5bc7f6a7dd54e876140ab0df514be32`:  
  https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/allowed-code.md
- AIcrowd code patterns, blob `2d1aa532af6f160fd0942da34f78595216a596de`:  
  https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/code-patterns.md

The allowed-code restriction matters directly: the grader supplies the Python interpreter, FlopScope, and pure-Python standard library; third-party numerical solvers/NumPy/SciPy/BLAS/compiled kernels are not an available execution route. Numerical work must be expressed through the metered FlopScope path. Therefore a literature result saying that an LP/SOCP/SDP is “tractable” is not by itself a Phase-2 implementation or timing proof.

## 2. Certificate template frozen for counting

Let

[
z=[1;x;h^1;ldots;h^{16}]inmathbb R^p,
qquad
p=1+17cdot1024=oxed{17,409}.
]

A lower or upper QGME certificate for output coordinate (j) has the form

[
M_j^pm(	heta_j,lambda_j)succeq0,
]

where (	heta_j) contains the quadratic input-envelope coefficients and (lambda_j) contains multipliers for sound graph/input quadratic constraints.

For an explicit cheap-QC count, R387 uses only the elementary exact scalar ReLU graph facts

[
yge0,qquad y-zge0,qquad y(y-z)=0
]

for every ReLU, plus one ball constraint. This is an intentionally weak but sound S-procedure template. It uses exactly

[
m_{m QC}=3(16)(1024)+1=oxed{49,153}
]

scalar QC multipliers per certificate before any sharing. A richer DeepSDP QC set can only increase this count.

The lifted symmetric matrix has exactly

[
N_{m sym}=rac{p(p+1)}2
=oxed{151,545,345}
]

independent entries and

[
N_{m off}=rac{p(p-1)}2
=oxed{151,527,936}
]

off-diagonal entries.

Primary soundness basis: Fazlyab, Morari & Pappas encode activation/input properties as quadratic constraints and combine them through the S-procedure into a PSD certificate.

- Mahyar Fazlyab, Manfred Morari, George J. Pappas, “Safety Verification and Robustness Analysis of Neural Networks via Quadratic Constraints and Semidefinite Programming,” IEEE TAC 2022 / arXiv:1903.01287.  
  https://arxiv.org/abs/1903.01287

## 3. Soundness rule for every cheap cone below

Let (mathcal Ksubseteqmathbb S_+^p).

Replacing

[
M_j^pmsucceq0
]

by the stronger condition

[
M_j^pminmathcal K
]

is **sound**: every feasible cheap certificate is still PSD, so the same S-procedure implication holds.

This is an inner approximation. It may destroy feasibility or make the envelope much looser, but it cannot create a false certificate if membership/equality is checked exactly.

The variants below are judged on this rule. Any shortcut that merely checks PSD on selected principal blocks without proving that the full matrix belongs to a PSD inner cone is rejected as unsound.

## 4. Gaussian readout is still exact

For one envelope

[
q(x)=x^	op A x+a^	op x+alpha
]

valid on

[
K_R={x:|x|_2le R},
qquad Xsim N(0,I_n),
]

define

[
p_R=P(chi_n^2le R^2)
]

and

[
	au_R
=rac1n E[|X|_2^2,1_{K_R}]
=P(chi_{n+2}^2le R^2).
]

Rotational symmetry gives

[
E[X1_{K_R}]=0,qquad
E[XX^	op1_{K_R}]=	au_R I_n.
]

Therefore, regardless of how the PSD certificate was obtained,

[
oxed{E[q(X)1_{K_R}]
=	au_Roperatorname{tr}(A)+p_Ralpha.}
]

For the specific input-quadratic structures:

- diagonal (A=operatorname{diag}(d)):
  [
  E[q1_{K_R}]=	au_Rsum_i d_i+p_Ralpha;
  ]
- block diagonal (A=oplus_s A_s):
  [
  E[q1_{K_R}]=	au_Rsum_soperatorname{tr}(A_s)+p_Ralpha;
  ]
- fixed-basis low-rank-plus-diagonal
  (A=D+UC U^	op):
  [
  E[q1_{K_R}]
  =	au_Rleft(operatorname{tr}D+
  operatorname{tr}(C,U^	op U)ight)+p_Ralpha.
  ]

The tail treatment from R381 is unchanged. If

[
0le f_j(x)leLambda_j|x|_2,
]

then

[
ho_R
=E[|X|_2,1_{{|X|_2>R}}]
=sqrt2,
rac{Gamma((n+1)/2,R^2/2)}{Gamma(n/2)}
]

gives a sound upper-tail addition (Lambda_jho_R).

Thus none of the low-cost cone substitutions breaks the analytic Gaussian expectation. The blocker is certificate construction/tightness, not readout.

## 5. Quadratic certificates really do escape the *specific* GELR affine theorem

R376's structural floor used the fact that a single global affine lower bound has no quadratic trace term; symmetry kills its linear expectation and (f(0)=0) forces the useful lower intercept to be nonpositive.

That argument does not extend to quadratic envelopes.

A concrete witness is one scalar ReLU on the ball. Let

[
f(x)=operatorname{ReLU}(c^	op x),qquad
a=R|c|_2,
]

and define

[
q_-(x)
=rac12c^	op x+
rac{(c^	op x)^2}{2R|c|_2}.
]

For (t=c^	op xin[-a,a]),

[
q_-(t)=rac t2+rac{t^2}{2a}.
]

If (tin[-a,0]), (q_-(t)=t(t+a)/(2a)le0=f(t)).  
If (tin[0,a]), (q_-(t)le t=f(t)).

Hence (q_-le f) on (K_R), while its quadratic matrix is

[
A_-=rac{cc^	op}{2R|c|_2}
]

with

[
operatorname{tr}(A_-)=rac{|c|_2}{2R}>0.
]

Its truncated Gaussian expectation is

[
E[q_-(X)1_{K_R}]
=rac{	au_R|c|_2}{2R}>0.
]

Therefore a quadratic certificate can have a positive certified lower expectation and **is not subject to R376's zero-lower affine obstruction**. If (c=e_i), the same witness is diagonal; for general (c), it is rank one.

This is only a separation theorem. It does **not** show a score improvement. In fact, the simple scalar witness is far too loose to establish the ARC target.

## 6. Variant A — diagonal PSD certificate

### Definition and soundness

Require

[
M_j^pm=operatorname{diag}(s),qquad sge0.
]

This is a subset of (mathbb S_+^p), so it is sound.

### Exact decision size

If the input quadratic envelope is also diagonal, its output-specific coefficients are

[
nquad	ext{quadratic}
+nquad	ext{linear}
+1
=oxed{2,049}.
]

Together with the frozen cheap QC multipliers, the minimal optimization-variable count is

[
49,153+2,049=oxed{51,202}
]

per lower/upper bound.

If the diagonal slack is introduced explicitly, add (p=17,409) variables:

[
oxed{68,611}
]

per bound.

### Fatal equality count

Diagonal PSD does not mean “check only the diagonal.” Exact soundness also requires every off-diagonal entry of (M_j^pm) to vanish:

[
oxed{151,527,936}
]

off-diagonal equalities per bound.

The ARC network has dense (1024	imes1024) weight matrices, so the QC matrix contains dense adjacent-layer cross-couplings. A diagonal certificate can survive only if the QC/envelope multipliers exactly cancel those couplings.

There are only 51,202 optimization variables in this frozen template against 151,527,936 off-diagonal equations. R387 does not claim a universal algebraic impossibility from dimension count alone, because the equations are structured, but there is no theorem or project artifact proving that such cancellation exists for the realized dense networks. Treating the off-diagonal entries as “ignored” would be unsound.

### Complexity/memory verdict

Raw diagonal storage is tiny: (17,409) float64 entries = **139,272 bytes**.

But the exact certificate-construction problem contains the 151,527,936 zero-equalities. No allowed-code algorithm with a deterministic iteration bound, exact FlopScope count (le B), 120-s wall proof, and 0.4-s residual proof is known.

**Variant A: CUT.** It is sound only with the huge cancellation system; dropping that system is unsound.

## 7. Variant B1 — disjoint block-diagonal PSD certificate

Partition the (p=17,409) lifted coordinates into disjoint blocks of size at most (b), and require

[
M_j^pm=operatorname{blkdiag}(Z_1,ldots,Z_q),
qquad Z_ssucceq0.
]

This is sound because block-diagonal PSD implies full PSD.

For (bmid1024), also restrict the input-envelope quadratic matrix to (1024/b) blocks of size (b). Its exact coefficient count is

[
d_{m env}(b)
=
rac{1024(b+1)}2+1024+1.
]

Representative exact counts are:

| (b) | envelope coeffs (d_{m env}) | QC+envelope vars | explicit PSD-block scalar entries | off-block zero equalities |
|---:|---:|---:|---:|---:|
| 1 | 2,049 | 51,202 | 17,409 | 151,527,936 |
| 8 | 5,633 | 54,786 | 78,337 | 151,467,008 |
| 32 | 17,921 | 67,074 | 287,233 | 151,258,112 |
| 64 | 34,305 | 83,458 | 565,761 | 150,979,584 |
| 128 | 67,073 | 116,226 | 1,122,817 | 150,422,528 |
| 256 | 132,609 | 181,762 | 2,236,929 | 149,308,416 |
| 512 | 263,681 | 312,834 | 4,465,153 | 147,080,192 |
| 1024 | 525,825 | 574,978 | 8,921,601 | 142,623,744 |

The explicit block storage in the table ranges from 0.13 MiB at (b=1) to 68.07 MiB at (b=1024), so **raw PSD-block memory is not the blocker**.

The blocker is structural: a disjoint block-diagonal matrix has zero cross-block entries. Dense adjacent-layer weight couplings do not respect any small disjoint partition. Soundness therefore again requires exact cancellation of roughly (1.4)–(1.5	imes10^8) off-block entries per bound.

A PSD check of already-constructed small blocks can be cheap; it does not solve the cancellation equations. Counting only block Cholesky/eigen work would therefore omit the dominant certificate-construction problem and would not be an all-in bound.

**Variant B1: CUT.** No bounded disjoint block size closes sound construction.

## 8. Variant B2 — bounded factor-width / overlapping small PSD blocks

The sound way to retain cross-block entries is not disjoint block diagonalization but a sum of embedded PSD blocks:

[
M=sum_{t=1}^{m_b}E_t^	op Z_tE_t,
qquad
Z_tsucceq0,quad |S_t|le b.
]

Every such (M) is PSD. This is the factor-width-(b) inner cone.

Primary sources:

- Ahmadi & Majumdar show that diagonally-dominant / scaled-diagonally-dominant inner PSD approximations lead to LP/SOCP alternatives:  
  https://arxiv.org/abs/1706.02586
- Kirschner & de Klerk treat constant factor-width cones and give an interior-point convergence/complexity analysis:  
  https://arxiv.org/abs/2301.06368
- Zheng, Sootla & Papachristodoulou develop block factor-width-two PSD inner approximations:  
  https://arxiv.org/abs/1909.11076

### Exact representation lower bound forced by dense layers

One dense ARC transition contains the complete bipartite coupling graph (K_{1024,1024}), i.e.

[
1024^2=1,048,576
]

cross-layer matrix positions.

A block of total size (b) can cover at most

[
leftlfloorrac{b^2}{4}ightfloor
]

such bipartite positions (split its support as evenly as possible between the two layers).

Therefore any fixed (b)-block cover that even gives every dense cross-layer coupling a place to appear needs at least

[
m_{m layer}(b)
ge
leftlceil
rac{1024^2}{lfloor b^2/4floor}
ightceil
]

blocks per dense transition, and at least

[
16m_{m layer}(b)
]

across the 16 transitions.

If every block is represented by a full (b	imes b) PSD variable, the scalar cone-coordinate count is at least

[
V_b
=
16m_{m layer}(b)rac{b(b+1)}2.
]

For even (b):

| (b) | blocks/transition | total blocks | (V_b) scalar PSD coordinates | float64 raw storage |
|---:|---:|---:|---:|---:|
| 2 | 1,048,576 | 16,777,216 | 50,331,648 | 384 MiB |
| 4 | 262,144 | 4,194,304 | 41,943,040 | 320 MiB |
| 8 | 65,536 | 1,048,576 | 37,748,736 | 288 MiB |
| 16 | 16,384 | 262,144 | 35,651,584 | 272 MiB |
| 32 | 4,096 | 65,536 | 34,603,008 | 264 MiB |
| 64 | 1,024 | 16,384 | 34,078,720 | 260 MiB |
| 128 | 256 | 4,096 | 33,816,576 | 258 MiB |

This is only a **representation lower bound**. It excludes:

- 49,153 QC multipliers;
- envelope coefficients;
- equality-constraint storage;
- dual variables;
- KKT/first-order workspaces;
- all 2048 objectives.

It also does not guarantee that the desired certificate lies in the factor-width cone; it only gives enough support to represent every dense edge.

### Solve complexity

For (b=2), factor width two is the scaled-diagonally-dominant/SOCP regime. For (b>2), it is a small-block conic program.

The literature provides polynomial/convergence analyses in ordinary conic models, but R387 needs a much stronger fact: an **exact worst-case all-in FlopScope operation schedule** under the challenge's allowed-code surface.

That fact is absent.

A generic conic iteration must at minimum read/update tens of millions of cone coordinates for one certificate. More importantly, the global equality/KKT system couples the blocks through the shared QC/envelope variables. Counting only independent (b	imes b) PSD projections is not an all-in solve bound.

No source gives a fixed iteration count to the envelope tightness needed for the ARC scorer, and no R387 run is permitted to measure one.

### Relation to chordal sparsity

Newton & Papachristodoulou and Xue, Lindemann & Alur show that network SDP sparsity can be exploited without losing the original SDP's expressiveness:

- https://proceedings.mlr.press/v144/newton21a.html
- https://arxiv.org/abs/2206.03482

But dense adjacent layers contain (K_{1024,1024}). Its treewidth is 1024, so any exact chordal completion has a clique of at least 1025 vertices. Thus an **exact** chordal reformulation cannot reduce all PSD blocks to a constant (bll1024). Constant-small blocks are an additional inner approximation, not a free exact decomposition.

**Variant B2: CUT.** It fixes the unsound zeroing problem of B1, but the sound representation itself has tens of millions of cone coordinates per certificate and no Phase-2 all-in solve bound.

## 9. Variant C — low-rank-plus-diagonal PSD certificate

### C1. Variable factor

Require

[
M=D+UU^	op,
qquad D=operatorname{diag}(d),quad dge0,
qquad Uinmathbb R^{p	imes r}.
]

Every feasible representation is PSD, hence sound.

The exact factor-variable count is

[
V_{m LR}(r)=p(r+1)=17,409(r+1).
]

Examples:

| rank (r) | factor variables | one float64 factor+diag |
|---:|---:|---:|
| 1 | 34,818 | 0.266 MiB |
| 8 | 156,681 | 1.195 MiB |
| 16 | 295,953 | 2.258 MiB |
| 32 | 574,497 | 4.383 MiB |
| 64 | 1,131,585 | 8.633 MiB |
| 1024 | 17,844,225 | 136.141 MiB |

However, imposing

[
M(	heta,lambda)=D+UU^	op
]

is quadratic and nonconvex in (U).

Burer & Monteiro's low-rank factorization replaces a PSD variable by (RR^	op) precisely to obtain a nonlinear/nonconvex optimization problem; it is a computational method, not a guarantee that an arbitrary small rank returns the SDP certificate.

Primary source:

- Samuel Burer, Renato D. C. Monteiro, “A Nonlinear Programming Algorithm for Solving Semidefinite Programs via Low-rank Factorization.”  
  https://optimization-online.org/2001/03/296/

R387 has no problem-specific theorem that every required QGME certificate has rank (le r), nor a global convergence/iteration bound for the nonconvex factor problem under the ARC allowed-code model.

So small (r) gives cheap storage but **not a certified construction algorithm**.

### C2. Fixed/cached low-rank basis

To keep convexity, freeze a basis (V=[v_1,ldots,v_r]) and require

[
M=D+sum_{k=1}^r s_kv_kv_k^	op,
qquad Dsucceq0	ext{ diagonal},quad s_kge0.
]

This is a sound PSD inner cone and is affine in ((d,s)).

It has only

[
p+r
]

cone coefficients per certificate after (V) is fixed.

But its off-diagonal part lies in an at-most-(r)-dimensional span of the fixed rank-one templates.

More concretely, restrict (M) to one adjacent-layer (1024	imes1024) cross block. A sum of (r) rank-one templates has matrix rank at most (r). A generic dense Gaussian ARC weight block is full rank 1024 almost surely. Unless the QC multipliers first cancel the dense coupling down to lower rank, representing that cross block requires

[
oxed{rge1024}.
]

No R381/R387 theorem provides such a cancellation.

At (r=1024), merely forming a dense (p	imes p) weighted Gram matrix by ordinary dense multiplication has the standard matmul-scale charge

[
2p^2r
=
oxed{620,694,079,488}
]

scalar FLOPs,

[
rac{620,694,079,488}{2^{41}}
=
oxed{0.2822589883580804}.
]

That is below the hard budget but already above the 0.1 scorer floor **before** QC assembly, solving, 2048 objectives, or output readout.

Repeating this independently for all 2048 bounds would be

[
oxed{578.0664,B}
]

of matmul-scale work.

This does not prove that every clever sparse implementation must form the dense Gram. It proves that the obvious fixed-basis low-rank route does not yield the requested all-in sub-budget theorem. A sparse equality check still has to reconcile the (16cdot1024^2) dense network couplings with the basis coefficients.

### Memory across outputs

If all 2048 output-specific (D,U) factors were resident simultaneously, raw float64 factor storage exceeds 8 GiB starting at (r=30):

- (r=28): 7.704 GiB;
- (r=29): 7.969 GiB, leaving less than the network itself plus solver workspace;
- (r=30): 8.235 GiB.

Streaming one objective avoids this memory wall, but then gives up simultaneous multi-output reuse and returns to 2048 solves.

**Variant C: CUT.** Variable-factor form is nonconvex with no certified small-rank/global iteration theorem; fixed-basis form needs rank comparable to the dense layer width absent an unproved cancellation theorem.

## 10. Variant D — shared/cached 2048 objectives

This is the only plausible way R381's arithmetic could be reduced enough, so R387 separates what is actually shareable from what is not.

### Shareable exactly

The following are identical across all output objectives for one MLP and can be cached once:

- network weights;
- lifted sparsity pattern;
- ReLU QC coefficient operators;
- input-ball QC;
- (p_R,	au_R,ho_R);
- symbolic block/chordal ordering;
- any fixed cone basis/cover.

This saves assembly and setup work.

### Not shareable by theorem

The lower/upper property changes with output coordinate and sign. Thus each of the 2048 certificates has a different property matrix and generally a different optimal multiplier/slack point.

For an interior-point SDP/SOCP, the numerical Newton/KKT matrix depends on the current primal/dual scaling point. Changing the objective changes the central path. A symbolic ordering can be reused, but a **numeric factorization is not guaranteed reusable across all 2048 solves**.

Warm starts and cached factorizations may work empirically; R387 is forbidden to benchmark them and found no primary-source theorem giving the required 2048-objective worst-case amortization for this QGME program.

### Forcing shared multipliers

One can deliberately impose

[
lambda_1^-=cdots=lambda_{1024}^-,
qquad
lambda_1^+=cdots=lambda_{1024}^+
]

(or even one common (lambda) for all 2048 bounds).

This remains sound **if every output-specific PSD condition is still independently satisfied**. It is simply a smaller feasible set.

For diagonal input quadratics, one common multiplier vector plus all envelope coefficients would contain

[
49,153+2048(2,049)
=
oxed{4,245,505}
]

scalar decision variables before certificate-cone variables.

For block-(64) input quadratics:

[
49,153+2048(34,305)
=
oxed{70,305,793}
]

variables before certificate-cone variables.

For unrestricted (1024	imes1024) input quadratics, the 2048 envelope coefficient arrays alone contain

[
2048(525,825)=oxed{1,076,889,600}
]

float64 scalars = **8.023 GiB**, already beyond the 8-GB process cap before weights or solver workspace.

The shared-multiplier restriction therefore makes small envelope parameterizations storable, but no theorem establishes that one common multiplier vector yields nontrivial lower and upper envelopes for all 1024 dense outputs.

### “One factorization + 2048 RHS” is not a valid worst-case solve model

If the problem were one fixed linear system, a factorization could be reused for multiple right-hand sides. QGME certificate optimization is not one fixed linear system: cone scaling/active constraints change with the objective.

Therefore R381's hypothetical “one factorization then cheap backsolves” cannot be promoted to an exact all-in bound without a new theorem that fixes a common feasible cone scaling point and proves all 2048 resulting certificates/tightness.

No such theorem was found.

**Variant D: CUT.** Symbolic/cache reuse is real but does not remove the 2048 optimization/certification burden in worst case.

## 11. Exact scorer implication

All variants above can, in principle, escape the *specific affine* GELR lower-bound theorem because a quadratic trace term can contribute to the Gaussian expectation.

That is not the same as escaping the actual fixed scorer.

R373/R381's correction remains binding: a population-mean interval does not itself certify error against the baked scorer target vector.

For a future frozen target-free estimator, the same-panel gate remains

[
S
=
rac1{100}sum_{i=1}^{100}
left[
rac1{1024}
|widehatmu_i-y_i|_2^2
ight]
maxleft(0.1,rac{F_i}{2^{41}}ight)
<
8.170397440117225	imes10^{-9}.
]

R387 performs no target read and no scorer run.

Therefore the precise answer is:

- **escape from R376's affine certificate-floor theorem:** YES, mathematically possible;
- **certified escape from the fixed scorer floor / score improvement:** NO evidence;
- **Phase-2 executable all-in certificate construction:** NO surviving variant.

## 12. Worst-case all-in gate

The user-requested all-in requirement is stronger than a representation-size estimate.

To declare a survivor, R387 requires one concrete allowed-code algorithm with all of:

1. sound lower and upper certificates for all 1024 outputs;
2. exact deterministic construction schedule;
3. worst-case (Fle2^{41});
4. peak process memory (le8) GB including workspaces;
5. wall (le120) s;
6. residual (le0.4) s;
7. no unmetered meaningful arithmetic;
8. a fixed-target scorer falsifier only after 1–7 pass.

No tested cone closes 1–6 simultaneously.

For diagonal/disjoint blocks, soundness introduces enormous exact cancellation systems.  
For factor-width blocks, sound support already costs tens of millions of cone coordinates and still leaves a globally coupled conic solve.  
For low-rank-plus-diagonal, cheap factors make construction nonconvex; a fixed convex basis needs rank comparable to the dense width absent an unproved cancellation theorem.  
For shared objectives, only symbolic data are safely reusable in worst case; numerical solution points/factorizations are objective-dependent.

Most importantly, no candidate has a finite, source-backed iteration/tolerance theorem translated into the challenge's FlopScope operations, and no static source can prove the 120-s/0.4-s wall gates. Under the official allowed-code rules, an external solver cannot be assumed.

This is not merely “timing unmeasured”: the requested exact worst-case all-in algorithm is missing.

## 13. Survivor decision

### No survivor

[
oxed{
	ext{NO_GO_NO_SOUND_LOW_COST_QGME_CERTIFICATE_CLOSES_ALL_PHASE2_GATES}
}
]

The narrow salvage attempt does produce two useful conclusions:

1. **R376's affine 4.607% structural argument is not universal.** Quadratic trace terms genuinely evade its proof.
2. **R381's real obstruction survives every cheap PSD structure tested.** The hard part is not Gaussian integration; it is constructing 2048 tight, sound certificates under the actual Phase-2 execution surface.

The closest mathematical subfamily is bounded factor-width / block-factor-width certificates: they remain convex and sound and can represent dense cross-layer couplings without the unsound zeroing of disjoint blocks. But their exact support size is already tens of millions of cone coordinates per certificate, and no allowed-code shared solver with a deterministic Phase-2 all-in bound exists. Therefore they are **not** a Phase-2 survivor.

## 14. Re-entry condition

Do not run a benchmark merely to test these variants.

QGME may be reopened only if a new result supplies one of the following:

- a closed-form certificate construction for the realized dense ReLU QC matrices; or
- a proof that all 2048 objectives share a common multiplier/factorization state with certified envelope widths; or
- a problem-specific low-rank theorem reducing every required PSD slack to a fixed (rll1024);

and, in the same result, an explicit FlopScope-expressible operation schedule proving (Fle2^{41}), memory (le8) GB, wall (le120) s, and residual (le0.4) s.

Only then is a frozen Mini-100 fixed-scorer falsifier justified.

## 15. Provenance and non-actions

Internal parent:

- R381 report:  
  https://github.com/tim8es/arc-whitebox/blob/research/r381-new-estimator-search-20260925/research/r381/R381_NEXT_ESTIMATOR.md
- R376 GELR report:  
  https://github.com/tim8es/arc-whitebox/blob/research/r376-new-estimator-frontier-20260924/research/r376/R376_NEW_ESTIMATOR_FRONTIER.md
- live history blob read by R387: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`.

Primary external sources used:

1. Fazlyab, Morari, Pappas — quadratic constraints/S-procedure neural-network SDP:  
   https://arxiv.org/abs/1903.01287
2. Newton, Papachristodoulou — chordal sparsity in neural-network verification SDP:  
   https://proceedings.mlr.press/v144/newton21a.html
3. Xue, Lindemann, Alur — Chordal-DeepSDP:  
   https://arxiv.org/abs/2206.03482
4. Ahmadi, Majumdar — DSOS/SDSOS PSD inner approximations:  
   https://arxiv.org/abs/1706.02586
5. Kirschner, de Klerk — constant factor-width cone IPM:  
   https://arxiv.org/abs/2301.06368
6. Zheng, Sootla, Papachristodoulou — block factor-width-two PSD cones:  
   https://arxiv.org/abs/1909.11076
7. Burer, Monteiro — low-rank SDP factorization:  
   https://optimization-online.org/2001/03/296/

Performed:

- source/repository reads;
- symbolic derivation;
- arithmetic/counting only;
- one report write on the isolated R387 branch.

Not performed:

- downloads: 0;
- installs: 0;
- estimator implementations: 0;
- solver runs: 0;
- synthetic runs: 0;
- benchmark/scorer runs: 0;
- Actions: 0;
- submissions: 0;
- private/holdout/full access: none;
- R320 edits: 0;
- main edits: 0;
- PR edits: 0;
- control edits: 0;
- queue edits: 0.
