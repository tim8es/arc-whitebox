# E134 protocol — source-age K=3 direct ReLU-mean closure

Idempotency key: `ARC-E134-SOURCE-K3-DIRECT-CLOSURE-20260920`

Status at freeze: **PROTOCOL ONLY / ONE EXACT-SMALL SCIENTIFIC RUN AUTHORIZED AFTER CODE**.

Branch:
`research/e134-source-k3-direct-closure-20260920`.

Direct parent:
`research/bootstrap@7a0034088ebbffbd74b441e1797c272e9d33cbff`.

## Non-rescue boundary

E132 is closed. E134 does not change, tune, rerun or reinterpret its Hermite
control-variate mechanism.

E134 has no zero-mean post-hoc correction. It never evaluates

`sample output - fitted/source correction`.

Instead it is a **direct K=3 distributional estimator**: layer-born
non-Gaussian third-cumulant sources are transported through the network and the
final ReLU mean is materialized directly from the resulting mean/variance/K3
state.

No benchmark target, exact final mean, scorer result, public/public-mini,
holdout/full value or post-result coefficient enters the estimator.

## Full K=3 source object

A live symmetric third-cumulant source is represented as

`K_s = C_s x_1 Q_s x_2 Q_s x_3 Q_s`,

where
- `Q_s in R^(n x r)` has orthonormal columns;
- `C_s in R^(r x r x r)` is a symmetric cubic core.

The low-order slices are

`D3_s[i] = K_s[i,i,i]`

and

`D21_s[i,c] = K_s[i,i,c]`.

Thus D3 and D21 are not transported independently or approximately. They are
both slices of the same transported full low-order K=3 source tensor.

For a dense linear layer `W`:

`A = W^T Q_s = Q'_s R_s`

by deterministic thin QR, and

`C'_s[u,v,w] =
 sum_{a,b,c} C_s[a,b,c] R_s[u,a] R_s[v,b] R_s[w,c]`.

This exactly transports the represented full third-cumulant tensor through the
linear layer, including every D3/D21 term induced by that represented source.

ReLU itself creates a new source; old sources are not re-Gaussianized.

## Layer-born source innovation

Use `M=4096` Gaussian trajectories. At hidden layer `l`, let

`X_l = H_l - rowmean(H_l)`.

A deterministic range basis `Q_b` of rank `r_y` is constructed from
`X_l^T Omega_l`, where `Omega_l` is a frozen Rademacher sketch whose seed
depends only on E134 and layer index.

The exact empirical K3 projected into `Q_b` is computed without an `n^3`
tensor:

`U = X_l Q_b`,
`C_emp = M^-1 sum_p U_p x U_p x U_p`.

Project every transported old source into the same basis and sum its projected
cores:

`C_old_proj = Proj_{Q_b}(sum_s K_s)`.

The layer-born source is

`C_birth = C_emp - C_old_proj`.

Adding `(Q_b,C_birth)` therefore repairs the current K3 state exactly inside
the frozen birth subspace. Components outside that subspace remain explicit
source-compression residual, not hidden in a post-hoc correction.

## Frozen source-age shared/nested basis

Ranks are

`r_y(n)=max(1,ceil(n/32))`,
`r_s(n)=max(1,ceil(3n/64))`,
`r_n(n)=max(1,ceil(3n/128))`.

At production width 1024:

- young rank `r_y=32`;
- shared age-2..4 rank `r_s=48`;
- nested age>=5 rank `r_n=24`.

At the frozen exact-small width 32:

- `r_y=1`;
- `r_s=2`;
- `r_n=1`.

Age policy:

- ages 0 and 1 retain separate bases/cores;
- ages 2,3,4 are rebased into one shared basis `Q_s`;
- age >=5 sources are aggregated and compressed into
  `Q_n=Q_s R_n`, a nested sub-basis of the same shared basis.

The shared basis is the deterministic top-`r_s` left singular basis of the
weighted concatenation of transported source bases, with each source basis
weighted by `max(||C||_F,2^-100)^(1/3)`.

