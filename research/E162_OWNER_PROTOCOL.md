# E162 OWNER PROTOCOL — AGO exact angular gauge only

Date: 2026-09-21  
Status: **OWNER FROZEN / ONE TARGET-FREE RUN AUTHORIZED AFTER ARM COMMIT**

Branch:

`research/e162-owner-ago-gauge-only-20260921`.

Parent support:

`research/e160-primary-source-angular-support-20260921@f425e18feab11ebcb3e8a908e713f36677f84e09`.

Idempotency key:

`ARC-E162-OWNER-AGO-GAUGE-ONLY-20260921`.

## 1. Candidate identity

**AGO — Angular Gauge Only.**

E162 tests exactly one delta against one clean-room K2 parent:

- exact K1/K2 Gaussian-to-angular gauge transform after the first activation state;
- exact final radial `a1(n)` mean readout;
- no K4;
- no D4;
- no D22;
- no scalar `c4`;
- no recurrent K4;
- no K3/D21 state;
- no E154/E157 code, workflow, artifacts, or branch ancestry.

This is the H160 mechanism and nothing else.

## 2. Clean-room parent

The frozen parent is a deterministic full-covariance K2 Wick closure implemented
from scratch on E162.

Input:

`X ~ N(0,I_n)`.

Initial state:

`mu_0=0`,
`C_0=I`.

For each zero-bias dense layer with row-weight matrix `W`:

`mu_pre = W mu`;

`C_pre = W C W^T`;

`v_i = C_pre,ii`.

Let

`sigma_i=sqrt(v_i)`,
`alpha_i=mu_pre,i/sigma_i`,
`phi_i=normal_pdf(alpha_i)`,
`Phi_i=normal_cdf(alpha_i)`.

The exact Gaussian marginal ReLU raw moments are

`p1_i = sigma_i phi_i + mu_pre,i Phi_i`;

`p2_i = (mu_pre,i^2+v_i) Phi_i + mu_pre,i sigma_i phi_i`.

The K2 off-diagonal Wick closure is frozen as

`P11_ij
 = C_pre,ij w1_i w1_j
 + 1/2 C_pre,ij^2 w2_i w2_j`

for `i != j`, with

`w1=Phi`,
`w2=phi/sigma`.

Then

`mu_next=p1`;

`C_next,ii=p2_i-p1_i^2`;

`C_next,ij=P11_ij` for `i!=j`.

No higher-order state exists.

The parent applies this same arithmetic at every layer.

## 3. AGO delta

The first activation is computed by exactly the same parent arithmetic.

Immediately after that first activation state, and only there, AGO replaces the
Gaussian-input K1/K2 state by the exact angular gauge state.

Let

`a1(n)=sqrt(2/n) Gamma((n+1)/2)/Gamma(n/2)`.

For the first activation Gaussian-state estimate `(mu_G,C_G)`:

`mu_A = mu_G/a1`;

`C_A
 = C_G
 - (1/a1^2 - 1) mu_G mu_G^T`.

All later layers run the same frozen K2 Wick closure as the parent, now on the
angular state.

AGO reports the final Gaussian-input mean as

`mu_out = a1 mu_A,final`.

There is no other candidate delta.

## 4. Exact gauge identities

For a zero-bias homogeneous network and

`X=(R/sqrt(n))Y`,

with `R independent of Y`:

`H_G=(R/sqrt(n))H_A`.

Because

`E[R/sqrt(n)]=a1`

and

`E[(R/sqrt(n))^2]=1`,

the exact first two moments satisfy

`mu_G=a1 mu_A`;

`C_G=C_A+(1-a1^2)mu_A mu_A^T`.

Equivalently,

`mu_A=mu_G/a1`;

`C_A=C_G-(1/a1^2-1)mu_G mu_G^T`.

Frozen identity gates:

1. algebraic round-trip `G -> A -> G` relative Frobenius error <= `2e-12`;
2. samplewise network homogeneity
   `F(sY)=sF(Y)` for positive frozen `s` <= `2e-12`;
3. on exact2D, analytic first-activation angular/Gaussian K1/K2 moments obey the
   same gauge relation <= `2e-12`.

## 5. Target firewall

Forbidden:

- public Phase-2 targets;
- public mini targets;
- scorer;
- holdout;
- full suite;
- submission;
- target fitting;
- post-result fitting;
- seed/rank/threshold sweep;
- E154 code or artifacts;
- E157 code or artifacts;
- K4/D4/D22/c4;
- rerun or rescue.

Synthetic weights and synthetic exact/Monte-Carlo references only.

## 6. Frozen falsifier

Exactly one GitHub Actions scientific run contains all fixtures plus in-process
deterministic replay.

### F0 exact2d/depth8

- width/input: 2;
- depth: 8;
- zero bias;
- He-Gaussian row weights;
- seed: `162002`;
- float64.

Reference:

- exact activation-sector integration on the radius-`sqrt(2)` circle;
- multiply exact angular final mean by exact `a1(2)`;
- no sampling.

The verifier also analytically integrates the first activation K1/K2 angular
moments and checks the exact gauge identities.

