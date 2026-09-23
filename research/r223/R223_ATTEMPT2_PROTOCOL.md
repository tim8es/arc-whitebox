# R223 attempt 2 — infrastructure repair protocol under RESEARCH_PROCESS v2

Date: 2026-09-23
Job: `R223`
Owner: `method-research`
Attempt identity: `R223-v25-local-feed-attempt2-20260923`

## Authority and preserved evidence

Current `AGENTS.md` and `research/RESEARCH_PROCESS.md` on `main` explicitly permit
repair of an `INFRA_ERROR` with a new versioned attempt under the same queue job.
This supersedes the older blanket no-repair language embedded in the 2026-09-22 R223
protocol.

Attempt 1 is immutable and remains `INFRA_ERROR`:

- queue run id: `R223-v25-isolated-improvement-20260922`;
- Actions run: `35786723402`;
- terminal receipt commit:
  `64b5fa1a2fed2a3f77021534875dbc7b0e2ff27f`;
- receipt SHA256:
  `cdc27cf6342639249ac6d0753c428e637f74d7085ea8cf152a29c91f5ddfa4ea`;
- no parent artifact download occurred in the workflow;
- `whest validate` did not start;
- no candidate mini-100 panel row exists.

Central repair event was published at revision `164`, control commit
`7cf81b9966eb2be4ed1c9516f57794a4f4d0fed8`.

## Scientific hypothesis is unchanged

Attempt 2 tests exactly the original frozen R223 mechanism:

**V25-LF normalized per-neuron K4→K3 feed-local lambda.**

The following are immutable from `research/r223/R223_PROTOCOL.md`:

- upstream V25 commit/blob;
- R209 parent artifact, hashes and 100-network panel;
- dataset/split/order;
- `K4→K3` feed-local formula;
- V25 scalar lambda transport;
- clamp `[0.5,2]`;
- normalization to mean-one feed scale;
- source/rank/age configuration;
- cost envelope;
- all scientific thresholds and paired gates;
- no parent rerun;
- no tuning or alternate candidate.

No formula, coefficient, clamp, panel, threshold, rank, seed, source state or comparison
rule changes in attempt 2.

## Exact repair scope

Only two infrastructure defects from attempt 1 are repaired.

### Repair A — provenance bootstrap

Attempt 1 placed the multiline parent-source replacement pattern inside a YAML block
scalar. YAML common-indent stripping altered the leading spaces in the runtime Python
triple-quoted pattern, so `p.count(old)==1` failed even though the pinned upstream blob
had already verified.

Attempt 2 moves this byte-transform verification into
`scripts/r223_verify_exact_transform.py`. The verifier is a normal Python source file,
so its multiline literals have stable source indentation independent of YAML parsing.

It must:

1. verify the pinned upstream V25 git blob;
2. reconstruct the candidate by applying exactly the preregistered two arithmetic edits
   plus the documentation line;
3. compare the reconstructed bytes to the committed candidate;
4. fail before artifact download / validation / panel if any byte differs;
5. emit parent/candidate SHA256 and git-blob identities.

### Repair B — docstring newline

The committed attempt-1 candidate contains one literal backslash-n sequence in the
documentation transition:

`... (V25, 2026-09-03).\n+ R223 ...`

Attempt 2 replaces only that literal two-character escape with an actual LF. No executable
token or arithmetic line changes.

## Pre-panel gates

All must pass before the 100-network panel:

1. repository visibility is public;
2. runner label is exactly standard `ubuntu-24.04`; no larger/self-hosted/paid runner;
3. pinned upstream commit and V25 git blob match;
4. repaired candidate equals the exact preregistered parent→candidate byte transform;
5. candidate executable arithmetic is unchanged from attempt 1;
6. static feed identity tests from attempt 1 pass;
7. exact R209 artifact ZIP and report hashes pass;
8. `whest validate` succeeds;
9. toolchain matches the frozen attempt-1 versions;
10. no target-dependent code path is introduced.

Failure of any gate before `whest run` finishes attempt 2 as exact `INFRA_ERROR`; no
panel run is started.

## Sole attempt-2 panel run

Only if every pre-panel gate passes:

`whest run --estimator methods/r223_estimator_v25_local_feed.py --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --streaming --n-mlps 100 --runner local --flop-budget 2199023255552 --wall-time-limit 120 --residual-wall-time-limit 0.4 --max-threads 1 --format json`

Parent is never rerun. Comparison uses only the verified R209 parent report.

Exactly one attempt-2 candidate panel invocation is permitted.

## Frozen scientific gates

Unchanged from attempt 1:

1. exact 100-name/order identity with parent;
2. identical dataset SHA;
3. candidate failures = 0;
4. mean raw MSE < `2.228303490170447e-8`;
5. mean adjusted score <= `8.129545452916639e-9`;
6. adjusted score improves on >=55/100 networks;
7. paired parent-candidate adjusted delta mean > `2*SE`;
8. candidate mean C/B <= parent C/B + `1e-5`;
9. max residual < `0.4 s`;
10. exact provenance gates pass;
11. no second attempt-2 candidate panel run.

A measured failure is `SCIENTIFIC_REJECT`. A fully passing result is a development GO
on this already exposed public mini-100 panel only.

## Forbidden

- R239 or any replacement job;
- rewriting attempt 1;
- parent rerun;
- candidate tuning;
- clamp/formula/panel/threshold changes;
- paid/larger runner;
- private/holdout/scorer/submission;
- canonical estimator mutation;
- leaderboard/rank claim.
