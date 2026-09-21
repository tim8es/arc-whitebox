# E175 OWNER PROTOCOL — AGO-GAIN public-mode transfer falsifier

Date: 2026-09-21  
Status: **FROZEN BEFORE IMPLEMENTATION / ONE RUN ONLY**  
Idempotency: `ARC-E175-AGO-GAIN-TRANSFER-20260921`

## 1. Single hypothesis

H175 is exactly one change to the official public gain-only covariance closure:

[
(mu_G,C_G)_{	ext{after first ReLU}}
ightarrow
(mu_A,C_A)
]

with

[
a_1(n)=sqrt{2/n},Gamma((n+1)/2)/Gamma(n/2),
]
[
mu_A=mu_G/a_1,
]
[
C_A=C_G-(a_1^{-2}-1)mu_Gmu_G^T.
]

All later layers use the same gain-only K2 closure as the parent. Final readout is
[
mu_{G,mathrm{out}}=a_1mu_{A,mathrm{out}}.
]

No second-order Wick off-diagonal term is permitted. No K3/K4/V29 mechanism,
rank change, source deletion, Strassen, fit, sweep, or tuning is permitted.

## 2. Frozen parent arithmetic

The parent is reconstructed from
`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`,
`examples/03_covariance_propagation.py`, blob
`675b3dd8f032f342112a99f431115b35f8481620`.

For each layer:

[
mu^-=Wmu,qquad C^-=WCW^T,
]
[
v=max(operatorname{diag}C^-,10^{-12}),quad
sigma=sqrt v,quad alpha=mu^-/sigma,
]
[
mu^+=mu^-Phi(alpha)+sigmaphi(alpha),
]
[
v^+=(mu^{-2}+v)Phi(alpha)+mu^-sigmaphi(alpha)-mu^{+2},
]
[
C^+_{ij}=Phi_iPhi_j C^-_{ij},quad i
e j,
]
with the diagonal replaced by (v^+).

The clean-room array orientation may transpose all weights consistently; parent,
candidate and reference must use the same frozen orientation.

## 3. Fixture and ordering

Exactly one external run.

Fixture:
- n=1024;
- depth=16;
- zero bias;
- He-Gaussian weights;
- numpy PCG64 seed `1751024`;
- float64 research arithmetic.

Reference:
- 65,536 antithetic points on sphere radius sqrt(1024);
- 16 contiguous batches of 4096;
- PCG64 seed `175196608`;
- exact Gaussian radial readout (a_1);
- no baked/public target.

Mandatory order:
1. generate weights;
2. run parent and candidate;
3. replay both;
4. freeze hashes and cost;
5. only then import the streaming reference helper;
6. compute reference and parent-vs-candidate metrics;
7. write immutable result.

## 4. Gates

All are mandatory.

1. Source firewall: no public dataset/target/scorer/holdout/full/submission access.
2. Public-parent formula audit: implementation contains gain-only off-diagonal
   covariance and no second-order Wick (C_{ij}^2) term.
3. Gauge roundtrip after first activation <= `2e-12`.
4. Radial (a_1(1024)) absolute error versus E171 independently verified value
   `0.9997558892135413` <= `1e-15`.
5. Parent and candidate replay bitwise exactly.
6. All state/output/reference arrays finite.
7. Reference final mean reconciles the 16 saved batch means <= `2e-12`.
8. Reference RMS coordinate SE <= `1.2e-3`.
9. Candidate final MSE < parent final MSE.
10. Strong transfer gate:
    [
    MSE_{m AGO-GAIN}le0.98 MSE_{m parent}.
    ]
11. Paired batch delta
    [
    Delta_b=MSE_b(parent)-MSE_b(candidate)
    ]
    has positive mean.
12. At least 10/16 batches have positive delta.
13. Complete production cost <= `0.135B`.
14. Exactly one run; no rescue/rerun/sweep.

A noisy reference is a failure, not authorization to increase samples.

## 5. Complete production cost

Use the official public parent's measured complete 1024x16 cost:

[
C_{m parent}=51,709,240,799.
]

AGO overlay upper from the independently verified E164/E171 ledger:

[
C_{m AGO}=9,437,184.
]

Add a frozen integration/accounting reserve of 1,000,000,000 FLOPs.

[
C_{m all}^{upper}
=52,718,677,983.
]

With (B=2^{41}):

[
C_{m all}^{upper}/B=0.02397367915500581<0.135.
]

The research Monte-Carlo reference is verifier-only and is not estimator cost.

## 6. Decision

All gates pass:

**E175 TARGET-FREE GO — AGO-GAIN TRANSFERS TO PUBLIC GAIN-ONLY CLOSURE.**

Any mandatory failure:

**E175 TERMINAL NO-GO — AGO-GAIN TRANSFER.**

A GO does not authorize public mini/full, scorer, leaderboard, holdout, or
submission. It only establishes the one target-free transfer hypothesis.

Canonical baseline and canonical ledger must remain untouched.