The old nested sub-basis is obtained from the top-`r_n` eigenspace of the
mode-1 Gram of the aggregate old cubic core expressed in `Q_s`.

Signs are canonicalized by making the largest-magnitude entry of every basis
column non-negative, lowest index breaking ties.

No rank, age threshold or basis rule may change after the frozen run.

## Direct final ReLU estimator

The same `M=4096` trajectories are propagated through hidden layers
`1..L-1`. At the final layer compute preactivations

`Z = H_{L-1} W_L`

but do not use the sample ReLU mean in the candidate.

For output coordinate `j`, compute sample preactivation mean/variance

`mu_j = mean Z_j`,
`sigma_j^2 = mean (Z_j-mu_j)^2`.

Transport the complete live K3 source state through `W_L` and take its
diagonal third cumulant

`kappa3_j = K_final[j,j,j]`.

For `sigma_j>2^-40`, define `a_j=mu_j/sigma_j` and use the first
third-order Gram-Charlier/Edgeworth ReLU expectation

`m_j =
 sigma_j phi(a_j) + mu_j Phi(a_j)
 - kappa3_j mu_j phi(a_j)/(6 sigma_j^3)`.

For degenerate `sigma_j<=2^-40`, set

`m_j=max(mu_j,0)`.

This is the E134 estimate. It is a direct approximate expectation, not an
unbiased control variate.

The same-node raw Monte Carlo comparator is

`b_j=M^-1 sum_p ReLU(Z[p,j])`.

No candidate parameter depends on `b` or the exact reference.

## Target-free source-residual certificate

The certificate is deliberately for **source compression residual inside the
K=3 closure**, not for higher-cumulant truncation or finite-sample uncertainty.

On the exact-small verifier only, after the candidate state is frozen, form the
empirical penultimate third cumulant

`K_emp = M^-1 sum_p X_p x X_p x X_p`

and materialize the candidate source tensor `K_src`.

Let

`E = K_emp-K_src`.

For final column `w_j`,

`|delta kappa3_j|
 = |<E, w_j x w_j x w_j>|
 <= ||E||_F ||w_j||_2^3`.

The final K3 Edgeworth term is affine in `kappa3_j`; therefore with

`c_j =
 |mu_j phi(mu_j/sigma_j)|/(6 sigma_j^3)`

for nondegenerate `sigma_j` and zero otherwise,

`B_j = c_j ||E||_F ||w_j||_2^3`

rigorously bounds the difference between:

1. E134's compressed-source K3 closure mean; and
2. the same K3 closure using the full empirical penultimate K3 tensor.

Define

`CERT_RESID_MSE = mean_j B_j^2`.

The verifier also computes that actual target-free closure difference and must
confirm it is contained coordinatewise by `B_j`.

No exact network output mean enters this certificate.

Frozen certificate gate:

`CERT_RESID_MSE <= 1.89e-8`

on every exact-small network.

Passing this certificate does **not** certify Edgeworth truncation; the
independent exact-small MSE gate below tests total estimator accuracy.

## Frozen exact-small falsifier

Synthetic only:

- Gaussian input dimension: `2`;
- width: `32`;
- ReLU depth: `8`;
- zero bias;
- iid He-normal float64 weights;
- network seeds:
  `134200,134201,134202,134203`;
- candidate Gaussian seeds:
  `134400,134401,134402,134403`;
- trajectories: `M=4096`;
- ranks: `r_y=1,r_s=2,r_n=1`.

Depth 8 is required so the age>=5 nested source path is exercised.

The exact reference is independent analytic 2-D angular piecewise-linear
integration with the exact Gaussian radial factor. It is materialized only
after candidate estimate, baseline estimate, source state and certificate have
all been frozen.

## Frozen integrity gates

1. all candidate/baseline/source/core/certificate values finite;
2. deterministic replay is bitwise exact for candidate prediction and exact for
   the source ledger;
3. age>=5 nested path is exercised on every network;
4. every represented source core remains symmetric to max abs `<=1e-11`;
5. source D3 and D21 extracted from materialized K3 agree with direct slice
   extraction to max abs `<=1e-12`;
