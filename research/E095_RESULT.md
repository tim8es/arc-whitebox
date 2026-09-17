# E095 Result — terminal NO-GO / DROP

Idempotency key: `ARC-E095-OUTPUT-SUBSPACE-RESIDUAL-SAMPLING-20260917`

## Provenance

- Branch: `research/e095-output-subspace-residual-sampling-20260917`.
- Direct canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Frozen protocol commit: protocol/tests existed before implementation; RED-GREEN workflow head `9c12a70423c9285dcb2d0690d58ad13cefe8fadf`.
- Deterministic base: covariance propagation, canonical blob `f547b378faa56e299559bcefc89909fd401b8026`.
- No public/public-mini benchmark, official scorer, holdout/full split, benchmark labels, E092 fit, V29 state, canonical mutation, or ledger mutation was used.

## TDD receipts

Focused RED:

- run `35159072058`
- job `105005343700`
- conclusion `failure`
- expected cause: `ModuleNotFoundError: No module named 'methods.e095_output_subspace_sampling'`

Implementation:

- commit `3664bcd86af8e470934bcc83b80ba4ccbe8725c8`
- file `methods/e095_output_subspace_sampling.py`

Focused GREEN:

- run `35286148458`
- job `105418802649`
- conclusion `success`
- all frozen focused tests passed.

## Frozen Stage-A

Driver commit:

- `c584bf039d09c8d15554ab085c7948200d0300ae`

Sole scientific arm/workflow commit:

- `3cacb6f1a4e3a97dff5049e1524704b2d34f05f9`

GitHub Actions:

- run `35286260567`
- job `105419160491`
- final job conclusion `failure` because the frozen scientific terminal gate returned exit code 2
- artifact `e095-stage-a`, ID `10524346907`
- artifact ZIP SHA256 `b183571cadd1be26e555705134e3d85e6a72a44b480a13602949ffc55cbb5bcf`
- artifact size: `3105` bytes

Frozen corpus:

- width `32`
- depth `6`
- MLP seeds `95000..95007`
- high-sample antithetic reference: `65536`
- candidate/full-sample comparator: `2048`
- frozen target-free output-subspace rank: `6`

## Aggregate measurements

Final-layer aggregate MSE versus the frozen high-sample reference:

- covariance baseline: `1.9303277496159283e-03`
- ordinary 2048-sample mean: `1.3024242688774502e-04`
- E095 projected residual: `4.1918773734633493e-04`

Ratios:

- projected / covariance baseline: `0.2171588412536366`
- projected / ordinary full-sample mean: `3.2185190906157617`

Robustness and structural measurements:

- projected beats covariance baseline: `8/8`
- projected beats ordinary full-sample mean: `0/8`
- worst per-network projected / baseline ratio: `0.47159044692769136`
- mean oracle residual-energy capture by the frozen rank-6 subspace: `0.8137756235978275`
- residual-energy capture >= 0.50: `8/8`
- deterministic replay max abs diff: `0.0`
- all outputs finite: true

Per-network projected/full-sample ratios:

- seed 95000: `2.1401054752409494`
- seed 95001: `4.464019517907147`
- seed 95002: `17.029333436088756`
- seed 95003: `5.116343001543589`
- seed 95004: `2.346466243845592`
- seed 95005: `10.519537548399635`
- seed 95006: `2.3800173549911747`
- seed 95007: `1.587368511030748`

## Conservative Phase-2 cost upper bound

Frozen expression at width=1024, depth=16, N=4096, rank=6:

- covariance: `85,899,345,920`
- eigenspace/sign handling: `10,741,612,544`
- forward sampling: `137,573,171,200`
- reduction/projection: `16,824,320`
- total: `234,230,953,984`
- utilization / `2**41`: `0.10651590581983328`

The cost gate `<=0.12` passes.

## Frozen gate evaluation

PASS:

- finite outputs
- deterministic replay exactly zero
- projected / baseline <= 0.80
- projected beats baseline on >=6/8
- worst projected / baseline <=1.50
- mean oracle capture >=0.60
- capture >=0.50 on >=6/8
- conservative production utilization <=0.12

FAIL:

- projected / same-trajectory full-sample mean <=0.75: observed `3.2185190906157617`
- projected beats same-trajectory full-sample mean on >=6/8: observed `0/8`

## Interpretation

The target-free covariance eigenspace is genuinely aligned with most of the deterministic covariance-closure residual: it captures about 81.4% of oracle residual energy and the projected correction cuts covariance-baseline MSE by about 78.3%.

However, projection is the wrong use of the samples. The ordinary mean of the exact same 2048 trajectories is substantially more accurate on every frozen network. E095 discards sampled residual components outside the rank-6 subspace; those components contain enough true signal that the bias introduced by projection dominates any variance reduction.

This is a structural failure of the frozen mechanism, not a compute failure and not an isolated tail regression.

## Decision

**TERMINAL NO-GO / DROP E095.**

Under the preregistered rule there is no rank change, alternative subspace, sample-count change, seed change, shrinkage, blending, gating, learned selector, rescue, or scientific rerun under E095.

The reusable negative evidence is precise: a low-dimensional target-free output subspace can explain most covariance-closure bias, but hard projection of a finite-sample residual loses to using the complete same-sample mean. A successor must change the estimator architecture rather than retune E095; for example, it would need a principled control-variate or anisotropic sample-allocation identity that keeps the orthogonal sampled information instead of zeroing it.

No public/public-mini, official scorer, holdout/full split, tuning sweep, canonical mutation, ledger mutation, merge, or scientific rerun was performed.
