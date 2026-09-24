# R320 — sidecar research traceability audit

**Status:** COMPLETE — corrected by R323; extended by R332/R334/R336  
**Mode:** report-only traceability audit  
**Branch:** `review/r320-sidecar-research-traceability-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**R323 correction parent:** `ae418aa7bcdb08549b051745816bce16aafe1e7e`  
**R332 extension parent:** `0c4db1d79deb9b2f608001127d8359b0c0fafd27`  
**R334 extension parent:** `1c285e5d504d6eb3c971d5afae9db3188e0dcea0`  
**R336 extension parent:** `2a524361d1b39ef3066f97cc2d986f1596f58920`

## R323 correction notice

The original R320 report/receipt contained three confirmed traceability errors:

- R313 was incorrectly recorded as an artifact gap;
- R317 was incorrectly recorded as IN_PROGRESS;
- R319 was incorrectly recorded as PENDING.

This corrected version supersedes those statements everywhere below.

The supplied conversation-thread identifiers for R313/R317/R319 are not directly dereferenceable through the repository interface available in this session. Their stated terminal outputs were therefore cross-checked against exact GitHub branch history, heads, reports and receipts. The GitHub evidence matches the requested corrections.

## Scope

R320 reconciles the formal `research/control-v2` state with report-only sidecar work R306–R319.

No estimator was run by R320/R323, no benchmark or Actions job was started, no dataset/dependency was downloaded, and no main/PR/control/queue/submission/private/holdout/full-data mutation occurred.

Evidence used:

- formal branch `research/control-v2`;
- `research/control/state.json` at revision **479**, blob `1c594d83fe0564e3fffac0188fd9c4c48413434c`;
- formal control head `089532101b2d1bb767c9eb57dd5c781dbe852b33`;
- exact sidecar refs/heads and exact report/receipt files listed below;
- exact branch comparisons against base `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`.

The formal state contains **no R306–R319 sidecar jobs/events**. That absence must not be confused with absence of sidecar artifacts.

No separate pre-existing sidecar registry was found. The table therefore follows the existing control queue style while remaining a report-only traceability index, not a synthetic control record.

## Corrected sidecar traceability table

| Task | Type | Verdict / state | Exact branch / head | Artifacts confirmed | Reflected in formal control-v2? |
|---|---|---|---|---|---|
| R306 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r306-j2w-method-audit-20260924` / `6519194e8f570b4b519bd97a1f574b33a86033f2` | **YES** — report + receipt | **NO** |
| R307 | leaderboard forensic | `PARTIAL_PUBLIC_EVIDENCE` | `review/r307-andreas-update-audit-20260924` / `0962a1bd9230253bc37132961043459687aa6c79` | **YES** — report + receipt | **NO** |
| R308 | theory | `NO_GO_AFTER_DEDUPLICATION` | `review/r308-theory-scout-20260924` / `9c3ef5eefe014e7bdb1a11cc8941999048f6654b` | **YES** — report + receipt | **NO** |
| R309 | comparability | `COMPLETE` source/toolchain audit, with R313 correction incorporated | `review/r309-toolchain-delta-audit-20260924` / `1e23a25550369da60b976416fe0f502a6189b833` | **YES** — corrected report + receipt | **NO** |
| R310 | leaderboard forensic | `COMPLETE` public leaderboard snapshot/delta | `review/r310-leaderboard-top-check-20260924` / `80d55d7150e7907bd96f99a78a0b88cd4cdd6f5c` | **YES** — report + receipt | **NO** |
| R311 | comparability | `NOT_COMPARABLE` | `review/r311-leaderboard-score-comparability-20260924` / `af16cdf782e97e4a7a1753f1516635191493f0d1` | **YES** — report + receipt | **NO** |
| R312 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r312-luna-public-method-audit-20260924` / `4af4a8bda987abb99ea4a2f5b85c8d7c7ac46321` | **YES** — report + receipt | **NO** |
| R313 | comparability correction | **COMPLETE** — R223 attempt 6 evidence corrected | **same R309 branch** `review/r309-toolchain-delta-audit-20260924` / `1e23a25550369da60b976416fe0f502a6189b833` | **YES** — correction is preserved in R309 report blob `d26f0174b32ffa647a0454bb24be038cdf0e14c1` and receipt blob `2eb00990f3e1e8465ca48e918718033c0ecbd395`; no separate R313 files | **NO R313 event**; underlying R223 finish exists at revision 193 |
| R314 | comparability | `NOT_COMPARABLE` | `review/r314-r311-comparability-independent-audit-20260924` / `3c350f49176fc3bfff259f88288b353517946bc1` | **YES** — report + receipt | **NO** |
| R315 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r315-top2-top3-config-audit-20260924` / `aa5806c4c6b1bee41acf6ad6785aa53aac363120` | **YES** — report + receipt | **NO** |
| R316 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r316-a-s6-public-method-audit-20260924` / `aee8e4fd50efbbfb248f9c4586a9e3df37f6d965` | **YES** — report + receipt | **NO** |
| R317 | theory | `EVIDENCE_BASED_NO_GO_BEFORE_IMPLEMENTATION` — R324 caveat incorporated, core NO_GO unchanged | `review/r317-truncated-normal-gate-estimator-20260924` / `6ede298753b7ebc35765e18479775879769712ff` | **YES** — corrected report blob `b134ccb1c77c3d0e70fe70b64b651e6e5dd1f77c` + receipt blob `81f6adbc9cc64ab5ad3f4aaf230fe035fffa5ea5` | **NO** |
| R318 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r318-top6-public-config-audit-20260924` / `d0138a3fe772c712d331f5fde0c7e75be5bb56b7` | **YES** — report + receipt | **NO** |
| R319 | comparability | `NOT_JOINABLE` | `review/r319-public50-r209-join-audit-20260924` / `9086b846cc6e11ad91117870c3015d25bfc5504a` | **YES** — report blob `c858a8f3bd29f50c5188894aeaaa73e2208a374f` + receipt blob `517c4ea88041432c6929c561b18b42a01be94761` | **NO** |