6. layer-born projected-core identity
   `Proj_Qbirth(K_old+K_birth)=Proj_Qbirth(K_emp)`
   holds to max abs `<=1e-11`;
7. target-free certificate contains the actual compressed-vs-full K3 closure
   mean difference coordinatewise to `1e-12`;
8. candidate source audit contains no exact-reference, target, dataset, scorer,
   public, holdout/full or network-I/O dependency;
9. exact reference is constructed only after candidate/baseline/certificate;
10. no target/public/scorer/holdout/full access.

Failure => terminal integrity NO-GO, no rerun.

## Frozen scientific gates

All must pass:

11. pooled E134 exact-reference MSE is **strictly below** pooled same-node raw
    Monte Carlo MSE;
12. E134 improves exact-reference MSE on at least `3/4` networks;
13. pooled candidate/baseline MSE ratio `<=0.95`;
14. `CERT_RESID_MSE <=1.89e-8` on every network.

The raw `1.89e-8` target is also reported diagnostically for the actual
candidate MSE, but no candidate coefficient, rank or sample count is selected
from that result.

If gate 11 fails — even if any other diagnostic looks favorable:

**E134 TERMINAL NO-GO / CLOSE SOURCE-K3 DIRECT-CLOSURE LANE.**

No Gaussian/Hermite correction rescue, no rank/sample/seed change and no
post-result fitting.

If all integrity/scientific/production gates pass:

**E134 LOCAL SCIENTIFIC GO — SOURCE-AGE K3 DIRECT CLOSURE.**

This would still not authorize public/scorer execution.

## Frozen production FLOP proof

Production shape:

- `n=d=1024`;
- depth `L=16`;
- trajectories `M=4096`;
- `r_y=32,r_s=48,r_n=24`;
- budget `B=2^41=2199023255552`;
- utilization cap `0.13`.

Conservative operation classes:

1. Gaussian RNG/materialization:
   `32 M n = 134,217,728`.
2. Full dense preactivation/ReLU propagation upper:
   `M L (2n^2+2n) = 137,573,171,200`.
3. Hidden centering/moment reductions:
   `(L-1) 8 M n = 503,316,480`.
4. Birth range sketch, projection, QR:
   `(L-1)[4Mnr_y+4nr_y^2+8r_y^3]
    = 8,119,910,400`.
5. Birth cubic-core accumulation:
   `(L-1) 8 M r_y^3 = 16,106,127,360`.
6. Exact represented-source basis transport:
   `(L-1)2n^2(2r_y+r_s+r_n)
    = 4,278,190,080`.
7. Cubic-core basis transforms:
   `(L-1)8(2r_y^4+r_s^4+r_n^4)
    = 928,481,280`.
8. Shared/nested source-age rebase:
   `(L-1)[4n(2r_y+3r_s+r_n)^2
           +16(r_s+r_y)^4+16r_n^4]
    = 13,216,972,800`.
9. Final K3 diagonal contraction/materialization:
   `8n(2r_y^3+3r_s^3+r_n^3)
    = 3,368,026,112`.
10. Final mean/variance reductions:
    `8Mn = 33,554,432`.
11. Edgeworth/ReLU scalar helpers:
    `64n = 65,536`.
12. General source bookkeeping/certificate/accounting reserve:
    `5,000,000,000`.

All-in frozen upper bound:

`189,262,033,408 FLOPs`.

Utilization:

`189262033408 / 2^41
 = 0.08606640831567347 < 0.13`.

Cap FLOPs:

`0.13*2^41 = 285,873,023,221.76`.

Frozen slack:

`96,610,989,813.76 FLOPs`.

The executable must independently recompute every component and exact sum.
Any new unbilled candidate operation class makes the production gate fail.

## Run discipline

1. protocol-only commit;
2. implementation + exact verifier + focused tests;
3. workflow created last;
4. exactly one Actions scientific run;
5. immutable receipt with run/job/artifact/digest;
6. no rerun, rescue, tuning, sweep, benchmark/public/scorer/holdout/full,
   canonical mutation, ledger mutation or merge.
