# Hybrid analytic deep mean + certified kink-remainder scout

Idempotency key: `ARC-HYBRID-DEEP-KINK-REMAINDER-20260919`

Status at freeze: **SMALL-WIDTH IDENTITY FALSIFIER AUTHORIZED; PRODUCTION EXECUTION FORBIDDEN**.

## Non-overlap

This lane is distinct from:
- E108 first-layer exact-mean transported control variate;
- E109 deep Stein/JVP control;
- E110 deep line Rao-Blackwellization / fourth-harmonic / Householder lanes;
- post-E108 final-layer Jensen variance diagnostic.

There is no fitted coefficient, no target fitting, no Gaussian integration by parts,
no line conditioning, no first-layer transport, and no change to the E104 sampling law.

## Exact ReLU identity

For scalar anchor (m), let (s(m)=1[m>0]). Define

[
kappa_m(z)
=
operatorname{ReLU}(z)
-operatorname{ReLU}(m)
-s(m)(z-m).
]

Then for every real (z,m),

[
operatorname{ReLU}(z)
=
operatorname{ReLU}(m)+s(m)(z-m)+kappa_m(z).
]

The nonlinear remainder has certified support only at the kink crossing:

- if (m>0), (kappa_m(z)=-z) for (z<0), else 0;
- if (mle0), (kappa_m(z)=z) for (z>0), else 0.

Thus (kappa_m(z)ge0) and it is exactly zero whenever the sample stays on the
same affine ReLU branch as the anchor.

For a finite cloud of preactivations (z_i), choose
(m = rac1Nsum_i z_i). Then the linear fluctuation term averages to zero:

[
rac1Nsum_ioperatorname{ReLU}(z_i)
=
operatorname{ReLU}(m)
+
rac1Nsum_ikappa_m(z_i).
]

This is an exact finite-sample identity, not an approximation.

## Layerwise hybrid deep mean

For a zero-bias ReLU layer with previous activations (H_{ell-1}) and weights
(W_ell),

[
Z_ell = H_{ell-1}W_ell^T,qquad
m_ell = ar H_{ell-1}W_ell^T.
]

Linearity gives (m_ell = overline{Z_ell}). Therefore the empirical layer
mean obeys exactly

[
ar H_ell
=
operatorname{ReLU}(m_ell)
+
overline{kappa_{m_ell}(Z_ell)}.
]

The first term is the analytic mean-state backbone. The second term is the
certified nonlinear remainder and needs nonzero values only on sign-crossing
entries.

This identity may be applied at every depth. It does not by itself reduce
sampling variance; the purpose of this scout is to establish whether the
nonlinear remainder is sparse/small enough and cheap enough to justify a later
successor that evaluates or models only that certified remainder.

## Frozen small-width falsifier

No target/reference labels.

- width = 8
- depth = 4
- two E104-style independent Haar blocks plus exact antipodes
- total trajectories = 32
- analytic mean chi radius
- weight seed = 111104
- direction seed = 111105
- float64 propagation
- deterministic replay once inside the same process

For every layer and coordinate:

1. compute the direct empirical ReLU mean;
2. compute (m_ell=ar H_{ell-1}W_ell^T);
3. compute the analytic backbone (operatorname{ReLU}(m_ell));
4. compute the certified kink remainder;
5. reconstruct the direct mean;
6. verify the explicit piecewise remainder formula;
7. measure sign-crossing support fraction and remainder-energy fraction.

The aggregate residual support/energy measurements are diagnostics, not tunable gates.

## Frozen small-width gates

All required:

1. all values finite;
2. exact antithetic input pairs;
3. max layerwise mean reconstruction abs error <= 1e-12;
4. max pointwise ReLU identity abs error <= 1e-12;
5. max explicit-piecewise remainder disagreement <= 1e-12;
6. remainder exactly zero off the certified kink-crossing mask to <= 1e-12;
7. deterministic replay max abs == 0.

Any failed gate => **TERMINAL SMALL-WIDTH NO-GO**. No seed/width/depth rescue.

## Budget-first production admission

No production execution is authorized in this experiment.

Use the measured E104/E105 fully billed base:

- base FLOPs = 149,114,550,960
- base utilization = 0.06780944702768466
- budget = 2^41
- hard cap = 0.13

Freeze a deliberately loose overlay reserve of **1,000,000,000 FLOPs** for a
future production implementation of all 16 layerwise mean-state matvecs,
crossing-mask construction, sparse remainder extraction/reduction, hashes and
helpers.

Hence

[
F_{m upper}=150114550960,
]

[
u_{m upper}=150114550960/2^{41}
=0.06826419437857112 < 0.13.
]

The production budget admission gate therefore passes **before** any
production-shaped execution.

A small-width PASS plus this static budget admission means only:
**ADMISSIBLE FOR A SEPARATE PRODUCTION-SHAPE SUCCESSOR**.
It does not authorize a production run under this frozen scout and does not
claim competition accuracy improvement.

## Scope

No public/public-mini, benchmark target, official scorer, holdout/full,
target fitting, tuning, sweep, rescue, canonical mutation or ledger mutation.
