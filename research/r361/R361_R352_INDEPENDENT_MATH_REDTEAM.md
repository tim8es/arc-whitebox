# R361 — independent mathematical red-team of R352 block-TT Hermite/PCE no-go

**Status:** COMPLETE  
**Verdict:** **PASS_WITH_NONMATERIAL_CORRECTIONS — R352 NARROW VERDICT CONFIRMED**

Exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

Audited R352:
- branch `review/r352-tensorized-hermite-frontier-20260924`
- live head `4e46b2bd8d04c15270b40872101555b6ac77f3e7`
- report blob `6f25841331f0199bd6ee7966a4bda796d79d2c59`
- receipt blob `432737e41f2b3576d1b5192a01a177c799c58d3b`
- exact base→R352: ahead 1, behind 0, exact merge-base `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`, exactly the two R352 files.

R361 is mathematics/provenance only. It does not modify R352.

## 1. Primary sources freshly checked

1. Surbhi Goel, Sushrut Karmalkar, Adam R. Klivans, “Time/Accuracy Tradeoffs for Learning a ReLU with respect to Gaussian Marginals,” NeurIPS 2019.  
   Primary proceedings PDF: https://proceedings.neurips.cc/paper_files/paper/2019/file/067a26d87265ea39030f5bd82408ce7c-Paper.pdf

2. I. V. Oseledets, “Tensor-Train Decomposition,” SIAM J. Sci. Comput. 33(5), 2295–2317 (2011).  
   DOI: https://doi.org/10.1137/090752286

3. S. Dolgov, B. N. Khoromskij, A. Litvinenko, H. G. Matthies, “Polynomial Chaos Expansion of Random Coefficients and the Solution of Stochastic Partial Differential Equations in the Tensor Train Format,” SIAM/ASA J. Uncertainty Quantification 3 (2015).  
   DOI: https://doi.org/10.1137/140972536  
   Author manuscript: https://arxiv.org/abs/1503.03210

Only primary-paper claims are used for literature facts.

## 2. Normalized ReLU Hermite coefficients — PASS

Goel–Karmalkar–Klivans define normalized probabilists' Hermites
\[
\bar H_i=H_i/\sqrt{i!}
\]
and their Claim 1 gives
\[
\widehat{\mathrm{ReLU}}_0=\frac1{\sqrt{2\pi}},\qquad
\widehat{\mathrm{ReLU}}_1=\frac12,
\]
and for \(i\ge2\),
\[
\widehat{\mathrm{ReLU}}_i=
\frac{H_i(0)+iH_{i-2}(0)}{\sqrt{2\pi\,i!}}.
\]

Using
\[
H_{2m+1}(0)=0,\qquad
H_{2m}(0)=(-1)^m\frac{(2m)!}{m!2^m},
\]
one gets, for \(m\ge1\),
\[
\widehat{\mathrm{ReLU}}_{2m}
=
(-1)^{m-1}
\frac{(2m-2)!}
{\sqrt{2\pi(2m)!}(m-1)!2^{m-1}},
\]
and hence
\[
\boxed{
\widehat{\mathrm{ReLU}}_{2m}^{\,2}
=
\frac1{2\pi}
\frac{\binom{2m}{m}}{4^m(2m-1)^2}
}.
\]

All odd coefficients above degree 1 vanish. R352's normalization and squared-coefficient formula are correct.

For a generic normalized ridge direction \(a\), \(\|a\|_2=1\), the multivariate coefficient formula used in R352 follows from the probabilists' Hermite generating function:
\[
\bar H_p(a^\top\xi)
=
\sum_{|\alpha|=p}
\sqrt{\frac{p!}{\alpha!}}\,a^\alpha
\prod_q\bar H_{\alpha_q}(\xi_q).
\]

Therefore
\[
C_i[\alpha]
=
c_p\sqrt{\frac{p!}{\alpha!}}a_i^\alpha,\qquad |\alpha|=p,
\]
is correct.

## 3. Parseval recurrence and thresholds — PASS

Let
\[
a_m=\frac{\binom{2m}{m}}{4^m}.
\]
Then exactly
\[
a_0=1,\qquad
a_m=a_{m-1}\frac{2m-1}{2m},
\]
and
\[
c_{2m}^2=\frac{a_m}{2\pi(2m-1)^2}.
\]

Because normalized Hermites are orthonormal,
\[
T_{2M}=\sum_{m=M+1}^{\infty}c_{2m}^2
\]
is the best degree-\(2M\) squared Gaussian \(L^2\) projection error for a standardized ReLU.

