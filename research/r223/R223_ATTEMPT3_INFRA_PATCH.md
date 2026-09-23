# R223 attempt 3 — provenance-bootstrap patch only

Date: 2026-09-23
Job: `R223`
Owner: `method-research`

## Preserved attempts

Attempt 1 remains immutable `INFRA_ERROR` from the YAML multiline-source indentation
failure. Attempt 2 remains immutable `INFRA_ERROR` from a newly introduced bootstrap
version assertion. Neither attempt reached parent-artifact download, `whest validate`, or
the public mini-100 candidate panel.

Central control after attempt 2:

- finish attempt 2: revision `167`, commit
  `ba69d522784e10e4380b6c780dc4e49425da9f85`;
- infrastructure repair: revision `168`, commit
  `3097c095a2a14d8f9e4cdd713422a5f2cbab5d99`.

## Scientific protocol

The scientific protocol is unchanged and remains:

- `research/r223/R223_PROTOCOL.md`;
- `research/r223/R223_ATTEMPT2_PROTOCOL.md`.

No estimator source change is permitted in attempt 3. The current candidate blob must
remain exactly `a53f07513109abe24a58d91144cd202c19b77790`.

The K4→K3 feed-local lambda formula, V25 scalar lambda transport, clamp `[0.5,2]`,
mean-one normalization, source/rank/age state, R209 mini-100 panel, thresholds and
comparison logic are unchanged.

## Exact infrastructure patch

Attempt 2 installed the intended distributions successfully:

- `numpy-2.4.6`;
- `flopscope-0.12.1`;
- `whestbench-0.16.1`.

It then failed because the workflow asserted a module-level
`whestbench.__version__ == "0.16.1"`. Presence/value of that module attribute is not a
frozen R223 contract.

Attempt 3 changes only the provenance check:

- keep `whest version --json`;
- verify installed distribution versions with
  `importlib.metadata.version("whestbench") == "0.16.1"`;
- verify `importlib.metadata.version("flopscope") == "0.12.1"`;
- retain `numpy.__version__ == "2.4.6"`.

All subsequent source-transform, parent-artifact, validation, panel and scientific gates
remain byte-equivalent in intent to attempt 2.

## Run rule

If any pre-panel gate fails, finish this attempt as exact `INFRA_ERROR`.
If all gates pass, invoke exactly one candidate mini-100 panel run. Across R223 attempts,
no prior candidate panel invocation exists, so this remains within the user's
"at most one public mini-100 candidate test" limit.

No parent rerun, paid/larger runner, private/holdout, submission, canonical edit,
candidate tuning or leaderboard claim.
