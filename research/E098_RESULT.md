# E098 Result — terminal NO-GO / DROP

Idempotency key: `ARC-E098-LATE-K22-RESPONSE-RELEVANCE-20260918`

## Provenance

- Branch: `research/e098-late-k22-response-relevance-20260918`.
- Direct canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Protocol-only first commit: `ad1c75864dfe3134831293267a478320453cb098`.
- Frozen Stage-A implementation commit: `1990a6eb37ee8ec8d54ab07782e3c770eac5342d`.
- Sole workflow-trigger commit: `fa1e1215295cf70ff8f4fb737280d071b1d7d5ad`.
- No public/public-mini benchmark, official scorer, holdout/full split, benchmark target, canonical mutation, ledger mutation, or merge was performed.

## Sole frozen Stage-A evidence

GitHub Actions:

- run: `35286416596`
- job: `105419636891`
- run attempt: `1`
- scientific step conclusion: `failure` because preregistered scientific gates failed
- artifact: `e098-stage-a`
- artifact ID: `10524312158`
- artifact ZIP SHA-256: `b5c444599b46a25ad9a3ce4d440e773bb0c31103eb79402c293f4f9b5943d9a9`
- artifact size: `1937` bytes

The script wrote the complete receipt before exiting with code 2. Artifact upload succeeded. This is a scientific gate failure, not a setup/import/execution failure.

Frozen corpus:

- width `128`, depth `6`
- network seeds `98098, 98198, 98298`
- moment input seeds `198098, 198198, 198298`
- reference input seeds `298098, 298198, 298298`
- moment samples `32768` per network
- independent reference samples `32768` per network
- source layers `3,4`
- rank exactly `8`

## Aggregate measurements

Gaussian one-step base:

- MSE: `3.1351378338590815e-05`

Full-K22 oracle response:

- MSE: `3.23435842551638e-05`
- full/base ratio: `1.0316479200964401`

Rank-8 K22 candidate:

- MSE: `3.266196583354136e-05`
- rank8/base ratio: `1.0418031858375212`
- wins over Gaussian base: `2/6`
- worst per-observation rank8/base ratio: `1.127425032308415`

Representation quality:

- median rank-8 K22 captured energy: `0.8344107137731287`
- worst rank-8 K22 captured energy: `0.747632004990741`
- deterministic repeat scalar max abs: `0.0`

Static cost envelope:

- response FLOPs: `21,135,360`
- response fraction of `2**41`: `9.611248970031738e-06`
- two-late-transition envelope FLOPs: `111,476,736`
- fraction of `2**41`: `5.0693750381469727e-05`

## Frozen gate evaluation

PASS:

- all six observations finite and signal-eligible
- minimum preactivation sigma `>1e-10`
- median rank-8 K22 energy `>=0.82`
- worst rank-8 K22 energy `>=0.70`
- worst rank8/base MSE ratio `<=1.35`
- deterministic replay `<=1e-12`
- response cost fraction `<1e-5`
- two-late cost fraction `<1e-4`

FAIL:

- aggregate rank8/base MSE `<=0.90`: observed `1.0418031858375212`
- aggregate full/base MSE `<=0.90`: observed `1.0316479200964401`
- rank-8 response wins on at least `4/6`: observed `2/6`

Per-observation rank8/base ratios:

- seed `98098`, layer `3->4`: `1.0546375068114775`
- seed `98098`, layer `4->5`: `1.127425032308415`
- seed `98198`, layer `3->4`: `1.059131675627456`
- seed `98198`, layer `4->5`: `1.0452906079463564`
- seed `98298`, layer `3->4`: `0.9626291395487956`
- seed `98298`, layer `4->5`: `0.9471295513695017`

## Interpretation

The **late-layer low-rank representation premise itself survived** the frozen test: median/worst captured energy and static cost gates passed.

The tested fixed analytic response did not. Both the full K22 oracle term and the rank-8 approximation increased aggregate one-step MSE relative to the Gaussian moment-matched base. Therefore the failure cannot be attributed to rank-8 truncation alone: even the full measured K22 slice has the wrong net effect under this preregistered fourth-order Edgeworth response.

This closes the specific mechanism class **late-layer K22 -> fixed scalar fourth-order Edgeworth ReLU-mean correction**. It does not establish that all possible uses of K22 are useless, but any alternative response, sign, damping, learned mapping, layer choice, or propagation law would be a new experiment and may not be introduced as an E098 rescue.

## Decision

**E098 = terminal NO-GO / DROP.**

No rank change, source-layer change, seed/sample change, sign flip, damping, fitted scalar, alternative Edgeworth response, rerun, rescue, public diagnostic, scorer, holdout/full access, canonical/ledger mutation, or merge is authorized under E098.

`scientific_go = false`.
