# R353 — R209 capture-workflow readiness audit

**Status:** COMPLETE  
**Recommendation:** **YES, CONDITIONALLY — PR #36 can unblock the missing R209 residual-structure evidence at zero spend, but it is NOT currently authorized or runnable as-is.**  
**No measurement claim:** no real capture, residual-direction diagnostic, corrected MSE, score, or scientific outcome is produced by R353.  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r353-r209-capture-readiness-audit-20260924`

## 1. Question

Does the existing draft PR #36 provide a safe zero-spend path to obtain the missing V25 final prediction/target/residual vectors needed for real R209 residual-structure research, without turning the task into a private/holdout/full/submission or paid path and without bypassing current control rules?

**Answer: YES, conditionally.**

The technical capture path is ready enough to be a valid unblocker, but the current repository state is deliberately fail-closed:

- PR #36 is still **open / draft / unmerged**;
- the workflow requires dispatch from **main**;
- the frozen result branch does **not** currently exist;
- the protocol still records merge, result-branch creation, Actions dispatch, and benchmark execution as unauthorized;
- the current PR head has **zero check-runs and zero commit status contexts**;
- no real capture has ever been executed.

The next real execution therefore requires explicit coordinator/control authorization and repository-state preparation. R353 performs none of those writes or executions.

## 2. Live PR #36 state

Live pull request:

- PR: **#36**
- title: `R293: prepare manual one-shot V25 residual capture workflow`
- state: **open**
- draft: **true**
- merged: **false**
- mergeable: **true**
- mergeable state: **clean**
- base: `main`
- base SHA: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- head branch: `research/r293-v25-capture-workflow-prep`
- head SHA: `f6fb9018504632edffa1fb80d14ce8a68f442602`
- latest PR update observed: `2026-09-24T01:05:14Z`
- comments: 0
- review comments: 0
- live check-runs on exact head: **0**
- live status contexts on exact head: **0**

The absence of PR checks is consistent with the intentional absence of a pull-request trigger. It is not execution evidence. The safety evidence comes from the separately committed static/synthetic audits summarized below.

Current exact PR artifacts relevant to execution:

- workflow `.github/workflows/r293-v25-residual-capture.yml`
  - blob `19f6f95ceb2cacef5497eafd5e31e20e86cfad8c`
- protocol `research/r293/R293_PROTOCOL.json`
  - blob `cc51198550b0d35b7fb0e34e8b072d74a456476c`
- R294 corrected evaluator patch
  - blob `65abb2e2040e44a7965f5123acd17bb838891532`
- corrected R296/R302 workflow-security checker
  - blob `e6c975a72f8f4863b476bfe5b636984fe1169713`

The frozen output branch `research/r293-v25-capture-result` is **currently absent**. The workflow is explicitly forbidden from creating it.

## 3. Why a fresh capture is actually needed

### R278

R278 froze a narrow residual-structure question before seeing raw residual vectors:

- panel: public development `v2-phase2 mini:all-100`;
- sort immutable decimal `network_id` strings lexicographically;
- first 50 = FIT;
- last 50 = EVAL;
- fit one network-agnostic vector
  `d = mean_FIT(target_final - pred_final)`;
- evaluate `pred + d` only on EVAL;
- no per-network scalar/sign/rank/selector/feature/normalization/tuning.

Materiality requires all four:

1. EVAL mean raw MSE improves by at least 2%;
2. at least 30/50 EVAL networks improve;
3. paired mean MSE gain exceeds 2 descriptive SE;
4. median EVAL raw MSE improves.

R278 ended `INFRA_ERROR / BLOCKED_BEFORE_DIAGNOSTIC_EXECUTION` with:

- diagnostic executions: 0;
- estimator executions: 0;
- Actions runs: 0;
- no scientific result.

R278 receipt blob:
`1568273d596bd2510c8a3c3520db6da18d2918b0`.

### R282

R282 independently established that existing R209/R223/R224 evidence does **not** contain the required raw V25 vectors.

Exact missing evidence:

- V25 final prediction bytes, float32[1024], for each of 100 public Mini networks;
- exact final target bytes float32[1024] (or full targets);
- or exact signed residual `target_final - prediction_final`.

R282 verdict:
`NO_RECOVERABLE_RAW_V25_RESIDUAL_VECTORS_IN_EXISTING_EVIDENCE`.

R282 receipt blob:
`48a29e486405693a993fcc429a3fd9c80d28da5e`.

Therefore a faithful new capture is not duplicating an existing retained vector artifact. It is filling an identified evidence gap.

## 4. R291–R302 evidence chain

| Task | Evidence relevant to readiness | R353 interpretation |
|---|---|---|
| R291 | Capture harness prepared; 16/16 synthetic checks; no real benchmark. Captures final prediction, final target and residual at the scorer pre-MSE seam. | Core capture contract is frozen, but R291's original patch was not sufficient by itself. |
| R292 | Independent audit found the R291 unified diff malformed and unusable by `git apply`. | Historical blocker, not current blocker. |
| R293 | Draft PR #36 prepared as workflow-dispatch-only, public Mini-100 one-shot; no merge/run. | Establishes intended one-shot execution and explicit authorization gates. |
| R294 | New append-only patch applies cleanly to exact WhestBench 0.16.1 source; 41 additions, zero official-source deletions; score/FLOP/return semantics preserved. | Closes R292 patch-format blocker. |
| R295 | Independent security audit found missing rerun gate, non-atomic result-branch update, mutable action tags, and token-persistence issues. | Historical security NO-GO, later repaired. |
| R296 | Workflow hardened with attempt gate, explicit CAS leases, immutable action SHAs, process-scoped token helper, exact output allowlist. | Closes R295 design blockers, but its first committed checker later proved defective. |
| R297 | Final static/read-only review of exact current PR head `f6fb901...`: PASS, with explicit reliance on R294 and corrected R302 execution receipts. | Current static review remains applicable because live PR head is unchanged. |
| R298 | Offline real-capture analyzer prepared; 13/13 synthetic checks; no real vectors. | Downstream diagnostic implementation exists. |
| R299 | Adds coordinate-wise residual-energy diagnostic; delta semantics tested; full integration checker was not run there. | Superseded on arithmetic path by R300/R301. |
| R300 | Corrects binary32 coordinate-energy arithmetic and adds 21-check integrated selfcheck; no real vectors. | Correct downstream analyzer version. |
| R301 | Exact R300 analyzer/selfcheck bytes verified; **21/21 synthetic checks PASS**. Runtime was Python 3.13.13; target production pin Python 3.11.16 was not tested. | Analyzer is independently synthetically verified, with one runtime-version limitation before real-vector scientific use. |
| R302 | Corrects R296 checker helper argument order; exact current workflow/protocol/checker pass **21/21** security/CAS checks. | Current workflow security evidence is valid; do not rely on the superseded original R296 checker execution claim. |

Key receipt blobs:

- R291: `53251462138aab94d1cff51c284331eccec089d4`
- R292: `eca95be1a8907dedf5e04708a8c9c8db3906e32c`
- R293: `79aa5993883d31e5eec27d854781a86e470242d2`
- R294 current PR receipt: `6ca61e19a79e277e33f994b9bdbc407c8d796e61`
- R295: `0119ce35b6ce9fd6efd4765797eeb9735ad17759`
- R296 current PR receipt: `92614092309b3265162e03ace38984621dc470e9`
- R297: `ccdda2f0d60a68e38e5dfd2e89bedc7277352071`
- R298: `277058cb85e3425d9ba911c6210fb9bfdd0dc564`
- R299: `cc2eb44635f54ae315d2a03ac2d8eb0c117b601f`
- R300: `b7728caecfd9612e7fcaffab94562361279a4011`
- R301: `45538ad637630707601192c0633fb3dabfe6d4d6`
- R302: `a6b895abce913529c987eb64ba8d8fb40b523033`

No task in that chain claims a real R209 residual measurement.

## 5. What PR #36 would actually execute and access

If separately authorized, merged, prepared and dispatched, the current workflow would do the following.

### Preflight

On a standard GitHub-hosted `ubuntu-24.04` runner:

- require `github.ref == refs/heads/main`;
- require `github.run_attempt == 1`;
- require confirmation text `RUN_R293_V25_CAPTURE_ONCE`;
- run the R293 static workflow/protocol preflight;
- run the corrected R296/R302 workflow-security selfcheck;
- query the public repository branch API for the fixed result branch;
- require that result branch already exists, is `protected=false`, and points exactly to the dispatch SHA;
- require that no prior capture manifest exists.

### Durable one-shot claim

Before installing dependencies or running V25:

- recheck the result branch;
- create an empty claim commit;
- atomically move the result branch from dispatch SHA to the claim commit using explicit `--force-with-lease`;
- reject reruns/second dispatches/moved/deleted branches.

### Runtime/network access

The persistence job would then:

- use Python `3.11.16`;
- install exact direct pins:
  - NumPy `2.4.6`
  - FlopScope `0.12.1`
  - WhestBench `0.16.1`
  - datasets `4.1.1`;
- fetch exact V25 source bytes from public GitHub:
  - repository `504aldo/whest-p2-cumulant-k3`
  - commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
  - expected V25 blob `195373a110215256b759d7c172ba8c923c62e5cc`;
- verify and apply only the corrected R294 evaluator-side patch to exact WhestBench 0.16.1 scoring source;
- run `whest validate`;
- run V25 once on:
  - `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
  - split `mini`
  - streaming mode
  - exactly 100 MLPs
  - local runner
  - FLOP budget `2^41`
  - 120 s wall cap
  - 0.4 s residual cap
  - one thread.

