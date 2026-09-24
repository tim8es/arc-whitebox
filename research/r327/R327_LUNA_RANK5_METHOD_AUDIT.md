# R327 — Luna / dogus_ozel rank-5 public-method audit

**Status:** COMPLETE  
**Verdict:** **NO_PUBLIC_METHOD**  
**Idea count:** **0**  
**Branch:** `review/r327-luna-rank5-method-audit-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Scope

R327 audits only the new/changed public top-6 entry **Luna / dogus_ozel**. It does not repeat the R306 J2W audit or the R318 Puffi/reds audit, and it draws no methodological conclusion from rank, score, MSE, compute use, or submission cadence.

Allowed evidence:
- official AIcrowd leaderboard/submission/team/submission-list surfaces;
- official AIcrowd participant/forum surfaces when directly linked or attributable to the participant;
- repositories only when explicitly linked by the participant from an admissible public surface.

No arbitrary identity-matching repository search is treated as evidence.

## Snapshot / identity

R310's public leaderboard capture at **2026-09-24T09:29:17.177839Z UTC** recorded:

- visible rank: **05**
- participant/team: **Luna**
- public View submission ID: **332100**
- displayed adjusted score DOM string: **0.0000000026**
- entries: **7**

R327 independently inspected the public AIcrowd submission listing and submission page during an audit snapshot at **2026-09-24T10:29:59.376316039Z UTC**.

The official submission listing records submission **#332100** as:

- participant: **dogus_ozel**
- team: **Luna**
- status: **graded**
- adjusted score display: **2.60 e−9**
- final-layer MSE display: **1.67 e−8**
- submitted: **Sep 24, 03:32**
- public View target:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332100

The canonical submission page confirms:

- `#332100`
- Phase 2
- author/participant: `dogus_ozel`
- team: `Luna`
- graded successfully
- 50/50 public MLPs scored, 0 failed
- exact page-level public adjusted-score display: `2.598 ×10−9`

These facts identify the current public submission only. They are not used to infer its method.

## Public page availability vs method disclosure

The canonical page for **#332100 is publicly available**. It is not merely an inaccessible route or a generic Loading shell: the unauthenticated public rendering exposes submission identity, grader status, aggregate telemetry, per-MLP public scores, FLOPs, and sealed/private placeholders.

However, the same public rendering does **not** expose a reproducible method/config/source payload.

Observed public method fields:

| Item | Public evidence |
|---|---|
| estimator name/family | not exposed |
| algorithm/method description | not exposed |
| estimator parameters | not exposed |
| method-specific configuration | not exposed |
| source file / source archive | not exposed |
| repository URL | not exposed |
| immutable code commit/tag | not exposed |
| reproduction command/environment tied to #332100 | not exposed |
| participant write-up tied to #332100 | not exposed |

The page shows the UI labels `Overview` and `Configuration` plus generic `schema 2.0`, but the retrievable public content contains no estimator-specific configuration or source material. R327 therefore distinguishes:

- **page availability:** YES;
- **public reproducible method availability:** NO.

## Official linked surfaces

### Canonical submission

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332100

Direct links exposed by the submission page:

- participant:
  https://www.aicrowd.com/participants/dogus_ozel
- team:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/Luna

### Luna team page

The public Luna team page is available and lists:

- **1 / 5** members;
- **dogus_ozel — Team Organizer**.

It exposes no external repository, source-code URL, method description, or commit tied to #332100.

### Participant profile link

The canonical submission page visibly links to the participant URL above. During R327, the public extraction path for that participant URL returned an HTTP 404 / unavailable result. R327 does not interpret that as proof that the participant has no profile metadata; it only means no additional public participant-linked repository or method disclosure could be established from that route in this audit.

### Official AIcrowd forum/search

A search restricted to the participant/team identity and the challenge did not surface a participant-authored official AIcrowd post explicitly tying a method, configuration, repository, or source to submission #332100.

No arbitrary GitHub repository was attributed to dogus_ozel/Luna without an official participant-originated link.

## Participant-linked repository

**None established.**

R327 found no repository URL linked from:

- submission #332100;
- the Luna team page;
- an accessible participant profile surface;
- a participant-authored official AIcrowd forum disclosure tied to #332100.

Therefore there is no admissible code commit to record and no reproducibility claim.

## Verdict

**NO_PUBLIC_METHOD**

