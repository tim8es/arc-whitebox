# E154 protocol — clean-room angular-radial K4 correction

Idempotency key: `ARC-E154-CLEAN-ANGULAR-RADIAL-K4-20260921`.

Status at freeze:

**PROTOCOL ONLY / ONE TARGET-FREE FALSIFIER AUTHORIZED AFTER CODE.**

Branch:

`research/e154-clean-angular-radial-k4-20260921`.

Clean parent:

`research/e150-observable-response-query-closure-20260921@86f736cda004b60bc6c9d7379efe71164cecdef5`.

E151 is terminal for a procedural import-path failure before scientific main
entry. E154 does not reuse, copy, import, patch, rerun, or branch from E151
code. The only E151 fact used is its terminal receipt status:
science was never evaluated and rerun is forbidden.

## 1. Hypothesis

**H154 — ARK4: angular-radial analytic K4 correction.**

For a zero-bias ReLU network, positive homogeneity permits exact separation of
the Gaussian input radius from the angular input.

Let

`G ~ N(0,I_n)`,
`R = ||G||_2`,
`Y = sqrt(n) G / ||G||_2`.

Then

`G = (R/sqrt(n)) Y`

with `R` independent of `Y`, and `Y` uniform on the sphere of radius
`sqrt(n)`.

For every zero-bias ReLU network map `F`,

`F(a x)=a F(x)` for every `a>=0`.

Therefore exactly,

`F(G) = (R/sqrt(n)) F(Y)`.

E154 tests whether a minimal mechanistic closure operating on the angular law,
with an analytic sphere-induced K4 diagonal, improves the same closure without
K4 enough to justify further work.

This is a new clean-room estimator class, not E151 repair.

## 2. Exact radial moment identities

Define

`a_p(n)=E[R^p]/n^(p/2)`.

For chi radius `R~chi_n`:

`a_p(n)=2^(p/2) Gamma((n+p)/2)/(n^(p/2) Gamma(n/2))`.

The first four are:

`a_1 = sqrt(2/n) Gamma((n+1)/2)/Gamma(n/2)`;

`a_2 = 1`;

`a_3 = ((n+1)/n) a_1`;

`a_4 = (n+2)/n`.

For any scalar coordinate `Z=F_j(Y)`, let angular raw moments be
`m_p=E[Z^p]`. The corresponding Gaussian-input raw moments are exactly

`M_p = a_p m_p`.

Hence the exact fourth-cumulant diagonal identity is

`kappa4_G
 = a4 m4
 - 4 a1 a3 m1 m3
 - 3 m2^2
 + 12 a1^2 m1^2 m2
 - 6 a1^4 m1^4`.

No fitted coefficient enters this identity.

## 3. Exact sphere K4 tensor at the angular input

For `Y` uniform on the radius-`sqrt(n)` sphere:

`E[Y_i Y_j] = delta_ij`;

`E[Y_i Y_j Y_k Y_l]
 = n/(n+2)
   (delta_ij delta_kl
    + delta_ik delta_jl
    + delta_il delta_jk)`.

Therefore

`Cum4(Y_i,Y_j,Y_k,Y_l)
 = -2/(n+2)
   (delta_ij delta_kl
    + delta_ik delta_jl
    + delta_il delta_jk)`.

In particular:

`kappa4(Y_i) = -6/(n+2)`;

and for `i!=j`,

`Cum(Y_i,Y_i,Y_j,Y_j) = -2/(n+2)`.

For any deterministic linear image `Z=A^T Y` with covariance
`C=A^T A`,

`Cum4(Z_i,Z_j,Z_k,Z_l)
 = -2/(n+2)
   (C_ij C_kl + C_ik C_jl + C_il C_jk)`.

Thus the exact diagonal after a purely linear angular step is

`kappa4_i = -6 C_ii^2/(n+2)`.

The exact 31 and 22 identities are

`K31_ij = -6 C_ii C_ij/(n+2)`;

`K22_ij = -2(C_ii C_jj + 2 C_ij^2)/(n+2)`.

These are the analytic K4 identities under test.

## 4. Minimal V29-compatible closure

E154 intentionally does not reproduce the V29 source stack, fitted LAM table,
CORR_BETA, D21 feedback, or target-fitted riders.

It retains only the mechanistic interfaces needed to isolate the K4 question:

- full mean vector;
- full covariance matrix;
- per-neuron fourth-cumulant diagonal;
- Gaussian/ReLU Wick coefficients;
- zero-bias dense linear layers.

The closure is "V29-compatible" in the narrow mechanistic sense that K4 enters
a ReLU expectation through the same fourth-Wick derivative channel, while
covariance remains a full matrix state.

