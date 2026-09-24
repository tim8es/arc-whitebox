# R320 — sidecar research traceability audit

**Status:** COMPLETE — corrected by R323; extended by R332/R334/R336/R339  
**Mode:** report-only traceability audit  
**Branch:** `review/r320-sidecar-research-traceability-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**R323 correction parent:** `ae418aa7bcdb08549b051745816bce16aafe1e7e`  
**R332 extension parent:** `0c4db1d79deb9b2f608001127d8359b0c0fafd27`  
**R334 extension parent:** `1c285e5d504d6eb3c971d5afae9db3188e0dcea0`  
**R336 extension parent:** `2a524361d1b39ef3066f97cc2d986f1596f58920`  
**R339 synchronization parent:** `a9434ed9b22a41e1ecff2aba6fd7d0f790396d60`

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
| R335 | theory scout, R338-corrected | `COMPLETE / EVIDENCE_BASED_FEASIBILITY_NO_GO`; R338 material correction applied, no impossibility/lower-bound claim | `review/r335-accuracy-side-estimator-scout-20260924` / `1e233a439b81708353513998898e9f7cfd10caf2` | corrected report `research/r335/R335_ACCURACY_SIDE_ESTIMATOR_SCOUT.md`, blob `32fcd8e7c43c712aa81b2c0e2f3487f3911d9c23`, https://github.com/tim8es/arc-whitebox/blob/1e233a439b81708353513998898e9f7cfd10caf2/research/r335/R335_ACCURACY_SIDE_ESTIMATOR_SCOUT.md ; corrected receipt `research/r335/R335_RECEIPT.json`, blob `4e7d9523f1b08580358b9f2340f076977e611573`, https://github.com/tim8es/arc-whitebox/blob/1e233a439b81708353513998898e9f7cfd10caf2/research/r335/R335_RECEIPT.json | **NO — 0 ideas admitted; no run** |
| R337 | independent theory/forensics red-team | `COMPLETE / PASS_WITH_MATERIAL_CORRECTION`; terminal interpretation `EVIDENCE_BASED_FEASIBILITY_NO_GO_UNCHANGED` | `review/r337-r335-independent-red-team-20260924` / `9c233d8ba33ae64316d6ec71bc0f433dc8574451` | report `research/r337/R337_R335_INDEPENDENT_RED_TEAM.md`, blob `551d895ffdc222ee5e2b45246419a70613f9eae1`, https://github.com/tim8es/arc-whitebox/blob/9c233d8ba33ae64316d6ec71bc0f433dc8574451/research/r337/R337_R335_INDEPENDENT_RED_TEAM.md ; receipt `research/r337/R337_RECEIPT.json`, blob `4248094963d4f1161a71fba100479b227ea8d67b`, https://github.com/tim8es/arc-whitebox/blob/9c233d8ba33ae64316d6ec71bc0f433dc8574451/research/r337/R337_RECEIPT.json | **NO — theory/forensics only** |

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
- **R335/R338:** corrected final verdict is `EVIDENCE_BASED_FEASIBILITY_NO_GO`. Pilipovsky et al. (L4DC/PMLR 2023) is a directly relevant published deep-ReLU characteristic-function/Hilbert-transform method omitted by the original R335 screen. Its numerical construction propagates component-wise CFs; the joint-to-product factorization is stated under independence, while generic dense hidden mixing does not generally preserve that condition. Explicit orthant/mask enumeration remains one exact representation only, **not** a universal lower bound; no impossibility or exponential-hardness claim is made for a single Gaussian/orthant query. The remaining audited blocker is narrower: no finite reusable polynomial-size generic-dense joint-dependence state with rigorous composable propagated-error control and credible `<2^41` FLOP / `<0.4 s` residual guarantees was found. R338 is correction lineage on R335, not a separate study. The width-8/depth-4 re-entry criterion remains **unexecuted**, including candidate raw mean-vector MSE `<= 0.94×` matched parent plus the later cost/residual gates.
- **R337:** independent red-team `PASS_WITH_MATERIAL_CORRECTION`; it confirms the scalar CF identity and generic need for joint dependence, supplies the Pilipovsky omission/correction, rejects explicit-mask necessity and any general exponential lower bound, and leaves the narrower Phase-2 feasibility NO_GO unchanged. It is theory/forensics only, not a new estimator or benchmark result.

### Measurement separation

**Genuine new estimator measurements among R321, R322, R324–R329, R331, R333, R335, R337, and R338 correction lineage: 0.**

- R321 is theory/red-team only.
- R322, R326–R329 are source/identity/public-method audits.
- R324 and R330 are corrections only.
- R325 performs offline arithmetic on already committed R209 V25 per-MLP adjusted scores; it does not rerun V25 or the grader.
- R331 independently rechecks R325 arithmetic/provenance; it does not rerun an estimator or benchmark.
- R333 decomposes the already committed R209 score into a fixed-observed-accuracy compute-floor counterfactual; it does not measure a new estimator, prove achievability, or establish grader public-50 membership.
- R335 remains theory-only after R338: Pilipovsky et al. establishes a real deep CF/Hilbert method, but no audited generic-dense dependency-correct state/error/cost package qualifies for execution; `ideas_admitted=0`, and the exact-small gate remains unexecuted.
- R337 is an independent theory/forensics red-team with `PASS_WITH_MATERIAL_CORRECTION`; it adds no estimator or benchmark measurement.
- R338 is only the append-only material correction applied to R335's two artifacts; it is not a standalone study or measurement.

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

R320/R323/R332/R334/R336/R339 do not backfill claim/start/finish events and do not edit control-v2.

## Shortest safe next step

**Coordinator-owned append-only reconciliation:** import immutable completed sidecar evidence by task ID + branch head + receipt/report hashes through a supported archival/reconciliation mechanism, explicitly representing R313 as a correction to R309 rather than inventing a separate execution lifecycle.

No historical claim/start/finish events should be fabricated.

## R320/R323/R332/R334/R336/R339 execution accounting

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
## R344 integration — completed R340 / R341 / R343 sidecars

R344 extends this consolidated index only with completed artifacts that were absent from the prior R320 tip `62941d0757357f363381e8ee01b93dfc75a5d516`. Exact-string/head deduplication found **no existing R340, R341, or R343 entry** in either R320 artifact before this update. R342 remains in progress and is intentionally not represented as complete.

### R340 — current J2W submission #332136 public-method audit

- status: **COMPLETE**
- verdict: **`NO_PUBLIC_METHOD`**
- exact head: `3350f3f52976187c91207d8474de45feb90c3ac1`
- report: `research/r340/R340_J2W_SUBMISSION_332136_METHOD_AUDIT.md`
  - blob: `7ac3772f87b59e1da0a3b309a1f171c1ded64190`
  - source: https://github.com/tim8es/arc-whitebox/blob/3350f3f52976187c91207d8474de45feb90c3ac1/research/r340/R340_J2W_SUBMISSION_332136_METHOD_AUDIT.md
- receipt: `research/r340/R340_RECEIPT.json`
  - blob: `bca09edfeb7ec0efa792f7b2c4b3abebb7d2e3fb`
  - source: https://github.com/tim8es/arc-whitebox/blob/3350f3f52976187c91207d8474de45feb90c3ac1/research/r340/R340_RECEIPT.json

R340 found no publicly linked estimator family/configuration, source repository/commit, or reproducible instructions tied to current J2W submission **#332136**. It does not infer a method from rank, displayed score, MSE, entries, or timestamp.

The saved live UI anchor carried by R340 includes displayed adjusted score **`2.00e-9`**. In this consolidated index that value remains **stored UI display text only**; its exact underlying float, true contest gap, and any rank-equivalent interpretation remain **UNKNOWN / NOT_COMPARABLE**.

### R341 — partial visible-leaderboard delta capture

- status/verdict: **`PARTIAL_CAPTURE_DOM_PAGINATION_BLOCKED`**
- exact head: `86d37d0e5ad90dae62354df8ad3746e5405a9cbd`
- report: `research/r341/R341_FULL_LEADERBOARD_DELTA.md`
  - blob: `60455019c3691cae865aafd979280c7ba3603d6d`
  - source: https://github.com/tim8es/arc-whitebox/blob/86d37d0e5ad90dae62354df8ad3746e5405a9cbd/research/r341/R341_FULL_LEADERBOARD_DELTA.md
- receipt: `research/r341/R341_FULL_LEADERBOARD_DELTA_RECEIPT.json`
  - blob: `2809f024b167cf28507540f7a113aba8d57af750`
  - source: https://github.com/tim8es/arc-whitebox/blob/86d37d0e5ad90dae62354df8ad3746e5405a9cbd/research/r341/R341_FULL_LEADERBOARD_DELTA_RECEIPT.json

Exact coverage boundary:

- historical R304 first 100: **100/100**
- current live first-100 comparable rows: **1/100**
- current live page 2 rows: **0**
- current full board: **NOT_ESTABLISHED**
- rows 2–100 deltas: **UNKNOWN**
- historical rows 101+: **UNKNOWN**

Only one current row is comparable: the J2W rank-1 anchor. R341 must **not** be read as a full-board delta, a 197-row capture, or evidence of additions/removals/moves outside that one row. The displayed total `197` is task-supplied UI state, not an independently captured full membership list.

### R343 — independent arithmetic/source red-team

- status: **COMPLETE**
- verdict: **PASS**
- exact head: `a76a972711c865e92597c62864dc58ea010eb11f`
- report: `research/r343/R343_R333_2E9_ARITHMETIC_RED_TEAM.md`
  - blob: `ca319b2a634dfb95a04b4ca351661fe3e1ca7fd0`
  - source: https://github.com/tim8es/arc-whitebox/blob/a76a972711c865e92597c62864dc58ea010eb11f/research/r343/R343_R333_2E9_ARITHMETIC_RED_TEAM.md
- receipt: `research/r343/R343_RECEIPT.json`
  - blob: `5ae939e4344db9858c01a4422f21b06df39a71a4`
  - source: https://github.com/tim8es/arc-whitebox/blob/a76a972711c865e92597c62864dc58ea010eb11f/research/r343/R343_RECEIPT.json

R343 independently reproduces the R209 arithmetic from the immutable 100-row development artifact:

- exact-decimal mean raw MSE: **`2.22830349017044681e-8`**
- fixed-MSE scorer multiplier floor: **`0.1`**
- conditional fixed-MSE score floor: **`2.22830349017044681e-9`**
- saved UI display input: **`2.00e-9`**
- under the explicit same-panel/same-scorer counterfactual only, raw-MSE mean needed to equal that displayed number at the floor: **`2.00e-8`**
- absolute raw-MSE reduction required: **`2.2830349017044681e-9`**
- relative reduction: approximately **`10.245619197633778%`**
- compute-only at fixed observed R209 MSE cannot numerically reach the displayed `2.00e-9`.

These are conditional arithmetic statements, **not** a measured contest gap. The saved `2.00e-9` remains UI display text with unknown underlying exact float/rounding interval. Public-50 ↔ R209 identity remains **`NOT_COMPARABLE / NOT_JOINABLE`**; exact deployed public-50 mapping is not public, actual R209 public-50 score is unknown, and no predicted rank/place is implied.

### R344 measurement/comparability classification

R340, R341, and R343 generate **0 new estimator measurements**:

- R340: public-method/source audit only;
- R341: partial public leaderboard snapshot/delta only;
- R343: arithmetic/source verification over committed R209 outputs only.

R342 is still in progress and is not claimed complete here.

The consolidated boundary remains:

- current stored leaderboard display `2.00e-9`: **UI SNAPSHOT TEXT ONLY**
- exact underlying leaderboard float: **UNKNOWN**
- full-board R341 delta: **UNKNOWN / NOT ESTABLISHED**
- public-50 ↔ R209 row identity: **NOT_JOINABLE**
- leaderboard ↔ R209 score/rank equivalence: **NOT_COMPARABLE**
- true contest gap: **UNKNOWN**

## R346 integration — completed R342 addendum on existing R333 branch

R342 is now complete and is added here without modifying R333 history. The original R333 `2.10e-9` snapshot remains historical evidence; R342 is an append-only refresh on the same branch.

- task: **R342**
- status: **COMPLETE_WITH_LATEST_VERIFIED_PUBLIC_SNAPSHOT**
- branch: `review/r333-r209-compute-floor-headroom-20260924`
- exact head: `a7910fec8ad5613833db98c663452e7f232baf7f`
- parent: `b089c3e24f7ea5499b66f09da27a2be3f9b5d3de`
- report: `research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM.md`
  - blob: `439ccaf94f06520ab4355d177493faad8857b936`
  - source: https://github.com/tim8es/arc-whitebox/blob/a7910fec8ad5613833db98c663452e7f232baf7f/research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM.md
- receipt: `research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM_RECEIPT.json`
  - blob: `a225fe4d075eaeceab44ca47599775493744c7d1`
  - source: https://github.com/tim8es/arc-whitebox/blob/a7910fec8ad5613833db98c663452e7f232baf7f/research/r333/R333_R209_COMPUTE_FLOOR_HEADROOM_RECEIPT.json

Preserved interpretation:

- latest verified stored rank-1 UI snapshot: **`2.00e-9` at 2026-09-24 11:28 UTC**;
- exact underlying leaderboard float and formatter: **UNKNOWN**;
- exact-decimal R209 mean raw MSE: **`2.22830349017044681e-8`**;
- fixed-MSE score floor at multiplier `0.1`: **`2.22830349017044681e-9`**;
- under the same-panel/same-scorer counterfactual, required raw-MSE reduction to numerically equal the displayed `2.00e-9`: **`10.245619197633778283625343576205%`**;
- this is **not** a true leaderboard gap and **not** a rank prediction;
- public-50 ↔ R209 identity remains **UNKNOWN / NOT_COMPARABLE**;
- R333's earlier `2.10e-9` snapshot remains preserved as historical and is not overwritten.

R342 generated no new estimator measurement, benchmark, or submission. R343 remains a separate independent `PASS` arithmetic/source verification entry.

## R350 integration — completed R348 formatter source audit

R350 appends the completed R348 primary-source audit to this consolidated traceability index. R348 is classified as a **source audit, not an estimator measurement**. It does not modify or supersede the existing R341, R343, or R342 entries above.

### R348 — public leaderboard display precision / rounding source audit

- status/verdict: **`UNKNOWN_FORMATTER_NOT_PUBLICLY_OBSERVABLE`**
- branch: `review/r348-leaderboard-display-precision-audit-20260924`
- exact head: `4329109ff12afb44259b8221726dbb3f384688a5`
- report: `research/r348/R348_LEADERBOARD_DISPLAY_PRECISION_AUDIT.md`
  - blob: `77a88dd22cb29b2a6cc7a3a9e346c6ee2d665554`
  - source: https://github.com/tim8es/arc-whitebox/blob/4329109ff12afb44259b8221726dbb3f384688a5/research/r348/R348_LEADERBOARD_DISPLAY_PRECISION_AUDIT.md
- receipt: `research/r348/R348_LEADERBOARD_DISPLAY_PRECISION_AUDIT_RECEIPT.json`
  - blob: `ce0268c5f1e37d2dbe1b05ad84bf989ac9f12771`
  - source: https://github.com/tim8es/arc-whitebox/blob/4329109ff12afb44259b8221726dbb3f384688a5/research/r348/R348_LEADERBOARD_DISPLAY_PRECISION_AUDIT_RECEIPT.json

Preserved narrow conclusion:

- the AIcrowd **web leaderboard** formatter/rounding rule for displayed Adjusted Score is **UNKNOWN**;
- the Phase-2 challenge-specific web display precision is **UNKNOWN**;
- whether displayed `2.00e-9` is rounded, truncated, or transformed by another rule is **UNKNOWN**;
- the exact underlying leaderboard float is **UNKNOWN**;
- no mathematically valid underlying interval is derived from the public evidence;
- the AIcrowd web formatter for displayed Final Layer MSE is **UNKNOWN**;
- the lexical text `2.00e-9` alone does not prove a general three-significant-digit formatter.

R348 also records a separate first-party WhestBench local presentation helper using `f"{float(value):.2e}"` for local MSE-style report values. That local `.2e` formatter is **not evidence** for the AIcrowd web leaderboard renderer and must not be transferred to the web UI.

R348 adds **0 estimator measurements**, **0 benchmark measurements**, and **0 submissions**. It changes no R341/R343/R342 conclusion. The consolidated interpretation remains that `2.00e-9` is stored **UI display text only**; exact web formatting, exact underlying float/interval, public-50↔R209 comparability, and true contest gap remain unresolved where previously marked unknown/not comparable.

