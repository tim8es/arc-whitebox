# ARC E122 → E126 independent verifier handoff — 2026-09-20 02:38 +03

Control predecessor: `56bfe604cb3af50a755608bf151e2ba737b3c0ce`.

Status: **APPEND-ONLY CONTROL HANDOFF / E126 DESIGNATED / FAIL-CLOSED UNTIL RECEIPT**.

This receipt does not mutate or authorize mutation of `research/bootstrap` or `research/ledger.csv`. It does not promote E122 scientific status and does not authorize a rerun, rescue, tuning, candidate substitution, public/public-mini/scorer/holdout/full access, or any E119/E121/E128 reuse.

## Frozen E122 owner evidence

The only owner evidence admitted for this handoff remains exactly:

- experiment: `E122`;
- owner branch: `research/e122-haar8-antipodal-simplex-source-code-20260920`;
- protocol SHA: `fd2f2d93ed7be6124cd70485b561177c3b2787ad`;
- executed head: `6c175236e578149c3d6ce6493a008a613c8883f1`;
- Actions run: `35473392719`;
- job: `105978326828`;
- artifact: `10593646150` (`e122-haar8-simplex-falsifier`);
- artifact SHA256: `0c80738a83e2d996ad3c6cf75b2b206402d916cc52d9b0b548dfb121ad34cb44`.

No later E122 owner commit may replace the executed candidate for verification.

## Why E125 is not admissible for this handoff

A branch named `review/e125-arc-baseline-cost-verifier-20260920` already existed at commit `8230d7a23496f631c250970d6f07acab4ca04f3d`, timestamp `2026-09-19T22:24:09Z`, before the qualifying E122 run was created at `2026-09-19T22:27:40Z`. Its checkpoint explicitly reported E122 protocol/candidate absent and was therefore a pre-trigger reservation/checkpoint, not a verifier identity designated from the frozen E122 run evidence.

Under the standing rule that the verifier must be designated immediately from the first qualifying fresh owner run, E125 is consumed/premature for this handoff and is fail-closed. E123 remains consumed/premature and E124 remains collided as recorded by predecessor control receipt `56bfe604cb3af50a755608bf151e2ba737b3c0ce`.

## Sole verifier designation

**E126 is hereby designated as the one independent review-only verifier identity for frozen E122 evidence.**

At designation time, branch search found no E126 branch. E127 also had no branch. E126 is therefore collision-free at this control checkpoint.

E126 may only inspect/recompute from the immutable frozen E122 protocol/executed-head/run/job/artifact tuple above. It must not modify, substitute, rerun, rescue, tune, or regenerate the E122 candidate.

Required verifier gates:

1. protocol-first ancestry and executed-head identity are independently reconciled;
2. artifact digest matches the frozen SHA256;
3. target/oracle firewall is checked: no benchmark/public/scorer/holdout/full targets and no exact-reference/oracle state consumed before candidate materialization;
4. deterministic evidence/replay claims are checked only from frozen owner evidence; no new owner scientific run is permitted;
5. exact candidate-vs-reference error/certificate arithmetic is independently recomputed where the artifact permits it;
6. production all-in FLOP accounting is independently reconciled against the preregistered cap, including helper/RNG/geometry/materialization charges where applicable;
7. verifier emits one immutable append-only E126 receipt with exact inputs, calculations, decision, and any artifact/hash provenance.

A verifier workflow or branch name alone is not evidence. E126 scientific/control verification status remains **PENDING / FAIL-CLOSED** until a physical verifier receipt exists.

## Single next gate

**Obtain exactly one E126 review-only verifier receipt pinned to the frozen E122 tuple above.**

Until that receipt exists: E122 status promotion remains blocked; E123/E125 are not admissible for this handoff; both E124 lanes remain fail-closed; canonical/ledger mutation remains forbidden.