### 4.1 Baseline angular Gaussian closure

Given angular state `(mu,C)` and weight `W`:

`mu_pre = W^T mu`;

`C_pre = W^T C W`;

`v = diag(C_pre)`;

`sigma=sqrt(v)`,
`alpha=mu_pre/sigma`,
`phi=normal_pdf(alpha)`,
`Phi=normal_cdf(alpha)`.

Gaussian ReLU raw moments:

`g1 = sigma phi + mu_pre Phi`;

`g2 = (mu_pre^2+v) Phi + mu_pre sigma phi`.

Baseline post state:

`mu_next=g1`;

`C_next,ij = Phi_i Phi_j C_pre,ij` for `i!=j`;

`C_next,ii = g2_i-g1_i^2`.

This is the no-K4 comparator.

### 4.2 ARK4 candidate

At every preactivation E154 applies the memoryless angular-radial K4 identity

`k4_i = -6 v_i^2/(n+2)`.

This identity is exact for the first angular linear step. After a ReLU it
becomes the frozen closure hypothesis: the current angular law is replaced, for
the K4 channel only, by the covariance-matched sphere-linear law.

The fourth Wick coefficient for ReLU is

`w4_1
 = E[d^4 ReLU(N(mu,v))]
 = sigma^-3 (alpha^2-1) phi`.

Therefore the first-order K4 correction to the ReLU mean is

`delta g1 = k4 * w4_1 / 24`.

For the second raw moment, using
`d^4 ReLU(z)^2 = 2 d^3 ReLU(z)` in the Wick expectation,

`w4_2 = -2 alpha phi / sigma^2`.

Thus

`delta g2 = k4 * w4_2 / 24`.

Candidate update:

`mu_next = g1 + delta g1`;

`C_next,ii = (g2+delta g2)-mu_next^2`;

and the same minimal off-diagonal Gaussian/Wick update as the baseline.

No K3/D21 state is hidden inside E154.

### 4.3 Exact final radial reconstruction

The closure runs on the angular input law.

The final Gaussian-input mean estimate is exactly rescaled by

`a1(n)`:

`mu_G_hat = a1(n) mu_Y_hat`.

Any remaining estimator error is angular-closure error, not radial
reconstruction error.

## 5. Why Strassen is not authorized

The user permits exact one-level Strassen only if the cost ledger proves it is
needed/admissible.

The classical two-GEMM covariance propagation already leaves very large budget
slack.

Therefore E154 freezes:

**STRASSEN_LEVELS = 0.**

No Strassen code or parity path is allowed under E154.

This avoids importing a numerical/cost mechanism that is unnecessary for the
scientific question.

A future successor could separately test Strassen if classical covariance
became the binding cost.

## 6. Complete production FLOP upper

Production shape:

- width/input `n=1024`;
- depth `L=16`;
- zero bias;
- full covariance state;
- no K3 source carrier;
- no Strassen.

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`floor(0.135 B)=296,868,139,499 FLOPs`.

### A. Full covariance linear transport

Two dense square products per layer:

`C_pre=W^T C W`.

Charge:

`C_A=L*4 n^3
 =68,719,476,736`.

### B. Mean dense matvec

`C_B=L*2 n^2
 =33,554,432`.

### C. ReLU covariance update and diagonal replacement

Conservative:

`C_C=L*16 n^2
 =268,435,456`.

### D. K4 diagonal/Wick scalar work

Conservative:

`C_D=L*512 n
 =8,388,608`.

### E. Radial gamma/scalar/homogeneity helpers

Conservative:

`C_E=L*128 n
 =2,097,152`.

### F. General helper/accounting reserve

Freeze twenty V29 units:

`C_F=20*(2 n^3)
 =42,949,672,960`.

This covers:

- array clears/copies;
- symmetry enforcement;
- finite checks;
- normal CDF/PDF accounting;
- clipping;
- final radial scaling;
- any otherwise unnamed operation class.

Any unlisted class above this reserve is a cost failure.

### Complete all-in upper

`C_total
 =111,981,625,344 FLOPs`.

Utilization:

`C_total/B
 =0.05092334747314453`.

Slack to cap:

`184,886,514,155 FLOPs`.

Pre-code production cost gate:

**PASS**.

Because classical arithmetic is already only about 0.051B, one-level Strassen
is not scientifically or economically required and remains forbidden.

## 7. Frozen target-free falsifier

Exactly one workflow execution may contain all three fixtures and deterministic
replay.

No second run is permitted.

### Fixture A — exact 2D angular network

- width/input: 2;
- depth: 8;
- zero bias;
- He-Gaussian weights;
- network seed: `154002`.

The verifier computes the angular mean on the circle exactly by propagating the
piecewise-linear homogeneous network sector by sector.

