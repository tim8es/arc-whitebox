# R299 — frozen coordinate-wise residual-energy diagnostic supplement

Status: **COMPLETE / ANALYZER_SUPPLEMENT_PREPARED_DELTA_TESTED_NO_REAL_CAPTURE**

Job: R299  
Owner: `r298-coordinate-energy-analysis-r269`  
Run: `R299-coordinate-energy-analysis-20260924`  
Isolated branch: `research/r299-coordinate-energy-analysis-20260924`  
Code commit: `0184099e1062065d0821d2a8f530882c52192d33`

## Scope

R299 closes the diagnostic omission identified after R298. R278 explicitly requires
“coordinate-wise residual energy explained by the fixed vector, summarized globally and
by central quantiles.” R298 implemented the frozen split, global FIT correction and
network-level MSE/materiality diagnostics but did not emit this coordinate diagnostic.

R299 is append-only: R298 files and receipt are unchanged. The R299 analyzer is a copy
of the exact R298 analyzer plus only the pre-data coordinate-energy supplement.

No real capture vectors were opened or analyzed. No estimator/benchmark/Actions run,
dependency/data download/install, paid resource, PR #36 edit, private/holdout/full
access, submission, leaderboard edit, or canonical edit occurred.

## Frozen inputs preserved

- R278 protocol commit `83dfbe710cad5fbb1cab6e5b6fce0ccd06d47966`,
  blob `0ccc6b20fb4a8ad1c62a95d98dea4681970bb97d`.
- R298 final artifact commit `6f1e96d07cbb22c243c76d19a49ff8b4e7dd19fb`.
- R298 analyzer source blob
  `f1d5a9da7872ff6e632fef1e6c7dd2c90a6091ea`.
- R298 receipt blob `277058cb85e3425d9ba911c6210fb9bfdd0dc564`.
- R278 split remains lexicographic decimal `network_id`, first 50 FIT / last 50 EVAL.
- R278 fit remains `d = mean_FIT(target-pred)`.
- R298 binary32 supplement remains unchanged for capture validation, fitting `d`,
  corrected predictions, corrected residuals, MSE, paired SD/SE and median.
- No alpha/rank/sign/coordinate/network tuning was added.

## Pre-data coordinate-energy definition

For each EVAL coordinate `k`, with the fixed FIT vector `d`:

`B_k = sum_i r_ik^2`

`C_k = sum_i (r_ik - d_k)^2`

`explained_k = 1 - C_k / B_k` when `B_k > 0`.

The implementation uses the already-decoded canonical binary32 residuals and the
binary32 fitted `d`. For `C_k`, each `r_ik-d_k` is rounded to binary32 before
squaring; the sums and ratios use Python binary64 `math.fsum`. This convention is
frozen before any real capture is inspected.

### Zero-energy semantics

If `B_k == 0`, `explained_k` is undefined and is emitted as JSON `null`.
That coordinate is excluded from the finite-coordinate count and central quantiles.
Its `C_k` is nevertheless included in the global numerator. Thus a fixed correction
that introduces energy into a previously zero-energy coordinate is not hidden.

If `sum_k B_k == 0`, the weighted global fraction is likewise undefined and emitted
as `null`.

The global energy-weighted diagnostic is:

`1 - sum_k C_k / sum_k B_k`

when the total baseline EVAL energy is positive.

The analyzer emits all 1024 `(B_k,C_k,explained_k)` records, finite-coordinate count,
zero-energy count, negative-explained count, total B/C and the weighted global fraction.

## Frozen quantile convention

Central summaries are p10/p25/p50/p75/p90 over **finite** `explained_k` values only.

Convention: Hyndman–Fan type 7 / linear interpolation. Sort `x`, set
`h=(n-1)p`, `j=floor(h)`, `gamma=h-j`, then
`Q(p)=x[j]+gamma*(x[j+1]-x[j])`, using zero-based indexing and the exact endpoint
when `j=n-1`. With no finite coordinates all five quantiles are `null`.

## Artifacts

`research/r299/r299_capture_analyzer.py`

- Git blob: `d8469b233f458dbe7813babdcfe21a82016664e1`
- SHA256: `f4ac7a72773c87221f12a182165b0145673285c879290b4fd6020d0840f83a51`

`research/r299/r299_capture_analyzer_selfcheck.py`

- Git blob: `03ebb9c9a1f7cba61cd199ac2b8b8066b1de466a`
- SHA256: `bd1556d21a6fc338ceea26240cde4885168093662d2bb24ca6d927d340f154d1`

The committed self-check retains all 13 R298 synthetic/integrity checks and adds six
R299 assertions: zero-energy coordinate/null handling, all-zero global/null handling,
negative explained energy, global weighting including a zero-energy penalty, exact
type-7 quantile examples, and presence of the coordinate-energy output block.

## Test evidence and execution boundary

The five new pure numerical edge semantics were evaluated in the available local Python
runtime without reading repository/data files: **5/5 PASS**.

- zero-energy coordinate: `B=0, C=2, explained=null`;
- all-zero case: `sum_B=sum_C=0`, global fraction and all quantiles `null`;
- negative explained case: `B=2, C=8, explained=-3`;
- weighted global includes the `C` penalty from the zero-energy coordinate;
- type-7 examples p10/p25/p50/p75/p90 for `[0,10,20,30]` equal
  `3, 7.5, 15, 22.5, 27` within absolute tolerance `1e-12`.

The complete committed 19-check integration self-check was **not executed** in this
session. Exact blocker: this connected session has GitHub read/write APIs but no
repository checkout/command runner; the local filesystem contains no checkout, and the
task explicitly prohibits downloads, so materializing the branch by clone/raw download
solely to execute the script would violate the task boundary. The R298 inherited
13-check self-check is already recorded PASS in the immutable R298 receipt; R299's new
test code is committed for execution by a later authorized checkout-capable offline
session if required.

## Classification

Output remains
`OFFLINE_DIAGNOSTIC_ONLY_NOT_OFFICIAL_ADJUSTED_SCORE`. Coordinate energy is descriptive
diagnostic evidence only. It does not infer an official adjusted score, leaderboard
rank, or authorize a benchmark/capture run.

## Disposition

**ANALYZER_SUPPLEMENT_PREPARED_DELTA_TESTED_NO_REAL_CAPTURE.**

The requested formulas, zero-energy behavior, weighted global fraction, finite count and
fixed central quantiles are now frozen before real vectors. The only residual execution
gap is the explicitly documented absence of a permitted checkout/command runner for the
full committed self-check.
