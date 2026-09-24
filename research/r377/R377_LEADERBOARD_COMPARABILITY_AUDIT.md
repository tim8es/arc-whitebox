# R377 — Phase-2 leaderboard / target-bar comparability audit

**Status:** COMPLETE  
**Verdict:** **NOT_COMPARABLE_NO_EXACT_RANK_OR_TRUE_GAP**  
**Classification:** PUBLIC-SOURCE + EXISTING-REPO-EVIDENCE AUDIT; NO NEW LEADERBOARD CAPTURE  
**Branch:** `research/r377-leaderboard-comparability-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Audit date:** 2026-09-24

## 1. Question

Can the current public Phase-2 leaderboard target bar be compared honestly with the committed R209 V25 value

`8.170397440117225e-9`

measured on `v2-phase2 mini:all-100`, and can an exact place or score gap be derived?

**No.** Two independent blockers remain:

1. **panel mismatch / missing join:** the public leaderboard score is over the grader's 50 public MLPs, while R209 is a local development aggregate over the published 100-MLP `mini` split;
2. **leaderboard exact-score opacity:** the saved leaderboard evidence contains displayed score strings, but the exact underlying leaderboard floats and the Phase-2 challenge-specific score-precision/formatter rule are not public evidence.

The top-10 display can therefore be used only as a **displayed target bar**, not as an exact numerical comparator.

## 2. Current Phase-2 primary-source semantics

### Official Phase-2 announcement

AIcrowd's organizer announcement, current public source:

https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197

It states:

- Phase 2 is live;
- submissions close **17 October 2026 23:59 UTC**;
- MLP architecture: **1024 wide × 16 deep**;
- FLOP budget per MLP: **2^41 = 2,199,023,255,552**;
- wall cap: **120 s**;
- residual wall cap: **0.4 s**;
- Phase-2 dataset revision: **v2-phase2**;
- residual pricing is removed, so effective cost is metered FLOPs, `C_m = F_m`.

### Exact grader package pair publicly stated by organizer

Official organizer reply:

https://discourse.aicrowd.com/t/shipped-covariance-propagation-example-trips-the-phase-2-residual-cap-locally-0-16-0-but-grades-fine-what-happens-when-the-evaluator-upgrades/18202/2

It states that evaluators actually run:

- `whestbench@v0.16.0`;
- `flopscope[server]==flopscope[client]==0.12.0`.

### Current WhestBench public source

As checked during R377, the public `AIcrowd/whestbench` default branch `main` is still:

`4794ce8673c1221bdb245b19e933ae0afd7ffa3c`.

Official scoring source at that commit:

https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py

Official score-field documentation:

https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md

The score contract is:

`s_m = final_layer_mse_m * max(0.1, C_m/B_m)` for a valid row,

failure rows use multiplier 1.0, and

`adjusted_final_layer_score = mean_m(s_m)`.

### Public-vs-private panel semantics

Official public Phase-2 submission page:

https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

It currently states:

- public split: **50 / 50 MLPs scored**;
- displayed public Adjusted Score is the mean over **50 public MLPs**;
- private split: **50 sealed MLPs**;
- full test set: **100 MLPs**;
- the full-test score after sealed release is the final ranking quantity.

Thus the currently visible public leaderboard metric is a **public-50 aggregate**, not the published-development Mini-100 aggregate.

## 3. Existing R367 leaderboard evidence — no recapture

R377 did **not** repeat the top-10 capture.

Existing immutable artifact:

- branch: `review/r367-live-leaderboard-top10-capture-20260924`
- head: `8906d5abaa0d4688be6ceb89370ce7dcd27dbb4b`
- report: `research/r367/R367_LIVE_LEADERBOARD_TOP10_CAPTURE.md`
- report blob: `b9cc97c753fe2629c20326557d3f5a1b0988317d`
- receipt: `research/r367/R367_RECEIPT.json`
- receipt blob: `927b354159c7c2a13911c45443a297f1d0cd79c6`
- source route: Phase-2 leaderboard, `?round=phase-2`
- capture time: approximately `2026-09-24T14:26:07Z`, coordinator-provided
- visible range: `Showing 1–100 of 197`.

This is the latest persisted top-10 evidence used by R377. R377 does not claim the board could not have changed after that timestamp.

### R367 top-10 score status

| R367 displayed rank | Participant/team | Phase | displayed Adjusted Score | exact underlying score |
|---|---|---|---:|---|
| 01 | J2W / joe_wanza | Phase 2 | `2.00e-9` | **UNKNOWN** |
| 02 | suliman_tadros | Phase 2 | `2.20e-9` | **UNKNOWN** |
| 03 | marius_binner | Phase 2 | `2.30e-9` | **UNKNOWN** |
| 04 | a_s6 | Phase 2 | `2.50e-9` | **UNKNOWN** |
| 05 | dogus_ozel / Luna | Phase 2 | `2.60e-9` | **UNKNOWN** |
| 06 | Puffi | Phase 2 | `2.80e-9` | **UNKNOWN** |
| 06 | Oldboy / reds | Phase 2 | `2.80e-9` | **UNKNOWN** |
| 08 | oqaris | Phase 2 | `3.10e-9` | **UNKNOWN** |
| 08 | ben3 | Phase 2 | `3.10e-9` | **UNKNOWN** |
| 08 | mliston | Phase 2 | `3.10e-9` | **UNKNOWN** |

The strings above are **display text**, not audited raw floats.

## 4. Why displayed leaderboard values are not exact scores

Prior primary-source audit R348 remains applicable:

- branch: `review/r348-leaderboard-display-precision-audit-20260924`
- head: `4329109ff12afb44259b8221726dbb3f384688a5`
- report blob: `77a88dd22cb29b2a6cc7a3a9e346c6ee2d665554`
- receipt blob: `ce0268c5f1e37d2dbe1b05ad84bf989ac9f12771`
- verdict: `UNKNOWN_FORMATTER_NOT_PUBLICLY_OBSERVABLE`.

Current first-party AIcrowd design documentation still exposes a per-round **Score Precision** setting described as “Round off precision to compute ranks”:

https://design.aicrowd.com/pages/edit-challenge-rounds-admin

But public evidence does **not** expose the Phase-2 value of that setting or prove the leaderboard web formatter/rounding rule.

Therefore R377 does not:

- convert `2.00e-9` into a hypothetical interval;
- assume Python `.2e`;
- assume round-half-even, truncation, or any other rounding rule;
- infer the exact gap between any two displayed leaderboard entries.

The WhestBench local presentation helper using `f"{float(value):.2e}"` is a different presentation layer and is not evidence for the AIcrowd web leaderboard renderer.

## 5. R209 exact local evidence

Normalized R209 record:

- path: `research/results/R209-v25-mini100.json`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- Git blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini:all-100`
- rows: 100
- shape: 1024 × 16
- failures: 0
- exact recorded adjusted score: **`8.170397440117225e-9`**
- mean raw final-layer MSE: `2.228303490170447e-8`
- measured FLOPs/network: `806303721965`
- maximum residual wall time: `0.19043814401743475 s`
- local evaluator: `whestbench 0.16.1`
- local meter: `flopscope 0.12.1+np2.4.6`
- stage: development.

