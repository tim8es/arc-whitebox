# E142 protocol — response-aligned residual sufficient statistic for old K3/D21 contractions

Idempotency key: `ARC-E142-RESPONSE-ALIGNED-OLD-D21-20260921`.

Status at freeze: **PROTOCOL ONLY / ONE EXACT-SMALL ACTIONS RUN AUTHORIZED AFTER CODE**.

Branch:
`research/e142-response-aligned-old-d21-20260921`.

Parent:
`research/e140-smv-rank4-execution-20260921@b269b2e57ac61a3c25a3f5ea06e32594d12ab998`.

H140 is terminal and is not revived. H137 is terminal and is not revived.

## Goal

Test one new mechanism suggested by the E135 theory gap:

> retain exact residual action on the **actual downstream response directions**
> instead of replacing the old-source residual by only `||R||`, by a
> CountSketch product approximation, or by a rank-4 symmetric matrix-vector K3
> carrier.

The object under test is a sufficient statistic for old K3/D21 Hadamard
contractions. It is not a final challenge estimator and does not claim that the
unchanged V25/V29 backbone fits the project cap.

## Frozen old-tier algebra

At one D21 extraction point, write the exact old-tier shared-basis contraction

`C1 = sum_s [LA_s FA_s^T + LP_s FP_s^T] in R^(n x q1)`.

For the nested tier,

`C2 = sum_s [LA2_s FA2_s^T + LP2_s FP2_s^T] in R^(n x q2)`.

With orthonormal shared basis `Qc in R^(n x q1)` and nested basis
`U2 in R^(q1 x q2)`, the exact old D21 contribution is

`D = (C1 + C2 U2^T) Qc^T in R^(n x n)`.

This is the same algebraic interface as the public old-tier D21 contractions,
but E142 does not copy or modify the public estimator.

Split sources deterministically into a retained set and an omitted old set.
The retained set defines `D0`; the omitted set defines the residual

`R = D - D0`.

E142 never approximates a matrix product by hashing or by SMV decomposition.

## Response-aligned sufficient statistic

For a right response matrix `S in R^(n x r)` define

`V1 = Qc^T S`,
`V2 = U2^T V1`.

The omitted residual action is

`R S
 = sum_s [
     LA_s (FA_s^T V1) + LP_s (FP_s^T V1)
   ]
 + sum_s [
     LA2_s (FA2_s^T V2) + LP2_s (FP2_s^T V2)
   ]`.

Every term is computed directly from source factors. No `n x n` residual
matrix and no full old D21 matrix is formed.

For a left response `T in R^(n x r)`,

`R^T T
 = Qc [
     sum_s FA_s (LA_s^T T) + FP_s (LP_s^T T)
     + U2 sum_s (FA2_s (LA2_s^T T) + FP2_s (LP2_s^T T))
   ]`.

Thus the statistic is orientation-aware: it preserves the exact residual action
on the queried downstream subspace.

## Frozen adaptive downstream response sequence

The falsifier emulates the rank-16 style D21 response interface without using a
CountSketch.

Starting from a target-free deterministic response block `Omega`:

1. `Y1 = D Omega`;
2. `Q1 = qr(Y1)`;
3. `Z1 = D^T Q1`;
4. `Y2 = D Z1`;
5. `Q2 = qr(Y2)`;
6. `B = D^T Q2`.

E142 computes all four D/D^T actions as

`D0 response + exact residual response statistic`.

The sequence is adaptive because `Q1`, `Z1`, and `Q2` depend on earlier
responses. This is intentional: the statistic must work on actual downstream
directions, not only on a predeclared random probe.

## Exact-arithmetic sufficiency theorem

For any queried `S` and `T`, the formulas above are algebraic
reassociations of the exact contractions. Therefore

`D S = D0 S + R S`,
`D^T T = D0^T T + R^T T`

exactly.

Hence the exact-arithmetic residual certificate on every queried response is

`B_query = 0`.

This is target-free and stronger than a residual-norm bound: the residual
orientation on the actual response is retained rather than bounded away.

## Off-subspace orientation-aware certificate

To test that E142 is not merely a zero-certificate tautology, the small
falsifier also uses a held-out response `H`.

Let `V` be an orthonormal basis spanning all queried right-response columns
seen before the held-out test, and let

`E = (I - V V^T) H`.

The E142 approximation uses the exact stored residual projections on `V` and
drops only `R E`.

A computable target-free certificate is

`||R E||_F <= B_orient(E)`

with

`B_orient(E) =
  sum_s [
    ||LA_s||_F ||FA_s^T Qc^T E||_F
    + ||LP_s||_F ||FP_s^T Qc^T E||_F
  ]
 + sum_s [
    ||LA2_s||_F ||FA2_s^T U2^T Qc^T E||_F
    + ||LP2_s||_F ||FP2_s^T U2^T Qc^T E||_F
  ]`.

This follows from triangle inequality and
`||A B||_F <= ||A||_F ||B||_F`.

Unlike E135, the bound depends on the **orientation of E through each exact
right factor**. It is not a scalar `||R||` transport bound.

For comparison only, record the norm-only bound

`B_norm = ||R||_F ||E||_F`

on the small fixture, where `R` may be materialized only for verification.
Production E142 never needs `R` materialized.

## Floating-point response certificate

For each direct response action, also compute a conservative roundoff envelope

`B_fp = gamma_m * sum_source ||L||_F ||F^T V||_F`

with

`gamma_m = m u / (1 - m u)`,
`m = 4 n + 4 q1 + 4 q2 + 32`,
`u = 2^-52`.

The exact-small response error must be <= `B_fp + 1e-12 * scale`.

This certificate is entirely weight/source/response derived.

