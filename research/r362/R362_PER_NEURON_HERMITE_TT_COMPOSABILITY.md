# R362 — per-neuron Hermite/TT composability audit

**Status:** COMPLETE  
**Verdict:** **EVIDENCE_BASED_NO_GO_PER_NEURON_SCALAR_TT_NOT_CERTIFIED_COMPOSABLE**  
**Classification:** THEORY / PRIMARY-SOURCE DESK AUDIT ONLY — **0 estimator measurements**  
**Universal impossibility claim:** **NO**  
**Exact base:** \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`  
**Branch:** \`review/r362-per-neuron-hermite-tt-composability-20260924\`

## 1. Question and boundary

R352 closed the shared 1024-output block-TT/PCE route at the evidence level, but explicitly left one narrower possibility unresolved:

> store each first-layer ridge ReLU as its **own scalar TT/PCE over the same 1024 original Gaussian coordinates**, rather than placing the neuron index in one shared block TT.

R362 addresses only that scalar-carrier route.

The central result is:

> Separate scalar carriers do avoid the shared-output rank lower bound **at the first layer**, where one degree-\(p\) ridge ReLU has exact TT bond rank \(p+1\).  
> However, the very next **generic dense layer** forms, for each next-layer neuron, a weighted sum of all 1024 scalar ridge functions. Across a balanced \(512|512\) latent-coordinate cut, the degree-\(p\) coefficient slice of that scalar preactivation generically has exact unfolding rank at least
>
> \[
> \boxed{1024p-2046}
> \]
>
> for even \(p\ge4\), while the direct-sum TT construction gives the matching-scale upper bound
>
> \[
> \boxed{r\le1024(p+1)}.
> \]
>
> Thus the scalar route delays the shared-rank wall by one affine mix; it does not remove it.

After that mix, exact ReLU is not closed in finite-degree Hermite PCE, and any polynomial/TT-cross route requires recompression with layerwise error certificates that no audited primary source supplies for generic dense depth-16 ReLU composition.

R362 therefore returns an evidence-based feasibility NO-GO, **not** a universal impossibility theorem.

## 2. R352 starting evidence

R352:

- branch \`review/r352-tensorized-hermite-frontier-20260924\`
- head \`4e46b2bd8d04c15270b40872101555b6ac77f3e7\`
- report blob \`6f25841331f0199bd6ee7966a4bda796d79d2c59\`
- receipt blob \`432737e41f2b3576d1b5192a01a177c799c58d3b\`
- verdict \`EVIDENCE_BASED_NO_GO_NO_CERTIFIED_LOW_RANK_TT_HERMITE_PATH\`.

R352 established three facts used here:

1. one generic scalar degree-\(p\) ridge-ReLU PCE has exact TT bond rank \(p+1\);
2. the standardized single-ReLU Hermite squared-\(L^2\) tail reaches the R352 certificate scale \(1.89\times10^{-8}\) first at even degree
   \[
   p=17{,}118;
   \]
3. the cheaper degree
   \[
   p=214
   \]
   still has squared-\(L^2\) tail
   \[
   1.3492776924771553\times10^{-5},
   \]
   about \(713.9\times\) the \(1.89\times10^{-8}\) scale.

R362 does **not** re-use R352's shared-output block-rank argument as its conclusion; it derives the scalar-sum rank after the next dense layer.

## 3. Primary sources

Only primary sources are used for external TT/PCE facts.

### 3.1 Oseledets 2011 — TT ranks, addition, rounding and Hadamard products

I. V. Oseledets, **“Tensor-Train Decomposition,”** SIAM J. Sci. Comput. 33(5), 2295–2317 (2011).  
DOI: https://doi.org/10.1137/090752286  
Primary publisher: https://epubs.siam.org/doi/10.1137/090752286

Used facts:

- TT ranks are the ranks of the corresponding unfolding matrices; Theorem 2.1 shows those unfolding ranks are achievable as TT ranks.
- TT-SVD controls Frobenius error by the discarded unfolding errors.
- TT addition is implemented by block-diagonal/direct-sum cores, so ranks add before rounding.
- repeated addition therefore requires rounding; standard TT rounding costs \(O(dnr^3)\) when mode size is \(n\) and ranks are \(r\).
- elementwise/Hadamard multiplication multiplies TT ranks.

These are the exact operations needed to analyze “1024 separate scalar TTs, then dense linear combination, then polynomial/nonlinear update.”

### 3.2 Oseledets–Tyrtyshnikov 2010 — TT-cross is conditional on low-rank approximability

I. Oseledets and E. Tyrtyshnikov, **“TT-cross approximation for multidimensional arrays,”** Linear Algebra Appl. 432(1), 70–88 (2010).  
DOI: https://doi.org/10.1016/j.laa.2009.07.024  
Primary publisher: https://www.sciencedirect.com/science/article/pii/S0024379509003747

Used fact:

TT-cross interpolation error depends on closeness to a low-rank tensor and on the selected cross. The paper does not prove that generic deep dense ReLU coefficient tensors have uniformly small TT ranks.

### 3.3 Dolgov et al. 2015 — tensor-product PCE in TT and independent-vs-block carriers

S. Dolgov, B. N. Khoromskij, A. Litvinenko, H. G. Matthies, **“Polynomial Chaos Expansion of Random Coefficients and the Solution of Stochastic Partial Differential Equations in the Tensor Train Format,”** SIAM/ASA J. Uncertainty Quantification 3, 1109–1135 (2015).  
DOI: https://doi.org/10.1137/140972536  
Primary author manuscript: https://pure.mpg.de/rest/items/item_2125568_10/component/file_2241532/content

Used facts:

- a scalar tensor-product PCE TT core is \(r_{m-1}\times(p_m+1)\times r_m\);
- standard TT storage scales as \(O(Mpr^2)\);
- TT-cross ranks otherwise have to be fixed/guessed; rank-adaptive variants use SVD truncation;
- running \(L\) independent TT-cross approximations costs roughly \(L\) times the work, and adding \(L\) independent TT formats **sums their ranks**, followed by TT approximation/recompression;
- the authors therefore prefer block TT when several coefficient tensors must later be combined;
- their characteristic/level-set calculations can suffer rapid TT-rank growth when a non-coordinate-aligned nonsmooth set is introduced.

The last observation is supporting evidence about nonlinear level-set geometry, not a theorem that ReLU itself has the same rank growth.

### 3.4 Goel–Karmalkar–Klivans 2019 — exact Gaussian Hermite coefficients of ReLU

S. Goel, S. Karmalkar, A. R. Klivans, **“Time/Accuracy Tradeoffs for Learning a ReLU with respect to Gaussian Marginals,”** NeurIPS 2019.  
Primary proceedings PDF: https://proceedings.neurips.cc/paper_files/paper/2019/file/067a26d87265ea39030f5bd82408ce7c-Paper.pdf

Used facts:

- normalized probabilists' Hermites form the Gaussian orthogonal expansion used in the paper;
- Claim 1 gives the univariate ReLU Hermite coefficients;
- Claim 2 gives the multivariate ridge-ReLU expansion into products of univariate Hermites;
- nonzero even coefficients continue to arbitrarily high degree.

## 4. First layer: separate scalar TT/PCE carriers

Let

\[
\xi\sim N(0,I_d),\qquad d=1024,
\]

and let the \(i\)-th normalized first-layer ridge direction be \(a_i\in\mathbb R^d\).

Let \(P_p\) be the orthogonal Hermite projection of ReLU to even truncation degree \(p\), and define

\[
f_i^{(p)}(\xi)=P_p(a_i^\top\xi).
\]

For a generic coordinate split \(S|T\), both \(a_i^S\) and \(a_i^T\) are nonzero.

The top degree-\(p\) ridge term has the Hermite addition form

\[
H_p(a_i^\top\xi)
=
\sum_{t=0}^{p}
\gamma_{p,t}\,
H_t(\widehat a_i^S{}^\top\xi_S)
H_{p-t}(\widehat a_i^T{}^\top\xi_T),
\]

with nonzero coefficients for all \(t\) in the generic nondegenerate split. The \(p+1\) terms occupy distinct left/right degree sectors.

Therefore the scalar coefficient tensor has exact unfolding rank

\[
\boxed{r_{\mathrm{scalar}}=p+1}
\]

at any nondegenerate cut for the degree-\(p\) truncation. This reproduces the scalar result left open by R352.

### 4.1 Standard dense-core storage

Let

\[
q=p+1,\qquad r=q.
\]

A standard dense TT with \(d=1024\), boundary ranks \(r_0=r_d=1\), and uniform internal rank \(r\) stores

\[
S_{\mathrm{scalar}}
=
2qr+(d-2)qr^2
=
2q^2+1022q^3
\]

coefficients **per scalar neuron**.

This is standard dense-core TT storage. A special sparse automaton/ridge core can exploit additional zeros at the first layer, but that is not the standard dense-core representation to which ordinary TT rounding applies, and the ridge structure is not preserved by generic mixing.

## 5. Two degrees: certificate-scale and cheaper-but-inaccurate

### 5.1 Certificate-scale degree: \(p=17{,}118\)

R352 showed that this is the minimum even degree whose **standardized single-ReLU squared Gaussian \(L^2\) Hermite tail** is at or below \(1.89\times10^{-8}\).

\[
p=17118,\qquad q=r=17119.
\]

Standard dense-core storage:

\[
S_{\mathrm{scalar}}
=
5{,}127{,}269{,}213{,}994{,}820
\]

coefficients per first-layer neuron.

For 1024 separate scalar carriers:

\[
S_{1024}
=
5{,}250{,}323{,}675{,}130{,}695{,}680
\]

coefficients, or

\[
21{,}001{,}294{,}700{,}522{,}782{,}720
\]

bytes at float32, approximately **21.00 EB decimal**.

This is a standard dense-core storage count, not a claim that a hand-coded sparse ridge automaton must physically allocate those bytes.

The standard TT rounding scale from Oseledets is

\[
O(dqr^3)=O(dq^4)
\]

per scalar carrier. Across 1024 scalar carriers the substituted scale is

\[
O(1024^2 q^4)
=
O(2^{20}\cdot17119^4)
\approx O(9.0\times10^{22})
\]

arithmetic operations before any later dense mixing. This is an asymptotic standard-rounding scale, **not** an exact FlopScope lower bound.

### 5.2 Cheaper but inaccurate degree: \(p=214\)

R352's exact tail:

\[
T_{214}
=
1.3492776924771553\times10^{-5},
\]

about \(713.9\times\) the \(1.89\times10^{-8}\) reference scale.

Here

\[
q=r=215.
\]

Standard dense-core storage per scalar:

\[
S_{\mathrm{scalar}}
=
10{,}157{,}111{,}700
\]

coefficients.

Across 1024 separate scalar carriers:

\[
S_{1024}
=
10{,}400{,}882{,}380{,}800
\]

coefficients, or

\[
41{,}603{,}529{,}523{,}200
\]

float32 bytes, approximately **41.60 TB decimal**.

The standard all-1024 rounding scale is

\[
O(2^{20}\cdot215^4)
=
O(2{,}240{,}545{,}423{,}360{,}000),
\]

about \(1.019\times10^3\) times \(2^{41}\) at the leading substituted scale, before the second dense layer.

Again this is not an exact contest FLOP bill because the \(O(\cdot)\) constant and implementation are unspecified. It is sufficient to show that the ordinary dense-core rounding route is not a credible sub-\(2^{41}\) production path.

## 6. The decisive composability calculation: one generic dense layer recreates the large rank inside each scalar preactivation

Let the next-layer scalar preactivation be

\[
z_j^{(p)}(\xi)
=
\sum_{i=1}^{N} W_{ji} f_i^{(p)}(\xi),
\qquad N=1024.
\]

This is exactly the operation the scalar-carrier proposal must support.

Oseledets' TT addition rule gives an immediate constructive upper bound:

\[
r(z_j^{(p)})
\le
\sum_{i=1}^{1024} r(f_i^{(p)})
=
1024(p+1).
\]

The important question is whether generic cancellation/compression makes the exact rank dramatically smaller.

### 6.1 Generic lower bound from the degree-\(p\) slice

Take the balanced split

\[
|S|=|T|=512.
\]

For the top degree \(p\), decompose by left degree \(t\). The \(t\)-sector of the unfolding is

\[
M_t
=
U_t\,\operatorname{diag}(W_{j,:})\,V_{p-t}^{\top},
\]

where the columns of \(U_t\) are the degree-\(t\) symmetric ridge features of the 1024 first-layer directions restricted to \(S\), and the columns of \(V_{p-t}\) are the corresponding right-side features.

For generic dense directions and generic nonzero row weights,

\[
\operatorname{rank}M_t
=
\min\left(
1024,\,
\binom{511+t}{t},\,
\binom{511+p-t}{p-t}
\right).
\]

Different \(t\) occupy disjoint left- and right-degree sectors, so their matrix ranks add.

For even \(p\ge4\):

- \(t=0\) and \(t=p\): rank \(1\) each;
- \(t=1\) and \(t=p-1\): rank \(512\) each;
- every \(2\le t\le p-2\): both polynomial spaces have dimension \(>1024\), so generic rank is \(1024\).

Therefore

\[
\begin{aligned}
r_{512}(z_j^{(p)})
&\ge
1+512+(p-3)\cdot1024+512+1\\
&=
\boxed{1024p-2046}.
\end{aligned}
\]

Combined with the direct-sum upper bound,

\[
\boxed{
1024p-2046
\le
r_{512}(z_j^{(p)})
\le
1024(p+1)
}
\]

for the generic exact degree-\(p\) scalar preactivation.

This is the central R362 result.

It is not inherited from R352's output-block argument: the right polynomial dimension now limits the two endpoint sectors, which is why the lower bound is \(1024p-2046\), not R352's \(1024p-511\).

### 6.2 Numerical ranks

At \(p=214\):

\[
\boxed{217{,}090\le r_{512}\le220{,}160}.
\]

At \(p=17{,}118\):

\[
\boxed{17{,}526{,}786\le r_{512}\le17{,}529{,}856}.
\]

So independent scalar carriers are low-rank only **before** generic neuron mixing. Every generic next-layer neuron immediately becomes a high-rank scalar function of the original Gaussian coordinates.

## 7. Standard storage after the first generic dense mix

The same lower bound holds at the neighboring balanced cut for generic directions, so one central standard TT core of a next-layer scalar preactivation must have at least approximately

\[
q\,r^2
\]

entries.

### \(p=214\)

Using \(q=215\) and \(r\ge217{,}090\):

\[
q r^2
=
10{,}132{,}534{,}641{,}500
\]

entries in **one central core of one next-layer scalar**.

At float32 this is

\[
40{,}530{,}138{,}566{,}000
\]

bytes, approximately **40.53 TB** for that one core.

For 1024 next-layer neurons, merely replicating this one-core lower-bound scale is about **41.5 PB**.

### \(p=17{,}118\)

Using \(q=17{,}119\) and \(r\ge17{,}526{,}786\), one central core requires at least

\[
5{,}258{,}755{,}266{,}397{,}817{,}724
\]

entries, about **21.04 EB float32** for one next-layer scalar core.

Across 1024 next-layer neurons this one-core scale is about **21.54 ZB**.

These are storage consequences of the exact generic rank result for the standard dense-core format. They are not a universal lower bound on every possible structured representation.

## 8. What the next ReLU does

The scalar route is not closed after the dense sum.

### 8.1 Exact ReLU

Goel–Karmalkar–Klivans give nonzero even Hermite coefficients of ReLU at arbitrarily high degree.

Therefore, for a generic preactivation that crosses zero, exact

\[
\operatorname{ReLU}(z_j^{(p)}(\xi))
\]

does not remain in any finite-degree Hermite PCE.

A finite tensor-product PCE route must therefore truncate/reproject after every ReLU.

The first-layer standard-Gaussian tail numbers do **not** automatically certify later layers: after one ReLU and dense mixing, \(z_j\) is generally not a standard Gaussian scalar. The later polynomial/ReLU approximation error must be controlled under the actual induced distribution of \(z_j(\xi)\), with \(\xi\) still distributed as the original Gaussian vector.

### 8.2 Polynomial ReLU surrogate

Suppose a polynomial surrogate

\[
Q_m(z)=\sum_{k=0}^m b_k z^k
\]

is used.

If \(z\) has TT rank \(R\), Oseledets' Hadamard rule implies that before recompression

\[
r(z^k)\le R^k.
\]

Additions then sum ranks.

Thus exact polynomial evaluation is not rank-stable. A practical TT implementation must round after products/additions.

There is an additional degree issue: if \(z\) already has coordinate polynomial degree \(p\), then \(z^m\) has coordinate degree up to \(mp\). Projecting back to a fixed local mode size \(p+1\) introduces another truncation error.

A certified layer therefore needs to account for all three errors:

1. scalar polynomial approximation error
   \[
   \|\operatorname{ReLU}(z)-Q_m(z)\|_{L^2};
   \]
2. Hermite/PCE degree reprojection error after powers/products;
3. TT rounding error after rank growth.

TT-SVD provides a Frobenius coefficient-tensor error bound from discarded singular values. With an orthonormal Hermite basis that coefficient Frobenius norm equals the Gaussian \(L^2\) function error, so such errors can in principle enter a rigorous network error budget.

What is missing is a source-backed theorem that those discarded singular values decay fast enough after **generic dense sum + repeated ReLU** to keep ranks small.

### 8.3 TT-cross / rank-adaptive approximation

TT-cross is the only obvious non-polynomial escape: approximate the post-ReLU scalar function directly and let ranks adapt numerically.

But the primary sources do not give the needed guarantee:

- Oseledets–Tyrtyshnikov state cross accuracy in terms of closeness to low rank and cross quality; they do not prove low rank for this function class.
- Dolgov et al. explicitly describe fixed TT ranks as something that otherwise must be guessed and motivate SVD-adaptive rank selection.
- The same Dolgov paper warns that nonsmooth/non-axis-aligned characteristic or level-set functions can show rapid TT-rank growth and slow singular-value decay.

Therefore TT-cross leaves a **numerical hope**, not a pre-run certificate.

## 9. Error propagation to the final mean

Define the normalized layer function error

\[
e_\ell
=
\left(
\frac1{1024}
\mathbb E_\xi
\|h_\ell(\xi)-\widetilde h_\ell(\xi)\|_2^2
\right)^{1/2}.
\]

Let \(\tau_{\ell+1}\) be the normalized \(L^2\) error introduced by the chosen per-neuron ReLU/PCE/TT reprojection at the next layer, measured relative to the ReLU of the approximate preactivation.

Since ReLU is 1-Lipschitz,

\[
e_{\ell+1}
\le
\|W_\ell\|_2 e_\ell+\tau_{\ell+1}.
\]

Hence

\[
e_L
\le
\sum_{k=1}^{L}
\tau_k
\prod_{j=k}^{L-1}\|W_j\|_2.
\]

By Jensen,

\[
\frac1{1024}
\left\|
\mathbb E h_L-\mathbb E\widetilde h_L
\right\|_2^2
\le
e_L^2.
\]

So the **form** of a propagated final-mean certificate is available.

The missing object is not another Lipschitz inequality. It is a theorem/certificate providing, for each generic dense layer, ranks and computable \(\tau_\ell\) small enough to make the bound useful while keeping storage/work within budget.

## 10. Can a source-backed width-1024/depth-16 sub-\(2^{41}\) path be certified?

**No, not from the audited primary sources.**

There are two levels to the NO-GO.

### 10.1 Standard dense-core scalar TT route

Already at the first layer:

- certificate-scale \(p=17118\) standard storage is about 21 EB across 1024 carriers;
- even inaccurate \(p=214\) standard storage is about 41.6 TB;
- the ordinary all-1024 TT-rounding scale at \(p=214\) is already about \(10^3\times2^{41}\).

After one generic dense mix, each scalar preactivation has exact central rank \(r=\Theta(1024p)\), making standard dense cores drastically larger.

This is not a credible standard-TT production path.

### 10.2 Structured/sparse first-layer escape

One can object that a first-layer ridge TT has special sparse cores and should not be materialized as dense standard cores.

R362 agrees.

But that only rescues the **first ridge layer**. Generic dense mixing destroys the single-ridge form and creates the exact rank sandwich in §6 for each next-layer scalar.

To continue below \(2^{41}\), one would need aggressive approximate recompression after every affine sum and every ReLU.

No primary source audited here provides the required rank/error theorem for that composition.

## 11. Exact missing theorem / certificate

A future R362 successor would need a result of roughly the following form.

For every layer \(\ell\le16\), every neuron \(j\le1024\), and generic dense weights \(W_\ell\), for

\[
h_{\ell+1,j}(\xi)
=
\operatorname{ReLU}
\left(
\sum_{i=1}^{1024}
W_{\ell,ji} h_{\ell,i}(\xi)+b_{\ell,j}
\right),
\]

there must be a constructible TT/PCE approximation \(\widetilde h_{\ell+1,j}\) with:

1. an a priori or certifiable TT-rank bound
   \[
   r_{\ell+1,j}\le R_\ell(\varepsilon)
   \]
   after generic dense mixing and ReLU;
2. a computable Gaussian-\(L^2\) residual
   \[
   \tau_{\ell+1,j}
   \]
   including polynomial/ReLU approximation, PCE truncation and TT rounding;
3. a proof that the residuals satisfy the depth-16 final-mean envelope
   \[
   \left(
   \sum_k\tau_k\prod_{j>k}\|W_j\|_2
   \right)^2
   \le
   \text{required final-mean MSE};
   \]
4. an all-in storage and arithmetic bound for all 1024 neurons and all 16 layers that maps to a credible Phase-2 bill below
   \[
   2^{41}=2{,}199{,}023{,}255{,}552
   \]
   FLOPs and the residual-time envelope.

No such theorem is present in Oseledets 2011, Oseledets–Tyrtyshnikov 2010, Dolgov et al. 2015, or Goel–Karmalkar–Klivans 2019.

## 12. Decision

**R362 verdict:**

\[
\boxed{
\text{EVIDENCE\_BASED\_NO\_GO\_PER\_NEURON\_SCALAR\_TT\_NOT\_CERTIFIED\_COMPOSABLE}
}
\]

Exact reason:

1. each first-layer scalar ridge has exact rank \(p+1\), so the scalar carrier is genuinely cheaper than R352's shared block at that point;
2. a single generic 1024-way dense sum produces, inside **each** next-layer scalar preactivation,
   \[
   1024p-2046
   \le r
   \le1024(p+1),
   \]
   recreating the large-rank barrier one layer later;
3. exact ReLU is not finite-degree Hermite closed;
4. polynomial evaluation multiplies ranks before mandatory rounding;
5. TT-cross/rounding can only rescue the path if generic deep-ReLU unfoldings have rapid singular-value decay, for which no source-backed rank theorem or propagated final-mean certificate was found;
6. consequently there is no auditable width-1024/depth-16 all-in sub-\(2^{41}\) path.

This is **not** a universal impossibility result. Special weight structure, a different coordinate transformation, or a future theorem on approximate TT ranks could change the conclusion.

## 13. Execution accounting

R362 performed static source/repository research only.

- estimator implementation: **NO**
- code/test execution: **0**
- synthetic runs: **0**
- official/public benchmark runs: **0**
- Actions: **0**
- dataset/dependency downloads or installs: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- submission: **0**
- leaderboard access/edit: **0**
- PR/main/control/queue edits: **0**
- R320 edits: **0**
- estimator measurements: **0**
