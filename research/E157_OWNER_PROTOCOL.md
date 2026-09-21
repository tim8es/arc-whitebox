# E157 OWNER PROTOCOL — AIK4-1 clean-room one-birth execution

Date: 2026-09-21  
Status: **OWNER FROZEN / ONE TARGET-FREE RUN AUTHORIZED AFTER ARM COMMIT**  
Parent support: E155 `ARC-E155-AIK4-1-SUPPORT-20260921`

## Experiment identity

E157 is a new candidate class. It is not E154 or E151 rescue, and it imports no
E151/E154 code, workflow, run artifact, Strassen path, target, or result.

Candidate:
[
	ext{angular input K4}
	o 	ext{exact first linear transport}
	o 	ext{exact first-birth D4/D22 overlay}
	o 	ext{destroy K4}.
]

No recurrent K4 or scalar `c4` exists after layer 0.

## Frozen parent

Implementation:
- commit `cf1c86edf4f1a35f887bd464f78d5454eefcc68b`
- `scripts/e157_aik4_parent.py`
- blob `cf233297780b509da35edd149e3c83d1a3a06087`

Cost freeze:
- `research/E157_PARENT_COST_FREEZE.json`
- blob `aab829ed3f8e4eb5f8de2ee8a4fc38ae9980c465`

Parent arithmetic is clean-room angular K2 Wick propagation:
1. state starts with mean 0, covariance I;
2. every layer applies dense mean/covariance transport;
3. every nonlinearity uses the frozen K2 ReLU Wick arithmetic;
4. no K4/c4 state exists;
5. final mean is multiplied by exact radial (a_1(n)).

The first transported covariance is exactly
[
M=W_0 I W_0^T=W_0W_0^T,
]
so the parent already owns the matrix required by AIK4-1.

The parent state order is K2. E155's selected (Delta P_{21}) K3-birth term is
therefore identity-audited in E157 but is not retained by either parent or candidate.
No K3 compression, approximation, or new K3 state is introduced.

Frozen production envelope at width 1024, depth <=16:
- budget: `2^41 = 2199023255552` FLOPs;
- parent upper: `74238787584` FLOPs;
- parent utilization upper: `0.033759891986846924`;
- required parent ceiling: `0.1349904166907072`;
- overlay upper: `21073920` FLOPs;
- combined upper: `74259861504` FLOPs;
- combined utilization upper: `0.03376947529613972 <= 0.135`.

No Strassen is allowed.

## Frozen AIK4-1 overlay

For input dimension (n):
[
kappa=-rac{2}{n+2}.
]

At the first preactivation only:
[
M=W_0W_0^T,
]
[
K4_{abcd}
=kappa(M_{ab}M_{cd}+M_{ac}M_{bd}+M_{ad}M_{bc}),
]
[
D4_i=3kappa M_{ii}^2,
qquad
D22_{ij}=kappa(M_{ii}M_{jj}+2M_{ij}^2).
]

The candidate adds exactly:
[
Delta P_{p,i}=rac{1}{24}w_{4,p,i}D4_i,quad p=1,2,
]
to the parent's first-layer marginal power moments, and
[
Delta P_{11,ij}
=rac14 w_{2,1,i}w_{2,1,j}D22_{ij}
]
to the first-layer cross-covariance birth.

For identity audit only, also compute the E155-frozen
[
Delta P_{p,i}, p=3,4,qquad
Delta P_{21,ij}
=rac14 w_{2,2,i}w_{2,1,j}D22_{ij}.
]

Immediately after the first K2 conversion, all K4/D4/D22 objects are destroyed.
Layers 1..7 call exactly the same parent K2 arithmetic.

## Target firewall

Forbidden for the entire branch/run:
- public Phase-2 data, targets, labels, predictions, reference means;
- mini targets;
- scorer, holdout, full suite, submission;
- target fitting, post-result fitting, sampling/CV;
- E151/E154 imports or artifacts;
- Strassen;
- recurrent K4/c4;
- parameter/seed/rank/threshold sweep;
- rerun or rescue after failure.

The run script may import only the frozen E157 parent plus Python/numpy standard
scientific runtime.

## One frozen falsifier

Exactly one GitHub Actions scientific run is authorized after the immutable arm and
workflow are committed. It contains all fixtures and an in-process deterministic
replay.

### F0 exact2d/depth8

- width/input dimension: 2;
- depth: 8;
- zero bias;
- seed: `155002`;
- weights: numpy PCG64 Gaussian, scale (sqrt{2/n});
- float64.

Reference: exact activation-sector integration on the unit circle, multiplied by
(E[chi_2]=sqrt{pi/2}). No sampling.

### F1 dense32/depth8

- width/input dimension: 32;
- depth: 8;
- zero bias;
- seed: `155032`;
- Gaussian weights scaled by (sqrt{2/n});
- dense K4 materialization allowed only for identity verification.

### F2 adversarial16/depth8

- width/input dimension: 16;
- depth: 8;
- zero bias;
- seed: `155016`;
- each layer is (Q_L,diag(g),Q_R^T);
- (Q_L,Q_R) are deterministic QR factors of Gaussian matrices;
- (g) is linearly spaced from 0.5 to 1.5 and rescaled to RMS (sqrt2);
- QR signs are canonicalized to make the construction deterministic;
- dense K4 materialization allowed only for identity verification.

## Mandatory gates

All must pass.

1. target/reference firewall: PASS.
2. radial homogeneity on all fixtures: max relative error <= `2e-12`.
3. angular K4 dense fourth-moment identity on F0/F1/F2: relative Frobenius
   error <= `2e-12`.
4. ARC one-pair carrier identity `Sym(M tensor 3*kappa*M)`: <= `2e-12`.
5. D4 parity against dense K4: <= `2e-12`.
6. D22 parity against dense K4: <= `2e-12`.
7. selected Wick-term parity for p=1..4, P11 and P21: <= `2e-12`.
8. no recurrence: exactly one overlay call at layer 0; zero K4/c4 state after it.
9. exact-small scientific gate:
   [
   MSE_{AIK4-1}le0.98,MSE_{parent}
   ]
   against F0 analytic sector mean.
10. deterministic replay: output arrays and receipt metrics bitwise identical.
11. parent cost <= `0.1349904166907072 * 2^41`.
12. complete combined production cost <= `0.135 * 2^41`.
13. exactly one run; no sweep/rescue.

## Decision

Any failed or unevaluable gate:
[
oxed{	ext{E157 TERMINAL NO-GO}}
]

All gates pass:
[
oxed{	ext{E157 TARGET-FREE SCIENTIFIC GO}}
]

No GO here authorizes public/scorer/holdout/full/submission. A GO only permits the
separately reserved verifier handoff.