Fresh desk arithmetic reproduces R352's threshold values:

\[
\boxed{
T_{214}
=
1.34927769247715525935054914194184098\times10^{-5}
}
\]

\[
\boxed{
T_{17116}
=
1.89027113678643304205007617948592579\times10^{-8}
}
\]

\[
\boxed{
T_{17118}
=
1.88993987446720191639112151744281044\times10^{-8}
}
\]

Independent asymptotic/Euler–Maclaurin cross-checks give respectively
\(1.3492776859847975693\times10^{-5}\),
\(1.8902711367864328099\times10^{-8}\), and
\(1.8899398744672016844\times10^{-8}\), validating the reported values at the precision needed for the gate.

The local crossing is also internally exact:
\[
T_{17116}-T_{17118}
=
c_{17118}^2
=
3.31262319231125658954662043115305\times10^{-12},
\]
matching
\[
\frac{\binom{17118}{8559}}
{4^{8559}\,2\pi\,17117^2}.
\]

Relative to the target \(1.89\times10^{-8}\),
\[
T_{17116}-1.89\times10^{-8}
=
2.71136786433042050076\times10^{-12}>0,
\]
while
\[
1.89\times10^{-8}-T_{17118}
=
6.01255327980836088785\times10^{-13}>0.
\]

Since the degree-17117 coefficient is zero, degree 17117 has the same tail as degree 17116. Thus
\[
\boxed{p=17118}
\]
is indeed the smallest integer degree, hence also the smallest even degree, for which this single-ReLU squared \(L^2\) tail is at or below \(1.89\times10^{-8}\).

This is a function-space threshold, not a necessity theorem for final network mean.

## 4. Generic central-cut block-PCE exact rank — PASS

Consider the fixed total-degree-\(p\) coefficient slice for \(n=1024\) neurons. Split latent variables \(S|T\), \(|S|=s\), and place the output/neuron label \(i\) on the \(T\)-side.

For \(\alpha=(\beta,\gamma)\), \(|\beta|=j\), \(|\gamma|=p-j\),
\[
M_j[\beta,(\gamma,i)]
=
c_p\sqrt{p!}\,
\frac{a_{i,S}^{\beta}}{\sqrt{\beta!}}\,
\frac{a_{i,T}^{\gamma}}{\sqrt{\gamma!}}.
\]

For fixed \(j\),
\[
M_j=U_jR_j,
\]
where the \(i\)-th column of \(U_j\) is the degree-\(j\) Veronese feature vector of \(a_{i,S}\), and row \(i\) of \(R_j\) has support only inside the output-labelled column block \(i\).

For generic dense rows with nonzero complementary restrictions, \(R_j\) has row rank \(n\), so
\[
\operatorname{rank}M_j=\operatorname{rank}U_j.
\]

The degree-\(j\) homogeneous polynomial space in \(s\) variables has dimension
\[
D_j=\binom{s+j-1}{j}.
\]

For row restrictions in generic position under the degree-\(j\) Veronese map,
\[
\operatorname{rank}M_j=\min(n,D_j).
\]

### Why the degree-sector ranks add

For fixed total degree \(p\):
- row sectors with different \(j=|\beta|\) are disjoint;
- corresponding column sectors have different right degree \(p-j\) and are also disjoint.

After row/column permutation the fixed-\(p\) unfolding is block diagonal across \(j\). Therefore
\[
\operatorname{rank}M^{(p)}
=
\sum_{j=0}^{p}\operatorname{rank}M_j.
\]

The full degree-\(\le p\) tensor contains this as a submatrix, so its unfolding rank is at least that amount.

At \(n=1024,s=512,p\ge2\):
\[
D_0=1,\qquad D_1=512,\qquad D_2=\binom{513}{2}=131328>1024.
\]
Hence
\[
r_{512}\ge1+512+(p-1)1024
=
\boxed{1024p-511}.
\]

At the adjacent \(s=511\) cut,
\[
r_{511}\ge
\boxed{1024p-512}.
\]

R352's formulas are correct.

### Genericity assumptions

This is not universal over every dense-looking matrix. It assumes:
1. even \(p\ge2\), so the top ReLU coefficient \(c_p\neq0\);
2. normalized generic first-layer row directions;
3. the restricted rows \(a_{i,S}\) have generic Veronese rank;
4. complementary restrictions needed by \(R_j\) are nonzero;
5. the representation is the shared-coordinate standard block-TT/PCE candidate R352 defined.

