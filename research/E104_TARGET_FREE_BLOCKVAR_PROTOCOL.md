# E104 target-free two-block variance probe

Idempotency key: `ARC-E104-TARGET-FREE-BLOCKVAR-20260919`

Status: **PREREGISTERED BEFORE EXECUTION**.

## Scope

This probe layers a target-free variance estimator on the frozen E104 Haar-radial
Rao-Blackwell estimator. It does not change the E104 point estimate. It reads no
benchmark/public/scorer/holdout/full target and does not mutate canonical or ledger.

The frozen production E104 shape is inherited from
`research/E104_PRODUCTION_VERIFY_FREEZE.json`:

- width = 1024
- depth = 16
- total trajectories = 4096
- positive Haar directions = 2048
- exactly two independent 1024x1024 Haar-QR blocks
- measured E104 base FLOPs = 149047442096
- measured base utilization = 0.06777892944955966
- budget = 2^41
- utilization limit for this probe = 0.135

## Estimator

Let the two independent Haar blocks produce final-layer block means
(Y_1,Y_2\in\mathbb R^p), each using its own 1024 positive directions and
their antithetic partners.

The unchanged E104 point estimate is

[
\hat\mu = \frac{Y_1+Y_2}{2}.
]

For each output coordinate (j), define

[
\widehat V_j = \frac{(Y_{1j}-Y_{2j})^2}{4}.
]

If the two block estimates are iid with variance (sigma_j^2), then

[
E[\widehat V_j]
=\frac{1}{4}E[(Y_{1j}-Y_{2j})^2]
=\frac{1}{2}\sigma_j^2
=\operatorname{Var}(\hat\mu_j).
]

Thus (widehat V_j) is an unbiased target-free estimator of the sampling
variance of the two-block E104 mean. The scalar diagnostic is

[
\widehat V_{\rm mean}=\frac1p\sum_j\widehat V_j,
\qquad
\widehat{SE}_{\rm RMS}=\sqrt{\widehat V_{\rm mean}}.
]

This is a variance/standard-error estimator, **not** a deterministic absolute
error bound.

## Frozen target-free calibration probe

Use one synthetic zero-bias ReLU MLP only:

- width = 64
- depth = 8
- network seed = 104960
- 32 independent two-block E104 replicates
- replicate r uses Haar seeds (804960+2r) and (804961+2r)
- each block has 64 positive Haar directions plus exact antithetic partners
- analytic mean chi radius, no random radius
- float32 propagation, float64 reductions

No reference mean/truth is computed.

For replicate r:
1. compute block means (Y_{r,1},Y_{r,2});
2. compute E104 mean (M_r=(Y_{r,1}+Y_{r,2})/2);
3. compute scalar predicted variance
   (widehat V_r=mean((Y_{r,1}-Y_{r,2})^2/4)).

The independent-repeat empirical variance is

[
V_{emp}=
\frac{1}{p}\sum_j
\frac{1}{R-1}\sum_r (M_{rj}-\bar M_j)^2.
]

The calibration statistic is

[
c=\frac{mean_r(\widehat V_r)}{V_{emp}}.
]

## Frozen calibration gates

All must pass:

1. all arrays/scalars finite;
2. exact antithetic input pairing;
3. per-block Haar orthogonality max abs <= 1e-12;
4. deterministic full probe replay max abs == 0;
5. empirical variance > 0;
6. mean predicted variance > 0;
7. calibration ratio 0.70 <= c <= 1.30.

Gate 7 is deliberately broad because the probe uses a finite 32-replicate
target-free ensemble; no parameter is changed after observing the result.

## Frozen production-overlay cost probe

Create a deterministic synthetic final-activation array with shape (4096,1024)
and the same production trajectory ordering: all positives first, then all
antithetic negatives. Inside one flopscope BudgetContext compute:

- mean for block-0 positive slice;
- mean for block-0 negative slice;
- block-0 mean;
- corresponding block-1 quantities;
- coordinatewise ((Y_1-Y_2)^2/4);
- scalar mean variance and RMS standard error.

This deliberately measures the conservative **additional** cost of extracting
block means after the final activation matrix exists. The existing E104 point
estimate remains unchanged, so total upper cost is

[
F_{layered}=149047442096+F_{overlay}.
]

Required gates:

8. measured overlay FLOPs > 0;
9. exact repeat overlay FLOPs equality;
10. deterministic variance/RMS outputs;
11. layered utilization <= 0.135;
12. overlay utilization <= 0.001.

## Terminal rule

Any failed gate => **E104 target-free error-estimator probe NO-GO**. No rescue,
seed change, repeat-count change, tolerance change, tuning, sweep, public run,
scorer, holdout/full, canonical mutation, or ledger mutation.

A pass means only that this target-free variance estimator is mathematically
admissible, empirically calibrated on the frozen synthetic no-truth probe, and
cheap enough to layer on E104. It does not establish competition raw MSE.
