# R298 — offline analyzer preparation for the frozen V25 residual capture

Status: **COMPLETE / ANALYZER_PREPARED_SYNTHETICALLY_VERIFIED_NO_REAL_CAPTURE**

Job: R298  
Owner: `r288-capture-analysis-prep-r269`  
Run: `R298-capture-analysis-prep-20260924`  
Isolated branch: `research/r298-capture-analysis-prep-20260924`  
Analyzer/test code commit: `95cd3175129a0cfba740e7a0249a3f1131bb0ffc`

## Scope and frozen sources

This task prepared only an offline standard-library analyzer. It did not touch PR #36,
inspect any real capture vectors, run an estimator/benchmark/Actions job, install or
download dependencies/data, access private/holdout/full data, spend money, submit, or
edit canonical/leaderboard state.

Pinned inputs read before implementation:

- R278 protocol commit `83dfbe710cad5fbb1cab6e5b6fce0ccd06d47966`,
  `research/r278/R278_PROTOCOL.md` blob
  `0ccc6b20fb4a8ad1c62a95d98dea4681970bb97d`.
- R288 capture-contract commit `cac87b0377674d3591b69f2b09db1873e8df9747`,
  `R288_CAPTURE_PROTOCOL_REPORT.md` blob
  `3b0d21fab8b668e22ae4d08022bfbf27452c8cb5`.
- R291 harness commit `54658e100314f398007e6ed7525550cc5db6706c`,
  `r291_capture_harness.py` blob
  `3e438c0f6b87ab2fa90c1fc71bbf3cfea1e9052d`.
- R291 expected-panel blob
  `caf813cd5eab771108f105fe050fd6631b298733`.
- R291 synthetic self-check blob
  `265688d5bd80dc05a0469cfdc3e6239ae5d3921d`.

The analyzer source SHA256 is
`916cbaf658009a9805d9f2bd1a6127a8c3a0db093440cb05d7a435dae264b3d4`;
its Git blob is `f1d5a9da7872ff6e632fef1e6c7dd2c90a6091ea`.
The R298 self-check SHA256 is
`84f7230eb2ed6cd8693a93aaf3147e14d29284a99f0d53f21efbb2fdbf6b449c`;
its Git blob is `e05443ffece962cf54c8b568c1536b60a2c071fb`.

## Analyzer contract

`research/r298/r298_capture_analyzer.py` requires a sealed capture directory and the
frozen R291 expected-panel JSON. The production CLI has no pin-override option.

Before fitting, it fails closed unless all of the following hold:

- `vectors.f32le` is exactly 1,228,800 bytes and its hash agrees with both
  `SHA256SUMS` and the manifest;
- `SHA256SUMS` contains exactly the two R291 entries for `vectors.f32le` and
  `manifest.json`;
- manifest schema/status/dtype/shape/axis order/residual sign/raw byte count and all
  pinned V25/evaluator/meter/dataset identities match the R291 contract;
- the supplied expected panel is exactly 100 rows with the frozen R288 dataset
  metadata/name-order hashes;
- scorer index, MLP name, decimal `network_id`, R224 target fingerprint and payload
  offset agree row-by-row with the expected panel;
- network IDs are unique and the manifest's FIT/EVAL role equals the frozen
  lexicographic decimal-string split, exactly 50/50;
- prediction/target/residual/record hashes verify and every stored residual is bitwise
  the R291 canonical binary32 `target-pred`;
- failure flags are internally consistent with `scored_prediction_zeroed`, and every
  flagged/errored row has an all-zero scored prediction.

Failure rows are retained in their frozen fold; nothing is dropped, repaired, reordered,
or reassigned after residual inspection.

## Frozen analysis rule

The analyzer implements only R278:

- FIT: `d = mean(target-pred)` across the 50 frozen FIT networks;
- EVAL: `p_corrected = p + d`;
- no alpha, rank, sign, selector, per-network scalar, feature, normalization, or
  network-specific tuning.

For EVAL it emits per-network baseline/corrected final-layer diagnostic MSE and paired
gain, plus baseline/corrected mean and median, paired mean gain, sample SD, descriptive
SE, improved count/fraction, and the exact four R278 materiality gates:

1. EVAL mean raw MSE improves by at least 2%;
2. at least 30/50 EVAL networks improve;
3. mean paired MSE gain is greater than 2 descriptive SE;
4. median EVAL raw MSE improves.

The output is explicitly labeled
`OFFLINE_DIAGNOSTIC_ONLY_NOT_OFFICIAL_ADJUSTED_SCORE`; it contains no leaderboard
rank inference.

## Pre-data numerical supplement

R278 froze the split and algebraic rule but did not specify floating-point accumulation
and rounding for the offline diagnostic. R288/R291 did specify canonical binary32
capture/failure semantics. R298 therefore freezes this deterministic supplement **before
any real capture is inspected** rather than selecting arithmetic after seeing results:

- decode canonical little-endian binary32;
- verify the stored residual as binary32 `target-pred`;
- each coordinate of `d` is
  `binary32(math.fsum(50 decoded FIT residuals) / 50)`;
- corrected prediction is binary32 `pred+d`;
- corrected residual is binary32 `target-corrected_pred`;
- per-network MSE is `math.fsum(decoded_binary32_residual**2) / 1024` in Python
  binary64;
- paired mean uses `math.fsum/n`; sample SD uses denominator `n-1`; SE is
  `SD/sqrt(n)`; median is the standard-library median.

This arithmetic defines only the offline R278 diagnostic. It is not asserted to be the
official WhestBench MSE/adjusted-score accumulation path.

## Offline self-check

Executed on the exact committed analyzer/self-check bytes with Python 3.13.5:

`python research/r298/r298_capture_analyzer_selfcheck.py`

Result: **PASS, 13/13 required checks**.

The temporary synthetic capture exercised the exact 100-row, 1024-wide serialized
layout while using synthetic values only. Checks passed for:

- valid sealed fixture and exact 50/50 split;
- frozen rule only and explicit offline-only labeling;
- a retained synthetic failure row;
- all four materiality gates on deliberately simple synthetic values;
- frozen production pin constants;
- rejection of bad `SHA256SUMS`;
- rejection of duplicate network IDs;
- rejection of split-role corruption;
- rejection of R224 target-fingerprint corruption;
- rejection of failure-flag/zeroing inconsistency;
- rejection of residual-byte corruption.

No real `vectors.f32le`, manifest, or future capture result was opened or analyzed.

## Disposition

**ANALYZER_PREPARED_SYNTHETICALLY_VERIFIED_NO_REAL_CAPTURE.**

A later authorized analysis can run this code only after a real R288/R291 capture exists
and can be supplied together with the frozen R291 expected panel. Any integrity mismatch
terminates before fitting. The resulting numbers remain an offline diagnostic unless a
separate authorized, honestly metered estimator evaluation establishes score impact.
