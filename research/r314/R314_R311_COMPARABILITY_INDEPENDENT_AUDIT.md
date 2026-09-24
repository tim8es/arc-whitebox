# R314 — independent audit of R311 leaderboard-score comparability

**Status:** COMPLETE  
**Verdict:** **NOT_COMPARABLE**  
**Branch:** `review/r314-r311-comparability-independent-audit-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Question

Independently of R311, does the live Phase-2 AIcrowd leaderboard **ADJUSTED SCORE** represent the same numerical quantity on the same evaluation set as the committed R209 V25 Mini-100 `adjusted_final_layer_score`, such that a direct ratio, gap, or implied place would be justified?

**No. The evidence supports `NOT_COMPARABLE`.**

The score *formula and aggregation form* match structurally, but the evaluated set does not: the live submission-detail contract exposes an adjusted-score mean over **50 grader-public MLPs**, with **50 additional private MLPs sealed**, while R209 is an aggregate over **100 rows of the published Hugging Face `v2-phase2` `mini` split**. The public sources inspected here do not establish an identity/join between those 50 grader-public rows and any exact 50-row subset of R209 Mini-100. The current leaderboard display is rounded, and the final full-test score/rank is a separate sealed 100-MLP result.

No ratio, gap, or place is computed.

## 1. What the live leaderboard currently shows

The official current Phase-2 leaderboard exposes these columns:

`# | Participants | Adjusted Score | Final Layer MSE | Compute utilisation | MLPs failed | Entries | Last Submission | Submission Trend`.

For AndreasHad04 at the time of this R314 check, the current row is:

- displayed rank: `22`;
- **Adjusted Score:** `0.0000000043`;
- Final Layer MSE: `0.0000000186`;
- Compute utilisation: `0.2328913187`;
- failed MLPs: `0`;
- entries: `59`;
- current `View` target: **submission #332101**, not #332093.

Official leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

This matters for the requested #332093 audit: **#332093 is a historical submission, not the submission currently linked from the live AndreasHad04 leaderboard row.** R314 therefore does not substitute current #332101 fields for #332093.

## 2. Submission-detail split semantics: 50 public + 50 sealed + separate full-test final score

The official Phase-2 submission-detail surface exposes the evaluation partition explicitly. On the current indexed official Phase-2 detail page for submission #329251, AIcrowd shows:

- `Graded · 50/50 public scored`;
- `Adjusted score — Public split`;
- `Final-layer · lower is better · mean over 50 public MLPs`;
- `Public split n=50 · 50 scored`;
- `Private · locked n=50 · sealed`;
- `Final score · Full test set — Graded on all 100 MLPs — the number that ranks you`;
- `The 50 holdout MLPs — a different partition from the public split — that decide the final rank`;
- private values remain sealed until results release.

Official Phase-2 detail page:
https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

The canonical public route requested for #332093 is:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332093

In this R314 session, the #332093 route is publicly reachable as a dynamic AIcrowd route but its submission-specific body was not text-extractable through the current public fetch interface. R314 therefore **does not claim a fresh direct DOM capture of #332093-specific detail fields**. This is an evidence limitation, not a reason to infer different scoring semantics for that submission. The 50-public / 50-sealed / 100-full-test contract above is the official Phase-2 submission-detail contract from the same challenge.

The previously committed R307 report records that the public AIcrowd submissions listing identified #332093 as AndreasHad04, graded, adjusted score `4.65e-9`, Final Layer MSE `2.00e-8`, submitted Sep 24 01:22. R314 does not use that prior report as the primary basis for the split/comparability conclusion.

### Current rank vs final rank

These are distinct concepts:

1. **Live leaderboard rank** is based on the currently visible public adjusted score.
2. **Full-test final rank** is a separate result based on the full 100-MLP test set after the sealed private half is released/scored for final standings.

At the current date, the private half remains sealed on the public submission-detail surface; therefore the final full-test score/rank is not a public numeric comparator for R209.

## 3. Official WhestBench score formula and aggregation

Pinned official source inspected:

- repository: `AIcrowd/whestbench`;
- commit: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`;
- `src/whestbench/scoring.py`;
- `docs/reference/score-report-fields.md`.

The per-MLP score is:

`s_m = final_layer_mse_m * max(0.1, C_m / B_m)`

for a valid run, while a failure receives multiplier `1.0`.

The suite aggregate is the arithmetic mean of the per-MLP adjusted scores. In the source, the return value is computed as:

`float(fnp.mean(fnp.asarray(primary_scores)))`.

The schema documentation states that `adjusted_final_layer_score` is the leaderboard metric and is the **suite mean** of per-MLP budget-adjusted scores.

Primary sources:
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md

For Phase 2, the organizer's official announcement fixes the per-MLP FLOP budget at `2^41` (approximately `2.199e12`) and caps residual wall time at `0.4 s`; computation outside flopscope is prohibited. The organizer also publicly stated that the live evaluator runs `whestbench 0.16.0` and `flopscope 0.12.0`.

Organizer primary source:
https://www.aicrowd.com/participants/mohanty

## 4. Exact committed R209 evidence

Exact committed receipt:

- repository: `tim8es/arc-whitebox`;
- commit: `e1f6dd6a6bc351b8253e255fef424b1931b37de3`;
- path: `research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json`;
- Git blob: `7fec90369227839a9902c7cceb9f3519acb66cb8`.

R209 records V25 with:

- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`;
- dataset SHA256: `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`;
- split: **`mini`**;
- streaming: true;
- requested/reported MLPs: **100**;
- width/depth: `1024 × 16`;
- `official_scorer = false`;
- `holdout = false`;
- `full_split = false`;
- V25 failures: `0/100`;
- V25 `adjusted_final_layer_score = 8.170397440117225e-9`;
- observed toolchain: Python `3.11.16`, WhestBench `0.16.1`, FlopScope `0.12.1+np2.4.6`, NumPy `2.4.6`.

The receipt also records 100 immutable per-MLP metric records, but no raw prediction vectors.

Primary committed evidence:
https://github.com/tim8es/arc-whitebox/blob/e1f6dd6a6bc351b8253e255fef424b1931b37de3/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json

## 5. Split, aggregation, and source comparison

| Dimension | Live AIcrowd public leaderboard | R209 V25 Mini-100 | R314 conclusion |
|---|---|---|---|
| Metric | adjusted final-layer score | `adjusted_final_layer_score` | **Structural match** |
| Per-MLP formula | final MSE × budget multiplier | same WhestBench-style field/contract | **Structural match** |
| Aggregation | mean over 50 public MLPs | mean over 100 Mini MLPs | **Different aggregation set** |
| Public panel cardinality | 50 | 100 | **Different** |
| Additional sealed panel | 50 private/sealed | none; `holdout=false` | **Different** |
| Full-test final score/rank | separate 100-MLP sealed/final result | not a full split; `full_split=false` | **Different object** |
| Data provenance | AIcrowd grader public partition; public page does not publish a Mini-100 row mapping/hash | HF `v2-phase2` `mini`, exact dataset hash recorded | **Exact source-row identity not proven** |
| Official grader | yes, leaderboard grading surface | `official_scorer=false` | **Different provenance** |
| Toolchain | organizer: WhestBench 0.16.0 / FlopScope 0.12.0 | 0.16.1 / 0.12.1+np2.4.6 | **Not identical; numerical consequence not audited here** |

The important distinction is not merely “50 vs 100”. Even if a future identity audit proved that the grader-public 50 are a subset of the published Mini-100, a 50-row arithmetic mean and a 100-row arithmetic mean are still different numerical quantities unless the exact 50-row R209 subset is selected and recomputed under justified equivalent scoring semantics.

No such exact join/recomputation is established by the requested evidence.

## 6. Rounding and still-unknown fields

### Confirmed display rounding / precision loss

The live leaderboard currently displays scores as fixed decimal strings such as
`0.0000000043`. That display does not expose the underlying full-precision float.

Official WhestBench human presentation uses:

`f"{float(value):.2e}"`

