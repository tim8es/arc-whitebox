# R243 independent audit of R223 normalized registry integration

## Scope

R243 audits only the terminal R242 normalization of the immutable R223 attempt-6 result. It does not edit R242's record, execute an estimator/benchmark/Actions job, repair/retry R223, access private/holdout data, spend paid compute, submit, or mutate leaderboard/canonical candidates.

Frozen prep: `research/r243/R243_PREP_CHECKLIST.json` at `bb646a9ff9ccdf21bbc760ab8260b9994c7559e4`.

## Immutable sources

- R223 artifact: GitHub Actions artifact `10730459690`, `r223-v25-local-feed-mini100-attempt6`, ZIP SHA256 `f144bfd2a5a8a82aaa3e600d1f384d68cfe5e525eb7e22e91eb1d7e843763e00`.
- Artifact manifest: 23 entries / 23 files, no missing, extra, or hash mismatches; manifest SHA256 `4cfa68492df10aa860dd2aa701cf87a33c63f9c0beac470802bc24082f10da5b`.
- Artifact `candidate-report.json` SHA256 `72821cf9117b484b2cc4fe4affa21e08ece737e86813508d9c1c6d01b02f6710`.
- Artifact `R223_ATTEMPT6_RESULT.json` SHA256 `52c5da262f442d3a499c2c77885abc91f81d596e10703c1ac582192ffc8dda65`.
- R240 receipt: commit `3b99fcaea2ef29b050612610ff04a8fc7a6886cd`, SHA256 `e75ec5e2641df59887cf38520e9d9f3a449731fa5fcac481398433c4c4ac8bbd`.
- R209 parent normalized record: `research/results/R209-v25-mini100.json`, SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.
- R242 normalized record: `research/results/R223-v25-local-feed-mini100.json` at `b55b9ab2e3dd7ff58ea405704e8f63e86112d48d`; Git blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`; SHA256 `3c8633826ac2efb74db73ba7f5640ec34f0ebb8c91c517f0cf418b6794184587`.
- R242 integration receipt: `research/r242/R242_INTEGRATION_RECEIPT.json` at `b55b9ab2e3dd7ff58ea405704e8f63e86112d48d`; SHA256 independently recomputed as `c4ba58c73ceb0956fc284c9865a62220649a04f7354069dd1e91c3094ee9c200`.

## Row-by-row verification

All 100 normalized rows were checked in exact index order.

- Names/order: 100/100 exact against the immutable candidate report and R209 panel; 0 mismatches.
- `network_id`: 100/100 exact against authenticated R209; 0 mismatches.
- `target_sha256`: 100/100 exact against authenticated R209; 0 mismatches.
- Panel metadata: exact JSON equality to R209 for count, dataset, dtype, evaluator, meter, revision, shape, split, and stage.
- Candidate MSE/FLOPs/status/official adjusted score: 100/100 exact against the immutable artifact. An independent IEEE-754 projection over index/name/final-MSE/FLOPs/status/adjusted-score hashes to `f89ac0172aec3a8e37c0553e5f20bbddbba6bc39c6e153c570725c653ce593f1` for both artifact rows and committed normalized rows.
- Failures: artifact has 0/100; normalized record has 0/100 and all `failure_reasons` arrays are empty.
- Official scoring formula: 100/100 satisfy `final_mse * max(0.1, measured_flops / 2**41)`; 0 mismatches. Artifact report, owner recomputation, and normalized score agree row by row.
- Parent link: exact `parent_id = R209-v25-mini100`.
- Source binding: artifact ID `10730459690`, artifact ZIP digest, R240 receipt commit, and dataset metadata are preserved.

Independent aggregate recomputation from artifact rows gives mean raw MSE `2.2284993050902814e-8`, mean adjusted score `8.171116513490029e-9`, mean measured FLOPs `806303829485`, and 0 failures. The committed normalized record gives the same MSE/FLOPs/failure totals; its floating summation of adjusted scores is `8.171116513490032e-9`, a representation-order rounding difference only.

## Scientific status and STATUS

R242 preserves `development_verdict = SCIENTIFIC_REJECT` and `development_decision = R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED`. Authoritative control has R223 terminal `SCIENTIFIC_REJECT`; R240 independently concluded `R240_INDEPENDENT_DEVELOPMENT_NO_GO`. R243 does not reinterpret that result.

Current generated STATUS contains the normalized R223 row (100 rows, 0 failures, adjusted score `8.1711165e-09`), the comparison to R209 V25 (`1.000088`, 50/100 improved), and R242 marked COMPLETE.

## Verdict

**PASS — R242 registry integration is row-for-row consistent with immutable artifact 10730459690, authenticated R209 panel identity, R240 evidence, its own receipt, and the preserved R223 SCIENTIFIC_REJECT status.**

This is an integrity verdict on registry integration only, not a new scientific run or competition/holdout claim.
