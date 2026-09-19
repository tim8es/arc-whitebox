# E109 result — later-layer nonlinear centering structural gate

Idempotency key: `ARC-E109-LATERLAYER-NONLINEAR-CENTERING-GATE-20260919`

Decision: **STRUCTURAL GATE ESTABLISHED / MOMENT-2 AND ANTISYMMETRIC-CENTERING NO-GO**

## Provenance

- Branch: `research/e109-laterlayer-nonlinear-centering-gate-20260919`
- Direct parent: terminal E108 branch
  `research/e108-firstlayer-exactmean-transport-cv-20260919`
- Protocol commit:
  `54a4069790e2d291512871af4ad2783696f7d35b`
- Executable commit:
  `11c51449fddfb6e2e354cb2b14b3da5e707e1b19`
- Workflow commit:
  `6bdd443c3dbd1577055adb039090893cdd1cc85a`
- Run/job:
  `35453144708 / 105923684784`
- Workflow conclusion: `success`
- Artifact:
  `e109-laterlayer-nonlinear-centering`
- Artifact ID:
  `10587143381`
- Artifact ZIP SHA256:
  `bf38c7c8fb2efcbb044d1925dcdcc1693f424c351b877087fb11fadc741bd76d`
- Artifact size:
  `940` bytes

No targets, public/public-mini, scorer, holdout/full, production estimator run,
tuning, E104 rerun, canonical mutation, or ledger mutation.

## Exact later-layer identity

For any scalar preactivation,

[
operatorname{ReLU}(U)=rac{U+|U|}{2},
]

hence

[
E[operatorname{ReLU}(U)]
=
rac12 E[U]+rac12 E|U|.
]

E108 could center its first-layer statistic exactly because the corresponding
absolute first moment is available analytically from spherical/Gaussian
symmetry. A generic later-layer preactivation does not inherit that closure.

## Exact moment-2 counterexample

Two laws were evaluated with `fractions.Fraction`.

Law A:

- (-1) with probability (1/2)
- (+1) with probability (1/2)

Law B:

- (-2) with probability (1/8)
- (0) with probability (3/4)
- (+2) with probability (1/8)

Both have exactly:

[
E[U]=0,qquad operatorname{Var}(U)=1.
]

But:

[
E[operatorname{ReLU}(U)]_A=rac12,
qquad
E[operatorname{ReLU}(U)]_B=rac14.
]

Therefore no universal exact later-layer ReLU centering rule can depend only on
mean and variance.

## Explicit depth-2 nonlinear defect

For (qin{-1,+1}) equiprobably, first layer

[
h_1(q)=(operatorname{ReLU}(q),operatorname{ReLU}(-q))
]

and second-layer weight ((1,-2)) give preactivations

[
U(+1)=1,qquad U(-1)=-2.
]

The exact antipodal pair ReLU output is

[
rac12.
]

Its exact decomposition is

[
-rac14+rac34=rac12,
]

where the linear term is (-1/4) and the absolute-value nonlinear term is
(3/4). The nonlinear term is therefore larger in magnitude than the linear
term and reverses its sign in this explicit depth-2 example.

## Two-Haar antisymmetry obstruction

For iid blocks (X_A,X_B), any symmetric baseline

[
B(X_A,X_B)=B(X_B,X_A)
]

and any antisymmetric control

[
C(X_A,X_B)=-C(X_B,X_A)
]

satisfy by exchangeability

[
E[C]=0,
qquad
E[(B-E[B])C]=0.
]

The executable fixture used the maximally correlated within-block state
(Y=Gin{-1,+1}), with

[
B=rac{Y_A+Y_B}{2},
qquad
C=G_A-G_B.
]

Exact rational results:

- (operatorname{Var}(B)=1/2)
- (operatorname{Var}(C)=2)
- (operatorname{Cov}(B,C)=0)

For frozen (alpha=1),

[
operatorname{Var}(B-C)
=
operatorname{Var}(B)+operatorname{Var}(C)
=
rac52
>
rac12.
]

Thus a later-layer statistic with unknown expectation cannot become a useful
linear variance-reducing control merely by subtracting the same statistic from
the other independent Haar block. That exact-zero-mean construction is
antisymmetric and orthogonal to the symmetric estimator.

## Executable gates

All passed exactly:

- same mean/variance but different ReLU mean counterexample;
- depth-2 ReLU decomposition;
- antisymmetric control mean exactly zero;
- covariance with symmetric baseline exactly zero;
- corrected-variance identity exactly `5/2`;
- deterministic repeat exact.

## Exact next gate for a deep nonlinear successor

Before any production implementation, a successor must exhibit an
output-relevant later-layer statistic (G_ell) whose actual control satisfies
both:

1. **Exact centering:** its expectation is known exactly from frozen network
   weights / an exact identity without target fitting, or an alternative exact
   zero-mean construction is supplied.
2. **Non-antisymmetry:** the actual control added to the symmetric two-Haar
   estimator is not merely antisymmetric under Haar-block exchange.

A proposal based only on later-layer mean/variance closure fails condition 1.
A proposal centered only through `G(block_A)-G(block_B)` fails condition 2.

Passing this structural gate would establish only mathematical admissibility,
not useful risk reduction or competition accuracy.

## Verdict

**E109 closes two natural E108 successors before production code:**

- exact later-layer mean/variance-only ReLU centering;
- exact-zero-mean two-block difference controls applied linearly to the
  symmetric estimator.

The next admissible deep nonlinear candidate must provide a genuinely exact
non-antisymmetric later-layer centering identity.
