# E109 terminal result — deep Gaussian-Stein directional-JVP control variate

Idempotency key: `ARC-E109-DEEP-STEIN-JVP-CV-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Mechanism

E109 tested a target-free Gaussian-Stein control on the actual final-layer
nonlinear map. For fixed network-derived input direction `v` and final output
coordinate `F_j`:

`C_{v,j}(x) = D_v F_j(x) - (v*x) F_j(x)`

has exact Gaussian expectation zero. The directional derivative was propagated
through the realized ReLU gates of all 16 layers with a forward JVP. Eight
network-derived directions were used, each tied to one group of final outputs.
Sampling was ordinary iid Gaussian antithetic; no Haar/Rao-Blackwell,
first-layer exact mean, E091, E100 orthogonal sampler, latent mixture, QMC or
cubature was used.

## Budget admission

Frozen upper bound:

- FLOPs: `271,548,019,200`
- utilization: `0.1234857423696667 <= 0.13`

Measured per-estimator candidate path:

- FLOPs: `266,952,952,000`
- utilization: `0.12139614773332141`
- exact reconciliation: PASS

Measured standalone same-sample iid-antithetic baseline:

- FLOPs: `133,349,212,160`
- utilization: `0.06064020097255707`

The budget-first admission was therefore valid.

## Sole frozen workflow

- Protocol commit: `f0c1270bf08b9937d15e8094fb4badd1a852c268`
- Frozen script commit: `9a7b35cbc7bfb0eef3241ae7755330d41007e4b2`
- Workflow commit: `9fc5e6522a658a5d4934e85c16e36a4e9e927833`
- Arm / executed head: `38285fb21acf95da4126643cb0723c7efaf97a1e`
- Run/job: `35453167481 / 105923744825`
- run attempt: `1`
- workflow conclusion: `success`
- artifact: `e109-deep-stein-jvp-cv`
- artifact ID: `10587586251`
- artifact ZIP SHA256:
  `458476a94e6857979ba3651c0a74f67814ea55faa49964b8ae4501904a7a4304`

Exactly one workflow run exists for the arm head. No rerun occurred.

## Scientific result

The ordinary iid-antithetic baseline target-free risk was:

`1.5656428546598965e-05`.

The candidate could not produce a valid finite risk. At least one frozen
cross-fit half/output coordinate had exactly zero Stein-control variance:

- `control_den_min = 0.0`
- `beta_abs_max = NaN`
- candidate finite: `false`
- candidate target-free risk: `NaN`

The two exact replay executions reproduced the same candidate SHA256 values for
each seed, but the frozen candidate determinism gate uses finite array equality;
because the candidate contains NaNs that gate fails. Baseline replay is
bitwise deterministic and its risk replay difference is exactly zero.

Other integrity results:

- exact antithetic pair max abs: `0.0`
- all eight network-derived direction norms finite and positive:
  minimum `0.0032959341047387853`,
  maximum `0.0039843483257579046`
- prediction shape: `(16,1024)`
- complete FLOP reconciliation: PASS
- no benchmark/public/scorer/holdout/full target access: PASS

## Blocker and verdict

The exact Stein identity itself is admissible, and its full JVP implementation
fits the production budget. The frozen scalar cross-fit, however, is not
well-defined on the production-shaped realization because some control
coordinates have zero empirical variance in a training half. The protocol
explicitly forbids ridge, clipping, fallback, coefficient changes or rescue
after seeing the result.

Therefore:

**E109 = TERMINAL NO-GO / DROP.**

No rerun, coefficient repair, seed/sample/K change, tuning, public diagnostic,
scorer, holdout/full evaluation, canonical mutation or ledger mutation occurred.
