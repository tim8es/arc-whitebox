# R211 — protocol-first falsifier for exact contraction-DAG CSE/reassociation

Date: 2026-09-22
Idempotency: `ARC-R211-EXACT-DAG-CSE-REASSOC-20260922`
Branch: `research/r211-exact-dag-cse-reassociation-20260922`
Parent: R206 terminal branch `research/r206-ta-rank-sweep-20260922`.

## Scope

R211 tests exactly one graph-level mechanism proposed by R206:

> preserve every semantic V29/H185 contraction and leaf matrix-multiplication kernel,
> but eliminate exact duplicate contraction nodes and legally reassociate matrix chains
> before execution.

This is **not**:

- another TA/LITA rank sweep;
- a different bilinear matrix-multiplication scheme;
- a compiler implementation;
- K3/D21 compression;
- approximation, sketching, truncation, source dropping, or rank tuning.

Leaf matmul implementations and their billed cost are frozen to the parent. R211 may
only alter the contraction DAG above those leaves.

No holdout, paid resources, scorer, submission, leaderboard mutation, canonical mutation,
or scientific rerun is authorized.

## Primary source pin

Public V29:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Relevant primary files:

- `estimators/estimator_v29.py`;
- `docs/audit_v29_ns_d0.log`;
- `docs/findings_log.md`.

Frozen source-resolution F86 ledger inherited through E187/R206:

- young_transport = 60.71 u;
- hub = 54.90 u;
- dense K3 total = 222.44 u;
- fixed non-dense remainder = 37.62 u;
- project mechanism gate = 0.42;
- all-in cap = 138.24 u = 0.135 B.

Unit: `u = 2*1024^3` FLOPs.

## Frozen exact-small identities

The first admissible CSE/reassociation opportunity class is the one already represented
by the V29 young/hub batching structure.

For arbitrary conformable matrices over any ring:

[
W[A\;P] = [WA\;WP].
]

For hub-style source aggregation:

[
[X_1\;X_2][Y_1\;Y_2]^T
= X_1Y_1^T + X_2Y_2^T.
]

These identities permit exact batching/concatenation, but do not reduce the scalar
bilinear work of the underlying independent products. They only change DAG packaging and,
for the hub identity, can remove at most explicit output-accumulation additions.

Frozen 2x2 integer witness:

[
W=\begin{bmatrix}1&2\\3&4\end{bmatrix},;
A=\begin{bmatrix}2&-1\\0&3\end{bmatrix},;
P=\begin{bmatrix}1&4\\-2&1\end{bmatrix}.
]

Then

[
WA=\begin{bmatrix}2&5\\6&9\end{bmatrix},quad
WP=\begin{bmatrix}-3&6\\-5&16\end{bmatrix},
]

and

[
W[A\;P]=
\begin{bmatrix}
2&5&-3&6\\
6&9&-5&16
\end{bmatrix}.
]

For

[
X_1=\begin{bmatrix}1&0\\2&1\end{bmatrix},;
X_2=\begin{bmatrix}0&1\\1&-1\end{bmatrix},;
Y_1=\begin{bmatrix}2&1\\-1&3\end{bmatrix},;
Y_2=\begin{bmatrix}1&-2\\2&0\end{bmatrix},
]

both hub forms equal

[
\begin{bmatrix}0&-1\\8&3\end{bmatrix}.
]

Exact-small equality is therefore frozen before any execution.

## Why young_transport and hub are irreducible under R211

### young_transport

Pinned V29 already groups the common left operand `W` against multiple independent
right-hand leg matrices through one batched Strassen family. At the contraction-DAG level,
each required output is a binary semantic product `W @ leg_s`. Concatenating right
operands changes packaging but not the number of independent bilinear leaf products.
There is no third operand to reassociate and no duplicate right operand to eliminate.

### hub

Pinned V29 hub computes

[
H = sum_s X_sY_s^T
]

as a batched product family followed by source reduction. Concatenating the source blocks
into one wide product is exactly the second identity above. Under the frozen leaf-kernel
cost model it does not reduce the bilinear product work; at most it removes explicit
source-sum additions, which are below the leaf and are conservatively allowed to become
free in the lower-bound proof below.

Thus R211 grants the optimizer **all non-leaf work in these two namespaces for free** and
still retains their frozen binary leaf costs as unavoidable. This is intentionally
favorable to the candidate.

## Conservative production lower bound

The exact CSE/reassociation class cannot alter the unique binary leaf products in
`young_transport` and `hub`.

Even granting every other dense K3 namespace zero cost, and granting all explicit
batching/reduction/copy overhead inside these two namespaces zero cost, the frozen
source-resolution lower-bound envelope is bounded below by their parent leaf families:

[
C_{floor} = 60.71u + 54.90u = 115.61u.
]

Against the full dense K3 denominator:

[
r_{floor} = 115.61 / 222.44
          = 0.5197356590541269.
]

Frozen gate:

[
r_{floor} \le 0.42.
]

Result:

[
0.5197356590541269 > 0.42.
]

The gap is

[
115.61u - 0.42(222.44u)
= 22.1852u.
]

This is a conservative NO-GO: all old-source dense work, all join products, all thin work,
all covariance/closure work, integration overhead, materialization and runtime overhead are
treated as free.

The lower bound is specific to the R211 mechanism class, where leaf matrix multiplication
algorithms remain frozen. It is not a universal arithmetic-complexity lower bound.

## Float32 gate

If and only if the production lower bound had passed, the sole synthetic candidate would
have been required to satisfy, against the same float64 reference:

- relative-Frobenius candidate/parent float32 error <= 1.05;
- max-absolute candidate/parent float32 error <= 1.05;
- exact-small integer identity = exact;
- deterministic replay.

Because the cost lower bound fails before candidate execution, the float32 gate is
**NOT AUTHORIZED / NOT EVALUATED**. No synthetic run may be performed merely to measure a
mechanism that is already structurally over the frozen cost gate.

## Decision

`TERMINAL_NO_GO_COST_LOWER_BOUND`.

No compiler is built and no minimal synthetic numerical run is authorized after the
pre-execution structural cost failure.
