# R266 — score-gap and cost/MSE sensitivity analysis

## Decision

**Strict official comparison: NOT_COMPARABLE.** R263 (completed at control revision 302) verified that the official Phase-2 metric and mean-over-MLP aggregation rule match R209, but the evaluated split does not. R209 V25 is the public development `mini:all-100` panel; current visible online Phase-2 scoring uses 50 public MLPs, with 50 additional MLPs sealed for the final full-100 evaluation.

Therefore the exact official leader gap is **UNKNOWN**, and no competition rank/place is calculated or implied. The visible `2.1e-9` value is also rounded, so it is not an exact unrounded target.

## Frozen evidence

- R263 receipt: `d799a5e2fe54024eb0f39bfc9e256173d2660467f2928b17ec379a2362db9c73`; snapshot SHA256 `6cbb8ce69ad4330cc624e78209a49a1b333e3845daf8def1fd2a462d6ff49646`.
- R209 V25 normalized blob: `0183d0570f7c9965e00e8553ffc003c313865232`.
- R209 V29 normalized blob: `1c5d779ef7d6b0d85963c1db7bc4e91887a7086c`.
- R223 V25-local-feed normalized blob: `c8b617c43ff1145977c38e7e1cca6d23985ec392`.
- All three normalized records use the same public development `mini:all-100` panel metadata, so comparisons among those records are valid.

R209 V25 has 100/100 successful rows, mean raw final-layer MSE `2.228303490170447e-8`, measured FLOPs `806,303,721,965` per row, cost factor `0.3666644815734798613`, and mean adjusted score `8.170397440117225e-9`. R223 has 0 failures but is slightly worse at `8.171116513490032e-9` (+0.00880096%). R209 V29 has 57 failures and mean adjusted score `0.5270942878803214`; those failures dominate the result.

## Official score algebra

For a successful MLP:

`score_m = final_mse_m * max(0.1, measured_flops_m / B)`, with `B = 2**41 = 2,199,023,255,552`.

For a failed MLP the multiplier is forced to `1.0`. The reported competition metric is the mean of these per-MLP scores.

This means cheaper compute helps only until `measured_flops/B = 0.1`; below that floor, only lower MSE can improve score. For integer measured FLOPs, the largest value still fully clamped to the 0.1 floor is `219,902,325,555`.

## Conditional sensitivity to the displayed 2.1e-9 value

The following is **not an official gap**. It answers only: if the rounded visible `2.1e-9` were used as an algebraic threshold on the R209 mini-100 panel, what MSE/cost trade-off would be required?

At the current V25 cost factor, unchanged cost requires a uniform raw-MSE scale of about `0.25702544`: a **74.29745596% raw-MSE reduction**.

Cost reduction alone cannot reach that display threshold. With unchanged V25 MSE it would require cost factor `0.09424209984`, below the official `0.1` floor. At the floor, unchanged-MSE score would still be `2.228303490170447e-9`, so an additional **5.75790016% raw-MSE reduction** is still required.

| Cost factor | Nominal measured FLOPs | FLOP reduction vs V25 | Score if MSE unchanged | Additional raw-MSE reduction to 2.1e-9 |
|---:|---:|---:|---:|---:|
| 0.36666448 (current) | 806,303,721,965 | 0% | 8.1703974401e-9 | 74.29745596% |
| 0.30 | 659,706,976,665.6 | 18.18133060% | 6.6849104705e-9 | 68.58596672% |
| 0.25 | 549,755,813,888.0 | 31.81777550% | 5.5707587254e-9 | 62.30316006% |
| 0.20 | 439,804,651,110.4 | 45.45422040% | 4.4566069803e-9 | 52.87895008% |
| 0.15 | 329,853,488,332.8 | 59.09066530% | 3.3424552353e-9 | 37.17193344% |
| 0.10 (floor) | 219,902,325,555.2 nominal | 72.72711020% | 2.2283034902e-9 | 5.75790016% |

The arithmetic difference `8.170397440117225e-9 - 2.1e-9 = 6.070397440117225e-9` and ratio `3.8906654477×` are retained only as display-threshold sensitivity. They are **not** called an official leader gap because the split/panel is different.

## Failure semantics

All cost/MSE scenarios above assume failures remain zero. A failed row loses the compute discount entirely; therefore a cheaper estimator that begins failing can become much worse even if successful rows are inexpensive.

R209 V29 is the concrete existing example: 57/100 rows failed. Failure rows contribute `0.5270942854881286` to the overall mean adjusted score, while the 43 successful rows contribute only `2.392192892427515e-9`. Thus its cheaper successful-row FLOPs do not establish a useful cost-only path.

## Reproducibility and limits

`R266_CALCULATIONS.json` stores immutable input blob IDs, all row-level fields used, formulas, derived summaries, conditional scenarios, and explicit limitations. No estimator/benchmark rerun, GitHub Actions, new dataset access, paid/private/holdout/full data, submission, model edit, leaderboard edit, or canonical-result mutation was performed.
