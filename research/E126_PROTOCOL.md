# E126 THEORY — target-free finite-sample certificate for multi-source algebraic frames

Idempotency key: ARC-E126-MULTISOURCE-FRAME-CERTIFICATE-20260920

Status: ONE ADVERSARIAL 8D/16D CERTIFICATE FALSIFIER AUTHORIZED; NO PRODUCTION SCIENTIFIC RUN.

## Provenance

E123 independently verified that the E122 Haar-8 antipodal-simplex estimator is target-free and unbiased in exact arithmetic, but closed the frozen candidate because no computable finite-sample error certificate existed and its all-in ledger omitted executed diagnostics.

E126 does not reopen E122. It tests whether the same class of independent multi-source algebraic-frame estimators admits a target-free finite-sample certificate tight enough for ARC.

No exact reference, benchmark/public target, scorer, holdout/full, tuning, sweep or rescue is available to the certificate path.

## Estimator class

Let F:R^d->R^m be any finite zero-bias dense ReLU network with ReLU after every dense layer. Let U_p in V_(d,K) be iid Haar-Stiefel frames and C={a_1,...,a_J} a fixed unit algebraic code.

Define one independent frame contribution

Z_p = mu_d/J * sum_r F(U_p a_r),  mu_d = E[chi_d].

For every fixed a_r, Haar invariance makes U_p a_r uniform on S^(d-1). Therefore E[Z_p]=E[F(X)] for X~N(0,I_d), and mu_hat=(1/P)sum_p Z_p is exactly unbiased for arbitrary dense weights. Dependence inside one frame is unrestricted; frames are independent.

E126 instantiates K=8 and the fixed 18-word antipodal regular-simplex code, but the certificate uses only independent bounded frame contributions.

## Weight-only range envelope

With row-vector propagation h_0=q and h_l=ReLU(h_(l-1) W_l), for ||q||_2=1,

||h_l||_2 <= ||h_(l-1)||_2 ||W_l||_2 <= ||h_(l-1)||_2 ||W_l||_F.

Thus for final coordinate j,

0 <= F_j(q) <= (product_(l=1..L-1) ||W_l||_F) ||W_L[:,j]||_2.

Define

B_j = mu_d (product_(l=1..L-1) ||W_l||_F) ||W_L[:,j]||_2.

Then 0 <= Z_(p,j) <= B_j. This is computable from arbitrary finite dense weights without targets or weight-distribution assumptions.

For fixture tightness diagnostics only, E126 also reports a spectral-norm envelope replacing the Frobenius norms with exact spectral norms. Production admission does not rely on free spectral SVDs.

## Familywise empirical-Bernstein certificate

Freeze delta=0.05. This is deliberately lenient; stricter confidence only increases the bound.

Let s_j^2 be the unbiased sample variance of the P iid frame contributions Z_(p,j). Applying a two-sided empirical-Bernstein bound on [0,B_j] and a union bound over m coordinates gives simultaneous coverage at least 1-delta with

lambda = log(4m/delta),

r_j = sqrt(2 s_j^2 lambda / P) + 7 B_j lambda / (3(P-1)).

The target-free final-output RMS certificate is

C_RMS = sqrt(mean_j r_j^2).

It consumes only realized frame contributions, network weights, dimensions and frozen delta.

Define the optimistic variance-only floor

C_var = sqrt(mean_j (2 s_j^2 lambda / P)).

Because the range term is nonnegative, C_RMS >= C_var. If C_var exceeds sqrt(1.89e-8), no tighter range computation can rescue this empirical-Bernstein certificate at the same P.

ARC RMS target:
epsilon_star = sqrt(1.89e-8) = 1.374772708486752e-4.

## Frozen adversarial exact-reference fixtures

The candidate/certificate sees only dense weights. Exact means are materialized only after all candidate/certificate records are complete.

Fixtures:
- d=m=8: four independent exact 2-D depth-4 subnetworks;
- d=m=16: eight independent exact 2-D depth-4 subnetworks.

To hide block sparsity and adversarially stress weight-norm certificates:
1. apply a deterministic dense orthogonal input mixing Q;
2. after each of the first three nonlinear latent layers insert A=(1-rho)I + rho 11^T/d with rho=0.99;
3. because hidden activations are nonnegative, ReLU(hA)=hA;
4. compensate in the following weight by A^-1.

The seven-layer dense sequence is:
Q B1, A1, A1^-1 B2, A2, A2^-1 B3, A3, A3^-1 B4.

Each A has condition number 100. The represented function and exact Gaussian mean remain the original independent 2-D block function.

Frozen seeds:
8-D blocks 126800..126803; mixing 126890; frame seeds 126900..126903.
16-D blocks 1261600..1261607; mixing 1261690; frame seeds 1261700..1261703.

Every candidate uses the budget-max P derived below.

## Production cost gate before execution

Physical E122/E123 context:
- E104 base all-in = 149114550960 FLOPs;
- exact total 0.13 cap = floor(0.13*2^41)=285873023221 FLOPs;
- exact incremental cap = 136758472261 FLOPs.

Production constants: d=n=m=1024, L=16, K=8, J=18.

E126 bills:
1. original E122 algebraic-frame estimator formula;
2. E123 orthogonality and source-norm diagnostics;
3. deployable Frobenius range envelope:
   L*(2*n*n) + 8*((L-1)+n);
4. frame-code reduction, sample mean/variance and certificate:
   P*((J+8)*n) + 32*n.

At P=225:
- E126 increment = 136237052214 FLOPs;
- incremental slack = 521420047 FLOPs;
- total including E104 base = 285351603174 FLOPs;
- utilization = 0.12976288561458205.

At P=226:
- E126 increment = 136842400884 FLOPs;
- exceeds incremental cap by 83928623 FLOPs.

Therefore P_max=225. No larger frame count may be used as rescue.

## Frozen gates

Integrity:
1. dense fixture weights finite;
2. dense reparameterized network matches latent network on deterministic probes <=1e-10 max abs;
3. simplex algebra passes existing E122 tolerances;
4. all frame contributions/certificates finite;
5. observed frame contributions are <= Frobenius range;
6. deterministic replay exact;
7. candidate/certificate receives no exact mean or block decomposition;
8. no benchmark/public/scorer/holdout/full access.

Tightness on every frozen 8-D and 16-D seed:
9. verifier-only actual RMS error <= emitted target-free certificate;
10. C_RMS <= epsilon_star;
11. C_var <= epsilon_star.

Production:
12. P=225 all-in increment <=136758472261;
13. P=226 all-in increment >136758472261.

All gates pass => E126 THEORY CERTIFICATE GO.
Any gate 10 or 11 fails => E126 TERMINAL NO-GO — FINITE-SAMPLE CERTIFICATE NOT TIGHT ENOUGH UNDER PRODUCTION BUDGET.
No alternate confidence, P, K, code, fixture or bound after execution.
