# E114 output-specific Schur-complement final-mean compression protocol

Idempotency key: `ARC-E114-OUTPUT-SCHUR-FINALMEAN-20260919`

Status: **PREREGISTERED / EXACT SMALL-WIDTH FALSIFIER ONLY**.

## Identity firewall

This branch is a collision-isolated successor:

`research/e114-output-schur-finalmean-20260919`

Parent:

`research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`.

The parent E114 identity established an exact activation-boundary-flux representation. This branch does **not** overwrite or merge that receipt. It tests the user-requested separate hypothesis: output-specific low-dimensional compression of only the final mean observable.

Excluded/reopened lanes:

- no E112 factorized cumulant closure;
- no E112 full-mask/treewidth message passing;
- no E113 top-k/top-gate conditioning;
- no E110 deep-line Rao-Blackwell region enumeration;
- no E111 Gaussian-ReLU plug-in;
- no sampler/control-variate mechanism;
- no public/public-mini/scorer/holdout/full targets.

## Observable and compression point

For a zero-bias depth-4 width-8 ReLU network, write the penultimate preactivation vector

`z = W_3 h_2 in R^8`

and the final output vector

`y = ReLU(W_4 ReLU(z)) in R^8`.

Only `E[y]` is the scientific observable. No attempt is made to close the full hidden joint law.

Let

`M = E[z z^T]`

be the exact uncentered second-moment matrix of the penultimate preactivation.

For one rank-r linear observation matrix `U in R^(8xr)`, define the minimum-second-moment linear reconstruction

`zhat = M U (U^T M U)^+ U^T z`.

Its residual second moment is the Schur complement

`M_res = E[(z-zhat)(z-zhat)^T]
       = M - M U (U^T M U)^+ U^T M`.

The construction is homogeneous: `zhat` is linear in `z`, so no Gaussian plug-in or affine intercept is introduced.

## Output-specific optimal rank-r objective

For final row `w_j^T` define

`D_j = diag(|w_j|)`.

By two applications of ReLU's 1-Lipschitz property and weighted Cauchy-Schwarz,

`|y_j - yhat_j|
 <= sum_i |w_ji| |z_i-zhat_i|`

and therefore

`|E[y_j]-E[yhat_j]|^2
 <= ||w_j||_1 * tr(D_j M_res)`.

Averaging final coordinates gives the exact pooled bias-MSE certificate

`(1/n) sum_j |E[y_j]-E[yhat_j]|^2
 <= tr(D_pool M_res)`

where

`D_pool = diag(d)`,
`d_i = (1/n) sum_j ||w_j||_1 |w_ji|`.

This objective depends only on the final observable weights, not on the full hidden law.

Let `M^(1/2)` be the PSD square root and

`B = M^(1/2) D_pool M^(1/2)`.

For rank `r`, the minimum possible pooled certificate over all linear observations is the sum of the eigenvalues of `B` omitted by its top-r eigenspace. Equivalently, if `V_r` contains the top-r eigenvectors and `U=M^(-1/2)V_r` on the support of `M`, the corresponding Schur complement attains

`R_bound(r) = tr(D_pool M_res) = sum_{k>r} lambda_k(B)`.

This is the frozen output-specific low-dimensional compression mechanism.

## Exact angular reference

Frozen small-width family:

- Gaussian input dimension: 2;
- width: 8;
- depth: 4;
- zero bias;
- He Gaussian float64 weights;
- PCG64 seeds: `114201,114202,114203,114204`;
- frozen rank: `r=2`.

The exact reference recursively partitions the full unit circle at every preactivation zero. On each fixed-mask sector every hidden state is exactly linear in `q(theta)=(cos theta,sin theta)`.

No numerical quadrature is used.

For each seed the executable must compute exactly, up to floating-point analytic integration:

1. the angular sector partition through layer 3;
2. exact `M=E[zz^T]` using analytic sector integrals and `E[R^2]=2`;
3. `D_pool`, `B`, its eigenvalues and the rank-2 Schur certificate;
4. the exact original final mean vector;
5. the exact compressed-proxy final mean vector obtained by replacing `z` with the homogeneous linear reconstruction `zhat` and analytically refining any new proxy ReLU boundaries;
6. actual pooled final-mean bias MSE;
7. proof check `actual_bias_mse <= R_bound + 1e-12`;
8. deterministic replay.

## Decisive gate

Competition target scale:

`T = 1.89e-8`.

PASS requires **for every frozen seed**:

- finite exact/reference quantities;
- Schur matrix PSD to numerical tolerance;
- `actual_bias_mse <= R_bound + 1e-12`;
- deterministic replay max abs `==0`;
- `R_bound <= T`.

The pooled mean of the four `R_bound` values must also be `<=T`.

If any target-scale remainder gate fails:

**TERMINAL NO-GO / DROP THIS E114 OUTPUT-SCHUR VARIANT.**

No change to rank, seeds, width/depth, compression point, weighting, pseudoinverse tolerance, or proxy definition; no rescue/rerun/sweep.

## Production cost admission

This gate is pre-code and only establishes that the algebra would fit the budget if the small exact remainder survived.

Frozen production shape:

- width 1024;
- depth 16;
- trajectories 4096;
- rank 64;
- base E104 complete measured cost reference: `149,114,620,592` FLOPs;
- budget `B=2^41`;
- utilization cap `0.13`.

Conservative additional allowance:

- exact sample second moment `Z^T Z`: `8.60B`;
- symmetric PSD decomposition / weighted rank-64 factor construction: `15.0B`;
- low-rank score + reconstruction for all trajectories: `1.20B`;
- one replacement final-layer dense matmul + ReLU/reduction: `8.70B`;
- output-weight aggregation, Schur certificate, bookkeeping margin: `2.0B`.

Frozen all-in upper:

`184,614,620,592` FLOPs.

Utilization:

`184,614,620,592 / 2^41 = 0.0839527... < 0.13`.

**PRE-CODE COST ADMISSION PASS.**

No production execution is authorized by this protocol. A small-width PASS would only define the next production gate.

## Scope

- exact small-width synthetic only;
- no Monte Carlo scientific truth;
- no numerical quadrature;
- no benchmark/public target;
- no tuning/sweep;
- no canonical or ledger mutation.
