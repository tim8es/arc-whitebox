# R379 — AIcrowd Phase-2 submission preflight

**Status:** COMPLETE — PREFLIGHT ONLY  
**Submission authorization:** **NOT AUTHORIZED / NOT REQUESTED**  
**Submission performed:** **NO**  
**Login / AIcrowd eligibility check performed:** **NO**

Exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
Branch: `research/r379-aicrowd-preflight-20260924`

R379 is a slot-conservation preflight. It does not submit, authenticate to AIcrowd, download competition data, access private/holdout data, or claim that R223 improves R209.

## 1. R223 V25-LF is a negative reference, not a submission candidate

R223 live branch:
`research/r223-v25-isolated-improvement-20260922`

Live head:
`09efbb920313850a4727bd34db9088a46227ce5f`

Frozen candidate source:
- `methods/r223_estimator_v25_local_feed.py`
- Git blob: `eb95d4ae46a031be5131eef8dd0909f2061b8749`
- attempt-6 SHA-256: `a62f2d2e580c38a77741c5316a8a88b8a52b97d676ecd4a38639ca2c6e5c422b`

Pinned parent V25:
- upstream repository: `504aldo/whest-p2-cumulant-k3`
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`.

### Attempt-6 validation/run evidence

GitHub Actions run:
- run id: `35810427656`
- head: `09efbb920313850a4727bd34db9088a46227ce5f`
- job id: `107020553482`
- workflow blob: `d24e3f63e8ce447188868846e9b3e4ef755b395e`
- conclusion: **success**

The successful workflow:
1. verified the frozen candidate transform and `target_access=false`;
2. verified the immutable R209 parent artifact inside that historical run;
3. ran `whest validate --json` and required exit code 0;
4. ran exactly one same-panel Mini-100 candidate test;
5. produced a paired 100-row result;
6. uploaded an immutable evidence artifact.

Attempt-6 evidence artifact metadata:
- artifact id: `10730459690`
- name: `r223-v25-local-feed-mini100-attempt6`
- size: `261400` bytes
- GitHub artifact ZIP SHA-256 reported by upload step:
  `f144bfd2a5a8a82aaa3e600d1f384d68cfe5e525eb7e22e91eb1d7e843763e00`
- expiry recorded by GitHub: `2026-12-22T02:27:31Z`.

R379 did **not** download this artifact.

### R223 result versus R209

R209/V25 control:
- mean raw final MSE: `2.228303490170447e-8`
- mean adjusted score: `8.170397440117225e-9`
- mean C/B: `0.36666448157347986`.

R223/V25-LF:
- failures: `0/100`
- mean raw final MSE: `2.2284993050902814e-8`
- mean adjusted score: `8.171116513490029e-9`
- mean effective compute: `806303829485`
- mean C/B: `0.36666453046791503`
- max residual: `0.19380312699274782 s`
- improved networks: `50/100`
- paired parent-minus-candidate adjusted delta mean:
  `-7.190733728024271e-13`
- paired delta mean / SE: `-0.48188156603559223`.

Frozen result decision:
`R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED`.

**Therefore R223 is not an improvement.** It is slightly worse than R209 in both raw MSE and adjusted score on the same Mini-100 panel. Spending an AIcrowd slot on it would not satisfy this preflight's scientific admission condition.

The Mini-100 panel is also not proven identical/joinable to the competition public-50 subset; prior R319/R322 evidence remains `NOT_COMPARABLE / NOT_JOINABLE`. A Mini-100 comparison is an internal same-panel gate, not a leaderboard prediction.

## 2. R223 artifact is not a verified AIcrowd submission package

The attempt-6 artifact is a **development/evidence ZIP**, not a `whest package` submission tarball.

The R223 attempt-6 workflow never executes:
- `whest package`;
- `whest validate-package`;
- `whest submit --dry-run`;
- `whest submit`.

No committed R223 `manifest.json` or submission `.tar.gz` exists at the live R223 head.

The artifact instead contains the evidence directory plus frozen protocols, candidate source, and comparison/verification scripts.

So the honest package status is:

**NOT_BUILT_AS_AICROWD_SUBMISSION_PACKAGE / NOT_PACKAGE_VALIDATED.**

## 3. Current official Phase-2 execution requirements

Current official Phase-2 sources checked on 2026-09-24:

### Official launch / rules summary

AIcrowd's Phase-2 launch announcement currently states:
- MLP shape: **1024 wide × 16 deep**;
- per-MLP FLOP budget: **2^41 = 2,199,023,255,552**;
- wall cap: **120 s per MLP**;
- computation outside flopscope: **prohibited**;
- residual wall time: **0.4 s hard cap**;
- solution-process memory: **8 GB**;
- submissions: **10 per team per UTC day**;
- Phase-2 submission deadline: **2026-10-17 23:59 UTC**;
- registration/team-freeze deadline: **2026-10-02 23:59 UTC**.

The organizer also states that the evaluator actually runs:
- `whestbench==0.16.0`;
- `flopscope[client]==0.12.0`;
- `flopscope[server]==0.12.0`.

The current official starter kit main is:
`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`.

Its current local-development constraints pin:
- `whestbench>=0.16.1,<0.17.0`;
- `flopscope>=0.12.1,<0.13.0`.

The starter kit explicitly documents that it is one patch ahead of the live grader. A future candidate should therefore record compatibility with both the current starter-kit preflight environment and the published live grader contract; version proximity alone is not proof.

### Estimator contract

Official estimator contract blob:
`43c1494420b46aad4bc1dbbab83528eca6b89668`.

Required:
- `predict(self, mlp, budget)`;
- output shape `(mlp.depth, mlp.width)`, Phase 2 `(16,1024)`;
- all output values finite;
- `setup()` optional, idempotent, hard cap **5 s per worker**;
- FLOPs through flopscope;
- failure of an MLP due to shape/nonfinite/exception/FLOP/wall/residual limits causes zero predictions for that MLP;
- setup timeout fails the whole submission.

Randomness must use grader seeds:
- `ctx.seed` in setup;
- `mlp.seed` in predict.

## 4. What `whest validate` does — and does not prove

Official validation docs:
- starter-kit stage-2 blob:
  `615f737026f501d7d50afa54b7581da5af6e46ae`;
- current whestbench validator source:
  `AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c`,
  `src/whestbench/cli.py` blob
  `f214a0e210aa2cd10d0d0a68b14a2b1341b4091f`.

It checks a small probe for:
- estimator class resolution;
- setup execution/timing;
- return shape;
- finite values.

Important official warning: the rich **Checks table** must be inspected. A setup-time check can be reported as failed while the command still has a superficially successful status/exit behavior; `--json` does not preserve the full checks table.

R223 attempt-6 used `whest validate --json` and exit 0. That is useful historical contract evidence, but it is **not sufficient current pre-submission proof by itself**.

R223's source statically has a minimal setup:
`self._setup_rng = fnp.random.default_rng(ctx.seed)`,
and its 100-row run completed, but a future candidate must still archive the rich validation checks under the final package source.

## 5. Package structure and integrity checks

Official package docs:
- Stage 5 blob:
  `1b4009b6c7ae7db0a49a7ff82f9ecd653bba79eb`;
- ship-weights blob:
  `1e8dc52cd52bb4858de0aea0e6ca07354e7b4055`.

Current whestbench package sources:
- `src/whestbench/packaging.py`:
  `26f9f1c07cdbbec40659ce150e31e77d3c553bd7`;
- `src/whestbench/validation.py`:
  `d9c81db3f171a28d6b85ac8b4a2de1879fef02c0`;
- `src/whestbench/limits.py`:
  `77d3109367c646a50c5b8c19cba0826ba8533f8b`.

Single-file packaging:
- ships `estimator.py` plus generated `manifest.json`.

Folder packaging:
- requires root `estimator.py`;
- ships non-ignored regular files;
- appropriate for helper modules, data and attribution notices.

Hard package caps:
- **50 MiB total bundled file bytes**;
- **50 files**.

Manifest/integrity validation checks:
- readable gzip tar;
- readable valid `manifest.json`;
- supported schema/API version;
- declared estimator entry module present;
- `files[]` valid;
- each declared entry is a regular file and exists;
- per-file SHA-256 matches;
- directory/special-file entries are rejected.

`whest submit` runs local package validation before upload. The current CLI also supports:
`whest submit --estimator ... --dry-run`,
which packages and runs the same local archive-integrity check without submitting.

R379 did not execute any of these package commands.

## 6. Allowed code and what AIcrowd actually reviews

Official Allowed Code blob:
`525276e8e5bc7f6a7dd54e876140ab0df514be32`.

Phase 2 permits:
- grader Python;
- flopscope client API;
- whestbench contract types;
- pure-Python standard library for control/plumbing;
- shipped data files such as pickle-free weights/lookup tables.

Prohibited/disqualifiable:
- vendored numpy/scipy/BLAS;
- compiled kernels;
- ctypes/cffi/FFI;
- asyncio/threads/subprocess/multiprocessing;
- computation while a flopscope op is in flight;
- touching/replacing flopscope transport or accounting;
- meaningful numerical compute hidden in residual time;
- accounting-benefit packing of independent values.

AIcrowd documents layered enforcement:
1. package/manifest integrity checks before execution;
2. automated checks on every submission;
3. flagged cases receive agent-assisted validation;
4. unresolved cases receive human review;
5. review may continue after grading; nonconforming submissions can be invalidated later.

Therefore a successful local score or even a successful grader score is **not** an eligibility ruling.

### Static R223 source review

Current R223 estimator imports:
- `math`;
- `os`;
- `flopscope`;
- `flopscope.numpy`;
- whestbench contract types;
- a dev-only `local_engine` import under `if __name__ == "__main__"`.

No direct numpy/scipy import and no textual use of ctypes/cffi/threading/multiprocessing/subprocess/asyncio/concurrent.futures/network clients was found.

For a future submission source, remove the dev-only `__main__` / `local_engine` harness from the shipped `estimator.py` to eliminate an avoidable sandbox/static-review ambiguity.

## 7. Attribution / license preflight

Pinned V25 upstream is MIT:
- `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- LICENSE blob:
  `2c843327a87b547245b566f02391295ba71ad26a`;
