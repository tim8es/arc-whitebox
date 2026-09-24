# R374 — next distinct estimator frontier

**Status:** COMPLETE
**Verdict:** **NO_GO_EXPLICIT_POLYHEDRAL_CDF_CERTIFICATION_EXCEEDS_PHASE2**
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
**Live R320 evidence head:** `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`

## Result

R374 deduplicated the requested history and admits exactly one additional output-functional mechanism for a theory gate:

> **PCDF-MID — global polyhedral output-CDF certification followed by deterministic tail-integral midpoint readout.**

This is not R366 shallow-ridge flattening, sampled regression, a layerwise moment/Hermite/TT/CF state, QMC, or an activation-boundary flux estimator. It treats the fixed network globally as a piecewise-affine map, certifies upper/lower output CDFs, and converts those envelopes to a deterministic mean interval.

The mechanism is stopped before implementation because the constructive primary-source algorithm requires explicit activation-polytope extraction and is already beyond the Phase-2 compute and memory caps at the first 1024x1024 zero-bias layer.

## Evidence and dedupe

Read before selection:

- `research/history.json`, blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`;
- live R320 report/receipt at `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`, blobs `870c9131a4e4bc745ea6ad6510d6a45115dcc5a8` and `3fa12a194b1fd33361465bef815afe1eedc81460`;
- R317/R321 gate-conditioned compression;
- corrected R335/R338 characteristic-function/Hilbert route;
- R347 dense Hermite;
- corrected R352/R364 plus R361/R362/R363 low-rank Hermite/TT;
- R366 white-box shallow-ridge flattening;
- E100–E193 including Stein/CV, antithetic/Haar/radial, cumulant/higher-moment, CP/Tucker/TT/sketch, activation-boundary, displacement, QMC/cubature/sampling, and H185 lines.

All historical verdicts are preserved.

The strongest compatible same-panel internal parent remains R209 V25 on `v2-phase2 mini:all-100`:

- raw final-layer MSE `2.22830349017044681e-8`;
- adjusted score approximately `8.170397440117225e-9`;
- measured FLOPs/network `806303721965`;
- failures `0/100`.

## Primary-source derivation

Andrey Kofnov, Daniel Kapla, Ezio Bartocci, Efstathia Bura, “Exact Upper and Lower Bounds for the Output Distribution of Neural Networks with Random Inputs,” ICML 2025, PMLR 267, 31133–31157.

Primary links:
- https://proceedings.mlr.press/v267/kofnov25a.html
- https://arxiv.org/abs/2502.11672

Theorem 3.8 computes the exact CDF of a ReLU network for a piecewise-polynomial input density on compact support. The construction partitions the input into activation polytopes, intersects each with output sublevel halfspaces, triangulates the reduced polytopes, and integrates the polynomial density over the resulting simplices. The paper states that its computations use extraction of the **full set of polytopes** and local affine maps by propagation through layers.

Supporting primary source for ReLU region complexity:

Guido Montúfar, Razvan Pascanu, Kyunghyun Cho, Yoshua Bengio, “On the Number of Linear Regions of Deep Neural Networks,” NIPS 2014.
- https://proceedings.neurips.cc/paper_files/paper/2014/hash/fa6f2a469cc4d61a92d96e74617c3d2a-Abstract.html
- https://arxiv.org/abs/1402.1869

## Concrete estimator and error certificate

Let `f:R^1024->R^1024` be the fixed bias-free ReLU MLP and `X~N(0,I)`. Choose a target-independent box `K_R=[-R,R]^1024` and let `p_R=P(X in K_R)`.

For coordinate `Y_j=f_j(X)>=0`, construct certified conditional CDF bounds on `K_R`:

`L_j(t) <= F_{Y_j | X in K_R}(t) <= U_j(t)`.

Let `M_j` be a certified upper output bound on the box. Then

`p_R integral_0^M (1-U_j(t))dt <= E[Y_j 1_K] <= p_R integral_0^M (1-L_j(t))dt`.

Bias-free positive homogeneity and ReLU nonexpansiveness give

`||f(x)||_2 <= Lambda ||x||_2`, `Lambda=product_l ||W_l||_2`.

With `q_R=P(X notin K_R)`, Cauchy–Schwarz yields

`0 <= E[Y_j 1_{K^c}] <= Lambda sqrt(1024 q_R)`.

Define

`a_j=p_R integral(1-U_j)`,
`b_j=p_R integral(1-L_j)+Lambda sqrt(1024q_R)`,
`mu_hat_j=(a_j+b_j)/2`,
`h_j=(b_j-a_j)/2`.

Then deterministically

`|mu_hat_j-EY_j|<=h_j`

and the certified final-layer mean MSE satisfies

`MSE_i <= H_i^2=(1/1024)sum_j h_{i,j}^2`.

No unbiasedness claim is made; this is a controlled-final-mean-error estimator.

## Exact gate inequality

With all-in candidate FLOPs `C_i`, a sufficient same-panel improvement gate over R209 is

`(1/100) sum_i H_i^2 max(0.1,C_i/2^41) < 8.170397440117225e-9`.

Additionally every row must satisfy `C_i<2^41`, memory `<=8 GiB`, wall time `<=120 s`, residual time `<=0.4 s`, with no target means used in construction or tuning.

## Fatal first-layer cost

For a zero-bias first layer with invertible `W_1 in R^(1024x1024)`, the map `x -> W_1x` is bijective. Every one of the `2^1024` open orthants therefore has a nonempty inverse image, so the first layer alone has exactly `2^1024` nonempty sign cells. A square Gaussian matrix is nonsingular with probability one.

The cited PCDF construction requires the full activation-polytope set. Even assigning only one elementary operation to each first-layer cell gives

`C_poly >= 2^1024`.

Relative to the complete Phase-2 budget `2^41`, this is at least `2^983`, approximately `10^295.91`, before later layers, sublevel intersections, triangulation, polynomial integration, 1024 output coordinates, CDF refinement, or readout.

Memory fails independently: one impossible bit per first-layer cell is `2^1021` bytes. Against 8 GiB=`2^33` bytes, the factor is `2^988`, approximately `10^297.42`.

This is a lower bound for the **explicit full-polytope mechanism supplied by the primary source**, not a universal impossibility theorem for all exact integration algorithms.

## Distinction from R317/R321

R317/R321 sought a reusable non-Gaussian gate-conditioned state composable through dense ReLU layers. PCDF-MID does not propagate such a state; it asks for a whole-network output CDF by global piecewise-affine geometry and then integrates that CDF.

The mechanism is estimator-distinct, but its sourced constructive realization still touches activation-pattern geometry. A future compressed global-CDF theorem avoiding activation-cell enumeration would be a new route; none was found.

## Preregistered cheapest falsifier / re-entry theorem

No numerical falsifier is justified because the sourced production construction fails analytically before execution.

Re-entry requires, before any run:

1. a non-sampling algorithm for certified output-CDF bounds that avoids explicit first-layer activation-cell enumeration;
2. a proof `C_CDF(1024,16,epsilon)<2^41` and memory `<=8 GiB`;
3. a composable CDF+Gaussian-tail error certificate producing `H_i^2`;
4. target-independent `epsilon,R` with constants capable of satisfying the exact R209 inequality above.

Only after those four items should a separate coordinator allocation authorize an exact-small target-free falsifier.

**Exact missing theorem:** a sub-budget compressed global output-CDF certificate for generic dense width-1024/depth-16 ReLU networks, with rigorous numerical error strong enough to imply the R209 score gate, and without explicit activation-region enumeration.

No such theorem was found in the audited primary literature.

## Verdict

**NO_GO_EXPLICIT_POLYHEDRAL_CDF_CERTIFICATION_EXCEEDS_PHASE2.**

The mean-readout/error conversion is rigorous, but the only sourced constructive CDF mechanism is infeasible by at least `2^983` in compute under the most favorable one-operation-per-first-layer-cell accounting and by `2^988` in memory under the impossible one-bit-per-cell accounting.

No formal queue execution job is proposed.

## Execution accounting

No implementation, code run, estimator run, synthetic/official benchmark, Actions, download/install, paid resource, private/holdout/full access, submission, leaderboard experiment, or main/PR/control/queue/R320 edit was performed.
