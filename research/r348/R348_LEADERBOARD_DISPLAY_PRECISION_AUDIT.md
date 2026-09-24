# R348 — public leaderboard display precision / rounding primary-source audit

**Verdict: UNKNOWN — leaderboard formatter is not publicly evidenced.**

R348 is complementary to R341/R343. It is not a submission-method audit and does not inspect any competitor submission page.

Audit time: `2026-09-24T12:08:35Z`.

## 1. Dedupe

R341 preserves the current visible J2W rank-1 display text `2.00e-9` and Final Layer MSE `1.61e-8`, but explicitly does not infer exact unrounded scores.

R343 independently preserves the same `2.00e-9` text and explicitly records:

- exact underlying leaderboard float: `UNKNOWN`
- formatter/rounding interval: `UNKNOWN`

Neither R341 nor R343 performs a primary-source audit of the leaderboard renderer or round precision configuration. R348 therefore is not duplicate work.

Relevant committed evidence:

- R341 receipt blob: `2809f024b167cf28507540f7a113aba8d57af750`
- R343 report blob: `ca319b2a634dfb95a04b4ca351661fe3e1ca7fd0`
- R343 receipt blob: `5ae939e4344db9858c01a4422f21b06df39a71a4`

## 2. Exact question

For the current public leaderboard display text `2.00e-9`, determine from first-party public source whether it is:

- rounded,
- truncated,
- formatted by another rule,
- and, if evidenced, the exact display precision and valid interval for the underlying value.

Also determine whether the displayed Final Layer MSE has a known public formatter.

## 3. Official leaderboard page examined

Public route:

https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2

The public extractor available to this audit returns a client-side `Loading` shell rather than renderer/client source.

A search-indexed AIcrowd rendering exposes leaderboard values, but a rendered value is not evidence of the transformation that produced it. R348 therefore does not infer a formatting rule from `2.00e-9`, `1.61e-8`, or any other displayed example.

No submission page was opened.

## 4. AIcrowd platform first-party precision setting

First-party AIcrowd design/admin documentation:

https://design.aicrowd.com/pages/edit-challenge-rounds-admin

The leaderboard round configuration publicly documents:

- **Primary Score → Score Precision**
- description: **"Round off precision to compute ranks"**
- **Secondary Score → Secondary Score Precision**
- same rank-computation purpose

This establishes that AIcrowd has a per-round score-precision setting used in ranking.

It does **not** establish:

1. the Phase-2 value of that setting for this challenge;
2. whether the setting also controls the displayed string;
3. whether scientific notation uses fixed decimal places, significant figures, truncation, round-half-even, round-half-away, or another rule;
4. the formatter for "Other Score(s)" columns such as the displayed Final Layer MSE.

No public challenge-specific Phase-2 precision value was found.

## 5. Public AIcrowd source-code search

Public code under the official GitHub organization `AIcrowd` was searched for likely web-formatting implementations.

Results:

- `toExponential org:AIcrowd`: **1** result, only in `AIcrowd/whestbench-explorer`
- `toPrecision org:AIcrowd`: **0**
- `"score_format" org:AIcrowd`: **0**
- `toFixed leaderboard org:AIcrowd`: **0**
- `"formatNumber" leaderboard org:AIcrowd`: **0**
- `"formatScore" org:AIcrowd`: **0**
- `"scorePrecision" org:AIcrowd`: **0**

Searches for exact challenge column labels did not surface a public platform frontend:

- `"ADJUSTED SCORE" org:AIcrowd`: scorer/docs references, no leaderboard renderer
- `"FINAL LAYER MSE" org:AIcrowd`: scoring source reference, no leaderboard renderer

The sole public `toExponential` hit is:

- repo: `AIcrowd/whestbench-explorer`
- commit: `fb400159666b5bd45a2c22040e6a9daebc6b764c`
- file: `src/components/EstimatorComparison.jsx`
- blob: `ed8ca96a0f3617bb91272ffb23bfbfb041f6e0bd`
- URL:
  https://github.com/AIcrowd/whestbench-explorer/blob/fb400159666b5bd45a2c22040e6a9daebc6b764c/src/components/EstimatorComparison.jsx

