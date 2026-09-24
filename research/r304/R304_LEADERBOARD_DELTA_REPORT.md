# R304 — AIcrowd Phase-2 leaderboard delta

Status: COMPLETE. Owner: `r304-live-board-delta-statistician`. Run: `R304-live-leaderboard-poll-20260924-0230`.

Captured from the reloaded [official Phase-2 leaderboard](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2) at **2026-09-24T02:36:19.062Z**. AIcrowd displayed Phase 2 as LIVE and “Showing 1–100 of 195.”

Baseline: [R303 receipt](https://github.com/tim8es/arc-whitebox/blob/0c15bee860dc1d22224dd1294fcaa82bca26b8a4/research/r303/R303_RECEIPT.json), captured 2026-09-24T02:07:55.431Z.

## Delta

**Changed.** The leader remains J2W at rank 01, displayed adjusted score **2.10e−9** (three significant digits; exact unrounded score UNKNOWN), final-layer MSE 1.64e−8, 539× sampling reference, and 320 entries. These leader fields match R303.

Among the first ten rows, positions 1–4 and 6–10 match R303 across its eight recorded fields. Row 5 (dogus_ozel) has the same rank, score, MSE, sampling ratio, entry count, and absolute submission time; only the relative-age text advanced from “49 min ago” to “1 h ago.”

A scored change appears at AndreasHad04:

| Field | R303 | Current |
|---|---:|---:|
| Visible position / displayed rank | 30 / 28 | 26 / 25 |
| Δ indicator | ▲9 | ▲12 |
| Adjusted score (displayed) | 4.90e−9 | 4.70e−9 |
| Final-layer MSE | 2.12e−8 | 2.00e−8 |
| VS sampling approx. | 231× | 241× |
| Entries | 56 | 56 |
| Last submission | Sep 23, 12:15 · 13 h ago | Sep 24, 01:22 · 1 h ago |

This insertion moves pricop_tudor and Hack2Publish from visible positions 26–27 / rank 26 to positions 27–28 / rank 27, and drmohammad_banisalman and sophie549 from positions 28–29 / rank 28 to positions 29–30 / rank 29. The page total remains 195.

## Deadline and limits

AIcrowd’s [Phase-2 announcement](https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197) states submissions close **2026-10-17 23:59 UTC**. See also the [official rules](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules).

No R209/R223 numeric reconciliation was made: R303/R271 leave the exact visible-50 panel identity join unresolved, so no exact gap or rank is claimed. R304 checked the leader, first ten rows, and the affected neighborhood; it did not recompare/hash all 100 rows, so changes elsewhere are UNKNOWN.

The live AIcrowd page loaded. Browser access to `raw.githubusercontent.com` returned `net::ERR_BLOCKED_BY_CLIENT`; R303 was read through the GitHub repository connector. Text extraction of the AIcrowd rules page returned only a loading shell, so the deadline is sourced from AIcrowd’s official announcement.

No Actions, benchmark/estimator, data or dependency downloads, paid resources, private/holdout/full access, submission, leaderboard/canonical edits, or contact occurred.
