# R384 — R223 package reconciliation against R379

**Status:** COMPLETE — READ-ONLY RECONCILIATION + REPORT  
**Verdict:** **R379 PACKAGE CONCLUSION NARROWED; COORDINATOR-PROVIDED LOCAL PACKAGE EXISTS, BUT R384 CANNOT INDEPENDENTLY HASH OR VALIDATE IT**

Exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
Branch: `research/r384-r223-package-reconcile-20260925`

No AIcrowd login, eligibility check, upload, submission, slot use, package rebuild, dependency install, dataset access, or Actions execution occurred in R384.

## 1. Scope and access boundary

R384 was asked to reconcile R379 with a coordinator-local archive reported at:

`C:\Users\itimu\OneDrive\Документы\ChatGPT\Control Center\aicrowd-r223-submission.tar.gz`

That Windows filesystem path is **not mounted or addressable in the current execution environment**. A bounded check of the normal mounted artifact locations available to this session did not expose a file named `aicrowd-r223-submission.tar.gz`.

Therefore R384 did **not**:
- read the archive;
- calculate its SHA-256;
- independently list its tar members;
- read its manifest/README/LICENSE bytes;
- run `whest validate-package`.

This is an access boundary, **not evidence that the archive is absent**.

Accordingly:

`repository_visible_official_validation = UNKNOWN`

`r384_local_archive_validation = NOT_RUN_ARCHIVE_INACCESSIBLE`

## 2. Coordinator-provided local package facts

The following are recorded exactly as **COORDINATOR_PROVIDED_UNVERIFIED_BY_R384**:

- local path: `C:\Users\itimu\OneDrive\Документы\ChatGPT\Control Center\aicrowd-r223-submission.tar.gz`;
- archive size: **22,487 bytes**;
- archive members:
  - `estimator.py`
  - `LICENSE-504aldo.txt`
  - `README.md`
  - `manifest.json`
- manifest reports:
  - `whestbench 0.16.1`
  - `flopscope 0.12.1`
- README explicitly discloses:
  - upstream `504aldo`;
  - MIT licensing;
  - the R223 regression / non-improvement result.

R384 does **not** invent an archive hash or per-file hashes for these coordinator-local bytes.

## 3. What R379 said, and the precise correction

R379 is immutable at:

- branch: `research/r379-aicrowd-preflight-20260924`
- head: `1f6931ea39f4bf28ca2cc0893ffa27bb8c2073e1`
- report: `research/r379/R379_AICROWD_PREFLIGHT.md`
- report blob: `69eebfc1b2f75b24e3eb480e5830610e31e83339`

R379 correctly established the **repository-visible** facts at R223 head
`09efbb920313850a4727bd34db9088a46227ce5f`:

- the R223 attempt-6 GitHub Actions artifact is a development/evidence ZIP, not itself a `whest package` tarball;
- the R223 workflow does not run `whest package`, `whest validate-package`, or `whest submit --dry-run`;
- no committed R223 `manifest.json` or `aicrowd-r223-submission.tar.gz` exists in that branch.

R384 rechecked the live R223 tree. The only exact-name root file among the relevant package names is repository `README.md`; there is no branch-committed `LICENSE-504aldo.txt`, `manifest.json`, or `aicrowd-r223-submission.tar.gz`.

Those statements remain valid **about repository-visible evidence**.

The following stronger R379 implications are superseded/narrowed:

### Superseded package conclusion

R379 wrote:

`NOT_BUILT_AS_AICROWD_SUBMISSION_PACKAGE / NOT_PACKAGE_VALIDATED`.

Corrected R384 status:

`EXTERNAL_LOCAL_PACKAGE_COORDINATOR_PROVIDED; EXACT_BYTES_AND_VALIDATION_UNVERIFIED_BY_R384`.

It is no longer justified to infer from the GitHub branch alone that no submission package was built outside the repository.

### Superseded attribution conclusion

R379 correctly observed that the repository copy of
`methods/r223_estimator_v25_local_feed.py`
(blob `eb95d4ae46a031be5131eef8dd0909f2061b8749`) does not itself contain a `504aldo`/MIT notice.

However, attribution does not need to be text embedded inside `estimator.py` if the submitted folder includes the required notice/disclosure files.

Given the coordinator-provided member list and README description, R384 changes the package-level attribution status from R379's effective “incomplete” to:

`COORDINATOR_PROVIDED_ATTRIBUTION_PRESENT; BYTE-LEVEL_VERIFICATION_UNKNOWN`.

The upstream licensing source remains:

- `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- MIT LICENSE blob `2c843327a87b547245b566f02391295ba71ad26a`.

The MIT license requires its copyright and permission notice to accompany copies or substantial portions. A separate `LICENSE-504aldo.txt` can satisfy that packaging obligation if its bytes contain the required notice; R384 cannot verify those bytes from this environment.

## 4. Version reconciliation: manifest 0.16.1/0.12.1 vs live evaluator 0.16.0/0.12.0

There is **no inherent contradiction**.

### 4.1 Manifest versions describe the packaging environment

Current official WhestBench source:

- repository: `AIcrowd/whestbench`
- head checked: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`
- `src/whestbench/packaging.py`
- blob: `26f9f1c07cdbbec40659ce150e31e77d3c553bd7`
- source:
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/packaging.py

Its `build_manifest()` writes:

- `whestbench_version = _installed_version("whestbench")`
- `flopscope_version = _installed_version("flopscope")`
- plus local Python and NumPy versions.

Therefore a manifest containing `whestbench 0.16.1 / flopscope 0.12.1` proves the package was **built in a local environment with those installed versions**. It does **not** assert that AIcrowd's production evaluator runs those versions.

