# E104 Protocol — accounting-complete Haar-orthogonal antithetic sampler

Idempotency key: `ARC-E104-ORTHOGONAL-ANTITHETIC-COMPLETE-BILLING-20260918`

Status: **PREREGISTERED / LOCAL PRODUCTION-SHAPE ACCOUNTING ONLY**.

## Provenance and non-duplication

- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e104-orthogonal-antithetic-complete-billing-20260918`.
- E100 authoritative orthogonal-antithetic lane established the unchanged sampling law and synthetic variance-reduction evidence.
- E103 implemented that same law at production shape and executed once, but its estimator generated Gaussian and chi-square random values through plain NumPy before wrapping them in flopscope arrays. E103 accounting reconciliation commit `051e4f391fe86bac93949bb67788160ccbc26ce0` seals E103 and forbids rerun.
- E104 is **not a new scientific sampler** and is not an E103 rerun. It is the first accounting-complete package execution of the already-frozen law.
- E101/E102/E103 are occupied; E104 branch/commit/issue/PR collision surfaces were checked clean before branch creation.
- No public/public-mini, official scorer, holdout/full, benchmark labels, target fitting, canonical mutation, ledger mutation, or merge is authorized.

## Frozen mechanism

Keep exactly the E103 production-shape mechanism:

- width `W=1024`;
- depth `D=16`;
- trajectories `N=4096`;
- exactly two positive blocks of size `W`;
- per block draw a float64 iid Gaussian `G in R^(W x W)`;
- compute `Q,R = qr(G)`;
- canonicalize Q columns by `sign(diag(R))`, with zeros mapped to +1;
- draw `W` independent float64 radii with squared radius `chi-square(W)`;
- form `r_i q_i`, cast the positive block to float32;
- concatenate both positive blocks and exact antithetic negatives;
- row-vector forward propagation `h <- ReLU(h @ W_layer)` through all 16 zero-bias layers;
- return float64 trajectory means for **all** layers.

Frozen synthetic production-shape network:

- PCG64 weight seed `103103`;
- weights iid `N(0,2/1024)`, float32;
- sampling/setup seed `103104`;
- no biases, no targets.

No sample-count/rank/block/seed/precision/QR/sign/radius-law change is allowed.

## Sole implementation change relative to E103

In the estimator's billed path only:

- replace plain `np.random.Generator(...).standard_normal` with `fnp.random.default_rng(seed).standard_normal`;
- replace plain NumPy `chisquare` with the corresponding `fnp.random.Generator.chisquare`;
- do not generate a numeric random value outside flopscope inside `predict`;
- all QR/sign/sqrt/scaling/casts/matmul/ReLU/reductions remain flopscope operations.

Plain NumPy is allowed only outside `predict` for test/reference diagnostics and synthetic MLP construction supplied to the estimator.

## Frozen accounting cross-check

E103 reported:

- `149047446192` flopscope FLOPs;
- utilization `0.0677789313122048`.

Known unbilled E103 RNG work under the flopscope 0.12.x model:

- Gaussian draws: `2 * 1024^2 * 32 = 67108864`;
- chi-square draws: `2 * 1024 * 32 = 65536`;
- exact expected added bill: `67174400`.

If all non-RNG arithmetic is unchanged, expected E104 total is therefore:

`149114620592` FLOPs,

utilization

`0.06780947869265219`.

This exact expectation is a consistency check, not permission to hand-adjust the measured counter.

## Focused preflight

Before the sole production-shape run, local focused tests must verify:

1. at small width, flopscope RNG and NumPy reference generators with the same frozen PCG64 seed produce equal generated antithetic samples;
2. exact antithetic pairing;
3. QR-row direction orthogonality;
4. deterministic repeat;
5. row-vector estimator output equals direct NumPy propagation at small shape;
6. no plain `np.random` numeric draw occurs in the billed generator;
7. under `BudgetContext`, replacing the reference NumPy draws by flopscope draws increases the measured bill by exactly the frozen random-draw cost for the small test shape.

Focused tests are implementation/accounting checks only; no network target or scientific accuracy comparison is allowed.

## Sole production-shape run

Exactly one production-shape workflow execution after focused GREEN.

Record:

- branch/head and method blob;
- run/job/artifact IDs and artifact digest;
- width/depth/N and frozen seeds;
- prediction shape and finite state;
- exact antithetic pairing and target-free input variance/fourth moment;
- `BudgetContext.flops_used`;
- utilization `flops_used / 2^41`;
- measured minus E103 reported FLOPs;
- difference from expected `67174400` RNG delta;
- wall time.

## Frozen gates

All must pass:

1. shape exactly `(16,1024)`;
2. trajectories exactly `4096`;
3. output finite;
4. exact antithetic pair max abs `0`;
5. input variance in `[0.95,1.05]`;
6. input fourth moment in `[2.7,3.3]`;
7. measured FLOPs `>=149114620592`;
8. measured FLOPs `<=151000000000`;
9. measured utilization `<=0.12`;
10. measured utilization `<=0.135`;
11. measured-minus-E103 FLOPs exactly `67174400`;
12. no targets/public/scorer/holdout/full access.

A failed gate => **terminal E104 implementation/accounting NO-GO**. No rerun, rescue, sampler change, sample-count change, precision change, seed change, or alternate billing workaround under E104.

A pass => **ACCOUNTING-COMPLETE PRODUCTION-SHAPE GO ONLY**. It does not establish raw MSE `<=1.89e-8`, does not establish adjusted score, and does not authorize public execution.

`scientific_go = false` for every E104 outcome because no production/public accuracy is measured.