R321 onward began after the original R320/R323 audit window. R332 imports only immutable terminal evidence verified below; R324 and R330 are represented as corrections on their parent sidecar branches rather than standalone studies.

## R332 extension snapshot — R321–R329 plus terminal R331

R332 is a traceability-only extension. It does not reinterpret these sidecars as control-v2 jobs and does not create scientific measurements.

| Task | Type | Verdict / classification | Exact branch / head | Immutable two-file evidence | Actual new estimator measurement? |
|---|---|---|---|---|---|
| R321 | theory / independent red-team | `COMPLETE`; `EVIDENCE_BASED_INDEPENDENT_NO_GO_R317_CORE_NOT_FALSIFIED` | `review/r321-r317-compression-red-team-20260924` / `774aac4105bfe1a171f40f7272fc4267aae6c2f8` | report `research/r321/R321_R317_COMPRESSION_RED_TEAM_REPORT.md`, blob `b0b71f4d74596c4744d0353d1654ac5726aeb2bb`, https://github.com/tim8es/arc-whitebox/blob/774aac4105bfe1a171f40f7272fc4267aae6c2f8/research/r321/R321_R317_COMPRESSION_RED_TEAM_REPORT.md ; receipt `research/r321/R321_RECEIPT.json`, blob `2c3d9f881d669ee924cecca106611c6c295a7243`, https://github.com/tim8es/arc-whitebox/blob/774aac4105bfe1a171f40f7272fc4267aae6c2f8/research/r321/R321_RECEIPT.json | **NO** |
| R322 | official-source audit | `COMPLETE / EXISTS_BUT_NOT_PUBLICLY_EXPOSED` | `review/r322-public50-manifest-source-audit-20260924` / `552010f48d67d70b6bb8aae84fe4fc271ccf3f81` | report `research/r322/R322_PUBLIC50_MANIFEST_SOURCE_AUDIT.md`, blob `4f0b925acac9779b8fd6794418065d8bd6565e33`, https://github.com/tim8es/arc-whitebox/blob/552010f48d67d70b6bb8aae84fe4fc271ccf3f81/research/r322/R322_PUBLIC50_MANIFEST_SOURCE_AUDIT.md ; receipt `research/r322/R322_PUBLIC50_MANIFEST_SOURCE_AUDIT_RECEIPT.json`, blob `2625914219065bec11891317e4ea978ed9cb4308`, https://github.com/tim8es/arc-whitebox/blob/552010f48d67d70b6bb8aae84fe4fc271ccf3f81/research/r322/R322_PUBLIC50_MANIFEST_SOURCE_AUDIT_RECEIPT.json | **NO** |
| R324 | correction to R317, not standalone result | R317 core `NO_GO` unchanged; adds polynomial single-orthant-query caveat and narrows blocker to reusable all-mask state | `review/r317-truncated-normal-gate-estimator-20260924` / correction head `6ede298753b7ebc35765e18479775879769712ff` | corrected R317 report `research/r317/R317_TRUNCATED_NORMAL_GATE_ESTIMATOR_REPORT.md`, blob `b134ccb1c77c3d0e70fe70b64b651e6e5dd1f77c`, https://github.com/tim8es/arc-whitebox/blob/6ede298753b7ebc35765e18479775879769712ff/research/r317/R317_TRUNCATED_NORMAL_GATE_ESTIMATOR_REPORT.md ; receipt `research/r317/R317_RECEIPT.json`, blob `81f6adbc9cc64ab5ad3f4aaf230fe035fffa5ea5`, https://github.com/tim8es/arc-whitebox/blob/6ede298753b7ebc35765e18479775879769712ff/research/r317/R317_RECEIPT.json | **NO — correction only** |
| R325 | conditional offline reanalysis | `COMPLETE / CONDITIONAL_ENVELOPE_COMPUTED_MEMBERSHIP_UNPROVEN` | `review/r325-r209-mini100-public50-conditional-bounds-20260924` / `efd518021ccc120ccb4e859f2588648d83f2b57f` | report `research/r325/R325_R209_MINI100_PUBLIC50_CONDITIONAL_BOUNDS.md`, blob `05f568f257c7e7a23244232deecd19b108184529`, https://github.com/tim8es/arc-whitebox/blob/efd518021ccc120ccb4e859f2588648d83f2b57f/research/r325/R325_R209_MINI100_PUBLIC50_CONDITIONAL_BOUNDS.md ; receipt `research/r325/R325_RECEIPT.json`, blob `80be370c465323a5f74760595fb582051f1866ba`, https://github.com/tim8es/arc-whitebox/blob/efd518021ccc120ccb4e859f2588648d83f2b57f/research/r325/R325_RECEIPT.json | **NO — recomputes stored R209 outputs only** |
| R326 | official-source public-method audit | current rank-2 `suliman_tadros` / #331931: `NO_PUBLIC_METHOD` | `review/r326-rank2-suliman-method-audit-20260924` / `c9e7738030b2c6443c155a411e893b3f738af1a6` | report `research/r326/R326_RANK2_SULIMAN_METHOD_AUDIT.md`, blob `81e1cd551ed34bb7800af1ebd41524dc1ac13629`, https://github.com/tim8es/arc-whitebox/blob/c9e7738030b2c6443c155a411e893b3f738af1a6/research/r326/R326_RANK2_SULIMAN_METHOD_AUDIT.md ; receipt `research/r326/R326_RANK2_SULIMAN_METHOD_AUDIT_RECEIPT.json`, blob `406e1e26d28bd6d161041b79124d3d76037f4384`, https://github.com/tim8es/arc-whitebox/blob/c9e7738030b2c6443c155a411e893b3f738af1a6/research/r326/R326_RANK2_SULIMAN_METHOD_AUDIT_RECEIPT.json | **NO** |
| R327 | official-source public-method audit, corrected lineage | `CONFIRMATORY_DUPLICATE_OF_R312`; same #332100; underlying `NO_PUBLIC_METHOD` unchanged; no novel method delta | `review/r327-luna-rank5-method-audit-20260924` / R330-corrected head `ae471fef454ff8fe75473d4df9c99ead6f0abeda` | report `research/r327/R327_LUNA_RANK5_METHOD_AUDIT.md`, blob `a5724e2a6bf022e9755ce0822219ffa8d5190a54`, https://github.com/tim8es/arc-whitebox/blob/ae471fef454ff8fe75473d4df9c99ead6f0abeda/research/r327/R327_LUNA_RANK5_METHOD_AUDIT.md ; receipt `research/r327/R327_RECEIPT.json`, blob `7b317e36637a1a3fc2868ec2708865b79bfc06d5`, https://github.com/tim8es/arc-whitebox/blob/ae471fef454ff8fe75473d4df9c99ead6f0abeda/research/r327/R327_RECEIPT.json | **NO** |
| R328 | official-source public-method / identity-delta audit | `NO_PUBLIC_METHOD`; current J2W View remains #331539; #332101 belongs to AndreasHad04 | `review/r328-j2w-current-submission-method-delta-20260924` / `0f5c3212eb0da2e9fba2bade2ceea33d818c403b` | report `research/r328/R328_J2W_CURRENT_SUBMISSION_METHOD_DELTA.md`, blob `c9967bc084c3371324c291cf1e5ce1d7c57689bc`, https://github.com/tim8es/arc-whitebox/blob/0f5c3212eb0da2e9fba2bade2ceea33d818c403b/research/r328/R328_J2W_CURRENT_SUBMISSION_METHOD_DELTA.md ; receipt `research/r328/R328_RECEIPT.json`, blob `96d7d51d902c44d9773fee794d8122627de96156`, https://github.com/tim8es/arc-whitebox/blob/0f5c3212eb0da2e9fba2bade2ceea33d818c403b/research/r328/R328_RECEIPT.json | **NO** |
| R329 | official-source public-method audit | current rank-3 `marius_binner` / #331953: `NO_PUBLIC_METHOD` | `review/r329-rank3-marius-method-audit-20260924` / `17713f7dd2fa43f86a1b02f24f843b77bb433960` | report `research/r329/R329_RANK3_MARIUS_METHOD_AUDIT.md`, blob `4f05197a07391fc92515b085bc78f4f2665295ea`, https://github.com/tim8es/arc-whitebox/blob/17713f7dd2fa43f86a1b02f24f843b77bb433960/research/r329/R329_RANK3_MARIUS_METHOD_AUDIT.md ; receipt `research/r329/R329_RANK3_MARIUS_METHOD_AUDIT_RECEIPT.json`, blob `0172658228760db0d685e4e43f2cfd93b5c4a8c8`, https://github.com/tim8es/arc-whitebox/blob/17713f7dd2fa43f86a1b02f24f843b77bb433960/research/r329/R329_RANK3_MARIUS_METHOD_AUDIT_RECEIPT.json | **NO** |
| R331 | independent arithmetic/provenance red-team | `COMPLETE / PASS`; R325 quantitative results independently reproduced, no correction | `review/r331-independent-r325-bound-verification-20260924` / `695bde569e8164d3bccceae4c0d5ab01698de1fd` | report `research/r331/R331_INDEPENDENT_R325_BOUND_VERIFICATION.md`, blob `4f46e1550e0e900556793712eff45c08e413f0fd`, https://github.com/tim8es/arc-whitebox/blob/695bde569e8164d3bccceae4c0d5ab01698de1fd/research/r331/R331_INDEPENDENT_R325_BOUND_VERIFICATION.md ; receipt `research/r331/R331_RECEIPT.json`, blob `3a8e567c58518335fa9e6aa2bb7c90afda0c41d0`, https://github.com/tim8es/arc-whitebox/blob/695bde569e8164d3bccceae4c0d5ab01698de1fd/research/r331/R331_RECEIPT.json | **NO — arithmetic/provenance verification only** |
| R333 | conditional offline score-decomposition | `COMPLETE / COMPUTE_ONLY_INSUFFICIENT_AT_FIXED_OBSERVED_ACCURACY` | `review/r333-r209-compute-floor-headroom-20260924` / `b089c3e24f7ea5499b66f09da27a2be3f9b5d3de` | report `research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM.md`, blob `5e2b58a80a647b9f0a8dcc3355a65d8e5a01e4f5`, https://github.com/tim8es/arc-whitebox/blob/b089c3e24f7ea5499b66f09da27a2be3f9b5d3de/research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM.md ; receipt `research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM_RECEIPT.json`, blob `3718a7ce748a57db36f08fbd64fd55cabd51c801`, https://github.com/tim8es/arc-whitebox/blob/b089c3e24f7ea5499b66f09da27a2be3f9b5d3de/research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM_RECEIPT.json | **NO — offline decomposition of stored R209 outputs only** |
| R335 | theory scout | `COMPLETE / EVIDENCE_BASED_NO_GO / ALREADY_COVERED_AT_DEEP_REALIZATION` | `review/r335-accuracy-side-estimator-scout-20260924` / `9e01cb63dc2a4e662422b3ae98af67d1830505b7` | report `research/r335/R335_ACCURACY_SIDE_ESTIMATOR_SCOUT.md`, blob `1477f3be912bf8c641e3e51c9812cc4833a603d1`, https://github.com/tim8es/arc-whitebox/blob/9e01cb63dc2a4e662422b3ae98af67d1830505b7/research/r335/R335_ACCURACY_SIDE_ESTIMATOR_SCOUT.md ; receipt `research/r335/R335_RECEIPT.json`, blob `d4d1891d2f13dd51b38032baacd7cb8dd92066b5`, https://github.com/tim8es/arc-whitebox/blob/9e01cb63dc2a4e662422b3ae98af67d1830505b7/research/r335/R335_RECEIPT.json | **NO — 0 ideas admitted; no run** |

