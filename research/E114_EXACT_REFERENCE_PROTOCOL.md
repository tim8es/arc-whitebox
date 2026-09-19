# E114 exact-reference extension — final-observable output-space compression

Tracking key: `ARC-E114-EXACT-REFERENCE-OUTPUT-COMPRESSION-20260919`

Status: **REFERENCE ENGINEERING / NO NEW MECHANISM / ONE FROZEN EXACT RUN AUTHORIZED**.

## Scope

This extension does not change E114's mechanism. The parent E114 result
(`research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`)
already established the exact activation-boundary flux identity for deep,
zero-bias, positively homogeneous ReLU outputs.

The purpose here is only to provide a reusable exact small-width instrument for
a later E114 compression experiment. The instrument must measure, for any
**externally supplied output-space projector** and final scalar observable:

- exact Gaussian final-output mean;
- exact Gaussian final-output covariance;
- exact activation-boundary jump vectors and flux Gram matrix;
- exact compression bias;
- exact compressed/residual covariance and cross-covariance;
- exact mean-square remainder;
- exact observable-specific bias, residual variance and residual MSE;
- exact boundary-flux mean and energy remainder.

The harness does **not** define a deployable projector, rank-selection rule,
weight-derived subspace, learned alignment, or target-fitted correction.

## Exact angular reference

Frozen reference family:

- input Gaussian dimension: `2`;
- hidden/final width: `8`;
- ReLU depth: `4`;
- biases: exactly zero;
- weights: iid He-normal float64;
- frozen seeds: `114200, 114201, 114202, 114203`;
- no Monte Carlo;
- no numerical quadrature;
- no benchmark/public target.

For every layer and every current angular sector, activations on the unit
circle have the exact form

`h(theta) = A [cos(theta), sin(theta)]^T`.

Every preactivation zero inside a sector is solved analytically from
`atan2`, the sector is split at all such roots, and the exact ReLU mask at the
subsector midpoint selects the next affine coefficient matrix.

At the final layer, for each final sector `[a,b]` with coefficient matrix
`A`:

- the angular first moment is integrated exactly from sine/cosine endpoints;
- the angular pair-product matrix is integrated exactly from
  `int qq^T dtheta`;
- Gaussian radial moments are `E[R]=sqrt(pi/2)`, `E[R^2]=2`.

Thus the harness returns exact

`mu = E[F(X)]`

and

`Sigma = Cov(F(X))`

for `X~N(0,I_2)`.

At every final angular partition boundary, the vector derivative jump is
computed from the adjacent affine coefficient matrices. Their sum `s` must
satisfy E114 coordinate-wise:

`mu = E[R]/(2*pi) * s`.

The exact flux Gram is

`C_flux = sum_b j_b j_b^T`.

## Generic compression measurement

The reusable API accepts an externally supplied orthonormal basis
`U in R^(8 x k)` and defines `P=UU^T`, `Q=I-P`.

It returns exactly:

- compressed mean `P mu`;
- compression bias `P mu - mu = -Q mu`;
- compressed covariance `P Sigma P`;
- residual covariance `Q Sigma Q`;
- compressed/residual cross-covariance `P Sigma Q`;
- residual second moment
  `M_R = Q Sigma Q + (Q mu)(Q mu)^T`;
- total mean-square remainder `tr(M_R)=E[||QF(X)||^2]`;
- relative remainder against `E[||F(X)||^2]`;
- flux-mean remainder `Q s`;
- residual flux energy
  `tr(Q C_flux Q)/tr(C_flux)`;
- for every final coordinate observable `c=e_j`:
  exact bias, residual variance and residual MSE.

These are reference quantities only.

## Oracle capacity diagnostic

To make the receipt useful without inventing a candidate mechanism, the frozen
run may additionally report an **oracle-only** capacity diagnostic. For
`k in {1,2,4}`, form `U_oracle(k)` from the leading eigenvectors of the
exact `C_flux`.

This is explicitly unavailable to a deployable estimator and is not a
candidate mechanism. It answers only:

> if the exact boundary-flux output space were compressed optimally in its own
> measured energy geometry, how much exact final-observable bias/covariance/
> remainder would remain?

No GO/NO-GO threshold is attached to the oracle capture numbers.

## Frozen instrument gates

The reference harness passes only if all four networks satisfy:

1. all sector coefficients, moments, covariances, jumps and metrics finite;
2. final angular sectors form a complete ordered partition of `[0,2pi]`;
3. E114 flux mean vs independent sector mean max abs `<=1e-10`;
4. covariance symmetry max abs `<=1e-12`;
5. covariance minimum eigenvalue `>=-1e-10`;
6. identity projector has bias/remainder max abs `<=1e-12`;
7. zero projector residual second moment equals exact final second moment to
   max abs `<=1e-12`;
8. oracle projectors are symmetric/idempotent to max abs `<=1e-12`;
9. rank-1/2/4 oracle residual flux energy and final-output mean-square
   remainder are non-increasing with rank up to `1e-12`;
10. deterministic exact replay max abs `==0`;
11. no benchmark/public/scorer/holdout/full access.

Failure means **REFERENCE INSTRUMENT NO-GO**. It does not falsify E114's
already verified mathematical identity.

Passing means only **E114 EXACT REFERENCE HARNESS VERIFIED**. It does not
authorize production execution or select a compression mechanism.

## Execution

Exactly one workflow run is authorized by adding
`research/E114_EXACT_REFERENCE_RUN_ARM.json` with this tracking key and
`execute_once=true`.

The workflow may run focused unit tests plus the frozen exact reference once,
then upload the JSON/log/arm artifact. No scientific rerun, seed/rank sweep,
public data or target access is authorized.
