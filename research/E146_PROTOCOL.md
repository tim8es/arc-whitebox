# E146 protocol — frozen H143 MUB128 in-flow D21 falsifier

Idempotency key: `ARC-E146-H143-MUB128-D21-20260921`

Status: **FROZEN STAGE-A / EXACTLY ONE SCIENTIFIC RUN AUTHORIZED AFTER IMPLEMENTATION FREEZE**.

Parent: E143 research branch at receipt `c94fa7dbf5d243cfd00dce7df47d66b114d2374a`.

Pinned public V29:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Pinned ARC exact-small reference:
`alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

## Frozen point

No sweep:

- 64 production Kerdock/MUB lines from 64 distinct non-coordinate bases;
- antipodal closure: 128 particles;
- feedback rank: 16;
- depth: 8;
- fixture A: width 32 He-Gaussian, seed 146032;
- fixture B: width 32 dense adversarial rotation/gain, seed 146132.

The production MUB family is dimension 1024. For the width-32 exact-small falsifier,
construct the same 1024-D Kerdock chirps, take the first 32 coordinates of one canonical
line from each of bases u=0..63, and renormalize each restricted line. This is a
deterministic restriction of the frozen production lines; it does **not** claim the
restricted width-32 lines themselves form a complete 32-D MUB.

## Candidate-before-reference firewall

For each fixture:

1. run the pinned V29 estimator on the synthetic MLP and capture its internal pre-nonlinear
   D21 slices by a wrapper around `Estimator._dslices`;
2. capture V29's own preactivation mean/variance through a wrapper around its Wick cache;
3. construct and propagate the frozen 128-particle cloud;
4. affine-match each cloud preactivation coordinate to the captured V29 mean/variance,
   apply ReLU, and form the empirical post-ReLU D21;
5. map that cloud D21 to the next preactivation with the next dense weight and form a
   target-free residual against V29's next-layer D21;
6. project only that residual through the frozen rank-16 V29-style range finder seeded by
   the next layer weight's first 16 columns; repaired D21 = V29 D21 + projected residual;
7. hash/freeze all baseline and repaired candidate arrays.

Only **after step 7** may the harness instantiate/materialize the ARC K=3 SIMPLE exact
reference and compute exact D21 tensors. Exact/reference arrays are not callable inputs to
the candidate.

If the pinned V29 cannot be instrumented without changing its arithmetic, Stage A is
terminal NO-GO/UNEVALUABLE; no substitute baseline is permitted.

## Observable

For every evaluated layer l:

[
e_{0,l}=|D21^{V29}_l-D21^{exact}_l|_F,qquad
e_{1,l}=|D21^{repair}_l-D21^{exact}_l|_F.
]

Family-pooled ratio:

[
R=sqrt{rac{sum_l e_{1,l}^2}{sum_l e_{0,l}^2}}.
]

Primary gate: `R <= 0.90` independently on both fixture families.

Secondary frozen E143 gate retained: no layer with nonzero baseline error may have
`e1/e0 > 1.05`.

## Determinism

Run the candidate path twice before exact reference materialization. Candidate hashes and
numeric arrays must be bitwise identical.

## Full incremental production cost gate

Budget `B=2^41`. Frozen cap:
`0.00437546 B`.

Conservative all-in ledger, n=1024, L=16, N=128, r=16:

- particle dense propagation: `2*N*n^2*L`;
- empirical D21 contractions: `2*N*n^2*L`;
- affine moment repair and reductions: `12*N*n*L`;
- rank-16 residual projection/injection: `4*n^2*r*(L-1)`.

Total frozen upper:
`9,621,733,376 FLOPs = 0.004375457763671875 B`.

The run must independently recompute this formula and require
`incremental/B <= 0.00437546`.

## Stage-A GO

All must pass:

1. both pooled repaired/baseline D21 ratios <= 0.90;
2. no layer ratio > 1.05;
3. candidate constructed and frozen before exact reference;
4. deterministic bitwise replay;
5. pinned V29 and ARC commits verified;
6. target/oracle/public/scorer/holdout/full firewall;
7. full incremental production cost <= 0.00437546 B;
8. finite arithmetic.

Any failure => **TERMINAL NO-GO H143**. No particle/rank/layer/seed sweep, no rescue,
no rerun, no final-MSE validation.

Stage-A GO authorizes only a verifier handoff. It does not itself authorize final-MSE
validation.
