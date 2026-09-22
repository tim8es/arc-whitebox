# R231 V25 mini-100 error-tail and target-frontier audit

Status: COMPLETE quantitative read-only analysis
Run ID: R231-v25-error-tail-audit-20260923

## Scope and interpretation

This audit uses only the exact R226-integrated R209 V25 mini-100 normalized record.
It is descriptive. It does not run an estimator and does not infer network structure
from names or unavailable features.

The 2.1e-9 number below is used only as a cross-panel numerical orientation inherited
from the R228 public-leaderboard snapshot. It is NOT an exact-panel comparison, NOT
evidence of leaderboard position, and NOT a rank claim.

## Input integrity

Input:
- path: research/results/R209-v25-mini100.json
- SHA256: f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742
- git blob: 0183d0570f7c9965e00e8553ffc003c313865232
- normalized id: R209-v25-mini100
- panel: v2-phase2 mini:all-100
- shape: [16, 1024]
- dtype: float32
- evaluator: whestbench 0.16.1
- meter: flopscope 0.12.1+np2.4.6

Integrity checks:
- rows: 100/100
- unique names: 100
- unique network_id values: 100
- per-row target_sha256 present and unique: 100/100
- name-order SHA256: 18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce
- budget: exactly 2**41 = 2,199,023,255,552 FLOPs on every row
- measured FLOPs: exactly 806,303,721,965 on every row
- status: ok on every row
- failures: 0/100
- recomputed per-row official adjusted score vs stored value: max absolute error 0

The exact input was integrated by R226 from the R224-normalized evidence [S1].

## Raw final-layer MSE distribution

Quantiles use linear interpolation equivalent to the usual NumPy default for n=100.

| statistic | raw final MSE |
|---|---:|
| mean | 2.228303490170447e-8 |
| min / q0 | 1.4371615009167726e-8 |
| q10 | 1.7661151829884147e-8 |
| q25 | 1.981994879329818e-8 |
| median / q50 | 2.2776289299031305e-8 |
| q75 | 2.420327938068567e-8 |
| q90 | 2.610909728417710e-8 |
| q95 | 2.7616096343052732e-8 |
| q99 | 2.956936937081878e-8 |
| max / q100 | 3.028865336318631e-8 |

The median is slightly above the mean because the lower-MSE side extends farther below
the center than the upper side extends above it. No causal interpretation is attached
to this shape.

## Tail concentration

| highest-error subset | share of total raw MSE |
|---|---:|
| top 1 | 1.3592696639751474% |
| top 5 | 6.471417664447708% |
| top 10 | 12.472450907335074% |
| top 20 | 23.847414826413793% |

The nonnegative-sample Gini coefficient of per-network raw MSE is
0.07978133112646968. Both the top-k shares and this low Gini indicate weak
concentration: the total error mass is fairly diffuse across the 100 networks.

The largest single raw MSE is 3.028865336318631e-8 on network_id
1876000384391229791. The row label is only an identifier; no structural cause is
inferred from it.

## Leave-one-out sensitivity

For each network, recompute the mean raw MSE on the other 99 rows.

- full mean: 2.228303490170447e-8
- minimum leave-one-out mean: 2.2202170068760206e-8
- maximum leave-one-out mean: 2.2362948233952313e-8
- maximum absolute leave-one-out shift: 8.086483294426365e-11
- maximum relative shift vs full mean: 0.36289865047995844%

Thus no single MLP controls the mini-100 aggregate.

## Official score floor arithmetic

The official Phase-2 rule is, for a valid MLP,

    s_m = final_layer_mse_m * max(0.1, C_m / B)

with Phase-2 C_m = F_m and B = 2**41; the leaderboard metric is the suite mean [S2].

For this archived V25 record, every row has the same:
- F_m = 806,303,721,965
- C/B = 0.36666448157347986

The observed mean adjusted score recomputes to:

    8.170397440117225e-9

If raw MSE were held fixed but compute were reduced to or below the 0.1 multiplier floor,
the best score obtainable from compute reduction alone would be:

    0.1 * mean_raw_mse
    = 2.228303490170447e-9

Therefore compute-factor improvement alone cannot reach the 2.1e-9 numerical orientation
while the observed V25 raw MSE is held fixed.

