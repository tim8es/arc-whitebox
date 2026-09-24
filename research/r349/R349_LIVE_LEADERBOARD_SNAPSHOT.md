# R349 — coordinator-recovered live public Phase-2 leaderboard snapshot + R304 first-page delta

**Status:** COMPLETE  
**Mode:** report-only persistence of coordinator CUA capture + bounded first-page display delta  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r349-live-leaderboard-snapshot-20260924`

## Current snapshot provenance

This artifact persists a later coordinator-recovered public leaderboard snapshot. The coordinator used the user's Chrome UI with CUA on the official public Phase-2 leaderboard.

Official URLs:
- page 1: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2
- page 2 route attempted: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2&page=2

The direct `?page=2` URL was ignored by client state. The coordinator instead clicked the visible pagination button `2` in the UI. No submission pages were opened.

Capture UTC: **2026-09-24T12:20:18.917Z**

Verified UI ranges:
- page 1: **Showing 1–100 of 197**, 100 visible rows
- page 2: **Showing 101–197 of 197**, 97 visible rows
- total visible board: **197**
- cells per visible row: **10**

The compact `JSON.stringify` of concatenated current page-1 then page-2 row-cell arrays was:
- UTF-8 byte length: **21,732**
- SHA-256: **`a16f4399d9c71e869a1199285584148066746204ebe66a54c22d254b954e81bf`**

The raw 197 row arrays were retained in the coordinator browser session, but **are not committed as a GitHub file in R349**. This branch contains only this report and its JSON receipt.

R349 does not edit, supersede, or erase R341's earlier partial capture or R345's earlier pagination blocker report.

## R304 first-page baseline

Independently verified baseline:
- branch: `review/r304-leaderboard-delta-20260924`
- head: `fcff8898104a21431eb9e1a5eec0f5cb6bb00468`
- capture UTC: `2026-09-24T02:36:19.062Z`
- displayed range: **Showing 1–100 of 195**
- visible rows: **100**
- raw artifact blob: `2fee6241febe322fbff2cbc605581590fc072ee6`
- raw file SHA-256: `807df449176bd1cde98e6da418f30aa4aba848c9767a7e44196385587f17b016`
- normalized rows SHA-256: `4ffcdf469435f3b6dd55df39b6a06c3b5a186b7de89251a526254169a0fbe0d5`

R304 did not capture its historical page 2. Therefore the historical full-board delta remains UNKNOWN.

## Exact display-cell-3 identity comparison: current first 100 vs R304 first 100

Both sides contain 100 first-page rows.

- exact shared display identities: **95**
- old-only display strings: **5**
- current-only display strings: **5**

Old-only:
- `DO dogus_ozel —`
- `ED edo2 —`
- `NK DancinGirl 1 member`
- `CW cwc —`
- `EL ely2sh —`

Current-only:
- `DO Luna 1 member`
- `ED edo2 None`
- `NK DancinGirl 1 member · CSU`
- `CL clawdia —`
- `EX exploringsolver —`

These string differences **must not be interpreted as five exits and five entrants**. In particular, DO/ED/NK may reflect team or metadata/display changes rather than identity turnover.

Additional observed placement context:
- `cwc` is present on current page 2 at rank **101**
- `ely2sh` is present on current page 2 at rank **102**
- `clawdia` and `exploringsolver` are present in the current first 100 but were absent from the R304 first 100; they may have been below rank 100 historically

Because historical R304 page 2 was never captured, exact historical placement for those names outside the first 100 is not available.

## Delta among 95 exact shared display identities

Among the 95 exact display identities shared between R304 first 100 and the current first 100:

- displayed rank changed: **64**
- displayed Adjusted Score changed: **13**
  - numerically lower: **13**
  - numerically higher: **0**
- displayed Final Layer MSE changed: **10**
  - lower: **9**
  - higher: **1**
- Entries changed: **22**
- exact date+time portion of Last Submission changed: **13**

These are display-level comparisons only.

## J2W display delta

J2W remains displayed rank 1.

R304 → current:
- Adjusted Score: **`2.10e−9` → `2.00e−9`**
- Final Layer MSE: **`1.64e−8` → `1.61e−8`**
- sampling ratio: **`539×` → `566×`**
- Entries: **320 → 323**
- Last Submission display: **Sep 19 00:05 → Sep 24 08:55**

These are UI display values. The exact unrounded score is UNKNOWN.

## Scope and interpretation boundaries

The UI total changed from **195** at R304 to **197** at the current R349 snapshot. This is a verified UI-count change only.

R349 does **not** claim:
- exact full-board additions/removals between the two times;
- exact historical page-2 membership or movement;
- that the five first-page string replacements represent five exits and five entrants;
- an exact unrounded leaderboard score delta;
- a true score gap to R209;
- any leaderboard placement prediction or estimator inference.

Reason: R304 never captured historical page 2, so full historical board membership cannot be reconstructed.

Leaderboard ↔ R209/public-50 identity remains **NOT_COMPARABLE / NOT_JOINABLE**. No placement or gap inference is made.

## Execution accounting

- coordinator browser/CUA capture: **YES, public leaderboard only**
- submission pages opened: **NO**
- benchmark/estimator run: **NO**
- GitHub Actions: **NO**
- downloads/installs: **NO**
- private/holdout/full data access: **NO**
- competition submission: **NO**
- main edit: **NO**
- PR edit: **NO**
- control edit: **NO**
- queue edit: **NO**
- branch artifacts: **exactly report + JSON receipt**
