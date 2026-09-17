# E103 Accounting Reconciliation — implementation evidence incomplete

Idempotency key: `ARC-E103-ORTHOGONAL-ANTITHETIC-PRODUCTION-SHAPE-20260918`

Status: **APPEND-ONLY FACTUAL CORRECTION / E103 SEALED**

This note does not edit the frozen E103 sampler, rerun E103, or change any scientific gate. It corrects the interpretation of `research/E103_RESULT.md`.

## Frozen evidence retained

Sole production-shape run:

- run `35287256818`
- job `105422236549`
- head `868e31d4a6c0c438eccae185b04bb25d81186f09`
- artifact `10525181002`
- artifact ZIP SHA-256 `2141c794724b30e706822f1b1a04d61a73bb7d979db04d7c078933e73099630f`
- workflow conclusion `success`
- output shape `(16,1024)`
- finite output: true
- exact antithetic pair max abs: `0.0`
- input variance: `0.9986440860698316`
- input fourth moment: `2.9873390141472815`
- flopscope-reported FLOPs: `149047446192`
- reported utilization: `0.0677789313122048`

These execution facts remain valid.

## Factual accounting defect

The billed estimator path in `methods/e103_orthogonal_antithetic.py` used plain NumPy RNG:

`np.random.Generator(np.random.PCG64(seed)).standard_normal(...)`

and

`np.random.Generator(...).chisquare(...)`

then wrapped the already-generated arrays with `fnp.asarray`.

Therefore the random draws occurred outside flopscope and were absent from `BudgetContext.flops_used`.

Under the flopscope 0.12.x cost model, random samplers are billable numerical operations. `standard_normal` and `chisquare` are transcendental-tier draws; at their default float64 dtype they bill `32 * numel(output)`.

For E103:

- two `1024 x 1024` Gaussian QR-source matrices:
  `2 * 1024^2 * 32 = 67108864` missing billed FLOPs;
- two vectors of `1024` chi-square radii:
  `2 * 1024 * 32 = 65536` missing billed FLOPs;
- exact minimum missing RNG bill:
  `67174400` FLOPs.

Thus an arithmetic correction to the observed run is at least

`149047446192 + 67174400 = 149114620592` FLOPs,

or utilization

`149114620592 / 2^41 = 0.06780947869265219`.

This corrected value still passes both `0.12` and `0.135` cost thresholds by a large margin.

## Classification

The original statement

> E103 = PRODUCTION-SHAPE IMPLEMENTATION GO ONLY

is **superseded as a claim of complete measured flopscope accounting**.

Correct classification:

- production-shape execution/shape/finite/marginal checks: **VERIFIED**;
- cost feasibility after explicit missing-RNG correction: **VERIFIED analytically below gate**;
- complete package-safe flopscope billing: **NOT VERIFIED**;
- production/public accuracy: **UNEXECUTED**;
- `scientific_go = false`.

This is an implementation/evidence-integrity defect, not evidence that the orthogonal-antithetic scientific mechanism failed.

## Seal / successor rule

E103 has already consumed its sole frozen production-shape run. It must not be rerun or rescued under E103.

Any accounting-complete implementation must use a new collision-checked experiment ID, keep the E100/E103 sampling law, width/depth/N/seeds unchanged, replace only the unbilled NumPy RNG in the estimator path with flopscope RNG primitives, and perform exactly one local production-shape accounting run before any public data.

No public/public-mini, official scorer, holdout/full, benchmark targets, tuning, sample-count change, QR change, seed change, canonical/ledger mutation, merge, or E103 rerun is authorized.
