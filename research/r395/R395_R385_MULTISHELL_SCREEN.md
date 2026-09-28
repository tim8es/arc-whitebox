# R395 — R385 multi-shell implementation/screen preflight

**Status:** BLOCKED_PRE_IMPLEMENTATION  
**Verdict:** **STOP — REQUIRED LOCAL REPO / WHEST / FLOPSCOPE / BASELINE / AFFINE-BOUND IMPLEMENTATION NOT AVAILABLE**  
**Branch:** `experiment/r395-r385-multishell-screen-20260928`  
**Branch base:** R385 commit `2ba08cb916cc504f1c38673971c2aa811b2da48c`  
**Date:** 2026-09-28

## Assignment / handoff

R395 is the primary implementation task and **supersedes the unstarted R394 assignment in R316**. No R394 work was started or duplicated here. If the R394 session later resumes, it should treat R395 as the active handoff and avoid duplicate implementation/screen work.

## Required gate

R395 was allowed to proceed only if all required implementation/runtime components were **already locally available**, with explicit prohibition on:

- downloading/fetching/cloning code or datasets;
- installing packages;
- accessing Mini/public/private/holdout tensors;
- submitting to AIcrowd.

The task also required stopping rather than fabricating a replacement if any of the following were absent:

1. local R385/R383/R376/R388 source artifacts;
2. a sound affine-bound implementation producing R385 `ell,u` from generated MLP weights;
3. frozen V25/R223 baseline code;
4. Whest runtime/current estimator contract;
5. FlopScope instrumentation.

## Local-only inspection

Only the already-mounted local filesystem and existing executable/module environment were inspected.

Observed:

- `git`: present — `git version 2.47.3`
- `uv`: present — `uv 0.10.0`
- Python: present — `/opt/pyvenv/bin/python`, Python 3.13 environment
- `pip`: present — `pip 25.1.1`
- local Git repository candidates under the available work/mount roots: **0**
- local ARC artifacts matching R385/R383/R376/R388 or `estimator_v25.py`: **0**
- `whest` executable: **MISSING**
- Python module `whestbench`: **MISSING**
- Python module `flopscope`: **MISSING**

Representative local probes:

```text
git=git version 2.47.3
uv=uv 0.10.0
pip=pip 25.1.1 from /opt/pyvenv/lib/python3.13/site-packages/pip (python 3.13)
repo_candidates=0
arc_files=0
whest_cmd=MISSING
whestbench_module=MISSING
flopscope_module=MISSING
```

No remote code/data fetch was used to fill these gaps.

## Exact blockers

### 1. ARC repository/source artifacts are not mounted locally

There is no local checkout containing R385, R383, R376, R388, V25/R223, or any estimator implementation. Therefore R395 cannot read/modify/test candidate code without a prohibited clone/fetch.

### 2. Sound affine-bound implementation cannot be established

Because the repo/source tree is absent, no existing CROWN/Fast-Lin/other sound affine-bound implementation can be inspected or verified to produce the R385 `ell,u` pair from generated MLP weights.

R395 does **not** substitute sample-fit, cubature, heuristic bounds, or a newly downloaded implementation.

### 3. Frozen baseline code is unavailable locally

Neither frozen V25 nor R223 baseline source is locally present. Therefore the required paired candidate-vs-parent screen cannot identify or execute a valid frozen control.

**Baseline actually available locally:** **NONE**.

### 4. Whest current estimator contract/runtime is unavailable locally

The `whest` executable and `whestbench` Python module are absent. Therefore:

- published estimator-interface red→green cannot be run;
- contract validation cannot be run;
- no-dataset generated MLP suite cannot be produced;
- current local contract source cannot be inspected.

R395 does not rely on stale conversational summaries as a substitute for the required current executable contract.

### 5. FlopScope instrumentation is unavailable locally

The `flopscope` Python module is absent. Therefore exact Phase-2 FLOP accounting and required timing/resource instrumentation cannot be measured.

## Actions not performed

Because the preconditions failed before implementation:

- R385 estimator implementation: **NOT STARTED**
- affine-bound implementation/modification: **NOT STARTED**
- red→green interface test: **0 runs**
- Whest contract validation: **0 runs**
- R388 paired screen (8 roots × 3 MLP): **0 runs**
- candidate measurements: **0**
- baseline measurements: **0**
- paired deltas/root-level CI: **not available**
- FLOPs/wall/residual/RSS measurements: **not available**
- package installs: **0**
- code/data downloads/fetches/clones: **0**
- Mini/public/private/holdout access: **0**
- submissions: **0**
- Actions: **0**
- R320/main/PR/control/queue edits: **0**

## Scientific conclusion

There is **no R395 metric result** and no GO/NO-GO on R385 accuracy.

The only valid conclusion is an infrastructure blocker:

> The current execution environment does not contain the repository, baseline, WhestBench runtime, FlopScope instrumentation, or inspectable affine-bound code required by the task. Proceeding would require actions explicitly forbidden by R395.

This is not evidence against R385 and does not alter any historical R376/R383/R385/R388 verdict.

## Minimum unblock condition

R395 can be resumed without changing the scientific protocol only in an environment where the following are already present before work starts:

1. local checkout containing exact R385/R383/R376/R388 artifacts and frozen V25/R223 source;
2. inspectable sound affine-bound code that can generate R385 `ell,u`;
3. installed `whest` / `whestbench` matching the intended current contract;
4. installed compatible `flopscope`;
5. no need to fetch/install/download anything.

Then the same isolated branch can implement the minimal target-free candidate and run the preregistered R388 8×3 paired screen.
