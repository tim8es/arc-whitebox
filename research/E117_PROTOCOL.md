# E117 protocol — scalar final-observable adjoint boundary-flux factorization

Idempotency key: `ARC-E117-SCALAR-OBSERVABLE-ADJOINT-FLUX-20260919`

Status: **PREREGISTERED / EXACT SMALL POSITIVE-CLOSURE TEST**.

## Provenance and non-duplication

- Branch: `research/e117-scalar-observable-adjoint-flux-20260919`.
- Direct parent: sealed E114 receipt commit
  `b9f64030f65da9b32fc7718d04fb108ee1a73dab`.
- E114 established the exact activation-boundary flux identity for deep
  zero-bias ReLU expectations on a depth-3 fixture.
- E116 separately studies fixed low-dimensional linear projection transport
  (F(x)=g(U^T x)) and is not reused.
- E117 asks a different question: can the E114 boundary integrand for a
  **scalar final observable** be represented by a scalar downstream transport
  rather than a full hidden/output vector closure?
- No Gaussian later-layer closure, Stein/JVP, latent mixture, mask-message
  table, QMC/cubature, target fit, public/scorer/holdout/full access, tuning,
  production run, canonical mutation, or ledger mutation.

## Local exact factorization theorem

Consider one scalar output (F(x)) of a zero-bias ReLU network. Fix a regular
codimension-one facet (Gamma) of the network's polyhedral partition on which
exactly one ReLU gate (g=(ell,j)) changes state and no other preactivation is
zero.

On each side of the facet, upstream and downstream masks are locally fixed.

Let

[
z_g(x)
]

be the preactivation of the switching gate. Inside the fixed upstream mask cell,

[
z_g(x)=a_g^T x,
qquad
a_g=
abla_x z_g.
]

Let

[
lambda_g
=
rac{partial F}{partial h_g}
]

be the scalar downstream adjoint sensitivity of the final observable with
respect to the post-ReLU activation (h_g=operatorname{ReLU}(z_g)), evaluated
with the locally fixed downstream masks on the active side.

Crossing the facet from inactive to active changes only

[
h_g: 0 longrightarrow z_g.
]

Therefore the full input-gradient jump is exactly

[
oxed{

abla_x F_{m active}-
abla_x F_{m inactive}
=
lambda_g,a_g.
}
]

For (qinGammacap S^{d-1}), homogeneity gives (a_g^Tq=0), so (a_g) is
already tangent to the sphere at the boundary. If the oriented unit normal
points from inactive to active,

[

u_g=rac{a_g}{|a_g|},
]

the E114 scalar boundary-flux jump becomes

[
oxed{
J_Gamma
=
(
abla_S F_{m active}-
abla_S F_{m inactive})cdot
u_g
=
lambda_g|a_g|.
}
]

Thus the E114 expectation identity specializes to a scalar-observable form

[
oxed{
E[F(X)]
=
rac{E[R]}{|S^{d-1}|(d-1)}
sum_{Gamma}
int_{Gamma}
lambda_Gamma(q),
|
abla_x z_Gamma(q)|,
dsigma_{d-2}(q).
}
]

The sum is over regular facet cells; if a geometric activation hyperplane is
split by downstream masks, each cell carries its own scalar adjoint
(lambda_Gamma).

This is exact local compression of the **observable transport**. It does not
compress the boundary geometry itself.

## Why this is not full-vector closure

A vector-valued output would require a vector adjoint for every output
coordinate. With one frozen scalar final observable, each facet needs only:

1. the local preactivation normal (a_g), needed to describe the facet and its
   measure;
2. one scalar downstream adjoint (lambda_g).

No full final-output covariance, joint hidden law, or vector-valued correction
state appears in the flux integrand.

The unresolved production question is whether the relevant facet cells and
normal measures can themselves be compressed.

## Frozen fixture

Reuse only the mathematical E114 depth-3 network identity:

[
W_1=
egin{bmatrix}
1&0\
0&1
end{bmatrix},
qquad
W_2=
egin{bmatrix}
1&1\
-2&0
end{bmatrix},
qquad
W_3=
egin{bmatrix}
2\
-1
end{bmatrix}.
]

With row-vector convention:

[
h_1=operatorname{ReLU}(xW_1),
quad
h_2=operatorname{ReLU}(h_1W_2),
quad
F(x)=operatorname{ReLU}(h_2W_3).
]

The three regular output kinks on the unit circle are:

1. (	heta=-pi/2): first-layer gate (h_{1,1});
2. (	heta=0): first-layer gate (h_{1,2});
3. (	heta=alpha=arctan(1/4)): final-layer gate.

For the first two facets, the active-side downstream masks are frozen by the
fixture and the scalar adjoints are obtained by exact matrix/backprop
multiplication.

Expected exact factors:

### Facet 1: (h_{1,1}) at (-pi/2)

[
a_1=(1,0),qquad lambda_1=1,
qquad lambda_1|a_1|=1.
]

### Facet 2: (h_{1,2}) at (0)

[
a_2=(0,1),qquad lambda_2=-4,
qquad lambda_2|a_2|=-4.
]

### Facet 3: final ReLU at (alpha)

The final preactivation in its active upstream cell is

[
z_3=x_1-4x_2,
]

so

[
a_3=(1,-4),qquad lambda_3=1,
qquad lambda_3|a_3|=sqrt{17}.
]

Hence scalar-adjoint flux predicts

[
sum_glambda_g|a_g|
=
1-4+sqrt{17}
=
sqrt{17}-3.
]

This must equal both the E114 derivative-jump sum and the direct angular
integral.

## Frozen executable test

Exactly one deterministic Python executable must mechanically:

1. construct the three weight matrices from integer entries;
2. compute active-side masks for the three frozen regular facet cells;
3. compute the switching preactivation input gradient (a_g) by exact masked
   chain multiplication;
4. compute the scalar downstream adjoint (lambda_g) by exact masked
   backpropagation;
5. verify the full region-gradient difference equals (lambda_ga_g) for each
   facet;
6. verify scalar fluxes are (1,-4,sqrt{17}) to absolute tolerance
   `1e-14`;
7. verify their sum is (sqrt{17}-3);
8. verify the implied Gaussian expectation equals
   ((sqrt{17}-3)/(2sqrt{2pi}));
9. verify deterministic replay is exact.

The script may use only deterministic arithmetic. No Monte Carlo or numerical
quadrature is scientific evidence.

## Frozen decision rule

If all gates pass:

**EXACT POSITIVE SCALAR-OBSERVABLE CONDITIONAL TRANSPORT IDENTITY VERIFIED.**

Interpretation:

- E114 boundary flux does admit a scalar final-observable transport
  factorization at each regular facet.
- Full-vector output closure is unnecessary for the local flux weight.
- This does **not** prove that the number/geometry of relevant facets is
  production-compressible.

If any factorization or gradient-jump identity fails, E117 is terminal
mathematical NO-GO. No alternate network, facet set, observable, masks, or
tolerance after execution.

## Next structural gate after a pass

A production-oriented successor must test whether many facet cells sharing the
same switching neuron can be aggregated by a finite output-specific signature
((a_g,lambda_g)) without enumerating all downstream mask refinements.

That is a boundary-state compression problem, not a hidden-vector moment
closure problem.
