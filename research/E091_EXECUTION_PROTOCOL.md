# E091 executable readiness/falsifier extension

Idempotency key: `ARC-E091-READINESS-20260916`

This file extends the already-committed protocol without modifying it or its append-only readiness receipt. It authorizes one **synthetic-only** executable falsifier sequence: focused RED, implementation, GREEN, then exactly one bounded diagnostic. It does not authorize public-mini, scorer, holdout, full-suite, tuning, sweep, canonical mutation, or ledger mutation.

## Frozen exact identity

For fixed target-independent `X`, fixed `lambda > 0`, residual targets `Z`,

`A = X.T @ X + lambda I`, `B = A^{-1} X.T Z`, `h_i = x_i.T A^{-1} x_i`, `e_i = z_i - x_i.T B`.

The row-wise omitted prediction is

`zhat_i^(-i) = x_i.T B - h_i e_i / (1-h_i) = (zhat_i - h_i z_i)/(1-h_i)`.

It must equal the direct refit

`x_i.T (X_-i.T X_-i + lambda I)^{-1} X_-i.T Z_-i`

for every row. The executable parity gate is `max_abs <= 1e-12` and relative Frobenius `<= 1e-12` in float64. Require `min_i(1-h_i) >= 1e-6`; fail closed with no clipping, jitter, pseudoinverse, or rescue.

## Frozen minimal small-network counterexample

No repository dataset or benchmark target is read. One deterministic tiny bias-free ReLU network is fixed:

`W1 = [[1.0,-0.5],[-0.25,0.75],[0.6,0.4]]`

`W2 = [[0.8,-0.3,0.5],[-0.4,0.7,0.2]]`

and seven fixed inputs:

`[[-1.0,-0.5],[-0.75,0.25],[-0.25,1.0],[0.25,-1.0],[0.5,0.75],[1.0,-0.25],[1.25,0.5]]`.

The base output is `b(u) = W2 @ relu(W1 @ u)`.

The target-free feature row is frozen as

`x(u) = [1, u0, u1, u0^2 + u1^2]`, so `p=4`.

Synthetic residual truth is generated independently of fitting as

`z1(u)=0.15 + 0.20 u0 - 0.10 u1 + 0.05 u0 u1`,

`z2(u)=-0.10 + 0.10 u0 + 0.15 u1 - 0.04 u0^2`,

and `y=b+z`. Ridge `lambda=1.0` is frozen.

Counterexample row is zero-based `i=3`. Perturb **only** that row's residual target by `delta=[7,-5]`.

The falsifier must demonstrate both:

- naive full-fit prediction at row 3 is self-target-sensitive: perturbation changes it by `>=1e-2` max absolute;
- exact LOO prediction at row 3 is self-target-invariant: perturbation changes it by `<=1e-12` max absolute.

This is the minimal executable counterexample to treating in-sample ridge residual fit as leakage-free.

## Frozen signed-influence gates

For each omitted row define explicit signed influence weights on retained targets

`w_ij = x_i.T (X_-i.T X_-i + lambda I)^{-1} x_j`, `j != i`,

so `zhat_i^(-i) = sum_{j!=i} w_ij z_j`.

Record all row-wise signed diagnostics and require:

- `max_i sum_j |w_ij| <= 4.0`;
- `max_i sum_j max(-w_ij,0) <= 1.5`;
- `max_{i,j} |w_ij| <= 2.0`;
- `max_abs(zhat_LOO) <= 4 * max_abs(Z)`;
- all weights/predictions finite.

These are stability/falsifier gates only; passing them is not an accuracy claim.

## Frozen cost gates

The deployable correction is one dense `x @ B` only. LOO calculations are offline and are forbidden at benchmark/scorer inference.

For a dense dot with `p` features and `q` outputs, count `(2p-1)q` scalar multiply/add FLOPs and also report the conservative `2pq` ceiling.

At the Phase-2 readiness cap `p=16`, `q=16384`, `B_phase2=2^41` require:

- exact dense-dot count `(2*16-1)*16384 = 507,904` FLOPs;
- conservative ceiling `2*16*16384 = 524,288` FLOPs;
- conservative budget fraction `<= 2.5e-7`;
- coefficient state `16*16384*4 = 1,048,576` bytes for float32 `B` (`<=1 MiB`);
- no inference-time matrix inverse, factorization, LOO loop, target access, or corpus lookup.

The bounded synthetic diagnostic must also report its own `p`, `q`, exact dense-dot count, conservative ceiling, and coefficient bytes.

## Execution order and terminal rule

1. Commit this protocol extension first.
2. Commit focused tests/workflow while implementation is absent; obtain actual RED.
3. Implement only the frozen algebra/counterexample; obtain actual GREEN.
4. Arm and execute exactly one synthetic bounded diagnostic; no public data.
5. Append a new immutable receipt line containing commit/run/job/artifact identifiers, observed metrics, gate booleans, and terminal readiness decision. Never alter or replace earlier receipt lines.

Any identity, leakage, leverage, signed-stability, cost, finite, or determinism gate failure => `READINESS NO-GO`. No rescue/rerun/tuning under E091.