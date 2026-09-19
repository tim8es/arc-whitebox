# E104 Benchmark-Owner Successor Protocol — one-shot mini0 raw-MSE gate

Idempotency key: `ARC-E104-BENCHMARK-OWNER-MINI0-20260919`

Status: **PREREGISTERED / EXACTLY ONE TARGET-BEARING DIRECT-METRIC RUN AUTHORIZED, NOT EXECUTED**.

## Why this successor exists

The authoritative E104 branch `research/e104-haar-radial-raoblackwell-20260918`
currently ends at `d8e06c806d18b1ccd1405648cf990e0b32d5762f`.
Its original protocol is synthetic-only and explicitly authorizes no public run.
The owner-side blocker receipt `research/E104_E051_BENCHMARK_BLOCKER_RECEIPT.json`
and independent verifier receipt both record that E104 raw benchmark MSE,
benchmark FLOPs/utilization, and benchmark failures are **UNEXECUTED** and that
an explicit successor protocol is required before reading the E051 target.

This document is that minimal successor. It changes evaluation authorization
only. It does not tune or change the E104 estimator law.

## Frozen evidence entering this gate

- E104 Stage-A local scientific GO: protocol commit
  `f85ce2487ae953f20b611b327d2269f1c54548fc`.
- Independent synthetic production-shape verification:
  run `35446062235`, job `105905067035`, artifact `10584569066`;
  measured E104 FLOPs `149047442096`, utilization
  `0.06777892944955966`, finite and deterministic.
- Owner benchmark blocker: raw competition MSE remains UNEXECUTED.
- Supplemental target-free transfer evidence is non-authorizing:
  branch `research/e104-target-free-transfer-20260919` head
  `4d7d3bdf8713f3ae5b7250b8fdbfeaf851b4659b`.
- Supplemental target-free variance evidence is non-authorizing:
  branch `research/e104-error-estimator-probe-20260919` head
  `e42758dda587b7a10a6fadaa614f96236ef1bf2a`.

## Exactly authorized target access

Exactly one future workflow execution may read exactly:

- dataset: `aicrowd/arc-whestbench-public-2026`
- revision: `v2-phase2`
- split: `mini`
- record index: `0`
- target field: `row["final_means"]`

This is the same target-bearing benchmark record previously used by E051.
The run is a direct metric calculation only. **Official scorer, public sweep,
other public records, holdout, full suite, target fitting, and any second run
are not authorized.**

Creating this protocol, the frozen benchmark script/workflow, and the
authorization receipt does not consume the one run because none of those steps
read the target.

## Frozen E104 benchmark estimator

For the single record:

- require width `1024`, depth `16`;
- total trajectories `4096`;
- positive directions `2048` in exactly two `1024 x 1024` Haar-QR blocks;
- direction RNG seed `104105`, fixed before target access;
- float64 Gaussian QR with diagonal-sign canonicalization, zero sign -> +1;
- radius is analytic `E[chi_1024]`; no random radii;
- exact antithetic negatives;
- float32 trajectory propagation;
- float64 per-layer means;
- official WhestBench weight orientation: `h <- ReLU(h @ w)` for each
  `w in mlp.weights`;
- budget `2**41`.

The use of `h @ w` is the canonical WhestBench MLP convention. Earlier
synthetic E104 verification used iid generated matrices with a transpose;
for iid square Gaussian matrices that did not change the synthetic law, but
the benchmark adapter must follow the actual benchmark MLP orientation.

For benchmark cost accounting, Gaussian direction draws are made through
`flopscope.numpy.random` so RNG work is billed. This is an accounting
completion only; it does not change the frozen Gaussian/Haar sampling law.

## Frozen measurements

The one execution must persist:

- final-layer raw MSE against `final_means`;
- prediction FLOPs;
- metric FLOPs;
- all-in FLOPs = prediction FLOPs + metric FLOPs;
- utilization = all-in FLOPs / `2**41`;
- failures;
- finite state;
- prediction shape and SHA256;
- exact antithetic input-pair error;
- dataset/revision/split/index;
- workflow run/job/artifact identity and digest in the immutable follow-up receipt.

No all-layer target metric is required because the E051 benchmark provenance
did not freeze an all-layer target tensor for this record.

## Frozen gates

Competition-promotion evidence requires all of:

1. target record shape is width/depth `1024/16`;
2. prediction shape is exactly `(16,1024)`;
3. output finite;
4. exact antithetic input-pair max abs `== 0`;
5. failures `== 0`;
6. raw final-layer MSE `<= 1.89e-8`;
7. utilization `<= 0.135`.

A failed scientific or cost gate is a measured E104 benchmark **NO-GO**.
There is no rerun, rescue, seed change, sample-count change, threshold change,
tuning, sweep, alternate record, or second target read under this idempotency key.

A pass establishes only this frozen mini0 benchmark gate. It does not authorize
holdout/full evaluation or official scoring.

## One-shot arming rule

The workflow is intentionally triggered only when the previously absent file
`research/E104_BENCHMARK_RUN_ARM.json` is created on branch
`research/e104-benchmark-owner-successor-20260919`.

The arm file must contain this idempotency key and the authorization-receipt
commit SHA. The workflow verifies that commit is an ancestor and that its
receipt status is `AUTHORIZED_NOT_EXECUTED` before target access.

The authorization receipt records the exact one-shot `gh api` creation
command. Reissuing that command without the current file SHA fails rather than
creating a second arm commit.

## Mutation boundary

No canonical, ledger, public scorer, holdout/full, or submission mutation is
authorized by this successor.
