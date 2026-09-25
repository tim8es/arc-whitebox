# R383 — independent red-team of the R376 GELR mathematical boundary

**Status:** COMPLETE  
**Verdict:** **PASS_ON_THE_R376_ONE_SIDED_GELR_ALGEBRA_WITH_MATERIAL_SCOPE_CORRECTION_AND_CONCRETE_ESCAPE**  
**Universal / broader affine-family impossibility:** **NOT PROVED**  
**Mode:** independent primary-source desk audit; no estimator, benchmark, synthetic, scorer, or submission execution  
**Branch:** \`research/r383-gelr-independent-redteam-20260925\`  
**Exact branch base:** \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`

## 1. Audited artifact and immutable provenance

R383 audits the completed R376 GELR artifact independently:

- R376 branch: \`research/r376-new-estimator-frontier-20260924\`
- R376 head: \`3e61563bf46d09081dfae133407219763f27bf7f\`
- exact R376 base / merge-base:
  \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`
- R376 report:
  \`research/r376/R376_NEW_ESTIMATOR_FRONTIER.md\`
  - Git blob SHA-1: \`999de9d6203ac263a5da1c9d1b1e20daba43488d\`
- R376 receipt:
  \`research/r376/R376_RECEIPT.json\`
  - Git blob SHA-1: \`8d19fb3fdd4fc53f1807874e76bdc04e1c6af633\`
- R376 branch is exactly two commits ahead of the exact base and changes only those two R376 files.

R383 does not modify R376, R320, main, any PR, control state, or queue state.

## 2. Primary sources

R383 checked the following primary sources.

1. **Weng et al., ICML 2018, Fast-Lin**, “Towards Fast Computation of Certified Robustness for ReLU Networks.”  
   Primary proceedings page/PDF:
   [PMLR 80:5276–5285](https://proceedings.mlr.press/v80/weng18a.html) /
   [paper PDF](https://proceedings.mlr.press/v80/weng18a/weng18a.pdf).  
   Theorem 3.5 constructs explicit affine lower/upper output bounds valid on the whole bounded input domain.

2. **Zhang et al., NeurIPS 2018, CROWN**, “Efficient Neural Network Robustness Certification with General Activation Functions.”  
   Primary proceedings:
   [NeurIPS paper](https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html) /
   [paper PDF](https://proceedings.neurips.cc/paper/2018/file/d04863f100d59b3eb688a11f95b0ae60-Paper.pdf).  
   Definition 3.1 and Theorem 3.2 propagate affine activation relaxations to affine network-output bounds; CROWN permits different/adaptive lower and upper slopes.

3. **Weng et al., ICML 2019, PROVEN**, “PROVEN: Verifying Robustness of Neural Networks with a Probabilistic Approach.”  
   Primary proceedings:
   [PMLR 97:6727–6736](https://proceedings.mlr.press/v97/weng19a.html) /
   [paper PDF](https://proceedings.mlr.press/v97/weng19a/weng19a.pdf).  
   Theorem 3.1 turns sound affine network bounds into distributional probability bounds. Corollary 3.3 explicitly uses that an affine function of a multivariate Gaussian is Gaussian with analytically available CDF. This is directly relevant to the escape in §8.

4. **Bunel et al., JMLR 2020**, “Branch and Bound for Piecewise Linear Neural Network Verification.”  
   [JMLR 21(42):1–39](https://www.jmlr.org/papers/v21/19-468.html) /
   [paper PDF](https://www.jmlr.org/papers/volume21/19-468/19-468.pdf).  
   This source is used only to distinguish explicit branch/subdomain or activation-region splitting from the non-enumerative analytic transformations considered below.

5. **Official WhestBench 0.16.1 source**, pinned commit
   \`4d08668b485c8a7d25a105c3c00d2f4fc2538f18\`.  
   Canonical scoring source:
   [\`src/whestbench/scoring.py\`](https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py),
   blob \`9cf7653a0267c4d048617c9045ac8be127f3c8bf\`.  
   Canonical budget/round source:
   [\`src/whestbench/budget.py\`](https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/budget.py),
   blob \`6586f12d178e0136420cb282535663f1faad5abc\`.  
   Phase-2 round documentation:
   [\`docs/reference/rounds.md\`](https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/docs/reference/rounds.md),
   blob \`c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890\`.

## 3. Setup

For one final output coordinate write \(f=f_j\). The audited Phase-2 network is bias-free and ends in ReLU, hence

\[
f(x)\ge0,\qquad f(0)=0,\qquad f(\alpha x)=\alpha f(x)\quad(\alpha\ge0).
\]

Let

\[
K_R=[-R,R]^n,\qquad n=1024,
\]

and suppose a sound affine upper relaxation on \(K_R\) is

\[
u_R(x)=c^\top x+\gamma_R,\qquad f(x)\le u_R(x)\quad(x\in K_R).
\]

Let

\[
p(R)=P(X\in K_R)
=\left(2\Phi(R)-1\right)^n
=\operatorname{erf}(R/\sqrt2)^n,
\qquad q(R)=1-p(R)
\]

for \(X\sim N(0,I_n)\).

Because \(K_R\) and the Gaussian law are centrally symmetric,

\[
E[X\,1_{K_R}]=0.
\]

For a certified Euclidean Lipschitz constant \(\Lambda\),

\[
f(x)\le \Lambda\|x\|_2,
\]

and therefore

\[
E[f(X)1_{K_R^c}]
\le
\Lambda E[\|X\|_2 1_{K_R^c}]
\le
\Lambda\sqrt{nq(R)}.
\]

Thus R376's upper certificate

\[
U(R)=p(R)\gamma_R+\Lambda\sqrt{nq(R)}
\]

is sound.

## 4. Check of \(h_j\ge c(R)\mu_j\)

Define

\[
M=\sup_{\|v\|_2=1} f(v).
\]

Choose a maximizing direction \(v\). Since both \(Rv\) and \(-Rv\) lie in \(K_R\),

\[
c^\top(Rv)+\gamma_R\ge f(Rv)=RM,
\]

\[
-c^\top(Rv)+\gamma_R\ge f(-Rv)\ge0.
\]

Adding gives

\[
2\gamma_R\ge RM,
\qquad
\boxed{\gamma_R\ge RM/2}.
\]

Also \(\Lambda\ge M\), because \(f(0)=0\) and \(f(v)\le\Lambda\|v\|_2\).

With the Gaussian polar decomposition \(X=\rho\Theta\),

\[
\mu:=E f(X)
=
E\rho\,E f(\Theta)
\le
\bar r\,M,
\]

where

\[
\bar r=E\|X\|_2
=
\sqrt2\frac{\Gamma((n+1)/2)}{\Gamma(n/2)}
=
\sqrt2\frac{\Gamma(512.5)}{\Gamma(512)}
\]

and numerically

\[
\boxed{\bar r=31.9921884548381698126330959207\ldots}.
\]

R376 reported \`31.992188454829048\`; that decimal is slightly inaccurate, although the discrepancy is immaterial to the scientific conclusion.

Combining the inequalities,

\[
U(R)
\ge
M\left(\frac{p(R)R}{2}+\sqrt{nq(R)}\right)
\ge
\frac{\mu}{\bar r}
\left(\frac{p(R)R}{2}+\sqrt{nq(R)}\right).
\]

**For the specific R376 interval construction \([0,U]\)**, its midpoint radius is

\[
h(R)=U(R)/2,
\]

so

\[
\boxed{
h(R)\ge c(R)\mu,
\qquad
c(R)=
\frac{p(R)R+2\sqrt{nq(R)}}{4\bar r}.
}
\]

**Finding:** the algebra of this lower bound is correct **conditional on using R376's one-sided interval \([0,U]\)**.

That qualifier becomes material in §8.

## 5. Independent optimization of \(c(R)\)

Since

\[
p(R)=\operatorname{erf}(R/\sqrt2)^n,
\]

\[
p'(R)
=
n\operatorname{erf}(R/\sqrt2)^{n-1}
\sqrt{\frac2\pi}e^{-R^2/2}.
\]

Writing the numerator of \(c(R)\) as

\[
N(R)=p(R)R+2\sqrt{n(1-p(R))},
\]

its derivative is

\[
\boxed{
N'(R)
=
p(R)
+
p'(R)
\left(
R-\frac{\sqrt n}{\sqrt{1-p(R)}}
\right).
}
\]

The positive stationary minimum is near

\[
\boxed{R_*\approx5.545908}.
\]

At \(R=5.5459\), \(c'(R)<0\); at \(R=5.54591\), \(c'(R)>0\), bracketing the stationary point.

Using the exact \(\bar r\) above gives approximately

\[
\boxed{c_{\min}\approx0.0460734409652}.
\]

At the rounded value \(R=5.546\),

\[
p(R)\approx0.9999700711,\qquad
q(R)\approx2.99289\times10^{-5},
\]

and

\[
c(5.546)\approx0.0460734410542.
\]

Therefore R376's statement “\(R\approx5.546\), \(c_*\approx0.046073441\)” is correct at the shown precision, but the stored longer decimal

\[
0.04607344105297431
\]

should **not** be treated as the exact numerical optimum. The true minimizing decimal is slightly smaller. This is a nonmaterial numerical correction.

## 6. Midpoint estimator: what is and is not proved

For an interval known only as

\[
0\le\mu\le U,
\]

the minimax constant estimate is indeed

\[
\boxed{\widehat\mu=U/2}
\]

with worst-case radius

\[
\boxed{h=U/2}.
\]

So R376's midpoint formula is correct for its chosen interval.

However, the premise that the **best usable lower expectation from the same affine-relaxation information is necessarily zero** is too strong.

At \(x=0\), an affine lower bound

\[
\ell_R(x)=a^\top x+\beta_R\le f(x)
\quad(x\in K_R)
\]

must satisfy \(\beta_R\le0\), and symmetry indeed gives

\[
E[\ell_R(X)1_{K_R}]=p(R)\beta_R\le0.
\]

That only shows that **integrating the raw affine lower function** gives no positive lower bound. It does not show that all sound transformations of that same affine lower relaxation have zero expectation.

Because \(f\ge0\),

\[
\boxed{
f(x)\ge \max(0,\ell_R(x))
\quad(x\in K_R).
}
\]

This is the concrete escape analyzed in §8.

## 7. Phase-2 score-floor arithmetic

The pinned WhestBench source defines, for a valid MLP,

\[
s_m
=
\operatorname{MSE}_{m,\mathrm{final}}
\max\left(0.1,\frac{C_m}{B_m}\right).
\]

For Phase 2 the pinned round configuration gives

\[
B_m=2^{41}=2,199,023,255,552,
\qquad
\lambda=0,
\]

so effective compute is FLOPs only, with residual wall time separately gated at \(0.4\) s.

If every candidate MLP stays at or below the score floor,

\[
C_m/B_m\le0.1,
\]

then the Mini-100 aggregate score is

\[
0.1\times
\frac1{100}\sum_m\operatorname{MSE}_{m,\mathrm{final}}.
\]

Against the stored same-panel R209 adjusted score

\[
S_{209}=8.170397440117225\times10^{-9},
\]

a **sufficient certified-error gate** based on radii \(H_m\) is

\[
\frac1{100}\sum_m H_m^2
<
8.170397440117225\times10^{-8}.
\]

This score-floor arithmetic is correct.

### The important logical correction

From the one-sided GELR radius theorem,

\[
H^2_{\mathrm{avg}}
\ge c_{\min}^2 T^2,
\]

where

\[
T^2=
\frac1{100\cdot1024}\sum_{m,j}\mu_{mj}^2.
\]

Therefore, in order for **that worst-case radius certificate itself** to satisfy the sufficient gate, it is necessary that

\[
T
<
\frac{\sqrt{8.170397440117225\times10^{-8}}}{c_{\min}}.
\]

Using the independently corrected \(c_{\min}\),

\[
\boxed{
T<0.00620398791194\ldots
}
\]

instead of R376's

\[
0.00620398790011652.
\]

The difference is negligible at the requested \`0.0062039879\` precision.

But this is **not a necessary condition for the actual midpoint estimator to beat R209**.

A lower bound on the certificate radius \(h\) is not a lower bound on the realized error

\[
|\widehat\mu-\mu|.
\]

For example, \(\mu\) may happen to lie close to the midpoint even when the certified interval is wide.

Hence the exact interpretation is:

> \(\boxed{T<0.0062039879\text{ is necessary only for R376's one-sided worst-case certificate to certify the score-floor GO inequality.}}\)

It is **not** a theorem that an estimator with \(T\ge0.0062039879\) cannot empirically or exactly beat R209.

The same semantic distinction applies to the stricter raw-parent number.

## 8. Concrete non-enumerative escape: clip the affine lower relaxation at zero

This escape uses the **same global affine lower relaxation** and the known nonnegativity of the final ReLU output. It does not enumerate activation regions, sample inputs, or invoke CV/Hermite/TT machinery.

Let

\[
\ell_R(x)=a^\top x+\beta
\]

be any sound lower affine output bound on \(K_R\), with \(\beta\le0\), and let

\[
\sigma=\|a\|_2.
\]

For the untruncated Gaussian,

\[
Z=a^\top X\sim N(0,\sigma^2).
\]

The positive part has the exact Gaussian expectation

\[
E[(Z+\beta)_+]
=
\sigma\phi(\beta/\sigma)
+
\beta\Phi(\beta/\sigma),
\]

with the \(\sigma=0\) case interpreted directly.

On \(K_R\),

\[
f(X)\ge(\ell_R(X))_+.
\]

Therefore

\[
E[f(X)1_{K_R}]
\ge
E[(Z+\beta)_+]
-
E[(Z+\beta)_+1_{K_R^c}].
\]

Since

\[
(Z+\beta)_+\le |Z|+|\beta|,
\]

Cauchy–Schwarz gives

\[
E[|Z|1_{K_R^c}]
\le
\sigma\sqrt{q(R)}.
\]

Thus the following **fully analytic, target-free lower certificate** is sound:

\[
\boxed{
L_{\mathrm{clip}}(R)
=
\left[
\sigma\phi(\beta/\sigma)
+\beta\Phi(\beta/\sigma)
-\sigma\sqrt{q(R)}
-|\beta|q(R)
\right]_+.
}
\]

Whenever \(L_{\mathrm{clip}}(R)>0\), combine it with the existing upper certificate \(U(R)\):

\[
L_{\mathrm{clip}}(R)\le\mu\le U(R).
\]

The minimax midpoint and radius become

\[
\boxed{
\widehat\mu_{\mathrm{clip}}
=
\frac{U+L_{\mathrm{clip}}}{2},
\qquad
h_{\mathrm{clip}}
=
\frac{U-L_{\mathrm{clip}}}{2}.
}
\]

Hence, whenever \(L_{\mathrm{clip}}>0\),

\[
\boxed{
h_{\mathrm{clip}}<U/2=h_{\mathrm{R376}}.
}
\]

This is a **strict certificate-radius reduction** using no activation-region enumeration and no sampling.

PROVEN independently establishes the key primary-source premise that affine bounds under multivariate Gaussian input admit analytic Gaussian probability calculations; the formula above is then direct one-dimensional Gaussian integration plus Cauchy–Schwarz.

### Cost status

The expensive affine bound propagation is unchanged. The added work per output is:

- one coefficient-vector norm;
- a small number of scalar arithmetic operations;
- scalar \(\phi,\Phi\) evaluations.

Across 1024 outputs this is \(O(1024^2)\) ordinary arithmetic plus \(O(1024)\) scalar special-function evaluations, versus R376's frozen matrix-propagation envelope of

\[
138,512,695,296\ \text{FLOPs}.
\]

The Phase-2 10% score-floor boundary is

\[
0.1\,2^{41}=219,902,325,555.2,
\]

leaving roughly \(8.139\times10^{10}\) FLOPs of static headroom relative to that frozen R376 envelope.

R383 does **not** promote this to an exact FlopScope production count: no implementation was created, and the exact permitted/billed realization of the scalar Gaussian CDF/PDF path was not executed. The cost blocker is therefore an exact billing/implementation fact, not a matrix-scale asymptotic obstacle.

### What this escape proves

It proves that R376's structural theorem is **not a no-go theorem for all methods using one global affine lower/upper relaxation**.

The theorem is valid for the narrower construction that discards the affine lower bound after observing its raw symmetric expectation is nonpositive.

Whether the actual R376/CROWN lower coefficients on the fixed Mini-100 networks make \(L_{\mathrm{clip}}>0\) often enough to clear the scorer gate is unknown without the forbidden/missing payload and an implementation measurement.

## 9. Second exact escape mechanism: nested symmetric truncation shells

There is also a purely upper-bound escape from the single-truncation structural floor.

Suppose

\[
u_1(x)=a^\top x+\gamma
\]

is valid on \(K_1\). Positive homogeneity gives, for every \(R>0\),

\[
\boxed{
u_R(x)=a^\top x+R\gamma
}
\]

as a valid upper bound on \(K_R\): write \(x=Ry\), \(y\in K_1\), and use \(f(Ry)=Rf(y)\).

Choose

\[
0=R_0<R_1<\cdots<R_K.
\]

The shells

\[
S_k=K_{R_k}\setminus K_{R_{k-1}}
\]

are centrally symmetric, so the linear term integrates to zero on every shell. Hence

\[
\boxed{
U_{\mathrm{shell}}
=
\gamma\sum_{k=1}^K
\left[p(R_k)-p(R_{k-1})\right]R_k
+
\Lambda\sqrt{nq(R_K)}.
}
\]

For the same outer radius \(R_K\), the original single-truncation upper certificate from the same scaled affine bound is

\[
U_{\mathrm{single}}
=
\gamma p(R_K)R_K
+
\Lambda\sqrt{nq(R_K)}.
\]

Their exact difference is

\[
\boxed{
U_{\mathrm{single}}-U_{\mathrm{shell}}
=
\gamma
\sum_{k=1}^{K-1}
p(R_k)(R_{k+1}-R_k)
>0
}
\]

for any nontrivial partition with \(\gamma>0\).

Thus nested symmetric truncations **strictly improve the upper certificate** without activation-pattern enumeration. Because all affine bounds are obtained by homogeneity scaling of one bound, this does not require \(K\) full CROWN passes; the extra work is scalar shell bookkeeping.

This independently demonstrates why the \(c_*\) floor cannot be generalized from “one truncation + one-sided midpoint” to all finite combinations of global affine relaxations/truncations.

Again, no claim is made that the shell construction clears R209 on the fixed panel: exact network-specific \(\gamma,\Lambda\), exact billing, and fixed target payload evidence are absent.

## 10. Scope of the valid no-go

The strongest statement supported after red-team is:

> **For R376's specific GELR construction consisting of one symmetric box truncation, one global affine upper bound, a Lipschitz tail, zero lower endpoint, and the midpoint \(U/2\), the certificate radius obeys \(h\ge c_{\min}\mu\) with \(c_{\min}\approx0.0460734409652\). Therefore that particular worst-case certificate cannot certify a score-floor win unless the fixed-panel target RMS is below approximately \(0.0062039879\).**

The following broader claims are **not proved**:

- no single global affine **pair** can yield a tighter Gaussian mean interval;
- no analytic transformation of affine lower/upper bounds can beat the \(c_*\) radius;
- no finite combination of global affine relaxations can beat the \(c_*\) radius;
- no finite nested truncation construction can beat it;
- no affine-relaxation estimator can actually beat R209 when target RMS exceeds \(0.0062039879\);
- no affine-relaxation method can fit Phase-2 compute.

The clipped-lower and shell constructions above are explicit counterexamples to extending the R376 structural floor to those broader families.

## 11. Exact blocker after the escape

Benchmark payload is absent and was not downloaded.

The remaining facts needed to decide whether either escape is a real Phase-2 improvement are:

1. the actual per-network affine lower coefficients \((a,\beta)\) and upper intercept/Lipschitz data produced by a frozen sound relaxation;
2. whether \(L_{\mathrm{clip}}>0\) and/or shell refinement reduces the 1024-output RMS certificate enough on the exact fixed Mini-100 panel;
3. exact FlopScope/allowed-code billing for the chosen Gaussian scalar-function realization and the complete implementation;
4. the fixed target arrays/RMS if the decision is to be tied to actual scorer performance rather than certificate-only admissibility.

None of those facts can be reconstructed from target hashes alone.

No population-over-random-weights statement can replace the fixed-panel scorer evidence.

## 12. Verdict

\[
\boxed{
\text{PASS\_ON\_R376\_ONE\_SIDED\_GELR\_ALGEBRA}
}
\]

with two material scope corrections:

1. the long decimal \`c*=0.04607344105297431\` is not the exact optimizer; the independently bracketed minimum is near \(R=5.545908\) with \(c_{\min}\approx0.0460734409652\);
2. \(T<0.0062039879\) is necessary for **that certificate to certify the score-floor gate**, not necessary for the actual estimator score to beat R209.

And there is a concrete escape:

\[
\boxed{
\text{R376 DOES NOT PROVE A BROADER AFFINE-RELAXATION NO-GO.}
}
\]

Clipping the affine lower relaxation at zero yields an analytic positive lower certificate whenever the displayed formula is positive, strictly reducing radius; nested symmetric truncation shells also strictly reduce the upper certificate while reusing one homogeneous affine relaxation.

Therefore the correct scientific boundary is a **narrow no-go for the exact one-sided single-truncation GELR certificate**, not a no-go for global affine relaxation methods as a class.

## 13. Execution accounting

- project/code execution: **0**
- estimator implementation: **NO**
- estimator runs: **0**
- synthetic runs: **0**
- benchmark/scorer runs: **0**
- Actions runs: **0**
- benchmark payload downloads: **0**
- dependency installs: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submissions: **0**
- browser/UI competition interaction: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