which is three significant figures. The official Phase-2 submission-detail example #329251 demonstrates additional presentation layers:

- top-level `Score 1.93e-8`;
- detail `Adjusted score 1.932×10^-8`.

Therefore the public UI demonstrably presents rounded values at different precisions.

### Unknown / not established

R314 cannot establish from the public evidence:

1. the exact unrounded float behind a live leaderboard cell;
2. the exact frontend formatter/rounding rule used for the leaderboard table itself;
3. the exact identities/hash/join keys of the 50 grader-public MLPs;
4. whether those 50 are exactly a known subset of R209's 100 Mini rows;
5. the exact full-test score or final rank while the private 50 remain sealed;
6. bit-for-bit evaluator equivalence between live grader WhestBench 0.16.0 / FlopScope 0.12.0 and R209's 0.16.1 / 0.12.1+np2.4.6;
7. whether any version difference changes the relevant score numerically. No such effect is inferred.

## 7. Independent audit of R311 for overclaims

R311 report audited:
https://github.com/tim8es/arc-whitebox/blob/af16cdf782e97e4a7a1753f1516635191493f0d1/research/r311/R311_LEADERBOARD_SCORE_COMPARABILITY.md

### Central conclusion

**SUPPORTED.** R311's `NOT_COMPARABLE` verdict is independently reproduced.

Its core claims are evidence-supported:

- public leaderboard/submission adjusted score is a 50-public-MLP aggregate;
- another 50 MLPs are sealed/private;
- full-test final scoring/rank is a separate 100-MLP result;
- WhestBench's high-level formula is a per-MLP adjusted score followed by a suite mean;
- R209 is a 100-row `mini` aggregate and explicitly not an official scorer/full/holdout run;
- exact public leaderboard float is not recoverable from the rounded display;
- ratio/place should not be inferred.

### Material overclaims

**None found that change the verdict.**

### Qualifications / evidence-provenance improvements

1. **R311 did not inspect #332093 specifically.** It used official Phase-2 submission #329251 to establish the challenge-wide 50-public / 50-sealed / full-test UI contract. That is valid evidence for the scoring surface, but it should not be described as a #332093-specific DOM capture. R311 itself did not make that false claim; this is a provenance qualification for R314.
2. **“Local development aggregate” is potentially ambiguous wording.** R209 was executed in GitHub Actions with WhestBench runner `local`; the important evidence-backed distinction is “non-official-grader HF Mini-100 aggregate”, not “ran on a local machine”.
3. **Toolchain uncertainty can now be stated more concretely.** Primary organizer evidence says the live grader uses WhestBench 0.16.0 / FlopScope 0.12.0; R209 records 0.16.1 / 0.12.1+np2.4.6. R311 correctly declined to claim exact toolchain equivalence. R314 also does not infer a scoring difference merely from the version mismatch.
4. **Current AndreasHad04 row must not be back-projected onto #332093.** The live leaderboard now links to #332101. Any #332093-specific score/rank statement is historical, not the current row.

None of these qualifications rescues direct quantitative comparability.

## 8. Final decision

**`NOT_COMPARABLE`.**

What matches:
- metric family;
- per-MLP adjustment formula at the documented contract level;
- arithmetic-mean aggregation form;
- Phase-2 budget scale.

What does not match or is not proven:
- number of MLPs in the aggregate (50 vs 100);
- exact panel identity;
- grader-vs-HF Mini data provenance;
- official-grader status;
- exact toolchain identity;
- exact unrounded leaderboard value;
- final full-test score/rank, still sealed.

Accordingly R314 computes **no ratio, no gap, no place, and no implied leaderboard rank for R209**.

## Scope / execution accounting

- benchmark or estimator run: **NO**
- challenge dataset access/download: **NO**
- dependency/package download: **NO**
- GitHub Actions run: **NO**
- competition submission: **NO**
- private/holdout/full-data access: **NO**
- sealed values accessed: **NO**
- main edit: **NO**
- PR edit/open: **NO**
- control edit: **NO**
- report-only branch: **YES**
