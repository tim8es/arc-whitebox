# E119 theory support — streaming activation-boundary sweep

Idempotency key: `ARC-E119-SUPPORT-STREAMING-BOUNDARY-SWEEP-20260919`

Status at freeze: **ONE SUPPORT RUN / OWNER E119 IDENTITY UNCHANGED**.

Branch:
`support/e119-streaming-boundary-sweep-20260919`.

Parent:
`research/e119-generic-boundary-flux-certificate-20260919@d731e845c96d401ac001da82c8998c06a03ec484`.

This is theory/implementation support for E119, not a replacement E119 result and
not a new benchmark candidate.

## Problem

Owner E119 proved that actual weight-driven boundary flux can be constructed
exactly for 2-D input, width<=8, depth<=4, but its constructor materializes the
entire final angular region list before forming scalar boundary flux.

The support question is whether the same scalar final observable can be
constructed **without a region tree or stored activation-mask state table**.

## Chosen option: event-driven streaming sweep

For a zero-bias ReLU network and an open angular region, every activation is

`h_l(theta) = A_l q(theta)`,
`q(theta)=(cos(theta),sin(theta))`,

with one current coefficient matrix `A_l` per layer.

At the current region, mechanically compute every current preactivation
coefficient

`P_l = W_l^T A_{l-1}`.

Each scalar preactivation is
`a cos(theta)+b sin(theta)`.
The next activation event is the smallest root strictly to the right of the
current angle among **all layers and neurons in the current affine state**.

The candidate then:

1. keeps only the current per-layer coefficient/mask state;
2. finds the next root;
3. emits the scalar final-observable derivative jump at that root;
4. adds the jump to a running flux sum;
5. recomputes the right-hand current state;
6. discards the left state and continues.

No region tree, list of masks, list of region coefficients, or fixture-specific
boundary angle is input to the candidate. A trace of emitted angles/jumps is
enabled only for verification; the scalar mean itself needs only the running
sum.

## Exactness theorem

Assume a nondegenerate sweep interval: all current preactivations are continuous
sinusoids and the next event is isolated.

If `theta_i` is the current event and the current masks are valid immediately
to its right, every preactivation keeps its sign until its first zero. Hence no
ReLU mask can change before the minimum positive root over all current
preactivations. Therefore the coefficient state remains valid on the entire
open interval to that minimum root, and that root is exactly the next network
activation boundary.

Recomputing all layers immediately to the right of the event gives the exact
next affine state. Induction over events therefore visits every angular region
once in cyclic order and emits exactly the E114 derivative jumps. The running
sum is consequently the exact E114 scalar boundary-flux mean.

This is an event sweep, not an activation-mask enumeration: memory is
`O(sum_l width_l)` coefficient/mask state and is independent of the number of
regions. Runtime remains linear in the number of encountered boundary events;
the theorem does **not** prove sublinear boundary-time complexity.

## Frozen numerical nondegeneracy rule

Floating implementation uses right probe
`PROBE = 2^-32` radians after each event.

The exact-reference partition is used only after candidate execution to verify
that the minimum true region width exceeds `64*PROBE`. Failure is an
instrument NO-GO; no probe change is allowed.

Candidate root deduplication tolerance remains the owner E119
`ROOT_TOL=2^-40`.

## Frozen corpus and observable

Reuse owner E119 unchanged:

- input dimension 2;
- width 8;
- depth 4;
- zero bias;
- iid He-normal float64;
- seeds `114200,114201,114202,114203`;
- scalar observable
  `c_j=(j+1)/sqrt(sum_{r=1}^8 r^2)`.

The independent reference is owner E119's full generic constructor and is not
available to the sweep while choosing events.

## Frozen measurements/gates

Per network record:

1. sweep event/region count;
2. independent owner-E119 region count;
3. max wrapped boundary-angle discrepancy;
4. max scalar-jump discrepancy;
5. sweep mean vs independent full mean;
6. minimum independent region width / `PROBE`;
7. deterministic replay;
8. peak candidate coefficient scalars and mask bits;
9. dense propagation FLOPs plus conservative geometry ledger.

PASS requires:

- finite candidate state;
- event count == reference region count;
- angle max error <=1e-10;
- jump max abs error <=1e-10;
- scalar mean abs error <=1e-10;
- minimum reference region width >=64*PROBE;
- deterministic replay exact;
- no target/public/scorer/holdout/full access.

## Verdict

If all gates pass:

**E119 THEORY SUPPORT GO — EXACT STREAMING BOUNDARY SWEEP.**

This establishes a generic non-tree construction with exact scalar flux and
boundary-count-independent memory. It does not solve boundary-count runtime
growth at production width/depth.

Any gate failure:

**E119 THEORY SUPPORT NO-GO — STREAMING SWEEP.**

Exactly one workflow execution. No seed/probe/tolerance/observable rescue,
tuning, rerun, canonical/ledger mutation, or merge.