### Data captured

At the frozen evaluator seam, after failure zeroing and after scorer materialization of the final vectors but before final-layer MSE computation, the harness records for all 100 rows:

- final prediction float32[1024];
- final public-development target float32[1024];
- residual `target - prediction` float32[1024];
- row/network/failure/integrity metadata.

It does **not** persist all-layer target tensors.

Raw vector payload:
**1,228,800 bytes**.

### Persistence

The workflow permits exactly four result paths:

1. `research/captures/r293/vectors.f32le`
2. `research/captures/r293/manifest.json`
3. `research/captures/r293/SHA256SUMS`
4. `research/captures/r293/run-receipt.json`

Persistence is ordinary Git content through a narrowly scoped `GITHUB_TOKEN` `contents: write` job.

It does not use:

- `actions/upload-artifact`;
- Git LFS;
- GitHub Packages;
- cache storage;
- PAT;
- private/holdout/full data;
- competition submission;
- leaderboard mutation.

## 6. Is this target-free, public-development, repeat, holdout, paid, or submission work?

### Capture execution classification

**Not target-free.**

The workflow intentionally reads and persists the **public development targets** needed to form the residuals.

**It is an operational repeat of V25 on the already-exposed public Mini-100 panel.**

The estimator and panel are not new. The workflow invokes `whest run` again because the original R209 artifact did not retain the needed vectors.

