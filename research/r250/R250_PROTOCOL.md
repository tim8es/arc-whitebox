# R250 — V25 LEG2-R1 young A/P channel-compression protocol

Status: **FROZEN BEFORE MEASUREMENT**  
Run ID: `R250-post-r248-next-method-research-20260923`

## Evidence boundary

R250 uses current `AGENTS.md`, `research/RESEARCH_PROCESS.md`, the complete 194-entry
`research/history.json` inventory (Git blob
`8f94f371572fedbd8c1ebd9d19cc48ca837592fb`), the immutable R209 V25 normalized
record, R246 score decomposition, R245 source-compliance report, R248 terminal report,
and the exact public V25 source. It does **not** read R223/R244 candidate outputs or
artifacts.

Pinned V25 source:
- upstream repository `504aldo/whest-p2-cumulant-k3`;
- commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- `estimators/estimator_v25.py`;
- Git blob `195373a110215256b759d7c172ba8c923c62e5cc`.

R209 baseline:
- normalized record SHA256
  `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`;
- mean raw MSE `2.228303490170447e-8`;
- mean adjusted score `8.170397440117225e-9`;
- measured FLOPs/MLP `806303721965`;
- failures `0/100`.

## Full-history novelty screen

The complete history inventory and branch/mechanism names were screened before choosing
the candidate. Explicitly excluded are R247 2:4/N:M D21 right-factor sparsity, R248
rank-1 Kronecker transport, R244 MP-R16, R223 V25-LF, and the historical families for
source dropping/windowing, source-axis rank compression, old-tier spatial bases/ranks,
TensorSketch/CountSketch/sampling, DEIM/cubature, FWHT/structured projections,
response-aligned D21, tensor-train K3, CP carrier, trilinear aggregation, Strassen/fast
matmul, precision changes, and displacement/Toeplitz structure.

Literal search of the complete history JSON finds zero occurrences of
`leg-channel`, `channel-rank`, `channel rank`, `a/p pair`, `collinear`,
`collinearity`, `joint leg`, `two-channel`, `leg type`, or `leg-type`.

The frozen mechanism is therefore **V25-LEG2-R1-YOUNG-AP**: rank-1 compression only
across the two-dimensional **leg-type channel** `(A_s,P_s)` of each young source.
It does not reduce source count, spatial matrix rank, columns/entries, or the transport
operator itself.

## Frozen mathematics

For each young source, flatten the two spatial legs into

`X_s = [vec(A_s); vec(P_s)] in R^(2 x n^2)`.

The oracle structural question is whether `X_s` is numerically rank one. The best
rank-1 approximation is

`Xhat_s = sigma_1 u_1 v_1^T`,

equivalently `Ahat_s = a_s H_s`, `Phat_s = p_s H_s` for one shared spatial matrix
`H_s`.

If this representation were accurate, V25's separate young A/P transports become one
transport of `H_s`. In the D21 core, the two dense right-factor contractions collapse:

`LA @ Ahat_s.T + LP @ Phat_s.T = (a_s LA + p_s LP) @ H_s.T`.

The production implementation, if ever authorized, must derive the principal
two-channel direction from the 2x2 fnp Gram using only metered `fnp.sum`,
`fnp.sqrt`, `fnp.maximum`, multiplication/addition and fnp array division.
Coefficients remain fnp arrays; no output-affecting `math.*`, NumPy, or Python-float
materialization is permitted.

## Analytical all-in cost gate

Use the conservative R247/R248 V25 anatomy already frozen for this line:
54 units of young A/P transport plus 54 units of young D21 right-factor contractions,
with one unit `u=2*n^3`. Rank-1 leg-channel compression halves each family:

- parent: `375.4644291312434 u`;
- transport: `54 -> 27 u`;
- D21 right-factor contractions: `54 -> 27 u`;
- reserve `8 u` for metered 2x2 Gram extraction, normalization, reconstruction and
  integration overhead;
- conservative candidate: `329.4644291312434 u`;
- FLOP bound: `707519474157`;
- candidate/parent: `0.8774850653457754`.

Frozen static gate: ratio `<=0.9`. **PASS as a planning bound**, not a measured result.

## Frozen target-free falsifier

Script: `scripts/r250_leg2_r1_falsifier.py`.

No ARC dataset, target, network name, prediction, R223/R244 output, estimator execution,
or public mini row is used. NumPy/SVD is an offline oracle only.

Frozen controls/cases:
- exact channel-rank-1 control, seed `25000`;
- realistic synthetic width `n=192`, latent covariance rank `24`;
- seeds exactly `25001,25002,25003,25004`;
- source ages exactly `0,2`, giving 8 realistic cases;
- Gaussian weight matrices scaled by `1/sqrt(n)`;
- PSD-derived off-diagonal covariance and bounded derivative-like Wick vectors;
- V25-like birth `A=W@(w1*C_off)`, `P=W`;
- age transport by independent `WD=W*reshape(w,1,-1)`;
- D21 core mirrors the dense A/P part of V25 `_dslices`:
  `AP=A*P`, `PP=P*P`, `MP=PP*s+3*AP*e`,
  `LA=2*AP*w2+PP*e`,
  `LP=A*A*w2+PP*s/3+2*MP/3`,
  `D=LA@A.T+LP@P.T`, diagonal zeroed.

All gates must pass:
1. exact-rank-1 control max(A RRMS, P RRMS, D21-core RRMS) `<=1e-12`;
2. two complete executions serialize identically;
3. 8/8 realistic cases finite;
4. every realistic A and P reconstruction RRMS `<=0.015`;
5. every realistic D21-core RRMS `<=0.015`;
6. mean realistic D21-core RRMS `<=0.012`.

Any failure is terminal **DEVELOPMENT NO-GO** for R250. No altered seed, width, age,
tolerance, rank, second candidate, estimator implementation, benchmark, or Actions run
is permitted after a failure.

## Public panel and scientific gates — only if all preregistration gates pass

Exact panel:
- `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`, dataset SHA256
  `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`;
- split `mini`, all 100 rows, shape `[16,1024]`, dtype `float32`;
- name/order SHA256
  `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`;
- `whestbench 0.16.1`, `flopscope 0.12.1+np2.4.6`, budget `2**41`.

At most one preverified-free standard Actions workflow, no retry. GO requires all:
exact row/hash identity; 0 failures; mean adjusted score
`<=0.995*R209 = 8.12954545291664e-9`; at least 55/100 rows better; paired
parent-minus-candidate gain (>2) descriptive SE; mean FLOPs
`<=0.9*806303721965 = 725673349768.5`; max residual wall time `<0.4s`.

No paid/private/holdout, submission, leaderboard mutation, canonical V25 edit, or gate
relaxation.
