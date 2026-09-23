# R246 — R209 V25 mini-100 score-contribution diagnostic

## Scope and immutable inputs

This is a deterministic offline diagnostic of the exposed development panel only. It reads only:

- `research/results/R209-v25-mini100.json`, Git blob `0183d0570f7c9965e00e8553ffc003c313865232`, SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.
- Its pinned source receipt `research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json` at commit `e1f6dd6a6bc351b8253e255fef424b1931b37de3`, Git blob `7fec90369227839a9902c7cceb9f3519acb66cb8`, SHA256 `5c87e8868ce3221b01979f7360079960e8991629926a7623037662f3c4511740`.
- The source receipt binds Actions run `35544406064`, V25 artifact `10617855153`, artifact ZIP SHA256 `820bf9368beac10ea537fc018c3c2185bbd310b9542603cbfa8309519c8e3e08`, and report SHA256 `68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3`.

The full 100-row diagnostic, including every name, `network_id`, `target_sha256`, MSE, FLOPs, multiplier, recorded/recomputed score, rank and aggregate share, is in `research/r246/R246_ROW_DIAGNOSTIC.json` (commit `84019700d6b0b65eb0a62c9a79c008615056f4d0`, Git blob `bc2d42b065369a14bf01aa5f8937627626fb7dbd`, SHA256 `5100b2312392c744e087404f64343fb097866fc9f90d65e662df5b3718dde244`).

No candidate result was read for this diagnostic.

## Score recomputation

Official per-network formula:

`score_i = final_mse_i * max(0.1, measured_flops_i / budget_flops_i)`.

All 100 rows have budget `2**41 = 2,199,023,255,552` FLOPs and measured FLOPs `806,303,721,965`. Therefore every row has the same cost multiplier:

`806303721965 / 2199023255552 = 0.36666448157347986`.

Results:

| Check | Result |
|---|---:|
| Rows checked | 100 |
| Failed rows | 0 |
| Recorded vs recomputed score mismatches | 0 |
| Maximum absolute score delta | 0 |
| Rows where 0.1 floor binds | 0 |
| Mean raw final-layer MSE | 2.228303490170447e-8 |
| Mean official adjusted score | 8.170397440117225e-9 |
| Total raw MSE across 100 | 2.228303490170447e-6 |
| Total adjusted score across 100 | 8.170397440117224e-7 |
| Cost multiplier | 0.36666448157347986 |
| Multiplier / 0.1 floor | 3.6666448157347986 |

The source receipt reports the same mean MSE, mean adjusted score, mean effective compute and zero failures.

## Score concentration

Networks are ranked by recomputed official adjusted score. Because the cost multiplier is identical for all 100 rows, this ranking and every contribution share are exactly the raw-MSE ranking/shares.

| Highest-score set | Share of aggregate score | Uniform-share reference | Relative to uniform |
|---|---:|---:|---:|
| Top 1 | 1.3592696639751477% | 1% | 1.3593x |
| Top 5 | 6.471417664447711% | 5% | 1.2943x |
| Top 10 | 12.47245090733508% | 10% | 1.2472x |
| Top 20 | 23.847414826413804% | 20% | 1.1924x |

The largest single contributor is row 47, `douglas-kelly`, network ID `1876000384391229791`, target SHA256 `e7e276e55667cc175301cc5a865679be7f8b6cec5cc460935d417c6f3d86f4db`: raw MSE `3.028865336318631e-8`, adjusted score `1.1105773382971547e-8`, 1.3592696639751477% of the aggregate.

The top-20 list and all remaining row identities/hashes are retained in the row diagnostic rather than using this exposed ordering to tune a candidate.

## Raw-MSE versus cost contribution

There are two distinct questions:

1. **Cross-network concentration/variation.** Measured FLOPs and the cost multiplier are constant across all 100 rows. Multiplier CV is exactly 0; MSE CV is `0.1418248455750718` and adjusted-score CV is `0.14182484557507194`. Thus all observed cross-network score concentration comes from raw-MSE variation, not cost variation.
2. **Absolute score level.** Cost still matters multiplicatively: the common multiplier `0.36666448157347986` scales the mean raw MSE `2.228303490170447e-8` to mean adjusted score `8.170397440117225e-9`. The floor is not active, so compute reductions can still reduce score if they do not induce too much MSE loss. Holding MSE fixed, reaching the 0.1 floor would multiply current score by `0.27272889801288247` (a 72.72711019871175% reduction); this is a mathematical counterfactual, not evidence that such a compute reduction is achievable.

A 10% uniform FLOP reduction, while still above the floor, would improve adjusted score whenever the accompanying MSE increase is less than `1/0.9 - 1 = 11.111111111111116%`. This threshold follows from the scoring formula and does not use individual network identities.

## Interpretation and limitations

The mini-100 aggregate is not dominated by a tiny tail: the highest 20 rows contribute about 23.85%, only moderately above their 20% uniform reference. Since cost is identical row-to-row, targeting exposed high-error network identities would be a development-set tuning strategy and is not justified by this diagnostic.

The source receipt states that raw prediction tensors were not archived. Therefore R246 can independently recompute every official adjusted score from the immutable stored per-network MSE/FLOPs/budget, but cannot independently regenerate each MSE from prediction tensors.

This panel is exposed development data. No conclusion here is a holdout, leaderboard, submission-readiness, or generalization claim.

## One preregisterable next hypothesis

**H-R246:** A single network-agnostic V25 simplification, fixed before observing an independent preregistered development panel, can reduce measured FLOPs by at least 10% while keeping mean raw-MSE degradation below 11.111111111111116%; under the official score formula this combination would lower adjusted score while remaining well above the 0.1 floor.

The experiment should test that one global tradeoff on an independent preregistered panel, with no per-network selection or tuning from the R209 mini-100 ranking.
