# E109 protocol — later-layer nonlinear centering gate

Idempotency key: `ARC-E109-LATERLAYER-NONLINEAR-CENTERING-GATE-20260919`

Status: **PREREGISTERED / ANALYTIC PRE-CODE FALSIFIER**.

## Provenance and scope

- Branch: `research/e109-laterlayer-nonlinear-centering-gate-20260919`.
- Direct parent: terminal E108 branch `research/e108-firstlayer-exactmean-transport-cv-20260919`.
- E108 measured only a 0.275% target-free risk reduction and concluded that the exact first-layer mean fluctuation transported through the fixed `0.5` Jacobian does not explain the dominant final-layer angular error.
- E109 does not alter E104/E108 sampling, does not fit a coefficient, does not run a production estimator, and does not evaluate any benchmark/public/reference target.
- No tuning, seed sweep, scorer, holdout/full, canonical mutation, or ledger mutation.

## Exact later-layer identity

For every real scalar preactivation (U),

[
operatorname{ReLU}(U)=rac{U+|U|}{2}.
]

Therefore

[
E[operatorname{ReLU}(U)]
=
rac12 E[U]+rac12 E|U|.
]

At the first layer under a spherical/Gaussian input, the E108 exact-mean identity
supplies the needed absolute first moment analytically. At later layers, a generic
preactivation is a signed linear combination of nonnegative ReLU outputs, and its
absolute first moment is not determined by its mean and variance.

### Exact moment-2 counterexample

Freeze two centered scalar laws:

**Law A**

- (U=-1) with probability (1/2);
- (U=+1) with probability (1/2).

**Law B**

- (U=-2) with probability (1/8);
- (U=0) with probability (3/4);
- (U=+2) with probability (1/8).

Both satisfy exactly

[
E[U]=0,qquad E[U^2]=1.
]

But

[
E[operatorname{ReLU}(U)]_A=rac12,
qquad
E[operatorname{ReLU}(U)]_B=rac14.
]

Hence there is no universal function of only ((E[U],E[U^2])) that gives the
exact later-layer ReLU mean.

This kills any proposed **exact** later-layer centering rule whose state contains
only mean/variance (or quantities algebraically equivalent to them).

## Explicit depth-2 nonlinear defect

Use the two-point sphere (qin{-1,+1}) with equal probability.

First layer:

[
h_1(q)=(operatorname{ReLU}(q),operatorname{ReLU}(-q)).
]

Second-layer scalar preactivation with frozen weight vector ((1,-2)):

- for (q=+1): (U=1);
- for (q=-1): (U=-2).

The exact antipodal pair output is

[
rac{operatorname{ReLU}(1)+operatorname{ReLU}(-2)}2
=rac12.
]

The decomposition is

[
rac{1+(-2)}4
+
rac{|1|+|-2|}{4}
=
-rac14+rac34
=
rac12.
]

Thus the nonlinear absolute-moment term is not a perturbative detail: in this
explicit depth-2 network it is larger in magnitude than the linear term and
changes the sign of the result.

## Two-Haar antisymmetry obstruction

Let (X_A,X_B) be two iid independent block objects. Let the baseline estimator
(B(X_A,X_B)) be symmetric under block exchange:

[
B(X_A,X_B)=B(X_B,X_A).
]

Let an exactly centered unknown-mean control be constructed only as a block
difference

[
C(X_A,X_B)=G(X_A)-G(X_B).
]

Then (C) is antisymmetric:

[
C(X_B,X_A)=-C(X_A,X_B).
]

Exchangeability gives exactly

[
E[C]=0
]

and

[
E[(B-E[B])C]=0.
]

Therefore for every frozen deterministic scalar coefficient (alpha),

[
operatorname{Var}(B-alpha C)
=
operatorname{Var}(B)+alpha^2operatorname{Var}(C)
ge
operatorname{Var}(B).
]

The vector version follows componentwise / by the same swap argument for cross
covariances.

So simply estimating an unknown later-layer centering constant on the other
Haar block and using the resulting antisymmetric difference cannot provide
variance reduction to the symmetric two-block estimator.

## The exact next gate

A deep/later-layer nonlinear successor is admissible only if it supplies at
least one output-relevant statistic (G_ell) satisfying **both**:

1. **Exact centering:** an expectation
   [
   	heta_ell(W)=E_Q[G_ell(Q)]
   ]
   is known exactly from frozen network weights / an exact identity, without
   benchmark targets, fitted truth, or same-run tuning; **or** an exactly
   zero-mean construction is given that is not merely antisymmetric under the
   two-Haar block swap.

2. **Non-antisymmetry:** the actual control added to the symmetric E104/E108
   estimator is not an antisymmetric block-difference control, because such a
   control is exactly orthogonal to the symmetric baseline.

If a proposed successor has only mean/variance closure for the later-layer
ReLU expectation, or centers an unknown nonlinear statistic solely by
`G(block_A)-G(block_B)`, it fails this gate **before production code**.

Passing this gate does not imply useful risk reduction; it only establishes that
the proposed later-layer nonlinear control is mathematically capable of being
both exactly centered and nontrivially correlated with the symmetric estimator.

## Frozen executable falsifier

Exactly one deterministic standard-library Python script must verify:

1. Law A and Law B have exact rational mean (0) and variance (1);
2. their exact ReLU means are (1/2) and (1/4);
3. the depth-2 example gives linear term (-1/4), absolute term (3/4),
   exact pair output (1/2);
4. on an explicit two-state iid block fixture with maximal within-block
   correlation (Y=Gin{-1,+1}), the symmetric baseline
   (B=(Y_A+Y_B)/2) and antisymmetric control (C=G_A-G_B) have exact
   covariance (0);
5. for frozen (alpha=1),
   [
   operatorname{Var}(B-C)=operatorname{Var}(B)+operatorname{Var}(C)
   =5/2>1/2=operatorname{Var}(B);
   ]
6. deterministic repeated evaluation is identical.

All arithmetic for these identities must use `fractions.Fraction`; no floating
approximation is required for the scientific result.

## Frozen verdict rule

If all identities pass, E109 verdict is:

**STRUCTURAL GATE ESTABLISHED / MOMENT-2 AND ANTISYMMETRIC-CENTERING NO-GO.**

This is not a competition-accuracy claim and does not authorize a public or
production-shape run. The sole next admissible deep nonlinear candidate must
first exhibit an exact, non-antisymmetric later-layer centering identity.
