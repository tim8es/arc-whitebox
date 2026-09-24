# R303 — Official Phase-2 leaderboard refresh

## Snapshot

Retrieved from the live AIcrowd Phase-2 leaderboard at **2026-09-24T02:07:55.431Z**. Endpoint: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2. The page showed rows 1–100 of 195; the receipt preserves all 100 visible rows and the exact displayed strings.[1]

The current visible leader was team **J2W**, displayed rank **01**. Its Adjusted Score was **2.10e−9**, rendered to three significant digits; Final Layer MSE was **1.64e−8**, the approximate sampling comparison was **539×**, and the entry count was **320**. The page did not expose an unrounded score, so the underlying exact value is **UNKNOWN**.[1]

The Phase-2 submission deadline is **2026-10-17 23:59 UTC**.[2] The challenge overview says the estimator is scored against a high-budget Monte Carlo reference and points to the official rules for binding terms.[3] The AIcrowd challenge-rules page itself returned only its heading in this retrieval, with no rule text; the deadline and metric below are therefore sourced to the Phase-2 announcement and AIcrowd’s official starter-kit documentation.[2][4][5][6]

## Official metric

The ranking metric is adjusted_final_layer_score, lower is better. For each MLP, final-layer MSE is multiplied by max(0.1, F_m/B), with B = 2^41 = 2,199,023,255,552 FLOPs, then averaged across MLPs. In Phase 2, C_m = F_m; the residual-time allowance is a separate cap, not a score discount. A cap failure uses multiplier 1.0. Raw final_layer_mse is diagnostic; it is not the leaderboard ranking metric.[4][5]

## Comparability with project results

**Verdict: NOT_COMPARABLE. No score gap or rank was computed.**

The current displayed leader is 2.10e−9. R209 V25 is 8.170397440117225e−9 on public development mini:all-100; R223 V25 is 8.1711165e−9 on mini-100. These values are context only: neither receipt demonstrates identity with the current visible public-50 evaluation panel.[7][8][10]

R271 found zero stable-identity overlap between the 50 MLPs represented by the current visible panel and R209, exposed no public network IDs, and did not prove an exact panel match. It also found that evaluator and meter versions were not an exact match. R263 and R266 independently recorded NOT_COMPARABLE because mini:all-100 does not match the online visible-50 split; R266’s conditional arithmetic against a rounded display is explicitly not an official gap or rank.[7][8][9]

The missing evidence is an immutable visible-50 manifest mapping each public mlp_index/mlp_name to network_id (preferably target_sha256), together with the grader evaluator and meter versions. For an existing R209 comparison, those identities must occur in R209; otherwise an immutable per-MLP V25 result artifact for the exact visible 50 is needed. The compared per-network results must use the same panel, scoring definition, and compatible evaluator/meter versions.[8]

R263 recorded the leader’s display as 0.0000000021 with 312 entries; this snapshot shows 2.10e−9 with 320 entries. The displayed score is consistent at R263’s lower precision, but rounded displays do not establish an exact underlying score or a project-to-leader gap.[1][7]

The 100 leaderboard participant rows are not the 50-MLP evaluation panel. They are separate counts.[1][8]

## Checks and limits

- Confirmed live Phase-2 endpoint, capture time, displayed leader, score precision, page row count, deadline, and scoring rule from first-party AIcrowd sources.[1][2][4][5]
- Confirmed the already-published R303 claim/start at control revision 474, run_id R303-official-leaderboard-refresh-20260924, and code_commit 4619801e0cc5e7e340cd0406eb44e0633d8aa5e5. No second claim or start was created.[10]
- No Actions, estimator/benchmark, data or dependency download, paid resource, private/holdout/full-data access, competition submission, leaderboard edit, canonical-results edit, PR #36 edit, or contact was performed.
- The exact unrounded leader score and exact visible-50 identity join remain UNKNOWN; comparison remains NOT_COMPARABLE.

## Sources

[1] [AIcrowd Phase-2 leaderboard](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2)  
[2] [AIcrowd Phase-2 launch announcement](https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197)  
[3] [AIcrowd challenge overview](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026)  
[4] [AIcrowd starter kit — scoring model, commit 5eb9aa1455fcb3216af55994bdf25dc242b95797](https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/scoring-model.md)  
[5] [AIcrowd starter kit — competition rounds, commit 5eb9aa1455fcb3216af55994bdf25dc242b95797](https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/rounds.md)  
[6] [AIcrowd challenge rules page](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules)  
[7] [R263 receipt](https://github.com/tim8es/arc-whitebox/blob/6a6b0b0ed53b69a1822b3b281a93a120ff153b3e/research/r263/R263_RECEIPT.json)  
[8] [R271 receipt](https://github.com/tim8es/arc-whitebox/blob/772f010042a818ba641b64be58db55a78344217f/research/r271/R271_RECEIPT.json)  
[9] [R266 receipt](https://github.com/tim8es/arc-whitebox/blob/94afd42db902d7dcaa7b6aa4f9a142d04120e971/research/r266/R266_RECEIPT.json)  
[10] [R303 control state, revision 474](https://github.com/tim8es/arc-whitebox/blob/e1dac28c1bfeacb4ec33d997238bb0c6be73b632/research/control/state.json)
