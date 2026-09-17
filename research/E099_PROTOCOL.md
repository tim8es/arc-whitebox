# E099 protocol — constant-weight shared-latent two-Gaussian closure

Idempotency key: ARC-E099-SHARED-LATENT-2G-20260918

Status: PREREGISTERED / PRE-EVIDENCE

## Provenance and firewall

- Branch: research/e099-shared-latent-2g-closure-20260918.
- Direct canonical parent: research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83.
- E092-E098 are occupied and not inherited or reopened.
- No public, public-mini, scorer, benchmark holdout/full labels, tuning, sweep, canonical mutation, or ledger mutation.
- This lane is an accuracy-architecture falsifier, not a source-axis compression, checkpoint replay, Strassen, residual sampling, or calibration lane.

## Chassis

Represent each hidden-layer law by a two-component Gaussian mixture with one shared binary latent S:

    X = mu + d S + eps,
    eps ~ N(0, Sigma0),   eps independent of S.

Freeze the component weight at

    pi = P(S = a_plus) = 0.1,

with standardized two-point latent values

    a_plus  = sqrt((1-pi)/pi),
    a_minus = -sqrt(pi/(1-pi)),

so E[S]=0 and Var(S)=1. The same pi is width-independent and frozen before evidence.

The mixture therefore has

    Cov(X) = Sigma0 + d d^T,
    kappa3(X_i) = m3(S) d_i^3,

where m3(S)=E[S^3].

This is a deliberately compact skew-aware replacement architecture: linear maps preserve the two-component form exactly, while nonlinear ReLU moments would be recomputed component-wise. No K3 source history is carried.

## Budget-first path

A full implementation with K=2 components is intended to remain O(K L n^3) for dense covariance transforms plus O(K L n^2) nonlinear moment work. Freeze an intentionally conservative dense algebra ceiling of

    12 * L * n^3

scalar FLOPs before special-function accounting.

At n=1024, L=16 this is 206,158,430,208 FLOPs, utilization 0.09375 against B=2^41, leaving 90,709,708,991.52 FLOPs to the 0.135 limit for special functions, reconstruction, and instrumentation. This is only a feasibility ceiling, not a measured scorer claim.

## First structural falsifier

Use the exact first-layer law for independent coordinates

    Z_i ~ iid N(0,1),
    H_i = ReLU(Z_i).

The exact scalar moments are analytic:

    mean = 1/sqrt(2*pi),
    second raw moment = 1/2,
    third raw moment = sqrt(2/pi),

hence variance v and central third cumulant kappa3 are exact.

For a width-n iid ReLU vector, target covariance is v I and each marginal third cumulant is kappa3. Exact marginal skew matching in the frozen two-component family forces

    d_i = cbrt(kappa3 / m3(S))

for every i. Exact covariance matching then requires

    Sigma0 = v I - d d^T

to be positive semidefinite.

Because d is constant across coordinates, the minimum eigenvalue is exactly

    lambda_min(Sigma0) = v - n d^2.

This is a representation-feasibility identity, not a numerical approximation.

## Frozen kill gates

Run exactly one local structural falsifier at official width n=1024.

GO requires all of:

- finite=true;
- exact moment identities agree with direct analytic formulas to <=1e-15;
- lambda_min(Sigma0) >= -1e-12;
- covariance reconstruction max_abs <=1e-12;
- third-cumulant reconstruction max_abs <=1e-12;
- deterministic repeat max_abs == 0.0;
- conservative dense utilization ceiling <=0.135.

If the PSD gate fails, E099 is TERMINAL ANALYTIC/STRUCTURAL NO-GO. No changing pi, adding components, width-dependent mixture weights, rescue, rerun tuning, public data, or second falsifier under E099. Such changes require a new experiment ID.

## Receipt requirements

Record protocol commit, implementation/workflow commit, run/job/artifact/digest, exact v, kappa3, m3(S), d, lambda_min, covariance and kappa3 reconstruction errors, budget ceiling/utilization, deterministic repeat result, and terminal decision.
