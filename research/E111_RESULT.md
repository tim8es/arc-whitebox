# E111 Result — terminal scientific NO-GO

Idempotency key: `ARC-E111-LATE4-GAUSSIAN-RELU-PLUGIN-EXACT-BIAS-20260919`

Decision: **TERMINAL SCIENTIFIC NO-GO / DROP E111**

## Identity

Authoritative branch:

`research/e111-late4-gaussian-relu-plugin-cost-20260919`

E111 is a **deterministic Gaussian-ReLU late-layer plug-in estimator**. It is not a sampler or control-variate lane.

The existing cost audit and the scientific bias gate are one E111 identity:

- production cost protocol: `research/E111_PROTOCOL.md`
- cost receipt: `research/E111_COST_RECEIPT.jsonl`
- exact scientific gate freeze: `research/E111_BIAS_FALSIFIER_FREEZE.json`
- exact scientific falsifier: `scripts/e111_bias_falsifier.py`
- auxiliary exact two-ray sanity helper: `methods/e111_gaussian_relu_bias.py`

No E104/E108 terminal sampler/control lane is reopened.

## Production cost gate

Previously verified:

- inherited E104 measured cost: `149,114,620,592` FLOPs
- E111 late-4 plug-in increment: `105,891,842` FLOPs
- complete upper: `149,220,512,434` FLOPs
- utilization: `0.06785763272728218`
- utilization cap: `0.13`
- cost gate: **PASS**

Thus compute is not the blocker.

## Exact scientific mechanism test

The decisive reference uses:

- latent Gaussian dimension: `2`
- width: `8`
- depth: `4`
- zero biases
- He Gaussian weights
- frozen weight seed: `111111`
- no Monte Carlo
- no numerical quadrature
- no benchmark/public targets

Because the network is zero-bias and positively homogeneous, each fixed activation-mask angular sector is exactly linear in `cos(theta), sin(theta)`. The verifier recursively splits the full `[0,2pi)` circle at every exact preactivation zero and analytically integrates each sector, using exact Rayleigh radial moments

`E[R]=sqrt(pi/2)`, `E[R^2]=2`.

The Gaussian plug-in is then evaluated using the **exact pre-ReLU mean and variance** from this reference. Therefore measured discrepancy is irreducible Gaussian-assumption bias rather than trajectory noise.

## Frozen exact falsifier provenance

- cost parent head: `96aada531736b45061af47f35ed34f0c5d2a8e6c`
- exact bias freeze commit: `a7ca77a4c7360d9920f3302b2d6e7df6ce13a467`
- exact falsifier implementation lineage includes `c3ff1fcb151334fddce856df990e006f16f722ae`
- sole scientific arm head: `efd97d10311ded61aa943f4022e8a1c098a77711`

Execution:

- run: `35454366943`
- job: `105926930545`
- conclusion: `success`
- artifact: `e111-bias-falsifier`
- artifact ID: `10588270189`
- artifact ZIP SHA256:
  `6e26857b181e9ce29ec99a231002e824ffe8f257fd2c302346d0e76d1be92b5d`
- independently downloaded ZIP SHA256: identical
- extracted JSON SHA256:
  `276a46c205f4df0a1067b4a6ec4933e5621ca85fb637936aa182e94f978ce056`
- deterministic repeat max abs: `0.0`
- final exact angular interval count: `91`

## Exact bias measurements

Layerwise plug-in mean-bias MSE:

1. layer 1: `1.4059288594026822e-32`
2. layer 2: `2.460899425463496e-3`
3. layer 3: `4.066378888984171e-3`
4. layer 4 / final: `1.6698051697168073e-3`

The first layer is exact to floating-point precision, as required: its preactivation is genuinely Gaussian.

After the first ReLU, the plug-in assumption fails sharply.

Final-layer additional diagnostics:

- final bias MSE: `1.6698051697168073e-3`
- final max absolute mean bias: `7.700470798758577e-2`
- final signed-average bias: `3.0803717001582052e-2`
- competition raw target: `1.89e-8`
- final bias / target: **`88,349.48x`**
- maximum layer bias / target: **`215,152.32x`**

Current E108/E104-style production stochastic-risk scale is approximately
`1.0016395958298237e-5`.

The exact E111 final-layer deterministic plug-in bias MSE is therefore approximately
**`166.71x` larger than the entire current ~1e-5 stochastic-risk scale**.

This is decisive: even eliminating sampling variance completely would leave the frozen Gaussian plug-in many orders of magnitude above the target.

## Independent engineering sanity path

A separate closed-form one-dimensional two-ray helper was added after the exact 2-D falsifier solely as an implementation sanity check.

Focused RED:

- run `35454357206`
- job `105926906080`
- expected missing-module failure

Initial helper implementation exposed a scalar-only engineering bug; no scientific rerun occurred.

After the scalar fix:

- fix commit: `632302ab7a9224a15d8ee15a56ef6cccff2d16c3`
- focused GREEN run: `35454492351`
- job: `105927263839`
- conclusion: `success`

This helper does not supersede or modify the authoritative 2-D exact falsifier.

## Scientific interpretation

The mechanism under test was:

`exact pre-ReLU mean/variance -> Gaussian ReLU analytic mean`.

The failure occurs despite giving the plug-in **perfect first two moments**. Therefore the blocker is not sample variance, moment-estimation error, FLOP budget, or coefficient fitting. It is the non-Gaussian shape of later-layer preactivations after ReLU gating.

The first layer behaves exactly as Gaussian theory predicts; the error appears immediately at layer 2 and remains orders of magnitude too large.

Consequently there is **no credible path from the current ~1e-5 risk scale to 1.89e-8 using the frozen Gaussian-ReLU moment plug-in alone**.

Any repair based on skew/kurtosis, mixtures, alternate Gaussianization, extra state, clipping, layer selection, or fitted correction is a different mechanism and must use a new experiment identity. It is not an E111 rescue.

## Gates

PASS:

- production all-in utilization `<=0.13`
- exact reference finite
- plug-in finite
- deterministic exact-reference replay
- first-layer Gaussian sanity
- no benchmark/public targets
- no tuning/sweep/rerun

FAIL:

- every-layer mean-bias MSE `<=1.89e-8`
- final-layer mean-bias MSE `<=1.89e-8`
- credible path to competition raw target

## Verdict

**E111 = TERMINAL SCIENTIFIC NO-GO / DROP.**

Production cost remains feasible, but deterministic late-layer Gaussian plug-in bias is already about `8.8e4` times the raw target on an exact width-8/depth-4 reference and materially larger than the current production stochastic-risk scale.

No production scientific execution, public/public-mini, scorer, holdout/full, tuning, rescue, canonical mutation, ledger mutation, or merge is authorized or performed.
