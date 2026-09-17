# E103 Protocol — production-shape Haar-orthogonal antithetic sampler

Idempotency key: `ARC-E103-ORTHOGONAL-ANTITHETIC-PRODUCTION-SHAPE-20260918`

Status: **PREREGISTERED / LOCAL PRODUCTION-SHAPE ONLY**.

## Provenance

- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e103-orthogonal-antithetic-production-shape-20260918`.
- E100 authoritative protocol is the earlier collision winner:
  `e94a485b80a3e89bcb564dd43106727bea77450f`.
- E100 frozen Stage-A: run `35286592051`, job `105420177508`,
  artifact `10525165155`; orthogonal/iid MSE ratio
  `0.1883275202813626`, wins `8/8`, worst ratio
  `0.4780911047150302`, analytic utilization ceiling
  `0.06380971272801617`.
- E100 independent law/accounting review: run `35286924532`, job
  `105421199103`, artifact `10524278137`; review PASS. Gaussian marginal
  moments, Haar-row orthogonality, chi-radius moments, seed independence, and
  the analytic cost expression passed their frozen gates.
- E101 and E102 are independently occupied and are not modified.

## Single question

Can the **unchanged E100 sampling mechanism** be implemented through the local
estimator API at actual Phase-2 shape and remain finite and below the frozen
complete utilization ceiling under measured flopscope billing?

E103 is a packaging/cost falsifier. It does not evaluate competition accuracy.

## Frozen estimator

For width `n=1024`, depth `16`, total trajectories `N=4096`:

1. positive trajectories are generated in exactly two blocks of `n`;
2. per block draw a float64 iid Gaussian `G in R^(n x n)`;
3. compute QR and canonicalize columns by `sign(diag(R))`;
4. draw independent float64 radii with squared radius `chi-square(n)`;
5. form `r_i q_i`, cast the resulting block to float32;
6. append exact antithetic negatives;
7. propagate every trajectory through every zero-bias dense ReLU layer using
   the repository row-vector convention `h <- ReLU(h @ W)`;
8. return the float64 trajectory mean at every layer.

No covariance baseline, V29 state, learned coefficient, target, clipping,
jitter, shrinkage, rank selection, or adaptive sample count is present.

The production-shape synthetic MLP is frozen to:

- width `1024`;
- depth `16`;
- PCG64 weight seed `103103`;
- weights iid `N(0, 2/1024)`, float32;
- sampling seed `103104`;
- setup seed `103104`;
- no biases and no targets.

## Focused preflight

Before the full-shape job, tests must verify at small width:

- exact antithetic pairing;
- deterministic repeat;
- QR-row direction orthogonality;
- estimator output shape `(depth,width)`;
- finite output;
- row-vector orientation against a direct NumPy propagation;
- fixed sample count and divisibility rules.

No scientific network-MSE comparison is permitted in focused tests.

## Sole production-shape run

Exactly one workflow job after focused GREEN.

Required evidence:

- exact branch/head and implementation blob;
- width/depth/N;
- all outputs finite;
- output shape;
- flopscope `flops_used`;
- utilization `flops_used / 2**41`;
- analytic E100 ceiling `140319042219 / 2**41`;
- measured-minus-analytic delta;
- wall time;
- input marginal variance/fourth moment and antithetic-pair check, measured
  without reading any target.

## Frozen gates

All must pass:

1. width/depth exactly `1024/16`;
2. trajectories exactly `4096`;
3. finite output and correct `(16,1024)` shape;
4. exact antithetic pair max-abs `0`;
5. measured utilization `<=0.12`;
6. measured utilization `<=0.135`;
7. candidate input variance in `[0.95,1.05]`;
8. candidate input fourth moment in `[2.7,3.3]`;
9. no public/scorer/holdout/full/benchmark-label access.

A failed gate is **terminal E103 NO-GO**. No precision change, sample-count
change, QR change, block change, seed change, clipping, rescue, rerun, or
public diagnostic.

A pass is **PRODUCTION-SHAPE IMPLEMENTATION GO ONLY**. It does not establish
raw MSE <= `1.89e-8` and does not authorize public execution.

## Scope

No public/public-mini, official scorer, holdout/full, benchmark targets,
canonical mutation, ledger mutation, merge, or tuning.
