# R273 - R209 V25 error concentration audit

## Scope

Independent descriptive audit of the immutable `research/results/R209-v25-mini100.json` only, against the official Phase-2 formula:

`score_m = final_mse_m * max(0.1, measured_flops_m / budget_flops_m)`.

Source pins:
- R209 V25 normalized Git blob SHA1: `0183d0570f7c9965e00e8553ffc003c313865232`
- Official scoring-model Git blob SHA1: `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`
- Panel: public development `mini:all-100`; evaluator `whestbench 0.16.1`; meter `flopscope 0.12.1+np2.4.6`.

No leaderboard comparison or rank is made.

## Row verification

All **100/100** rows reproduce the stored `official_adjusted_score` exactly under the official formula; maximum absolute disagreement is `0`. There are **0 failures**.

Every row has the same measured FLOPs, `806,303,721,965`, and the same budget, `2,199,023,255,552`, so every row has the same compute multiplier:

`0.36666448157347986125387251377105712890625`.

## Distribution

Statistics use sample SD across networks, `SE = SD / sqrt(100)`, and Hyndman-Fan type-7 quantiles.

| Statistic | Adjusted score | Final-layer MSE |
|---|---:|---:|
| Mean | 8.170397440117225e-9 | 2.228303490170447e-8 |
| SD | 1.1587653552315885e-9 | 3.160287983878172e-9 |
| SE | 1.1587653552315885e-10 | 3.160287983878172e-10 |
| Min | 5.269560766710126e-9 | 1.4371615009167726e-8 |
| p05 | 6.385327324593524e-9 | 1.7414632846879385e-8 |
| p10 | 6.475717079694986e-9 | 1.7661151829884147e-8 |
| p25 | 7.267271249107595e-9 | 1.981994879329818e-8 |
| p50 | 8.351256307996911e-9 | 2.2776289299031305e-8 |
| p75 | 8.874482886497207e-9 | 2.420327938068567e-8 |
| p90 | 9.573278620054346e-9 | 2.6109097284177096e-8 |
| p95 | 1.0125841648708702e-8 | 2.7616096343052732e-8 |
| Max | 1.1105773382971547e-8 | 3.028865336318631e-8 |

Both coefficient-of-variation values are `0.141824845575...`, as expected from a constant score multiplier.

## Concentration

Sorted by descending adjusted score:

- worst 1 network: **1.3593%** of total score;
- worst 5 networks: **6.4714%**;
- worst 10 networks: **12.4725%**;
- worst 25 networks: **29.3131%**;
- remaining 90 networks still contribute **87.5275%**;
- remaining 75 networks still contribute **70.6869%**.

For context, equal contribution would assign 10% of total score to 10% of networks and 25% to 25%. The observed top-tail concentration is only about `1.247x` and `1.173x` those equal-share baselines. The largest single row contributes only `1.36%`.

As a descriptive trimmed-mean diagnostic, removing the worst 10 and recomputing the mean over the remaining 90 lowers the mean by only **2.75%**; removing the worst 25 lowers the recomputed mean by only **5.75%**. These are concentration diagnostics, not competition metrics.

## Cost variation versus MSE variation

There is **no across-network cost variation** in this record: one FLOP count, one budget, one multiplier. Therefore

`adjusted_score_i = 0.36666448157347986... * MSE_i`

for every network.

The compute multiplier has sample SD `0`. The score/MSE correlation is numerically `~1.0`, and `Var(score) = factor^2 * Var(MSE)` to floating-point precision. Thus **0% of the cross-network score dispersion is attributable to cost-factor variation; all observed dispersion comes from MSE variation.**

## Conclusion for global research

The development-panel error burden is **broad-based, not outlier-dominated**. A few high-error networks do not control the mean: the worst 10% account for only 12.47% of total score, while 87.53% comes from the other 90%.

For global research with no per-network selection, this favors mechanisms expected to lower MSE across the central bulk of networks, not special-case fixes for a small tail. Candidate evaluation should therefore require movement in central quantiles as well as the mean and should still monitor the upper tail for regressions, using one fixed global method/configuration.

This is descriptive public-development evidence only. It does not establish held-out performance, a leaderboard gap, or a competition rank.
