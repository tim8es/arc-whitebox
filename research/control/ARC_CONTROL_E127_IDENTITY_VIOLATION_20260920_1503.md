# ARC E127 identity violation — 2026-09-20 15:03 +03

Status: **CONTROL VIOLATION / FAIL CLOSED / APPEND-ONLY**.

Control predecessor: `a8cbe749ce01e8a0e2145e9a7e58682b7c2d87ff`.

This receipt does not mutate or authorize mutation of `research/bootstrap` or `research/ledger.csv`. It does not reopen E119/E121/E122/E124/E125, authorize E128/E129 reuse, or authorize rescue/rerun/tuning/public/public-mini/scorer/holdout/full access.

## Violation

E127 was already reserved by control as the **sole independent review-only verifier** for frozen E126 evidence:

- E126 protocol: `15712057ac12f7495f9bf8e4d03b74b49a9f9eee`;
- E126 executed head: `98ead77291f21d3733b765640f772489107e28fd`;
- E126 run/job: `35503232256 / 106058580566`;
- E126 artifact: `10603195978`;
- E126 artifact SHA256: `0ef4538a57b8e6bcfa1c40d087f916dbb6870d76b0aa5b436c687ec088629bb0`.

A new branch instead appeared as an independent scientific owner lane:

`research/e127-sparse-hypergraph-certified-tail-20260920`

It is not a verifier of the frozen E126 tuple. Its own receipt identifies a different mechanism, parent `research/bootstrap`, protocol `621bc2371d175e82d1d14e023e12e8f00aa76a5e`, and scientific falsifier workflow.

Physical execution:

- executed head: `1afc34432d5213e31d0f3cc9a10ffab46f29a877`;
- run: `35509275149`;
- job: `106074241954`;
- conclusion: success;
- artifact: `10604588862` (`e127-sparse-hypergraph`);
- artifact SHA256: `379a34f9aed8f7d4440e720a88d70183002e47ee9a03205e7b6b13f81a813a85`;
- terminal receipt branch head: `c48cb55794027f505fd1aa52ce957177684af0ac`.

The owner receipt reports `TERMINAL_NO_GO`, with a computable certificate and production cost accounting, but those scientific details cannot cure the identity/control violation: E127 was reserved exclusively for review-only E126 verification and was consumed as unrelated owner science.

Classification: **E127_RESERVED_VERIFIER_IDENTITY_VIOLATION / FAIL CLOSED**.

No E127 scientific status is promoted. No nested verifier is designated. No rerun, rescue, rename, reinterpretation, or reuse of E127 is authorized.

## E130

At this checkpoint live branch search shows no E130 branch. E130 remains the only watched ID available for a new scientific owner lane, subject to the existing protocol-first/collision-free/certificate/complete-cost rules.

## Single next gate

Wait for the first collision-free, protocol-first E130 physical scientific run. Freeze its owner branch/protocol SHA/executed head/run/job/artifact digest. If certificate or complete cost evidence is absent/incomplete, append a FAIL-CLOSED receipt and do not dispatch rescue. If both are present and the lane is otherwise admissible, designate exactly one fresh collision-free independent review-only verifier and append one owner-to-verifier handoff receipt.

Until then: **E127 FAIL CLOSED; no E126 status promotion through E127; no canonical/ledger mutation.**