The rank-deficient exceptions form an algebraic exceptional set; no claim is made that every possible contest weight matrix saturates the generic rank.

### Output-mode ordering

Wherever a single output/block mode is placed in a TT ordering, one of its two sides contains at least 512 of the 1024 latent coordinates. Choose a cut in that side leaving exactly 512 latent coordinates on the side without the output mode; transpose the unfolding if needed. Matrix rank is unchanged.

The adjacent 511-coordinate cut exists on the same side, so one latent core can have the neighboring bond lower bounds \(r_{511}\) and \(r_{512}\).

Thus output-mode placement does not invalidate the R352 standard block-TT exact-rank argument.

## 5. Exact rank is not approximate TT rank

Oseledets Theorem 2.1 supports the exact-rank/unfolding connection. Theorem 2.2 separately shows that approximate TT error is governed by discarded unfolding singular values.

Therefore
\[
r_{512}\ge1024p-511
\]
is an **exact generic rank lower bound**.

It is **not** an \(\varepsilon\)-rank lower bound. A high exact rank can still have low approximate rank if singular values decay rapidly.

R352 explicitly leaves that escape open. R361 confirms that the defensible terminal statement is only that no certified generic-dense approximate-rank/error/cost theorem is available for this depth-16 ReLU PCE state.

## 6. Exact core-element / byte arithmetic

### p = 214

\[
r_{511}=218624,\quad r_{512}=218625,\quad p+1=215.
\]

One standard dense core has exactly
\[
218624\times215\times218625
=
\boxed{10,276,284,480,000}
\]
entries.

Float32:
\[
\boxed{41,105,137,920,000\text{ bytes}}
=
41.10513792\text{ TB decimal}
=
37.38490515388548\text{ TiB}.
\]

R352 Markdown is correct.

### p = 17118

\[
r_{511}=17,528,320,\quad
r_{512}=17,528,321,\quad
p+1=17,119.
\]

Exact core entries:
\[
\boxed{5,259,676,132,688,775,680}.
\]

Exact float32 bytes:
\[
\boxed{21,038,704,530,755,102,720}
=
21.03870453075510272\text{ EB decimal}.
\]

Exact float64 bytes:
\[
\boxed{42,077,409,061,510,205,440}
=
42.07740906151020544\text{ EB decimal}.
\]

These exact integers agree with the R352 Markdown report.

### R352 receipt precision defect

R352's JSON receipt stores the large p=17118 values as JSON numbers and loses low digits:

- receipt entries: `5259676132688775000`  
  exact: `5259676132688775680`  
  difference: **680**;

- receipt float32 bytes: `21038704530755100000`  
  exact: `21038704530755102720`  
  difference: **2720 bytes**;

- receipt float64 bytes: `42077409061510200000`  
  exact: `42077409061510205440`  
  difference: **5440 bytes**.

This is a serialization/precision defect in the receipt, not a derivation error in the Markdown report. Exact large integers should be serialized as strings.

## 7. O(d n r^3) scale arithmetic — arithmetic PASS, source/interpretation correction

R352 attributes “standard dense-core TT rank reduction \(O(Mpr^3)\)” to Dolgov et al. That attribution is imprecise.

The primary source for standard TT rounding is **Oseledets 2011**, which gives
\[
O(dnr^3).
\]

For the PCE tensor:
- \(d=M=1024\);
- physical mode size \(n=p+1\).

Dolgov et al. instead give \(O(Mpr^2)\) storage asymptotically and a more detailed block-TT-cross cost in Statement 6.

Thus the R352 substitution
\[
1024(p+1)r^3
\]
is a valid **Oseledets-style standard dense-TT rounding scale**, but not the Dolgov block-TT-cross complexity.

Fresh exact arithmetic:

### p=2, r=1537
\[
1024\cdot3\cdot1537^3
=
\boxed{11,154,312,662,016}
\]
and
\[
/2^{41}
=
\boxed{5.0723941340111196041}.
\]

### p=214, r=218625
\[
1024\cdot215\cdot218625^3
=
\boxed{2,300,582,882,070,000,000,000}
\]
and
\[
/2^{41}
=
\boxed{1,046,183,971.1160791921}.
\]

### p=17118, r=17,528,321
\[
1024\cdot17119\cdot17528321^3
=
\boxed{94,405,935,994,351,499,235,467,426,816}
\]
and
\[
/2^{41}
=
\boxed{42,930,849,301,388,434.1214486\ldots}.
\]

R352 Markdown's displayed scales are correct.