- copyright:
  `Copyright (c) 2026 504aldo`.

The MIT license permits use and modification but requires the copyright and permission notice to be included in copies or substantial portions.

AIcrowd Participation Terms §4.1 additionally require the participant, upon submission, to clearly identify embedded/used third-party materials and describe their licensing terms.

Current R223 estimator contains no `504aldo`, MIT-license, or copyright notice, and the R223 branch contains no R223 submission `THIRD_PARTY_NOTICES`/LICENSE package artifact.

Thus:
- **technical reuse permission:** confirmed by upstream MIT;
- **current R223 submission attribution package:** incomplete;
- **future submission requirement:** include the upstream MIT notice and explicit third-party disclosure before any authorized submit.

A clean folder package should normally contain at least:
- `estimator.py`;
- `THIRD_PARTY_NOTICES.md` (or equivalent), including the pinned upstream repo/commit and MIT notice;
- only genuinely required data/helper files;
- generated `manifest.json`.

The disclosure also needs to be reflected in whatever submission metadata/write-up is required at the time of actual authorized submission.

## 8. Exact slot-conservation gate for a future candidate

A future candidate should **not reach package/upload authorization** until all of these are complete.

### A. Scientific admission — internal, not an AIcrowd rule

1. Frozen candidate source/config/hashes.
2. Same Mini-100 panel identity with R209:
   - dataset SHA `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`;
   - names/order SHA `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`.
