# R367 — public Phase-2 leaderboard top-10 UI attestation

**Status:** COMPLETE  
**Classification:** PUBLIC_UI_ATTESTATION_TOP10_ONLY  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r367-live-leaderboard-top10-capture-20260924`

## Provenance

Source URL:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2

This report persists a **read-only coordinator-provided CUA capture** from the official public Phase-2 leaderboard. No additional browser interaction was performed by R367.

Capture time supplied by the coordinator: **approximately `2026-09-24T14:26:07Z`**. R367 does not claim an independently observed browser timestamp more precise than that coordinator-provided value.

Visible UI range: **`Showing 1–100 of 197`**.

Only the first 10 visible rows and only the fields explicitly supplied by the coordinator are recorded below. No full-board archive is available from this capture.

## First 10 visible rows

| Rank | Participant / team | Affiliation / members | Adjusted Score | Final Layer MSE | Sampling | Entries | Last Submission |
|---|---|---|---:|---:|---:|---:|---|
| 01 | J2W / joe_wanza | Numascale AS / 1 member | 2.00e-9 | 1.61e-8 | 566× | 325 | Sep 24 08:55 |
| 02 | suliman_tadros | — | 2.20e-9 | 1.63e-8 | 514× | 52 | Sep 23 01:42 |
| 03 | marius_binner | University of Bergen | 2.30e-9 | 1.56e-8 | 492× | 158 | Sep 23 06:46 |
| 04 | a_s6 | — | 2.50e-9 | 2.00e-8 | 453× | 108 | Sep 21 13:55 |
| 05 | dogus_ozel / Luna | 1 member | 2.60e-9 | 1.67e-8 | 435× | 7 | Sep 24 03:32 |
| 06 | Cipo / lawrence_dam / andrew_epstein — Puffi | 3 members | 2.80e-9 | 1.94e-8 | 404× | 78 | Sep 8 14:09 |
| 06 | Oldboy / reds | 1 member | 2.80e-9 | 1.73e-8 | 404× | 60 | Sep 21 08:47 |
| 08 | oqaris | Sobolev Institute of Mathematics | 3.10e-9 | 2.15e-8 | 365× | 93 | Sep 14 05:56 |
| 08 | ben3 | Max Planck Institute for Intelligent Systems | 3.10e-9 | 1.68e-8 | 365× | 23 | Sep 22 19:38 |
| 08 | mliston | — | 3.10e-9 | 1.80e-8 | 365× | 41 | Sep 23 14:50 |

The table above is a transcription of the coordinator-supplied visible cells only. It does not add movement markers, hidden links, relative-time text, submission IDs, or any other fields not supplied for this capture.

## R359 leader-row comparison

Prior R359 evidence is preserved separately on branch `review/r359-live-leaderboard-top10-capture-20260924`, head `314750b3456138a91295213ed5019899011fcd3e`.

R359 leader row:
- J2W / joe_wanza
- rank 01
- Adjusted Score `2.00e-9`
- Final Layer MSE `1.61e-8`
- sampling `566×`
- entries **324**

R367 leader row:
- same displayed rank `01`
- same displayed Adjusted Score `2.00e-9`
- same displayed Final Layer MSE `1.61e-8`
- same displayed sampling `566×`
- entries **325**

Therefore the only asserted R359→R367 leader-row change is the **displayed Entries count 324→325**. R367 does not infer that the exact score moved.

## Interpretation boundaries

This artifact is **public UI attestation only**.

The following remain **UNKNOWN / NOT_COMPARABLE**:
- exact unrounded leaderboard scores;
- leaderboard formatter/rounding interval;
- full-board additions, removals, or rank deltas outside the persisted top 10;
- true contest-score gap;
- R209 ↔ public-50 score identity/comparability;
- any placement implication for our work.

R367 does **not** imply our score moved and does **not** predict rank.

## Scope / execution accounting

- additional browser interactions by R367: **0**
- submission pages opened: **0**
- estimator runs: **0**
- benchmark runs: **0**
- GitHub Actions: **0**
- downloads/installs: **0**
- paid resources: **0**
- private/holdout/full access: **0**
- submissions: **0**
- main edits: **0**
- PR edits: **0**
- R320 edits: **0**
- control/queue edits: **0**
- branch artifacts: **exactly this report + one JSON receipt**
