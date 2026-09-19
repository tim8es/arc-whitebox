# E113 protocol — annealed radial sufficiency vs quenched dense-ReLU obstruction

Idempotency key: `ARC-E113-ANNEALED-RADIAL-SUFFICIENCY-20260919`

Status at freeze: **ONE MATHEMATICAL/SMALL-EXACT FALSIFIER ONLY**.

## Provenance and non-duplication

- Branch: `research/e113-annealed-radial-sufficiency-20260919`.
- Parent: terminal E111 head `9d0dcc429fc4b62a6607ea28c97fbb44327dbaf2`.
- E111 already closed exact first-two-moment Gaussian-ReLU plug-in closure.
- Concurrent E112 studies explicit binary activation-mask message passing/treewidth.
- E113 does not use Gaussian moment closure, mask enumeration, Haar/QMC, Stein/JVP controls,
  fitted targets, latent mixtures, or line breakpoint Rao-Blackwellization.
- No public/public-mini, benchmark targets, scorer, holdout/full, tuning, sweep,
  rescue, canonical/ledger mutation, or merge.

## Question

Does the actual dense random zero-bias ReLU MLP law admit an **exact low-dimensional
state** that can be propagated through later layers?

E113 separates two probability notions that are easy to conflate:

1. **annealed**: average over a fresh iid Gaussian weight matrix at the next layer;
2. **quenched**: condition on the realized white-box weight matrix and average only
   over the input/random-direction law.

The competition estimator is quenched: the network weights are known and fixed.

## Positive closure: exact annealed scalar radial state

Let `h in R^d` be fixed and let a fresh next-layer matrix have iid entries
`W_ji ~ N(0,2/d)`. For output width `m`,

`z = W h | h ~ N(0, (2||h||^2/d) I_m)`.

Therefore the full one-step activation law

`ReLU(W h) | h`

depends on `h` **only through the scalar radius** `r=||h||`.

Moreover

`R_next = ||ReLU(W h)|| = r * sqrt(2/d) * chi_K`,

where `K~Binomial(m,1/2)` and, conditional on `K=k`, `chi_K` is a chi
random variable with `k` degrees of freedom (with `chi_0=0`).

Hence radius is an exact one-dimensional Markov sufficient state for all future
activations **when every future dense Gaussian weight matrix is also averaged over**.

The exact expected radial multiplier is

`a(d,m)=sqrt(2/d) * sum_{k=1}^m C(m,k)2^{-m} E[chi_k]`,

`E[chi_k]=sqrt(2) Gamma((k+1)/2)/Gamma(k/2)`.

This is a genuine positive closure, not an approximation.

## Quenched obstruction theorem

Fix one realized square dense layer `W in R^(n x n)` with full rank and use
column convention `y(h)=ReLU(W^T h)`.

Suppose an exact differentiable low-dimensional state exists:

`T:R^n -> R^k`, `G:R^k -> R^n`, with `y=G o T`.

Because `W` is invertible, `h0=(W^T)^(-1) 1` exists. In an open
neighborhood of `h0`, every preactivation is positive, so

`y(h)=W^T h`

and its Jacobian has rank `n`.

But by the chain rule,

`rank D(G o T) <= rank DT <= k`.

Therefore **k>=n**. No exact C1 state with dimension `k<n` can reproduce even
one realized full-rank ReLU layer on an open set.

For iid continuous Gaussian square weights, full rank holds with probability one.
Thus the obstruction is almost sure under the actual dense random MLP law once
weights are conditioned on.

A simpler constructive counterexample for the radius statistic is `h` and
`-h`: they have identical radius, while for generic `W`,
`ReLU(W^T h) != ReLU(-W^T h)`.

Scope of theorem: exact C1 state sufficient for the full next activation vector.
It does not rule out discontinuous encodings, exact statistics for one special
scalar observable, approximate compression, or annealed weight averaging.

## One new class after the obstruction

The sole successor class tested under E113 is the **annealed radial plug-in**:
use the exact scalar radial closure above as a deterministic surrogate for the
quenched fixed-network final mean.

To isolate later-layer behavior, the falsifier reports plug-ins that preserve the
realized network exactly through layer `s=1,2,3`, then anneal only the remaining
future Gaussian layers. In particular, `s=3` keeps the first three realized
layers exact and anneals only the final dense layer.

For a state radius `R_s` and `r=L-s` remaining layers, the annealed predicted
final coordinate mean is

`E[R_s] * a(n,n)^(r-1) / sqrt(pi*n)`.

`E[R_s]` is measured from the exact fixed-network angular law using deterministic
high-order Gauss-Legendre integration inside the exact ReLU angular sectors.
No target labels are used.

## Frozen small exact falsifier

- latent Gaussian input dimension: `2`;
- hidden/output width: `8`;
- depth: `4`;
- zero bias;
- iid He-Gaussian realized weights;
- PCG64 weight seed: `113113`;
- float64;
- exact fixed-network final means: piecewise angular integration with analytic
  Rayleigh radial moment `E[R]=sqrt(pi/2)`;
- radius expectations at layers 1..3: 64-point Gauss-Legendre integration per
  exact angular sector, repeated at 96 points only as an independent convergence
  check;
- raw target scale: `1.89e-8`.

No production-shaped run is authorized by this protocol.

## Frozen gates

Mathematical/integrity gates:

1. every realized square later-layer matrix has rank 8;
2. active-cone certificate `W^T h0=1` has max residual <= `1e-10`;
3. local active-cone Jacobian rank is 8, certifying the `k>=n` obstruction;
4. a same-radius `h,-h` pair gives unequal realized ReLU outputs;
5. exact angular final mean is finite;
6. 64-vs-96 Gauss-Legendre layer-radius expectation max relative difference <= `1e-10`;
7. deterministic replay is exact;
8. no external target/public/scorer/holdout/full access.

New-class scientific gate:

9. for each start layer `s=1,2,3`, annealed-radial plug-in final-mean MSE
   versus the exact quenched final mean must be <= `1.89e-8`;
10. especially the strongest late test `s=3` (only final layer annealed) must
    pass the same threshold.

All gates are required for E113 GO. Any failed/unevaluable gate =>
**TERMINAL NO-GO / DROP E113**. No alternate seed, width/depth, quadrature order,
layer start, statistic augmentation, fit, correction, rerun, or rescue.
