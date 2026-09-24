# R329 — current rank-3 marius_binner public-method audit

**Verdict: NO_PUBLIC_METHOD.**

R329 is a narrow follow-up focused only on the current Phase-2 leaderboard-linked submission for **marius_binner**. It was performed only after dedupe against completed R306, R318, and R326; none of those reports audited the current Marius submission.

## Frozen scope

- exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- report-only branch: `review/r329-rank3-marius-method-audit-20260924`
- target: current leaderboard-linked submission for `marius_binner`
- evidence: official public AIcrowd leaderboard/submission pages and participant-linked public AIcrowd/Discourse sources only
- no method inference from rank, score, MSE, compute, entry count, display name, or affiliation
- no arbitrary external identity/repository search
- no benchmark, code execution, dependency/data download, Actions, paid/private/holdout/full access, submission, contact, or main/PR/control/queue edit

Audit date: `2026-09-24`.

## 1. Dedupe against prior exact audits

R306 receipt:
- scope: J2W / submission #331539
- verdict: `NO_PUBLIC_METHOD`
- receipt blob: `e0f86ba1c7b9ee757bc432dbaf7c2e98918ef726`

R318 receipt:
- scope: Puffi #330322 and reds #331730
- verdict: `NO_PUBLIC_METHOD` for both
- receipt blob: `501fae48dc32112772b6cc55132663f9a23d24f9`

R326 receipt:
- scope: suliman_tadros / current linked submission #331931
- verdict: `NO_PUBLIC_METHOD`
- receipt blob: `406e1e26d28bd6d161041b79124d3d76037f4384`

None targets marius_binner or submission #331953.

Result: **not already audited**; R329 proceeds.

## 2. Current leaderboard-linked submission identity

Official leaderboard:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

At audit time the current row showed:

- rank: **03**
- participant: **marius_binner**
- Adjusted Score display: **0.0000000023** (`2.30e-9`, UI-rounded)
- Final Layer MSE display: **0.0000000156**
- Compute utilisation display: **0.1474118618**
- MLPs failed: **0**
- Entries: **158**
- Last Submission: **Wed, 23 Sep 2026 06:46**

The row's current public **View** target resolves directly to:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953

Therefore the exact current leaderboard-linked submission ID is:

**#331953**

This direct View link is the only basis for submission identity. No algorithmic inference is made from the row metrics.

## 3. Canonical submission page access vs method disclosure

Canonical page:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953

The page is publicly reachable without authentication.

In the anonymous public text rendering inspected by R329, however, the submission-specific body does not expose a public estimator description, estimator name, configuration, source-code link, repository link, script/archive, commit SHA, or reproducible method.

This distinction is explicit:

- public canonical page access: **YES**
- submission-specific method disclosure: **NO**

Classification:

- estimator name/family: **NO_PUBLIC_METHOD**
- estimator config/params: **NO_PUBLIC_METHOD**
- source/code: **NO_PUBLIC_METHOD**
- repository: **NO_PUBLIC_METHOD**
- commit: **NO_PUBLIC_METHOD**
- reproducible method: **NO_PUBLIC_METHOD**

## 4. Participant-linked public AIcrowd/Discourse material

Public first-party posts authored by `marius_binner` were located on the official challenge forum, including:

1. **Phase 1 final evaluation question: Overfitting to public instances**
   https://discourse.aicrowd.com/t/phase-1-final-evaluation-question-overfitting-to-public-instances/18118

2. **Potential flopscope accounting bypass bug**
   https://discourse.aicrowd.com/t/potential-flopscope-accounting-bypass-bug/18099/3

These are participant-linked public sources, but neither discloses the estimator, source tree, configuration, repository, commit, or reproducible method used by current Phase-2 submission #331953.

A separate public post by another participant discusses what the top methods might be doing and explicitly labels that discussion as a best guess. R329 treats such third-party speculation as **non-admissible method evidence** and does not transfer it to #331953.

No participant-linked repository or code URL explicitly connected to #331953 was found in the admissible public surfaces inspected.

## 5. Method evidence and idea transfer

Explicit public method disclosure for #331953: **none found**.

Therefore:

- method disclosed: **NO**
- reproducible from public evidence: **NO**
- participant-linked source/repository: **none established**
- submission-specific commit: **none established**
- candidate idea count: **0**
- experiment-history dedupe for a new idea: **not triggered**

No idea is generated from rank, score, affiliation, participant identity, or third-party speculation.

## 6. Final verdict

**NO_PUBLIC_METHOD.**

The current rank-3 leaderboard row is directly linked to submission **#331953**, but the audited public official AIcrowd/participant-linked sources do not disclose an estimator name, source, configuration, repository, commit, or reproducible method for that submission.

## Source URLs

1. Current leaderboard:
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
2. Current leaderboard-linked submission:
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331953
3. Participant-authored forum thread:
   https://discourse.aicrowd.com/t/phase-1-final-evaluation-question-overfitting-to-public-instances/18118
4. Participant-authored forum post:
   https://discourse.aicrowd.com/t/potential-flopscope-accounting-bypass-bug/18099/3

## Execution accounting

- code/estimator execution: **NO**
- benchmark/science run: **NO**
- dependency/data download: **NO**
- GitHub Actions: **NO**
- paid compute/spend: **NO**
- private/holdout/full access: **NO**
- competition submission: **NO**
- participant/organizer contact: **NO**
- arbitrary external identity/repository attribution: **NO**
- main edit: **NO**
- PR edit/open: **NO**
- control edit: **NO**
- queue edit: **NO**
- report-only branch used: **YES**
