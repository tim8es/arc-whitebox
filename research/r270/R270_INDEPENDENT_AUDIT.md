# R270 - Independent audit of R266 score-gap arithmetic

Checked at: 2026-09-23T12:24:14.770Z
Owner: `score-gap-independent-audit`
Branch: `research/r270-score-gap-independent-audit-20260923`
Protocol commit: `385756cddca324a96acd6a50d0f7294ed8e825e7`
Independent calculation commit: `f84dc295705790fb14539ef0f627cc1b56c6b899`

## Decision

**R266 arithmetic is independently verified. Strict competition comparison remains NOT_COMPARABLE.**

No official rank or exact leader gap is inferred. R209 V25 is the public development `mini:all-100` panel, while the current online evaluation exposes 50 public MLPs and keeps the other 50 sealed for the final full-100 evaluation. The metric and aggregation rule match, but the evaluated panel does not.

## Immutable inputs

- R209 V25 normalized result Git blob SHA1: `0183d0570f7c9965e00e8553ffc003c313865232`
- R209 V29 normalized result Git blob SHA1: `1c5d779ef7d6b0d85963c1db7bc4e91887a7086c`
- R266 report Git blob SHA1: `0c0c193244738b4adf4c6369589e8bdcaa28d5ef`
- R266 calculations Git blob SHA1: `8b5ee19cd40ade790a82e5d7e0f1a7ba94ef89da`
- R266 receipt Git blob SHA1: `28d721653959746502fd5cb104045ef05f876e30`
- R266 receipt SHA256 recorded by control: `795bb53fabc907f367a98aaf605bc7304a916eced234e854d16dd1fa552a604c`
- Official Phase-2 scoring source Git blob SHA1: `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`

Official scoring source:
https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md

The official rule is:
`adjusted_final_layer_score = mean_m(final_mse_m * max(0.1, C_m/B))`,
with `B = 2**41`, Phase-2 `C_m = F_m`, and failed MLPs forced to multiplier 1.0.

## V25 row-level recomputation

The 100 immutable R209 V25 rows contain zero failures and a single measured FLOP value for every row:

- measured FLOPs per row: `806,303,721,965`
- budget: `2,199,023,255,552`
- exact cost factor: `0.36666448157347986125387251377105712890625`
- mean raw final-layer MSE: `2.228303490170447e-8`
- recomputed mean adjusted score: `8.170397440117225e-9`
- mean of recorded per-row official adjusted scores: `8.170397440117225e-9`
- maximum per-row disagreement between recomputed formula and stored official score: `0`

This confirms R266's mean score and current cost factor exactly to the precision represented by the immutable rows.

## Conditional sensitivity to displayed 2.1e-9

This section is algebra against a displayed threshold only. It is **not** an official gap or rank.

Using `2.1e-9` literally:

- uniform MSE scale at unchanged V25 cost: `0.2570254403646085291...`
- required raw-MSE reduction at unchanged cost: **74.29745596353915%**
- cost-only factor required with unchanged MSE: `0.09424209984248452477...`
- that factor is below the official `0.1` floor, so cost-only matching is impossible
- score at the 0.1 floor with unchanged V25 MSE: `2.228303490170447e-9`
- additional raw-MSE reduction still required at the floor: **5.757900157515475%**
- largest integer FLOP count still at the floor: `219,902,325,555`

The arithmetic difference `6.070397440117225e-9` and ratio `3.890665447674869...` are only display-threshold sensitivities.

## Rounding audit

The official leaderboard renders the leader's Adjusted Score as `0.0000000021` with ten digits after the decimal point. The underlying unrounded score and the UI's exact rounding/truncation implementation are not exposed.

Therefore R266 was correct to call `2.1e-9` a rounded/displayed value and not an exact target. No exact hidden interval is asserted.

For sensitivity only, if the UI used conventional nearest rounding to a `1e-10` display quantum, the hidden value would lie in `[2.05e-9, 2.15e-9)`. Under that assumption, the same-cost raw-MSE reduction would range from about **73.68549% to 74.90942%**, and the floor residual MSE reduction from about **3.51404% to 8.00176%**. This is illustrative only, not a claim about the renderer.

Official leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

## V29 failure treatment

Independent recomputation of the immutable R209 V29 rows confirms:

- 100 rows total
- 43 successful rows
- 57 failed rows
- every failure is `residual_wall_time_exhausted`
- every failed row's recorded adjusted score equals its raw final-layer MSE, consistent with multiplier 1.0
- recomputed mean adjusted score: `0.5270942878803214`
- failure rows contribute `0.5270942854881286` to the overall 100-row mean
- successful rows contribute only `2.392192892427515e-9`

R266 therefore correctly states that V29's failures dominate its score and that reducing successful-row FLOPs cannot be treated as a cost-only path while those failures persist.

## Comparability

Official/current submission detail pages state that visible scores are calculated over 50 public MLPs and the other 50 are sealed; the full 100-MLP test-set result is reserved for final evaluation. R209 is a different public development `mini:all-100` panel.

Representative official Phase-2 submission page:
https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

Thus:

- metric: MATCH
- aggregation: MATCH
- panel/split: MISMATCH
- exact official gap: UNKNOWN / NOT_COMPARABLE
- competition rank/place: NOT CLAIMED

## Audit conclusion

No substantive arithmetic or scoring-semantics error was found in R266. Its conditional percentages are correct when interpreted exactly as stated: sensitivity to the displayed `2.1e-9`, not a same-panel competition gap.

No estimator, benchmark, GitHub Actions workflow, competition dataset fetch, private/holdout/full evaluation, paid resource, submission, leaderboard mutation, model edit, or canonical-result edit was performed.
