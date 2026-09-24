# R343 — independent arithmetic/source red-team for the proposed R342 addendum

**Status:** COMPLETE  
**Verdict:** **PASS — arithmetic/source claims independently reproduced**  
**Mode:** report-only arithmetic/source verification; no leaderboard re-audit and no benchmark  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r343-r333-2e9-arithmetic-red-team-20260924`

## Scope

R343 independently verifies the arithmetic that would support the proposed R342 addendum.

R343 uses only:

1. the committed immutable R209 V25 per-network artifact;
2. the pinned Phase-2 WhestBench scoring formula/version;
3. the already preserved public leaderboard display value **`2.00e-9`**, supplied for the snapshot at **2026-09-24 11:28 UTC** and preserved in the R340/R341 sidecar evidence.

R343 does **not** browse the leaderboard, open submission pages, rerun an estimator, run a benchmark, download a dataset/dependency, invoke Actions, or inspect private/holdout/full data.

The proposed R342 addendum itself is not used as an input source; this is an independent source/arithmetic check.

## 1. Immutable R209 source

Authoritative normalized artifact:

`research/results/R209-v25-mini100.json`

Integration ref:
`20fafab5471e6ed227562c651179dd2ef331ea22`

Verified Git blob:

`0183d0570f7c9965e00e8553ffc003c313865232`

Expected recorded SHA-256:

`f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`

R343 independently recomputed SHA-256 over the fetched UTF-8 JSON bytes:

`f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`

**Hash match: PASS.**

Row/source checks:

- `per_network` rows: **100**
- unique `network_id`: **100**
- serialized `final_mse` values: **100**
- all rows `status="ok"`: **YES**
- failure rows: **0**
- panel: `v2-phase2 mini:all-100`
- stage: `development`
- evaluator recorded by artifact: `whestbench 0.16.1`

## 2. Pinned Phase-2 scorer source

Pinned WhestBench version:

`0.16.1`

Exact source commit:

`4d08668b485c8a7d25a105c3c00d2f4fc2538f18`

Verified source blobs:

- `src/whestbench/scoring.py`: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- `src/whestbench/budget.py`: `6586f12d178e0136420cb282535663f1faad5abc`
- `docs/reference/rounds.md`: `c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890`

For a valid row:

[
s_m = mathrm{MSE}_{m,mathrm{final}}
      max(0.1, C_m/B_m).
]

Failures use multiplier 1.0.

For Phase 2, residual mode is gated rather than priced, so the residual rate is zero and

[
C_m=F_m.
]

All 100 R209 rows are valid. Their common recorded values are:

- (B_m=2^{41}=2{,}199{,}023{,}255{,}552);
- (F_m=806{,}303{,}721{,}965);
- (F_m/B_m=0.36666448157347986).

Independent rowwise recomputation under the pinned formula gives maximum absolute discrepancy from stored `official_adjusted_score`:

**0** in binary floating-point arithmetic.

## 3. Exact-decimal mean raw MSE

R343 does not use the rounded binary-float aggregate for the core arithmetic. It parses the 100 serialized `final_mse` decimal lexemes and sums them as exact base-10 integers.

Exact sum of 100 serialized raw final-layer MSE values:

[
0.00000222830349017044681.
]

Exact-decimal mean:

[
oxed{
ar M
=
0.0000000222830349017044681
=
2.22830349017044681	imes10^{-8}
}
]

This is the R343 authoritative arithmetic input.

R333 recorded the same quantity as the binary-float-rounded
`2.228303490170447e-8`; R343 does not revise that historical receipt.

## 4. Fixed-MSE compute floor

At fixed per-row raw MSE, compute-only improvement can lower each valid row's multiplier no further than the scorer floor (0.1).

Therefore the aggregate floor is exactly

[
0.1,ar M
=
oxed{
2.22830349017044681	imes10^{-9}
}.
]

This is a counterfactual **fixed-MSE scorer floor**, not a measured leaderboard result.

The observed R209 compute multiplier is currently about (0.36666448), but reducing compute below the (0.1B) threshold cannot lower the score multiplier below (0.1).

## 5. Conditional arithmetic for the saved `2.00e-9` display

Saved snapshot input:

- displayed public leaderboard value: **`2.00e-9`**
- supplied snapshot time: **2026-09-24 11:28 UTC**
- exact underlying leaderboard float: **UNKNOWN**
- formatter/rounding interval: **UNKNOWN**

The value is independently preserved in committed R340/R341 evidence:

- R340 report blob: `7ac3772f87b59e1da0a3b309a1f171c1ded64190`
- R340 receipt blob: `bca09edfeb7ec0efa792f7b2c4b3abebb7d2e3fb`
- R341 report blob: `89b6822324f19187683d448bdfef1116be0896fe`
- R341 receipt blob: `2e088a7b6e95cc8f47ecc87431930cd5f8ec14b4`

R341 explicitly keeps the exact unrounded score change `UNKNOWN` and does not compute a score gap.

R343 treats `2.00e-9` only as the saved **displayed text**.

### Same-panel/same-scorer counterfactual only

Under the explicit assumption that one were comparing the same panel under the same scorer, and using (0.1) as the multiplier floor, equality to the displayed text numerically would require

[
0.1,ar M_{	ext{target}}=2.00	imes10^{-9}.
]

Hence

[
oxed{
ar M_{	ext{target}}
=
2.00	imes10^{-8}
}.
]

Required absolute raw-MSE reduction from committed R209:

[
Delta M
=
2.22830349017044681	imes10^{-8}
-
2.00	imes10^{-8}
]

[
oxed{
Delta M
=
2.2830349017044681	imes10^{-9}
}.
]

Required relative reduction:

[
rac{Delta M}{ar M}
=
0.102456191976337782836253435762ldots
]

or

[
oxed{
10.245619197633778% 	ext{approximately}
}.
]

Again, this is a **conditional arithmetic target against displayed text**, not a measured competition gap.

## 6. Can compute-only reach displayed `2.00e-9` at fixed observed MSE?

No, under the same-panel/same-scorer fixed-MSE counterfactual.

The minimum score obtainable by changing compute alone is

[
2.22830349017044681	imes10^{-9},
]

which is numerically above the saved displayed text (2.00	imes10^{-9}) by

[
oxed{
2.2830349017044681	imes10^{-10}
}.
]

Thus:

**COMPUTE_ONLY_INSUFFICIENT_AT_FIXED_OBSERVED_MSE for the numerical `2.00e-9` display target.**

This statement does not imply that the displayed leaderboard score is directly comparable to R209.

## 7. R333 historical `2.10e-9` snapshot is preserved

R333 remains the earlier-snapshot analysis and is not overwritten.

Exact R333 branch/head:

- branch: `review/r333-r209-compute-floor-headroom-20260924`
- head: `b089c3e24f7ea5499b66f09da27a2be3f9b5d3de`
- report blob: `5e2b58a80a647b9f0a8dcc3355a65d8e5a01e4f5`
- receipt blob: `3718a7ce748a57db36f08fbd64fd55cabd51c801`

R333's recorded earlier displayed target was `2.10e-9`, with:

- required raw-MSE mean at floor: `2.10e-8`;
- recorded absolute reduction: `1.2830349017044704e-9`;
- recorded relative reduction: `0.05757900157515477` ≈ **5.7579001575%**.

Those values remain historical evidence for that earlier display snapshot.

R343 does not retroactively replace the R333 snapshot with `2.00e-9`.

## 8. Comparability boundary remains unchanged

The public leaderboard uses the grader public-50 panel, while R209 is the committed 100-row development Mini-100 panel.

Existing immutable identity audits remain:

- R319: `NOT_JOINABLE`
  - receipt blob `517c4ea88041432c6929c561b18b42a01be94761`
  - canonical public `network_id` coverage: `0/50`
- R322: `EXISTS_BUT_NOT_PUBLICLY_EXPOSED`
  - receipt blob `2625914219065bec11891317e4ea978ed9cb4308`
  - exact deployed Phase-2 public-50 canonical seed/ID mapping not public

Therefore the leaderboard↔R209 identity bridge remains:

**NOT_COMPARABLE / NOT_JOINABLE.**

R343 does not claim:

- a true contest score gap;
- an exact leaderboard float;
- an actual R209 public-50 score;
- a predicted rank/place;
- that the public-50 is a subset of R209 Mini-100;
- that the conditional raw-MSE target is achievable.

## 9. Red-team verdict

**PASS.**

Independently confirmed:

1. R209 exact Git blob and SHA-256;
2. 100 valid per-network rows;
3. pinned Phase-2 formula and (0.1) multiplier floor;
4. exact-decimal mean raw MSE `2.22830349017044681e-8`;
5. fixed-MSE floor `2.22830349017044681e-9`;
6. conditional target raw mean for displayed `2.00e-9`: `2.00e-8`;
7. absolute reduction: `2.2830349017044681e-9`;
8. relative reduction: approximately `10.245619197633778%`;
9. compute-only at fixed observed MSE cannot numerically reach the displayed `2.00e-9`;
10. R333's earlier `2.10e-9` snapshot remains separate and preserved;
11. public-50↔R209 remains `NOT_COMPARABLE / NOT_JOINABLE`.

## Execution accounting

- live leaderboard browsing: **0**
- submission pages opened: **0**
- estimator/model runs: **0**
- benchmark runs: **0**
- code artifacts committed: **0**
- dataset/dependency downloads: **0**
- GitHub Actions: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- competition submissions: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- intended R343 branch diff: exactly this report + one JSON receipt
