# R312 — Luna submission #332100 public-method audit

**Outcome: NO_PUBLIC_METHOD.**

R312 audited only public, first-party AIcrowd pages for a public method/code linkage to the current top-5 Luna entry and submission **#332100**. The leaderboard-to-submission identity is public and direct; no public estimator description, source code/repository, author write-up, or commit was found that is explicitly tied to **#332100**.

No causal method inference is made from rank, score, MSE, compute utilisation, entry count, or timestamp.

## Frozen scope and repository base

- exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- report-only branch: `review/r312-luna-public-method-audit-20260924`
- external evidence scope: public first-party AIcrowd pages only
- no identity search outside official AIcrowd surfaces
- no participant contact
- no login/private access
- no submission, benchmark, Actions, downloads, paid resources, holdout/full-data access, or main/PR/control edits

Audit capture time: `2026-09-24T09:37:35Z` UTC.

## Confirmed public facts

### 1. Current leaderboard row — CONFIRMED

The public ARC White-Box Estimation Challenge 2026 leaderboard showed:

- rank: **05**
- participant/team: **Luna**
- adjusted score: **0.0000000026** (`2.6e-9`)
- Final Layer MSE: **0.0000000167** (`1.67e-8`)
- compute utilisation: **0.1554446198**
- MLPs failed: **0**
- entries: **7**
- last submission: **Thu, 24 Sep 2026 03:32**
- row state: **New entry**

First-party source:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

These leaderboard fields are descriptive only. They do not establish which estimator, code change, repository revision, or method produced the result.

### 2. Leaderboard row directly links to submission #332100 — CONFIRMED

The **View** link on the Luna leaderboard row resolves directly to the first-party AIcrowd submission page:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332100

This is the public source linkage that permits R312 to identify **#332100** as the submission associated with the audited current Luna row.

The unauthenticated public rendering of the canonical submission page did not expose a method description, source-code link, repository link, commit identifier, or author analysis in the page content available to this audit.

### 3. Luna team membership — CONFIRMED

The first-party AIcrowd Luna team page shows one member:

- **dogus_ozel** — Team Organizer

First-party source:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/Luna

R312 did not search for or infer any identity outside official AIcrowd pages.

## Public linkage audit

### Estimator description explicitly tied to #332100 — NO_PUBLIC_METHOD

No public AIcrowd challenge page or AIcrowd Forum result located in this audit explicitly names submission **#332100** together with an estimator description or algorithmic write-up.

Searches restricted to first-party AIcrowd domains for:
- `332100`
- `Luna` + `332100`
- `dogus_ozel` + `332100`
- `dogus_ozel` + ARC White-Box Estimation Challenge
- `Luna` + ARC White-Box Estimation Challenge

did not surface a public method write-up tied to #332100.

Classification: **NO_PUBLIC_METHOD**.

This is an evidence-bounded absence statement: it means no such linkage was publicly located on the audited first-party surfaces, not that no method description exists privately or may appear later.

### Source code / repository explicitly tied to #332100 — NO_PUBLIC_METHOD

No public first-party AIcrowd page located in this audit links **#332100** to:
- source code,
- a script,
- a source archive,
- a Git repository,
- a repository URL,
- or a commit SHA.

R312 therefore records no repository URL or commit identifier.

Classification: **NO_PUBLIC_METHOD**.

### Author analysis explicitly tied to #332100 — NO_PUBLIC_METHOD

No public AIcrowd Forum post or challenge-page write-up located in this audit explicitly ties author analysis to **#332100**.

Classification: **NO_PUBLIC_METHOD**.

## Confirmed facts vs unknowns

| Question | R312 classification | Evidence-bounded conclusion |
|---|---|---|
| Is the current Luna leaderboard row publicly linked to #332100? | **CONFIRMED** | Yes. The row's first-party `View` link resolves directly to `/submissions/332100`. |
| Is an estimator description publicly tied to #332100? | **NO_PUBLIC_METHOD** | No direct first-party linkage located. |
| Is source code or a repository publicly tied to #332100? | **NO_PUBLIC_METHOD** | No direct first-party linkage located. |
| Is a commit publicly tied to #332100? | **NO_PUBLIC_METHOD** | No commit is recorded because none was directly linked by an audited public source. |
| Is there a public author write-up tied to #332100? | **NO_PUBLIC_METHOD** | No direct first-party linkage located. |
| Can rank/score identify the method? | **NO** | Rank/score are not causal evidence and are not used to infer the estimator. |
| What estimator produced #332100? | **UNKNOWN** | Not publicly identifiable from the audited first-party evidence. |

## Conclusion

The current top-5 Luna leaderboard entry is publicly and directly linked by AIcrowd to submission **#332100**. That establishes the submission identity only.

No public estimator description, source code/repository, commit, or author analysis was found that AIcrowd publicly links to **#332100**. R312 therefore terminates as **NO_PUBLIC_METHOD**.

No method is inferred from the row's rank, score, MSE, compute utilisation, timestamp, or entry count.

## Safety / execution record

- Actions/workflows run: **NO**
- benchmark/science run: **NO**
- submission made: **NO**
- login/private access: **NO**
- participant contacted: **NO**
- identity research outside official AIcrowd: **NO**
- dataset/dependency download: **NO**
- paid resource use: **NO**
- holdout/full-data access: **NO**
- main changed: **NO**
- PR changed/opened: **NO**
- control state changed: **NO**
- workflow changed: **NO**
- report-only branch used: **YES**
