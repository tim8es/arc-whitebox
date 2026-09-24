# R325 — conditional public-50 bounds from committed R209 V25 Mini-100 rows

Status: **COMPLETE — CONDITIONAL ENVELOPE ONLY; NOT A LEADERBOARD RESULT**

- Exact repository base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Report-only branch: `review/r325-r209-mini100-public50-conditional-bounds-20260924`
- No estimator/benchmark execution, no code, no dataset/dependency download, no Actions, no paid compute, no private/holdout/full access, no submission, and no main/PR/control/queue edit.

## 1. Authoritative committed R209 V25 per-MLP source

The calculation uses the committed normalized result:

- path: `research/results/R209-v25-mini100.json`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22` — “results: integrate R224 normalized R209 mini-100 records”
- git blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- file SHA256 recorded by R231: `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`
- underlying R209 archive V25 per-MLP canonical-record SHA256: `85472c4808bff7a83a9ca853688ad9068895b073bb1592fd0f364d82c112b13e`
- runtime index/metric SHA256 recorded by the archive audit: `f5605b03d55808ac4afd7ff2de42c317b96ae20483551a2f7ddddb9d89cd680b`

Source links:

- https://github.com/tim8es/arc-whitebox/blob/20fafab5471e6ed227562c651179dd2ef331ea22/research/results/R209-v25-mini100.json
- https://github.com/tim8es/arc-whitebox/commit/20fafab5471e6ed227562c651179dd2ef331ea22
- archive audit: https://github.com/tim8es/arc-whitebox/blob/research/r209-e136-archive-evidence/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json
- R231 independent arithmetic audit: https://github.com/tim8es/arc-whitebox/blob/research/r265-method-theory-scout-20260923/research/r231/R231_V25_ERROR_TAIL_REPORT.md

The normalized file contains exactly 100 `per_network` rows, 100 unique `network_id` values, and each row has both:

- `final_mse` — raw final-layer MSE;
- `official_adjusted_score` — the per-MLP budget-adjusted score used in this calculation.

All 100 rows are `status="ok"` with no failure reasons.

## 2. Independent scorer / units verification

R209 records `whestbench 0.16.1`. The pinned v0.16.1 source is commit
`4d08668b485c8a7d25a105c3c00d2f4fc2538f18`.

Relevant immutable source blobs:

- `src/whestbench/scoring.py`: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- `src/whestbench/budget.py`: `6586f12d178e0136420cb282535663f1faad5abc`
- `docs/reference/rounds.md`: `c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890`

Official per-MLP formula for a valid row is

[
s_m = operatorname{MSE}_{m,mathrm{final}},
      max(0.1, C_m/B_m).
]

Failures use multiplier 1.0. The suite aggregate `adjusted_final_layer_score` is the arithmetic mean of the per-MLP scores.

For current `v2-phase2`, the official rounds document states `lambda=0`, hence
[
C_m=F_m.
]

Every committed R209 V25 row has:

- `B_m = 2^41 = 2,199,023,255,552` FLOPs;
- `F_m = 806,303,721,965` FLOPs;
- `F_m/B_m = 0.36666448157347986 > 0.1`.

Recomputing
[
	exttt{final_mse}	imes max(0.1,	exttt{measured_flops}/	exttt{budget_flops})
]
for all 100 committed rows gives maximum absolute discrepancy **0** from
`official_adjusted_score` in binary-float arithmetic.

Therefore the values bounded below are **adjusted per-MLP scores, not raw MSE**. The multiplier is dimensionless, so adjusted score has the same MSE units as final-layer MSE, numerically scaled by the compute multiplier.

Official source links:

- https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py
- https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/budget.py
- https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/docs/reference/rounds.md

## 3. Sharp 50-of-100 conditional envelope

Let the 100 committed per-MLP adjusted scores sorted ascending be

[
s_{(1)}lecdotsle s_{(100)}.
]

For any subset (S) of exactly 50 rows,

[
ar s(S)=rac1{50}sum_{iin S}s_i.
]

The sharp extrema are

[
L_{50}=rac1{50}sum_{i=1}^{50}s_{(i)},qquad
U_{50}=rac1{50}sum_{i=51}^{100}s_{(i)}.
]

This is sharp by the elementary exchange/order-statistic argument: no 50-element subset can have a sum below the 50 smallest values or above the 50 largest, and both extrema are attained by those two subsets.

Using the decimal values serialized in the committed JSON:

- sum of 50 smallest = `3.621436058919074213e-7`
- **minimum possible 50-row mean = `7.242872117838148426e-9`**
- sum of 50 largest = `4.5489613811981524e-7`
- **maximum possible 50-row mean = `9.0979227623963048e-9`**

Useful boundary checks:

- smallest single row: `5.269560766710126e-9`
- 50th sorted row: `8.345217855754383e-9`
- 51st sorted row: `8.357294760239438e-9`
- largest single row: `1.1105773382971547e-8`

The arithmetic mean of the 100 serialized row values is
`8.170397440117226613e-9`, consistent to serialization/float-rounding precision with the archived R209 aggregate
`8.170397440117225e-9`.

## 4. The condition is not established

This envelope becomes relevant to grader public-50 **only under both assumptions**:

> **IF** the grader public-50 is exactly some 50-row subset of the R209 `mini:all-100` panel **AND** the scorer is comparable, **THEN** its R209-V25 mean adjusted score must lie in
> [
> [7.242872117838148426	imes10^{-9},
>  9.0979227623963048	imes10^{-9}].
> ]

Neither membership nor an exact row join is established.

R319 independently concluded `NOT_JOINABLE`: the public 50 exposes no admissible direct identity key and “existing evidence does not establish that the grader-public 50 are a particular 50-row subset of R209 Mini-100.”

- R319 head: `9086b846cc6e11ad91117870c3015d25bfc5504a`
- report blob: `c858a8f3bd29f50c5188894aeaaa73e2208a374f`
- https://github.com/tim8es/arc-whitebox/blob/review/r319-public50-r209-join-audit-20260924/research/r319/R319_PUBLIC50_R209_JOIN_AUDIT.md

R322 then found that the identity-bearing evaluation mapping exists in the evaluation-data workflow but the exact deployed Phase-2 public-50 mapping is **not publicly exposed**.

- R322 head: `552010f48d67d70b6bb8aae84fe4fc271ccf3f81`
- report blob: `4f0b925acac9779b8fd6794418065d8bd6565e33`
- https://github.com/tim8es/arc-whitebox/blob/review/r322-public50-manifest-source-audit-20260924/research/r322/R322_PUBLIC50_MANIFEST_SOURCE_AUDIT.md

Therefore R325 does **not** identify the actual public-50 subset and does not compute an actual public leaderboard score for R209.

## 5. Conditional comparison to the currently displayed leaderboard row

The official public leaderboard currently displays rank 1 Adjusted Score as exactly the visible text

`0.0000000021` = `2.10e-9`

in the observation around **2026-09-24 10:20 UTC**:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

R325 does not infer the hidden exact float, rounding interval, or formatter behind that displayed text.

Relative to that text, the conditional R209 50-of-100 envelope
[
[7.242872117838148426e-9,;9.0979227623963048e-9]
]
is narrower and lies numerically above the displayed `2.10e-9`. Thus, **under the two explicit assumptions only**, the envelope rules out a conditional R209-V25 public-50 mean near that displayed value.

This is **not** a measured leaderboard gap, place, rank prediction, or proof that R209 was evaluated on the grader public-50. Both the subset identity and exact cross-surface comparability remain unproved.

A safe summary is:

> The conditional envelope adds information about what *any 50-row subset of the committed R209 Mini-100 scores* can average. It does not turn those 100 development rows into a competition result.

## 6. Reproducibility recipe

No estimator or dataset access is required.

1. Read exactly `research/results/R209-v25-mini100.json` at commit `20fafab5471e6ed227562c651179dd2ef331ea22`.
2. Verify git blob `0183d0570f7c9965e00e8553ffc003c313865232` and the recorded file SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.
3. Extract exactly the 100 `per_network[*].official_adjusted_score` decimal values.
4. Sort ascending.
5. Average rows 1–50 for the lower extremum and rows 51–100 for the upper extremum.
6. Do not substitute `final_mse` for `official_adjusted_score`.
7. Treat the result only as conditional unless an exact public-50→R209 identity mapping is later proven.
