# R219 — one-factor Gaussian-copula dependence carrier

Date: 2026-09-22  
Idempotency: `ARC-R219-1FGC8-20260922`  
Branch: `research/r219-dependence-carrier-frontier-20260922`  
Central queue start: revision 74, run id `R219-dependence-carrier-frontier-20260922`.

## 0. One family only

R219 screens exactly one dependence-aware estimator family:

**1FGC-8 — one-factor Gaussian-copula conditional-independence closure with eight fixed latent-factor quadrature nodes.**

The represented dependence is not coordinate-wise marginal state. It is a single common latent Gaussian factor:

[
Z_i=lambda_i F+sqrt{1-lambda_i^2},epsilon_i,
qquad
F,epsilon_istackrel{iid}{sim}N(0,1),
]

with scalar marginals attached monotonically through the Gaussian copula.

Conditional on `F`, coordinates are independent. Production propagation uses exactly
eight fixed Gauss–Hermite factor nodes; no factor-count, node-count, rank, seed, or
structure sweep is permitted.

## 1. Immutable-history novelty audit

R219 is not a rescue or repetition of R215.

Relevant closed lanes inspected before freeze:

- R215 FMCF: coordinate-wise marginal characteristic functions only; terminal because
  dependence was absent.
- E039: fixed two-component half-space Gaussian location mixture, two equal components,
  one shared covariance. R219 is not a finite frozen half-space split and does not inherit
  E039 code or measurements.
- E124: Chow–Liu tree of pairwise gate/amplitude statistics; pair-tree closure reduced
  error but remained ~119,463x target.
- E127: sparse higher-order Möbius hypergraph closure; terminal because certified joint
  clusters were not sparse enough under the cost cap.

Repository branch/commit/code search found no prior
`factor copula`, `one-factor copula`, `common factor copula`, or
`copula factor` implementation or experiment.

## 2. Primary literature

Primary family source:

Pavel Krupskii and Harry Joe,
**Factor copula models for multivariate data**,
Journal of Multivariate Analysis 120 (2013), 85–101,
DOI `10.1016/j.jmva.2013.05.001`.

The paper defines conditional-independence copula models with one or more latent factors
and emphasizes the parsimonious O(d) dependence parameterization. A multivariate normal
model with factor-structured correlation is a special case.

Dependence/marginal separation source:

André Nataf,
**Détermination des distributions de probabilités dont les marges sont données**,
C. R. Acad. Sci. Paris 255 (1962), 42–43.

R219 uses only the normal-copula/factor representation. It does not use benchmark targets
or fitted post-result dependence.

## 3. Why this is a substantive continuation of R215

R215's 2-D witness used:

- correlated: ((X,Y)=(S,S));
- anti-correlated: ((X,Y)=(S,-S)).

A one-factor Gaussian copula can represent those limiting structures with
((lambda_X,lambda_Y)=(1,1)) and ((1,-1)), respectively.

Therefore R219 does not merely add more marginal frequencies. It adds a real shared
dependence variable and removes the exact R215 two-coordinate indistinguishability.

The R219 falsifier instead targets irreducible higher-order dependence.

## 4. Frozen exact-small witness

Let (X=(X_1,X_2,X_3,X_4)in{-1,+1}^4).

### Law P — even parity

Uniformly distribute mass over the eight states satisfying

[
X_1X_2X_3X_4=+1.
]

### Law I — independent

Four independent Rademacher coordinates, uniform over all 16 sign states.

For both laws:

1. every marginal is Rademacher;
2. every pair is exactly independent;
3. every pairwise Pearson/rank/sign dependence is zero.

For the one-factor Gaussian copula with Rademacher sign marginals,

[
operatorname{Corr}(X_i,X_j)
=
rac{2}{pi}arcsin(lambda_ilambda_j).
]

Thus pairwise independence forces

[
lambda_ilambda_j=0quadorall i
e j.
]

At most one loading can be nonzero. The resulting one-factor model therefore reduces to
joint independence for the four observed coordinates. Hence the complete 1FGC state
selected from these marginals/pairwise dependencies is identical for Law P and Law I.

