# R382 — no-download evaluation route for ARC Phase 2

**Status:** COMPLETE  
**Verdict:** **NO_DOCUMENTED_NO_SLOT_PUBLIC50_VALIDATION_ROUTE**  
**Mode:** read-only primary-source audit; no login, no browser/account mutation, no upload, no submission, no dataset/dependency download or install  
**Branch:** `research/r382-aicrowd-no-download-test-route-20260925`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Date:** 2026-09-25

## Executive answer

There are four distinct things that must not be conflated:

1. **Local contract/package validation** can be done with no contest dataset, no AIcrowd authentication, no upload, and no submission slot — but it does **not score any contest MLPs**.
2. **Development Mini-100 scoring** uses the real WhestBench scoring pipeline on the published `v2-phase2` Mini split and exposes exact local `per_mlp` records — but a first run needs the roughly **7.03 GB** public Mini dataset to be fetched/cached. It is **not** the live leaderboard public-50 panel.
3. **Live public-50 scoring** is server-side grader work. In the audited official participant client/docs, the only documented route to it is a real AIcrowd submission: authenticate, pass eligibility, upload the package, create a submission, then wait for grading. No separate participant-facing “validate on public-50 without creating a submission” endpoint or CLI mode was found.
4. A **leaderboard submission** is therefore currently the same official route that produces public-50 evidence. A successful graded submission creates a submission ID and a public submission/leaderboard result. It is subject to the submission quota and post-grading rules review.

So, under the exact R382 restriction “no test-set download and no submission slot / leaderboard entry,” **there is no documented official way to obtain a live public-50 score**.

There is a useful no-download local rehearsal — `whest run` without `--dataset` — but it generates fresh local MLPs and lower-precision Monte-Carlo ground truth. It is Phase-2-shaped, not same-panel evidence.

## 1. Primary-source baseline

### Official starter kit snapshot

Repository: `AIcrowd/whest-starterkit`  
Audited commit: `5eb9aa1455fcb3216af55994bdf25dc242b95797`

Important immutable files:

| Purpose | Path | Git blob SHA-1 |
|---|---|---|
| local Stage 3 / Mini-100 | `docs/getting-started/stage-3-run-local.md` | `2bc23fd23210f513a9bfab4917dde6f4ef18c125` |
| subprocess rehearsal | `docs/getting-started/stage-4-run-subprocess.md` | `eda1d7a48547a6eab44d4d145b7303d8d195c7ac` |
| public dataset workflow | `docs/how-to/use-evaluation-datasets.md` | `53af1ead77023bb2c4c27fa2a64b494a4f46aa26` |
| Stage 5 submit | `docs/getting-started/stage-5-package.md` | `1b4009b6c7ae7db0a49a7ff82f9ecd653bba79eb` |
| CLI reference | `docs/reference/cli-reference.md` | `cec1369dc94e89f40c1bba274465712a0c1a74b1` |
| Phase-2 limits | `docs/reference/rounds.md` | `2aaf38a54b5d6ed83ce2604870dcac59e62cee59` |
| report/per-MLP schema | `docs/reference/score-report-fields.md` | `4656a892bfeea52a233b900f6d698db8524936fc` |
| FlopScope / grader rehearsal | `docs/reference/flopscope-primer.md` | `7c1478581347f362f691aa1b8023d8edcd44874d` |
| allowed-code rules summary | `docs/concepts/allowed-code.md` | `525276e8e5bc7f6a7dd54e876140ab0df514be32` |
| local dependency requirements | `pyproject.toml` | `2c1d562a2073046d6912868184b52c8c593d23c5` |

Primary URLs:

- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-3-run-local.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-4-run-subprocess.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/use-evaluation-datasets.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-5-package.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/cli-reference.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md

### Official WhestBench participant client

Repository: `AIcrowd/whestbench`  
Audited commit: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

