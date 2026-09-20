# E132 protocol — layer-born source-age D21 Hermite transport

Idempotency key: `ARC-E132-LAYER-BORN-SOURCE-AGE-D21-20260920`.

Status at freeze: **PROTOCOL ONLY / ONE TARGET-FREE EXACT-SMALL FALSIFIER RUN AUTHORIZED AFTER CODE**.

Branch:
`research/e132-layer-born-source-age-d21-20260920`.

Direct parent:
`research/bootstrap@7a0034088ebbffbd74b441e1797c272e9d33cbff`.

## Public clue admitted — and no more

E132 uses only the following public mechanism clue as scientific motivation:

- non-Gaussian source terms are born at different ReLU layers;
- the cross-neuron `D21_{ic}=kappa3_{iic}` slice is a meaningful interface to later ReLU updates;
- older transported sources can retain substantial high-rank dependence while increasingly sharing a common subspace.

E132 does **not** import another team's implementation, fitted ranks, fitted coefficients,
per-layer tuning tables, benchmark outputs, or private targets.

Its source-age schedule, ranks, estimator and certificate below are independently frozen.

## Explicit non-rescue boundary

E132 is not and does not modify:

- E122 Haar-8 antipodal simplex source code;
- either E124 source-interaction lane;
- E127 sparse hypergraph/Mobius closure;
- E121 Haar-plane orbit;
- activation-boundary flux lanes;
- target-fitted control coefficients.

E132 does not change, rerun, or reinterpret any closed experiment.

## Estimator overview

E132 is an **unbiased Gaussian-input Monte Carlo estimator with a structure-derived
zero-mean cubic Hermite correction**.

The correction coefficient is built from an explicit layer-born D21 state whose old
sources are transported by age and compressed into shared/nested bases.

There is no target fit. The exact final mean is verifier-only and is materialized only
after the candidate output is frozen.

### 1. Pilot/evaluation split

Production-frozen counts:

- pilot trajectories: `P=256`;
- evaluation trajectories: `M=2048`;
- width/input dimension: `n=d=1024`;
- ReLU depth: `L=16`.

Pilot trajectories are propagated through layers `1..15` only.

Evaluation trajectories are propagated through all 16 layers.

The pilot set is used only to construct the source/D21 correction. The final estimate
uses only the independent evaluation set, preserving conditional unbiasedness.

## Layer-born D21 state

For pilot hidden activation matrix `H_l in R^(P x n)`, define centered state

`X_l = H_l - mean_rows(H_l)`.

Define the empirical cross-neuron third slice

`D_l[i,c] = P^{-1} sum_p X_l[p,i]^2 X_l[p,c]`.

This includes the diagonal `D3`; the final Hermite correction zeroes the diagonal and
uses only cross-neuron `i != c` entries.

For a dense layer matrix `W`, define the frozen algebraic D21 transport

`T_W(D) = (W o W)^T D W`.

If `D ~= Q C`, this transport is evaluated as

`Q' = (W o W)^T Q`,
`C' = C W`.

E132 never claims that `T_W` is the exact nonlinear D21 law. Instead every layer
creates an explicit **birth residual** that absorbs the difference between the newly
observed pilot D21 and the compressed transported old-source prediction.

At hidden layer `l`:

1. transport every live older source state through `T_{W_l}`;
2. combine/rebase states according to their age;
3. reconstruct the transported old-source prediction `D_old,l`;
4. compute the new birth
   `B_l = D_l - D_old,l`;
5. compress `B_l` into the fresh-source rank and attach age 0.

Thus sources are explicitly born at layers and aged by transport. Compression error
does not introduce estimator bias because the resulting D21 object is used only as a
coefficient of an exactly zero-mean control term.

## Frozen source-age basis schedule

Independent schedule, fixed before code:

- age 0 and age 1:
  separate one-sided rank
  `r_y(n)=max(1,ceil(n/32))`;
- ages 2, 3, 4:
  one **shared left basis**
  `Q_s` of rank
  `r_s(n)=max(1,ceil(3n/64))`,
  with distinct right coefficients for each age;
- age >=5:
  one old aggregate using a **nested left sub-basis**
  `Q_n=Q_s R_n` of rank
  `r_n(n)=max(1,ceil(3n/128))`.

At production width 1024 this is:

- `r_y=32`;
- `r_s=48`;
- `r_n=24`.

No rank sweep or post-result rank change is allowed.

### Deterministic compression

Every full matrix-to-basis compression uses a fixed Rademacher range sketch whose seed
is a deterministic function of experiment id, layer and cohort.

For matrix `A` and target rank `r`:

1. form `Y=A Omega`;
2. thin QR of `Y`;
3. use the first `r` canonicalized columns as `Q`;
4. store `C=Q^T A`.

Column signs are canonicalized by the largest-magnitude entry.

No target, exact final mean, candidate error or benchmark score enters basis choice.