At the 0.1 floor, a numerical score of 2.1e-9 requires:

    required mean raw MSE = 2.1e-9 / 0.1 = 2.1e-8

Relative to the observed V25 mean raw MSE, the minimum aggregate raw-MSE reduction is:

    absolute reduction = 1.2830349017044704e-9
    relative reduction = 5.757900157515477%

Again, this is only target arithmetic. The 2.1e-9 number came from a different official
grader panel in R228 [S3], while R209 V25 is the local mini:all-100 development panel.
It must not be interpreted as a rank or an exact competitive comparison.

The fixed-raw floor 2.228303490170447e-9 is 6.1096900081165195% above the numerical
2.1e-9 orientation.

## What would a tail-only strategy require?

Because the tail is weakly concentrated, a strategy that improved only the current
highest-error rows would need large within-subset reductions to produce the required
5.7579% aggregate raw-MSE reduction:

| subset improved, all other rows unchanged | required reduction of that subset's current raw-MSE mass |
|---|---:|
| top 1 | 423.60% - impossible even if the row were driven to zero |
| top 5 | 88.97% |
| top 10 | 46.16% |
| top 20 | 24.14% |

These are arithmetic upper-bound diagnostics, not evidence that the same networks would
remain high-error under a modified estimator. A tail-targeted successor would also need a
target-free, pre-prediction way to identify the relevant subset; this record contains no
such feature.

## Recommendation

Next effort should prioritize GLOBAL ACCURACY rather than compute factor alone or a
small high-error subset.

Evidence:
1. compute reduction can lower the multiplier from 0.36666448 to 0.1, but the resulting
   fixed-raw floor is still 2.2283e-9, above the 2.1e-9 numerical orientation;
2. at least 5.7579% aggregate raw-MSE reduction is therefore required even at the compute
   floor;
3. error mass is diffuse (top-10 only 12.47%, top-20 23.85%, Gini 0.0798);
4. leave-one-out mean sensitivity is at most 0.363%.

A measurable tail subset could still be a diagnostic lane, but this dataset alone does not
justify making it the primary optimization target.

## Limits

- All 100 networks have the same recorded shape [16,1024] and budget 2**41, so there is
  no network-size variation from which to infer a size/error relationship.
- The normalized record does not contain causal architecture features beyond identifiers
  and the fixed panel metadata. Names are not features.
- Raw prediction tensors are not archived, so no neuron-level, layer-residual, sign,
  calibration, or error-direction decomposition is possible.
- This analysis describes one local public mini-100 panel. It does not establish behavior
  on the official grader public-50 or sealed private panel.

## Reproducible artifacts

- script: research/r231/r231_v25_error_tail.py
  SHA256 11b857b41b7722bd5aeb9dcfd0ca48457ded9fd33f91002f9cfe4a23636ba6b0
- per-network table: research/r231/R231_V25_ERROR_TAIL_TABLE.csv
  SHA256 d2659587b31100ba96de54cc2011d06bffaac5f0f57c7850c293865c1247f157

The script verifies the input and name-order hashes, recomputes the official score formula,
prints the summary, and can reproduce the CSV table. It performs arithmetic only.

## Sources

[S1] Exact R226-integrated V25 normalized record:
https://github.com/tim8es/arc-whitebox/blob/20fafab5471e6ed227562c651179dd2ef331ea22/research/results/R209-v25-mini100.json

[S2] Official AIcrowd starter-kit score-report reference, Phase-2 budget-adjusted scoring:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/score-report-fields.md

[S3] R228 official leaderboard/rankability audit, source of the 2.1e-9 snapshot orientation
and the warning that R209 mini-100 is not an exact leaderboard panel:
https://github.com/tim8es/arc-whitebox/blob/2a1924e9d266000f4e9fcdde5979b789dfad8340/research/R228_OFFICIAL_LEADERBOARD_AUDIT.md

[S4] Official AIcrowd starter-kit overview for Phase-2 shape/budget and the 0.1 floor:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/README.md

## Constraints confirmed

No estimator run. No paid compute. No private/holdout data. No submission. No canonical
estimator/result edit. No structural-causality claim from unknown features. No rank claim.