That separate explorer application uses its own display rules (`toExponential(1)` for one plot label and `toExponential(4)` for its MSE formatter). It is not the AIcrowd challenge leaderboard renderer and provides no evidence for leaderboard precision.

## 6. WhestBench local presentation formatter — explicitly not leaderboard evidence

Official WhestBench public source:

- repo: `AIcrowd/whestbench`
- commit: `4794ce8673c1221bdb245b19e933ae0afd7ffa3c`
- file: `src/whestbench/presentation/adapters.py`
- blob: `bc92da337db234b598303dda96e3da470e126e4e`
- URL:
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/presentation/adapters.py

The local report helper `_display_mse_value` states that MSE-style values are shown in scientific notation with three significant figures and implements:

`f"{float(value):.2e}"`

That helper is used by the WhestBench **local report/presentation layer** for Adjusted Final-Layer Score and Raw Final-Layer MSE.

Official participant docs likewise show locally rendered report examples such as `9.10e-02`:

- repo: `AIcrowd/whest-starterkit`
- commit: `5eb9aa1455fcb3216af55994bdf25dc242b95797`
- file: `docs/getting-started/stage-3-run-local.md`
- blob: `2bc23fd23210f513a9bfab4917dde6f4ef18c125`

However, no first-party source found by R348 links this WhestBench local presentation helper to the AIcrowd web leaderboard renderer.

Therefore it is **not valid** to conclude that the web leaderboard uses Python `.2e` merely because current web values visually resemble that output.

## 7. Metric semantics are public; display semantics are not

Official score-field documentation establishes the underlying metric names and meanings:

- `adjusted_final_layer_score`: leaderboard metric
- `final_layer_mse`: raw diagnostic

Pinned public file:

- `AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c`
- `docs/reference/score-report-fields.md`
- blob: `3b66b33a0775f01eecbda2a148495d471f2eff65`

The documentation does not specify the AIcrowd web leaderboard numeric renderer, scientific-notation threshold, significant-digit count, decimal-place count, or tie behavior for display rounding.

## 8. Conclusions for current displayed values

### Adjusted Score `2.00e-9`

Observed display text: **known**.

Underlying exact float: **UNKNOWN**.

Leaderboard formatter: **UNKNOWN**.

Rounded vs truncated vs other: **UNKNOWN**.

General significant-digit rule: **UNKNOWN**.

General decimal precision rule: **UNKNOWN**.

Mathematically valid underlying interval implied by the leaderboard formatter: **UNKNOWN / not derivable from public evidence**.

R348 intentionally does **not** emit an interval such as one based on hypothetical `.2e` formatting, because the task requires an interval only when that leaderboard formatter is evidenced.

The lexical string `2.00e-9` itself contains three significant digits, but that fact does not prove a general three-significant-digit formatter.

### Final Layer MSE

Known public metric semantics: **YES**.

Known AIcrowd leaderboard display formatter: **NO / UNKNOWN**.

The current display `1.61e-8` likewise cannot establish rounding mode or a valid underlying interval.

## 9. Primary-source verdict

**UNKNOWN_FORMATTER_NOT_PUBLICLY_OBSERVABLE.**

First-party public evidence establishes:

1. the score/MSE metric semantics;
2. a generic AIcrowd per-round "Score Precision" control whose stated purpose is rounding for rank computation;
3. a separate WhestBench local-report formatter using `.2e`.

First-party public evidence does **not** establish:

1. the Phase-2 challenge's configured Score Precision value;
2. the web leaderboard renderer implementation;
3. whether web display formatting is the same as WhestBench local-report formatting;
4. whether `2.00e-9` is rounded, truncated, or transformed by another formatter;
5. a valid numerical interval for its exact underlying value;
6. the web formatter for Final Layer MSE.

R341/R343 remain separate immutable artifacts. No estimator measurement is added or revised by R348.

## Execution accounting

- competitor submission pages opened: **0**
- estimator/model runs: **0**
- benchmark runs: **0**
- data/dependency downloads: **0**
- GitHub Actions: **0**
- private/sealed/holdout access: **NO**
- competition submissions: **0**
- method inference: **NO**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