## D21 Hermite correction

Let `D_corr` be the final compressed penultimate D21 state with its diagonal zeroed.

Let `u_i` be the normalized first-layer weight column for hidden coordinate `i`.
For standard Gaussian input `x`, define the exact zero-mean cubic Gaussian Hermite
feature

`H_iic(x)
 = (u_i^T x)^2 (u_c^T x)
   - ||u_i||^2 (u_c^T x)
   - 2 (u_i^T u_c)(u_i^T x)`.

For every fixed `u_i,u_c`,

`E[H_iic(X)]=0`.

Let final weight matrix be `W_L`.

The pilot-frozen scale is

`gamma = 1 / ( n * max(1, ||D_corr||_F) )`.

For output coordinate `j`,

`g_j(x)
 = gamma * sum_{i,c} W_L[i,j] D_corr[i,c] H_iic(x)`.

The candidate estimator is

`mu_hat = M^{-1} sum_{m=1}^M [F(x_m)-g(x_m)]`.

Conditioned on the pilot state,

`E[mu_hat | pilot] = E[F(X)]`.

Therefore source compression, imperfect D21 transport, and imperfect basis selection
can change variance but cannot introduce approximation bias in exact arithmetic.

This distinguishes E132 from a closure estimator and from target-fitted control
variates.

### Efficient evaluation identity

With `a_i=u_i^T x`, `rho_ic=u_i^T u_c`, and
`b_i=sum_c D_corr[i,c] a_c`,

`sum_c D_corr[i,c] H_iic
 = (a_i^2-1)b_i
   - 2 a_i sum_c D_corr[i,c] rho_ic`.

So evaluation requires:

- one input projection onto the fixed first-layer directions;
- low-rank application of the compressed D21 state;
- one final dense map by `W_L`.

No cubic tensor is materialized.

## Computable total-error certificate

The candidate is unbiased conditioned on pilot. Hence its exact-arithmetic vector MSE
is purely evaluation-sampling variance.

For output coordinate `j`, Gaussian Poincare gives

`Var(F_j(X)) <= L_j^2`

for any valid Lipschitz upper bound `L_j`.

E132 uses the target-free computable bound

`L_j =
  [prod_{l=1}^{L-1} sqrt(||W_l||_1 ||W_l||_inf)]
  * ||W_L[:,j]||_2`.

For unit `u_i,u_c`,

`Var(H_iic)
 = 2 + 4 (u_i^T u_c)^2
 <= 6`.

By Minkowski in `L2`,

`sd(g_j)
 <= gamma sqrt(6)
    sum_i |W_L[i,j]| sum_c |D_corr[i,c]|`.

Therefore

`Var(F_j-g_j)
 <= [L_j + sd(g_j)]^2`.

The frozen **total MSE certificate** is

`CERT_MSE
 = M^{-1} mean_j [L_j + sd(g_j)]^2`.

It is:

- target-free;
- computable from weights and pilot state;
- inclusive of all source-age/D21 compression effects because those affect only the
  zero-mean correction coefficient, not bias;
- a mathematical MSE bound, not a post-hoc realized-error fit.

Raw target:

`1.89e-8`.

Certificate gate:

`CERT_MSE <= 1.89e-8` on every frozen small-width network.

If this certificate is too loose, E132 is terminal NO-GO even if realized error or
variance reduction looks favorable.

## Exact small-width falsifier

Synthetic only.

Frozen networks:

- Gaussian input dimension: `2`;
- width: `8`;
- depth: `8` ReLU layers;
- zero bias;
- iid He-normal float64 weights;
- network seeds:
  `132200,132201,132202,132203`.

Depth 8 is intentional: the age>=5 nested path must actually execute.

Candidate random seeds:

`132400,132401,132402,132403`.

For each network, candidate parameters are the production-homologous:

- pilot `P=256`;
- evaluation `M=2048`;
- `r_y=max(1,ceil(n/32))=1`;
- `r_s=max(1,ceil(3n/64))=1`;
- `r_n=max(1,ceil(3n/128))=1`.

The exact verifier independently performs exact 2-D angular piecewise-linear
integration with analytic Gaussian radial factor.

Order is mandatory:

1. generate weights;
2. run E132 candidate and raw same-evaluation-set Monte Carlo baseline;
3. freeze prediction, D21/source diagnostics, certificate and accounting;
4. only then build exact angular final mean;
5. score candidate and baseline.

No exact reference is available to candidate construction.

## Frozen gates

### Integrity

1. all predictions, D21 states, factors and certificate values finite;
2. every deterministic range basis is replay-identical;
3. prediction replay is bitwise identical;
4. source-age transition reaches and exercises the nested age>=5 path;
5. before birth compression, each layer satisfies
   `D_l = D_old,l + B_l` to max abs `<=1e-12`;
6. D21 correction diagonal is exactly zero before Hermite evaluation;
7. candidate source audit finds no exact-reference, dataset, scorer, public,
   holdout/full, target-fit or network I/O dependency;
