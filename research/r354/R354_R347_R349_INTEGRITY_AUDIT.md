# R354 — independent artifact integrity/content audit of R347 and R349

**Status:** COMPLETE  
**Verdict:** **CONSISTENT_WITH_PERSISTED_EVIDENCE; R349_CURRENT_RAW_CAPTURE_NOT_INDEPENDENTLY_REPRODUCIBLE_FROM_REPO**

R354 is a repository-only integrity/content audit performed before any integration of R347/R349 into consolidated traceability. It does not recapture the public site, open submission pages, infer methods, or edit R320/main/control/queue/PR/Actions.

Exact audit base:
`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

Audit branch:
`review/r354-r347-r349-integrity-audit-20260924`

## 1. R347 branch / artifact integrity

Target branch:
`review/r347-hermite-spectral-mean-estimator-scout-20260924`

Expected/found live head:
`53070953bc502b8847f57e235b5ec5e57acf909e`

Commit parent:
`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

Exact base→R347 comparison:
- ahead: **1**
- behind: **0**
- merge-base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- changed paths: exactly **2**
  1. `research/r347/R347_HERMITE_SPECTRAL_MEAN_ESTIMATOR_SCOUT.md`
  2. `research/r347/R347_RECEIPT.json`

Exact blobs:
- report: `e2d31a3b097904b15de27540ae9af019912324ff`
- receipt: `9d318ea7e2d9c9727ba9c92f1bc0778d2439cf5a`

Report and receipt agree on:
- status `COMPLETE`
- verdict `ALREADY_COVERED`
- measurement classification `NO_NEW_ESTIMATOR_MEASUREMENT`
- exact base and branch
- direct duplicate: **E115**
- E115 live head `85552f57c263be172fdceae25fffe278be065680`
- E115 protocol blob `a63ac3cdedc6bf8a4948c22b8b907a1333f84f70`
- E115 result receipt blob `1f4c10bba845238bd07055c2f423a92c0cdb612a`
- terminal E115 scope: dense total-degree Hermite chaos only
- no new R347 derivation/run after the dedupe stop rule.

### R347 → E115 persisted-evidence verification

The E115 branch is live at the exact head claimed by R347:

`research/e115-hermite-chaos-certified-tail-20260919 @ 85552f57c263be172fdceae25fffe278be065680`

Fetched immutable E115 artifacts resolve to the exact blobs claimed by R347:
- `research/E115_PROTOCOL.md` → `a63ac3cdedc6bf8a4948c22b8b907a1333f84f70`
- `research/E115_RESULT_RECEIPT.json` → `1f4c10bba845238bd07055c2f423a92c0cdb612a`

The E115 receipt records the same mechanism, verdict, historical falsifier values, basis counts, FLOP lower bounds, and scope caveat quoted by R347.

### Independently recomputed R347/E115 numeric claims

For `d=w=1024` and dense total-degree basis
`B(d,p)=C(d+p,p)`:

- `B(1024,1)=1025`
- `B(1024,2)=525825`

For R347/E115's favorable two-late-layer linear-transport lower bound
`4 w^2 B(d,p)`:

- degree 1: `4*1024^2*1025 = 4,299,161,600` FLOPs
- degree 2: `4*1024^2*525825 = 2,205,469,900,800` FLOPs
- Phase-2 budget: `2^41 = 2,199,023,255,552`
- degree-2 excess above the full budget: **6,446,645,248 FLOPs**
- degree-2 utilization: `1.0029315948486328`
- relative to the E115 0.13 utilization cap: `7.7148584219125595x`

Those values match the persisted E115 receipt and R347 report.

The scalar ReLU Parseval remainders also reproduce from the standard-normal Hermite calculation:
- degree-1 remainder: `0.25 - 1/(2*pi) = 0.09084505690810465`
- degree-2 remainder: subtracting the degree-2 contribution `1/(4*pi)` gives approximately `0.01126758536215698`, consistent with the persisted `0.011267585362156995` up to floating representation.

### R347 registry reference check

R347 records R320 at:
`949361e498dd4339e75ddc2baf199782f7a9a5e5`

The live R320 branch currently resolves to that exact head. The fetched R320 artifacts match R347's claimed blobs:
- report `41b14238c0062081e1b3970e2961cb7c18ef88f9`
- receipt `280516be04a2606a431f084e8cef9e678d290184`

### R347 remaining unverifiable without re-execution

R354 does **not** independently rerun E115. Therefore the following are verified only as persisted E115 evidence, not re-measured here:
- E115 historical GitHub Actions execution success;
- artifact ZIP digest/replay claim;
- runtime-specific execution metadata;
- any historical environment behavior beyond the committed receipt.

No R347 discrepancy was found.

## 2. R349 branch / artifact integrity

Target branch:
`review/r349-live-leaderboard-snapshot-20260924`

Expected/found live head:
`0447834b74ac88712200c14997e1fd24276b30e6`

