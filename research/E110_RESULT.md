# E110 terminal result — deep-Jacobian fourth-harmonic exact falsifier

Idempotency key: `ARC-E110-DEEP-JACOBIAN-H4-20260919`

Decision: **TERMINAL NO-GO / DROP at Stage S**  
Classification: **exact small admission blocker — degenerate frozen instance**.

## What was tested

E110 targeted a genuinely deep angular component rather than E108's first-layer transported mean error.

For each final output coordinate, E110 formed a direction from the complete mean-field Jacobian

`J=(0.5 W1.T)(0.5 W2.T)...(0.5 WL.T)`

and the exact-zero-mean spherical fourth harmonic

`z_j(q)=(q^T u_j)^4-3/(n(n+2))`.

At width 2, one Haar block is parameterized by one angle and the block-averaged control is exactly

`Z_j(theta)=cos(4(theta-phi_j))/8`.

The frozen falsifier recursively enumerated every ReLU angular sign sector and integrated the block mean/variance and harmonic covariance analytically.

## Frozen exact run

- width/depth: `2 / 4`
- weight seed: `110004`
- protocol: `d986b0b349f779ad13402faf5f4c28b0bf922972`
- implementation: `50b830f89ab0fbfd56fd5e1340f78504f1a9369f`
- tests: `a993aba0e19aa458bc6384c88c7eea786d216121`
- falsifier: `09d4d04fdae669398a5b25e39dba0c089eaaf62e`
- executed head: `ca5a6b7fe6692316a865c404efd70477aa7f04d8`
- run/job: `35453241091 / 105923933691`
- focused tests: `5 passed in 0.15s`
- no rerun.

Artifact: `e110-exact-falsifier`, ID `10587576340`, ZIP SHA256
`5ce947492ca3e01f82342b92b329e252e2c63a773afe7ec67a6d1364480fe9a1`.

## Exact evidence

The angular construction itself validated exactly to float64 precision:

- recursive final sectors: `6`
- Haar-block pieces: `4`
- direct-vs-sector max abs error: `0.0`
- direct-vs-block-piece max abs error: `0.0`
- quartic block formula max abs error: `3.400058012914542e-16`
- analytic control mean: exactly `0`.

But the frozen network is dead at the final layer over the **entire** input circle:

- output 0 exact block mean: `0.0`
- output 1 exact block mean: `0.0`
- output 0 exact Haar-block variance: `0.0`
- output 1 exact Haar-block variance: `0.0`.

Therefore `pooled_ratio = sum(Vres)/sum(Var(B))` is undefined because both numerator and denominator are zero. No output is nondegenerate.

## Admission consequence

The preregistered Stage-S gates required:

- all outputs nondegenerate;
- pooled residual ratio `<=0.50`;
- per-output residual ratio `<=0.80`.

The nondegeneracy gate fails and the variance-reduction gate is unevaluable. Under the frozen protocol this is terminal.

The conditional production cost estimate would have fit the budget (`~0.08623 < 0.13`), but **budget fit does not authorize production after scientific Stage-S admission fails**.

No production-shaped run was executed.

## Exact blocker

This result does **not** establish that the deep fourth-harmonic hypothesis is scientifically false. It establishes a stricter process blocker: the frozen exact falsifier instance contains no final-layer angular signal at all, so it cannot identify the mechanism.

Changing the seed/network after seeing this result would be a post-result rescue and is forbidden under E110.

E110 is therefore closed. Any future attempt must be a distinct experiment with nondegeneracy established before freezing the mechanism, not an E110 rerun.

No public/public-mini, benchmark targets, official scorer, holdout/full, tuning, sweep, canonical/ledger mutation, or merge occurred.
