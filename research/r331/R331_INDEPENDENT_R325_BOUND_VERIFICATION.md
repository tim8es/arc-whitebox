# R331 — independent quantitative red-team of R325

**Status:** COMPLETE  
**Verdict:** **PASS — R325 saved quantitative results independently reproduced**  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r331-independent-r325-bound-verification-20260924`  
**Scope:** arithmetic/provenance verification only; no estimator or benchmark rerun.

## 1. R325 frozen target

Exact R325 head audited:

`efd518021ccc120ccb4e859f2588648d83f2b57f`

Artifacts:

- `research/r325/R325_R209_MINI100_PUBLIC50_CONDITIONAL_BOUNDS.md`
  - Git blob: `05f568f257c7e7a23244232deecd19b108184529`
- `research/r325/R325_RECEIPT.json`
  - Git blob: `80be370c465323a5f74760595fb582051f1866ba`

R331 does not modify R325.

## 2. Authoritative R209 input provenance

Authoritative file:

`research/results/R209-v25-mini100.json`

R331 fetched the file independently from both:

- integration commit `20fafab5471e6ed227562c651179dd2ef331ea22`;
- R224 normalization/fingerprint commit `8fb0afb77ae834d88bae29557a41356d4d98401f`.

Both refs resolve to the exact same Git blob:

`0183d0570f7c9965e00e8553ffc003c313865232`

R331 independently recomputed SHA-256 over the fetched UTF-8 JSON bytes. Result:

`f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`

This exactly matches the recorded R209/R325 file SHA-256.

The normalized file identifies:

- id: `R209-v25-mini100`;
- panel: `v2-phase2 mini:all-100`;
- stage: `development`;
- count: 100;
- evaluator: `whestbench 0.16.1`;
- meter: `flopscope 0.12.1+np2.4.6`;
- dtype: `float32`;
- shape: 16 × 1024.

## 3. Row and field validation

Independent validation of `per_network`:

- rows: **100**
- unique `network_id`: **100**
- all rows contain `final_mse`, `official_adjusted_score`, `measured_flops`, `budget_flops`, `status`, and `failure_reasons`;
- all `final_mse` values finite;
- all `official_adjusted_score` values finite;
- all rows: `status="ok"`;
- failure rows: **0**;
- common `budget_flops`: **2,199,023,255,552 = 2^41**;
- common `measured_flops`: **806,303,721,965**;
- common compute ratio: **0.36666448157347986**.

Thus the bound input is exactly 100 valid per-MLP adjusted-score rows, not raw MSE rows.

## 4. Pinned scorer formula and semantics

Pinned R209 evaluator version: **WhestBench 0.16.1**, source commit:

`4d08668b485c8a7d25a105c3c00d2f4fc2538f18`

Verified immutable source blobs:

- `src/whestbench/scoring.py`: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- `src/whestbench/budget.py`: `6586f12d178e0136420cb282535663f1faad5abc`
- `docs/reference/rounds.md`: `c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890`

For a valid row the source computes

`official_adjusted_score = final_mse * max(0.1, C / B)`.

Failure/no-budget uses multiplier 1.0.

For `v2-phase2`, residual mode is gated and the residual price is zero, so

`C = F`.

Since every R209 row is valid and `F/B = 0.36666448157347986 > 0.1`, R331 independently recomputed all 100 rows as

`final_mse * measured_flops / budget_flops`.

**Maximum absolute discrepancy against stored `official_adjusted_score`: 0** in binary floating-point arithmetic.

R325's recorded scorer discrepancy of 0 is therefore confirmed.

## 5. Independent exact-decimal sort and 50/50 arithmetic

R331 extracted the 100 serialized decimal lexemes from
`per_network[*].official_adjusted_score`, converted them to exact base-10 integers at a common decimal scale, sorted ascending, and recomputed the two sharp 50-row extrema without using rounded display values.

Result:

| Quantity | Independent R331 value | R325 | Check |
|---|---:|---:|---|
| sum 50 lowest | `3.621436058919074213e-7` | same | PASS |
| mean 50 lowest | **`7.242872117838148426e-9`** | same | PASS |
| sum 50 highest | `4.5489613811981524e-7` | same | PASS |
| mean 50 highest | **`9.0979227623963048e-9`** | same | PASS |
| smallest row | `5.269560766710126e-9` | same | PASS |
| 50th row | `8.345217855754383e-9` | same | PASS |
| 51st row | `8.357294760239438e-9` | same | PASS |
| largest row | `1.1105773382971547e-8` | same | PASS |
| exact mean of 100 serialized rows | `8.170397440117226613e-9` | same | PASS |

The 50th and 51st values are strictly ordered, so there is no boundary-tie ambiguity.

The exact 50 lower witness `network_id` sequence and exact 50 upper witness sequence in R325's receipt also match the independently sorted rows.

The serialized 100-row mean differs from the archived binary-float aggregate
`8.170397440117225e-9` only by approximately
`1.6543612251060553e-24`, consistent with serialization/binary-float representation.

## 6. Bound theorem check

For any 50-element subset of 100 scalar scores, the minimum subset sum is attained by the 50 smallest scores and the maximum by the 50 largest scores. Therefore R325's conditional interval

`[7.242872117838148426e-9, 9.0979227623963048e-9]`

is the sharp 50-of-100 envelope for the committed R209 per-network adjusted-score values.

No estimator assumptions are needed for this order-statistic statement.

## 7. Conditionality / leaderboard guardrail red-team

R325 passes the requested interpretation checks.

It explicitly states:

- the result is **“CONDITIONAL ENVELOPE ONLY; NOT A LEADERBOARD RESULT”**;
- the grader public-50 must be exactly a 50-row subset of R209 Mini-100 **and** scorer semantics must be comparable before the envelope can be applied to that panel;
- exact membership/join is **not established**;
- R319 is `NOT_JOINABLE`;
- R322 says the identity-bearing evaluation mapping exists in the evaluation workflow but the exact deployed public-50 mapping is **not publicly exposed**;
- the displayed leaderboard value `2.10e-9` is treated only as visible rounded text;
- exact leaderboard float and formatter are unknown;
- R325 claims **no actual leaderboard gap, place, rank prediction, exact score, or public-50 membership**.

Therefore R325 does not convert the conditional envelope into a leaderboard result.

## 8. Red-team verdict

**PASS. No quantitative correction found.**

Confirmed independently:

1. exact R209 Git blob;
2. exact file SHA-256;
3. 100-row validity and field semantics;
4. pinned scorer formula/version;
5. maximum scorer discrepancy = 0;
6. exact ordering;
7. lower/high 50 sums and means;
8. witness membership;
9. 100-row mean;
10. strict conditional interpretation.

The remaining limitation is external to the arithmetic: the canonical grader public-50 identity manifest is unavailable, so the actual public-50→R209 Mini-100 join remains unproved.

## Execution accounting

- estimator/model execution: **0**
- benchmark runs: **0**
- dataset downloads: **0**
- dependency downloads/installations: **0**
- GitHub Actions: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- competition submission: **NO**
- code artifact committed: **NO**
- R325 modified: **NO**
- main/PR/control/queue edited: **NO**
- R331 branch intended diff: exactly this report + one JSON receipt
