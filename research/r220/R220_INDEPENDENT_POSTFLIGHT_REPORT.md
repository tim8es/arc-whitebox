# R220 independent postflight of R218

Status: **PROTOCOL_INVALID / INCONCLUSIVE**.

This audit is read-only. It did not rerun GitHub Actions, execute the estimator, access private/holdout data, submit, or modify canonical estimators/results.

## Queue and audit order

R220 was claimed at queue revision 160 and started at revision 161 before R218 evidence was inspected.

Before inspecting the R218 artifact, the R237 hardened offline synthetic suite was reconstructed from its pinned sources and run fresh:

- hardened verifier commit: `9e260d25d2f4ead1cbba1845de07e13aa6d7b9b2`
- hardened verifier SHA256: `d8ee7485606dd62b60b38abddf601b8ce1a5aad36c5255a0def962c4d22bcf7c`
- R237 suite commit: `a1b7179a011eed858a8a14edeffa33073ba695eb`
- suite SHA256: `f9a8efb6a4af357a744452a8ff46328f69bf87b4eb17357d29b34953b855ab0b`
- fresh result: **7/7 tests passed, exit 0**
- fresh stderr SHA256: `eef489d4b3e2ef00ae0a1050184430cd24acd67681cd1fbd2ebf06443372bcbb`

