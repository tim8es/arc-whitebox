# R390 — current ARC win-position refresh

**Status:** COMPLETE  
**Audit date:** 2026-09-28  
**Read-only public-source check time:** approximately 2026-09-27T22:10Z  
**Verdict:** **UNESTABLISHED / NOT_COMPETITION_COMPARABLE**  
**Scope:** current first-party public sources + existing ARC repo evidence only  
**Branch:** `research/r390-current-win-position-20260928`  
**Base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## 1. Verified current leader bar: precise limitation

### Fresh current leaderboard rank/top

A fresh current Phase-2 leaderboard top/rank **could not be verified from the read-only public fetch surface used for R390**.

The unauthenticated challenge page is public:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026

and current unauthenticated submission pages and the submissions listing are publicly readable, for example:

- submissions list:  
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions
- Phase-2 submission #331359:  
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331359
- Phase-2 submission #330706:  
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330706
- Phase-2 submission #331027:  
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331027
- Phase-2 submission #330812:  
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/330812

However, the direct Phase-2 leaderboard route used by the earlier R367 capture was not retrievable through the same public read-only fetch, so R390 does **not** manufacture a current top row or rank from search snippets, submission ordering, or individual submission pages.

### What is current and visible without login

Current first-party submission pages expose displayed public-split aggregates at more precision than the compact submission-list row. Examples visible in the current public source include:

- #331359, marius_binner, Phase 2: displayed public adjusted score **2.460×10^-9**;
- #330706, marius_binner, Phase 2: displayed public adjusted score **2.667×10^-9**;
- #331009, yrik_ivanov, Phase 2: displayed public adjusted score **5.325×10^-9**.

These are **submission-level public scores**, not proof that any one of them is the current leaderboard leader.

The current public submissions list also contains submissions dated 2026-09-27, so the persisted R367 leaderboard capture from 2026-09-24 is stale as a “current” snapshot even if its rows remain useful historical evidence.

### Last persisted leaderboard capture

R377 re-read:

- branch: `research/r377-leaderboard-comparability-20260924`
- head: `fe8aed53d0ab1f5d972c6a1423f1a2aa86c1f356`
- report blob: `a92ecc6b5bbba0f119a894dd26bb7ea3d1361ad1`
- receipt blob: `d6581fbf6bad1ac5026087cef0990ca57b7a7de4`

R377's source capture was R367 at approximately `2026-09-24T14:26:07Z`. Its top displayed rows were:

| historical displayed rank | participant/team | displayed Phase-2 score | exact underlying float |
|---:|---|---:|---|
| 1 | J2W / joe_wanza | `2.00e-9` | UNKNOWN |
| 2 | suliman_tadros | `2.20e-9` | UNKNOWN |
| 3 | marius_binner | `2.30e-9` | UNKNOWN |
| 4 | a_s6 | `2.50e-9` | UNKNOWN |
| 5 | dogus_ozel / Luna | `2.60e-9` | UNKNOWN |

R390 preserves those only as **historical displayed strings**. It does not assume they remain current and does not infer exact values from their rounded display.

## 2. Current official Phase-2 score/rule semantics

The current official Phase-2 announcement remains:

https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197

It states:

- Phase 2 submissions close **17 October 2026 23:59 UTC**;
- MLP shape **1024 wide × 16 deep**;
- per-MLP FLOP budget **2^41 = 2,199,023,255,552**;
- wall-clock cap **120 s**;
- residual wall-time cap **0.4 s**;
- solution-process memory cap **8 GB**;
- dataset revision **v2-phase2**;
- residual pricing removed, so **C_m = F_m**.

The current first-party WhestBench main head is still:

`AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

Current score documentation:

https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md

with report blob:

`3b66b33a0775f01eecbda2a148495d471f2eff65`.

The ranking quantity is the suite mean of:

`s_m = final_layer_mse_m × max(0.1, C_m/B_m)`

for valid runs, with failure multiplier 1.0.

The current starter-kit main head is still:

`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`.

Its Mini-100 documentation is:

https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-3-run-local.md

and explicitly defines Mini as **100 fixed 1024×16 MLPs with baked N=1e9 ground truth**.

### Current public submission-page panel evidence

Current official submission pages also show that the public/gated partition exposed for individual Phase-2 submissions is not uniformly identifiable from one fixed “50 public” public-page assumption:

- #330706: 50 public / 50 gated;
- #331027: 51 public / 49 gated;
- #331359: 55 public / 45 gated;
- #330812: 58 public / 42 gated.

R390 does **not** infer why these counts differ. It uses the narrow conclusion only:

> Public first-party pages do not establish that R209 Mini-100 and the current leaderboard/submission public aggregates use the same MLP set.

Those pages also state that the **full 100-MLP test score is the final ranking quantity**, with the gated/private portion sealed until results release. Therefore even a public-board lead would not itself prove the final win.

## 3. Our best measured score and provenance

### Best confirmed local competitive-style measurement

No newer repo artifact after R389 establishes a measured candidate or a submitted Phase-2 score.

The best confirmed internal/local score therefore remains R209 V25:

- artifact: `research/results/R209-v25-mini100.json`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- estimator family: V25
- panel: `v2-phase2 mini:all-100`
- rows: 100 fixed Mini MLPs
- exact recorded adjusted score: **8.170397440117225e-9**
- mean raw final-layer MSE: `2.228303490170447e-8`
- measured FLOPs/MLP: `806303721965`
- failures: 0
- local evaluator: `whestbench 0.16.1`
- local meter: `flopscope 0.12.1+np2.4.6`
- evidence class: **development/local**
- `official_scorer=false`
- `submission=false`
- `holdout=false`

This is exact for R209's local Mini-100 artifact and **NOT_COMPARABLE** to current leaderboard/public submission scores unless same phase + same MLP set + same scorer/runtime are proven.

### Submitted score

**No ARC repo evidence proves an own Phase-2 submission score after R389.**

R389:

- branch: `research/r389-portfolio-decision-20260925`
- head: `5344409a434c3fb1659f13b8740378294cec8f15`
- report blob: `efb18e6f1725c896abbd5c82432ade5e9d2a120e`

explicitly records:

- estimator/synthetic/benchmark/scorer runs: 0;
- submissions: 0.

Post-R389 repository check:

- no pre-existing `R390` branch;
- no branch names dated `20260926`, `20260927`, or `20260928`;
- no `r39*` branch existed before this R390 branch was created;
- main remains unchanged at `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`.

Thus there is no tracked post-R389 own candidate measurement or submission to supersede R209.

## 4. Honest win-prospect category

### Category: **UNESTABLISHED / NOT_COMPETITION_COMPARABLE**

This category means:

- there is a strong exact internal Mini-100 measurement (R209);
- current public first-party pages show Phase-2 submission scores in the low-e-9 range;
- but our exact local score is on a different evidence surface and no same-panel/current-official measurement exists;
- the current primary R389 research path (R385) had only a conditional theory/static-compute case and no measured score;
- no post-R389 own candidate or submission exists in repo evidence;
- the fresh current leaderboard rank/top itself was not recoverable from the read-only public leaderboard route in R390;
- final ranking is on the full 100-MLP test, whose gated/private portion remains sealed.

Therefore R390 does **not** classify ARC as leading, trailing by a quantified gap, or likely/unlikely to win. Any such statement would require converting non-comparable evidence into a competition forecast.

A safe orientation statement is narrower:

> We have an internally strong Phase-2-shaped Mini-100 baseline, but we do not currently possess competition-comparable evidence that establishes a winning position.

## 5. Minimum evidence needed to upgrade the category

The minimum useful upgrade is **one frozen own Phase-2 candidate measured on the same official ranking surface being compared**.

For a public-board upgrade, preserve an immutable artifact containing:

1. frozen estimator commit/path/blob hash;
2. exact official Phase-2 submission ID;
3. exact grader/runtime versions;
4. exact public-panel identity or enough immutable row identifiers to prove the panel;
5. all exposed per-MLP score/FLOP/failure rows;
6. exact machine-readable public aggregate if the platform exposes it;
7. public leaderboard rank and the timestamp/round used for that rank.

If the leaderboard only displays rounded strings, the artifact may establish a rank/current bar but must still not claim an exact numerical leader gap unless the unrounded leaderboard score or exact ranking precision is public.

To upgrade from “public-board competitive” to an actual **win** claim requires the final official **full 100-MLP** result for the designated Phase-2 submission, because current first-party submission pages explicitly state that the full-test score determines final rank and the gated/private portion remains sealed until release.

## 6. Final assessment

**Current leader:** not freshly verifiable from the read-only public leaderboard endpoint used by R390; no current top row/rank is fabricated.

**Current first-party public bar:** individual Phase-2 public submissions with displayed aggregates such as `2.460×10^-9` are visible without login, but they are not certified here as the current leaderboard leader.

**Our best exact measured result:** R209 V25, `8.170397440117225e-9`, local fixed Mini-100 development evidence.

**Comparability:** **NOT_COMPARABLE**.

**Win prospect:** **UNESTABLISHED / NOT_COMPETITION_COMPARABLE**.

**Next evidence that changes the answer:** one frozen own official Phase-2 measurement on the same public ranking surface, followed ultimately by the official full-100 final result.

## 7. Execution accounting

- logins: **0**
- browser/account changes: **0**
- downloads: **0**
- installs: **0**
- estimator/benchmark/generated-network runs: **0**
- Actions: **0**
- submissions/uploads: **0**
- private/sealed/holdout/full access: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- repository output: **exactly one Markdown memo**