Now freeze the dense observable

[
U=X_1+X_2+X_3+X_4.
]

For Law P, only the all-plus state contributes positively:

[
E[operatorname{ReLU}(U)]
=
rac18cdot 4
=
rac12.
]

For Law I,

[
P(U=4,2,0,-2,-4)=rac1{16}(1,4,6,4,1),
]

so

[
E[operatorname{ReLU}(U)]
=
rac{4+4cdot2}{16}
=
rac34.
]

The exact true gap is therefore

[
Delta=rac14.
]

Any deterministic estimator that emits the same 1FGC state for both laws has worst-case
absolute mean error at least

[
Delta/2=rac18.
]

Moreover the specific Gaussian-copula state with zero pairwise dependence predicts the
independent law, so its error on Law P is exactly

[
rac34-rac12=rac14.
]

Frozen continuation gate:

[
	ext{worst-case absolute ReLU-mean error}le 10^{-6}.
]

No tolerance is used for the rational probability identities.

## 5. Conservative production FLOP boundary

Production shape:

- width `n=1024`;
- depth `L=16`;
- latent-factor quadrature nodes `Q=8`.

A concrete conditional-moment 1FGC propagation can, per factor node and layer:

1. evaluate scalar conditional activation moments;
2. propagate conditional means with one dense matrix-vector family;
3. propagate conditional independent variances with squared-weight matrix-vector family;
4. integrate factor-conditioned means/variances;
5. reconstruct the next one-factor conditional state.

### Mandatory arithmetic lower bound

The two dense conditional transforms cost at least

[
4Qn^2L
=
536,870,912
]

FLOPs, or

[
0.000244140625B.
]

### Conservative all-in estimator upper envelope

Charge, per layer:

[
8Qn^2+128Qn
]

for doubled dense conditional work, scalar moment transforms, factor integration and
dependence-state reconstruction.

Across 16 layers:

[
1,090,519,040.
]

Add a deliberately large `4,000,000,000` FLOP integration/materialization/certificate
reserve:

[
C_{m upper}
=
5,090,519,040.
]

With

[
B=2^{41}=2,199,023,255,552,
]

[
C_{m upper}/B
=
0.0023149000480771065.
]

This is well below the project admission cap `0.135B`.

Therefore the exact-small synthetic falsifier is **cost-feasible and authorized**.

This cost envelope applies to the frozen one-factor conditional-moment implementation.
It is not a cost claim for arbitrary multi-factor/vine/copula estimators.

## 6. Sole synthetic falsifier

One target-free executable must:

1. enumerate Law P and Law I exactly with rational weights;
2. verify identical univariate marginals;
3. verify all six pairwise 2x2 laws are identical and independent;
4. verify all pairwise correlations are exactly zero;
5. verify the one-factor loading constraint implies at most one nonzero loading;
6. verify the family therefore selects the independent four-coordinate joint law;
7. compute exact ReLU means `1/2` and `3/4`;
8. compute exact family error on parity `1/4`;
9. verify same-state worst-case lower bound `1/8`;
10. recompute the frozen production lower/upper FLOP arithmetic;
11. replay bitwise-identically.

### Gate

A scientific GO requires simultaneously:

- family distinguishes Law P from Law I from its carried state;
- worst-case absolute ReLU-mean error <= `1e-6`;
- production upper <= `0.135B`;
- deterministic replay.

If the parity law maps to the independent 1FGC state as derived above, R219 is terminal:

`R219_TERMINAL_NO_GO_ONE_FACTOR_COPULA_NONCLOSURE`.

No rescue by changing factor count, copula family, quadrature nodes, marginal grid,
loadings, or witness is allowed under R219. Multi-factor, vine, or explicit higher-order
copula state is a different experiment family.

## 7. Safety

Forbidden:

- public/public-mini benchmark;
- paid compute;
- holdout;
- scorer;
- submission;
- broad sweep;
- target fitting;
- R215 rerun/rescue;
- canonical/leaderboard mutation.

Exactly one synthetic Actions run is authorized after this protocol commit.
