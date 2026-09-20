# E126 THEORY result — target-free finite-sample certificate for multi-source algebraic frames

Idempotency key: ARC-E126-MULTISOURCE-FRAME-CERTIFICATE-20260920

Decision: **TERMINAL NO-GO — FINITE-SAMPLE CERTIFICATE NOT TIGHT ENOUGH UNDER PRODUCTION BUDGET**.

## Theory

For iid Haar-Stiefel frames U_p and any fixed unit algebraic code C={a_r}, define

Z_p = E[chi_d] * (1/J) * sum_r F(U_p a_r).

Every fixed U_p a_r is marginally uniform on the sphere, so E[Z_p]=E[F(X)] for X~N(0,I_d). The frame mean is therefore exactly unbiased for arbitrary dense zero-bias ReLU weights.

For final coordinate j the target-free weight-only envelope

B_j = E[chi_d] * prod_(l<L)||W_l||_F * ||W_L[:,j]||_2

satisfies 0 <= Z_(p,j) <= B_j.

With P independent frames, coordinate sample variance s_j^2, m outputs, and frozen delta=0.05, the familywise empirical-Bernstein radius is

lambda = log(4m/delta)

r_j = sqrt(2*s_j^2*lambda/P) + 7*B_j*lambda/(3*(P-1)).

Thus with familywise confidence at least 95%,

RMS(mu_hat-E[F(X)]) <= C_RMS = sqrt(mean_j(r_j^2)).

The optimistic variance-only floor is

C_var = sqrt(mean_j(2*s_j^2*lambda/P)),

and C_RMS >= C_var regardless of how the deterministic range envelope is improved.

ARC RMS target:

sqrt(1.89e-8) = 1.374772708486752e-4.

## Adversarial dense fixtures

Frozen fixtures were exact-reference-capable but candidate-visible only as dense weights:

- 8-D / 4 independent exact 2-D nonlinear sources;
- 16-D / 8 independent exact 2-D nonlinear sources;
- dense orthogonal input mixing;
- three positive dense hidden basis transforms A=(1-rho)I+rho*11^T/d with rho=0.99;
- compensating A^-1 in the following nonlinear weight;
- seven dense weight matrices total;
- condition number(A)=100.

Dense-vs-latent functional agreement:

- 8-D max abs: 1.0080825063596421e-13
- 16-D max abs: 7.638334409421077e-14

Every frozen weight matrix had dense fraction 1.0.

## Tightness

Budget-max P=225 independent frames was used.

### 8-D

Across four frozen seeds:

- target-free C_RMS: approximately 1.868827587e7
- verifier-only spectral-envelope certificate: approximately 5.183352898e6
- variance-only C_var:
  0.0078816616 .. 0.0087710363
- C_var / ARC RMS target:
  **57.3307x .. 63.7999x**
- post-hoc exact-reference RMS:
  2.04008977e-4 .. 3.25090274e-3
- every emitted certificate covered the realized exact error.

### 16-D

Across four frozen seeds:

- target-free C_RMS: approximately 3.949732471e7
- verifier-only spectral-envelope certificate: approximately 3.973833570e6
- variance-only C_var:
  0.0180285592 .. 0.0182046397
- C_var / ARC RMS target:
  **131.1385x .. 132.4193x**
- post-hoc exact-reference RMS:
  1.45406243e-4 .. 6.31129652e-3
- every emitted certificate covered the realized exact error.

The decisive blocker is not the deliberately adversarial norm envelope. Even after deleting the range penalty entirely, the computable sample-variance term exceeds the winning RMS scale by at least 57.33x on 8-D and 131.14x on 16-D at the largest production-admissible frame count.

Therefore no improvement to the weight-range calculation alone can make this E126 empirical-Bernstein certificate sufficiently tight.

## Production accounting

Physical E122/E123 accounting was corrected to include all diagnostics and E126 certificate work.

At P=225:

- incremental all-in: 136,237,052,214 FLOPs
- incremental cap: 136,758,472,261 FLOPs
- slack: 521,420,047 FLOPs
- total with E104 base: 285,351,603,174 FLOPs
- utilization: 0.12976288561458205

At P=226:

- incremental all-in: 136,842,400,884 FLOPs
- cap exceeded by: 83,928,623 FLOPs
- total utilization: 0.1300381663186272

Hence P=225 is the maximum frame count under the frozen complete accounting.

## Execution

A first Actions attempt failed before tests/science because pytest was absent from the runner environment:

- run/job: 35503180953 / 106058452194
- scientific falsifier: skipped
- artifact: absent
- scientific evidence: none.

Only the workflow dependency line was repaired; no scientific code, fixture, seed, confidence, frame count, code or bound changed.

The first actual scientific falsifier:

- run/job: 35503232256 / 106058580566
- focused tests: 4 passed in 0.16s
- scientific step: success
- artifact: e126-multisource-frame-certificate
- artifact ID: 10603195978
- artifact ZIP SHA256: 0ef4538a57b8e6bcfa1c40d087f916dbb6870d76b0aa5b436c687ec088629bb0

## Verdict

**E126 TERMINAL NO-GO.**

The certificate is mathematically target-free and valid for arbitrary dense weights, and the production accounting fits at P=225. It is not remotely tight enough at that P. The variance-only term itself is already orders of magnitude above the ARC RMS target, so tighter global range certification cannot rescue this lane.

No public/public-mini, benchmark target, scorer, holdout/full, production scientific run, target fitting, tuning, sweep, canonical mutation or ledger mutation occurred.
