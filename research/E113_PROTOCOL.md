# E113 Protocol — top-4 actual-gate-conditioned Gaussian-ReLU plug-in

Idempotency key: `ARC-E113-TOP4-GATE-CONDITIONED-PLUGIN-20260919`

Status: **PREREGISTERED / EXACT SMALL-WIDTH SCIENTIFIC GATE**.

## Identity and disjointness

E113 is a deterministic **structural conditional closure**, not a sampler/control variant and not a fitted latent mixture.

It conditions on actual upstream ReLU gate states already present in the network, rather than fitting a hidden mixture component. It does not reopen E099 latent-mixture closure, E109 mean-field gate-pair controls, or E111 unconditional Gaussian plug-in.

No public/public-mini/scorer/holdout/full targets, tuning, sweep, rescue, or rerun.

## Frozen mechanism

For each output preactivation coordinate `Z_j` in a later layer:

1. inspect its incoming weight column;
2. choose exactly the four parent indices with largest `|w_{ij}|`, ties by lower index;
3. form the observed four-bit parent gate state
   `S_j in {0,...,15}`, where each bit is `1[h_i>0]`;
4. estimate/compute `p_s=P(S_j=s)`, `mu_s=E[Z_j|S_j=s]`, and `v_s=Var(Z_j|S_j=s)`;
5. report
   `sum_s p_s * GaussianReLUMean(mu_s,v_s)`.

Empty states contribute zero. If `v_s<=1e-15`, use deterministic `max(mu_s,0)`.

The first layer remains the ordinary exact Gaussian plug-in; gate conditioning starts at layer 2.

There is no fitted coefficient, latent variable, ridge, clipping, state merge, state pruning, alternative parent selector, or mixture optimization.

## Exact small-width truth gate

Frozen network:

- `X~N(0,I_2)`
- width `8`
- depth `4`
- zero biases
- He Gaussian weights
- PCG64 seed `113113`
- float64

As in E111, recursively split the full angular circle at every exact preactivation zero. On each resulting interval the complete upstream ReLU gate pattern is constant and each preactivation is a known linear form in `cos(theta),sin(theta)`.

For every output and every selected four-gate state, integrate exactly:

- state probability from angular interval length;
- first preactivation moment using exact `E[R]`;
- second preactivation moment using exact `E[R^2]`;
- exact post-ReLU mean for the truth comparator.

Thus the conditional Gaussian candidate and truth are both target-free and evaluated against an exact small-width reference with no Monte Carlo or numerical quadrature.

## Metrics

Per layer:

- exact post-ReLU mean;
- unconditional Gaussian plug-in mean;
- E113 top-4 gate-conditioned mean;
- unconditional Gaussian bias MSE;
- E113 bias MSE;
- E113/Gaussian bias-MSE ratio;
- max absolute E113 bias;
- occupied state counts.

Aggregate:

- pooled all-layer E113 bias MSE;
- final-layer E113 bias MSE;
- final unconditional Gaussian bias MSE;
- final E113/Gaussian ratio.

## Scientific gates

Integrity:

1. exact reference finite;
2. all state probabilities/moments/candidate outputs finite;
3. for every coordinate, state probabilities sum to one within `1e-14`;
4. deterministic replay max abs `==0`;
5. first-layer bias MSE `<=1e-24`.

Mechanism survives only if:

6. final-layer E113 bias MSE `<=1.89e-8`;
7. pooled all-layer E113 bias MSE `<=1.89e-8`;
8. final-layer E113 bias MSE is strictly below unconditional Gaussian bias MSE.

Failure => **TERMINAL NO-GO / DROP E113**.

Pass => **SMALL-EXACT SCIENTIFIC GO ONLY** and authorizes one production-shaped synthetic gate defined after the result.

## Production cost admission

Inherited E111/E104 all-in upper:
`149,220,512,434` FLOPs.

Frozen conservative E113 increment allowance for the four production late layers:

- top-4 selector over each `1024x1024` weight matrix;
- gate-state extraction from already-computed previous-layer activations;
- 16-state counts, first/second conditional reductions for every output;
- 16-state Gaussian-ReLU transforms and reductions;
- bookkeeping;

bounded by `2,500,000,000` FLOPs.

Pre-code all-in upper:

`151,720,512,434` FLOPs.

Utilization:

`151720512434 / 2^41 = 0.06899450110449834 < 0.13`.

No fresh RNG or forward trajectories.

## One-run rule

Protocol commit first. Then implementation/tests/verifier. Exactly one path-isolated frozen local exact-gate workflow may execute. No parent-count change, alternate selector, state merge, seed/width/depth change, rescue, tuning, or rerun.