Therefore it should not be described as “no benchmark execution” when eventually run.

### Scientific diagnostic classification

The **residual-structure measurement is new**, because R278 never executed and R282 proved that the vectors necessary to compute it are absent from retained evidence.

The downstream R278/R300 diagnostic is:

- public-development research;
- target-bearing;
- frozen before real vector inspection;
- no per-network tuning;
- offline diagnostic only unless later inserted into an honestly metered estimator.

The 50-row EVAL half is **not a fresh holdout/confirmation panel**. It is a preregistered internal split of an already exposed development panel.

### Explicit non-classifications

The proposed path is **not**:

- private data;
- holdout data;
- full competition test data;
- paid compute;
- competition submission;
- leaderboard inference;
- a new candidate score benchmark;
- a new independent confirmation panel.

## 7. Zero-spend evidence

R290 separately audited the result-persistence path and concluded:

`DIRECT_GIT_PERSISTENCE_CONFIRMED_NO_ACTIONS_ARTIFACT_STORAGE`.

R290 evidence:

- repository is public;
- standard GitHub-hosted runner usage is documented as free for public repositories;
- ordinary Git repository content is used for persistence;
- no Actions artifact / Packages / LFS / cache storage is used;
- the planned capture is about 1.36 MB maximum;
- no billing-dashboard input is required for this persistence design.

R290 receipt blob:
`cf0c899bb29c05097df94f1471ce3fff61388da7`.

Current PR protocol preserves exactly that architecture:

- runner class: `standard GitHub-hosted public-repository runner`;
- ordinary Git persistence;
- exact four-file allowlist;
- no paid persistence fallback.

**R353 finding: a zero-spend execution path is evidenced, provided the repository remains public and the run stays on the pinned standard GitHub-hosted runner/persistence path.**

A push or runner-policy failure must fail closed. It must not fall back to paid storage, PAT, LFS, Packages, or another paid resource.

## 8. Current process constraints

Current main policy files inspected:

- `AGENTS.md`
  - blob `6d9c61537a282a7d141af316dd8be438d1015a49`
- `research/RESEARCH_PROCESS.md`
  - blob `bf5a4676d8f36100e2dfdde32d544a39661eba8d`

Relevant requirements:

- only the coordinator allocates executable research work;
- claim/start must be published before actual execution;
- free/existing compute is allowed where verified;
- development-data exploration is allowed;
- all exposed panels are development data and must not be relabeled as fresh holdout;
- infrastructure errors may be repaired with recorded attempts;
- no competition submission is performed by research workers;
- historical failed outcomes must not be rewritten.

