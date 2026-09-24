# R311 — Phase-2 leaderboard score comparability audit

**Status:** COMPLETE  
**Verdict:** **NOT_COMPARABLE**  
**Branch:** `review/r311-leaderboard-score-comparability-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Question

Can the current public Phase-2 leaderboard **ADJUSTED SCORE** be compared quantitatively, as the same score on the same panel, with the committed R209 V25 Mini-100 `adjusted_final_layer_score`?

**Answer: no.** The scoring formula is structurally the same, but the evaluated panels are not the same object: the current AIcrowd public score is the aggregate over **50 grader-public MLPs**, while R209 V25 is a local development aggregate over **100 MLPs from the published `v2-phase2` `mini` split**. R209 also records `official_scorer=false`. The public UI exposes only a rounded display value. R311 therefore does not compute a ratio, gap, or implied place.

## 1. Exact current public-score panel

An official current Phase-2 submission page exposes the scorer split semantics directly:

- top-level submission `Score` is the current public adjusted score;
- expanded `Adjusted score` is labeled **Public split**;
- it is described as the final-layer metric, **mean over 50 public MLPs**;
- the page shows `public · 50 scored`;
- a second **private / holdout split of 50 MLPs** is locked/sealed until results release;
- the page separately describes a **Full test set = 100 MLPs** final score once the sealed half is available.

Primary page:
https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

Therefore, for the live/current public Phase-2 leaderboard, the observable score is the **50-MLP grader public split aggregate**, not the R209 Mini-100 aggregate and not the still-sealed 100-MLP full-test aggregate.

This report does not enumerate or map the 50 grader-public names/IDs; that would duplicate the separate R305 identity/manifest audit.

## 2. Score formula and aggregation

The official WhestBench scoring implementation defines, for each MLP (m):

```
final_layer_mse_m = mean_i((prediction_m[-1,i] - truth_m[-1,i])^2)

s_m = final_layer_mse_m * max(0.1, C_m / B_m)   # valid run
s_m = final_layer_mse_m * 1.0                    # failure
```

and the suite score is the arithmetic mean:

```
adjusted_final_layer_score = mean_m(s_m)
```

Official source, pinned current repository commit inspected by R311:
- repository: `AIcrowd/whestbench`
- commit: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`
- file: `src/whestbench/scoring.py`
- blob: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- URL: https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py

The official score-report schema/documentation states the same contract: `adjusted_final_layer_score` is the leaderboard metric and is the suite mean of the per-MLP budget-adjusted scores.

- file: `docs/reference/score-report-fields.md`
- blob: `3b66b33a0775f01eecbda2a148495d471f2eff65`
- URL: https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md

For Phase 2 specifically, the official launch announcement fixes:
- (B_m = 2^{41} = 2,199,023,255,552) FLOPs per MLP;
- residual pricing (lambda = 0);
- therefore (C_m = F_m), the metered FLOPs;
- residual wall time is capped separately at 0.4 s.

Official organizer announcement:
https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197

R311 does not compare evaluator/meter package versions beyond these score semantics; exact toolchain-difference analysis is R309 scope.

## 3. Rounding / displayed precision

There is **no explicit score rounding step in the canonical WhestBench aggregation** above: per-MLP Python float scores are accumulated and the aggregate is returned as a float.

Official WhestBench human presentation formats MSE-style values with:

```python
f"{float(value):.2e}"
```

i.e. three significant digits in scientific notation.

