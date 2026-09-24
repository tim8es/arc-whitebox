# R318 — public configuration audit for Puffi #330322 and reds #331730

**Outcome: NO_PUBLIC_METHOD for both submissions.**

R318 inspected only the public, first-party AIcrowd canonical submission surfaces for the current rank-6 tie entries **Puffi** and **reds**, specifically submission **#330322** and submission **#331730**. The goal was narrower than R280: determine whether these exact submission pages/configuration surfaces publicly expose an estimator name, estimator parameters/configuration, source code, repository, script/archive, commit, or author analysis directly linked to the corresponding submission ID.

No method is inferred from rank, score, MSE, compute utilisation, entry count, or timestamp.

## Frozen scope and repository base

- exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- report-only branch: `review/r318-top6-public-config-audit-20260924`
- external evidence: public first-party AIcrowd pages only
- no profile/forum re-audit beyond what was necessary to identify direct submission-page linkage
- no identity research outside AIcrowd
- no participant contact
- no login/private access
- no Actions, benchmark, data/dependency downloads, paid resources, private/holdout/full access, submission, or main/PR/control edits

Audit date: `2026-09-24`.

## Current leaderboard identity anchor

The public ARC White-Box Estimation Challenge 2026 leaderboard currently shows a rank-6 tie:

### Puffi

- rank: **06**
- adjusted score: **0.0000000028**
- Final Layer MSE: **0.0000000194**
- compute utilisation: **0.1456939183**
- MLPs failed: **0**
- entries: **78**
- last submission: **Tue, 8 Sep 2026 14:09**
- the row's public **View** link resolves directly to submission **#330322**

Canonical submission URL:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330322

### reds

- rank: **06**
- adjusted score: **0.0000000028**
- Final Layer MSE: **0.0000000173**
- compute utilisation: **0.1623309082**
- MLPs failed: **0**
- entries: **60**
- last submission: **Mon, 21 Sep 2026 08:47**
- the row's public **View** link resolves directly to submission **#331730**

Canonical submission URL:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331730

First-party leaderboard:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

These leaderboard fields establish the public row/submission identity only. They are not method evidence.

## Submission #330322 — Puffi

### Canonical public page / visible metadata

The public unauthenticated canonical page for **#330322** was inspected.

The retrievable public rendering exposed the submission-page identity and generic AIcrowd page chrome/share controls, but did not expose any submission-specific method/configuration payload containing:

- estimator name,
- estimator family,
- estimator parameters,
- estimator configuration,
- source-code link,
- repository link,
- script/archive link,
- commit SHA,
- author analysis tied to #330322.

The public page therefore provides no direct method linkage usable by this audit.

A first-party AIcrowd participant page independently lists **330322** as a graded Puffi submission at the same Sep 8 time, which is consistent with the leaderboard identity. That page is used only as submission-status corroboration, not as method evidence.

Classification for **#330322**:

- estimator name: **NO_PUBLIC_METHOD**
- estimator params/config: **NO_PUBLIC_METHOD**
- source/repository/code: **NO_PUBLIC_METHOD**
- commit: **NO_PUBLIC_METHOD**
- author analysis directly tied to #330322: **NO_PUBLIC_METHOD**

No repository URL or commit is recorded because none was directly linked to #330322 by a public first-party AIcrowd source.

## Submission #331730 — reds

### Canonical public page / visible metadata

The public unauthenticated canonical page for **#331730** was inspected.

As with #330322, the retrievable public rendering exposed the canonical submission-page identity and generic AIcrowd page chrome/share controls, but did not expose a public submission-specific method/configuration payload containing:

- estimator name,
- estimator family,
- estimator parameters,
- estimator configuration,
- source-code link,
- repository link,
- script/archive link,
- commit SHA,
- author analysis tied to #331730.

No direct public code/repository link was present in the audited first-party canonical surface.

Classification for **#331730**:

- estimator name: **NO_PUBLIC_METHOD**
- estimator params/config: **NO_PUBLIC_METHOD**
- source/repository/code: **NO_PUBLIC_METHOD**
- commit: **NO_PUBLIC_METHOD**
- author analysis directly tied to #331730: **NO_PUBLIC_METHOD**

No repository URL or commit is recorded because none was directly linked to #331730 by a public first-party AIcrowd source.

## Configuration/metadata limitation

The canonical submission URLs are public, but their unauthenticated retrievable HTML rendering is client-shell style: it does not expose a public Configuration payload or method-specific metadata in the text surface available to this audit.

R318 therefore does **not** infer that private or authenticated submission metadata lacks configuration information. The narrower conclusion is only that no estimator/config/source/repository/code linkage is publicly exposed on the audited unauthenticated first-party surfaces.

This distinction matters: absence from the public canonical rendering is evidence of **no public method linkage**, not evidence about private grader state.

## Per-submission verdict

| Submission | Team | Estimator name | Params/config | Source/repo/code | Commit | Direct author analysis | Verdict |
|---|---|---|---|---|---|---|---|
| #330322 | Puffi | not publicly exposed | not publicly exposed | no direct public link | none publicly linked | none directly linked | **NO_PUBLIC_METHOD** |
| #331730 | reds | not publicly exposed | not publicly exposed | no direct public link | none publicly linked | none directly linked | **NO_PUBLIC_METHOD** |

## Conclusion

For both current rank-6 tie entries, AIcrowd publicly links the leaderboard row to the stated canonical submission ID, but the audited public canonical submission/configuration surfaces do not expose a directly linked estimator name, estimator parameters/configuration, source code, repository, script, commit, or author analysis.

- **Puffi #330322: NO_PUBLIC_METHOD**
- **reds #331730: NO_PUBLIC_METHOD**

No causal or methodological conclusion is drawn from their tied rank or displayed scores.

## Safety / execution record

- Actions/workflows run: **NO**
- benchmark/science run: **NO**
- submission made: **NO**
- login/private access: **NO**
- participant contacted: **NO**
- identity search outside official AIcrowd: **NO**
- dataset/dependency download: **NO**
- paid resource use: **NO**
- private/holdout/full-data access: **NO**
- main changed: **NO**
- PR changed/opened: **NO**
- control state changed: **NO**
- workflow changed: **NO**
- report-only branch used: **YES**
