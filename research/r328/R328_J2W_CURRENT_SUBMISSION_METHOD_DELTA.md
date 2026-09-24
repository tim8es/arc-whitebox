# R328 — J2W current-submission public-method delta vs R306

**Status:** COMPLETE  
**Verdict:** **NO_PUBLIC_METHOD**  
**Secondary finding:** **TARGET_ID_MISMATCH — current J2W View is #331539, not #332101**  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r328-j2w-current-submission-method-delta-20260924`  
**Audit date:** 2026-09-24

## Scope

R328 is a delta-only public-evidence audit relative to R306. It does not infer a method from score, rank, MSE, compute utilisation, entry count, or timing.

Admissible evidence:
1. current official AIcrowd Phase-2 leaderboard;
2. the exact submission linked by the current J2W leaderboard row;
3. official J2W/team/participant surfaces and official AIcrowd Forum search results;
4. repositories only if directly linked from an admissible J2W/joe_wanza public surface;
5. R306 as the frozen prior comparison point;
6. R314 only to resolve the provenance of submission #332101.

No arbitrary name-matched repository is attributed to J2W.

## 1. Current J2W row: fresh first-party check

Current official leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

Fresh public row observed:

- participant/team: **J2W**
- displayed rank: **01**
- displayed Adjusted Score: **0.0000000021** = UI-rounded **2.10e-9**
- displayed Final Layer MSE: **0.0000000164**
- displayed compute utilisation: **0.1306572576**
- displayed failed MLPs: **0**
- displayed Entries: **321**
- displayed Last Submission: **Sat, 19 Sep 2026 00:05**
- current row `View` target: **submission #331539**

Fresh direct click target:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539

This is the decisive identity check. The current J2W leaderboard row does **not** link to #332101.

## 2. #332101 is not the current J2W-linked submission

The current leaderboard's **AndreasHad04** row links to:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332101

That attribution is also independently preserved in the exact R314 receipt:

- R314 branch: `review/r314-r311-comparability-independent-audit-20260924`
- R314 receipt blob: `1c353d3746a83006b4cff0b49f041d6b5aa2e89e`
- recorded field: `andreas_current_row.current_view_submission_id = 332101`

R314 receipt:
https://github.com/tim8es/arc-whitebox/blob/review/r314-r311-comparability-independent-audit-20260924/research/r314/R314_RECEIPT.json

The unauthenticated public #332101 route is reachable, but its current retrievable text body is only the generic client-rendered submission shell (`Loading`, share controls) and exposes no method/config/source fields.

Therefore R328 does **not** inspect #332101 as a J2W method artifact and does not transfer any #332101 metadata to J2W.

## 3. Delta relative to R306

Frozen R306:
- branch: `review/r306-j2w-method-audit-20260924`
- head: `6519194e8f570b4b519bd97a1f574b33a86033f2`
- report blob: `68d7a5e45d05eaa584e3a1c5137696ae9dab89d8`
- receipt blob: `e0f86ba1c7b9ee757bc432dbaf7c2e98918ef726`
- target submission: **#331539**
- verdict: `NO_PUBLIC_METHOD`
- entries display: **320**
- adjusted score display: **2.10e-9**
- final-layer MSE display: **1.64e-8**

R306 report:
https://github.com/tim8es/arc-whitebox/blob/review/r306-j2w-method-audit-20260924/research/r306/R306_J2W_METHOD_AUDIT.md

### Exact observed delta

| Field | R306 | R328 fresh check | Delta |
|---|---:|---:|---|
| rank display | 01 | 01 | unchanged |
| adjusted score display | 2.10e-9 | 2.10e-9 | unchanged at UI precision |
| final-layer MSE display | 1.64e-8 | 1.64e-8 | unchanged at UI precision |
| entries | 320 | 321 | **+1** |
| last submission display | Sep 19, 00:05 | Sep 19, 00:05 | unchanged |
| leaderboard-linked submission | #331539 | **#331539** | **unchanged** |
| public method description | none verified | none verified | no positive delta |
| participant-linked source repo | none verified | none verified | no positive delta |
| reproducible submission-specific config | none verified | none verified | no positive delta |

The extra entry count is telemetry only. R328 does not infer what that extra entry contained, whether it was graded, whether it differed algorithmically, or whether it was competitive.

## 4. Current #331539 public method/config/source surface

Current J2W-linked submission:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539

Fresh unauthenticated rendering still exposes only generic page chrome/share controls. It does **not** expose, in the retrievable public text:

- estimator/method name;
- estimator formula;
- source-code link;
- Git repository link;
- immutable source commit/tag;
- downloadable estimator artifact;
- J2W-specific environment/configuration manifest;
- sufficiently detailed reproduction instructions.

Official J2W team page:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/J2W

It currently identifies one member:
- **joe_wanza — Team Organizer**

No repository or source-code link is exposed on the retrievable team page.

Searches of official AIcrowd/AIcrowd Forum surfaces for `joe_wanza`, `J2W`, and the exact submission ID did not surface a participant-authored method write-up or repository explicitly tied to #331539. Search results can mention joe_wanza as leaderboard/submission telemetry or in third-party comparative discussion; those are not J2W method disclosures and are not treated as such.

## 5. Version claims

No new **J2W-specific** package/version/configuration claim was found.

R306's challenge-wide evaluator statement remains background only:
- WhestBench `0.16.0`;
- FlopScope server/client `0.12.0`.

R328 does not convert those organizer-confirmed grader versions into a J2W source-tree dependency claim.

## 6. Fact / unknown boundary

### Confirmed facts

- J2W is currently displayed at rank 01.
- current UI-adjusted score is `0.0000000021` (rounded display);
- entries display increased from 320 in R306 to 321;
- current J2W `View` still resolves to **#331539**;
- J2W team page identifies **joe_wanza** as sole organizer/member;
- current retrievable #331539 public body exposes no readable method/source/config/reproduction payload;
- current leaderboard maps **#332101 to AndreasHad04**, not J2W.

### Unknown / not inferred

- exact unrounded J2W score;
- nature of the additional 321st entry;
- whether any non-public/private J2W method/config/code exists;
- whether authenticated or participant-only views expose additional fields;
- whether #331539 uses any particular estimator family;
- any causal explanation for J2W's score/rank;
- any J2W-linked GitHub repository absent an explicit participant/AIcrowd link.

## 7. Delta verdict

**NO_PUBLIC_METHOD.**

Relative to R306, the only verified J2W row delta is **Entries 320 → 321**. The current best-linked/public `View` target remains **#331539**, and no newly readable method, source implementation, submission-specific configuration, repository, immutable code commit, or reproducible instruction was found on admissible public J2W surfaces.

The premise that the current J2W `View` is #332101 is contradicted by the fresh official leaderboard. #332101 is currently linked from AndreasHad04's row and is not used as J2W evidence.

No leader-derived estimator hypothesis is admitted.

## Execution / mutation accounting

- code execution: **NO**
- benchmark/estimator run: **NO**
- dataset/dependency download: **NO**
- GitHub Actions: **NO**
- paid compute: **NO**
- private/holdout/full access: **NO**
- competition submission: **NO**
- participant/organizer contact: **NO**
- main edit: **NO**
- PR edit: **NO**
- control/queue edit: **NO**
- intended branch diff: exactly this report + one JSON receipt
