# R315 — public Configuration/metadata audit for submissions #331931 and #331953

## Scope

Public, unauthenticated AIcrowd first-party surfaces only for the two canonical Phase-2 submissions requested:

- `#331931` — `suliman_tadros`
- `#331953` — `marius_binner`

No score/rank inference, no general forum scan, no participant contact, no login, no private/holdout/full access, no download, no benchmark, no Actions, no submission, and no main/PR/control edit.

- Exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Report-only branch: `review/r315-top2-top3-config-audit-20260924`
- Capture time: `2026-09-24T09:47:54.311419Z` UTC

## Canonical submission linkage

The current official Phase-2 leaderboard directly links the requested participants to the canonical submission pages:

| participant | submission ID | canonical first-party URL |
|---|---:|---|
| suliman_tadros | 331931 | https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331931 |
| marius_binner | 331953 | https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953 |

Leaderboard source:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

## Public submission-page audit

Both canonical submission URLs are publicly reachable without authentication. In the current unauthenticated first-party text capture, however, the submission-detail body is client-rendered and the captured DOM exposes only the generic page shell plus `Share` / `Copy URL`; it does not expose target-specific Configuration values or any participant method metadata.

### #331931 — suliman_tadros

Direct page:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331931

Observed public linkage fields:

- estimator / method name: **not publicly verified**
- participant-selected estimator parameters or algorithm configuration: **not publicly verified**
- source-code link: **none exposed in the captured public page surface**
- repository link: **none exposed in the captured public page surface**
- direct method/write-up link tied to submission `331931`: **none exposed in the captured public page surface**
- grading/evaluator Configuration payload: **not present in the captured text DOM; no values are inferred**

Verdict: **NO_PUBLIC_METHOD**.

### #331953 — marius_binner

Direct page:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953

Observed public linkage fields:

- estimator / method name: **not publicly verified**
- participant-selected estimator parameters or algorithm configuration: **not publicly verified**
- source-code link: **none exposed in the captured public page surface**
- repository link: **none exposed in the captured public page surface**
- direct method/write-up link tied to submission `331953`: **none exposed in the captured public page surface**
- grading/evaluator Configuration payload: **not present in the captured text DOM; no values are inferred**

Verdict: **NO_PUBLIC_METHOD**.

## Interpretation boundary

This audit does **not** infer a method from leaderboard position, score, compute utilization, participant identity, unrelated forum posts, or techniques published by other participants. A method/code association requires a direct public first-party link to the exact submission ID. No such linkage was visible for either target submission in the audited public surfaces.

The failure of the current text capture to expose the client-rendered Configuration payload is recorded as an evidence limitation, not converted into invented configuration values. The conclusion is correspondingly narrow: **no public method/code linkage was verified for #331931 or #331953**.

## Result

| submission | participant | public method/code linkage |
|---:|---|---|
| 331931 | suliman_tadros | `NO_PUBLIC_METHOD` |
| 331953 | marius_binner | `NO_PUBLIC_METHOD` |

No other R306/R307/R312 participant audit was repeated.
