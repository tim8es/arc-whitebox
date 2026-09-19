# E114 protocol — exact activation-boundary flux identity for deep ReLU expectation

Idempotency key: `ARC-E114-ACTIVATION-BOUNDARY-FLUX-20260919`

Status: **PREREGISTERED / EXACT SMALL POSITIVE CLOSURE ONLY**.

## Provenance and non-duplication

- Branch: `research/e114-activation-boundary-flux-20260919`.
- Direct parent: terminal E111 branch
  `research/e111-late4-gaussian-relu-plugin-cost-20260919`.
- E111 showed that exact later-layer pre-ReLU mean/variance followed by a
  Gaussian ReLU plug-in has irreducible bias after the first layer.
- E112 separately targets explicit activation-mask message passing and has a
  treewidth/state-size obstruction for dense networks.
- E110 deep-line Rao–Blackwellization conditions on a one-dimensional Gaussian
  coordinate and integrates the network along affine lines.
- E114 is different: it derives the expectation from **activation-boundary
  flux on the sphere**, not from a Gaussian moment closure, Stein/JVP identity,
  finite latent mixture, mask-state table, QMC/cubature, or line conditioning.
- No benchmark/public/scorer/holdout/full targets, tuning, sweep, production
  execution, canonical mutation, or ledger mutation.

## General exact identity

Let (F:\mathbb R^d\to\mathbb R) be continuous, positively homogeneous of
degree one, and piecewise linear. Every scalar output coordinate of a zero-bias
ReLU network has this form.

Restrict to the unit sphere:

[
f(q)=F(q),\qquad q\in S^{d-1}.
]

On every spherical linear region (C_r),

[
f(q)=a_r^\top q.
]

The degree-one spherical harmonic identity gives, inside each open region,

[
\Delta_S f=-(d-1)f.
]

Across a codimension-one interface (Gamma) between two adjacent regions,
the tangential gradient has a normal jump. For one fixed orientation (
u)
on (Gamma), define

[
J_Gamma(q)
=
(\nabla_S f^+(q)-\nabla_S f^-(q))\cdot\nu(q),
]

with (+) chosen on the side pointed to by (
u).

Distributionally,

[
\Delta_S f
=
-(d-1)f
+
\sum_Gamma J_Gamma\,\delta_Gamma.
]

The integral of the spherical Laplacian over a closed sphere is zero. Therefore

[
\boxed{
(d-1)\int_{S^{d-1}} f(q)\,d\sigma(q)
=
\sum_Gamma
\int_Gamma J_Gamma(q)\,d\sigma_{d-2}(q)
}
]

for (d\ge2).

For (X\sim N(0,I_d)), polar decomposition (X=RQ) gives (R\perp Q) and
positive homogeneity gives

[
E[F(X)]
=
E[R]\,E_Q[f(Q)].
]

Hence the exact deep-ReLU expectation can be written entirely as a
codimension-one activation-boundary flux:

[
\boxed{
E[F(X)]
=
\frac{E[R]}
{|S^{d-1}|(d-1)}
\sum_Gamma
\int_Gamma J_Gamma\,d\sigma_{d-2}
}
]

with no Gaussian approximation of later-layer preactivations.

This is an identity, not yet a production algorithm. The number/geometry of
interfaces may still be too large at production width/depth.

## Two-dimensional finite specialization

For (d=2), write (q(\theta)=(\cos\theta,\sin\theta)) and
(f(\theta)=F(q(\theta))). Between kink angles (	heta_k),

[
f''(\theta)+f(\theta)=0.
]

At each kink, let

[
\Delta_k=f'(\theta_k^+)-f'(\theta_k^-).
]

Then exactly

[
\boxed{
\int_0^{2\pi} f(\theta)\,d\theta
=
\sum_k\Delta_k
}
]

and, since (E[R]=\sqrt{\pi/2}) for a 2-D standard Gaussian,

[
\boxed{
E[F(X)]
=
\frac{\sqrt{\pi/2}}{2\pi}
\sum_k\Delta_k.
}
]

Thus a deep non-Gaussian expectation is computable from a finite set of
activation-boundary derivative jumps whenever those boundaries can be
enumerated finitely.

## Frozen explicit depth-3 network

Use the exact zero-bias network

Layer 1:

[
h_1=(\operatorname{ReLU}(x_1),\operatorname{ReLU}(x_2)).
]

Layer 2:

[
u_1=\operatorname{ReLU}(h_{1,1}-2h_{1,2}),\qquad
u_2=\operatorname{ReLU}(h_{1,1}).
]

Layer 3 scalar output:

[
F(x)=\operatorname{ReLU}(2u_1-u_2).
]

Equivalently, with row-vector convention:

[
W_1=
\begin{bmatrix}1&0\\0&1\end{bmatrix},\quad
W_2=
\begin{bmatrix}1&1\\-2&0\end{bmatrix},\quad
W_3=
\begin{bmatrix}2\\-1\end{bmatrix}.
]

On the unit circle, the exact final output is

[
f(\theta)=
\begin{cases}
\cos\theta, & -\pi/2<\theta<0,\\
\cos\theta-4\sin\theta,
& 0<\theta<\alpha,\\
0,&\text{otherwise},
\end{cases}
]

where

[
\alpha=\arctan(1/4).
]

The three output kink angles are

[
-\pi/2,\quad 0,\quad\alpha.
]

Their derivative jumps are exactly

[
1,\quad -4,\quad \sqrt{17}.
]

Therefore

[
\sum_k\Delta_k=\sqrt{17}-3.
]

Direct sector integration gives the same exact angular integral:

[
\int_0^{2\pi}f(\theta)d\theta=\sqrt{17}-3.
]

Consequently

[
\boxed{
E[F(X)]
=
\frac{\sqrt{17}-3}{2\sqrt{2\pi}}
}
]

for (X\sim N(0,I_2)).

The boundary at (	heta=\arctan(1/4)) is created by the **third-layer ReLU**.
It is not a first-layer Gaussian identity. This makes the fixture explicitly
deep and nonlinear.

## Frozen executable test

Exactly one deterministic standard-library Python executable must:

1. evaluate the three-layer network directly on deterministic interior angles
   from every stated sector;
2. verify the exact piecewise formulas to absolute tolerance `1e-14`;
3. compute the three derivative jumps from the adjacent linear-region
   coefficient vectors;
4. verify their sum against `sqrt(17)-3` to `1e-14`;
5. compute the sector integral analytically from endpoint sine/cosine values
   and verify it against the same closed form to `1e-14`;
6. verify boundary-flux sum == sector integral to `1e-14`;
7. verify the Gaussian expectation from the boundary identity equals
   `(sqrt(17)-3)/(2*sqrt(2*pi))` to `1e-14`;
8. verify the downstream kink at `atan(1/4)` is not a first-layer boundary
   (first-layer boundaries are multiples of `pi/2`);
9. repeat deterministically with exact equality of the JSON payload.

No Monte Carlo or numerical quadrature is scientific evidence in E114.

## Frozen verdict rule

If all gates pass:

**EXACT POSITIVE CLOSURE — ACTIVATION-BOUNDARY FLUX IDENTITY VERIFIED.**

This establishes a new exact representation of a deep ReLU Gaussian
expectation beyond Gaussian closure and first-order Stein.

It does **not** establish that the boundary set is compact at width 1024/depth
16. A production successor is admissible only after a separate structural
gate shows that the output-relevant boundary flux can be represented or
sampled within the ARC utilization cap without target fitting.

Any failed identity gate => terminal E114 mathematical NO-GO. No fixture,
network, tolerance, or identity change after execution.
