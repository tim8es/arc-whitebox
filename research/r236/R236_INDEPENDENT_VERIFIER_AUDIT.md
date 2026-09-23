# R236 independent audit of the R234 R218 postflight verifier

Status: DEFECT
Role: independent-verifier-audit
Run ID: R236-r234-verifier-independent-audit-20260923

## Scope

This review audits only the prepared R234 verifier/checklist against frozen R217 and
pinned R218 source/tooling. It does not inspect, download, parse, or interpret the
unfinished R218 scientific artifact.

No estimator or scientific run was performed. No Actions workflow was triggered.

## Frozen source identities

| Source | Frozen identity |
|---|---|
| R234 verifier | research/r234/r234_verify_r218.py, blob 772843d4bc2b5929e851e621f33dd25a38cd5319, latest R234 commit 0a4ddaa499199c88213eb2b13336d2649bff5ef8 |
| R234 checklist | research/r234/R234_VERIFIER_CHECKLIST.json, blob 610c71426f262c08a4c7390f9bb089aacb0c62da, latest R234 commit 5dc06399db5a59ce63646f6a9eff023450310075 |
| R217 protocol | research/r217/R217_NEXT_RUNTIME_PROTOCOL.json at e8fc0364f69c12f2f94a06362b43e925ea61b365, blob a940706931d280fe2a720836d9db248146862270, SHA256 40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968 |
| R218 workflow | .github/workflows/r218-affinity-crossover.yml at 85f5ba13236aad07bf31436b356cfa2a3744ad33, blob d1fa366b1056d09f829a9620eda81034584147af |
| R218 executor | scripts/r218_run_crossover.py at 85f5ba13236aad07bf31436b356cfa2a3744ad33, blob 456364bd0558eb98d41a4f9cd0512484fe972d20 |
| R218 expected panel | research/r218/R218_EXPECTED_PANEL.json at 85f5ba13236aad07bf31436b356cfa2a3744ad33, blob 8669ffff7408c4f251c700ca0d5f9fc24db5c8f0 |
| R218 prelaunch | research/r218/R218_PRELAUNCH_GATE.json at 85f5ba13236aad07bf31436b356cfa2a3744ad33, blob fe0745d3d0265b7afb8d952530998c6b0f942aa3 |
| R218 arm | research/R218_RUN_ARM.json on arm head c8cb97dcd1383f4a1d741c5a36ba816deec452eb, blob 542f8f80cee29c83b4f9648a1c56f49ae9b9262a |

The current pinned arm head is exactly one commit above executor commit
85f5ba13236aad07bf31436b356cfa2a3744ad33 and that one-commit diff adds only
research/R218_RUN_ARM.json. That source ancestry is clean. The defect below is that the
prepared verifier/evidence schema does not require R220 to prove this relationship.

## What R234 gets right

The quantitative analysis is faithful to R217:

| Item | R217 | R234 verifier |
|---|---|---|
| block order | U,C0,C1,C1,C0,U | exact match |
| evaluations | 300 | requires 6 x 50 and exact_300_rows |
| per-MLP primary | mean of two C0 minus mean of two C1 | exact match |
| primary aggregate | median_i(C0_mean_i-C1_mean_i) | exact match |
| CPU0 slower count | count_i(C0_mean_i>C1_mean_i) | exact match |
| failure difference | failures(C0 two blocks)-failures(C1 two blocks) | exact match |
| GO delta | >=0.020 s | exact match |
| GO slower count | >=35/50 | exact match |
| GO failure difference | >=10 | exact match |
| U comparisons | descriptive only | preserved as secondary |

The verifier also correctly withholds GO/NO-GO when no external Actions evidence is
supplied, checks the six raw report files rather than trusting the owner summary, checks
child C0/C1/U affinity, and compares stable lscpu identity across blocks.

No metric or threshold drift was found.

## Defects

| ID | Severity | Fail-open path | Evidence / consequence |
|---|---|---|---|
| R236-D1 | HIGH | External Actions evidence accepts a rerun attempt as long as it equals artifact preflight. It never requires run_attempt == 1. | R217 says one six-block job only, no retry/rescue; R218 arm says attempt=1 and attempts_allowed=1. Synthetic predicate with both sides set to attempt 2 returns actions_ok=true. |
| R236-D2 | HIGH | The local artifact is not cryptographically bound to the independently inspected Actions run. actions-evidence contains run/job/source strings but no artifact ID/name/digest, workflow head SHA, arm commit/blob, workflow blob, or executor blob at checkout head. | A locally substituted artifact can self-report the same run_id/attempt. The verifier then has no machine-enforced proof that artifact-dir came from that run. The checklist text asks R220 to inspect run/job, but its evidence schema cannot express the required binding. |
| R236-D3 | HIGH | Expected-panel provenance is not pinned in code. --expected-panel is accepted if it has 50 indices plus the known dataset/source hashes; artifact expected-panel is only compared to that caller-supplied file. | The frozen expected-panel blob 8669ffff... is listed in the checklist but never enforced. A paired modified expected-panel plus matching reports can redefine names/FLOPs while all verifier expected-panel gates pass. Synthetic predicate confirms this. |
| R236-D4 | HIGH | sha256.json completeness is not checked. An existing empty manifest passes artifact_manifest because the verifier validates only entries that happen to be listed. Consumed files are not required to appear in the manifest. | Synthetic predicate with manifest={} returns pass. This defeats the stated manifest-integrity gate unless R220 separately binds the extracted directory to the immutable GitHub artifact digest. |
| R236-D5 | MEDIUM | Frozen prelaunch provenance and required preflight gate names are not enforced. The artifact prelaunch copy is not checked against blob fe0745d3..., and preflight_all_named_gates_true accepts any non-empty all-true map. | Synthetic predicate with {"unrelated": true} passes the named-gates predicate. The verifier also does not independently enforce the raw Python/NumPy/flopscope version fields; it mostly relies on owner-generated gate booleans plus whestbench report version. |
| R236-D6 | MEDIUM | Per-block dataset path is not checked, even though the pinned R218 executor treats dataset_path as a runtime contract gate and the R234 checklist explicitly says require dataset SHA/path. | r234_verify_r218.py checks ds.sha256 but omits ds.path == hf://aicrowd/arc-whestbench-public-2026@v2-phase2. |
| R236-D7 | MEDIUM | Mandatory instrumentation can be missing without invalidating artifact_contract_ok. | R217 requires lscpu, /proc/cpuinfo, /proc/self/status, sched affinity/taskset and worker ID/region telemetry. R234 checks per-block lscpu, orchestrator affinity and child taskset, but not per-block proc_cpuinfo, orchestrator/child proc status, taskset_orchestrator, or worker-region evidence. The external evidence schema likewise has no runner-name/region gate. |

