# E145 protocol — integrate E142 response-aligned old-D21 actions into pinned V25/V29

Idempotency key: `ARC-E145-V25-V29-RESPONSE-INTEGRATION-20260921`.

Status at freeze:

**PROTOCOL ONLY / PRE-CODE TERMINAL COST NO-GO / NO IMPLEMENTATION OR OWNER RUN AUTHORIZED.**

Branch:
`research/e145-v25-v29-response-integration-20260921`.

Parent:
`research/e142-response-aligned-old-d21-20260921@c8418babd468a8c2c6e214512dfed5ebd3a34ee2`.

## Goal

Integrate the E142 response-aligned residual statistic into the public V25/V29
old-D21 contraction interface while leaving all other public baseline arithmetic
unchanged.

The successor is deliberately stricter than E142:

- E142 proved only the contraction-interface sufficient statistic.
- E145 must account for the **entire** pinned baseline arithmetic, not just the
  E142 module.
- no public target, scorer, holdout or submission is permitted before a future
  independent verifier GO.
- no implementation or 1024x16 owner run is permitted unless the complete
  pre-code all-in cost gate passes.

The pre-code gate fails below, so E145 closes at protocol stage.

## Frozen public baseline identities

Public repository:

`504aldo/whest-p2-cumulant-k3`

Pinned upstream commit:

`18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Pinned files:

- V25 method baseline:
  `estimators/estimator_v25.py`
  git blob
  `195373a110215256b759d7c172ba8c923c62e5cc`;
- V29 live-cost baseline:
  `estimators/estimator_v29.py`
  git blob
  `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- V29 namespace audit:
  `docs/audit_v29_ns_d0.log`
  git blob
  `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`.

V29 is the production-cost host because it preserves V25 estimator arithmetic
while applying later public cost engineering. V25 remains the clean arithmetic
reference. If the cheaper V29 host cannot satisfy the cap, V25 cannot either.

## Frozen E142 identity

E142 receipt:

`research/E142_RECEIPT.json`

E142 final commit:

`c8418babd468a8c2c6e214512dfed5ebd3a34ee2`.

E142 established:

- exact residual action on adaptive `D S` and `D^T T` response directions;
- target-free queried-response certificate;
- target-free held-out orientation certificate;
- standalone response-module upper
  `225,462,175,744 FLOPs = 104.989006996 units`;
- no CountSketch, SMV, SVD recompression or norm-only residual replacement.

E142 explicitly did **not** establish a complete challenge-estimator cost.

## Allowed integration delta

E145 may replace only the public old-D21 shared-basis contraction family that
forms the full old-source D21 contribution for downstream use.

Public algebra:

`D_old = [sum LA FA^T + LP FP^T + nested lift] Qc^T`.

E142 replacement:

- preserve the existing V25/V29 source births, transports, age gates, shared
  basis, nested basis, K4 regeneration, D3 formula, D21 feedback rank,
  lambda rule and final-layer trim;
- preserve the same source factors and basis state;
- when a downstream consumer needs one of the frozen response actions, evaluate
  `D_old S` or `D_old^T T` directly from source factors using E142;
- do not hash columns;
- do not alter ranks;
- do not alter source windows;
- do not introduce a new K3 carrier;
- do not fit any coefficient to a target.

No public baseline arithmetic outside this old-D21 response substitution may be
changed under E145.

## Integration obstruction: V25/V29 still require the full D21 object elsewhere

The public V25 arithmetic uses the full D21 matrix for more than the rank-16
feedback range finder.

Examples in the pinned V25 source include:

- Wick scaling:
  `D21_w = d(w1)^2 D21 d(w1)`;
- formation of
  `rep21 = D21_w + D21_new`;
- nonlinear closure tables consuming both `d21` and `d21T`;
- diagnostics and subsequent layer state.

Therefore E142 response actions cannot replace all old-D21 computation while
leaving public arithmetic elsewhere unchanged.

There are only two admissible interpretations:

1. **strict arithmetic preservation**:
   keep the full public D21 materialization and add E142 response actions only
   for selected consumers. This cannot reduce the public all-in cost.

2. **replace the full D21 interface**:
   refactor all other D21 consumers to operate on response actions instead of
   the full matrix. That changes public arithmetic/dataflow outside the allowed
   E145 delta and is a new mechanism, not this integration.

E145 freezes interpretation 1 because the user requirement forbids changing
public baseline arithmetic elsewhere.

## Complete production all-in FLOP ledger

Competition budget:

`B = 2^41 = 2,199,023,255,552 FLOPs`.

Project production cap:

`0.135 B = 296,868,139,499 FLOPs`.

One public V29 namespace unit is

`2 n^3 = 2^31 = 2,147,483,648 FLOPs`

at `n=1024`.

The pinned steady-state V29 audit reports the following complete grouped
ledger:

| family | units |
|---|---:|
| K3 young dense sources | 115.61 |
| K3 old shared-basis tier | 106.83 |
| K3 thin / elementwise | 24.78 |
| covariance | 7.10 |
| birth / closure | 5.71 |
| other / untagged | 0.03 |
| **total** | **260.06** |

The log headline rounds this to `260.1 units = 0.2540 B`.

### Structural lower bound before any E142 work

Even granting a physically impossible **zero-cost deletion of the entire old
tier**, unchanged non-old V29 arithmetic is

`115.61 + 24.78 + 7.10 + 5.71 + 0.03 = 153.23 units`.

This is

approximately
`329,058,919,383 FLOPs = 0.149638671875 B`.

The cap is only `138.24 units`.

Thus unchanged non-old arithmetic exceeds the project cap by about