| Purpose | Path | Git blob SHA-1 |
|---|---|---|
| AIcrowd participant REST client | `src/whestbench/aicrowd_client.py` | `000750d57a7720c336e751f89efc7bc05ae78fa5` |
| participant CLI | `src/whestbench/cli.py` | `f214a0e210aa2cd10d0d0a68b14a2b1341b4091f` |
| package validator | `src/whestbench/validation.py` | `d9c81db3f171a28d6b85ac8b4a2de1879fef02c0` |
| packager | `src/whestbench/packaging.py` | `26f9f1c07cdbbec40659ce150e31e77d3c553bd7` |

Primary URLs:

- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/aicrowd_client.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/cli.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/validation.py

### Live public submission semantics

Official public graded Phase-2 example:

https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

The current public page states:

- Phase 2;
- public split: **50/50 MLPs scored**;
- public Adjusted Score is the mean over **50 public MLPs**;
- private split: **50 sealed MLPs**;
- full test: **100 MLPs**;
- the public split is the set participants iterate against and is recomputed for each submission;
- a public per-MLP ledger is rendered for the 50 public MLPs.

This is a dynamic official page, so there is no Git blob SHA for it.

### Live grader package pair

Official organizer answer, 2026-08-27:

https://discourse.aicrowd.com/t/shipped-covariance-propagation-example-trips-the-phase-2-residual-cap-locally-0-16-0-but-grades-fine-what-happens-when-the-evaluator-upgrades/18202/2

The organizer states that the evaluators actually run:

- `whestbench@v0.16.0`;
- `flopscope[server]==flopscope[client]==0.12.0`.

The starter-kit `pyproject.toml` locally requires:

- Python `>=3.10`;
- `whestbench>=0.16.1,<0.17.0`;
- `flopscope>=0.12.1,<0.13.0`.

That local one-patch lead is already analyzed in R309; source-level score semantics for frozen V25 were found compatible, while exact runtime replay remains unproven.

## 2. Four modes that must be separated

| Mode | Contest data needed locally? | AIcrowd auth? | Upload? | Creates submission? | Uses live public-50? | Exact local `per_mlp`? | Suitable for exact V25 public-50 comparison? |
|---|---|---|---|---|---|---|---|
| `whest validate` | **No** | No | No | No | No | No scoring | **No** |
| `whest package` / `validate-package` / `submit --dry-run` | **No** | No for dry-run | No | No | No | No scoring | **No** |
| `whest run` without `--dataset` | **No** | No | No | No | No — fresh local MLPs | Yes, for local synthetic suite | **No** |
| `whest run --dataset ...@v2-phase2 --split mini` | **Yes unless already cached** | No | No | No | No — development Mini-100 | Yes | **No** for public-50; yes for Mini-100 comparisons |
| real `whest submit` | Dataset stays server-side | **Yes** | **Yes** | **Yes** | **Yes** | public UI ledger exists; raw participant export not documented | Only route to same live public-50 measurement found |

## 3. Local package validation: zero slot, zero score

### `whest validate`

The official CLI describes `whest validate` as estimator loading/output-contract validation. It checks the estimator class, optional `setup()`, returned shape, and finite values on a small probe.

It is **not** a Phase-2 score run. The FlopScope primer explicitly notes that this stage is not a real budget test: validation calls `predict()` outside the normal per-MLP contest `BudgetContext` and uses a small probe network.

Therefore:

- no dataset download;
- no AIcrowd auth;
- no upload;
- no submission slot;
- no Mini-100 score;
- no public-50 score.

### `whest package` and `whest validate-package`

These validate the shipment structure and manifest integrity.

`validate-package` checks that the declared entrypoint is present and that archived files match their manifest SHA-256 values. It is the same **archive integrity** check the grader runs, not a scientific scoring run.

### `whest submit --dry-run`

This is particularly important for R382.

Official docs/source say the dry run:

- packages to a temporary location;
- previews the files, sizes, and versions;
- runs local package validation;
- stops **without uploading**;
- does not require AIcrowd auth.

