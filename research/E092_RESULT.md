# E092 result — terminal NO-GO / DROP

Idempotency key: `ARC-E092-FROZEN-RESIDUAL-CALIBRATOR-20260917`

## Provenance

- Branch: `research/e092-frozen-loo-residual-calibrator-20260917`.
- Direct canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Protocol-only first commit: `ff0d2602db84f0efc9cb4684fed5c54f170b6d98`.
- Pinned covariance baseline blob: `baselines/covariance_propagation.py@f547b378faa56e299559bcefc89909fd401b8026`.
- No public-mini, scorer, holdout or full-split target was accessed.

## TDD receipts

Focused RED tests commit: `4cfedf4dc274fc91974395ff5126674f7cd0bbfd`.

Primary RED workflow commit/run:

- workflow commit `5a78de265bc1d5817f31a8a814e75ce8866ea1c9`
- run `35158374284`
- job `105003106064`
- conclusion `failure`
- expected cause: `ModuleNotFoundError: No module named 'methods.e092_frozen_residual_calibrator'`

Control note: workflow trigger commit `e96821abff592da1e159813abbf76088341a868d` unintentionally caused a second pre-implementation RED push run `35158398511`. It contained no implementation, benchmark/public data, reference targets or scientific result and is not counted as independent evidence. No rerun API was used.

Implementation commit: `b69fca5a182155aa27c6625cca719b5826ea663d`.

GREEN engineering receipt:

- run `35158478283`
- job `105003442455`
- conclusion `success`
- focused E092 tests passed.

## Frozen scientific Stage-A

Driver commit: `15af340e38a942cf01e893a9715f3b9901fdf6e0`.

Sole scientific workflow commit: `4991583c8ba5238338b5835bc3a52e02dd58cfab`.

GitHub Actions:

- run `35158592837`
- job `105003811382`
- scientific step conclusion `failure` because one frozen GO gate failed
- artifact `10471719801`, name `e092-stage-a-receipt`
- artifact SHA-256 `7a1f3e70b0dbcd209acf490da10d71927477c9a6ba1d3d7b4d6d8bc2969ef9e3`

Frozen corpus:

- width `8`, depth `4`
- train seeds `92000..92015`
- held-out seeds `92100..92107`
- `32768` antithetic reference samples per MLP
- feature dimension `p=8`
- fixed ridge `lambda=1e-2`

## Metrics

Aggregate held-out final-layer MSE:

- covariance baseline: `4.4728507970714145e-04`
- calibrated: `3.497318993977423e-04`
- ratio: `0.7818993193931892`
- aggregate reduction: about `21.81%`

Robustness:

- held-out wins: `6/8`
- deterministic max abs diff: `0.0`
- coefficient L2 norm: `0.36397559003494406`
- conservative Phase-2 deploy correction upper bound: `17,891,392` FLOPs
- correction / `2**41`: `8.136063115671277e-06`

Per-network ratios `adjusted_mse / baseline_mse`:

- seed `92100`: `0.2996048737415177`
- seed `92101`: `0.6622421204322569`
- seed `92102`: `0.12070749357637493`
- seed `92103`: `0.5556591082462776`
- seed `92104`: `2.0297403186050618`
- seed `92105`: `3.0389112635144264`
- seed `92106`: `0.3401731999070267`
- seed `92107`: `0.38313979266733333`

## Frozen gate evaluation

PASS:

- finite outputs and coefficients
- deterministic repeat
- aggregate MSE ratio `<=0.95`
- at least `6/8` held-out wins
- coefficient norm `<=5`
- deploy correction fraction `<1e-5`
- no target/reference input to feature extraction/inference

FAIL:

- frozen worst-network degradation gate `<=1.25`; observed maximum `3.0389112635144264`.

The failure is material rather than numerical noise: two held-out networks regress by about `2.03x` and `3.04x` despite the strong aggregate improvement.

## Decision

**NO-GO / DROP.**

E092 demonstrates that a cheap target-free linear residual correction can capture a substantial shared covariance-closure error on this frozen synthetic distribution, but the correction is not uniformly stable across unseen networks. Under the preregistered terminal rule, E092 is closed: no feature change, lambda change, shrinkage/gating rescue, seed/sample change, rerun or public promotion is allowed in this lane.

A successor may use this only as negative/structural evidence: residual error has a learnable cross-network component, but a globally applied fitted correction lacks a reliable target-free trust criterion. Any successor must be a new independent mechanism rather than an E092 rescue/reparameterization.

No canonical/ledger mutation, merge, public-mini, holdout/full split, official scorer, tuning, sweep, rescue or scientific rerun was performed.
