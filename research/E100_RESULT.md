# E100 Result — terminal NO-GO / DROP

Idempotency key: `ARC-E100-CROSSFIT-TWO-SUBSPACE-SHRINKAGE-20260918`

## Provenance

- Branch: `research/e100-crossfit-two-subspace-shrinkage-20260918`.
- Direct canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Protocol freeze commit: `d113433552638818688516f9c8d0526ecbd51341`.
- Deterministic covariance base blob: `f547b378faa56e299559bcefc89909fd401b8026`.
- E095 is terminal and immutable. E100 retained both rank-6 covariance-subspace and orthogonal sampled residual components and used target-free cross-fitted positive-part shrinkage; it did not reuse E095 hard projection or E092 fitted coefficients.
- No public/public-mini benchmark, official scorer, holdout/full split, benchmark labels, V29 state, canonical mutation, or ledger mutation was used.

## TDD receipts

Focused RED tests commit:

- `cf0d80a0ad8aade55d2f9ff0bd3b1658ba842773`

Focused RED workflow commit:

- `a929af05ffa76da64a184610e3d73ce4bacf9c82`

Actual RED:

- run `35286600530`
- job `105420202461`
- conclusion `failure`
- expected cause: `ModuleNotFoundError: No module named 'methods.e100_crossfit_shrinkage'`

Implementation:

- commit `5847f598fa71668bcce17f9b84c5751ee71dbcf4`
- file `methods/e100_crossfit_shrinkage.py`

Focused GREEN:

- run `35286682480`
- job `105420450744`
- conclusion `success`
- all frozen focused tests passed.

## Frozen Stage-A

Driver commit:

- `e25a83f3d7bb2425a1f8a1d7b8d4b332d4fc59a0`

Sole scientific arm/workflow commit:

- `d26b531d81f82e91ac35cb193b0b15b191235650`

GitHub Actions:

- run `35286776056`
- job `105420738303`
- final job conclusion `failure` because the frozen scientific terminal gate returned exit code 2
- scientific computation step completed successfully before the terminal gate
- artifact `e100-stage-a`, ID `10525205404`
- artifact ZIP SHA256 `d755b0f6ddfa13c49b3a5b25f43ad0e5fd9f3286f13bfa3060828aef332ce279`
- artifact JSON SHA256 `5d16dc36f2d7ca3554ce24a344a911d1ff57dc6be62f9823db2e7c735be7274c`
- artifact ZIP size `4350` bytes
- extracted JSON size `7086` bytes

Frozen corpus:

- width `32`
- depth `6`
- network seeds `100000..100007`
- high-sample antithetic reference: `65536`
- candidate/full-sample comparator: `2048`
- covariance subspace rank: `6`
- pair-preserving deterministic A/B cross-fit split

## Aggregate measurements

Final-layer aggregate MSE versus the frozen high-sample reference:

- covariance baseline: `1.5536096525349315e-03`
- ordinary same-trajectory 2048-sample mean: `9.909795588160482e-05`
- E100 cross-fit shrinkage: `1.7727576979762293e-04`

Ratios:

- E100 / covariance baseline: `0.1141057340293765`
- E100 / ordinary full-sample mean: `1.7888943139192437`

Robustness and mechanism activity:

- E100 beats ordinary full-sample mean: `3/8`
- worst per-network E100/full-sample ratio: `2.9102251513425457`
- networks with at least one frozen shrink coefficient <0.99: `8/8`
- all coefficients remained in `[0,1]`
- deterministic replay max abs diff: `0.0`
- all outputs finite: true

Per-network E100/full-sample ratios:

- seed `100000`: `2.295197466116762`
- seed `100001`: `2.25746642250437`
- seed `100002`: `2.1289338328301732`
- seed `100003`: `2.9102251513425457`
- seed `100004`: `0.6575821073195974`
- seed `100005`: `0.35684903340770463`
- seed `100006`: `0.40329212457861086`
- seed `100007`: `2.6938694320876717`

## Conservative Phase-2 cost upper bound

Frozen width=1024, depth=16, N=4096, rank=6 expression:

- covariance: `85,899,345,920`
- eigenspace/sign handling: `10,741,612,544`
- forward sampling: `137,573,171,200`
- split/group statistics + cross-fit: `251,801,600`
- total: `234,465,931,264`
- utilization / `2**41`: `0.10662276111543179`

The frozen cost gate `<=0.12` passes.

## Frozen gate evaluation

PASS:

- all finite
- deterministic replay exactly zero
- E100 / covariance baseline <=0.20
- all coefficients in [0,1]
- mechanism active on >=4/8 networks (observed 8/8)
- conservative production utilization <=0.12

FAIL:

- aggregate E100 / full-sample <=0.95: observed `1.7888943139192437`
- beats full sample >=6/8: observed `3/8`
- worst E100/full-sample <=1.25: observed `2.9102251513425457`

## Interpretation

The frozen positive-part two-group shrinkage is active and substantially improves the deterministic covariance baseline, but its target-free noise-energy estimate does not provide a reliable risk advantage over simply retaining the complete same-trajectory sample mean. The failure is broad: five of eight networks regress against the full mean and the worst regression is about 2.91x.

E095 established that hard projection loses useful orthogonal sampled signal. E100 establishes that the tested cross-fitted positive-part shrinkage rule does not recover a stable advantage: estimating groupwise shrink from the same finite sampling regime introduces enough coefficient error and/or bias to erase the theoretical scalar-shrink headroom.

This is an accuracy/stability failure, not a compute failure.

## Decision

**TERMINAL NO-GO / DROP E100.**

No coefficient-formula change, alternate split, rank/sample/seed change, clipping change, pooled coefficient, tuning, rescue, scientific rerun, public diagnostic, holdout/full, or scorer is allowed under E100.

Reusable evidence: the covariance baseline supplies a strong low-dimensional bias direction, but neither hard projection (E095) nor this target-free groupwise plug-in shrinkage (E100) beats the full same-trajectory sample mean robustly. A future sampling successor must gain efficiency without estimating unstable per-network shrink factors from the candidate sample itself; it should use an exact unbiased identity, deterministic variance reduction, or an independently computable control variate.

No public/public-mini, official scorer, holdout/full split, tuning sweep, canonical mutation, ledger mutation, merge, or scientific rerun was performed.
