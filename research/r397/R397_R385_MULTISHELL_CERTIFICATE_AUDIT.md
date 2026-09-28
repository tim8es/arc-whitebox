# R397 — adversarial audit of R385 multi-shell clipped GELR certificates

**Status:** COMPLETE  
**Verdict:** **PASS_REAL_ARITHMETIC_FORMULAS_WITH_NUMERICAL_CORRECTIONS__DETERMINISTIC_SOUND_J_LOWER_BOUND_SURVIVES__NO_GO_FOR_EXACT_J_OR_0.4S_RESIDUAL_CERTIFICATE_FROM_STATIC_EVIDENCE**  
**Mode:** research/source/algebra audit only; no estimator, synthetic, benchmark, scorer, dataset, Actions, or submission execution.  
**Branch:** \`research/r397-r385-multishell-certificate-audit-20260928\`  
**Exact base:** \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`

## 1. Scope and immutable inputs

R394 was superseded by R395 before any R394 branch/code/run was created in this session. R397 is independent and does not continue R394.

Audited internal artifacts:

- R385 exact commit: \`2ba08cb916cc504f1c38673971c2aa811b2da48c\`
  - report: \`research/r385/R385_MULTISHELL_CLIPPED_GELR.md\`
  - blob: \`08a04c634f9b489092d4f3636799908cdf51a1a6\`
- R383 head: \`31b79a0896de889b190b141a2f5c2a7da0967346\`
  - report: \`research/r383/R383_GELR_REDTEAM.md\`
  - blob: \`6e8216e136924553a24f81d165abdebaf0941ae8\`
- R376 head: \`3e61563bf46d09081dfae133407219763f27bf7f\`
  - report blob: \`999de9d6203ac263a5da1c9d1b1e20daba43488d\`
- R388 head: \`e00498ffbab0ef5e5e5c1a58d5874ec4af5627e6\`
  - report: \`research/r388/R388_NO_DATASET_SCREEN_PROTOCOL.md\`
  - blob: \`ec4a6126d29b2475c9459bb2bf435eecea8bb0b3\`

No benchmark/network/target tensors were accessed.

## 2. Primary sources

Affine-relaxation soundness:

1. Weng et al., “Towards Fast Computation of Certified Robustness for ReLU Networks,” ICML 2018, PMLR 80:5276–5285. Theorem 3.5 derives explicit affine output bounds from ReLU linear relaxations.  
   https://proceedings.mlr.press/v80/weng18a.html
2. Zhang et al., “Efficient Neural Network Robustness Certification with General Activation Functions,” NeurIPS 2018. Definition 3.1 / Theorem 3.2 propagate linear activation bounds into certified affine network-output bounds.  
   https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html
3. Weng et al., “PROVEN: Verifying Robustness of Neural Networks with a Probabilistic Approach,” ICML 2019, PMLR 97:6727–6736. The paper explicitly converts affine bounds under Gaussian perturbations into analytic univariate-Gaussian probability expressions.  
   https://proceedings.mlr.press/v97/weng19a.html

Normal-tail inequalities / stable deterministic bounding:

4. R. D. Gordon, “Values of Mills' Ratio of Area to Bounding Ordinate and of the Normal Probability Integral for Large Values of the Argument,” Annals of Mathematical Statistics 12(3), 1941, 364–366, DOI 10.1214/aoms/1177731721. In particular the classical Mills-ratio bounds include
   \[
   \frac{t}{t^2+1}<\frac{Q(t)}{\phi(t)}<\frac1t,\qquad t>0.
   \]
5. A. J. Gross and D. W. Hosmer, “Approximating Tail Areas of Probability Distributions,” Annals of Statistics 6(6), 1978, 1352–1359, DOI 10.1214/aos/1176344380.
6. Chu-In Charles Lee, “On Laplace continued fraction for the normal integral,” Annals of the Institute of Statistical Mathematics 44, 1992, 107–120, DOI 10.1007/BF00048673. It records the alternating continued-fraction bounds; the second upper convergent is
   \[
   \frac{Q(t)}{\phi(t)}
   <
   \frac{t^2+2}{t^3+3t},
   \qquad t>0.
   \]

Execution/numerics:

7. IEEE 754-2019, “IEEE Standard for Floating-Point Arithmetic,” DOI 10.1109/IEEESTD.2019.8766229.
8. AIcrowd FlopScope 0.12.1 pinned source \`b599f015b0bc005b1edb6d7a1b10e0814675e693\`:
   - \`src/flopscope/stats/_norm.py\`, blob \`fd60a11537a1b8a3beb73a14816c05482c0b348a\`
   - \`src/flopscope/numpy/__init__.py\`, blob \`d9e12cb1b66875d936f4b73cb7e092596912b7c1\`
   - \`src/flopscope/_registry.py\`, blob \`de7388e5649224360ca3fa8e5f62b4ad5ebcc596\`
9. Official Phase-2 starter-kit rules: \(B=2^{41}\), per-\`predict()\` wall 120 s, residual wall 0.4 s; meaningful numerical work belongs in FlopScope rather than the residual bucket.

## 3. Shell geometry and probability audit

Let

\[
K_R=[-R,R]^n,\qquad
0=R_0<R_1<\cdots<R_K,
\]

and

\[
S_k=K_{R_k}\setminus K_{R_{k-1}}.
\]

For \(X\sim N(0,I_n)\), coordinate independence gives exactly

\[
p_k=P(K_{R_k})
=
\left(2\Phi(R_k)-1\right)^n,
\]

\[
\Delta p_k=P(S_k)=p_k-p_{k-1}.
\]

The sets \(S_1,\ldots,S_K,K_{R_K}^c\) are disjoint and partition \(\mathbb R^n\). Each \(S_k\) is centrally symmetric, hence

\[
E[X\,1_{S_k}]=0.
\]

**Finding: PASS.** R385's shell probabilities, nesting, and symmetry argument are correct in exact real arithmetic.

## 4. Positive-homogeneity scaling audit

Assume the fixed bias-free ReLU network is positively homogeneous,

\[
f(\alpha x)=\alpha f(x),\qquad \alpha\ge0,
\]

and a sound affine pair on \(K_1\) is

\[
a^\top x+\beta
\le f(x)\le
c^\top x+\gamma.
\]

For \(x\in K_R\), write \(x=Ry\), \(y\in K_1\). Then

\[
f(x)=R f(y),
\]

so multiplying the unit-box inequalities by \(R\) yields

\[
\boxed{
a^\top x+R\beta
\le f(x)\le
c^\top x+R\gamma.
}
\]

No coefficient-vector rescaling is missing: \(R a^\top y=a^\top x\).

**Finding: PASS.** One sound unit-box affine pair can be reused for every shell. Recomputing CROWN/Fast-Lin at every radius could tighten the bound, but is not required for soundness.

## 5. Upper shell aggregation audit

On \(S_k\subseteq K_{R_k}\),

\[
f(X)\le c^\top X+R_k\gamma.
\]

By central symmetry,

\[
E[c^\top X\,1_{S_k}]=0,
\]

hence

\[
\boxed{
U_k^{\rm shell}
=
R_k\gamma\,\Delta p_k.
}
\]

Therefore

\[
\boxed{
U_{\rm in}
=
\gamma\sum_{k=1}^K R_k\Delta p_k.
}
\]

With any certified coordinate Lipschitz constant \(\Lambda\),

\[
f(x)\le\Lambda\|x\|_2,
\]

Cauchy–Schwarz gives

\[
E[f(X)1_{K_{R_K}^c}]
\le
\Lambda\sqrt{nq_K},
\qquad q_K=1-p_K.
\]

Thus

\[
\boxed{
U_{\rm MS}
=
\gamma\sum_{k=1}^K R_k\Delta p_k
+
\Lambda\sqrt{nq_K}
}
\]

is sound.

**Finding: PASS in real arithmetic.**

## 6. Exact clipped shell integral \(J_k\)

Because the final output is nonnegative and the affine lower bound is valid on \(K_{R_k}\),

\[
f(x)\ge[a^\top x+R_k\beta]_+.
\]

Set

\[
d_k=-R_k\beta\ge0,\qquad
Z=a^\top X,\qquad
\sigma=\|a\|_2.
\]

Then

\[
Z\sim N(0,\sigma^2)
\]

and the exact shell contribution is

\[
\boxed{
J_k
=
E[(Z-d_k)_+1_{S_k}].
}
\]

The symmetry identity is also correct:

\[
\boxed{
J_k
=
\frac12
E[(|Z|-d_k)_+1_{S_k}].
}
\]

The event \(S_k\) depends on all coordinates of \(X\), while \(Z=a^\top X\) is an oblique projection. Except in special coefficient patterns, the indicator and \(Z\) do not reduce to a one-dimensional Gaussian event.

**Exact-evaluation verdict:** **NO-GO FOR A CLAIM OF CHEAP EXACT \(J_k\).** The audited primary sources provide affine Gaussian projections, not a closed form for an oblique projection jointly truncated by a 1024-dimensional cube shell. Deterministic convolution/Fourier/truncated-Gaussian integration could be constructed in principle, but R397 found no source-backed algorithm with a rigorous truncation/error certificate and a worst-case Phase-2 operation/residual bound. This is a narrow no-go, not a universal impossibility theorem.

## 7. R385's analytic lower certificate is mathematically sound

Define the unconditional stop-loss expectation

\[
G_k=E[(Z-d_k)_+].
\]

For \(\sigma>0\), \(t_k=d_k/\sigma\), and

\[
\boxed{
G_k
=
\sigma\phi(t_k)-d_kQ(t_k),
\qquad
Q(t)=1-\Phi(t)=\Phi(-t).
}
\]

For \(\sigma=0\), \(G_k=0\).

The three disjoint sets

\[
K_{R_{k-1}},\qquad
S_k,\qquad
K_{R_k}^c
\]

partition \(\mathbb R^n\), so

\[
G_k
=
J_k
+
E[(Z-d_k)_+1_{K_{R_{k-1}}}]
+
E[(Z-d_k)_+1_{K_{R_k}^c}].
\]

Outer loss:

\[
(Z-d_k)_+\le Z_+\le|Z|
\]

and Cauchy–Schwarz give

\[
E[(Z-d_k)_+1_{K_{R_k}^c}]
\le
\sigma\sqrt{q_k}.
\]

Inner loss: with

\[
\tau=\|a\|_1,
\]

on \(K_{R_{k-1}}\),

\[
Z\le R_{k-1}\tau,
\]

so

\[
E[(Z-d_k)_+1_{K_{R_{k-1}}}]
\le
p_{k-1}(R_{k-1}\tau-d_k)_+.
\]

Therefore R385's bound

\[
\boxed{
\underline J_k
=
\left[
G_k
-\sigma\sqrt{q_k}
-p_{k-1}(R_{k-1}\tau-d_k)_+
\right]_+
}
\]

satisfies

\[
0\le\underline J_k\le J_k.
\]

The zero-inner-loss condition

\[
d_k\ge R_{k-1}\tau
\]

is also correct.

**Finding: PASS in exact arithmetic.** The main correction is numerical, not algebraic.

## 8. Material numerical defect in the displayed \(G_k\) evaluation

R385 writes

\[
G_k
=
\sigma\phi(t_k)
-d_k(1-\Phi(t_k)).
\]

Two implementation hazards follow.

### 8.1 Never form \(1-\Phi(t)\) for positive large \(t\)

The stable equivalent is

\[
Q(t)=\Phi(-t).
\]

FlopScope already provides \`stats.norm.cdf\`; evaluating it at \(-t\) has the same documented cost as evaluating it at \(t\). Therefore replacing

\[
1-\Phi(t)
\]

by

\[
\Phi(-t)
\]

costs no extra Gaussian kernel.

### 8.2 Even \(\phi(t)-tQ(t)\) suffers cancellation

Write

\[
G_k
=
\sigma\phi(t_k)
\left[
1-t_k\frac{Q(t_k)}{\phi(t_k)}
\right].
\]

For large \(t\), the Mills ratio is asymptotic to \(1/t\), so the bracket is small: the two terms in the original formula are nearly equal.

A deterministic lower bound avoids this subtraction entirely.

The Gross–Hosmer / Laplace-continued-fraction upper bound recorded by Lee is

\[
\frac{Q(t)}{\phi(t)}
<
\frac{t^2+2}{t^3+3t},
\qquad t>0.
\]

Therefore

\[
1-t\frac{Q(t)}{\phi(t)}
>
1-\frac{t^2+2}{t^2+3}
=
\frac1{t^2+3},
\]

and hence

\[
\boxed{
G_k
>
G_k^-:=
\frac{\sigma\phi(t_k)}{t_k^2+3},
\qquad t_k>0.
}
\]

At \(t_k=0\),

\[
G_k=\sigma\phi(0),
\]

so use the exact \(t=0\) branch.

This yields a simpler cancellation-free shell certificate

\[
\boxed{
\underline J_k^{\rm Mills}
=
\left[
G_k^-
-\sigma\sqrt{q_k}
-p_{k-1}(R_{k-1}\tau-d_k)_+
\right]_+
\le J_k.
}
\]

It is generally looser than exact \(G_k\), but is **sound in real arithmetic**, deterministic, sample-free, and asymptotically sharp enough to avoid the catastrophic subtraction.

This is the preferred adversarial-safe mathematical form when certificate soundness matters more than squeezing every bit from \(G_k\).

## 9. Stable shell probabilities

The raw formulas

\[
q_k=1-p_k,
\qquad
\Delta p_k=p_k-p_{k-1}
\]

lose relative precision when \(p_k\) is close to one.

Use

\[
Q_R=\Phi(-R),
\qquad
r_R=2Q_R,
\]

and

\[
\lambda_R
=
n\log1p(-r_R)
=
\log p_R.
\]

Then

\[
\boxed{
p_R=e^{\lambda_R},
\qquad
q_R=-\operatorname{expm1}(\lambda_R).
}
\]

For \(k\ge2\),

\[
\boxed{
\Delta p_k
=
p_k
\left[
-\operatorname{expm1}(\lambda_{k-1}-\lambda_k)
\right].
}
\]

For \(k=1\), \(\Delta p_1=p_1\).

This avoids both \(1-p\) and subtraction of two nearly equal \(p\)'s.

The pinned FlopScope 0.12.1 surface explicitly exposes \`fnp.log1p\` and \`fnp.expm1\`; both are metered transcendental operations. Thus the stable formulation does not require unmetered Python math.

### Underflow guard

If \(p_1\) itself underflows to zero, the upper shell sum would silently omit positive probability mass and cease to be a formal upper certificate.

Therefore a production certificate must either:

1. choose the first positive radius so \(p_1\) is representable in the chosen arithmetic; or
2. absorb any underflow-prone inner mass into a separately conservative upper term.

Similarly, for the outer tail, silently rounding a positive \(q_K\) to zero is unsafe for an upper certificate.

For the intended radii around the R376 optimum (~5.5), these probabilities are nowhere near binary64 underflow; the issue is still part of the required edge-case contract because R385 did not constrain radii numerically.

## 10. Machine-level soundness caveat

The proofs above are real-arithmetic proofs.

The official FlopScope normal CDF/PDF kernels have documented analytical FLOP costs and are the permitted path, but the audited documentation/source does **not** expose an outward-rounded interval guarantee for every returned CDF/PDF value. IEEE 754 default arithmetic is round-to-nearest unless another rounding direction is selected.

Therefore:

- R385's **mathematical** interval is sound;
- a float64 implementation using ordinary approximate CDF/PDF values is not automatically a formally outward-rounded interval-arithmetic certificate;
- this issue already applies to the affine-bound construction if its floating implementation does not account for roundoff.

For the ARC engineering screen this may be an accepted numerical convention, but R397 does not upgrade it into a theorem of machine-level enclosure.

A strict implementation claiming formal certificate soundness must add explicit conservative error margins or a documented directed/outward rounding construction.

## 11. Interval aggregation audit

Define

\[
L_{\rm MS}
=
\sum_{k=1}^K\underline J_k
\]

(or the more conservative Mills version).

Because shells are disjoint and the omitted outside-tail contribution is nonnegative,

\[
L_{\rm MS}\le E f(X).
\]

Together with the upper endpoint,

\[
\boxed{
L_{\rm MS}\le\mu\le U_{\rm MS}.
}
\]

The midpoint

\[
\widehat\mu_{\rm MS}
=
\frac{L_{\rm MS}+U_{\rm MS}}2
\]

therefore has radius

\[
h_{\rm MS}
=
\frac{U_{\rm MS}-L_{\rm MS}}2.
\]

**Finding: PASS in real arithmetic.**

A defensive implementation must explicitly fail closed if numerical evaluation produces non-finite values or \(L_{\rm MS}>U_{\rm MS}\).

## 12. Strict-improvement condition audit

For the same outer radius \(R_K\), same scaled affine upper bound, and same tail,

\[
U_{\rm single}
=
\gamma R_Kp_K+\Lambda\sqrt{nq_K}.
\]

R385's summation-by-parts identity is correct:

\[
\boxed{
U_{\rm single}-U_{\rm MS}
=
\gamma
\sum_{k=1}^{K-1}
p_k(R_{k+1}-R_k)
=:\Delta U_{\rm shell}.
}
\]

Hence

\[
\boxed{
h_{\rm single}-h_{\rm MS}
=
\frac{\Delta U_{\rm shell}+L_{\rm MS}}2.
}
\]

Thus, in exact arithmetic,

\[
\boxed{
h_{\rm MS}<h_{\rm single}
\iff
\Delta U_{\rm shell}+L_{\rm MS}>0.
}
\]

Sufficient conditions are exactly as R385 states:

- \(\gamma>0\) and at least one interior shell has positive probability and positive radius gap; or
- \(L_{\rm MS}>0\).

Two scope corrections:

1. This is strict improvement over **R376's specific single-shell certificate radius**, not proof of lower fixed-target MSE.
2. A floating implementation should not infer strictness from a tiny positive computed difference unless its probability/error evaluation has a margin exceeding numerical uncertainty.

## 13. Deterministic cost of a numerically safer \(J_k\) bound

R385's expensive part remains affine-bound acquisition. Its frozen, unmeasured implementation envelope is

\[
C_{\rm affine}
\le
8Ln^3+64Ln^2
=
138,512,695,296
\]

for \(L=16,n=1024\).

R397 does not validate that affine implementation here; it audits only the shell mathematics/readout.

### 13.1 Existing R385 readout envelope

R385 states

\[
C_{\rm read}(K)
\le
(4mn-m)+K(180m+142)+16m.
\]

For \(n=m=1024\),

\[
C_{\rm read}(K)
\le
4,209,664+184,462K.
\]

This is already negligible relative to \(2^{41}\).

### 13.2 Stable shell-probability overhead

The stable \(\log1p/\expm1\) formulation adds only \(O(K)\) scalar operations. At the pinned FlopScope cost model:

- \`stats.norm.cdf\`: 96 billed FLOPs/float64 element;
- \`stats.norm.pdf\`: 54 billed FLOPs/float64 element;
- float64 \`exp\`, \`expm1\`, \`log1p\`: 32 billed FLOPs/element;
- ordinary float64 arithmetic/reduction is width-rated at 2× the scalar count.

A conservative scalar shell-probability schedule is below 220 billed FLOPs per shell.

### 13.3 Mills lower path is cheaper per output

The cancellation-free \(G_k^-\) path needs one normal PDF per shell/output and no normal CDF per shell/output. Allowing a deliberately conservative 96 billed FLOPs per shell/output for PDF plus all arithmetic, selects, clipping, and the inner/outer deductions gives

\[
\boxed{
C_{\rm read}^{\rm stable}(K)
\le
(4mn-m)
+
K(96m+220)
+
20m.
}
\]

For \(n=m=1024\),

\[
\boxed{
C_{\rm read}^{\rm stable}(K)
\le
4,213,760
+
98,524K.
}
\]

At \(K=64\),

\[
\boxed{
C_{\rm read}^{\rm stable}(64)
\le
10,519,296.
}
\]

Combining with the frozen R376/R385 affine envelope gives

\[
\boxed{
C_{\rm total}^{\rm stable}(64)
\le
138,523,214,592
<
0.1\cdot2^{41}
=
219,902,325,555.2.
}
\]

So the deterministic **sound lower-bound readout** is not the FLOP blocker. It fits even the 10%-of-budget scorer floor by a wide static margin, conditional on the affine pass actually satisfying its frozen envelope.

This is a source-derived static bill, not a measured FlopScope trace.

## 14. Residual-time verdict

The 0.4-s residual gate is a hard execution gate, not a FLOP formula.

The stable schedule can be expressed as whole-array FlopScope operations over \(K\times m\) arrays, leaving Python only fixed-size orchestration. That is the correct design for keeping meaningful arithmetic out of residual time.

However, **no static source/algebra proof can establish a hardware-measured 0.4-s residual wall time for a not-yet-executed implementation.**

Therefore:

\[
\boxed{
\text{0.4-s residual compliance = UNKNOWN without an authorized run.}
}
\]

R397 is forbidden to run one, so it stops there. It does not convert FLOP feasibility into a timing claim.

## 15. Final verdict by question

| Question | R397 verdict |
|---|---|
| shell probabilities/nesting | **PASS** mathematically; raw subtraction forms need stable evaluation |
| positive-homogeneity affine scaling | **PASS** |
| upper shell aggregation | **PASS** |
| exact \(J_k\) closed form / cheap exact evaluation | **NO-GO / not established** |
| R385 analytic lower bound on \(J_k\) | **PASS** in real arithmetic |
| numerically safer deterministic \(J_k\) lower bound | **YES:** Mills-ratio \(G_k^-\) construction |
| \(2^{41}\) FLOP feasibility of readout | **PASS statically**; \(K=64\) stable readout <= 10,519,296 FLOPs |
| all-in FLOP feasibility including frozen affine envelope | **CONDITIONAL PASS**; <= 138,523,214,592 under the unmeasured R376 affine envelope |
| 0.4-s residual compliance | **UNKNOWN / cannot be certified statically** |
| strict certificate-radius improvement over R376 | **PASS** under \(\Delta U_{\rm shell}+L_{\rm MS}>0\) |
| measured score improvement | **NOT CLAIMED / no data or run** |

The narrow overall result is:

\[
\boxed{
\text{R385's multi-shell certificate is algebraically sound,}
}
\]

but its displayed numerical implementation recipe needs two corrections:

1. evaluate shell probabilities with \(\Phi(-R)\), \(\log1p\), and \(\expm1\), not \(1-p\) / close-\(p\) subtraction;
2. do not rely on the cancellation-prone \(G=\sigma[\phi(t)-tQ(t)]\) when a certificate is required; the Mills-ratio lower surrogate
   \[
   G^-=\sigma\phi(t)/(t^2+3)
   \]
   gives a deterministic, cheaper, cancellation-free lower certificate.

The remaining blockers are **not** the \(J_k\) readout FLOPs. They are:

- availability/cost/soundness of the affine-bound builder (outside R397's scope);
- machine-level outward-rounding/error margins if “certificate” is meant literally at floating precision;
- measured 0.4-s residual / 120-s wall compliance;
- fixed-panel accuracy, which R397 does not and may not measure.

## 16. No-action accounting

Performed:

- repository/source reads;
- primary-source web research;
- symbolic algebra and static cost audit;
- one research-only Markdown report write.

Not performed:

- estimator runs: 0;
- synthetic runs: 0;
- benchmark/scorer runs: 0;
- contest dataset access: none;
- Mini/public/private/holdout/full tensors: none;
- downloads/clones: 0;
- dependency installs: 0;
- Actions: 0;
- submissions: 0;
- AIcrowd action: 0;
- R320 edits: 0;
- main edits: 0;
- PR edits: 0;
- control edits: 0;
- queue edits: 0.

No measured score or leaderboard claim is made.
