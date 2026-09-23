# R276 Protocol — one distinct global V25 accuracy direction

- Job: R276
- Owner: `v25-accuracy-research`
- Dependencies: R209 COMPLETE, R273 COMPLETE.
- Control baseline: revision 341 / HEAD `ccbec8d84c45555c1ca57fcc798fb9cbdb612ae6`; live claim published later on revision 343 after a concurrent R275 queue update.
- Pinned V25 source: commit `dff3dd65e9d2210e02418cca99e05556f6bf2c75`, `methods/public_504aldo/estimator_v25.py` blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- Pinned development evidence: `research/results/R209-v25-mini100.json` blob `0183d0570f7c9965e00e8553ffc003c313865232`; panel `mini:all-100`, whestbench 0.16.1, flopscope 0.12.1+np2.4.6.
- Full-history evidence: `research/history.json` blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb` (194 E-IDs / 631 artifacts in the last complete full-history screen).
- Recent method evidence to deduplicate explicitly: R223 local-feed lambda, R227 SRM2, R232 DRRE, R238 RSRF, R244 MP-R16, R247 young-D21 right sparsification, R248 rank-1 Kronecker transport, R250 rank-1 Legendre AP, R251 GFNP, R252 D21-CWG/CFSP4, R260 BPK2K, R261 mean-correction-rider removal screen, R265 full-history accuracy screen, R269 randomized multilevel/depth-prefix telescope.
- New R273 constraint: R209 V25 error is broad-based rather than tail-dominated; any useful candidate must be one fixed global mechanism expected to move the central bulk, not a per-network selector.

## Decision gate before implementation

A candidate may be implemented/tested only if all are true before execution:

1. It is mechanistically distinct from the history families and recent R2xx lanes above.
2. It has a concrete global output rule, not a relabeling or a per-network selector.
3. There is a defensible mechanism signal/rationale before reading candidate mini-100 outcomes.
4. A production FLOP path can be honestly bounded under the pinned meter.
5. The same fixed configuration can be compared pairwise against V25 on the exact R209 mini:all-100 panel.

If no candidate survives these gates after the complete dedupe, R276 terminates with evidence-based NO-GO rather than inventing or renaming a method. In that case no estimator, mini-100, Actions, new data, tuning, paid/private/holdout/full, submission, leaderboard or canonical edit is authorized.

If one candidate survives, freeze its exact math/config and a bounded local execution plan before any mini-100 measurement. Preserve all attempts and publish a normalized result only if complete per-network MSE/adjusted-score/FLOP/failure rows are valid.
