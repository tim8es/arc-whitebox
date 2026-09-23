# R257 terminal report — repaired BPK2K one-shot

Status: **INFRA_ERROR before science; no retry**

## Frozen control

- run ID: `R257-BPK2K-ONE-SHOT-20260923-A1`
- protocol commit: `b63936a38bc0e3a6394b00f2ef1d484311aff9e4`
- workflow commit: `187bc8f9ca459a96af1f7cf0d014bc906b278a2a`
- arm commit: `47d082eca6d70bed44c3d4346e15672efc09f333`
- branch: `research/r257-bpk2k-repaired-one-shot-20260923`
- exact R256 receipt base: `f1e458952f2274ca375f97125ba3d181c494ad40`

The workflow was path-filtered to the arm file. Before arming, the branch had zero R257
Actions runs. The arm commit triggered exactly one workflow and one attempt.

## Sole Actions execution

- GitHub Actions run: `35838865448`
- job: `107108851475`
- attempt: `1`
- workflow: `.github/workflows/r257-one-shot.yml`
- head: `47d082eca6d70bed44c3d4346e15672efc09f333`
- runner: standard GitHub-hosted `ubuntu-24.04`
- workflow conclusion: **failure**
- artifact: `10740567074`, `r257-one-shot-evidence`
- artifact ZIP SHA256:
  `e33cdfe28cc74f6ece1896a62fefe5e221fec67ff3c7c1f928aeac50434db24a`

Exactly one R257 Actions run exists. No rerun or second workflow was dispatched.

## Exact infrastructure failure

The first substantive guard step,
`Verify frozen ancestry and source identities`, ran under the default shallow
`actions/checkout@v4` checkout.

Its first command was:

`git merge-base --is-ancestor b63936a38bc0e3a6394b00f2ef1d484311aff9e4 HEAD`

The checkout had fetched only the arm head. The protocol ancestor was not present in the
local shallow repository. Git emitted exactly:

`fatal: Not a valid commit name b63936a38bc0e3a6394b00f2ef1d484311aff9e4`

and the step exited `128`.

This is an R257 workflow ancestry-guard/bootstrap defect. It is not evidence about
BPK2K accuracy, cost, timing, source compliance, fixture behavior, or public behavior.

## What did and did not execute

Executed:
- checkout;
- immutable run metadata initialization;
- the ancestry/source-identity step up to its first failing command;
- always-run workflow receipt/hash construction;
- artifact upload.

Skipped:
- setup-python;
- pinned wheel download/hash verification/install;
- runtime version checks;
- pinned V25 parent fetch;
- fixture reconstruction/replay;
- parent estimator execution;
- BPK2K candidate construction;
- BPK2K candidate execution;
- target-free MSE/FLOP/timing gates;
- candidate validation;
- exact R209 public identity access;
- public mini-100;
- public gates.

Because `set -euo pipefail` stopped the source-identity step at its first command,
the later Git-blob/SHA256 checks in that step were not executed. Source identities are
therefore frozen by protocol but **not runtime-verified by R257**.

## Scientific accounting

- parent executions: **0**
- candidate constructions: **0**
- candidate executions: **0**
- persisted target-free measurements: **0**
- persisted public measurements: **0**
- target-free result: absent
- public report: absent
- per-network public evidence: absent because the public stage was never authorized/reached

Scientific status: **UNEVALUATED**.

No numeric claim about BPK2K MSE, FLOPs, residual time, public score, improved rows, SE,
or rank is made from R257.

## Artifact integrity

The downloaded artifact independently hashes to the GitHub-reported ZIP digest above.
It contains exactly seven files:
- `R257_WORKFLOW_RECEIPT.json`
- `R257_ARTIFACT_HASHES.json`
- `github_run_attempt.txt`
- `github_run_id.txt`
- `image_os.txt`
- `runner_os.txt`
- `workflow_head_sha.txt`

The workflow receipt SHA256 is
`99c55aae415cb88de917db6ed771748f33a720fcbf6d905efd005039a0a3186d`.
The artifact hash-map SHA256 is
`86f4b01fad2f49a0e8dcfc540b010cc13cced5b416d64c688914a69664d47bdf`.

The workflow receipt decision is
`INFRA_ERROR_BEFORE_TARGET_FREE_RESULT`.

## Terminal disposition

R257 is terminal **INFRA_ERROR** under the frozen no-retry/no-second-workflow rule.
No workflow repair or scientific retry is authorized inside R257.

No paid/private/holdout/full execution, R223/R244 artifact access, submission,
leaderboard/canonical mutation, R254 history change, threshold tuning, or method tuning
occurred.

Workflow conclusion and research status are distinct here:
- workflow conclusion: **failure**
- research status: **INFRA_ERROR**
- scientific status: **UNEVALUATED**