The public submission is accessible, but no estimator method/config/source/repository/commit is publicly exposed or participant-linked strongly enough to reproduce #332100.

This verdict is evidence-limited. It does not claim that no method/config exists privately, inside the submitted package, or in authenticated organizer/participant views.

## Transferable idea / experiment-ledger gate

**Ideas admitted: 0.**

The brief permits an idea only when a source directly discloses a concrete mechanism and it survives deduplication against the experiment ledger. Here the first gate fails: no concrete method is publicly disclosed for #332100.

Therefore R327 does not infer an idea from rank, score, MSE, FLOPs, wall time, score progression across dogus_ozel submissions, or any other grader telemetry, and no ledger-derived novelty claim is made.

## Comparison with prior top-method audits

- R306 audited J2W and concluded `NO_PUBLIC_METHOD`.
- R318 audited Puffi #330322 and reds #331730 and concluded `NO_PUBLIC_METHOD` for both.
- R327 is limited to the subsequently surfaced **Luna / dogus_ozel #332100** entry and does not repeat those audits.

## Exact URLs

Official AIcrowd:

- leaderboard:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2
- public submissions listing:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions?q%5Bparticipant_name_equals%5D=dogus_ozel
- canonical submission #332100:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332100
- participant link exposed by #332100:
  https://www.aicrowd.com/participants/dogus_ozel
- Luna team:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/Luna

Project comparison evidence:

- R310:
  https://github.com/tim8es/arc-whitebox/blob/80d55d7150e7907bd96f99a78a0b88cd4cdd6f5c/research/r310/R310_RECEIPT.json
- R306:
  https://github.com/tim8es/arc-whitebox/blob/review/r306-j2w-method-audit-20260924/research/r306/R306_RECEIPT.json
- R318:
  https://github.com/tim8es/arc-whitebox/blob/d0138a3fe772c712d331f5fde0c7e75be5bb56b7/research/r318/R318_TOP6_PUBLIC_CONFIG_AUDIT_RECEIPT.json

## Safety / execution record

- benchmark/science run: **NO**
- competitor code download: **NO**
- dependency download/install: **NO**
- dataset download/access: **NO**
- GitHub Actions: **NO**
- paid compute: **NO**
- private/holdout/full-data access: **NO**
- competition submission: **NO**
- participant/organizer contact: **NO**
- arbitrary identity-matched repository attribution: **NO**
- main edit: **NO**
- PR edit/open: **NO**
- control/queue edit: **NO**
- report-only branch: **YES**

## R330 integrity correction — prior R312 overlap

**Integrity classification:** `CONFIRMATORY_DUPLICATE_OF_R312`  
**Novel method delta:** **NONE**

R327 did **not** newly discover or first audit Luna / dogus_ozel submission **#332100**. An earlier completed audit, **R312**, had already audited the same public submission, the same displayed submission timestamp (**Sep 24, 03:32**), and had already concluded **NO_PUBLIC_METHOD**.

Exact prior R312 identity inspected for this correction:

- branch: `review/r312-luna-public-method-audit-20260924`
- final branch head: `4af4a8bda987abb99ea4a2f5b85c8d7c7ac46321`
- report: `research/r312/R312_LUNA_PUBLIC_METHOD_AUDIT.md`
- report blob SHA-1: `584c53dc7938be817d9a9cc78505bd69b5032e45`
- receipt: `research/r312/R312_LUNA_PUBLIC_METHOD_AUDIT_RECEIPT.json`
- receipt blob SHA-1: `c12e4223e22850c7086a21cf6b28a2350a390977`
- R312 audit capture: `2026-09-24T09:37:35Z`
- R312 verdict: `NO_PUBLIC_METHOD`
- R312 canonical submission: `#332100`

R327's only incremental value is its **later public snapshot at 2026-09-24T10:29:59.376316039Z UTC**, which independently confirmed that the same public submission **#332100** still exposed grader telemetry but no estimator description, method-specific configuration, source/repository, commit, or reproducible implementation linkage.

Accordingly:

- R327's `NO_PUBLIC_METHOD` remains valid as a **confirmed status**;
- it must **not** be cited as a novel top-6 method discovery or first audit;
- there is **no new method delta** relative to R312;
- both R312 and R327 explicitly made **no method inference from rank, score, MSE, compute utilisation, timestamp, or entry count**;
- ideas admitted remain **0**.

R330 changes only this integrity classification/lineage. It does not alter the underlying R327 public-evidence observations.