Therefore `--dry-run` is safe preflight, but it **cannot** answer “what score does this get on the 50 live public MLPs?”

## 4. No-download local scoring exists, but it is not a fixed contest panel

A plain:

`whest run --estimator estimator.py`

does not require the published test dataset.

Current Stage-3 documentation says that, without `--dataset`, WhestBench still uses the Phase-2 shape/rules but generates a local suite:

- default 10 MLPs;
- width 1024;
- depth 16;
- `B=2^41`;
- local ground truth from **200,000 Monte-Carlo draws per MLP**;
- fresh MLPs and ground truth on each run unless a seed is pinned.

This is useful for:

- shape failures;
- FLOP-budget failures;
- rough runtime/residual checks;
- deterministic candidate-vs-parent tests if the same local seed is pinned.

It is **not**:

- the published Mini-100;
- the live public-50;
- evidence of leaderboard performance.

So it is the only official no-download scientific score path, but not a same-conditions competition score.

## 5. Development Mini-100: real scorer, but requires the public dataset

Official Stage 3 calls the Mini path the **real scoring pipeline** used against the public-release Mini split:

`uv run whest run --estimator estimator.py --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --runner local`

Properties:

- 100 fixed development MLPs;
- 1024×16;
- baked N=1e9 ground truth;
- same WhestBench score schema;
- exact machine-readable local report, including `results.per_mlp[]`;
- reproducible candidate/parent comparison on that Mini-100 panel.

But the official dataset guide states that Phase-2 Mini is about **7.03 GB** and is fetched/cached on first use.

Therefore, under R382's explicit “no data download” rule, this route is unavailable unless an exact `v2-phase2` Mini cache already exists locally. R382 did not inspect or use any local cache and downloaded nothing.

This is the panel on which the committed R209/V25 score `8.170397440117225e-9` exists. It remains a development Mini-100 measurement, not a live public-50 measurement.

## 6. Subprocess rehearsal still does not solve the dataset problem

Stage 4 changes the runner:

`--runner subprocess`

It adds the grader-like process boundary and, on Linux, applies the 8 GB process address-space limit used for participant solution execution.

It still uses whichever local/generated dataset the `whest run` invocation supplies.

Thus:

- subprocess mode can improve transport/import/memory fidelity;
- it does **not** grant access to the hidden live public-50;
- with `--dataset ... --split mini`, it still needs the Mini data locally;
- without `--dataset`, it still scores generated local MLPs.

## 7. Live public-50: the documented path is a real submission

The official WhestBench participant client documents the complete network path.

### Authentication and eligibility

A real submit uses:

- `Authorization: Token <api_key>`;
- `GET /api/v1/api_user` to validate the participant identity;
- `GET /api/v1/challenges/<slug>/eligibility` to ask whether submissions are permitted.

Eligibility can depend on challenge participation/terms state. No login or eligibility call was made by R382.

### Upload and submission creation

After local package validation, the client:

1. requests a presigned upload target from AIcrowd;
2. uploads the package to S3;
3. calls `POST /api/v1/submissions`;
4. receives a `submission_id`;
5. optionally polls `GET /api/v1/submissions/{id}` until grading is terminal.

The documented status response exposes fields including:

- `grading_status_cd`;
- `score`;
- `score_secondary`;
- `grading_message`.

There is no documented participant-client call in the audited source that says “score this package on public-50 but do not create a submission.”

No official participant docs/source audited by R382 expose:

- a `validate-on-public` endpoint;
- an `unlisted`/private-validation flag;
- a `leaderboard=false` flag;
- a no-quota public-50 scoring mode.

This is an **evidence statement about the published participant surface**, not a claim that no internal AIcrowd endpoint exists.

## 8. Submission side effects

A successful public-50 grade is not a neutral validation call.

Official docs state that `whest submit` uploads to the AIcrowd leaderboard, and the public submission page shows the resulting score/per-MLP public ledger.

