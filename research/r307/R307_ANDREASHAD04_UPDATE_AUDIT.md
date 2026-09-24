# R307 — forensic audit of the AndreasHad04 leaderboard update

**Outcome: PARTIAL_PUBLIC_EVIDENCE.**

R307 audited the R304 AndreasHad04 delta using only public, first-party AIcrowd surfaces. A corresponding public submission record is identifiable: **submission #332093**, participant **AndreasHad04**, status **graded**, score **4.65e-9**, Final Layer MSE **2.00e-8**, displayed time **Sep 24, 01:22**. Those fields match the R304 updated row after leaderboard display rounding (4.65e-9 -> 4.70e-9) and its 2.00e-8 / 01:22 fields.

This identifies a public submission record corresponding to the observed R304 update. It does **not** identify the algorithmic change that caused the score/rank movement.

## Frozen scope and base

- exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- report-only branch: `review/r307-andreas-update-audit-20260924`
- R304 full-delta source: commit `fcff8898104a21431eb9e1a5eec0f5cb6bb00468`, `research/r304/R304_FULL_DELTA_AUDIT.md`
- R304 raw visible-row source: commit `5351f455c87afdd6eb3a4147e94c38d191968d18`, `research/r304/R304_RAW_VISIBLE_ROWS.json`
- external evidence scope: public first-party AIcrowd pages only
- no login, participant contact, submission, benchmark, Actions, dataset/dependency download, paid access, private/holdout/full-data access, or main/PR/control mutation

## R304 anchor

R304 recorded one scored-entry update for AndreasHad04 between its two saved leaderboard snapshots:

- displayed score: `4.90e-9 -> 4.70e-9`
- displayed Final Layer MSE: `2.12e-8 -> 2.00e-8`
- displayed rank: `28 -> 25`
- compute ratio: `231x -> 241x`
- last-submission display: `Sep 23, 12:15 -> Sep 24, 01:22`
- updated raw row retained `56` in the entries column

The current public leaderboard has moved beyond that R304 state, so R307 does not use the current row's present-day `View` target as evidence for the earlier 01:22 event.

## Public AIcrowd evidence

### 1. Matching submission ID — CONFIRMED_PUBLIC_EVIDENCE

The public AIcrowd submissions listing exposed the following record:

- submission: **#332093**
- participant: **AndreasHad04**
- state: **graded**
- score: **4.65e-9**
- Final Layer MSE: **2.00e-8**
- displayed time: **Sep 24, 01:22**

The submission-list score is more precise than the one-decimal mantissa shown in the R304 leaderboard row: `4.65e-9` displays there as `4.70e-9`. Together with the exact participant, `2.00e-8` Final Layer MSE, and `01:22` timestamp, this is sufficient to identify #332093 as the public submission record corresponding to the R304 updated row.

First-party AIcrowd surfaces:
- public submissions index: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions
- canonical submission path: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332093
- public leaderboard: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

The canonical #332093 page itself was not relied on for method/code fields; the identifying fields above were exposed by the public submissions listing.

### 2. Public method description for #332093 — NO_PUBLIC_LINKAGE

A public AIcrowd forum reply by AndreasHad04 dated Sep 22 describes parts of their then-current chain/representation, including a materialized `(2,2)` slice of post-activation kappa4, candidate covariance measurements, and a shipped configuration/cap. That is genuine public method-related information from the participant.

However:

- the post predates the Sep 24 01:22 submission;
- it does not name submission #332093;
- it does not claim that the described experiment/configuration produced the R304 score;
- therefore R307 does not bind that method description to #332093 and does not infer causality from the score change.

First-party thread:
https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

Classification: **public background method evidence exists, but no public method description was found that is explicitly linked to #332093.**

### 3. Source code for #332093 — NO_PUBLIC_EVIDENCE

In the same Sep 22 public AIcrowd thread, AndreasHad04 explicitly states that their workspace is not public and offers to paste a script if useful. The visible thread contains the request to paste it, but no subsequent AndreasHad04 script/code publication was found there. No public AIcrowd page located in this audit links source code, a repository, a script, or a code artifact to submission #332093.

Classification: **NO_PUBLIC_EVIDENCE** for source code associated with #332093.

This does not assert that no code exists. It states only that no associated source code was publicly exposed on the first-party AIcrowd surfaces audited here.

### 4. Regrade explanation — NO_PUBLIC_EVIDENCE

No first-party public AIcrowd page located in this audit marks the R304 change as a regrade or provides a public regrade explanation for #332093.

Classification: **NO_PUBLIC_EVIDENCE** for a regrade explanation.

The existence of a matching newly visible graded submission record means a public submission ID is available; R307 does not infer from that fact alone whether any separate backend rescoring/regrade process also occurred.

## Confirmed facts vs unknowns

| Question | R307 classification | Evidence-bounded conclusion |
|---|---|---|
| Corresponding public submission ID | **CONFIRMED_PUBLIC_EVIDENCE** | #332093 matches AndreasHad04, 4.65e-9, 2.00e-8, Sep 24 01:22 |
| Public method description explicitly tied to #332093 | **NO_PUBLIC_LINKAGE** | Andreas has an earlier public method-related post, but it names no #332093 |
| Public source code tied to #332093 | **NO_PUBLIC_EVIDENCE** | No linked code/repository/script found; participant stated workspace was not public |
| Public regrade explanation | **NO_PUBLIC_EVIDENCE** | No public regrade marker/explanation found |
| Causal reason for score/rank change | **UNKNOWN / NOT INFERRED** | A score delta does not identify a causal method change |

## Forensic conclusion

R307 resolves one part of the R304 uncertainty: the Sep 24 01:22 AndreasHad04 update has a publicly identifiable corresponding AIcrowd submission record, **#332093**.

R307 does **not** establish which estimator change, if any, produced that result. No public AIcrowd method write-up or source-code artifact was found that explicitly maps to #332093, and no public regrade explanation was found. The Sep 22 AndreasHad04 forum material is retained only as unlinked background evidence, not as an explanation of the R304 score movement.

Therefore the terminal evidence label is **PARTIAL_PUBLIC_EVIDENCE**, not global `NO_PUBLIC_EVIDENCE`.

## Safety / execution record

- Actions/workflows run: **NO**
- benchmark/science run: **NO**
- submission made: **NO**
- login/private access: **NO**
- participant contact: **NO**
- dataset/dependency download: **NO**
- paid resource use: **NO**
- holdout/full-data access: **NO**
- main changed: **NO**
- PR changed/opened: **NO**
- control state changed: **NO**
- report-only branch used: **YES**