### F1 dense32/depth8

- width/input: 32;
- depth: 8;
- zero bias;
- He-Gaussian row weights;
- seed: `162032`;
- deterministic antithetic sphere reference;
- `M=32768`;
- reference seed: `162320`.

Reference Gaussian-input final mean:

`a1(32) * mean(F(Y))`.

### F2 adversarial16/depth8

- width/input: 16;
- depth: 8;
- zero bias;
- seed: `162016`;
- each layer:
  `W=Q_L diag(g) Q_R^T`;
- `Q_L,Q_R` are canonicalized QR factors of deterministic Gaussian matrices;
- `g` is linearly spaced on `[0.5,1.5]` then rescaled to RMS `sqrt(2)`;
- deterministic antithetic sphere reference;
- `M=32768`;
- reference seed: `162160`.

## 7. Candidate-before-reference order

Mandatory within the sole run:

1. construct frozen weights;
2. execute parent;
3. execute AGO;
4. execute AGO deterministic replay;
5. freeze/hashes of parent and AGO states;
6. only then import/build the verifier reference;
7. score final means/MSE;
8. emit one receipt payload.

Candidate/parent implementation may not import the verifier module.

## 8. Scientific metrics and gates

For each fixture:

`MSE = mean((mu_hat-mu_ref)^2)`.

Record:

- parent final-mean MSE;
- AGO final-mean MSE;
- ratio `MSE_AGO/MSE_parent`;
- relative RMS final-mean error for both.

Frozen scientific gate:

`MSE_AGO <= 0.98 * MSE_parent`

on **each** of F0, F1, F2.

No averaging across fixtures can rescue a failure.

If parent MSE is numerically zero or the ratio is otherwise unevaluable, the
gate fails.

### Reference stability for F1/F2

Split the deterministic sphere reference into four equal contiguous batches.

Let `SE_ref` be the RMS standard error of the four batch means after exact
radial scaling.

Require either

`SE_ref <= 0.20 * min(RMSE_parent, RMSE_AGO)`

or

`SE_ref <= 1e-4`.

If not, the sole run is terminal NO-GO; increasing `M` is forbidden.

## 9. Determinism

AGO replay must be bitwise identical for:

- final mean;
- all stored layer means;
- all stored covariance matrices;
- gauge-transformed first state;
- cost receipt.

Parent is also hashed and frozen before reference materialization.

## 10. Complete production cost upper

Production shape:

- width `n=1024`;
- depth `L=16`;
- float deterministic full-covariance K2 closure.

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`floor(0.135B)=296,868,139,499 FLOPs`.

### A. Covariance linear transport

Two dense square GEMMs per layer:

`C_A = L * 4 n^3
     = 68,719,476,736`.

### B. Mean dense matvec

`C_B = L * 2 n^2
     = 33,554,432`.

### C. K2 ReLU off-diagonal/diagonal arithmetic

Conservative:

`C_C = L * 24 n^2
     = 402,653,184`.

### D. Wick/CDF/PDF/scalar work

Conservative:

`C_D = L * 1024 n
     = 16,777,216`.

### E. General parent helper reserve

Twenty `2n^3` units:

`C_E = 42,949,672,960`.

This covers symmetry enforcement, clears/copies, finite checks, allocations,
and unnamed parent helper arithmetic.

### F. AGO gauge overlay

Frozen E160 conservative bound:

`C_F = 8n^2 + 64Ln
     = 9,437,184`.

This covers:

- first-state mean division;
- one `mu mu^T` outer product;
- covariance gauge correction;
- final radial scaling;
- overlay finite/bookkeeping work.

### Complete parent+AGO upper

`C_total
 = 112,131,571,712 FLOPs`.

Utilization:

`C_total/B
 = 0.05099153518676758`.

Slack:

`296,868,139,499
 -112,131,571,712
 =184,736,567,787 FLOPs`.

Pre-code cost gate:

**PASS**.

No Strassen is needed or permitted.

## 11. Mandatory gates

All must pass:

1. source firewall;
2. no E154/E157 code/artifact import;
3. no K4/D4/D22/c4 token/state in candidate implementation;
4. candidate/reference separation;
5. finite parent/candidate/reference;
6. exact gauge round-trip <= `2e-12`;
7. exact2D analytic first-state gauge identity <= `2e-12`;
8. homogeneity <= `2e-12` all fixtures;
9. bitwise deterministic replay;
10. reference stability F1/F2;
11. AGO MSE <= `0.98 parent MSE` on F0;
12. AGO MSE <= `0.98 parent MSE` on F1;
13. AGO MSE <= `0.98 parent MSE` on F2;
14. independent production ledger exactly reconciles;
15. complete cost <= `0.135B`;
16. exactly one external run;
17. no sweep/rescue/rerun.

Any failed or unevaluable mandatory gate:

**E162 TERMINAL NO-GO / CLOSE AGO.**

All gates pass:

**E162 TARGET-FREE SCIENTIFIC GO — AGO.**

A GO does not authorize public/scorer/holdout/full/submission work.

No canonical or ledger mutation.
