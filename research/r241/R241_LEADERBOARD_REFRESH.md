# R241 — Official Phase-2 leaderboard refresh

Checked: 2026-09-23 03:31:44 UTC, timestamped immediately after re-fetching the public AIcrowd leaderboard. The page labels its snapshot 'Crawled: today'; the browser tool does not expose underlying HTML bytes or a content digest.

## Current public leaderboard snapshot

AIcrowd's live leaderboard showed:

- Rank 1: **J2W**, submission [#331539](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539).
- Adjusted score: **0.0000000021** (displayed, rounded); final-layer MSE **0.0000000164**; compute utilization **0.1306572576**; failed MLPs **0**; 310 entries; latest submission shown as 19 Sep 2026 00:05 UTC.
- Rank 2 was **suliman_tadros**, displayed score **0.0000000022**, last submission 23 Sep 2026 01:42 UTC.

The official starter-kit documentation defines `adjusted_final_layer_score` as the leaderboard metric: mean of per-MLP `final_layer_mse × max(0.1, C/B)`, with failures receiving multiplier 1.0; lower is better.

## Comparison with our current reproducible public result

The control-branch record [R209-v25-mini100](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/results/R209-v25-mini100.json) has 100 rows, 0 failures, Phase-2 `v2-phase2`, `mini:all-100`, float32, width 1024 × depth 16, and score **8.170397440117225e-9** (recomputed from all 100 per-network rows with the official formula). Its Git blob SHA-1 is `0183d0570f7c9965e00e8553ffc003c313865232`.

Against the leaderboard's rounded display only, our number is approximately **3.8907×** the rank-1 displayed score, or **289.1% higher** (worse, since lower is better). This is a conditional numeric comparison, not an official rank or a confirmed same-panel gap.

## Comparability decision

**No official rank is inferred.** The metric formula matches the official leaderboard metric, but the leaderboard table does not expose the scored panel or aggregation metadata for submission #331539. R209 is explicitly a 100-network public development mini panel. Without exact panel/aggregation evidence, strict leaderboard comparability is **NOT VERIFIED**.

The current Phase-2 announcement says submissions close 17 October 2026 at 23:59 UTC. This refresh involved only public pages and the public R209 record; no private/holdout data, estimator or benchmark execution, Actions run, paid resource, submission, or leaderboard mutation.

## Sources

- [AIcrowd Phase-2 leaderboard](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards)
- [AIcrowd Phase-2 announcement and rules summary](https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197)
- [Official score-report fields](https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/score-report-fields.md)
- [Official public Mini evaluation instructions](https://github.com/AIcrowd/whest-starterkit/blob/main/docs/getting-started/stage-3-run-local.md)
- [R209 V25 normalized result](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/results/R209-v25-mini100.json)
