# E111 protocol — last-4-layer Gaussian-ReLU plug-in cost audit

Idempotency key: ARC-E111-LATE4-GAUSSIAN-RELU-PLUGIN-COST-20260919

Status: PREREGISTERED / COST-ONLY / NO SCIENTIFIC ACCURACY CLAIM.

## Provenance

- Branch: research/e111-late4-gaussian-relu-plugin-cost-20260919.
- Parent: E104 accounting-complete receipt head dc4c1f8edfae07841b0c32be4004c352c8dcd1dd.
- Pinned E104 measured base: 149114620592 FLOPs at width=1024, depth=16, N=4096.
- Budget B=2^41.
- Production audit gate: all-in utilization <=0.13.
- No public/public-mini, scorer, holdout/full, benchmark targets, tuning, canonical mutation, or ledger mutation.

## Candidate mechanism

This lane tests only whether a later-layer nonlinear estimator has an honest production FLOP path.

Reuse the E104 trajectories and dense forwards unchanged. No fresh random draw and no extra network trajectory is allowed.

For exactly the last 4 layers, on the already-computed pre-ReLU trajectory matrix Z in R^(4096 x 1024), compute coordinatewise

    mu = E_sample[Z]
    var = max(E_sample[Z^2] - mu^2, 1e-12)
    sigma = sqrt(var)
    alpha = mu / sigma
    plugin = sigma * phi(alpha) + mu * Phi(alpha)

using flopscope-billed operations, including normal pdf/cdf.

The candidate would use plugin as the reported mean for those four layers. This protocol does not claim that the Gaussian approximation is accurate.

## Error-estimator accounting

The frozen E104 trajectory layout contains two independent Haar blocks, each paired with its own antithetic negatives.

At the final layer only, form one plug-in estimate from block 0 plus its antithetic block and one from block 1 plus its antithetic block. Bill every block reduction, square, sqrt, pdf/cdf and final reduction.

Record

    variance_hat = mean((plugin_0 - plugin_1)^2) / 4.

For iid block estimators Y0,Y1, this is unbiased for Var((Y0+Y1)/2) coordinatewise after averaging coordinates. It is a randomization-variance estimator only; it does not certify nonlinear plug-in bias and therefore cannot by itself prove raw MSE <=1.89e-8.

## Billing rules

The E104 measured base already includes:
- Gaussian RNG;
- chi-square RNG;
- QR and sign normalization;
- radial sqrt/scaling/cast/concatenation;
- all 16 dense forwards;
- ReLUs;
- all layer mean reductions.

E111 must not subtract any of those old reductions. Its production cost upper bound is

    E104_MEASURED_FLOPS + measured_E111_increment.

The E111 increment must contain all moment reductions, squares, clips/max, sqrt/division, normal pdf/cdf, block helpers and variance-estimator reduction. No numeric helper may execute outside BudgetContext.

Fixture construction for the cost harness is outside BudgetContext because it represents pre-existing pre-ReLU activations supplied by the already-billed forward path.

## Frozen shape

- width 1024
- depth 16
- trajectories 4096
- nonlinear layers audited: exactly 4
- independent block count: exactly 2
- dtype of trajectory activations: float32
- reductions/moment transforms: float64 where requested by the harness

## Cost gates

Let HARD=floor(0.13 * 2^41).

PASS requires:
1. incremental harness finite;
2. deterministic repeat max_abs == 0;
3. no RNG call in E111 incremental helper;
4. normal pdf/cdf are flopscope-billed;
5. error-estimator/block helpers are inside the measured BudgetContext;
6. E104 measured base + E111 measured increment <= HARD;
7. total utilization <=0.13;
8. remaining FLOPs after the complete upper bound >0.

If gate 6 or 7 fails, E111 is terminal COST NO-GO. No layer-count reduction, precision change, removal of error accounting, helper omission or cost credit is allowed as rescue under E111.

A PASS is COST FEASIBILITY ONLY. It does not authorize benchmark/public execution or scientific GO.
