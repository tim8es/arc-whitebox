# R310 — public Phase-2 leaderboard top check

## Scope and constraints

Read-only audit of the public AIcrowd leaderboard only. Comparator: frozen R304 public snapshot. No benchmark, Actions, dataset/download, package install, submission, main/PR/control edit, or inference from anonymous rows. R307 owns the separate AndreasHad04 method/submission audit; R310 does not analyze that participant.

- Exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Report-only branch: `review/r310-leaderboard-top-check-20260924`
- Current public leaderboard URL fetched: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
- Snapshot time: `2026-09-24T09:29:17.177839Z` UTC
- Pagination review-correction capture: `2026-09-24T09:34:58Z` UTC; exact visible string: `Showing 1–100 of 197`; page count: `2`
- Frozen comparator: R304 raw capture `research/r304/R304_RAW_VISIBLE_ROWS.json`, blob `2fee6241febe322fbff2cbc605581590fc072ee6`, commit `5351f455c87afdd6eb3a4147e94c38d191968d18`
- R304 capture time: `2026-09-24T02:36:19.062Z` UTC
- R304 source URL recorded in its receipt: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2

## Current first 20 visible rows

Scores below preserve the exact decimal strings exposed by the current public leaderboard DOM. Submission IDs are taken from each row's public `View` link target.

| visible row | displayed rank | participant | submission ID | adjusted score (exactly as shown) | Entries |
|---:|---:|---|---:|---:|---:|
| 1 | 01 | J2W | 331539 | 0.0000000021 | 321 |
| 2 | 02 | suliman_tadros | 331931 | 0.0000000022 | 52 |
| 3 | 03 | marius_binner | 331953 | 0.0000000023 | 158 |
| 4 | 04 | a_s6 | 331756 | 0.0000000025 | 108 |
| 5 | 05 | Luna | 332100 | 0.0000000026 | 7 |
| 6 | 06 | Puffi | 330322 | 0.0000000028 | 78 |
| 7 | 06 | reds | 331730 | 0.0000000028 | 60 |
| 8 | 08 | oqaris | 330951 | 0.0000000031 | 93 |
| 9 | 08 | ben3 | 331882 | 0.0000000031 | 23 |
| 10 | 08 | mliston | 332026 | 0.0000000031 | 41 |
| 11 | 11 | Camaro | 331734 | 0.0000000033 | 68 |
| 12 | 11 | MeatProxy | 332060 | 0.0000000033 | 12 |
| 13 | 13 | thegamers | 330514 | 0.0000000036 | 38 |
| 14 | 13 | hyojun_kwon | 332017 | 0.0000000036 | 116 |
| 15 | 13 | emanuel_ruzak | 332103 | 0.0000000036 | 4 |
| 16 | 16 | shiv_m | 332013 | 0.0000000037 | 125 |
| 17 | 16 | lode_dockx | 332122 | 0.0000000037 | 81 |
| 18 | 18 | jlacombe | 332114 | 0.0000000039 | 45 |
| 19 | 19 | fklassen | 331831 | 0.0000000040 | 40 |
| 20 | 20 | thibault_gounant | 331819 | 0.0000000041 | 131 |

Public submission targets:
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331931
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331756
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332100
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330322
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331730
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330951
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331882
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332026
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331734
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332060
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330514
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332017
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332103
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332013
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332122
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332114
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331831
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331819

## First place

J2W remains first. R304 showed rank `01`, score `2.10e−9`; the current page shows rank `01`, score `0.0000000021`. Those are the same displayed rounded value in different rendering formats. No exact unrounded score is exposed by this page, so no more precise delta is claimed.

## Delta from R304

R304's first 20 visible rows were:
`J2W, suliman_tadros, marius_binner, a_s6, dogus_ozel, Puffi, reds, oqaris, ben3, mliston, Camaro, MeatProxy, thegamers, hyojun_kwon, shiv_m, emanuel_ruzak, fklassen, thibault_gounant, lode_dockx, LuDoe`.

Current first 20 visible rows:
`J2W, suliman_tadros, marius_binner, a_s6, Luna, Puffi, reds, oqaris, ben3, mliston, Camaro, MeatProxy, thegamers, hyojun_kwon, emanuel_ruzak, shiv_m, lode_dockx, jlacombe, fklassen, thibault_gounant`.

Changes in the first-20-row set:
- entered: `Luna`, `jlacombe`
- left: `dogus_ozel`, `LuDoe`

Material displayed rank/score changes among rows present in both first-20 snapshots:
- `emanuel_ruzak`: R304 rank 16 / `3.80e−9` → current rank 13 / `0.0000000036`.
- `shiv_m`: R304 rank 15 / `3.70e−9` → current rank 16 / `0.0000000037` (score unchanged at displayed precision).
- `lode_dockx`: R304 rank 19 / `4.20e−9` → current rank 16 / `0.0000000037`.
- `fklassen`: R304 rank 17 / `4.00e−9` → current rank 19 / `0.0000000040` (score unchanged at displayed precision).
- `thibault_gounant`: R304 rank 18 / `4.10e−9` → current rank 20 / `0.0000000041` (score unchanged at displayed precision).

Tie note: R304 had three displayed rank-19 rows; therefore `jlacombe` was row 21 while still carrying displayed rank 19. If "top-20" is defined as displayed rank <=20 instead of the first 20 table rows, R304 contained 21 rows and included `jlacombe`. R310 uses "first 20 visible rows" for the primary set comparison and records this tie explicitly.

Review correction capture at `2026-09-24T09:34:58Z` UTC from the official Phase-2 UI/DOM shows the exact visible range string `Showing 1–100 of 197`. The visible pagination controls are `Previous page` (disabled), `1`, `2`, and `Next page`; therefore the leaderboard currently displays 197 records across 2 pages. This supersedes the earlier R310 statement `NOT_DISPLAYED_IN_CAPTURED_PUBLIC_DOM`.

## Exclusions and interpretation guardrails

- No exact gap to any ARC estimator is computed or implied.
- No anonymous/public leaderboard row is linked to project code.
- AndreasHad04 is outside the current first 20 (displayed rank 22 on the page) and is not analyzed here; R307 owns that audit.
- This is a public leaderboard snapshot/delta only. No causal conclusion is drawn from rank or score movements.

## Evidence

Official current leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

Frozen R304 comparator:
https://github.com/tim8es/arc-whitebox/blob/5351f455c87afdd6eb3a4147e94c38d191968d18/research/r304/R304_RAW_VISIBLE_ROWS.json

R304 full-delta audit:
https://github.com/tim8es/arc-whitebox/blob/fcff8898104a21431eb9e1a5eec0f5cb6bb00468/research/r304/R304_FULL_DELTA_AUDIT.md