### Caveats preserved by R332

- **R321:** randomized polynomial-time algorithms exist for a single correlated Gaussian orthant/convex-set query; this does not falsify the narrower lack of a reusable polynomial-size non-Gaussian all-mask state with composable error and Phase-2 cost bounds.
- **R322:** the identity-bearing evaluator mapping exists in the evaluation-data construction, but the exact deployed public-50 mapping is not publicly exposed; R322 does not prove a separately named public manifest.
- **R324:** this is a correction commit on R317, not a standalone scientific task/result. Explicit all-mask state bookkeeping is `Theta(2^n n)` for conditional first moments or `Theta(2^n n^2)` for full conditional covariances; that statement is not a lower bound on one orthant query.
- **R325:** the sharp R209 50-of-100 adjusted-score envelope is `[7.242872117838148426e-9, 9.0979227623963048e-9]` only **conditionally** on grader public-50 being a 50-row subset of R209 Mini-100 and scorer comparability. Membership remains unproved, so this is not a contest score or leaderboard gap/place result.
- **R326:** current rank-2 row directly links suliman_tadros to #331931, but no public method/config/source/repository linkage is established.
- **R327/R330:** R330 is only an append-only lineage correction to R327. R327 is confirmatory of already-completed R312 for the same #332100, not a novel audit or method discovery.
- **R328:** the fresh J2W View remains #331539; #332101 is attributable to AndreasHad04 from the current leaderboard, not J2W. Exact unrounded J2W score remains unknown.
- **R329:** current rank-3 row directly links marius_binner to #331953; public access does not establish method disclosure.
- **R331:** independently reproduces R325's saved arithmetic/provenance and preserves the same external limitation: the actual public-50 to R209 membership/join remains unproved.
- **R333:** at fixed committed R209 mean raw MSE `2.228303490170447e-8`, the Phase-2 `0.1` multiplier floor gives counterfactual mean adjusted score `2.228303490170447e-9`, still numerically above the rounded leaderboard display `2.10e-9`. Matching that display at multiplier `0.1` would require mean raw MSE `2.10e-8`, a `5.7579%` reduction from the committed R209 mean. This is score decomposition only: no achievable-estimator claim, no same-panel leaderboard claim, and the exact public-50→R209 join remains unproved.
- **R335:** the scalar characteristic-function positive-part identity gives an exact ReLU mean when the required joint characteristic-function values are available. The deep realization is not a new estimator family: exact generic-dense propagation returns to R317/R321 orthant/gate state (or E114–E119 boundary state), while tractable approximations re-enter already occupied sampling, Gaussian/mixture, or compression lanes. The preregistered re-entry gate was **not executed**: only if a future concrete non-duplicate polynomial-size joint-CF closure exists should a width-8/depth-4 exact-small test require candidate raw mean-vector MSE `<= 0.94×` matched parent, no median per-neuron degradation, and later proof of `<2^41` FLOPs/network plus a credible `<0.4 s` residual path.

