# R341 — Phase-2 visible leaderboard delta vs exact R304 baseline

**Verdict: PARTIAL_CAPTURE_DOM_PAGINATION_BLOCKED.**

R341 is separate from R340's method audit of submission #332136. It attempts only a public visible-leaderboard snapshot/delta and does not open submission pages.

The requested same-timestamp two-page live capture could not be completed from the public interfaces available in this session. The leaderboard is client-rendered: the accessible crawl exposed only a stale subset, while page 2 returned only a `Loading` shell. R341 therefore does **not** claim full 197-row coverage.

Capture-attempt timestamp: **2026-09-24T11:36:20Z**.

## 1. R304 baseline — verified before comparison

Baseline branch:
`review/r304-leaderboard-delta-20260924`

Exact R304 capture:
- captured at: `2026-09-24T02:36:19.062Z`
- displayed range: `Showing 1–100 of 195`
- visible rows: **100**
- raw artifact: `research/r304/R304_RAW_VISIBLE_ROWS.json`
- raw artifact Git blob SHA-1: `2fee6241febe322fbff2cbc605581590fc072ee6`
- normalized rows SHA-256: `4ffcdf469435f3b6dd55df39b6a06c3b5a186b7de89251a526254169a0fbe0d5`
- raw file SHA-256 recorded by R304 supplement: `807df449176bd1cde98e6da418f30aa4aba848c9767a7e44196385587f17b016`

R304 verification receipt:
- `research/r304/R304_CAPTURE_SUPPLEMENT_RECEIPT.json`
- Git blob SHA-1: `02aa0698369cc23bcd78753f3de7691589606acb`

The supplement and raw artifact agree on timestamp, source URL, row count, blob, normalized-row hash, and file hash.

R304 did **not** capture historical page 2. Therefore all historical comparison outside the first 100 rows remains **UNKNOWN**.

## 2. Current public leaderboard capture attempt

Requested URLs:

- page 1:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2
- page 2:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2&page=2

Observed public-access behavior:

- a crawlable official leaderboard representation exposed **50 rows**, but it was stale for J2W relative to the independently preserved live UI anchor;
- the page-2 URL returned only a client-side `Loading`/generic shell and no table rows;
- the stale 50-row crawl is therefore **excluded** from the requested current-live delta;
- no submission page was opened as a workaround.

The task-supplied current UI reports **197 total**. R341 records that value as a task-supplied visible count, but does **not** claim that all 197 current rows were independently captured.

### Actual coverage

- R304 historical first page: **100/100 rows verified**
- R304 historical page 2: **0 rows; UNKNOWN**
- current live rows certifiable in this audit lineage: **1**
- current live first-100 comparable rows: **1/100**
- current live page-2 rows: **0**
- stale official crawl rows observed but excluded: **50**
- claimed full 197-row capture: **NO**

## 3. Current rank-1 live anchor

The immediately preceding completed R340 audit preserved the current live rank-1 leaderboard anchor:

- participant/team: **J2W / joe_wanza**
- rank: **1**
- displayed Adjusted Score: **2.00e-9**
- displayed Final Layer MSE: **1.61e-8**
- entries: **323**
- latest displayed: **Sep 24 08:55**
- direct View target: **submission #332136**
- View URL:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/332136

R340 receipt:
- branch: `review/r340-j2w-submission-332136-method-audit-20260924`
- path: `research/r340/R340_RECEIPT.json`
- Git blob SHA-1: `bca09edfeb7ec0efa792f7b2c4b3abebb7d2e3fb`

R341 did **not** open that submission page. The target ID/URL are carried only from the live leaderboard anchor already preserved by R340.

## 4. Exact comparable delta: R304 rank-1 J2W → current anchor

R304 row 1 at `2026-09-24T02:36:19.062Z`:

- rank: `01`
- participant/team display: `J2W 1 member · Numascale AS`
- displayed adjusted score: `2.10e−9`
- displayed Final Layer MSE: `1.64e−8`
- entries: `320`
- last submission: `Sep 19, 00:05 5 d ago`
- raw R304 row stored only the text `View`; the href/submission ID was not preserved in that artifact.

Current live anchor:

- rank: `1`
- participant/team: `J2W / joe_wanza`
- displayed adjusted score: `2.00e-9`
- displayed Final Layer MSE: `1.61e-8`
- entries: `323`
- latest: `Sep 24 08:55`
- direct View target: `#332136`

Concrete supportable changes:

- J2W remains at displayed rank 1;
- displayed adjusted score changed `2.10e−9 → 2.00e-9`;
- displayed Final Layer MSE changed `1.64e−8 → 1.61e−8`;
- entries changed `320 → 323`;
- latest-submission display moved from Sep 19 to Sep 24 08:55;
- the current rank-1 row now links to **submission #332136**.

This is the requested flag for the new current rank-1 **linked submission**. It is not a claim that a new participant entered rank 1.

R341 does not infer:
- an exact unrounded-score change;
- a score gap;
- an estimator or algorithm;
- causality from the displayed movement.

## 5. Other additions / removals / moves within the comparable first 100

Because current rows 2–100 could not be captured live at the common timestamp:

- concrete additions in rows 1–100: **UNKNOWN**
- concrete removals in rows 1–100: **UNKNOWN**
- concrete moves other than J2W retaining rank 1: **UNKNOWN**
- rows 2–100 field-by-field delta: **UNKNOWN**

The stale 50-row crawl is not mixed with the live J2W anchor because that would combine incompatible snapshots.

## 6. Current visible count vs historical remainder

- R304 displayed total: **195**
- task-supplied current UI total: **197**

R341 records both displays but **does not infer a full-board change** from them, because:
- current membership was not captured across both pages;
- historical page 2 was never captured by R304;
- additions/removals outside the first 100 cannot be reconstructed.

Historical remainder outside R304's first 100: **UNKNOWN**.

## 7. Exact blocker

**DOM/pagination blocker:** the official leaderboard table is client-rendered and the available public extraction interfaces in this session could not execute/hydrate the live page-1/page-2 table consistently.

Specifically:
- the accessible crawl was stale for J2W;
- page 2 returned only `Loading`;
- no browser-control surface available here could paginate the live table and extract the hydrated DOM;
- submission pages were not opened.

## 8. Final status

**PARTIAL_CAPTURE_DOM_PAGINATION_BLOCKED**

Verified:
- exact R304 100-row baseline and hashes;
- current visible-count observation `197` as task-supplied UI state;
- current rank-1 J2W anchor and View target #332136 through committed R340 evidence;
- one concrete R304→current row delta.

Not verified:
- full current page 1;
- current page 2;
- full 197-row current snapshot;
- any additions/removals/moves for rows 2–100;
- historical page-2 changes.

## Safety / execution accounting

- submission pages opened: **NO**
- sealed/private/holdout tables inspected: **NO**
- datasets/dependencies accessed or downloaded: **NO**
- estimator/benchmark run: **NO**
- GitHub Actions run: **NO**
- paid resources used: **NO**
- competition submission: **NO**
- participant/organizer contact: **NO**
- main edit: **NO**
- PR edit/open: **NO**
- control edit: **NO**
- queue edit: **NO**
- report-only branch: **YES**
