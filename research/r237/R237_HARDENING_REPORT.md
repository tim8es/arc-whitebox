# R237 verifier hardening report

Status: PASS
Role: verifier-hardening
Run ID: R237-r234-verifier-hardening-20260923

## Scope

R237 repaired the seven provenance/integrity defects confirmed by R236 in the prepared
R234 postflight verifier/checklist. Frozen R217 scientific thresholds and formulas are
unchanged. R218 workflow, executor, run, artifact, source and ownership are unchanged.
R220 remains the sole postflight owner after R218 completes.

R237 did not inspect or interpret the in-progress R218 artifact and did not trigger
GitHub Actions.

## Frozen scientific contract preserved

The hardened verifier still uses exactly:

- block sequence: U,C0,C1,C1,C0,U
- evaluations: 300
- primary delta: median_i(C0_mean_i - C1_mean_i)
- cpu0_slower_count: count_i(C0_mean_i > C1_mean_i)
- failure_difference: failures across two C0 blocks minus failures across two C1 blocks
- GO threshold primary_delta_s >= 0.020
- GO threshold cpu0_slower_count >= 35/50
- GO threshold failure_difference >= 10
- U comparisons remain descriptive only

No R217 metric or threshold was changed.

## Hardened artifacts

Verifier:
- path: research/r234/r234_verify_r218.py
- commit: 9e260d25d2f4ead1cbba1845de07e13aa6d7b9b2
- git blob: c5bdb49977550ff682b73c151807d9aeb8d18e98
- SHA256: d8ee7485606dd62b60b38abddf601b8ce1a5aad36c5255a0def962c4d22bcf7c

Checklist:
- path: research/r234/R234_VERIFIER_CHECKLIST.json
- commit: 0309c6c1c6aa0905cbfbcc4e6fa9f01b69e45302
- git blob: a17bdb292273049b292a52163dc1ee1fed7f7064
- SHA256: f811564789b439f5b5df9ed72df577f5a51748d8e8432cf7b4c85399ce2b475a

Regression suite:
- path: research/r237/test_r234_verifier_hardening.py
- commit: a1b7179a011eed858a8a14edeffa33073ba695eb
- git blob: 6e31aa9e48f55e6bbe23dc83f5e819b509096d72
- SHA256: f9a8efb6a4af357a744452a8ff46328f69bf87b4eb17357d29b34953b855ab0b

Regression result:
- path: research/r237/R237_SYNTHETIC_REGRESSION_RESULT.json
- commit: 546176a78f02e3459ba1edd4270fbbce5017ba76
- result: PASS_7_OF_7_HARDENING_REGRESSION_CATEGORIES

## R236 defects and repairs

| Defect | Repair |
|---|---|
| D1 attempt fail-open | External evidence and artifact preflight must both have GITHUB_RUN_ATTEMPT exactly 1. Attempt 2 is invalid even if both values match. |
| D2 artifact/source binding | R220 must provide original downloaded Actions ZIP plus independent run/job evidence. Verifier hashes ZIP, byte-compares ZIP contents to artifact-dir, requires positive artifact ID, exact artifact name, ZIP SHA256, run ID, job ID/name, frozen head SHA, arm commit/blob/SHA, parent executor commit, one-file arm diff proof, workflow blob, executor blob and estimator hash. |
| D3 unpinned panel | --expected-panel and artifact panel copy must match frozen SHA256 c09fdfb867fbb20ea1bea7e7334b3592d9fb5996a02419a0488d622413dbf9b6; external evidence also requires frozen panel blob 8669ffff.... |
| D4 incomplete manifest | sha256.json must be nonempty and its key set must exactly equal every other file in artifact-dir; every listed digest must match. Empty, missing or extra coverage is invalid. |
| D5 weak preflight provenance | Artifact prelaunch copy is pinned to SHA256 e7ca2c1ff2449ff4c9bd393969f63fbd7416e1d62209fa1b6a16687aae819cd9. Preflight gate-name set must exactly equal the frozen executor set and every value must be true. Local Python/whest evidence is checked and R220 external evidence must independently verify Python 3.11.16, NumPy 2.4.6, flopscope 0.12.1 and whestbench 0.16.1. |
| D6 dataset/max_threads omission | Every block now requires exact dataset path and SHA plus max_threads=1, in addition to existing budget/residual/shape/version gates. |
| D7 incomplete telemetry | Verifier now requires all preflight and per-block mandatory telemetry, validates orchestrator and child taskset plus /proc CPU sets, requires per-block lscpu identity to match preflight, and requires recorded worker name plus Azure region to match external evidence. |