### Measurement separation

**Genuine new estimator measurements among R321, R322, R324–R329, R331, R333, and R335: 0.**

- R321 is theory/red-team only.
- R322, R326–R329 are source/identity/public-method audits.
- R324 and R330 are corrections only.
- R325 performs offline arithmetic on already committed R209 V25 per-MLP adjusted scores; it does not rerun V25 or the grader.
- R331 independently rechecks R325 arithmetic/provenance; it does not rerun an estimator or benchmark.
- R333 decomposes the already committed R209 score into a fixed-observed-accuracy compute-floor counterfactual; it does not measure a new estimator, prove achievability, or establish grader public-50 membership.
- R335 is a theory-only scout: the scalar CF identity is exact, but no genuinely new deep realization survived dedupe; `ideas_admitted=0`, and the preregistered exact-small gate remains unexecuted.

This preserves the earlier distinction: a report can recognize or recompute facts from a prior scientific measurement without itself becoming a new estimator measurement.

## R313 correction lineage and R223 measurement

R313 is **not** a missing sidecar and **not** a separate R313 branch. It is a fast-forward correction on the existing R309 branch.

Exact R309 branch lineage:

1. `d526eb9c8663acad798ec658b740f2a945d83768` — `research: add R309 toolchain delta audit`
2. `1e23a25550369da60b976416fe0f502a6189b833` — `research(R313): correct R309 R223 attempt-6 evidence`

