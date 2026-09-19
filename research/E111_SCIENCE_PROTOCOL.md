# E111 scientific protocol addendum — exact small-width Gaussian-ReLU plug-in bias gate

Idempotency key: `ARC-E111-LATE4-GAUSSIAN-RELU-PLUGIN-EXACT-BIAS-20260919`

Status: **PREREGISTERED SCIENTIFIC BIAS GATE / SAME E111 IDENTITY**.

This addendum continues the existing cost-feasible E111 branch. It does not create a new sampler, control variate, or estimator family.

## Inherited E111 cost result

The frozen production cost audit already established:

- E104 measured base: `149,114,620,592` FLOPs;
- E111 late-4 plug-in increment: `105,891,842` FLOPs;
- all-in upper: `149,220,512,434` FLOPs;
- utilization: `0.06785763272728218 <= 0.13`;
- no fresh trajectories or RNG are required by the plug-in.

Therefore compute is not the active scientific gate. The unresolved question is deterministic Gaussian-approximation bias.

## Candidate mechanism under test

For a pre-ReLU scalar coordinate `Z`, E111 replaces the exact ReLU mean by the Gaussian moment plug-in

`G(mu,var) = sigma*phi(mu/sigma) + mu*Phi(mu/sigma)`

with `mu=E[Z]`, `var=Var(Z)`, `sigma=sqrt(var)`.

The production proposal would apply this coordinatewise to already-computed pre-ReLU trajectory moments in the last four layers.

This gate asks whether the formula itself has sufficiently small **irreducible non-Gaussian bias** when its input mean and variance are known exactly. Sampling noise is deliberately removed.

## Exact small-width reference

Frozen family:

- Gaussian input dimension: `1`;
- hidden width: `8`;
- depth: `4`;
- zero biases;
- first-layer weights: iid `N(0,2)`;
- later-layer weights: iid `N(0,2/8)`;
- float64 reference arithmetic;
- PCG64 network seeds: `111200..111207`.

For `X~N(0,1)`, positive homogeneity implies that every hidden layer has exactly two rays:

- for `X>0`, `h_l(X)=X p_l`;
- for `X<0`, `h_l(X)=(-X)m_l`.

The ray coefficients are deterministic:

- layer 1: `a_l^+=W_1`, `a_l^-=-W_1`, `p_l=ReLU(a_l^+)`, `m_l=ReLU(a_l^-)`;
- later layers: `a_l^+=W_l p_{l-1}`, `a_l^-=W_l m_{l-1}`, followed by ReLU.

Hence the exact pre-ReLU moments for each coordinate are

`E[Z] = (a^+ + a^-)/sqrt(2*pi)`

and

`E[Z^2] = ((a^+)^2 + (a^-)^2)/2`.

The exact post-ReLU mean is

`E[ReLU(Z)] = (ReLU(a^+) + ReLU(a^-))/sqrt(2*pi)`.

These are closed-form Gaussian integrals; no Monte Carlo, quadrature, fitted target, or approximate truth construction is used.

The Gaussian plug-in is evaluated using the **exact** pre-ReLU mean and variance above. Therefore any discrepancy is pure plug-in bias.

## Frozen metrics

For every seed/layer:

- exact post-ReLU mean vector;
- Gaussian plug-in mean vector;
- coordinate MSE of plug-in bias;
- max absolute bias;
- exact pre-ReLU variance;
- standardized skewness/kurtosis where finite.

Aggregate:

- pooled layerwise bias MSE;
- pooled all-layer bias MSE;
- pooled final-layer bias MSE;
- worst-seed final-layer bias MSE;
- first-layer bias sanity check.

Reference production frontier scales, used only for interpretation:

- current E108/E104-style stochastic-risk scale: `~1.0016396e-5`;
- competition raw target: `1.89e-8`.

## Frozen scientific gates

Integrity gates:

1. all exact/plugin arrays finite;
2. deterministic replay bitwise exact;
3. exact-reference formulas independently reimplemented by verifier and agree within `1e-14`;
4. first-layer plug-in bias MSE `<=1e-24` (Gaussian sanity check).

Credible-path gate:

5. pooled final-layer irreducible plug-in bias MSE `<=1.89e-8`;
6. pooled all-layer irreducible plug-in bias MSE `<=1.89e-8`.

If 5 or 6 fails, E111 is **TERMINAL SCIENTIFIC NO-GO / DROP**. The reason is deterministic approximation bias, not sampling variance or compute.

If both pass, E111 receives only **SMALL-EXACT SCIENTIFIC GO**, authorizing one production-shaped synthetic plug-in falsifier under the already-proven `<=0.13` cost envelope. It does not authorize public/scorer/holdout/full.

## No-rescue rule

After this frozen exact gate there is no:

- layer-count change;
- seed/width/depth sweep;
- variance correction;
- skew/kurtosis correction;
- mixture fit;
- clipping;
- target fit;
- alternate Gaussianization;
- sampler/control variant;
- rerun.

A failed Gaussian plug-in may motivate a new later experiment ID, but E111 itself is terminal.
