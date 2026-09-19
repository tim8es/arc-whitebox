# ARC E122+ control violation receipt — 2026-09-20 01:33 +03

Control predecessor: `0549cfe0cc6f784ae9c018d27751fe942be17aa5`.

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL VIOLATION**.

This receipt does not mutate or authorize mutation of `research/bootstrap` or `research/ledger.csv`. It does not promote any scientific status.

## Fresh evidence after watermark 35464849858

A fresh E122 scientific lane appeared:

- owner branch: `research/e122-haar8-antipodal-simplex-source-code-20260920`;
- protocol commit: `fd2f2d93ed7be6124cd70485b561177c3b2787ad` (`research(E122): preregister Haar-8 simplex source-code falsifier`), parent `e2c7473a2919b4444daa581b14d1ed706960f7d8`;
- protocol is implementation-level and freezes mechanism, deterministic fixtures/seeds, same-node comparator, all-in FLOP cap/gates, target-access exclusions, one-run/no-rescue discipline, and terminal kill rule;
- implementation/workflow commits follow the protocol commit;
- executed head: `6c175236e578149c3d6ce6493a008a613c8883f1`;
- Actions run: `35473392719`;
- job: `105978326828`;
- run conclusion: `failure`; the scientific falsifier step failed while evidence upload succeeded;
- artifact: `10593646150`, `e122-haar8-simplex-falsifier`;
- artifact digest: `sha256:0c80738a83e2d996ad3c6cf75b2b206402d916cc52d9b0b548dfb121ad34cb44`.

The owner later sealed a terminal receipt at branch head `f55989ba441b7527569713b0249ffed65d1a03af`; this control receipt does not independently promote that status until verifier admissibility is resolved.

## Control violations / collisions

### V1 — verifier dispatched before the qualifying owner run

`research/e123-independent-multisource-verifier-20260920` executed run `35473330106` at `2026-09-19T22:26:19Z`, before E122 owner run `35473392719` was created at `2026-09-19T22:27:40Z`.

A later E123 verification run `35473558089` exists on head `631d0ef45e466d55ee5a77406261eca28cd81571`, but the E123 identity was already consumed by pre-run verifier activity. Under the standing control rule, this is not a clean post-trigger verifier designation.

Classification: **PREMATURE_VERIFIER_IDENTITY / FAIL CLOSED**.

### V2 — E124 collision

Two distinct E124 scientific branches/runs exist after baseline:

- `research/e124-walsh-coset-source-interactions-20260920`, run `35473373186`, executed head `617333d829ba2076524228ca1e08c3e1a51ceccc`, conclusion `failure`;
- `research/e124-chowliu-gate-amplitude-cluster-20260920`, run `35473469592`, executed head `430f32b270a843ecdc8580864abbf6cc14b96b9f`, conclusion `success`.

Classification: **E124_ID_COLLISION / FAIL CLOSED**. Neither E124 lane may be promoted under the collision-free rule.

## Frozen owner evidence

For control purposes, the first qualifying post-baseline owner evidence is frozen as:

`E122 / research/e122-haar8-antipodal-simplex-source-code-20260920 / protocol fd2f2d93ed7be6124cd70485b561177c3b2787ad / executed head 6c175236e578149c3d6ce6493a008a613c8883f1 / run 35473392719 / job 105978326828 / artifact 10593646150 / sha256 0c80738a83e2d996ad3c6cf75b2b206402d916cc52d9b0b548dfb121ad34cb44`.

## Exactly one next verifier gate

Do **not** rerun/rescue/tune E122 and do not reuse collided E123 or E124 identities.

The only admissible next control action is to allocate a fresh collision-free E125+ review-only verifier identity, protocol/receipt first, pinned exactly to the frozen E122 executed evidence above. It may inspect/recompute from the immutable owner evidence but must not modify, substitute, rerun, rescue, or tune the E122 candidate. No canonical/ledger mutation is authorized.

Until that fresh verifier receipt exists: **E122 STATUS PROMOTION BLOCKED; E123/E124 FAIL-CLOSED FOR THIS HANDOFF.**
