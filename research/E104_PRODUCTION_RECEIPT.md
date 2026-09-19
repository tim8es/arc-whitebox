# E104 Production-Shaped Accounting Receipt

Idempotency key: `ARC-E104-ORTHOGONAL-ANTITHETIC-COMPLETE-BILLING-20260918`

Status: **ACCOUNTING-COMPLETE PRODUCTION-SHAPE GO ONLY / scientific_go=false**

This receipt is append-only. It records the sole frozen E104 production-shaped accounting execution and does not authorize public/public-mini, official scorer, holdout/full, benchmark target access, tuning, rerun, canonical mutation, ledger mutation, or merge.

## Provenance

- Branch: `research/e104-orthogonal-antithetic-complete-billing-20260918`
- Direct canonical origin: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `2bec307743a0f2ef35556014acd4565eb13a77f3`
- Focused GREEN test-only fix head: `e269870ca6c583319e88b1fd7c78a7a8ad5fa454`
- Frozen production harness commit: `dfd7b4925a7cbaad587e99968996e3ed1ae6eec7`
- Sole production workflow/head commit: `f1f468bb707f1dbea5c7cd1a5e6350ce591f35d2`

File Git blobs at the executed head:

- `methods/e104_orthogonal_antithetic.py`: `3d591f4d53f24cb050c9f6b8fb5e77ca202ca458`
- `scripts/e104_production_shape.py`: `64ac5cca648d8b1ed46d95875676c075693421df`
- `.github/workflows/e104-production-shape.yml`: `bf6f91ef2854602307dd718e3cd012dc8faacfe4`

## Frozen execution

GitHub Actions:

- workflow: `E104 sole complete-billing production shape`
- run ID: `35445997032`
- job ID: `105904896063`
- run attempt: `1`
- head SHA: `f1f468bb707f1dbea5c7cd1a5e6350ce591f35d2`
- run conclusion: `success`
- scientific/accounting step conclusion: `success`

Frozen shape/config:

- width: `1024`
- depth: `16`
- trajectories: `4096`
- weight seed: `103103`
- sample seed: `103104`
- budget: `2**41 = 2199023255552`

No benchmark/public/scorer/holdout/full target data were read.

## Immutable artifact

- artifact name: `e104-production-shape`
- artifact ID: `10585338694`
- artifact size: `1224` bytes
- artifact SHA-256: `0c1d9eda83b641ebcb7bba25931c44c5c79079909f271094182a8352cbe1770e`
- artifact expiry: `2026-12-18T13:31:01Z`

Artifact payload includes:

- `e104-production-shape.json`
- `e104-run-meta.txt`

## Measured accounting

Frozen expectations:

- E103 reported FLOPs: `149047446192`
- expected RNG delta: `67174400`
- expected E104 total FLOPs: `149114620592`

Measured E104:

- measured FLOPs: `149114620592`
- measured minus E103 FLOPs: `67174400`
- measured minus expected total: `0`
- measured utilization: `0.06780947869265219`
- wall time inside production harness: `1.7012742040000006 s`

Therefore:

- `measured_flops == expected_total`: **PASS**
- `measured_minus_e103 == expected_rng_delta`: **PASS**
- exact counter deviation from frozen expectation: **0 FLOPs**

## Structural/marginal gates

- prediction shape: `[16,1024]`: **PASS**
- finite output: **PASS**
- trajectories exactly `4096`: **PASS**
- exact antithetic pair max abs: `0.0`: **PASS**
- input variance about zero: `0.9986440860698316` in `[0.95,1.05]`: **PASS**
- input fourth moment: `2.9873390141472815` in `[2.7,3.3]`: **PASS**
- measured FLOPs `>=149114620592`: **PASS**
- measured FLOPs `<=151000000000`: **PASS**
- utilization `<=0.12`: **PASS**
- utilization `<=0.135`: **PASS**
- no targets/public/scorer/holdout/full: **PASS**

All frozen E104 production-shaped accounting gates passed.

## Classification

**VERIFIED**

- accounting-complete flopscope RNG billing;
- production-shaped `1024 x 16` execution;
- exact frozen RNG billing delta;
- exact frozen total FLOP expectation;
- shape/finite/antithetic/marginal target-free checks.

**UNEXECUTED**

- raw final-layer MSE on competition/public data;
- adjusted score;
- official scorer;
- holdout/full;
- benchmark target evaluation.

## Decision

**E104 = ACCOUNTING-COMPLETE PRODUCTION-SHAPE GO ONLY.**

`scientific_go = false`.

This receipt does **not** authorize public/public-mini, official scorer, holdout/full, tuning, rerun, or a claim that the project accuracy target has been reached. The sole production-shaped accounting workflow has been consumed and E104 should remain sealed against rerun.