The current official starter-kit reference states a Phase-2 submission cap of **10 submissions per team per UTC day**.

Thus a normal successful submission has these side effects:

- requires participant credentials;
- requires challenge eligibility/accepted participation terms;
- uploads the estimator package;
- creates a durable submission ID;
- enters the grading/submission system;
- consumes the normal submission path/quota;
- produces public-facing score/submission evidence;
- is subject to automated rules checks and possible agent/human review.

The allowed-code documentation states that review continues after grading and nonconforming submissions can later be invalidated.

### Smoke-test failure is not a loophole

Official failed submission #329176 states:

> “Nothing graded; nothing counted against your quota.”

Source:

https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329176

That is useful operationally, but it does **not** provide a validation route: a smoke-test failure produces no public score and no per-MLP scientific evidence.

## 9. Exact Phase-2 package/runtime requirements that matter here

### Package

From the official current packager/docs:

- single-file mode ships only the estimator file, renamed to `estimator.py`;
- folder mode requires root `estimator.py`;
- folder mode ships non-ignored helper/data files;
- generated `manifest.json` binds entrypoint, package/runtime version metadata, file list and SHA-256 hashes;
- submission size cap: **50 MiB**;
- submission file-count cap: **50**;
- credentials/secrets matching the built-in patterns are excluded;
- precomputed data files are allowed;
- third-party execution payloads such as vendored NumPy/SciPy/BLAS/compiled kernels are prohibited.

### Local participant toolchain

The current starter-kit project declares:

- Python `>=3.10`;
- `whestbench>=0.16.1,<0.17.0`;
- `flopscope>=0.12.1,<0.13.0`.

### Live grader pair

Organizer-confirmed:

- WhestBench `0.16.0`;
- FlopScope client `0.12.0`;
- FlopScope server `0.12.0`.

The exact grader Python patch/build is **not established by the primary sources audited here**, so R382 does not invent it.

### Phase-2 execution limits

Current official WhestBench/starter-kit sources give:

- MLP width: **1024**;
- depth: **16**;
- per-MLP FLOP budget: **2^41 = 2,199,023,255,552**;
- effective compute in Phase 2: `C_m = F_m`;
- per-`predict()` wall cap: **120 s**;
- residual wall cap: **0.4 s**;
- `setup()` cap: **5 s**;
- participant solution-process memory: **8 GB**;
- numerical work must go through the allowed FlopScope surface; residual time is plumbing, not an unmetered arithmetic budget.

The grader environment is server-side; the participant does not need to download the live public/private MLP dataset to submit.

## 10. What exactly would need to be authorized/uploaded for live public-50

If a future coordinator authorizes a real live evaluation, the minimum external action chain is:

1. authorize use/storage of an **AIcrowd API key** (or an already configured credential);
2. ensure challenge eligibility / required participation terms are accepted;
3. authorize packaging the frozen estimator source plus any allowed data files;
4. authorize upload of that tarball to the AIcrowd-presigned S3 target;
5. authorize creation of an AIcrowd **submission** for the ARC challenge;
6. allow server-side grading;
7. optionally use the authenticated status endpoint / public submission page to read the result.

No contest dataset needs to be downloaded to the participant machine for this route.

But steps 4–5 are precisely the upload/submission actions R382 was instructed **not** to perform.

## 11. Can we obtain exact per-MLP public-50 scores?

### Local Mini/generated runs: yes

The WhestBench local report schema contains `results.per_mlp[]`, with per-MLP:

- `mlp_index` / `mlp_name`;
- final-layer MSE;
- adjusted final-layer score;
- FLOPs/effective compute;
- timing/failure fields;
- per-layer MSE and breakdown information.

Those are machine-readable local run records.

### Live public-50 participant-facing evidence: exactness is not established

The official public submission page renders a 50-row public ledger, but its visible score fields are presentation-formatted scientific notation.

For the participant REST client, the documented submission-status response exposes aggregate `score`, `score_secondary`, grading status/message, but the audited contract does **not** promise a raw `per_mlp` report.

