# R252 final report — terminal INFRA_ERROR before science

Run ID: `R252-one-shot-actions-global-accuracy-20260923`  
Owner: `actions-accuracy-method-research`  
Candidate frozen: `V25-D21-CWG`  
Disposition: **INFRA_ERROR — no scientific measurement**

## Frozen work before dispatch

R252 read/deduplicated the immutable 194-entry history and required R231/R232/R238/R239/R245/R249/R250/R251 evidence. It froze one distinct candidate, V25-D21-CWG, which changes only the old-source shared-basis birth weights from the V25 hub-leg heuristic to D21-channel weights:

- parent: `dA = 9 + w2^2 + 9 e^2`, `dP = 1 + s^2`
- candidate: `dA = w2^2 + e^2`, `dP = w2^2 + s^2`

No R251 GFNP, DRRE/RSRF descendant, R247/R248/R250 family, R244 MP-R16, R223 V25-LF or other closed/rejected family was reused. R223/R244 candidate outputs/artifacts were not read.

A new target-free production-shape fixture was frozen before the workflow: `R252-BLOCK2-252001`, width 1024, depth 16, 512 independent deterministic 2x2 blocks per layer, exact analytic 2D Gaussian truth. Expected concatenated dense-weight SHA256 is `1ed998cad7f2ba4c8259f70a241913359ac49b7b0252d91a0c578539893ddfb0`; expected truth SHA256 is `0803ca4d381ad13ab0842fcd4775a3e4b1ad2f1409f517d196ac89073c479946`.

Protocol/spec/harness were committed before dispatch. The candidate source was deliberately not materialized before the unchanged-parent gate.

## Sole Actions workflow

Exactly one workflow was triggered:

- GitHub Actions run: `35830273198`
- job: `107081017265`
- attempt: 1
- workflow/head commit: `c00cf0b98016c6fa81c203a6613ce811f585f0c2`
- runner image: standard `ubuntu-24.04` (24.04.5 LTS), hosted runner version 2.337.0
- repository: `tim8es/arc-whitebox`, verified public before dispatch
- artifact: `r252-one-shot-evidence`, ID `10736967637`
- artifact ZIP SHA256: `4ecd1ed42f28a4b02caccd70dce9570a0738d7cb2b4f3976207fdd31f98bb989`
- artifact size: 2072 bytes

Official GitHub documentation checked before dispatch states standard GitHub-hosted runners are free for public repositories. No larger/self-hosted/private/paid runner was used.

## What passed

The pre-science wheel download/hash gate passed for all three pinned packages:

- NumPy 2.4.6 CPython-3.11 wheel SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`
- FlopScope 0.12.1 wheel SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`
- WhestBench 0.16.1 wheel SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`

Python setup also passed exactly at 3.11.16, and installation completed successfully.

## Exact infrastructure failure

The workflow then applied an overly strict runtime-version assertion:

`expected = {"python":"3.11.16","numpy":"2.4.6","flopscope":"0.12.1","whestbench":"0.16.1"}`

The installed runtime reported:

`{"python":"3.11.16","numpy":"2.4.6","flopscope":"0.12.1+np2.4.6","whestbench":"unknown"}`

This is a harness/version-reporting mismatch after the wheel hashes had already proved the requested FlopScope and WhestBench distributions. FlopScope exposes the expected local-version suffix `+np2.4.6`; the imported WhestBench module does not expose `__version__` through the field the harness queried. The shell step exited 1 before fixture reconstruction.

Per the frozen one-workflow/no-retry rule, this defect is **not repaired or rerun** under R252.

## Same-attempt protocol ambiguity detected after dispatch

After the sole workflow had already been triggered, the authoritative `research/control-v2` branch received additional same-R252, same-owner research commits that were not queue transitions:

- `f46c9c8d49c129c29d4e74df1cfa778d10af3465` — full-history novelty audit;
- `4fc054bf8fb0c087a7edeb32f73bd1f54f2656f8` — a different frozen `CFSP4` protocol;
- `e3e82a3542d414296eac3c8aa1636f7c4fb3638c` — a different production-shape fixture replay;
- `63a2f49313364dcae7f0a975bf0773800b0553f2` — different fixture byte hashes.

These commits preserve queue revision 240 and the same sole RUNNING attempt, but they describe a different candidate/fixture from the already-triggered D21-CWG workflow. No second R252 workflow exists in GitHub Actions at finalization time. Because the user requires exactly one method and one workflow, R252 must not continue on the later CFSP4 line. This is recorded as protocol ambiguity, not scientific evidence, and is an additional reason to terminate without retry.

## Scientific state

There were **zero scientific measurements**:

- frozen fixture reconstruction/exact-truth verification: not executed in Actions;
- unchanged V25 parent: not executed;
- parent checkpoints/MSE/FLOPs: absent;
- candidate source construction: not executed;
- candidate falsifier: not executed;
- validation: not executed;
- public R209 mini-100: not accessed/run;
- Actions retries/second workflow: none.

Therefore R252 makes no claim about V25-D21-CWG accuracy, FLOPs, source eligibility, or public score. The correct terminal class is **INFRA_ERROR**, not a scientific rejection and not parent INCONCLUSIVE (the parent gate was never reached).

## Safety / scope

No paid compute, larger/self-hosted runner, private/holdout data, submission, leaderboard mutation, canonical V25 edit, gate relaxation, second method, or retry occurred. R251/GFNP was not resumed.

The uploaded workflow receipt has SHA256 `37e6ddd91136c280c60375490885cba35f824372c3add845c5c85e4ac9a4e63a`; its decision is `INFRA_ERROR_BEFORE_TARGET_FREE_RESULT`.