Commit parent:
`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

Exact base→R349 comparison:
- ahead: **1**
- behind: **0**
- merge-base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- changed paths: exactly **2**
  1. `research/r349/R349_LIVE_LEADERBOARD_SNAPSHOT.md`
  2. `research/r349/R349_RECEIPT.json`

Exact blobs:
- report: `268bb1b6e8f53b11c713b8b97adbba1ad81e0394`
- receipt: `c1a1689061e22f96bddbce65586c24d1dd60eefc`

The branch tree contains no third R349 artifact and no raw leaderboard-array file.

### Report ↔ receipt consistency

R349 report and receipt agree on all material persisted fields checked:
- capture timestamp: `2026-09-24T12:20:18.917Z`
- page 1 range/rows: `Showing 1–100 of 197` / 100
- page 2 range/rows: `Showing 101–197 of 197` / 97
- total visible rows: 197
- cells per row: 10
- compact concatenated row-array byte length: 21,732
- compact concatenated row-array SHA-256:
  `a16f4399d9c71e869a1199285584148066746204ebe66a54c22d254b954e81bf`
- R304 baseline identities/hashes
- first-page exact display-identity counts: 95 shared / 5 old-only / 5 current-only
- the exact old-only and current-only string lists
- shared-95 field-change counts
- J2W display-level old/current fields
- full historical page-2 delta remains `UNKNOWN`
- leaderboard↔R209/public-50 remains `NOT_COMPARABLE / NOT_JOINABLE`
- no estimator/method inference.

### R349 raw-array non-commit labeling

This requirement is satisfied clearly and redundantly.

The report states:

> The raw 197 row arrays were retained in the coordinator browser session, but **are not committed as a GitHub file in R349**.

The receipt records:
- `raw_rows_committed_to_repository: false`
- note: raw page1+page2 arrays were retained in the coordinator browser session but are not stored as a GitHub file in R349.

The exact R349 commit/tree independently confirms only two files exist in the branch diff: report + receipt. There is no committed raw 197-row array artifact.

### R304 baseline verification for R349

R349 points to:
- branch `review/r304-leaderboard-delta-20260924`
- head `fcff8898104a21431eb9e1a5eec0f5cb6bb00468`
- raw artifact `research/r304/R304_RAW_VISIBLE_ROWS.json`
- Git blob `2fee6241febe322fbff2cbc605581590fc072ee6`

R354 independently fetched that immutable file and recomputed:

- raw-file SHA-256:
  `807df449176bd1cde98e6da418f30aa4aba848c9767a7e44196385587f17b016`
- compact `JSON.stringify(rows)` SHA-256:
  `4ffcdf469435f3b6dd55df39b6a06c3b5a186b7de89251a526254169a0fbe0d5`
- row count: 100
- every row cell count: 10

All match the R304 supplement and R349 report/receipt.

R349's five `old-only` display strings are all present exactly in the committed R304 first 100:
- `DO dogus_ozel —`
- `ED edo2 —`
- `NK DancinGirl 1 member`
- `CW cwc —`
- `EL ely2sh —`

The R304 J2W row also independently matches R349's historical-side fields:
- rank 01
- Adjusted Score `2.10e−9`
- Final Layer MSE `1.64e−8`
- sampling ratio `539×`
- Entries 320
- Last Submission `Sep 19, 00:05 ...`

### R349 claims that remain unverifiable from committed artifacts

Because the current 197 raw row arrays are **not committed**, R354 cannot independently recompute or authenticate the current-capture-derived claims below without recapturing the site, which this task forbids:

- the 21,732-byte current concatenated-array length;
- current concatenated-array SHA-256 `a16f4399d9c71e869a1199285584148066746204ebe66a54c22d254b954e81bf`;
- that the current arrays contain exactly 100 + 97 rows;
- all 95/5/5 current-vs-R304 identity counts as calculations;
- the five `current-only` strings as current capture facts;
- the shared-95 field-change counts (64 rank, 13 score, 10 MSE, 22 entries, 13 timestamp);
- current page-2 placements `cwc=101`, `ely2sh=102`;
- current J2W fields (`2.00e−9`, `1.61e−8`, `566×`, 323, Sep 24 08:55);
- capture timestamp/range values as independently observed UI facts;
- the statement that raw arrays remained retained in a coordinator browser session after capture.

Those claims are **internally consistent between R349 report and receipt**, but their underlying current row payload is absent from Git, so R354 classifies them as **PERSISTED_ATTESTATION_ONLY / NOT_INDEPENDENTLY_RECOMPUTABLE_FROM_REPOSITORY**.

This is not a contradiction: R349 explicitly discloses the absence of the raw arrays.

## 3. Final audit verdict

**No material artifact-integrity or report-vs-receipt discrepancy found in R347 or R349.**

R347:
- exact live head: PASS
- exact base/parent: PASS
- exactly two-file diff: PASS
- report/receipt blobs: PASS
- E115 referenced head/blobs: PASS
- key basis/FLOP arithmetic: PASS
- Parseval values: independently consistent
- no-new-measurement classification: consistent.

R349:
- exact live head: PASS
- exact base/parent: PASS
- exactly two-file diff: PASS
- report/receipt blobs: PASS
- explicit raw-array non-commit disclosure: PASS
- R304 baseline blob/hash/row structure: independently PASS
- R304 historical-side identity/J2W claims checked: PASS
- current 197-row-derived statistics/hash: internally consistent but **not independently verifiable from committed artifacts**.

## 4. Execution accounting

- public site recapture: **NO**
- submission pages opened: **NO**
- competitor method inference: **NO**
- estimator/benchmark execution: **NO**
- GitHub Actions: **NO**
- dataset/dependency download: **NO**
- private/sealed/holdout/full access: **NO**
- R320 integration/edit: **NO**
- main/control/queue/PR edits: **NO**
- intended R354 diff: exactly this report + one JSON receipt