There is an additional primary-source limitation: in an organizer reply on the official AIcrowd forum, Mohanty stated that the submission **download report** function was a WhestBench-specific **admin-only** feature and was removed for participants:

https://discourse.aicrowd.com/t/submission-fails-due-to-the-redirect/18033/8

Therefore R382 cannot claim that a participant can currently retrieve the grader's exact raw 50-row `per_mlp` JSON through a supported public interface.

A participant may be able to obtain a machine-readable aggregate `score` from the authenticated own-submission status API; the official client explicitly documents that field. That is different from having all 50 exact row values.

## 12. Can V25 be compared on the same 50 public MLPs?

### Aggregate, competition-condition comparison

Conceptually yes **only by grading frozen V25 as a real Phase-2 submission** on the live public split.

That would place V25 on the same live public-50 evaluation route as another submitted candidate, with the same grader pair and Phase-2 limits.

But it would:

- require auth and upload;
- create a submission;
- use a submission opportunity;
- publish submission/leaderboard evidence.

R382 did none of these.

### Exact paired 50-row comparison

Not yet supported by the documented participant-facing evidence.

For an exact paired comparison such as:

`candidate_public50_per_mlp - V25_public50_per_mlp`

we need an official machine-readable raw public-50 row artifact for each graded submission, or a documented participant API exposing those exact rows.

The rendered public ledger alone is insufficient for exact arithmetic because its displayed numeric precision is a presentation surface.

This is consistent with R305/R377: the development Mini-100 identities cannot be joined honestly to the live public-50 merely by name/order, and rounded UI values must not be treated as exact floats.

## 13. Reconciliation with R379

R379 remains correct and R382 sharpens one boundary.

R379:

- established the local validation/package ladder;
- verified package caps and allowed-code constraints;
- established that a real submission requires auth/upload;
- recommended not spending a slot on R223 because it did not beat the R209 control on Mini-100;
- left authorization status separate.

R382 adds the explicit no-download/public-50 answer:

| Question | R379 | R382 clarification |
|---|---|---|
| Can local validation test packaging without a slot? | Yes | Yes; it never produces a public-50 score |
| Can `submit --dry-run` contact grader public-50? | not its purpose | **No**; source says no upload/auth and no server grade |
| Can Mini-100 be scored locally? | yes | Yes, but Phase-2 Mini is ~7.03 GB unless already cached |
| Can no-dataset `whest run` score something? | not the public comparison route | Yes, fresh local 10-MLP/200k-MC suite; not Mini/public-50 |
| Is there a documented no-slot public-50 validation endpoint? | not established | **No documented participant route found** |
| Does a live public-50 score require a real submission? | effectively yes | **Yes on the audited official participant surface** |
| Can participant download exact grader `per_mlp` report? | not established | **Not documented; organizer says report download is admin-only** |

No historical R379 conclusion is rewritten.

## 14. Shortest next step

Do **not** spend a slot merely to discover whether a hidden validation mode exists.

The shortest next step is one narrow organizer/support question, using the official rules/support channel already named in the starter kit:

**Ask whether AIcrowd exposes either:**

1. a participant-facing, no-quota/no-leaderboard server-side validation endpoint that runs a package on the live 50 public MLPs; **or, if not,**
2. a supported machine-readable endpoint/export for the exact raw public-50 `per_mlp` records of the participant's own normal graded submission.

If the answer to (1) is **no** and (2) is **yes**, then the shortest scientifically useful next action after coordinator authorization is one frozen **V25 control submission**: it would establish the live public-50 V25 baseline without any test-set download, and the raw per-MLP export would make later candidate comparisons paired and exact.

If both are **no**, then without downloading the public Mini dataset there is no official route to exact per-MLP same-50 candidate validation short of ordinary leaderboard submissions, and public comparisons must remain aggregate/display-level.

Official rules/support contact named by the current starter kit:

`arc-whestbench@aicrowd.com`

R382 does **not** send this email.

## 15. Evidence status / execution accounting

### Evidence status

- official no-slot public-50 participant route found: **NO**
- claim of internal AIcrowd nonexistence: **NOT MADE**
- local no-download generated-suite route: **CONFIRMED**
- Mini-100 real-score route: **CONFIRMED, REQUIRES DATA FETCH UNLESS CACHED**
- real submission live public-50 route: **CONFIRMED**
- participant machine-readable aggregate submission status field: **CONFIRMED**
- participant raw exact public-50 `per_mlp` export: **NOT DOCUMENTED**
- public page per-MLP rendered ledger: **CONFIRMED**
- report download for participants: **NOT AVAILABLE per organizer statement; admin-only feature**
- exact V25 same-public50 evidence currently available: **NO**

### R382 actions

- AIcrowd login/auth: **0**
- eligibility/account mutation: **0**
- browser/account changes: **0**
- external package upload: **0**
- submission creation: **0**
- submission slot used: **0**
- contest data download: **0**
- dependency/package install: **0**
- estimator/benchmark run: **0**
- Actions run: **0**
- private/holdout/full access: **0**
- R320 edit: **0**
- main edit: **0**
- PR edit: **0**
- control edit: **0**
- queue edit: **0**
- repository output: **exactly one Markdown report on the dedicated R382 branch**

## 16. Primary-source references

1. AIcrowd Whest starter kit, frozen commit `5eb9aa1455fcb3216af55994bdf25dc242b95797`:  
   https://github.com/AIcrowd/whest-starterkit/tree/5eb9aa1455fcb3216af55994bdf25dc242b95797
2. Stage 3 — real scoring pipeline on development Mini-100, blob `2bc23fd23210f513a9bfab4917dde6f4ef18c125`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-3-run-local.md
3. Stage 4 — subprocess/grader-transport rehearsal, blob `eda1d7a48547a6eab44d4d145b7303d8d195c7ac`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-4-run-subprocess.md
4. Public evaluation dataset workflow and sizes, blob `53af1ead77023bb2c4c27fa2a64b494a4f46aa26`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/use-evaluation-datasets.md
5. CLI reference, blob `cec1369dc94e89f40c1bba274465712a0c1a74b1`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/cli-reference.md
6. Stage 5 package/submit, blob `1b4009b6c7ae7db0a49a7ff82f9ecd653bba79eb`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-5-package.md
7. Allowed-code rules summary, blob `525276e8e5bc7f6a7dd54e876140ab0df514be32`:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md
8. Official WhestBench AIcrowd REST client, blob `000750d57a7720c336e751f89efc7bc05ae78fa5`:  
   https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/aicrowd_client.py
9. Official WhestBench CLI, blob `f214a0e210aa2cd10d0d0a68b14a2b1341b4091f`:  
   https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/cli.py
10. Organizer-confirmed live grader pair:  
    https://discourse.aicrowd.com/t/shipped-covariance-propagation-example-trips-the-phase-2-residual-cap-locally-0-16-0-but-grades-fine-what-happens-when-the-evaluator-upgrades/18202/2
11. Official graded Phase-2 submission showing the 50-public / 50-sealed split and public per-MLP ledger:  
    https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251
12. Organizer statement that the WhestBench report download is admin-only / removed for participants:  
    https://discourse.aicrowd.com/t/submission-fails-due-to-the-redirect/18033/8
13. Official failed submission showing that a smoke-test failure can yield no score and no quota count:  
    https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329176
14. R379 preflight, immutable project evidence, head `1f6931ea39f4bf28ca2cc0893ffa27bb8c2073e1`, report blob `69eebfc1b2f75b24e3eb480e5830610e31e83339`:  
    https://github.com/tim8es/arc-whitebox/blob/1f6931ea39f4bf28ca2cc0893ffa27bb8c2073e1/research/r379/R379_AICROWD_PREFLIGHT.md