- file: `src/whestbench/presentation/adapters.py`
- blob: `bc92da337db234b598303dda96e3da470e126e4e`
- same repository commit `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

The official AIcrowd Phase-2 submission page gives an observable example of presentation rounding: the detail card shows `1.932×10−8` while the top-level `Score` shows `1.93 e−8`.

However, R311 did **not** find an admissible primary source publishing the exact formatter used by the AIcrowd leaderboard frontend itself. Therefore:

- calculation-time rounding: **none established**;
- WhestBench human-format convention: **3 significant digits**;
- AIcrowd current submission-header display: **observed 3 significant digits**;
- exact leaderboard frontend rounding implementation: **UNKNOWN**;
- exact unrounded score cannot be recovered from a displayed leaderboard value alone.

## 4. Committed R209 V25 evidence

The committed R209 receipt is:

- commit: `e1f6dd6a6bc351b8253e255fef424b1931b37de3`
- path: `research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json`
- blob: `7fec90369227839a9902c7cceb9f3519acb66cb8`
- URL: https://github.com/tim8es/arc-whitebox/blob/e1f6dd6a6bc351b8253e255fef424b1931b37de3/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json

It records V25 as:

- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`;
- split: `mini`;
- `n_mlps_requested = 100`;
- `n_mlps_reported_each_version = 100`;
- width/depth: `1024 × 16`;
- stage/evidence usage: local development/archive evidence;
- `official_scorer = false`;
- `holdout = false`;
- `full_split = false`;
- failures: `0/100`;
- V25 `adjusted_final_layer_score = 8.170397440117225e-9`.

That number is the arithmetic mean of the 100 recorded Mini-split per-MLP adjusted scores. It is a valid committed R209 local score, but it is **not the same-panel quantity** as the live AIcrowd public-50 score.

## 5. Comparability decision

| Dimension | Result |
|---|---|
| Metric definition | **MATCHES STRUCTURALLY** — per-MLP final-layer MSE × budget multiplier, arithmetic mean |
| Phase-2 budget semantics | **MATCHES AT CONTRACT LEVEL** — (B=2^{41}), (C_m=F_m) |
| Evaluation panel size | **DIFFERS** — live public grader 50 vs R209 Mini 100 |
| Exact panel identity | **NOT ESTABLISHED IN R311**; detailed identity audit belongs to R305 |
| Official scorer | **DIFFERS/UNPROVEN** — R209 explicitly says `official_scorer=false` |
| Exact leaderboard float | **UNKNOWN** from rounded public display |
| Exact evaluator/meter equivalence | **OUT OF R311 SCOPE**; R309 owns that audit |
| Honest direct quantitative comparison | **NO** |

**Final decision: `NOT_COMPARABLE`.**

R311 does not output any ratio, score gap, inferred rank, or place.

## 6. Concrete missing fields required to upgrade comparability

At minimum, an exact comparison would require:

1. **V25 per-MLP score evidence on the exact 50 grader-public MLPs**, or a proven exact join showing which R209 records correspond to those 50 plus a justified recomputation on that exact subset.
2. **An immutable public-50 panel identity/join key** sufficient to establish that join. R311 does not redo R305's manifest/name-to-network-ID work.
3. **The exact unrounded AIcrowd public aggregate** (or an official raw score field/API), if the comparison is intended below the public display's rounding precision.
4. **Compatible scorer/toolchain semantics for the two measurements**, a separate prerequisite whose detailed version audit is explicitly left to R309.

Without these fields, the only defensible statement is that R209 and the live leaderboard use the same high-level score formula on **different/unproven panels**.

## Sources used

Only primary sources plus the committed R209 receipt were used:

1. Official AIcrowd Phase-2 submission page #329251:
   https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251
2. Official AIcrowd Phase-2 launch announcement:
   https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197
3. Official `AIcrowd/whestbench` scoring source at `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`:
   https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py
4. Official WhestBench score-report fields at the same commit:
   https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md
5. Official WhestBench presentation adapter at the same commit:
   https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/presentation/adapters.py
6. Committed R209 receipt:
   https://github.com/tim8es/arc-whitebox/blob/e1f6dd6a6bc351b8253e255fef424b1931b37de3/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json

## Constraints

No benchmark, estimator run, dataset/dependency download, GitHub Actions run, competition submission, private/holdout/full access, or leaderboard polling beyond public primary pages. No main/PR/control edits. No R305 identity audit duplication. No R309 toolchain-diff duplication. No R310 top-20 work.
