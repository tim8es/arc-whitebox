# R320 — sidecar research traceability audit

**Status:** COMPLETE — corrected by R323  
**Mode:** report-only traceability audit  
**Branch:** `review/r320-sidecar-research-traceability-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**R323 correction parent:** `ae418aa7bcdb08549b051745816bce16aafe1e7e`

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
| R317 | theory | `EVIDENCE_BASED_NO_GO_BEFORE_IMPLEMENTATION` | `review/r317-truncated-normal-gate-estimator-20260924` / `6264781a18c1cea2ec6540ea312875ec1d5aba56` | **YES** — report blob `102854932f111e793657747a4aa227b23f19e7fc` + receipt blob `926e190d4672d9a8f26853566bf66b4c82cba291` | **NO** |
| R318 | leaderboard forensic | `NO_PUBLIC_METHOD` | `review/r318-top6-public-config-audit-20260924` / `d0138a3fe772c712d331f5fde0c7e75be5bb56b7` | **YES** — report + receipt | **NO** |
| R319 | comparability | `NOT_JOINABLE` | `review/r319-public50-r209-join-audit-20260924` / `9086b846cc6e11ad91117870c3015d25bfc5504a` | **YES** — report blob `c858a8f3bd29f50c5188894aeaaa73e2208a374f` + receipt blob `517c4ea88041432c6929c561b18b42a01be94761` | **NO** |

R321/R322 began after the original R320 audit window. They are not used for any conclusion here.

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

R320/R323 do not backfill claim/start/finish events and do not edit control-v2.

## Shortest safe next step

**Coordinator-owned append-only reconciliation:** import immutable completed sidecar evidence by task ID + branch head + receipt/report hashes through a supported archival/reconciliation mechanism, explicitly representing R313 as a correction to R309 rather than inventing a separate execution lifecycle.

No historical claim/start/finish events should be fabricated.

## R320/R323 execution accounting

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
