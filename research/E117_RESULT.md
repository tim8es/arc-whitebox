# E117 result — scalar final-observable adjoint flux positive closure

Idempotency key: `ARC-E117-SCALAR-OBSERVABLE-ADJOINT-FLUX-20260919`

Decision: **EXACT POSITIVE SCALAR-OBSERVABLE CONDITIONAL TRANSPORT VERIFIED**

## Provenance

- Branch: `research/e117-scalar-observable-adjoint-flux-20260919`
- Parent: sealed E114 receipt commit
  `b9f64030f65da9b32fc7718d04fb108ee1a73dab`
- Protocol commit:
  `299231c3ddca1025fc5db7c5404d04dc2aed0aae`
- Executable commit:
  `1bda8fd0133015009a1637b16588e1a764ea700e`
- Workflow commit:
  `bff728f38fb006674f4fd3558bf8ab6d3760ae39`
- Run/job:
  `35456272279 / 105931983784`
- Workflow conclusion: `success`
- Artifact:
  `e117-scalar-observable-adjoint-flux`
- Artifact ID:
  `10587968246`
- Artifact ZIP SHA256:
  `29857a2c2ab1001d7c4952601a3b1e2a5476623da0b4a0dad16a5ee129023f1e`
- Artifact size:
  `1156` bytes

No target, public/public-mini, scorer, holdout/full, tuning, Monte Carlo,
numerical quadrature, production run, canonical mutation, or ledger mutation.

## Exact scalar-observable identity

On a regular activation facet (Gamma) where a single ReLU gate
(g=(ell,j)) switches and all other masks are locally fixed, its preactivation
is locally linear in the input,

[
z_g(x)=a_g^Tx,
qquad a_g=
abla_x z_g.
]

For one frozen scalar final observable (F), define the active-side scalar
downstream adjoint

[
lambda_g=rac{partial F}{partial h_g}.
]

The active/inactive input-gradient jump factorizes exactly as

[
oxed{

abla F_{m active}-
abla F_{m inactive}
=
lambda_g a_g.
}
]

On the spherical boundary (a_g^Tq=0), so the oriented E114 flux is

[
oxed{
J_Gamma=lambda_g|a_g|.
}
]

Combining with E114,

[
oxed{
E[F(X)]
=
rac{E[R]}{|S^{d-1}|(d-1)}
sum_{Gamma}
int_Gamma
lambda_Gamma(q),
|
abla_x z_Gamma(q)|
,dsigma_{d-2}(q).
}
]

The local observable transport is therefore scalar: each regular facet needs
one downstream scalar adjoint rather than a full output-vector closure.

## Mechanical fixture result

The executable reconstructed masks, preactivation gradients, scalar adjoints,
and full region gradients directly from the frozen E114 matrices.

### Facet 1 — first-layer (x_1) gate

- preactivation gradient:
  [
  a_1=(1,0)
  ]
- scalar downstream adjoint:
  [
  lambda_1=1
  ]
- exact full gradient jump:
  [
  (1,0)
  ]
- factored jump:
  [
  lambda_1a_1=(1,0)
  ]
- scalar flux:
  [
  1.
  ]

### Facet 2 — first-layer (x_2) gate

- preactivation gradient:
  [
  a_2=(0,1)
  ]
- scalar downstream adjoint:
  [
  lambda_2=-4
  ]
- exact full gradient jump:
  [
  (0,-4)
  ]
- factored jump:
  [
  lambda_2a_2=(0,-4)
  ]
- scalar flux:
  [
  -4.
  ]

### Facet 3 — final-layer gate

- preactivation input gradient:
  [
  a_3=(1,-4)
  ]
- scalar downstream adjoint:
  [
  lambda_3=1
  ]
- exact full gradient jump:
  [
  (1,-4)
  ]
- factored jump:
  [
  lambda_3a_3=(1,-4)
  ]
- scalar flux:
  [
  sqrt{17}.
  ]

All three vector factorizations were exact under rational arithmetic before the
norm operation.

## Recovered E114 expectation

Scalar fluxes:

[
1,quad -4,quad sqrt{17}.
]

Their sum is

[
sqrt{17}-3
=
1.1231056256176606.
]

The implied Gaussian expectation is

[
rac{sqrt{17}-3}{2sqrt{2pi}}
=
0.22402715970779363.
]

Executable scalar-flux reconstruction gave

[
0.22402715970779358,
]

with max individual flux error `0.0` against
((1,-4,sqrt{17})) at the frozen tolerance.

Deterministic replay was exact.

## Interpretation

This is positive mathematical support for E114's alternative compression:

- the hidden vector law does **not** need to be closed in order to assign the
  local boundary-flux weight for one scalar final observable;
- the downstream transport contribution collapses exactly to one scalar
  adjoint (lambda_g);
- the remaining noncompressed object is the activation-boundary geometry and
  its local normal (a_g).

So the next obstruction is sharper than “full-vector dependence”: the
production difficulty is whether exponentially many downstream mask-refined
facet cells can be aggregated without losing the scalar pair
((a_g,lambda_g)).

## Next exact gate

For a fixed switching neuron, test whether all descendant mask refinements
produce only a small number of distinct output-specific signatures

[
(a_g,lambda_g).
]

If the number of distinct scalar-adjoint signatures grows exponentially even
when only one final observable is retained, then scalar transport does not
solve E114's production state problem. If it remains small, E114 acquires a
genuine compression path.