### 4.2 Current official starter kit intentionally leads the grader by one patch

Current official starter kit:

- `AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`
- `pyproject.toml` blob:
  `2c1d562a2073046d6912868184b52c8c593d23c5`
- source:
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml

It pins local development to:

- `whestbench>=0.16.1,<0.17.0`
- `flopscope>=0.12.1,<0.13.0`

and explicitly states in the same primary source that:

- the grader is on `whestbench v0.16.0`;
- grader `flopscope[server]==0.12.0`;
- the starter kit leads the grader by one patch on each.

AIcrowd organizer discussion independently states that the evaluators actually run
`whestbench@v0.16.0` and `flopscope[server]==flopscope[client]==0.12.0`:
https://www.aicrowd.com/participants/mohanty

R384 found no explicit first-party deployment statement in the checked current sources superseding that production-version statement.

### 4.3 The v0.16.0 package validator does not require manifest package-version equality

Primary source checked directly at the evaluator-relevant tag:

https://github.com/AIcrowd/whestbench/blob/v0.16.0/src/whestbench/validation.py

The v0.16.0 `validate_package()` checks, among other things:

- manifest `schema_version` against supported `1.0`;
- manifest `api_version` against supported `2.0`;
- declared entrypoint presence;
- `files[]` structure;
- regular-file membership;
- SHA-256 integrity.

It does **not** reject an archive because manifest
`whestbench_version` or `flopscope_version`
differs from the evaluator's installed versions.

The v0.16.0 packager itself already records these installed-version fields:
https://github.com/AIcrowd/whestbench/blob/v0.16.0/src/whestbench/packaging.py

Thus a locally packaged 0.16.1/0.12.1 archive is structurally compatible with the v0.16.0 manifest contract **provided its schema/API/files/hashes are valid**. R384 cannot certify that particular coordinator-local archive without its bytes.

## 5. What changed in 0.16.1 / 0.12.1, and relevance to R223

Official WhestBench changelog:

- head: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`
- `CHANGELOG.md`
- blob: `fb2e2ababe42c7764fad4b99681445b65c75f7ad`
- source:
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/CHANGELOG.md

The v0.16.1 entry says:
- WhestBench raises the flopscope floor to 0.12.1;
- the new WhestBench public helper changes no score;
- the one documented price change reachable from the 0.12.1 patch is `full` / `full_like` with a **non-scalar** `fill_value`;
- no already-scored submission in the current phase used that case.

R384 also rechecked R223 estimator blob
`eb95d4ae46a031be5131eef8dd0909f2061b8749`:
it has **no calls to `fnp.full(...)` or `fnp.full_like(...)`**.

So the documented 0.12.1 price delta does not apply to the frozen R223 source through those operations.

This is a narrow compatibility observation, not a proof that every runtime behavior of 0.16.1/0.12.1 is byte-identical to the production 0.16.0/0.12.0 stack.

## 6. Offline `validate-package` outcome

**NOT RUN.**

Reason: the coordinator-local archive is outside this session's accessible filesystem.

R384 did not install WhestBench, download the archive, reconstruct it, or substitute another tarball.

Therefore the exact current status is:

- coordinator-local package existence: **COORDINATOR_PROVIDED**
- archive size/member list/manifest versions: **COORDINATOR_PROVIDED_UNVERIFIED_BY_R384**
- archive SHA-256: **UNKNOWN_TO_R384**
- member SHA-256 values: **UNKNOWN_TO_R384**
- `validate-package` outcome for those exact bytes: **UNKNOWN**
- repository-visible committed package: **NO**
- repository-visible official validation receipt for that external package: **NO / UNKNOWN**

If a later session obtains direct byte access to exactly this tarball, the correct bounded follow-up is:
1. compute SHA-256;
2. list exactly the four members;
3. read `manifest.json`, `README.md`, and `LICENSE-504aldo.txt`;
4. if a compatible validator is already installed, run offline `whest validate-package <exact tarball>`;
5. do **not** rebuild, install, download, login, or submit.

## 7. Scientific status is unchanged

Nothing in the package reconciliation changes the R223 scientific result.

Same-panel Mini-100:

- R209/V25 adjusted score:
  `8.170397440117225e-9`
- R223/V25-LF adjusted score:
  `8.171116513490029e-9`

R223 remains slightly worse than R209 and remains:

`R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED`.

A technically valid package would not make R223 a representative slot candidate.

## 8. Final corrected R379 interpretation

Use the following replacement interpretation for R379 Sections 2 and 7:

> The GitHub-visible R223 evidence does not contain a committed `whest package` tarball or package-validation receipt. Separately, the coordinator reports an external local 22,487-byte package containing `estimator.py`, `LICENSE-504aldo.txt`, `README.md`, and `manifest.json`, built under local WhestBench 0.16.1 / FlopScope 0.12.1, with README disclosure of 504aldo/MIT and the R223 regression. R384 cannot access those bytes, so exact hashes and `validate-package` status remain unknown. The manifest version pair describes the local packaging environment and does not contradict the first-party live-evaluator statement of WhestBench 0.16.0 / FlopScope 0.12.0. Scientific rejection of R223 is unchanged.

## 9. Execution accounting

- local Windows archive read: **NO — inaccessible**
- archive download: **0**
- package rebuild: **0**
- `validate-package` execution: **0**
- dependency install: **0**
- competition-data fetch/download: **0**
- benchmark/synthetic/estimator run: **0**
- Actions triggered: **0**
- AIcrowd login/eligibility check: **0**
- submission: **0**
- submission slots spent: **0**
- private/holdout/full access: **0**
- R379 edits: **0**
- R320/main/PR/control/queue edits: **0**
- R384 artifacts: exactly this Markdown report.
