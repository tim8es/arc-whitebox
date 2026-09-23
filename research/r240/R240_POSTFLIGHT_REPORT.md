# R240 — independent postflight of R223 attempt 6

Status: **COMPLETE — independent DEVELOPMENT NO-GO**

R240 independently audited the immutable R223 attempt-6 artifact after GitHub Actions
run `35810427656` / job `107020553482` completed successfully. No R223 code,
candidate, protocol, workflow, benchmark, Actions run, retry or gate was changed.

## Frozen identity

- R223 run id: `R223-v25-local-feed-attempt6-20260923`
- Actions attempt: `1`
- Actions head: `09efbb920313850a4727bd34db9088a46227ce5f`
- artifact: `10730459690`, `r223-v25-local-feed-mini100-attempt6`
- GitHub digest and independently recomputed ZIP SHA256:
  `f144bfd2a5a8a82aaa3e600d1f384d68cfe5e525eb7e22e91eb1d7e843763e00`
- frozen protocol blob: `1e88341a6320bf91c8f4eff0aa60d8b6a33cf484`
- attempt-6 workflow blob: `d24e3f63e8ce447188868846e9b3e4ef755b395e`
- candidate blob: `eb95d4ae46a031be5131eef8dd0909f2061b8749`
- transform verifier blob: `961e5afb052e2cfdc15e1284de49e57ba1514a73`
- owner comparator blob: `fd1ce8711f92bb123f69d7bcddb37bb0fec3b8b0`

R240 verifier/checklist were committed before artifact inspection:
- verifier commit `7dddfad12ad5720751225bc8d6127e10cd40a81e`;
- checklist commit `9131534ed843dfad8208a062e9b2149b9c1aa016`;
- synthetic self-check commit `779e66a7e45e52beb9bfdb53aad7b34c457cefd7`;
- self-check result commit `84d0f27141f9719eb1834baaab55f0dbf5437f25`.

The self-check covered 100-row identity, official adjusted-score arithmetic,
`error_code`-only failure penalty, all frozen thresholds, duplicate-panel rejection
and fail-closed manifest tamper detection, using synthetic records only.

## Artifact / provenance verification

All checks passed:

- ZIP digest exact;
- archive contained 24 files: 23 evidence/source files plus `sha256.json`;
- manifest has exactly 23 entries, with zero missing, extra or hash-mismatched files;
- all mandatory evidence files are present;
- uploaded protocol/patch/candidate/verifier/comparator files match every frozen git blob;
- attempt-6 arm content is exact;
- exact parent->candidate transform guard passes;
- static feed identity and mean-normalization test pass;
- free/public standard-runner gate passes;
- NumPy 2.4.6, flopscope 0.12.1 and whestbench 0.16.1 identities pass;
- validation and panel run exits are both zero.

The candidate source is therefore the preregistered V25-LF source, not a post-result
variant.

## Parent binding

The artifact parent report SHA256 is exactly
`68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3`.

R240 also compared all 100 parent rows against the normalized R209 V25 registry rather
than trusting the aggregate. A canonical binary projection of
(index, name, MSE, FLOPs, adjusted score, failure flag, residual time) has SHA256:

`9f07b271d5d1a4f3180ba0a8a8b01b720198c08e3ee3906feb8416d01f38ec24`

for both the normalized registry and the artifact parent report.

Parent recomputation:
- 100 rows;
- failures: 0;
- mean raw final MSE: `2.228303490170447e-8`;
- mean adjusted score: `8.170397440117226e-9`
  (floating recomputation of frozen `8.170397440117225e-9`);
- mean effective compute: `806303721965`;
- mean C/B: `0.36666448157347986`;
- max residual: `0.19043814401743475 s`.

## Independent 100-row candidate recomputation

R240 used the canonical whestbench 0.16.1 failure predicate:
`error_code OR budget_exhausted OR time_exhausted OR
residual_wall_time_exhausted OR combined_budget_exhausted`.

Every candidate row's reported adjusted score exactly agrees with independent
`MSE * (1 on failure else max(0.1, effective_compute/B))` recomputation.

Candidate:
- rows: 100, exact parent name/order;
- failures: 0;
- mean raw MSE: `2.2284993050902814e-8`;
- mean adjusted score: `8.171116513490029e-9`;
- mean effective compute: `806303829485`;
- mean C/B: `0.36666453046791503`;
- all rows measured `806303829485` FLOPs;
- max residual: `0.19380312699274782 s`.

Versus parent, candidate raw MSE is **0.0087876234% worse** and adjusted score is
**0.0088009595% worse**.

Paired adjusted-score comparison:
- candidate improves 50/100 networks;
- mean(parent - candidate):
  `-7.190733728024271e-13`;
- SE: `1.4922201293529365e-12`;
- mean/SE: `-0.48188156603559223`.

R240 also compared all 100 owner paired rows to the independent recomputation:
zero row mismatches.

## Frozen gates

| Gate | Result |
|---|---|
| exact 100-name/order identity | PASS |
| dataset SHA identical | PASS |
| candidate failures = 0 | PASS |
| candidate mean raw MSE < parent | **FAIL** |
| candidate adjusted <= 0.995 × parent | **FAIL** |
| improves >=55/100 networks | **FAIL** |
| paired delta mean > 2 × SE | **FAIL** |
| mean C/B <= parent + 1e-5 | PASS |
| max residual <0.4 s | PASS |
| exact source/config/provenance | PASS |
| only one candidate panel run | PASS |

For the last gate, Actions step metadata independently shows attempts 1–5 skipped their
candidate panel steps; attempt 6 is the only panel step that completed successfully.

No gate was relaxed. Therefore:

**R240_INDEPENDENT_DEVELOPMENT_NO_GO**

This agrees with owner decision
`R223_SCIENTIFIC_REJECT_DROP_V25_LOCAL_FEED`, but is based on R240's independent
row-level recomputation.

## Claim boundary

This is a same-exposed-panel **development** result only. It supports dropping the
frozen V25-LF change under R223's preregistered criteria.

It does **not** establish leaderboard rank, hidden/private generalization, official
submission readiness or competition outcome. No holdout/private data, submission or
canonical V25 change was used.