The archive audit explicitly records `official_scorer=false`, `holdout=false`, `full_split=false`, and `submission=false`.

## 6. Toolchain compatibility does not repair the panel mismatch

R309 source-only audit:

- branch: `review/r309-toolchain-delta-audit-20260924`
- head: `1e23a25550369da60b976416fe0f502a6189b833`
- report blob: `d26f0174b32ffa647a0454bb24be038cdf0e14c1`
- receipt blob: `2eb00990f3e1e8465ca48e918718033c0ecbd395`.

R309 found the direct WhestBench scoring/evaluator source semantics applicable to frozen V25 **compatible** across grader `0.16.0/0.12.0` and local `0.16.1/0.12.1`; V25 does not use the identified FlopScope price-changing paths.

However, R309 also leaves exact grader-runtime numeric replay **UNKNOWN**, and source compatibility does not convert Mini-100 into the grader public-50 panel.

## 7. Visible-50 identity is not joinable to R209 Mini-100

R305:

- branch: `review/r305-visible50-manifest-audit-20260924`
- head: `d6124d78714e9882f7d7384b6ad6482af22f7301`
- report blob: `d45093692dea0338acd65e612743ea5ed32e74ed`
- receipt blob: `6dca6965c3ef27263d1d1cd2aea12d303a485d9d`
- verdict: `NOT_COMPARABLE`.

The public submission ledger exposes `mlp_index` / `mlp_name` but no public `network_id` or `target_sha256` identity key. The prior identity audit found **0/50 visible-name overlap with R209**. Therefore no 50-row R209 subset score can be honestly reconstructed from the archived Mini-100 rows.

## 8. Comparability matrix