Sources: [R237 verifier](https://github.com/tim8es/arc-whitebox/blob/9e260d25d2f4ead1cbba1845de07e13aa6d7b9b2/research/r234/r234_verify_r218.py), [R237 suite](https://github.com/tim8es/arc-whitebox/blob/a1b7179a011eed858a8a14edeffa33073ba695eb/research/r237/test_r234_verifier_hardening.py), [R236 defect receipt](https://github.com/tim8es/arc-whitebox/blob/6313780c7975b866267612ae1e2798c5a2f3d54b/research/r236/R236_RECEIPT.json).

## Independent Actions and artifact provenance

Validated against GitHub Actions APIs, job logs, frozen repository objects, the independently downloaded ZIP, and the extracted artifact:

- run: [35783866968](https://github.com/tim8es/arc-whitebox/actions/runs/35783866968), attempt **1**, conclusion **success**
- job: [106935773981](https://github.com/tim8es/arc-whitebox/actions/runs/35783866968/job/106935773981), the sole job, name `crossover`, conclusion **success**
- head SHA: `c8cb97dcd1383f4a1d741c5a36ba816deec452eb`
- job API runner: id `1000005102`, name `GitHub Actions 1000005102`, label `ubuntu-24.04`
- job logs: worker ID `1afa6f87-fdc3-4e38-9eac-960fa4024f10`, Azure region `westus`
- artifact: `10726329197`, name `r218-v29-l4-affinity-crossover`, bound to the same run/head
- downloaded ZIP SHA256: `c70603fc45e40da9e03b926acf6656cf654c26d8046ea7cc8e808bd208f8cea0`, equal to the Actions artifact digest
- extracted files: 85 total; `sha256.json` contains exactly 84 entries for the other 84 files; file-set equality **true**, hash mismatches **0**

The Actions checkout log independently records checkout of `c8cb97d...`. The head is exactly one commit above executor commit `85f5ba13236aad07bf31436b356cfa2a3744ad33`, and the only diff is `research/R218_RUN_ARM.json`.

Frozen source bindings:

- arm blob `542f8f80cee29c83b4f9648a1c56f49ae9b9262a`, SHA256 `2c4c430c8ec8f0abcdbd84192f8c9040485804e65ca7adab3505dbf9c222cb54`
- workflow blob `d1fa366b1056d09f829a9620eda81034584147af`
- executor blob `456364bd0558eb98d41a4f9cd0512484fe972d20`
- expected-panel blob `8669ffff7408c4f251c700ca0d5f9fc24db5c8f0`, SHA256 `c09fdfb867fbb20ea1bea7e7334b3592d9fb5996a02419a0488d622413dbf9b6`
- prelaunch blob `fe0745d3d0265b7afb8d952530998c6b0f942aa3`, SHA256 `e7ca2c1ff2449ff4c9bd393969f63fbd7416e1d62209fa1b6a16687aae819cd9`
- R217 protocol SHA256 `40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968`
- upstream V29 estimator blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, SHA256 `86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27`

Sources: [arm head](https://github.com/tim8es/arc-whitebox/commit/c8cb97dcd1383f4a1d741c5a36ba816deec452eb), [executor commit](https://github.com/tim8es/arc-whitebox/commit/85f5ba13236aad07bf31436b356cfa2a3744ad33), [workflow](https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/.github/workflows/r218-affinity-crossover.yml), [executor](https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/scripts/r218_run_crossover.py), [expected panel](https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/research/r218/R218_EXPECTED_PANEL.json), [prelaunch gate](https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/research/r218/R218_PRELAUNCH_GATE.json), [upstream estimator](https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v29.py).

## R236 D1-D7

| Gate | Independent R220 result | Evidence |
|---|---|---|
| D1 attempt exactly 1 | PASS | run API, job API, artifact preflight and frozen arm all say attempt 1; no rerun |
| D2 artifact/source cryptographic binding | PASS | exact artifact ID/name/run/head and downloaded ZIP digest; head→executor ancestry and frozen blobs verified |
| D3 exact expected-panel pin | PASS | artifact copy SHA256 equals frozen `c09fdf...`; exact 50 names/order/FLOPs pass |
| D4 complete non-empty manifest | PASS | 84/84 entries exactly cover every non-manifest artifact file; 0 hash mismatches |
| D5 exact preflight gates/versions | PASS | frozen prelaunch SHA; exact required gate-name set and all true; Python 3.11.16, NumPy 2.4.6, flopscope 0.12.1, whestbench 0.16.1 corroborated by workflow/logs/artifact |
| D6 dataset path / max_threads | **FAIL** | dataset path/hash pass. However all six raw block reports omit `run_config.max_threads`; hardened R237 verifier therefore fails `block_01_max_threads` through `block_06_max_threads`. |
| D7 mandatory telemetry / worker-region | PASS | all mandatory telemetry files and affinity checks pass; stable lscpu identity; Actions job/runner and `westus` region corroborate artifact telemetry |

Important D6 boundary: every immutable `block_*_command.json` contains `--max-threads 1`, the workflow/executor also request `--max-threads 1`, and thread environment is pinned to 1. That does **not** satisfy the frozen R237 per-block report gate because `max_threads` is absent from every report's `run_config`. This audit does not substitute command intent for the required recorded field and does not relax the gate.

The hardened verifier evaluated **289 gates**: 283 pass and exactly six fail, all six being the per-block `max_threads` gates. External Actions/artifact/source provenance as a whole passed.

## Independent six-block recomputation

Artifact block sequence is exactly `U,C0,C1,C1,C0,U`, 50 rows per block, 300 rows total. Exact expected names/order and FLOP vector pass on all blocks.

| block | condition | failures | mean residual s | median residual s | adjusted score |
|---:|:---:|---:|---:|---:|---:|
| 1 | U | 9 | 0.384841146 | 0.362868356 | 0.162872070 |
| 2 | C0 | 6 | 0.380882954 | 0.367419908 | 0.111500640 |
| 3 | C1 | 7 | 0.388836228 | 0.373056124 | 0.144417595 |
| 4 | C1 | 30 | 0.443798830 | 0.428173742 | 0.566417117 |
| 5 | C0 | 46 | 0.517117979 | 0.520876313 | 0.845975411 |
| 6 | U | 10 | 0.384448425 | 0.363878795 | 0.196651051 |

Paired condition summaries over two blocks each:

- C0 failures: **52/100**; mean residual `0.449000466 s`
- C1 failures: **37/100**; mean residual `0.416317529 s`
- U failures: **19/100**; mean residual `0.384644786 s`

Frozen R217 primary thresholds recompute to:

- `primary_delta_s = median_i(C0_mean_i - C1_mean_i) = 0.04774312495 s` → passes `>=0.020`
- `cpu0_slower_count = 32/50` → **fails** `>=35/50`
- `failure_difference = 52 - 37 = 15` → passes `>=10`

If every contract/provenance gate had passed, the threshold-only branch would be `NO_GO_CPU0_SPECIFIC` because 32/50 misses the frozen 35/50 threshold. Under the actual hardened protocol, D6 fails, so R217's higher-priority rule applies: **PROTOCOL_INVALID; do not interpret runtime causally**.

## Final independent conclusion

**PROTOCOL_INVALID / INCONCLUSIVE.**

The artifact strongly supports the numerical recomputation and independently verifies almost all provenance, integrity, panel, FLOP and telemetry requirements. But R237's frozen fail-closed D6 requires per-block `run_config.max_threads == 1`; that field is absent in all six immutable reports. Therefore R220 cannot ratify the owner's `NO_GO_CPU0_SPECIFIC` as an independent causal verdict.

No rerun/rescue is authorized or requested by this audit. The exact evidence gap is recorded rather than repaired post hoc.
