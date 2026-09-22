# R228 — Official leaderboard and rankability audit protocol

Frozen before source research.

- Job: R228 / OFFICIAL-LEADERBOARD-RANKABILITY-AUDIT.
- Scope: read-only audit of ARC White-Box Phase 2 competition rankability.
- Sources: primary official sources only (official challenge/leaderboard/submission pages, official ARC/AIcrowd starter kit and its official documentation/code).
- Questions:
  1. What is the official Phase-2 scoring rule and failure/resource treatment?
  2. What public leaderboard scores/submissions are visibly exposed at retrieval time?
  3. What exact evaluation panel/split is documented for leaderboard scoring, including whether public/private rows and their identities are locally available?
  4. Are the published R209 mini-100 V25/V29 records exactly comparable to any visible competition score/rank?
- Rankability gate: no rank or place claim unless metric, evaluator semantics, panel identity, and submitted artifact context are exactly comparable and evidenced by official sources. Otherwise record the precise evidence gap.
- Evidence handling: record retrieval timestamp(s), canonical URLs, relevant version/commit identifiers where available, and distinguish observed facts from unavailable/undocumented fields.
- Repository limits: docs/research artifacts only. Do not run an estimator, use paid compute, submit to the competition, alter canonical results, or mutate external systems.
- Planned outputs: `research/R228_OFFICIAL_LEADERBOARD_AUDIT.md` and `research/R228_OFFICIAL_LEADERBOARD_AUDIT_RECEIPT.json`.