8. exact reference is materialized only after candidate/baseline execution;
9. no target/public/scorer/holdout/full access.

### Scientific

10. pooled E132 exact-reference MSE is strictly below pooled raw MC baseline MSE;
11. E132 improves raw MC on at least 3 of 4 networks;
12. every frozen network `CERT_MSE <=1.89e-8`;
13. pooled candidate exact-reference MSE `<=1.89e-8`;
14. every-network candidate MSE `<=1.89e-8`.

### Production admission

15. complete frozen production upper FLOPs
    `<=136,758,472,261`;
16. executable small ledger matches the protocol formulas by operation class.

Any failed or unevaluable gate gives:

**E132 TERMINAL NO-GO / CLOSE LAYER-BORN SOURCE-AGE D21 ESTIMATOR.**

A PASS would authorize only a separately frozen production-risk step, never
public/scorer execution.

## Complete production FLOP proof

Hard cap:

`C=136,758,472,261`.

Frozen shape:

- `n=d=1024`;
- `L=16`;
- pilot `P=256`;
- evaluation `M=2048`;
- `r_y=32, r_s=48, r_n=24`.

Every candidate operation class is billed below.

### A. Gaussian RNG/materialization

`32*(P+M)*n
 = 75,497,472`.

### B. Network propagation

Dense+ReLU convention per trajectory per square layer:

`2n^2+2n = 2,099,200`.

Pilot runs 15 layers; evaluation runs 16:

`[P*(L-1)+M*L]*(2n^2+2n)
 = 76,847,513,600`.

### C. Pilot D21 statistics

Per hidden layer:

`2*P*n^2 + 12*P*n`

for centered-square by centered matrix product plus centering/reductions.

Across 15 hidden layers:

`8,100,249,600`.

### D. Source-age transport

Conservative per hidden layer:

`8 n^2 r_y + 8 n^2 r_s + 2 n^2 r_n + 4 n r_s r_n`.

Across 15 layers:

`10,892,083,200`.

This bills two separate young factors, one shared left transport with three age
coefficients, and nested-old right/thin transport.

### E. Birth compression

Fixed range sketch + coefficient projection + QR/sign canonicalization:

per layer

`4 n^2 r_y + 4 n r_y^2 + 8 r_y^3`.

Across 15 layers:

`2,080,112,640`.

### F. Shared age-2..4 merge/rebase

Conservative:

`4 n^2 r_s
 + 4 n (r_s+r_y)^2
 + 8 (r_s+r_y)^3
 + 4 n r_s r_y`

per hidden layer.

Across 15 layers:

`3,568,926,720`.

### G. Nested old-source rebase

Within the shared basis:

`4 n r_s r_n + 4 r_s r_n^2 + 8 r_n^3`

per hidden layer.

Across 15 layers:

`74,096,640`.

### H. Old-state reconstruction for birth residual

Conservative:

`4 n^2 r_y + 2 n^2 r_s + 4 n r_s r_n`

per hidden layer.

Across 15 layers:

`3,593,994,240`.

### I. First-layer direction normalization

`6 n^2 = 6,291,456`.

### J. Direction Gram for Hermite correction

`2 n^3 = 2,147,483,648`.

### K. Evaluation input projection

`2 M n^2 = 4,294,967,296`.

### L. Low-rank D21 application

Maximum live effective right-rank count:

`R_eff = 2 r_y + 3 r_s + r_n = 232`.

Conservative two-sided low-rank apply:

`4 M n R_eff
 = 1,946,157,056`.

### M. Final D21 reconstruction/helpers

Full diagnostic reconstruction:

`2 n^2 R_eff = 486,539,264`.

Rowwise `D_corr o rho` reduction:

`3n^2 = 3,145,728`.

### N. Final Hermite correction dense map

`2 M n^2 + 8 M n
 = 4,311,744,512`.

### O. Certificate norm/reduction work

Conservative:

`16 L n^2 + 8n^2
 = 276,824,064`.

### P. Final reductions

`8 M n = 16,777,216`.

### Q. General helper/accounting reserve

`2,000,000,000`.

### All-in

Sum:

`126,189,396,992 FLOPs`.

Hard-cap slack:

`136,758,472,261 - 126,189,396,992
 = 10,569,075,269 FLOPs`.

Pre-code cost admission:

**PASS**.

No unlisted candidate operation class is permitted. If implementation introduces one,
the verifier must either bill it from the helper reserve with explicit receipt or mark
accounting failure.

## Immutable run discipline

1. this protocol-only commit;
2. only then implementation, exact verifier, tests and workflow;
3. exactly one Actions scientific run;
4. no seed/rank/sample/gate/certificate change after execution;
5. immutable result/receipt commit;
6. no rerun, rescue, public/scorer/holdout/full, canonical mutation, ledger mutation,
   or merge.