A supplied but invalid Actions evidence file now yields PROTOCOL_INVALID. Only total absence
of external evidence yields PENDING_EXTERNAL_ACTIONS_PROVENANCE after all artifact-local
gates pass.

## External R220 binding contract

For a causal GO/NO-GO, R220 must independently establish:

- run_attempt = 1
- one successful crossover job
- artifact ID and exact name r218-v29-l4-affinity-crossover
- SHA256 of the independently downloaded artifact ZIP
- artifact run ID
- frozen Actions head c8cb97dcd1383f4a1d741c5a36ba816deec452eb
- arm blob 542f8f80cee29c83b4f9648a1c56f49ae9b9262a and arm SHA256 2c4c430c8ec8f0abcdbd84192f8c9040485804e65ca7adab3505dbf9c222cb54
- arm parent executor commit 85f5ba13236aad07bf31436b356cfa2a3744ad33
- proof that the arm-head diff adds only research/R218_RUN_ARM.json
- workflow blob d1fa366b1056d09f829a9620eda81034584147af
- executor blob 456364bd0558eb98d41a4f9cd0512484fe972d20
- expected-panel blob 8669ffff7408c4f251c700ca0d5f9fc24db5c8f0
- prelaunch blob fe0745d3d0265b7afb8d952530998c6b0f942aa3
- estimator SHA256 86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27
- exact independent environment versions
- runner name and region matching artifact telemetry

The actual frozen arm ancestry was not changed by R237.

## Synthetic fail-closed regression

A committed unittest suite covers D1-D7 with synthetic temporary directories and ZIPs.
No R218 scientific files are used.

An offline helper-predicate execution in this session passed all seven categories:

1. matching attempt 2 is rejected;
2. artifact/source binding mutations are rejected;
3. modified panel/prelaunch content cannot satisfy frozen pins;
4. empty or incomplete manifest is rejected;
5. missing/extra preflight keys and version drift are rejected;
6. wrong dataset path or max_threads is rejected;
7. missing mandatory telemetry is rejected.

Execution used local Python 3.13.5 only for synthetic verifier predicates. It did not
execute whest, estimator code or Actions.

## Source links

R236 defect receipt:
https://github.com/tim8es/arc-whitebox/blob/6313780c7975b866267612ae1e2798c5a2f3d54b/research/r236/R236_RECEIPT.json

Hardened verifier:
https://github.com/tim8es/arc-whitebox/blob/9e260d25d2f4ead1cbba1845de07e13aa6d7b9b2/research/r234/r234_verify_r218.py

Hardened checklist:
https://github.com/tim8es/arc-whitebox/blob/0309c6c1c6aa0905cbfbcc4e6fa9f01b69e45302/research/r234/R234_VERIFIER_CHECKLIST.json

Regression suite:
https://github.com/tim8es/arc-whitebox/blob/a1b7179a011eed858a8a14edeffa33073ba695eb/research/r237/test_r234_verifier_hardening.py

Frozen R217 protocol:
https://github.com/tim8es/arc-whitebox/blob/e8fc0364f69c12f2f94a06362b43e925ea61b365/research/r217/R217_NEXT_RUNTIME_PROTOCOL.json

Pinned R218 workflow:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/.github/workflows/r218-affinity-crossover.yml

Pinned R218 executor:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/scripts/r218_run_crossover.py

## Verdict

PASS.

R236 D1-D7 are closed in the prepared verifier/checklist and covered by synthetic
fail-closed regressions. This PASS is only a tooling-hardening verdict. It makes no claim
about the unfinished R218 scientific outcome.

R220 must still independently obtain the completed Actions/artifact evidence and run the
hardened verifier after R218 completes.

## Scope confirmation

No R218 artifact was opened, downloaded or interpreted. No R217/R218 source, workflow,
executor, run or artifact was changed. No Actions run was triggered. No estimator/science
run, paid compute, private/holdout access, submission or canonical estimator edit occurred.
