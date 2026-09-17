# E102 — full third-cumulant tensor rank lower bound

Idempotency key: `ARC-E102-K3-TENSOR-RANK-BOUND-20260918`

Status: **PREREGISTERED / ANALYTIC FALSIFIER ONLY**.

## Provenance and independence

- Branch: `research/e102-k3-tensor-rank-bound-20260918`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E099 closed one shared binary latent at fixed `pi=0.1`.
- E101 closed compact independent-binary multi-latent exact moment matching at the same fixed `pi`, with a covariance/skew lower bound `m>=741`.
- E102 is stronger and independent of the latent skewness parameter: it tests exact matching of the **full joint third-cumulant tensor**, not only marginal skew plus covariance.
- E100 lanes are unrelated sampling/shrinkage mechanisms and are not modified.
- No public/public-mini, scorer, benchmark holdout/full labels, tuning, sweep, canonical mutation, or ledger mutation.

## Frozen model class

Consider an additive latent-factor Gaussian closure

[
X = mu + sum_{a=1}^{m} d_a S_a + arepsilon,
]

where:

- (d_ainmathbb R^n);
- scalar latent factors (S_a) are mutually independent, centered, and have finite third cumulants (gamma_a=kappa_3(S_a)), with arbitrary signs/magnitudes;
- (arepsilon) is any independent Gaussian vector with arbitrary PSD covariance.

No binary/two-point assumption is required. No fixed mixture weight is required.

Because Gaussian noise has zero third cumulant and independent cumulants add,

[
K^{(3)}_X = sum_{a=1}^{m} gamma_a, d_aotimes d_aotimes d_a.
]

Thus every scalar latent contributes one symmetric CP-rank-one third-cumulant tensor.

## Exact first-layer target

For

[
H_i=operatorname{ReLU}(Z_i),qquad Z_istackrel{iid}{sim}N(0,1),
]

the coordinates are independent and have nonzero scalar central third cumulant

[
kappa = sqrt{rac2pi}
-rac32rac1{sqrt{2pi}}
+2left(rac1{sqrt{2pi}}ight)^3
>0.
]

Therefore the exact joint third-cumulant tensor is diagonal:

[
K^{(3)}_H
=
kappasum_{i=1}^{n} e_iotimes e_iotimes e_i.
]

At Phase-2 width, freeze (n=1024).

## Frozen rank proof

Mode-1 unfold the tensor into an (n	imes n^2) matrix.

For the target tensor, row (i) has exactly one nonzero entry (kappa) in column ((i,i)). These (n) rows have disjoint nonzero columns, hence

[
operatorname{rank}igl(K^{(3)}_{H,(1)}igr)=n.
]

Each additive scalar latent contributes after unfolding

[
gamma_a d_a(d_aotimes d_a)^	op,
]

which has matrix rank at most one. A sum of (m) such factors therefore has unfolding rank at most (m). Exact equality with the target requires

[
oxed{mge n}.
]

At official width:

[
oxed{m_{min}ge1024}.
]

This bound is independent of binary mixture weight, latent skew magnitude, loading signs, Gaussian residual covariance, and the covariance PSD issue that killed E099/E101.

## Explicit finite-mixture implication

If the independent scalar factors are binary and nonlinear propagation is performed by explicit component enumeration, (mge1024) implies at least

[
2^{1024}
]

Gaussian components before one nonlinear update. E102 records this only symbolically using (log_{10}(2^{1024})); it does not allocate exponential state.

## Frozen compactness gate

E102 defines a compact shared-latent closure as (mle64), the same deliberately generous cap used in E101.

Scientific GO requires:

- exact full-K3 tensor matching can occur with (mle64).

Since the proof is dimension-rank based, no optimization over factor values is needed.

## Runnable cross-check

Exactly one deterministic local script must:

1. compute the exact ReLU scalar third cumulant and verify it is finite and positive;
2. construct the exact target mode-1 unfolding for a small frozen cross-check (n_{test}=8) and verify numerical matrix rank is exactly 8;
3. verify each deterministic rank-one synthetic latent contribution has unfolding rank (le1);
4. report the official analytic lower bound (m_{min}=1024);
5. report (log_{10}(2^{1024}));
6. repeat deterministically and require scalar outputs identical.

The small numerical cross-check validates indexing/algebra only. The official (n=1024) result is the exact analytic rank identity, not an extrapolated fit.

## Frozen gates

Integrity:

- finite positive (kappa);
- (n_{test}=8) target unfolding rank exactly 8;
- every frozen test factor unfolding rank (le1);
- deterministic repeat max abs (=0).

Scientific GO:

- official latent-factor lower bound (m_{min}le64).

Failure of the scientific gate => **TERMINAL ANALYTIC NO-GO / DROP E102**.

No changing the compact-rank threshold, introducing vector-valued factors under the same ID, correlated latent factors, non-additive latent maps, tensor approximation, rerun, rescue, or public diagnostic. Those require a new experiment ID.

## Interpretation boundary

A NO-GO closes exact low-rank **additive independent scalar-latent** closures for the full third-cumulant tensor. It does not rule out approximate K3 representations, correlated/non-additive latent structures, or direct moment propagation that never interprets K3 as a finite latent mixture.
