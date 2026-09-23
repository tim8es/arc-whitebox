# R280 — fresh Phase-2 standings and public-method disclosure scan

Observed: 2026-09-23 15:27 UTC / 18:27 MSK.

Scope was strictly read-only public evidence: official AIcrowd Phase-2 standings plus primary public forum/profile artifacts. No submission, Actions, paid compute, private/holdout data, leaderboard mutation, or canonical edit.

## Fresh official standings

Official source: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

Top visible rows at the observation timestamp:

| Rank | Participant | Adjusted score | Final-layer MSE | Compute utilisation | Failed | Entries | Last submission |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | J2W | 2.1e-9 | 1.64e-8 | 0.1306572576 | 0 | 312 | 2026-09-19 00:05 UTC |
| 2 | suliman_tadros | 2.2e-9 | 1.63e-8 | 0.1375978303 | 0 | 45 | 2026-09-23 01:42 UTC |
| 3 | marius_binner | 2.3e-9 | 1.56e-8 | 0.1474118618 | 0 | 158 | 2026-09-23 06:46 UTC |
| 4 | a_s6 | 2.5e-9 | 2.00e-8 | 0.1258033415 | 0 | 106 | 2026-09-21 13:55 UTC |
| 5 | Puffi | 2.8e-9 | 1.94e-8 | 0.1456939183 | 0 | 78 | 2026-09-08 14:09 UTC |
| 5 | reds | 2.8e-9 | 1.73e-8 | 0.1623309082 | 0 | 59 | 2026-09-21 08:47 UTC |
| 7 | oqaris | 3.1e-9 | 2.15e-8 | 0.1459882369 | 0 | 93 | 2026-09-14 05:56 UTC |
| 7 | ben3 | 3.1e-9 | 1.68e-8 | 0.1838821710 | 0 | 23 | 2026-09-22 19:38 UTC |
| 9 | mliston | 3.2e-9 | 1.81e-8 | 0.1756230281 | 0 | 39 | 2026-09-23 10:13 UTC |
| 10 | Camaro | 3.3e-9 | 1.90e-8 | 0.1754820884 | 0 | 68 | 2026-09-21 09:26 UTC |

The leader remains J2W at 2.1e-9. Relative to R263/R264, the notable fresh movement is immediately below the leader: suliman_tadros is now visible at #2 and marius_binner at #3.

Official submission pages resolved from the current leaderboard for the top rows:
- J2W: #331539
- suliman_tadros: #331931
- marius_binner: #331953
- a_s6: #331756
- Puffi: #330322
- reds: #331730

## Primary-source method scan beyond J2W

The scan was bounded to AIcrowd participant/forum pages and public artifacts surfaced from them. It did not infer methods from score/FLOP geometry alone.

- **suliman_tadros** — official participant profile currently says the participant has not posted on Discourse. No reproducible Phase-2 estimator disclosure was located in the bounded primary-source scan.
  - https://www.aicrowd.com/participants/suliman_tadros
- **marius_binner** — public activity/discussion is visible, but no reproducible Phase-2 estimator write-up/source artifact tied to the current top submission was located.
- **a_s6** — no reproducible Phase-2 method disclosure tied to the current top row was located.
- **Puffi** — public participant/team material exposes Phase-1 material/general discussion, but no reproducible Phase-2 method disclosure tied to the current rank-5 row was located in this scan.
  - https://www.aicrowd.com/participants/cipo
- **reds** — no reproducible Phase-2 method disclosure tied to the current rank-5 row was located.

A reproducible public Phase-2 method does exist outside the present top tier: 504aldo's forum write-up discloses factorized K=3 cumulant propagation, a memoryless fourth-cumulant core, source-age compression, cost engineering, negative results, and an MIT reproduction repository. The same thread contains a 2026-09-22 correction clarifying the pre/post covariance labeling of one reported law. Current official standings place 504aldo at rank 47 with adjusted score 5.4e-9.

Primary source:
https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

This evidence predates R264, so it is **not a newly disclosed top-tier method since R264**. It is recorded here only because R280 explicitly broadens the scan beyond the opaque J2W page.

## Verdict

**STANDINGS_CHANGED / NO_CHANGE_TOP_TIER_PUBLIC_METHOD_EVIDENCE.**

The visible leaderboard order below J2W changed, but the bounded primary-source scan found no newly disclosed reproducible method for the current top non-J2W entries. Existing reproducible public evidence from 504aldo remains materially below the present top tier and does not identify the mechanism used by J2W or the current #2–#5 rows.

No method attribution is made from leaderboard telemetry alone, and no row is attributed to our team without verified identity.