The R313 correction establishes from immutable control/R240/R242 evidence that:

- R223 attempts 1–5 did not reach a panel;
- **attempt 6 executed exactly one authenticated public Phase-2 `mini:all-100` development panel**;
- candidate and R209 parent each had 100 rows and 0 failures;
- R223 candidate adjusted score: `8.171116513490032e-9`;
- R209 parent adjusted score: `8.170397440117226e-9`;
- paired `parent - candidate` mean: `-7.190733728024271e-13`.

Equivalently, the R223 candidate was worse than R209 by approximately **`7.190733728e-13`** in adjusted score on this same development panel.

Terminal development verdict: **`SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED` / same-panel development NO-GO**.

This is a real prior scientific estimator measurement. R313 did not create a new experiment; it corrected R309's traceability to that already-existing R223 measurement.

The formal control-v2 distinction is therefore:

- **no formal R313 job/event**;
- **yes, R313 correction artifact exists**, preserved by fast-forwarding the R309 sidecar branch;
- **yes, formal R223 finish event exists** at revision 193.

## Scientific measurement vs audit/theory artifacts

### New estimator measurements generated by R306–R319 sidecars

**None.**

Completed sidecars are:

- leaderboard forensics: R306, R307, R310, R312, R315, R316, R318;
- comparability/source/identity audits: R309, R311, R313 correction, R314, R319;
- theory-only screens: R308, R317.

