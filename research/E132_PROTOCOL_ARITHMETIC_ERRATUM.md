# E132 protocol arithmetic erratum — pre-run

Experiment:
`ARC-E132-LAYER-BORN-SOURCE-AGE-D21-20260920`.

Status:
**PRE-RUN ARITHMETIC CORRECTION ONLY. NO SCIENTIFIC PARAMETER OR GATE CHANGE.**

The protocol commit
`d12500820f153b15a5e71a642c9ddcba6b0ecb43`
correctly froze every production cost component, but the displayed final sum and
slack were added incorrectly.

The frozen component values are unchanged:

- RNG/materialization: `75,497,472`
- network propagation: `76,847,513,600`
- pilot D21 statistics: `8,100,249,600`
- source-age transport: `10,892,083,200`
- birth compression: `2,080,112,640`
- shared rebase: `3,568,926,720`
- nested rebase: `74,096,640`
- state reconstruction: `3,593,994,240`
- direction normalization: `6,291,456`
- direction Gram: `2,147,483,648`
- evaluation input projection: `4,294,967,296`
- low-rank D21 apply: `1,946,157,056`
- final D21 reconstruction: `486,539,264`
- rowwise rho work: `3,145,728`
- final correction: `4,311,744,512`
- certificate: `276,824,064`
- final reductions: `16,777,216`
- helper/accounting reserve: `2,000,000,000`

Their exact sum is:

`120,722,404,352 FLOPs`.

Against the frozen hard cap

`136,758,472,261`

the corrected slack is

`16,036,067,909 FLOPs`.

Therefore the pre-code/pre-run cost admission remains **PASS**.

This erratum changes none of:

- mechanism;
- pilot/evaluation counts;
- ranks;
- source-age thresholds;
- seeds;
- certificate;
- scientific gates;
- hard cap;
- run discipline.

It exists only so the executable and immutable receipt can reconcile exactly to
the frozen component ledger.

No Actions scientific run had occurred before this erratum.
