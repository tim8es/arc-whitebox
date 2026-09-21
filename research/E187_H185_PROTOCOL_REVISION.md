# E187 H185 PROTOCOL HARDENING — append-only revision

Date: 2026-09-22  
Branch: `research/e187-h185-protocol-hardening-20260922`  
Parent review: E186 `89b514fff8c1e7e48a8bb3fc8e542984a84ba045`  
Original hypothesis: E185/H185 `10f5f0ab41da70b0661f44596f23f9e7f182ec11`  
Mode: **PROTOCOL HARDENING ONLY — NO IMPLEMENTATION CODE, NO SCIENTIFIC RUN**  
Decision: **PROTOCOL NO-GO / OWNER RUN NOT AUTHORIZED**

## Scope and machine-readable authority

This is append-only. E185 and E186 are untouched and H185 is unchanged: preserve the full V29 state and D21/K3 arithmetic, changing only the exact bilinear schedule.

Normative companions:
- `research/e187/E187_PARENT_LEDGER.json`
- `research/e187/E187_H185_PROTOCOL_LOCK.json`

If prose and JSON differ, JSON governs.

## Parent ledger reconciliation

Pinned F86 source is `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
`docs/audit_v29_ns_d0.log` blob `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`,
second-predict steady state.

Canonical GROUPED source-resolution values are:
- young K3 115.61u;
- old K3 106.83u;
- thin/elementwise 24.78u;
- covariance 7.10u;
- birth/closure 5.71u;
- other/untagged 0.03u;
- total **260.06u**.

Thus dense K3 is **222.44u**, fixed remainder **37.62u**, and the public `260.1u`
headline is the one-decimal rendering of 260.06u. The former coarse
`222.4 + 37.6 = 260.0u` model is forbidden.

At cap 138.24u the dense budget is 100.62u, so the source-resolution necessary ratio is
`100.62/222.44 ~= 0.4523467`; the stricter H185 gate remains 0.42.

**Blocking fact:** the published log does not expose the exact raw flopscope integer from
which these values were rounded. E186 G2 requires that raw integer. E187 cannot create it
without executing code, which this task forbids. G2 therefore remains a blocking FAIL.

## Complete dense mapping

There are no selected products. Every bilinear product under all eleven dense namespaces
`young_transport, hub, shared, old_legs, j_rf, j_rot, j_proj, j_tier2, j_qc, j_core,
qc_transport` routes to TA32. Every non-bilinear operation in those namespaces is
UNCHANGED. Production whole-product fallback is forbidden. Any escaping dense operation
is terminal `COVERAGE_NO_GO`.

Coverage reconciles to the grouped **222.44u**, never to a sum of display-rounded family
rows.

## Frozen coefficient/base-case/blocking/fallback table

One concrete H185 implementation is pinned:

- `khoruzhii/lita@c1dd9225df98676e385b53ae7517ff2ea0ec5779`
- `schemes/32x32x32_r14197.npz`
- rank 14197;
- Git blob `6f2dea4820245303dc2eb1fba13816436fabe54d`;
- size 2,057,836 bytes;
- generator `scripts/lita.py@278b52d91fc349eb2846439fcc9404208847a59b`;
- rational scheme header `src/scheme.h@bb3570c8d2a969b615771f9790c22595f217f9df`.

Rules: one TA outer stage, no TA recursion; zero-pad m/k/n to multiples of 32; split
each padded axis into exactly 32 blocks; consume rational CSR U/V/W rows in stored order;
no reorder/reduction/fusion/refit; leaf products use frozen parent `fnp.matmul`; crop only
after W reconstruction. Production fallback is forbidden. Off-contract fallback is
allowed only outside n=1024/depth=16/frozen dtype and is terminal if observed in the
production-shape bundle.

Any future vendored NPZ must have SHA-256 pinned before an arm exists.

## Numerical gates

Exact-small must pass exact integer/rational equality on one unpadded and one padded
rectangular fixture.

Float64 production-shape gates remain product relative Frobenius, D3 relative RMS and
off-diagonal D21 relative RMS <=2e-12, with absolute norms retained and denominator
`max(reference_norm,1e-300)`.

Float32 is now separate and mandatory. For every dense family and D3/D21, save parent
float64, parent float32 and TA32 float32 on byte-identical inputs. For relative
Frobenius, max-absolute, D3 RMS and D21 RMS, TA32 error versus parent-float64 must be
<=1.05x the corresponding parent-float32 error; parent zero error implies candidate zero
error. Any miss is terminal `NO_GO_FLOAT32`.

## Full cost/runtime projection

Every coefficient linear combination, add/subtract, coefficient multiply, padding/crop
when billed, leaf matmul, copy/temp when billed, setup and fallback is charged.

Frozen cost:
`C_projected_u = 37.62 + C_TA_dense_u + C_setup_u`,
with `C_TA_dense/C_parent_dense <= 0.42` and `C_projected_u <= 138.24`.

Pinned reported residual baseline is 0.322s from the F86 log. Frozen runtime:
`T_projected = 0.322 + (T_TA_dense_bundle-T_parent_dense_bundle) + T_setup <= 0.400s`.
Same process, one BLAS thread, same dtype/inputs/multiplicities; replay timing cannot
replace the first measurement.

## One-owner/one-run and immutable handoff

Current `authorized_owner_runs=0`.

If a later append-only revision supplies the exact raw parent ledger and an independent
review re-authorizes the mechanism, semantics are already frozen: one owner head, one
implementation, one coefficient table, one seed, one candidate, one attempt, no rescue,
rerun, sweep or post-result table change; one deterministic replay inside the same
workflow; any gate failure writes a terminal receipt.

A later run must emit append-only SHA-256 evidence covering every input/output, dtype,
shape, nbytes, parent/candidate result, D3/D21, exact raw flopscope logs, exact FLOPs,
coverage, projected cost, timing, replay and target-firewall audit.

The independent verifier may use only committed E185/E186/E187 plus immutable owner
artifacts. It must independently recompute hashes, exact-small, float64, float32,
coverage, FLOPs, ratio, all-in cost, runtime, replay/provenance and firewall. It may not
repair the candidate or choose a new decomposition/seed/fallback/threshold. Receipt fields:
`mechanism_go`, `protocol_go`, `integration_readiness`, `blocking_reason`.

## E186 gate matrix

- G0 implementation identity: FROZEN
- G1 complete 222.44u coverage: FROZEN
- G2 exact raw parent ledger: **BLOCKING FAIL**
- G3 immutable inputs: CONTRACT FROZEN
- G4 exact-small: FROZEN
- G5 float64: FROZEN
- G6 float32: FROZEN
- G7 all-in flopscope: FROZEN
- G8 runtime projection: FROZEN
- G9 replay: FROZEN
- G10 one-run arm: FROZEN, zero authorization
- G11 verifier handoff: FROZEN
- G12 target firewall: FROZEN

## Decision

**PROTOCOL NO-GO. OWNER RUN NOT AUTHORIZED.**

H185 itself is not scientifically rejected. The procedural blocker is exact and narrow:
the required raw parent flopscope integer ledger is absent from the published artifact,
and producing it would require an execution forbidden in E187.

No baseline, canonical ledger, scorer, submission or leaderboard state was changed.
