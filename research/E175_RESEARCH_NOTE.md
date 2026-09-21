# E175 RESEARCH NOTE — AGO transfer to the public gain-only covariance closure

Date: 2026-09-21  
Branch: `research/e175-ago-public-gain-transfer-20260921`

## Evidence reviewed

### Verified AGO evidence

E164 owner receipt:
- branch `research/e164-cleanroom-ago-20260921`
- receipt blob `a13c095cc2078711e722a6a6deb953aed33fdf81`
- pooled synthetic AGO/parent MSE ratio `0.6661376209420509`
- all-in candidate upper `112131571712` FLOPs = `0.05099153518676758 B`.

E165 independently verified E164, including exact K1/K2 gauge identities,
deterministic replay, target firewall and the same cost ledger.

E171 production-shaped multiseed owner receipt:
- branch `research/e171-verifier-ready-ago-20260921`
- receipt blob `bdba803680a3a51f695b942298612719ed409f20`
- width 1024, depth 16, three frozen seeds;
- pooled parent MSE `3.9298876324663385e-6`;
- pooled AGO MSE `3.32829036514411e-6`;
- pooled ratio `0.8469174379561903` = 15.31% MSE reduction;
- all three seeds improved;
- 131/144 paired reference batches favored AGO;
- all-in cost `0.05099153518676758 B`.

E172 independently recomputed the E171 MSE/SE metrics from saved immutable
coordinate and batch vectors and returned GO.

### Public implementation evidence

Official public starter kit pinned at
`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`.

Public covariance example:
- `examples/03_covariance_propagation.py`
- blob `675b3dd8f032f342112a99f431115b35f8481620`.

This public K2 estimator is **not** the E164/E171 parent. Its off-diagonal ReLU
closure is the cheaper first-order gain rule

[
C^+_{ij}approx Phi_iPhi_j C^-_{ij},quad i
e j,
]

whereas E164/E171 additionally keep the second-order Wick term

[
	frac12(C^-_{ij})^2
(phi_i/sigma_i)(phi_j/sigma_j).
]

The official public example reports a measured Phase-2 production cost of
`51,709,240,799` FLOPs at 1024x16, utilization `0.02351464027 B`.
The starter-kit documentation reports public-mini raw final-layer MSE around
`4.05e-6` for this class. E175 does not read those baked targets.

### Public V29

Pinned public repository:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

V29 estimator blob:
`17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.

The repository reports public raw final-layer MSE about `2.13e-8` but utilization
about `0.2526 B`. Its published cost anatomy totals about 260.06
`2 n^3`-equivalent units. Therefore V29 itself is not an admissible <=0.135B
parent. E175 does not combine AGO with V29, delete V29 source tiers, retune V29,
or reuse V29's public-fitted coefficients.

V29 is used only as the accuracy/cost context showing that a public-mode transfer
must preserve the cheap K2 path before a later stronger closure can be considered.

## Exactly one E175 hypothesis

**H175 / AGO-GAIN:** the exact one-time angular/radial K1/K2 gauge from E164/E171
also improves the distinct official public **gain-only** covariance closure.

Candidate delta:

1. run the official gain-only K2 arithmetic;
2. after the first ReLU state only, apply
   [
   mu_A=mu_G/a_1,qquad
   C_A=C_G-(a_1^{-2}-1)mu_Gmu_G^T;
   ]
3. continue the same gain-only closure for all later layers;
4. multiply the final mean by exact (a_1(n)).

No K3, K4, V29 tier change, Strassen, fit, coefficient, sampling correction,
or second hypothesis is added.

Why this is the lowest-risk public-transfer test:
- AGO already has independent synthetic production-shaped evidence;
- the public gain-only estimator is a documented public-mini implementation path;
- the overlay is exact gauge arithmetic and costs only O(n^2) once;
- parent production utilization is far below 0.135B;
- the only new uncertainty is whether AGO survives the **different public
  gain-only closure**, which E164/E171 did not test.

## Minimal experiment

One target-free production-shaped synthetic MLP:
- width 1024;
- depth 16;
- zero bias;
- He-Gaussian weights;
- weight seed `1751024`;
- parent = clean-room gain-only public formula;
- candidate = exactly H175;
- independent antithetic sphere reference: 65,536 samples, 16 frozen batches,
  seed `175196608`;
- reference is materialized only after parent/candidate and replay hashes are
  frozen.

This is not a public dataset run and never opens baked target means. It is the
minimal integration falsifier before any separately authorized public-mini run.