R313 is the important exception in *what it recognizes*, not in what it executes: it restores the correct record that **R223 attempt 6 was an actual Mini-100 scientific measurement**. That measurement belongs to R223/R240/R242, not to R313 itself.

R317 is terminal theory-only `EVIDENCE_BASED_NO_GO_BEFORE_IMPLEMENTATION`; its receipt explicitly records zero estimator implementation/execution, zero synthetic/public benchmark runs and zero Actions.

R319 is an identity/comparability audit, not an estimator measurement.

Therefore none of these sidecars belongs in the measured-results registry as a newly measured estimator result.

## Leaderboard ↔ R209 remains NOT_COMPARABLE

R311 and R314 remain `NOT_COMPARABLE`, and R319 sharpens the exact blocker to `NOT_JOINABLE`.

R319 confirms:

- grader-public panel: 50 rows;
- public rows with canonical `network_id`: **0/50**;
- public rows with `target_sha256`: **0/50**;
- R209/R224 Mini-100 rows with canonical `network_id`: **100/100**;
- R209/R224 rows with target fingerprint: **100/100**;
- direct-key coverage from public-50 into R209: **0/50 available**.

Thus the problem is not proof of zero underlying overlap. It is the absence of an admissible direct identity bridge.

The minimum missing artifact is an immutable **official grader-public 50-row canonical-ID manifest** mapping each public `mlp_index` to a canonical `network_id` with identity semantics explicitly compatible with R224's decimal exact int64 `mlp_seed`.

Until that artifact exists, leaderboard-public-50 ↔ R209 remains **NOT_COMPARABLE / NOT_JOINABLE**. No ratio, gap or implied place is justified.

## Formal-control gap

At the audited formal snapshot:

- control-v2 revision: **479**;
- state blob: `1c594d83fe0564e3fffac0188fd9c4c48413434c`;
- control branch head: `089532101b2d1bb767c9eb57dd5c781dbe852b33`;
- formal sidecar jobs/events for R306–R319: **0**.

This does **not** mean the sidecar artifacts are absent. R313 is the clearest example: no formal R313 event exists, while the completed correction is durably stored as the second fast-forward commit on R309's branch.

R320/R323/R332/R334/R336 do not backfill claim/start/finish events and do not edit control-v2.

## Shortest safe next step

**Coordinator-owned append-only reconciliation:** import immutable completed sidecar evidence by task ID + branch head + receipt/report hashes through a supported archival/reconciliation mechanism, explicitly representing R313 as a correction to R309 rather than inventing a separate execution lifecycle.

No historical claim/start/finish events should be fabricated.

## R320/R323/R332/R334/R336 execution accounting

- estimator/benchmark runs: **0**
- Actions runs: **0**
- dataset/dependency downloads: **0**
- submissions: **0**
- private/holdout/full access: **0**
- main edits: **0**
- PR edits: **0**
- control-v2 edits: **0**
- queue edits: **0**
- R320 branch file set relative to exact base: intended to remain **2 files**