## Exact-small falsifier

Synthetic only. No benchmark/public/scorer/holdout/full data.

### Fixture A — 32D

- `n=32`
- `q1=12`
- `q2=7`
- retained shared sources: 3
- omitted shared sources: 6
- retained nested sources: 2
- omitted nested sources: 5
- adaptive response rank: `r=4`
- deterministic seed: `142032`

### Fixture B — 16D adversarial orientation

- `n=16`
- `q1=8`
- `q2=5`
- retained shared sources: 2
- omitted shared sources: 5
- retained nested sources: 2
- omitted nested sources: 4
- adaptive response rank: `r=4`
- deterministic seed: `142016`

Both fixtures generate dense, anisotropic source factors and dense orthonormal
`Qc/U2`. The held-out response is generated independently from the adaptive
response seed and is not chosen from observed errors.

The exact verifier materializes `D` only after the response-statistic path has
completed.

## Frozen small gates

All must pass:

1. finite state and outputs;
2. deterministic replay bitwise exact;
3. direct right-action relative Frobenius error <= `1e-12` on every adaptive
   query;
4. direct left-action relative Frobenius error <= `1e-12` on every adaptive
   query;
5. final adaptive `Q2 Q2^T` projector error <= `1e-11`;
6. final `B=D^T Q2` relative Frobenius error <= `1e-12`;
7. held-out actual error <= `B_orient + 1e-12 * scale`;
8. `B_orient <= B_norm` on both fixtures;
9. queried-response floating-point error <= frozen `B_fp` envelope;
10. target/oracle firewall PASS;
11. production cost formula exactly reconciles and is <= `0.135 B`.

Any failed or unevaluable gate =>

**E142 TERMINAL NO-GO / CLOSE RESPONSE-ALIGNED OLD-D21 STATISTIC.**

No response-rank sweep, no seed replacement, no alternate fixture, no rescue,
no rerun.

## Production cost proof

This proof is for the **E142 old-tier response-statistic module**, from existing
old-source factor arrays at the D21 contraction interface through four adaptive
rank-16 response passes and its certificates.

It is not a claim that unmodified V25/V29 plus E142 is <=0.135B. In fact E135
already records that the public V29 non-old-tier backbone is about 0.150B.

Competition budget:

`B = 2^41 = 2,199,023,255,552`.

E142 module cap:

`floor(0.135 B) = 296,868,139,499`.

Frozen production dimensions:

- `n=1024`
- layers billed: `L=16`
- response rank: `r=16`
- shared basis rank: `q1=384`
- nested basis rank: `q2=224`
- conservative shared old-source count per layer: `k1=16`
- conservative nested old-source count per layer: `k2=16`
- adaptive response actions: `p=4`

The source-count bound deliberately double-counts tiers; it is an upper bound.

### A. Build/refresh LA, LP Hadamard left factors

Charge `32` scalar operations per source matrix element:

`C_A = 32 (k1+k2) n^2 L
      = 17,179,869,184`.

### B. Shared-tier response actions

For one source and one response pass, two factor families require

`4 n r (n+q1)`

FLOPs.

Thus

`C_B = p L k1 4 n r (n+q1)
      = 94,489,280,512`.

### C. Nested-tier response actions

`C_C = p L k2 4 n r (n+q2)
      = 83,751,862,272`.

### D. Qc/U2 response lifts

Charge per pass/layer

`2 n q1 r + 2 q1 q2 r`.

Thus

`C_D = 981,467,136`.

### E. Adaptive QR and response bookkeeping

Conservative QR/sign canonicalization:

`C_E = 16 n r^2 L
      = 67,108,864`.

Additional adaptive query products:

`C_F = p L 8 n r^2
      = 134,217,728`.

### F. Computable certificate norms

Charge, per source/pass/layer,

`4 n^2 + 8 n r`

for left-factor Frobenius norms, projected-right-factor norms, reductions and
accumulation.

`C_G = p L (k1+k2)(4n^2+8nr)
      = 8,858,370,048`.

### G. Helper/accounting reserve

`C_H = 20,000,000,000`.

This reserve covers array initialization, deterministic response generation,
orthogonalization scratch, finite checks, metadata-independent scalar
reductions and any implementation operation class not already billed. Any
unlisted class exceeding this reserve is an accounting failure.

### All-in E142 module upper

`C_total
 = C_A+C_B+C_C+C_D+C_E+C_F+C_G+C_H
 = 225,462,175,744`.

Utilization:

`C_total / B = 0.10252832714468241`.

Slack to E142 cap:

`296,868,139,499 - 225,462,175,744
 = 71,405,963,755`.

Pre-code production module cost gate:

**PASS**.

## Non-overlap / firewall

E142 is not:

- H140 rank-4 SMV: no symmetric matrix-vector K3 carrier, no K3
  recompression, no SVD;
- E137/H137: no CountSketch, no hashing, no randomized approximate matrix
  multiplication, no patch rescue;
- E135: residual orientation is retained explicitly through `R V`; no
  norm-only transported certificate;
- E132/E134: no source-age estimator or Hermite/Edgeworth correction;
- E124/E127: no pair-tree/hypergraph closure.

Allowed inputs:

- synthetic source factors;
- synthetic downstream response matrices;
- deterministic seeds;
- exact-small verifier matrices after candidate execution.

Forbidden:

- benchmark/public MLP weights;
- final means or targets;
- official scorer;
- holdout/full;
- leaderboard fit;
- post-result response-rank/seed selection.

## Run discipline

1. this protocol-only commit;
2. implementation/tests/workflow only afterward;
3. exactly one Actions scientific run;
4. immutable receipt after run;
5. no rerun/rescue;
6. no canonical or ledger mutation.
