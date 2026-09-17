# E094 result — terminal NO-GO at frozen official-shape spectrum probe

## Provenance

- Branch: `research/e094-source-axis-joint-compression-20260917`.
- Stage-A implementation/head before spectrum work: `9d4233c552ff6666967da2af4cbf74df186c04f1`.
- Stage-A run/job/artifact: `35159208262 / 105005774984 / 10472306249`.
- Stage-A artifact SHA256: `7850bd96bee03fee0ebfa96913da5f6713401c67fcbdca298726ddee2edd4bde`.
- Stage-A decision: `STAGE_A_GO`.
- Spectrum freeze commit: `c0980b53dfdf48ad6436ef01ebe8fc977049839a`.
- Spectrum implementation commit: `c4732e142b6485d21f8c5128d5161ebce4481e21`.
- Spectrum workflow commit: `a75572717557ded5dda8cefb13d23536b55115d9`.

## Stage-A evidence

The exact source-metric representation passed its frozen algebra/truncation gates:

- exact transport max abs: `8.881784197001252e-16`;
- exact hub max abs: `3.552713678800501e-15`;
- exact hub relative Frobenius: `7.283476736942065e-16`;
- source metric rank: `3`;
- required symmetric remaining source-heavy fraction for the measured V29 cost model:
  `0.452481568063298`.

This justified exactly one target-free official-shape source-spectrum probe.

## Frozen spectrum probe

Frozen before execution:

- exact upstream V29 commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- exact estimator blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- width/depth `1024 / 16`;
- PCG64 network seed `94194`;
- every dense weight iid `N(0,1/1024)`, float32;
- no targets/public/scorer/holdout/full data;
- finite exact-V29 prediction was a mandatory gate;
- source spectra would be read only at the unique non-trim state with `k=14`.

Execution:

- workflow run: `35286347862`;
- job: `105419433633`;
- conclusion: `failure`.

The failure occurred in the **uninstrumented baseline V29 run**, before the spectrum wrapper or any source-axis capture was reached.

Observed runtime warnings:

- overflow in multiply inside flopscope;
- invalid value in add.

Terminal traceback:

`Estimator.predict -> _predict_core -> flops.as_symmetric(C, symmetry=(0,1))`

raised

`flopscope.errors.SymmetryError: Tensor not symmetric ... max deviation = nan`

at upstream V29 line 1405.

The artifact upload also failed because the process terminated before
`e094-spectrum-probe.json` could be written; therefore this run has no artifact ID.
The GitHub Actions job log is the immutable execution evidence.

## Decision

**E094 = TERMINAL NO-GO / DROP.**

Reason: the frozen spectrum probe required a finite exact-V29 trajectory on the preregistered
synthetic official-shape network. The exact baseline became non-finite before the measurement
state existed. This is a scientific frozen-gate failure, not a source-spectrum measurement.

No seed replacement, weight-distribution change, precision change, clipping, jitter, rescue,
second spectrum run, public diagnostic, scorer, holdout/full evaluation, canonical mutation,
ledger mutation, or merge is permitted under E094.

An automatically triggered repeat of the old Stage-A workflow on the spectrum-workflow push is
not a new scientific experiment and is not used as evidence.

No claim about real V29 source-axis rank is made because the frozen probe never reached the
capture state.
