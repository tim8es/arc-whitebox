# ARC control evidence change — E122 fresh run / E124 namespace collision

Recorded: 2026-09-20 01:32 +03

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL**.

This note does not authorize scientific execution, rerun/rescue/tuning, public/public-mini/scorer/holdout/full access, merge, canonical mutation, or ledger mutation.

## E122 — first qualifying fresh owner run observed

Owner branch: `research/e122-haar8-antipodal-simplex-source-code-20260920`.

Fresh terminal owner tip: `f55989ba441b7527569713b0249ffed65d1a03af` (`research(E122): seal terminal Haar-8 simplex receipt`). The receipt records protocol-only commit `fd2f2d93ed7be6124cd70485b561177c3b2787ad`, implementation `3853efd5177f6931c7dcf884dd97f7342751ca03`, tests `c733af8f3b179c9c9ef8314abc136b2ff6a7940b`, falsifier `4b861d4137adc3abe95123882bcc05f6861c385b`, workflow `f5543dba3087df5371f4be1cf1cc84beeb66adac`, executed arm `6c175236e578149c3d6ce6493a008a613c8883f1`, candidate source SHA256 `8ad7cc902c756ad2582ad70ffb87dbc6d6aade6d2e8577f5dff445ef67be8ef6`.

Physical Actions evidence: run `35473392719`, job `105978326828`, attempt 1, head `6c175236e578149c3d6ce6493a008a613c8883f1`. Workflow conclusion is `failure`; the sole frozen falsifier step failed while evidence upload succeeded. Artifact `10593646150` (`e122-haar8-simplex-falsifier`) has digest `sha256:0c80738a83e2d996ad3c6cf75b2b206402d916cc52d9b0b548dfb121ad34cb44`.

The terminal receipt reports strong variance reduction versus IID but does **not** establish production/competition GO: 8-D pooled candidate MSE `8.810347464996878e-7` and candidate/IID `0.008425074397522755`; 16-D pooled candidate MSE `4.239163838762134e-6` and candidate/IID `0.20844147732086804`. Both remain far above raw `1.89e-8` (`46.6156x` and `224.2944x`). Production all-in upper is `135,554,463,424` FLOPs against cap `136,758,472,261`, slack `1,204,008,837`; however the frozen numerical gate fails because max frame orthogonality error `1.0707087565186895e-11` exceeds `2e-12`. Therefore E122 is terminal NO-GO, not a positive successor gate.

A later independent-verifier workflow exists as run `35473558089` on `research/e123-independent-multisource-verifier-20260920`, head `631d0ef45e466d55ee5a77406261eca28cd81571`, conclusion `success`. A successful verifier workflow does not override the owner terminal failure.

## E124 — namespace collision

Live branch state contains **two incompatible scientific identities using E124**:

1. `research/e124-walsh-coset-source-interactions-20260920`, terminal tip `c677b8778e3c7d8c0422609b3cb3351d8c06b2d2` (`record terminal one-shot serialization failure receipt`).
2. `research/e124-chowliu-gate-amplitude-cluster-20260920`, terminal tip `feb9d723e4e44aa745525ea14da4a5661132724f` (`record terminal Chow-Liu cluster result`), with physical workflow run `35473469592`, executed head `430f32b270a843ecdc8580864abbf6cc14b96b9f`, conclusion `success`.

Because the collision exists as durable branch/receipt identity, **neither E124 lane is admissible as a collision-free successor identity**, regardless of workflow success or terminal prose. No E124 GO may be recognized.

E119 remains terminally closed and its sole authoritative scientific execution remains run `35458020001` / job `105936659806` / artifact `10589345345` / SHA256 `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`.

## Exactly one bounded correction

**Quarantine E124 as permanently collided and require the next scientific mechanism to re-key to the next live-verified unused E-ID (currently E129 is branch/content-search clear) with a protocol-only first commit before any implementation or workflow execution.**

No scientific workflow is dispatched by this control action; canonical and `research/ledger.csv` remain untouched.