| Property | Public Phase-2 leaderboard | R209 V25 | Result |
|---|---|---|---|
| Round | Phase 2 | Phase-2 dataset revision | compatible round family |
| Metric formula | adjusted final-layer score | same structural formula | structurally compatible |
| Width/depth | 1024 × 16 | 1024 × 16 | match |
| Budget semantics | `B=2^41`, `C=F` | same recorded contract | match |
| Public evaluated rows | grader public 50 | published mini 100 | **mismatch** |
| Exact panel join | public IDs unavailable | network IDs/target hashes archived | **not joinable** |
| Grader pair | 0.16.0 / 0.12.0 | 0.16.1 / 0.12.1 | source-compatible for V25, exact runtime replay unknown |
| Leader exact aggregate | **UNKNOWN** | exact local aggregate known | **not exact-comparable** |
| Leader displayed aggregate | known strings | local exact float | display-only orientation, not score comparison |
| Exact placement | not derivable | — | **NO** |
| Exact true score gap | not derivable | — | **NO** |

## 9. Can R377 honestly state a place or gap?

### Place

**No.**

R377 cannot place R209 on the Phase-2 leaderboard because R209 has never been measured on the exact grader public-50 panel, and no submission is authorized or performed.

### Exact numerical gap

**No.**

Subtracting a displayed `2.00e-9`, `2.20e-9`, etc. from R209's exact Mini-100 `8.170397440117225e-9` would combine:

- different panels; and
- an exact local float with an unknown-rounded leaderboard display string.

Such a number would not be a competition-score gap.

### What can be stated

Only this display-level observation:

> At the R367 capture time, Phase-2 top-10 displayed Adjusted Scores ranged from `2.00e-9` through `3.10e-9`; R209's committed local Mini-100 adjusted score is `8.170397440117225e-9`. These are **not directly comparable score measurements**.

No ratio, placement, target reduction percentage, or true gap is inferred from those values.

## 10. Minimum public same-conditions artifact

There are two levels of closure.

### A. Minimum artifact to make **R209 itself comparable to the public leaderboard metric**

A single immutable artifact, call it for example:

`R209_V25_PHASE2_PUBLIC50_EXACT_RECEIPT.json`

must contain, for the **exact grader-public 50 MLPs**:

1. immutable public-panel identity:
   - `mlp_index`, `mlp_name`;
   - preferably `network_id` and `target_sha256`, or another first-party immutable join key;
2. frozen V25 estimator source/blob identity;
3. exact grader environment:
   - `whestbench 0.16.0`;
   - `flopscope client/server 0.12.0`;
   - runtime/NumPy/build digest sufficient for exact replay claims;
4. all 50 per-MLP:
   - exact final-layer MSE;
   - exact adjusted score;
   - metered FLOPs;
   - failure flags;
   - residual/wall timing;
5. exact machine-readable public-50 aggregate;
6. hashes/manifests binding the rows and aggregate.

This artifact must come from the exact public-50 conditions; another Mini-100 run is insufficient.

A public official 50-row manifest would be enough **only if** it establishes a join to already archived rows. Existing evidence says that join is not presently available, so the practical minimum is an exact-public-50 V25 measurement artifact.

### B. Additional public fact required for an **exact leader gap / counterfactual place without submission**

Even after A, the exact leader gap remains unknown unless one of these is public:

- an official machine-readable leaderboard payload exposing the unrounded primary scores; or
- the exact Phase-2 challenge-specific ranking precision/rounding rule **plus** enough raw score information to reproduce ranking.

The generic AIcrowd “Score Precision” control proves such a setting exists; it does not disclose this round's value.

Without B, a same-public-50 V25 artifact would establish metric/panel comparability, but comparison to leaders would still be limited by the leaderboard's public numeric precision.

## 11. Final verdict

**NOT_COMPARABLE_NO_EXACT_RANK_OR_TRUE_GAP.**

- R367 top-10 display is valid public Phase-2 UI evidence at its recorded timestamp.
- Leader exact underlying scores remain unknown.
- R209 `8.170397440117225e-9` is exact for its local Mini-100 development panel, not the public grader-50.
- No honest rank or exact competition gap follows.
- No new leaderboard capture was necessary for this audit.

## 12. Execution accounting

- new leaderboard capture: **NO**
- leaderboard polling/capture by R377: **0**
- contest dataset downloads: **0**
- estimator/benchmark runs: **0**
- submissions: **0**
- private/sealed/holdout/full access: **NO**
- Actions: **0**
- dependency installs: **0**
- main edits: **0**
- R320 edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- repository output: exactly this report + one JSON receipt on the dedicated R377 branch