For each angular sector, the active pattern is fixed and the network is a
linear map of

`Y(theta)=sqrt(2)(cos theta,sin theta)`.

Sector boundaries are exact ReLU zero crossings. The integral of each linear
piece is analytic.

This yields an exact target-free angular final mean.

The input K4 identity is also checked analytically:

`kappa4(Y_i)=-6/(2+2)=-3/2`.

### Fixture B — dense 32D

- width/input: 32;
- depth: 8;
- zero bias;
- He-Gaussian weights;
- seed: `154032`;
- deterministic antithetic sphere reference:
  `M=32768` directions;
- reference RNG seed: `154320`.

### Fixture C — adversarial 16D

- width/input: 16;
- depth: 8;
- zero bias;
- weight seed: `154016`;
- each layer is
  `sqrt(2) Q1 diag(g) Q2^T`;
- `g` is a frozen rotated geometric gain vector in `[0.70,1.30]`;
- deterministic antithetic sphere reference:
  `M=32768`;
- reference RNG seed: `154160`.

The adversarial fixture rotates coordinates every layer.

## 8. Candidate-before-reference ordering

Mandatory:

1. construct weights;
2. run baseline and ARK4 candidate;
3. deterministic replay and freeze all candidate state/hashes/cost;
4. only then construct exact/empirical angular reference;
5. score;
6. write one result.

Candidate code may import only weights/math/numpy; it may not import the
reference module.

## 9. Exact homogeneity gate

For deterministic verifier rays and positive radii:

`F((R/sqrt(n))Y)`

must equal

`(R/sqrt(n))F(Y)`

to relative Frobenius error

`<=1e-12`.

This gate is independent of the candidate closure.

## 10. K4 identity gates

### 2D analytic

Input diagonal K4 identity must be exact to absolute error `<=1e-14`.

### 32D/16D empirical input and first preactivation

For the deterministic sphere reference:

- input diagonal K4 relative RMS vs `-6/(n+2)` <= `0.06`;
- first-preactivation diagonal K4 relative RMS vs
  `-6 var^2/(n+2)` <= `0.06`.

These gates check the analytic identity and reference quality.

### Deep closure falsifier

For preactivation layers 2..8, compare the frozen memoryless ARK4 diagonal

`-6 var^2/(n+2)`

against empirical angular K4 diagonals.

Pooled relative RMS must be

`<=0.35`

on both 32D and adversarial 16D.

This is deliberately loose: E154 is testing whether the analytic radial K4
channel remains a meaningful mechanistic approximation after nonlinear angular
distortion.

Failure closes E154.

## 11. Final-mean scientific gates

Let the exact/reference Gaussian-input mean be the angular reference mean
multiplied by exact `a1(n)`.

For each fixture record baseline and ARK4 relative RMS final-mean errors.

All must pass:

1. ARK4 error is strictly lower than baseline error on all three fixtures;
2. ARK4/baseline error ratio <= `0.95` on 32D;
3. ARK4/baseline error ratio <= `0.95` on adversarial 16D;
4. exact 2D ARK4 relative RMS <= `0.05`;
5. 32D ARK4 relative RMS <= `0.05`;
6. adversarial16 ARK4 relative RMS <= `0.05`.

No public target enters these gates.

## 12. Reference-stability gate

For 32D/16D split the antithetic sphere sample into four deterministic equal
batches.

Let `SE_ref` be the RMS standard error of the four batch means.

Require

`SE_ref <= 0.20 * ||mu_candidate-mu_reference||_RMS`

or absolute `SE_ref <=1e-4`, whichever is easier to satisfy.

If the reference is too noisy to decide the candidate gate, E154 fails rather
than increasing `M` after the run.

## 13. Determinism and firewall

All must pass:

- candidate finite;
- reference finite;
- candidate replay bitwise exact;
- candidate imports no E151 module/file;
- candidate imports no exact-reference module;
- no dataset/public/public-mini/scorer/holdout/full/submission access;
- no target fit;
- no sweep;
- production ledger independently reconciles;
- classical all-in <=0.135B;
- Strassen code path absent.

## 14. Run discipline

After this protocol commit:

1. implement clean-room candidate;
2. implement separate verifier/reference;
3. focused tests;
4. create workflow last;
5. arm exactly one target-free execution;
6. seal GO or terminal NO-GO receipt;
7. no rerun/rescue.

If any gate fails or is unevaluable:

**E154 TERMINAL NO-GO / CLOSE ARK4.**

If every gate passes:

**E154 TARGET-FREE SCIENTIFIC GO — ARK4.**

A GO would still not authorize public/scorer/holdout/full/submission work.

No canonical or ledger mutation.