3. Zero candidate failures.
4. Mean raw MSE **strictly below** R209 `2.228303490170447e-8`.
5. Mean adjusted score **strictly below** R209 `8.170397440117225e-9`.
6. Prefer the already-frozen R223 anti-noise development gate before spending a slot:
   adjusted score `<= 8.129545452916639e-9` (0.5% better), at least 55/100 improved, and paired mean improvement (>2 SE).
7. No new cost/runtime regression that compromises Phase-2 limits.

This gate only proves same-panel development superiority. It does not prove competition public-50 improvement.

### B. Current contract / rule preflight

8. Static allowed-code review against final shipped source.
9. Remove dev-only/non-shipped imports.
10. Rich `whest validate` Checks table: every row OK; archive human-readable output.
11. Local 3-MLP and subprocess 3-MLP runs under the official checklist; scores within about 1%.
12. Final bounded run evidence shows, for every tested MLP:
    - no FLOP exhaustion;
    - no wall timeout;
    - no residual timeout;
    - residual <0.4 s;
    - 120 s cap respected;
    - setup <5 s;
    - memory comfortably <8 GB.
13. Reproducibility seeds use only `ctx.seed` / `mlp.seed`.
14. Record current starter-kit tooling and explicit compatibility review for the published live grader pins 0.16.0/0.12.0.

### C. Package/license preflight

15. Create a clean submission directory with root `estimator.py`.
16. Include required MIT attribution / third-party notice.
17. Package only required files; <=50 files and <=50 MiB.
18. Run `whest package`.
19. Inspect the file list and `manifest.json`; record archive SHA-256.
20. Run `whest validate-package`.
21. Run `whest submit --estimator . --dry-run`; confirm no upload and save the preview/integrity result.
22. Freeze the exact package hash and source-to-package provenance.

### D. Authorization immediately before real submission

23. Obtain explicit coordinator authorization for one submission slot.
24. Only then authenticate/check AIcrowd eligibility/team quota.
25. Reconfirm the current deadline/rules and that a slot is available.
26. Submit the already-frozen package without rebuilding it.

R379 authorizes **none** of steps 23–26.

## 9. Authorization status

`authorization_status = PREPARED_NOT_AUTHORIZED_TO_SUBMIT`

- No user/coordination instruction in R379 authorizes a real submission.
- No AIcrowd login was opened.
- No API key/identity/eligibility check was performed.
- Team quota/remaining slots are **UNKNOWN**.
- No package was uploaded.
- No submission id was created.
- R223 is specifically **NOT_ELIGIBLE_FOR_SLOT_BY_INTERNAL_SCIENCE_GATE** because it is worse than R209.

The next real submission should be a separately frozen candidate that first passes sections 8A–8C and then receives explicit slot authorization.

## 10. Execution accounting

R379 itself:
- estimator/benchmark/synthetic run: **0**
- Actions triggered: **0**
- competition-data download: **0**
- artifact download: **0**
- AIcrowd login/authentication: **0**
- submission: **0**
- private/holdout/full access: **0**
- R320/main/PR/control/queue edits: **0**
- report-only branch artifacts: exactly this report + JSON checklist.