`14.99 units ~= 32.19 billion FLOPs`

before paying one FLOP for an old-source replacement.

Because the displayed source ledger is rounded to 0.01 units, even subtracting
a full 0.025 units as a conservative five-row rounding allowance gives
`153.205 units > 138.24 units`.

This lower bound alone is terminal.

### Strict E145 integration upper

Under the allowed delta, the public full-D21 state must still exist for Wick
scaling and nonlinear closure. Therefore E142 response actions are additive.

For an intentionally favorable accounting comparison, remove the public
`shared` contraction namespace only (`27.91 units`) and insert the entire
E142 module upper:

`C_E145 <=/about
  260.06 - 27.91 + 104.989006996
  = 337.139006996 units`.

That is approximately

`724,000,504,627 FLOPs`

or

`0.3292373115 B`.

This is already a favorable estimate because it credits E145 with removing the
entire public `shared` namespace even though strict arithmetic preservation
still needs a full D21 for other consumers.

### V25 host

Published V25 is approximately `0.3667 B`, strictly more expensive than V29
for the same estimator arithmetic. Since V29 fails, V25 fails a fortiori.

## Production admission gate

Required before implementation:

`complete all-in <= 0.135 B`.

Result:

**FAIL**.

The stronger zero-cost-replacement lower bound already gives

`unchanged non-old V29 > 0.135 B`.

Therefore no implementation can satisfy the frozen E145 contract without
changing baseline arithmetic outside the E142 contraction interface.

That would require a new experiment identity.

## Target-free exact-small gate — preregistered but not authorized to run

If the cost obstruction did not exist, E145 would use exactly two synthetic
integration fixtures:

### Fixture A

- width 32;
- depth 8;
- zero bias;
- deterministic He-Gaussian weights;
- seed `145032`;
- response rank `4`.

### Fixture B

- width 16;
- depth 8;
- dense adversarial rotation/gain construction;
- seed `145016`;
- response rank `4`.

For both fixtures:

1. execute unmodified pinned-baseline arithmetic with exact old D21;
2. execute the E145 integrated response path with no target/reference access;
3. only after the candidate state is frozen, materialize the exact old-D21
   verifier state;
4. compare the four adaptive response actions
   `D Omega`, `D^T Q1`, `D Z1`, `D^T Q2`;
5. compare reconstructed feedback products `Xt`, `Yt` and
   `D21_new`, using projector-aware comparisons where QR sign is irrelevant.

Frozen exact-small gates:

- every response relative Frobenius error <= `1e-12`;
- final feedback reconstructed-state relative error <= `1e-11`;
- deterministic replay bitwise exact;
- finite state;
- no target/reference access before candidate freeze;
- no public/scorer/holdout/full/submission access.

These gates are **UNEXECUTED_BY_PRE_CODE_COST_GATE**.

## Residual certificate — preregistered but not authorized to run

For every queried response direction, retain E142's exact algebraic certificate:

`B_query = 0`

in exact arithmetic because omitted residual action is evaluated directly.

For a held-out response `H`, let `V` span all queried right-response
directions and

`E = (I - V V^T) H`.

Use the E142 target-free orientation certificate

`B_orient(E) =
  sum_s ||L_s||_F ||F_s^T projected(E)||_F`

including both shared and nested tiers.

Required gate:

`||R E||_F <= B_orient(E) + 1e-12 * scale`.

The sourcewise orientation bound must also be no larger than the frozen
sourcewise norm-only comparator from the E142 erratum.

No exact target mean enters construction.

Certificate gate status:

**UNEXECUTED_BY_PRE_CODE_COST_GATE**.

## Frozen 1024x16-shaped owner run — conditional authorization only

Had the pre-code cost gate passed, E145 would permit exactly one Actions run:

- synthetic `1024 x 16` zero-bias MLP;
- deterministic seed `1451024`;
- no benchmark/public weights;
- no final target/reference mean;
- pinned V25/V29 blob verification before import;
- one BLAS thread;
- baseline arithmetic and E145 response actions in the same run;
- deterministic replay inside that one workflow execution;
- complete flopscope/all-in receipt;
- no rerun/rescue.

Because the production cost gate fails **before implementation**, this owner run
is **NOT AUTHORIZED**.

No workflow or run arm may be created under E145.

## Independent verifier / public firewall

Even if a future successor solves the all-in cost floor:

- owner synthetic GO is insufficient for public validation;
- an independent verifier must first confirm baseline blob identity, no target
  leakage, exact-small response equivalence, certificate validity,
  deterministic replay and complete all-in FLOPs;
- only after explicit verifier GO may a later protocol authorize public-mini or
  any target-bearing validation;
- official scorer, holdout, full suite and submission remain forbidden unless
  separately authorized.

## Decision

E145 result at protocol stage:

**TERMINAL PRE-CODE NO-GO — FULL V25/V29 INTEGRATION CANNOT MEET 0.135B
WHILE PUBLIC BASELINE ARITHMETIC ELSEWHERE IS FROZEN.**

Reason:

1. V29 is already the cheaper arithmetic-equivalent public host.
2. Its non-old arithmetic alone is about `0.1496 B > 0.135 B`.
3. E142 is only a contraction-interface sufficient statistic and does not
   remove that non-old floor.
4. Full D21 remains required by pinned V25/V29 arithmetic outside the rank-16
   response interface.
5. Any integration that removes those consumers or changes their
   representation is a new estimator mechanism and violates E145's frozen
   scope.

No implementation, tests, workflow, Actions run, public target read, scorer,
holdout/full execution, submission, canonical mutation or ledger mutation is
authorized under E145.