R278's own frozen protocol additionally said “No Actions” for that exact R278 attempt.

Therefore PR #36 must **not** be launched by pretending it is a continuation/rerun of the old R278 attempt. A future Actions capture must be an explicitly authorized **new capture execution job** under the current control process, using the R293/R296/R297/R302 workflow evidence.

That new capture can then supply inputs to a **separate scientific consumer job** implementing the already-frozen R278/R300 diagnostic.

## 9. Remaining gates

### Gates before any real capture execution

1. **Explicit control GO / ownership**
   - coordinator must allocate the one-shot capture execution;
   - publish claim and start with a unique run ID, exact code SHA and exact dispatch command;
   - this is required because the run will install packages, access the public dataset, execute V25/WhestBench, and create new evidence.

2. **Explicit merge authorization**
   - PR #36 is draft/unmerged;
   - workflow requires `main`;
   - merge must be separately authorized.
   - R353 does not recommend an implicit merge merely because static review passed.

3. **No PR-head drift**
   - current R297/R302 evidence is tied to head `f6fb9018504632edffa1fb80d14ce8a68f442602`;
   - any workflow/protocol/security-checker change requires re-review.

4. **Pre-create the fixed result branch**
   - `research/r293-v25-capture-result` is currently absent;
   - it must be created externally at the exact merged-main dispatch SHA;
   - branch API must report `protected=false`;
   - no existing capture manifest may be present.

5. **Exactly one dispatch**
   - dispatch only from that exact main SHA;
   - confirmation token must be exact;
   - `run_attempt == 1`;
   - no rerun/second dispatch after durable claim without explicit reset/re-authorization.

### Gates after capture, before a scientific conclusion

6. **Verify persisted result**
   - result branch CAS lineage;
   - exactly four allowed files;
   - manifest/panel identity;
   - vector/hash/seal integrity;
   - runtime/pin identity;
   - no unexpected failures.

7. **Analyzer runtime gate**
   - R301 passed the R300 synthetic analyzer 21/21 on Python 3.13.13;
   - the pinned target runtime Python 3.11.16 was not tested.
   - Before first real-vector analysis, the shortest conservative path is to replay the same standard-library 21-check selfcheck under Python 3.11.16, without inspecting real vectors first.

8. **Separate scientific control GO**
   - consuming the real capture for the frozen residual-direction/coordinate-energy diagnostic is a scientific measurement;
   - it needs its own claim/start and durable receipt;
   - it must remain labeled public-development/offline diagnostic;
   - no official adjusted-score or leaderboard claim unless an honestly metered estimator is later tested under its own authorization.

## 10. Shortest safe next step

**Do not dispatch PR #36 yet.**

The shortest safe progression is:

1. coordinator creates/authorizes a new **capture-execution** job explicitly based on PR #36 head `f6fb901...`;
2. authorize merge of that exact reviewed head to main;
3. create the fixed result branch at the exact merged-main SHA and verify `protected=false`;
4. publish control `start` for exactly one workflow dispatch;
5. dispatch once and verify only the sealed four-file capture result;
6. only after capture verification, open a separate scientific job to replay the R300 selfcheck under Python 3.11.16 and analyze the real vectors.

This sequence preserves zero spend, public-development scope, one-shot behavior, and current control ownership.

## 11. Final recommendation

### YES — as an infrastructure unblocker

PR #36 is now supported by enough evidence to serve as the **zero-spend capture mechanism** that R278/R282 lacked:

- missing vector evidence is real;
- capture seam and serialization are frozen;
- malformed R291 patch was repaired by R294;
- R295 security findings were repaired by R296;
- the R296 checker defect was repaired and replayed 21/21 by R302;
- exact current head received R297 final static PASS;
- downstream analyzer arithmetic is frozen through R300 and synthetically verified 21/21 by R301;
- zero-spend standard-runner + ordinary-Git persistence is evidenced by R290.

### NO — as an immediately runnable or already measured experiment

Nothing currently authorizes execution.

The result branch is absent, PR is still draft/unmerged, the protocol authorization flags are false, and there are no live check-runs proving execution.

R353 therefore recommends **conditional GO after the explicit gates above**, not an immediate workflow run.

## Execution accounting

R353 itself performed:

- Actions runs: **0**
- benchmark/estimator runs: **0**
- public dataset access/download: **0**
- dependency install/download: **0**
- real capture vector access: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- competition submission: **0**
- PR comments/reviews/merge/edit: **0**
- main edits: **0**
- control/queue edits: **0**

R353 makes **no claim of a residual-structure measurement**.
