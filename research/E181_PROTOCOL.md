# E181 protocol — H180 aggregate symmetric-CP carrier

Date: 2026-09-21  
Branch: `research/e181-h180-symmetric-cp-carrier-cleanroom-20260921`  
Mode: protocol-first, one target-free owner experiment, no submission/leaderboard/baseline mutation.

## Ancestry and firewall

Scientific ancestry is exactly:

1. E177 primary-source audit commit `e1536d36a5e2d641ab3596892847e2fcf41e83ab`.
2. E180 cost-wall research branch `research/e180-cost-wall-cp-20260921`.
3. Pinned ARC reference `alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.
4. Pinned public V29 evidence `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

E178 is explicitly excluded: no E178 code, artifact, receipt, result, or rerun is used.

## Official K3 convention

ARC `FactoredTensor` represents

[
T = \mathrm{Sym}\sum_j A_{:j}\otimes B_{:j}\otimes C_{:j}.
]

The pinned implementation computes `(2,1)` with coefficient
`2! 1! / 3! = 1/3`, so for distinct indices

[
D21[i,c] = \frac13\sum_j
(A_{ij}B_{ij}C_{cj}+A_{ij}C_{ij}B_{cj}+B_{ij}C_{ij}A_{cj}),
]

with repeated diagonal entries zeroed. For symmetric CP

[
T_{CP}=\sum_q \lambda_q u_q^{\otimes 3},
]

this reduces to

[
D3[i]=\sum_q\lambda_q u_{iq}^3,qquad
D21[i,c]=\sum_q\lambda_q u_{iq}^2u_{cq},
]

again with the D21 diagonal zeroed.

Linear transport is exact: `u_q -> W u_q`.

## One frozen reprojection rule

Rank is fixed before the run:

[
n=1024,quad R=3n=3072.
]

No rank sweep is allowed.

Each general symmetric factor `Sym(a,b,c)` is first converted exactly to four
symmetric cubes by polarization:

[
\mathrm{Sym}(a,b,c)=\frac1{24}[
(a+b+c)^{\otimes3}-(a+b-c)^{\otimes3}
-(a-b+c)^{\otimes3}-(-a+b+c)^{\otimes3}].
]

After appending a newborn rank-`n` general K3 block, the aggregate carrier is
compressed to exactly `R=3072` terms by one deterministic, target-free rule:

[
score_q=|\lambda_q|\|u_q\|_2^3.
]

Keep the largest `R` scores with stable original-index tie breaking. No ALS,
reference-informed optimization, fitted coefficient, projection rescue, source-age
hybrid, or second projection is permitted.

This is the single H180 instantiation tested by E181.

## Frozen target-free fixture

The structural fixture is generated only from a fixed PRNG seed and estimator-state-like
matrices; it contains no benchmark reference means or leaderboard information.

Production-shape structural test:

- width `n=1024`;
- exactly two rank-`n` dense general K3 births;
- one dense linear transport plus positive Wick-like row scaling between births;
- parent retains the exact general factorization;
- candidate uses the rank-3072 symmetric-CP carrier above.

The two births deliberately include one inherited dense block and one dense young block,
which is the representation H180 is intended to replace.

## Gate order

### G0 — protocol/ancestry
Branch ancestry must descend from E180/E177. E178 is not read or imported.

### G1 — exact-small identities
On float64 width <= 6:

- general factorization -> four-cube polarization dense tensor identity;
- D3 identity;
- D21 identity under the official 1/3 normalization;
- linear transport identity;
- deterministic round-trip.

Tolerance: max relative error <= `1e-12`.

Failure is terminal.

### G2 — production-shape D21 structural gate
On the frozen `n=1024, R=3072` fixture:

[
\epsilon_{21} =
\frac{\mathrm{RMS}(D21_{CP}-D21_{parent})}
     {\mathrm{RMS}(D21_{parent})}
\le 0.015.
]

All vectors must be finite. Candidate replay on the same frozen inputs must be bitwise
identical.

Failure is terminal; no MSE/reference evaluation is allowed after failure.

### G3 — all-in FLOP gate
Use E180's frozen F86 unit `u=2n^3=2^31` and budget `B=2^41`.

Frozen accounting:

- 15 CP transports: `45u`;
- 14 full D21 extractions: `42u`;
- conservative retained V29 remainder: `37.6u`;
- polarization/scoring/D3/reprojection arithmetic: explicitly counted as O(n^2)
  overhead by the script.

Required:

- `C_candidate / B <= 0.135`;
- `153.0u - C_candidate >= 14.76u`.

Failure is terminal.

### G4 — accuracy gate, only if G1-G3 pass
Only after G1-G3, a separate frozen reference-bearing local/public-mini evaluation is
authorized. Estimator construction remains target-free. Required:

- candidate/parent mean MSE <= `1.02`;
- one-sided 95% upper confidence bound on paired relative degradation <= `+2%`.

If G2 or G3 fails in the single E181 run, G4 is recorded as
`NOT_RUN_BY_FROZEN_GATE`; there is no rescue run.

## Artifacts

The single run must write:

- immutable parent/candidate D3 and D21 vectors;
- manifest with SHA-256 for every immutable vector/result;
- exact-small metrics;
- D21 RMS metric;
- all-in FLOP ledger;
- replay status;
- append-only `E181_RECEIPT.json`.

The workflow may commit only E181 artifacts to this branch. Canonical baseline, ledger,
submission/scorer state, and leaderboard are out of scope.
