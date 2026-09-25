# R385 — explicit multi-shell clipped GELR estimator/certificate

**Status:** COMPLETE  
**Verdict:** **CONDITIONAL_GO_FOR_EXPLICIT_CERTIFICATE_AND_STATIC_COMPUTE_ENVELOPE__NO_GO_FOR_SCORE_IMPROVEMENT_CLAIM_WITHOUT_FIXED_NETWORK_AND_TARGET_TENSORS**  
**Mode:** primary-source desk derivation only; no estimator, benchmark, scorer, Mini, Actions, or submission execution  
**Branch:** \`research/r385-multishell-clipped-gelr-20260925\`  
**Parent:** R383 head \`31b79a0896de889b190b141a2f5c2a7da0967346\`  
**R383 report blob:** \`6e8216e136924553a24f81d165abdebaf0941ae8\`

## 1. Scope

R385 turns the two R383 escapes into one explicit deterministic estimator/certificate:

1. reuse one sound global affine lower/upper relaxation of a bias-free positively homogeneous ReLU network;
2. scale that affine pair to a nested sequence of symmetric Gaussian truncation boxes;
3. integrate the affine upper bound exactly shell by shell;
4. use the known final-ReLU nonnegativity to clip each affine lower bound at zero;
5. give the exact clipped shell expectation as a Gaussian integral, and a cheaper closed-form **certified lower bound** that uses only normal PDF/CDF, vector norms, and shell probabilities;
6. combine lower and upper endpoints into a midpoint estimator with a deterministic fixed-network mean-error radius;
7. separate affine-bound acquisition cost from Gaussian readout cost;
8. state the exact WhestBench scorer-level certificate gate against R209.

No claim below treats “certificate GO” as observed score improvement.

## 2. Primary sources

### Affine verification bounds

- Weng et al., **Fast-Lin**, ICML 2018, PMLR 80:5276–5285. The paper derives explicit certified output bounds for ReLU networks from linear activation relaxations; Theorem 3.5 is the relevant construction.  
  Primary source: https://proceedings.mlr.press/v80/weng18a.html  
  PDF: https://proceedings.mlr.press/v80/weng18a/weng18a.pdf

- Zhang et al., **CROWN**, NeurIPS 2018. Definition 3.1 gives linear upper/lower activation bounds; Theorem 3.2 gives explicit affine network-output bounds on an \(\ell_p\) input ball and permits adaptive upper/lower choices.  
  Primary source: https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html  
  PDF: https://proceedings.neurips.cc/paper/2018/file/d04863f100d59b3eb688a11f95b0ae60-Paper.pdf

### Gaussian processing of affine bounds

- Weng et al., **PROVEN**, ICML 2019, PMLR 97:6727–6736. The paper converts deterministic affine network bounds into probabilistic certificates; for multivariate Gaussian perturbations its corollary uses that an affine Gaussian projection is univariate Gaussian with analytic CDF.  
  Primary source: https://proceedings.mlr.press/v97/weng19a.html  
  PDF: https://proceedings.mlr.press/v97/weng19a/weng19a.pdf

### Phase-2 scoring and execution rules

Pinned official WhestBench 0.16.1 source at commit
\`4d08668b485c8a7d25a105c3c00d2f4fc2538f18\`:

- scoring:
  https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py  
  blob \`9cf7653a0267c4d048617c9045ac8be127f3c8bf\`
- budget/round configuration:
  https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/budget.py  
  blob \`6586f12d178e0136420cb282535663f1faad5abc\`

Pinned official FlopScope 0.12.1 source at commit
\`b599f015b0bc005b1edb6d7a1b10e0814675e693\`:

- normal PDF/CDF implementation and declared costs:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/stats/_norm.py  
  blob \`fd60a11537a1b8a3beb73a14816c05482c0b348a\`
- stats billing/promotion:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/stats/_base.py  
  blob \`aefba7faef4424876170629fe9a89767c6a11619\`

Current official starter-kit rules pinned for this audit at commit
\`5eb9aa1455fcb3216af55994bdf25dc242b95797\`:

- allowed code:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md  
  blob \`525276e8e5bc7f6a7dd54e876140ab0df514be32\`
- estimator contract:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/estimator-contract.md  
  blob \`43c1494420b46aad4bc1dbbab83528eca6b89668\`
- code patterns / normal PDF-CDF path:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/code-patterns.md  
  blob \`2d1aa532af6f160fd0942da34f78595216a596de\`

The official Phase-2 rules are important for cost interpretation: meaningful numerical work must go through FlopScope; residual wall time is plumbing, hard-capped at \(0.4\) s, not a second unmetered compute budget.

## 3. Fixed-network setup

Consider one final output coordinate \(f=f_j\) of the supplied network.

For the ARC Phase-2 architecture used by R376/R383,

\[
f(x)\ge0,\qquad f(0)=0,\qquad f(\alpha x)=\alpha f(x)\quad(\alpha\ge0).
\]

Let

\[
K_R=[-R,R]^n,\qquad n=1024,
\]

and obtain **once**, on the unit box \(K_1\), a sound affine pair

\[
\ell_1(x)=a^\top x+\beta
\le f(x)\le
u_1(x)=c^\top x+\gamma
\qquad (x\in K_1).
\]

Because \(f(0)=0\), validity at zero implies

\[
\beta\le0,\qquad \gamma\ge0.
\]

Positive homogeneity gives a key reuse identity. For every \(R>0\), write
\(x=Ry\) with \(y\in K_1\). Then

\[
f(x)=R f(y)
\]

and therefore

\[
\boxed{
\ell_R(x)=a^\top x+R\beta
\le f(x)\le
u_R(x)=c^\top x+R\gamma
\quad(x\in K_R).
}
\]

Thus a \(K\)-shell readout does **not** require \(K\) CROWN/Fast-Lin propagations if the same unit-box affine relaxation is reused by homogeneity.

Let a certified coordinate Lipschitz envelope satisfy

\[
f(x)\le\Lambda\|x\|_2.
\]

## 4. Nested Gaussian boxes and shell probabilities

Choose fixed radii

\[
0=R_0<R_1<\cdots<R_K.
\]

Define

\[
S_k=K_{R_k}\setminus K_{R_{k-1}}.
\]

For \(X\sim N(0,I_n)\),

\[
p_k:=P(X\in K_{R_k})
=
\left(2\Phi(R_k)-1\right)^n,
\]

\[
q_k:=1-p_k,
\qquad
\Delta p_k:=p_k-p_{k-1}.
\]

Every \(S_k\) is centrally symmetric, hence

\[
E[X\,1_{S_k}]=0.
\]

## 5. Exact upper Gaussian expectation for every shell

On \(S_k\subset K_{R_k}\),

\[
f(X)\le u_{R_k}(X)=c^\top X+R_k\gamma.
\]

Therefore

\[
E[u_{R_k}(X)1_{S_k}]
=
c^\top E[X1_{S_k}]
+
R_k\gamma P(S_k),
\]

so the shell expectation is exactly

\[
\boxed{
U_k^{\rm shell}
=
R_k\gamma\,\Delta p_k.
}
\]

Summing the shells gives the exact affine-bound contribution inside the outer box:

\[
\boxed{
U_{\rm in}
=
\gamma\sum_{k=1}^{K}R_k\Delta p_k.
}
\]

For the outside tail,

\[
E[f(X)1_{K_{R_K}^c}]
\le
\Lambda E[\|X\|_2 1_{K_{R_K}^c}]
\le
\Lambda\sqrt{nq_K}.
\]

Hence

\[
\boxed{
U_{\rm MS}
=
\gamma\sum_{k=1}^{K}R_k\Delta p_k
+
\Lambda\sqrt{nq_K}.
}
\]

This is a sound deterministic upper endpoint for \(\mu=Ef(X)\).

## 6. Exact clipped lower expectation for every shell

On \(K_{R_k}\),

\[
f(x)\ge0
\quad\text{and}\quad
f(x)\ge\ell_{R_k}(x).
\]

Therefore

\[
f(x)\ge[\ell_{R_k}(x)]_+
=
[a^\top x+R_k\beta]_+.
\]

Define

\[
d_k:=-R_k\beta\ge0,
\qquad
Z:=a^\top X,
\qquad
\sigma:=\|a\|_2.
\]

Then \(Z\sim N(0,\sigma^2)\) and the **exact clipped shell contribution** is

\[
\boxed{
J_k
=
E[(Z-d_k)_+\,1_{S_k}].
}
\]

Equivalently, as an exact \(n\)-dimensional Gaussian integral,

\[
\boxed{
J_k
=
\int_{S_k}
(a^\top x-d_k)_+
(2\pi)^{-n/2}e^{-\|x\|_2^2/2}\,dx.
}
\]

Central symmetry gives another exact form:

\[
\boxed{
J_k
=
\frac12
E\!\left[
(|a^\top X|-d_k)_+\,1_{S_k}
\right].
}
\]

This exact shell expectation is generally **not** a function only of
\((\sigma,d_k,p_k,p_{k-1})\): the cube event and the oblique projection
\(a^\top X\) are jointly involved. Evaluating \(J_k\) exactly would therefore
require a truncated multivariate Gaussian calculation (or an equivalent
high-dimensional integration), which is not the bounded readout claimed here.

The bounded-compute construction below uses an analytic **lower certificate**
for \(J_k\), not a false claim that the exact cube-shell integral reduces to a
one-dimensional normal CDF.

## 7. Closed-form lower certificate for every shell

The unconditional positive-part expectation is exactly univariate Gaussian:

\[
G_k
:=
E[(Z-d_k)_+].
\]

For \(\sigma>0\), let

\[
t_k=d_k/\sigma.
\]

Then

\[
\boxed{
G_k
=
\sigma\phi(t_k)
-
d_k\left(1-\Phi(t_k)\right).
}
\]

Equivalently, with \(m_k=R_k\beta=-d_k\),

\[
G_k
=
m_k\Phi(m_k/\sigma)
+
\sigma\phi(m_k/\sigma).
\]

For \(\sigma=0\), \(Z=0\) and \(G_k=0\) because \(d_k\ge0\).

Now decompose

\[
G_k
=
E[(Z-d_k)_+1_{S_k}]
+
E[(Z-d_k)_+1_{K_{R_{k-1}}}]
+
E[(Z-d_k)_+1_{K_{R_k}^c}].
\]

### Outer loss

Since \(d_k\ge0\),

\[
(Z-d_k)_+\le Z_+\le|Z|.
\]

Therefore

\[
E[(Z-d_k)_+1_{K_{R_k}^c}]
\le
E[|Z|1_{K_{R_k}^c}]
\le
\sigma\sqrt{q_k}.
\]

This is slightly tighter than the R383 generic
\(|Z|+|\beta|\) tail inequality because here the scaled intercept is known
nonpositive.

### Inner loss

Let

\[
\tau:=\|a\|_1.
\]

On \(K_{R_{k-1}}\),

\[
Z=a^\top x
\le
R_{k-1}\|a\|_1
=
R_{k-1}\tau.
\]

Hence

\[
(Z-d_k)_+
\le
(R_{k-1}\tau-d_k)_+,
\]

and therefore

\[
E[(Z-d_k)_+1_{K_{R_{k-1}}}]
\le
p_{k-1}(R_{k-1}\tau-d_k)_+.
\]

Combining both losses gives the explicit per-shell lower certificate

\[
\boxed{
\underline J_k
=
\left[
G_k
-\sigma\sqrt{q_k}
-p_{k-1}(R_{k-1}\tau-d_k)_+
\right]_+.
}
\]

By construction,

\[
0\le\underline J_k\le J_k.
\]

A useful sufficient condition that kills the inner-loss term exactly is

\[
\boxed{
d_k\ge R_{k-1}\tau.
}
\]

Under that condition,

\[
\underline J_k
=
[G_k-\sigma\sqrt{q_k}]_+.
\]

## 8. Explicit multi-shell clipped estimator/certificate

Because the shells are disjoint and the outside-tail contribution is nonnegative,

\[
\mu
=
E f(X)
\ge
\sum_{k=1}^{K}J_k
\ge
\sum_{k=1}^{K}\underline J_k.
\]

Define

\[
\boxed{
L_{\rm MS}
=
\sum_{k=1}^{K}\underline J_k.
}
\]

Together with §5,

\[
\boxed{
L_{\rm MS}\le\mu\le U_{\rm MS}.
}
\]

The explicit deterministic estimator is the interval midpoint

\[
\boxed{
\widehat\mu_{\rm MS}
=
\frac{L_{\rm MS}+U_{\rm MS}}2
}
\]

with fixed-network certified mean error

\[
\boxed{
|\widehat\mu_{\rm MS}-\mu|
\le
h_{\rm MS}
=
\frac{U_{\rm MS}-L_{\rm MS}}2.
}
\]

This is target-free and uses no input sampling.

For all final outputs \(j=1,\ldots,m\), apply the same formulas rowwise to
\((a_j,\beta_j,\gamma_j,\Lambda_j)\).

## 9. Exact strict-improvement condition over R376 single-shell \(U/2\)

Use the same outer radius \(R_K\), the same unit-box affine upper bound, and
the same Lipschitz tail.

The single-shell R376 upper endpoint is

\[
U_{\rm single}
=
\gamma R_Kp_K
+
\Lambda\sqrt{nq_K},
\]

and its radius is

\[
h_{\rm single}=U_{\rm single}/2.
\]

The multi-shell upper endpoint differs only in the in-box affine term:

\[
U_{\rm single}-U_{\rm MS}
=
\gamma
\left[
R_Kp_K-\sum_{k=1}^{K}R_k(p_k-p_{k-1})
\right].
\]

Discrete summation by parts gives

\[
\boxed{
U_{\rm single}-U_{\rm MS}
=
\gamma
\sum_{k=1}^{K-1}
p_k(R_{k+1}-R_k)
=: \Delta U_{\rm shell}.
}
\]

Since \(\gamma\ge0\), \(\Delta U_{\rm shell}\ge0\).

The exact radius improvement is

\[
\boxed{
h_{\rm single}-h_{\rm MS}
=
\frac{
\Delta U_{\rm shell}+L_{\rm MS}
}{2}.
}
\]

Therefore

\[
\boxed{
h_{\rm MS}<h_{\rm single}
\iff
\Delta U_{\rm shell}+L_{\rm MS}>0.
}
\]

Sufficient strict-improvement conditions include either:

1. \(K\ge2\), \(\gamma>0\), and at least one interior shell has
   \(p_k(R_{k+1}-R_k)>0\); or
2. \(L_{\rm MS}>0\).

Thus shell refinement and clipped lower information are additive improvements
to the radius.

This is a strict mathematical improvement over the specific one-sided
single-shell \(U/2\) certificate. It is **not yet evidence that the resulting
midpoint has lower fixed-panel MSE than R209**.

## 10. Parameterized Phase-2 compute

Let

- \(n=1024\): input width;
- \(m=1024\): final output width;
- \(L=16\): depth;
- \(K\): shell count;
- \(C_{\rm affine}\): all metered work needed to obtain the unit-box affine
  lower/upper coefficients and the certified \(\Lambda_j\) values;
- \(C_{\rm read}(K)\): Gaussian multi-shell readout.

### 10.1 Affine-bound acquisition

R376 froze, but did not execute, this conservative matrix-parallel envelope:

\[
\boxed{
C_{\rm affine}
\le
8Ln^3+64Ln^2
=
138,512,695,296.
}
\]

It corresponds to at most four dense \(n\times n\) products per layer plus
a \(64n^2\)-per-layer reserve for signs, slopes, intervals, norms, and
bookkeeping.

This remains an **implementation envelope, not a measured FlopScope count**.

The primary CROWN paper independently establishes polynomial-time bound
propagation; for an \(m\)-layer width-\(n\) network it states an
\(O(m^2n^3)\) complexity for its full robustness-bound procedure. R385 uses
the project-frozen R376 envelope for the proposed matrix-parallel
implementation, not the paper's asymptotic expression as a measured count.

### 10.2 Readout operations

The readout needs:

1. once per output:
   \(\sigma_j=\|a_j\|_2\) and \(\tau_j=\|a_j\|_1\);
2. \(K\) scalar shell probabilities \(p_k,q_k,\Delta p_k\);
3. for every shell/output pair:
   \(d_{jk}\), one normal CDF, one normal PDF, the closed-form \(G_{jk}\),
   tail/inner deductions, and clipping;
4. shell reduction, upper endpoint, midpoint, radius, and final-row assembly.

Pinned FlopScope 0.12.1 declares:

\[
\texttt{stats.norm.pdf}:27\ \text{flop\_cost/element},
\]

\[
\texttt{stats.norm.cdf}:48\ \text{flop\_cost/element},
\]

and the stats implementation computes in float64, so the billed rate is
\(2\times\): **54 and 96 billed FLOPs per element**, respectively.

The official Phase-2 rules forbid moving these Gaussian calculations into
unmetered Python \`math.*\` arithmetic for a scoring advantage; meaningful
numerical work must remain in FlopScope.

A conservative fully-vectorized billing envelope for the readout described
above is

\[
\boxed{
C_{\rm read}(K)
\le
(4mn-m)
+
K(180m+142)
+
16m.
}
\]

Interpretation:

- \(4mn-m\): one \(\ell_2\) and one \(\ell_1\) coefficient norm pass;
- \(180m\) per shell: conservative float64-rate envelope including the
  96m CDF bill, 54m PDF bill, and all vector arithmetic/selects used by
  \(G_k\), tail removal, inner removal, clipping, and shell accumulation;
- \(142\) per shell: conservative scalar shell-probability/radius arithmetic
  including normal CDF, power, differences, square root, and weighted-shell
  accumulation;
- \(16m\): endpoint/midpoint/radius/final-row assembly reserve.

This is a **static billing envelope for a specific vectorized schedule**, not
a measured trace. Exact billing must still be pinned by implementation before
submission.

For Phase 2 \(n=m=1024\),

\[
\boxed{
C_{\rm read}(K)
\le
4,209,664
+
184,462K.
}
\]

Examples:

\[
K=16:
\quad
C_{\rm read}\le7,161,056,
\]

\[
K=64:
\quad
C_{\rm read}\le16,015,232,
\]

\[
K=1024:
\quad
C_{\rm read}\le193,098,752.
\]

Even \(K=64\) is negligible next to the frozen affine envelope:

\[
C_{\rm total}(64)
\le
138,528,710,528.
\]

The Phase-2 score-floor compute boundary is

\[
0.1B
=
0.1\cdot2^{41}
=
219,902,325,555.2.
\]

Thus, **if** the affine implementation actually fits the R376 frozen envelope,
the \(K=64\) readout remains statically below the 10% scorer floor with very
large FLOP headroom.

This is a bounded-compute feasibility result, not an executed cost
measurement.

## 11. Memory

Separate acquisition memory from readout memory.

### Affine acquisition

R376 froze a conservative resident-memory envelope

\[
\boxed{
M_{\rm affine}\le256\ {\rm MiB},
}
\]

including the 16 supplied float32 weight matrices, multiple coefficient/work
matrices, vectors, and bookkeeping.

### Multi-shell readout

The lower coefficient matrix itself is

\[
4mn
=
4,194,304\ {\rm bytes}
=
4\ {\rm MiB}
\]

at float32.

If the shell/output calculations are vectorized over a \(K\times m\)
float64 work array and at most \(r\) such arrays are simultaneously live,

\[
\boxed{
M_{\rm read}
\le
4mn
+
8rKm
+
O(m+K)\ {\rm bytes}.
}
\]

For example, with \(K=64\), \(m=1024\), and a deliberately loose
\(r=10\),

\[
8rKm
=
5,242,880\ {\rm bytes}
\approx5\ {\rm MiB}.
\]

So a practical vectorized readout adds only single-digit MiB beyond the
coefficient matrix. It does not challenge the Phase-2 8 GB process cap under
the frozen R376 acquisition envelope.

Again, this is static allocation accounting, not a measured peak-RSS trace.

## 12. Residual-time operations

Phase 2 sets \(\lambda=0\) but imposes a hard \(0.4\) s residual cap. Official
rules explicitly state that residual time is for plumbing, not meaningful
unmetered computation.

Therefore the admissible implementation schedule is:

- Python residual work: fixed-size layer/shell orchestration, indexing,
  shape handling, and result assembly only;
- all coefficient norms, shell probabilities, Gaussian PDF/CDF calls,
  elementwise shell formulas, and reductions: FlopScope kernels;
- avoid a Python loop over \(K\times m\) scalar cells;
- preferably vectorize shells as \(K\times m\) arrays, so increasing \(K\)
  increases metered kernel size rather than unmetered Python arithmetic.

R385 cannot certify the \(0.4\) s residual gate or 120 s wall gate without an
implementation timing run. Those remain **UNKNOWN**.

## 13. Exact scorer-level GO gate against R209

For fixed MLP \(i\) and final coordinate \(j\), let

\[
L_{ij},U_{ij}
\]

be the multi-shell endpoints and

\[
\widehat\mu_{ij}
=
\frac{L_{ij}+U_{ij}}2,
\qquad
h_{ij}
=
\frac{U_{ij}-L_{ij}}2.
\]

Then

\[
|\widehat\mu_{ij}-\mu_{ij}|
\le h_{ij}.
\]

Define the certified final-row MSE envelope

\[
\boxed{
H_i^2
=
\frac1{1024}
\sum_{j=1}^{1024}h_{ij}^2.
}
\]

Let \(C_i\) be the **all-in measured candidate FLOPs** for that MLP once an
implementation exists.

WhestBench's exact valid-run per-MLP multiplier is

\[
g_i
=
\max\left(0.1,\frac{C_i}{2^{41}}\right).
\]

The exact **sufficient certificate GO gate** against the stored R209 same-panel
adjusted score

\[
S_{209}
=
8.170397440117225\times10^{-9}
\]

is

\[
\boxed{
\frac1{100}
\sum_{i=1}^{100}
H_i^2 g_i
<
8.170397440117225\times10^{-9}.
}
\]

If every MLP is measured at or below the score floor,

\[
C_i\le0.1\,2^{41},
\]

this simplifies to

\[
\boxed{
\frac1{100}
\sum_{i=1}^{100}
H_i^2
<
8.170397440117225\times10^{-8}.
}
\]

### What this gate means

If the inequality is established from sound intervals and measured valid-run
costs, then the **certificate itself** proves that the estimator's fixed-panel
score is below the R209 number.

### What this gate does not mean

Failure to certify the inequality does **not** prove the actual midpoint score
is worse than R209, because \(h_{ij}\) is a worst-case error radius.

Conversely, static FLOP feasibility alone is not a score claim.

The actual score-improvement statement is

\[
\boxed{
\frac1{100}
\sum_{i=1}^{100}
\left[
\frac1{1024}
\sum_{j=1}^{1024}
(\widehat\mu_{ij}-\mu_{ij}^{\rm target})^2
\right]
g_i
<
S_{209}.
}
\]

That quantity requires the fixed target means (or an official scorer result).

## 14. Numbers that remain unknown without Mini tensors / network weights

Without the fixed Phase-2 Mini network tensors, R385 cannot know, per MLP/output:

- \(a_j,\beta_j,c_j,\gamma_j\);
- \(\sigma_j=\|a_j\|_2\);
- \(\tau_j=\|a_j\|_1\);
- certified \(\Lambda_j\);
- exact shell clipped expectations \(J_{jk}\);
- cheap shell lower certificates \(\underline J_{jk}\);
- \(L_{ij},U_{ij},h_{ij}\);
- network-level \(H_i^2\);
- which radii \(R_1,\ldots,R_K\) minimize the actual certificate;
- whether any shell satisfies the zero-inner-loss condition
  \(d_{jk}\ge R_{k-1}\tau_j\);
- exact implementation-dependent \(C_{\rm affine,i}\);
- measured all-in \(C_i\);
- measured wall time / residual wall time / peak RSS.

Without the fixed Mini target tensors, R385 additionally cannot know:

- actual \(\mu_{ij}^{\rm target}\);
- actual midpoint error;
- actual final-layer MSE;
- actual adjusted score;
- whether the actual estimator beats R209 even if the certificate gate fails.

Target hashes or network IDs are insufficient to reconstruct these numerical
values.

## 15. GO / NO-GO

### Mathematical construction

\[
\boxed{\text{GO}}
\]

The combined method is explicit and sound:

\[
L_{\rm MS}\le\mu\le U_{\rm MS},
\qquad
\widehat\mu_{\rm MS}=(L_{\rm MS}+U_{\rm MS})/2,
\qquad
h_{\rm MS}=(U_{\rm MS}-L_{\rm MS})/2.
\]

It strictly improves the R376 single-shell \(U/2\) radius whenever

\[
\Delta U_{\rm shell}+L_{\rm MS}>0.
\]

### Bounded-compute feasibility

\[
\boxed{\text{CONDITIONAL GO}}
\]

If the affine-bound implementation fits the frozen R376 envelope, the
multi-shell readout is tiny by comparison and a practical \(K\) such as 16 or
64 remains far below the Phase-2 10% FLOP boundary. Memory is also statically
small.

Exact FlopScope cost, residual time, wall time, and RSS remain unmeasured.

### Fixed-panel certificate GO

\[
\boxed{\text{UNKNOWN / NOT ESTABLISHED}}
\]

The network weights needed to produce the affine coefficients and radii are
not available in this task.

### Actual score improvement over R209

\[
\boxed{\text{NO-GO FOR CLAIM}}
\]

No fixed target tensors/scorer result are available, and no run is authorized.
R385 therefore does not claim that the estimator beats R209.

## 16. Cheapest next falsifier if separately authorized

The next scientific step is **not** a scorer run.

On an already-local exact Mini network payload, with no targets exposed to
estimator construction:

1. freeze \(K\) and the radii before looking at targets;
2. implement one vectorized FlopScope unit-box affine pass plus the R385
   readout;
3. measure only:
   - exact all-in FlopScope cost;
   - residual time;
   - wall time;
   - peak memory;
   - \(L,U,h,H_i^2\);
4. stop if any resource gate fails;
5. only if the aggregate certificate inequality in §13 can be formed and
   passes should a separate allocation consider a same-panel scorer run.

R385 itself performs none of those steps.

## 17. Execution accounting

Requested scientific/project execution:

- estimator implementation: **NO**
- estimator runs: **0**
- synthetic runs: **0**
- Mini runs: **0**
- benchmark/scorer runs: **0**
- Actions runs: **0**
- benchmark/data downloads: **0**
- dependency installs: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submissions: **0**
- competition UI interaction: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**

Tooling disclosure: during desk work, **two local no-op shell invocations were
accidentally issued** (one empty Python heredoc and one \`true\` command). They
did not read project files, benchmark/data payloads, execute project code,
install anything, or produce scientific measurements. All scientific claims in
this report are source/algebra based.