R352 receipt's p=17118 ratio `42930849301388430` is only a rounded floating serialization of the exact value above.

### Important interpretation

These \(O(dnr^3)\) substitutions are **not runtime/FLOP lower bounds**.

The source expression is an asymptotic standard-rounding complexity in terms of representative/max rank \(r\). Plugging a central exact-rank lower bound into that \(O(\cdot)\) expression produces an illustrative dense-rounding scale, not a proof that every implementation spends that many operations.

R352 already labels these values “operation-count scale” and “NOT an exact FlopScope lower bound.” R361 confirms and strengthens that caveat.

The exact one-core dense storage calculation is a concrete exact-representation obstruction; the \(O(dnr^3)\) ratios are supporting scale only.

## 8. Minor p=214 ratio correction

From the verified tail,
\[
\frac{T_{214}}{1.89\times10^{-8}}
=
\boxed{713.9035409932038409\ldots}.
\]

R352 Markdown says “about 713.9×”, which is correct.

R352 receipt stores `713.9035440471721`; that differs by about \(3.05\times10^{-6}\) in the ratio. This is nonmaterial.

## 9. Function-L2 to final-mean envelope — PASS AS SUFFICIENT ONLY

Define
\[
e_\ell^2=
\frac1n\mathbb E\|h_\ell-\tilde h_\ell\|_2^2.
\]

If \(\tau_{\ell+1}\) is the normalized \(L^2\) reprojection error at the next layer, then:
- a dense linear map contributes \(\|W_\ell\|_2\);
- ReLU is 1-Lipschitz;
- triangle inequality applies in vector \(L^2\).

Therefore
\[
e_{\ell+1}
\le
\|W_\ell\|_2e_\ell+\tau_{\ell+1}.
\]

Unrolling:
\[
e_L
\le
\sum_{k=1}^{L}
\tau_k
\prod_{j=k}^{L-1}\|W_j\|_2.
\]

Jensen gives:
\[
\frac1n
\|\mathbb E h_L-\mathbb E\tilde h_L\|_2^2
\le e_L^2.
\]

This is correct.

It is a **sufficient upper envelope**, not a lower bound and not a necessity theorem. Downstream contraction, cancellation, or output-specific insensitivity can make final-mean error much smaller than function-space error.

Therefore p=17118 is not “required by the final mean.” It is the degree required for the standalone standardized-ReLU squared \(L^2\) tail to cross the chosen \(1.89\times10^{-8}\) certificate scale, and hence for that conservative unit-gain certificate.

## 10. Red-team decision

No material mathematical error overturns R352's narrow conclusion.

Confirmed:
- normalized ReLU Hermite formula: **PASS**;
- tail recurrence and 214 / 17116 / 17118 values: **PASS**;
- 17118 threshold crossing for single-ReLU squared \(L^2\): **PASS**;
- generic exact central-cut rank \(r\ge1024p-511\): **PASS**;
- degree-sector rank additivity: **PASS**;
- standard one-output-mode ordering argument: **PASS**;
- exact Markdown core/byte arithmetic: **PASS**;
- final-mean envelope: **PASS AS SUFFICIENT**.

Corrections:
1. standard \(O(dnr^3)\) rounding source is Oseledets 2011, not Dolgov block-TT-cross;
2. those \(O(dnr^3)\) numbers are illustrative scales, not cost lower bounds;
3. R352 JSON receipt loses exact low digits for several p=17118 integers;
4. R352 receipt's p=214 tail/target ratio has a tiny arithmetic discrepancy;
5. exact generic TT rank must not be promoted to approximate-rank necessity;
6. the L2→mean envelope must not be promoted to a necessity theorem.

### Narrow verdict confirmed

\[
\boxed{\text{NO CERTIFIED APPROXIMATE-RANK / ERROR / COST PATH}}
\]

for the concrete R352 block-TT Hermite/PCE proposal, under the evidence reviewed.

This is **not** a universal impossibility theorem for tensorized Hermite/PCE methods.

A future reopening would need a generic-dense approximate unfolding-rank/singular-value certificate through repeated ReLU, composable layerwise \(L^2\) residual control, and a resulting Phase-2 cost/residual bound.

## 11. Execution accounting

- implementation: **NO**
- project/script code execution: **NO**
- synthetic/official/benchmark run: **NO**
- dataset/dependency download: **NO**
- Actions: **NO**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submission: **NO**
- edits to R352/R320/main/PR/control/queue: **NO**
- R361 artifacts: exactly this report + one JSON receipt