A related source-provenance weakness is that actions_evidence.executor_commit is merely a
JSON value checked for equality. The workflow checks out the Actions head and runs the
script from that checkout. The verifier should require the observed Actions head/arm
commit and prove that its workflow/executor blobs equal the pinned blobs (or prove the
arm-head diff from executor commit contains only the arm file). The actual pinned arm
currently satisfies that ancestry, but the verifier does not enforce it.

## Synthetic fail-closed check

A small offline predicate test was executed without R218 data or Actions.

Artifact:
- research/r236/r236_fail_closed_synthetic.py
- commit 7534164e2e7d6fbfb2d5dff4e508cb115f46a0a4
- blob 34ddcea39a6a56f1598c38a4f10362d9b7077ab7

Result:
- empty manifest accepted: true
- unpinned synthetic expected panel accepted by the relevant predicates: true
- run_attempt=2 accepted by external provenance predicate: true
- incomplete all-true preflight gate map accepted: true

Result record:
research/r236/R236_SYNTHETIC_FAIL_CLOSED_RESULT.json
commit feb3ee2a7b37d5cb189581c55d66b053bd432b9f

This test reproduces only source predicates. It does not synthesize or inspect scientific
measurements and does not claim anything about the unfinished R218 outcome.

## Required repair before using R234 tooling for an authoritative R220 verdict

| Repair | Minimum fail-closed requirement |
|---|---|
| Rerun policy | require GITHUB_RUN_ATTEMPT == 1 and arm attempt/attempts_allowed == 1; reject any rerun/rescue |
| Artifact binding | external evidence must include run ID, job ID/name, artifact ID/name and GitHub artifact digest/download digest; bind artifact-dir materialization to that artifact |
| Checkout/source binding | record Actions head SHA; verify arm blob; verify workflow and executor blobs at that head, or prove head is the one-file arm commit above pinned executor |
| Expected panel | pin exact expected-panel git blob or SHA256 in verifier and require both external frozen file and artifact copy to match it |
| Manifest | require exact/complete manifest coverage for every artifact file consumed by verifier, not merely hashes of listed entries |
| Prelaunch/preflight | pin exact prelaunch blob; require the complete frozen gate-name set and independent version/source evidence where available |
| Runtime contract | add dataset path and max_threads=1 checks where report schema exposes them |
| Instrumentation | require mandatory /proc/taskset/affinity files and explicitly classify missing worker/region telemetry as protocol-invalid or a predeclared documented exception |

## Verdict

DEFECT.

R234 is directionally sound and its quantitative thresholds are frozen correctly, but it
is not yet fail-closed enough to serve as the authoritative R220 postflight verifier. The
defects are provenance/integrity defects, not evidence about the R218 scientific result.

R220 remains the authoritative audit after R218 completes. It should not issue a causal
GO/NO-GO using the current R234 verifier unless the fail-open provenance paths above are
repaired or independently closed by stricter R220 checks.

## Source links

R234 verifier:
https://github.com/tim8es/arc-whitebox/blob/0a4ddaa499199c88213eb2b13336d2649bff5ef8/research/r234/r234_verify_r218.py

R234 checklist:
https://github.com/tim8es/arc-whitebox/blob/5dc06399db5a59ce63646f6a9eff023450310075/research/r234/R234_VERIFIER_CHECKLIST.json

Frozen R217 protocol:
https://github.com/tim8es/arc-whitebox/blob/e8fc0364f69c12f2f94a06362b43e925ea61b365/research/r217/R217_NEXT_RUNTIME_PROTOCOL.json

Pinned R218 workflow:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/.github/workflows/r218-affinity-crossover.yml

Pinned R218 executor:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/scripts/r218_run_crossover.py

Pinned R218 expected panel:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/research/r218/R218_EXPECTED_PANEL.json

Pinned R218 prelaunch:
https://github.com/tim8es/arc-whitebox/blob/85f5ba13236aad07bf31436b356cfa2a3744ad33/research/r218/R218_PRELAUNCH_GATE.json

Pinned arm head:
https://github.com/tim8es/arc-whitebox/commit/c8cb97dcd1383f4a1d741c5a36ba816deec452eb

## Scope confirmation

No R218 artifact was inspected or interpreted. No private/holdout data was accessed. No
R218 source or workflow was changed. No Actions run was triggered. No estimator/science
run, paid compute, submission, or canonical edit occurred.
