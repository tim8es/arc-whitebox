# E112 Protocol — fourth-order Edgeworth Gaussian-ReLU plug-in

Idempotency key: `ARC-E112-EDGEWORTH4-RELU-PLUGIN-20260919`

Status: **PREREGISTERED / EXACT SMALL-WIDTH SCIENTIFIC GATE**.

## Identity and disjointness

E112 is a deterministic scalar marginal closure. It is not a sampler, control variate, fitted residual model, latent-mixture closure, or Gaussian first-two-moment plug-in.

Closed lanes E104-E111 remain closed. In particular:

- E104/E105 radial/Haar sampling is inherited only as the production trajectory source/cost base;
- E106/E108/E109 control-variate families are not reused;
- E111 established that the plain Gaussian ReLU plug-in using only exact mean/variance has irreducible later-layer bias.

E112 adds **standardized third and fourth cumulants** to the scalar pre-ReLU marginal and applies the frozen fourth-order Edgeworth correction to the positive-part mean.

No public/public-mini/scorer/holdout/full targets, tuning, sweep, rescue, or rerun.

## Frozen formula

For scalar preactivation `Z` with exact/estimated
`mu`, `sigma^2>0`, standardized skewness `g1`, and excess kurtosis `g2`, set

`a=-mu/sigma`, `phi=exp(-a^2/2)/sqrt(2*pi)`.

The Gaussian positive-part mean is

`G = sigma*phi + mu*Phi(mu/sigma)`.

The frozen Edgeworth-4 correction is

`E4 = G + sigma*phi * [ (g1/6) H1(a) + (g2/24) H2(a) + (g1^2/72) H4(a) ]`

with probabilists' Hermite polynomials

- `H1(a)=a`
- `H2(a)=a^2-1`
- `H4(a)=a^4-6a^2+3`.

No clipping, positivity repair, coefficient damping, term deletion, or alternate expansion is allowed.

If `sigma^2<=1e-15`, use deterministic `max(mu,0)`.

## Exact small-width truth gate

Frozen network family:

- input: `X~N(0,I_2)`
- width: `8`
- depth: `4`
- zero biases
- He Gaussian weights
- PCG64 weight seed: `112112`
- float64 reference arithmetic

Positive homogeneity reduces the exact law to angular sectors and Rayleigh radius. The verifier must recursively split `[0,2pi)` at every exact preactivation zero. On every fixed-mask sector, each preactivation is exactly

`R*(a cos(theta)+b sin(theta))`.

Angular powers 1..4 are integrated analytically; radial moments are exact:

`E[R^k]=2^(k/2) Gamma(1+k/2)`.

Thus exact pre-ReLU raw moments 1..4 and exact post-ReLU means are available without Monte Carlo or numerical quadrature.

The Edgeworth candidate is evaluated from those exact moments. Any error is deterministic closure bias.

## Exact-gate metrics

Record per layer:

- exact post-ReLU mean;
- Gaussian plug-in mean;
- E112 Edgeworth-4 mean;
- Gaussian bias MSE;
- E112 bias MSE;
- E112/Gaussian bias-MSE ratio;
- max absolute E112 bias;
- skewness/kurtosis ranges.

Aggregate:

- pooled all-layer E112 bias MSE;
- final-layer E112 bias MSE;
- final-layer Gaussian bias MSE;
- final E112/Gaussian ratio.

## Scientific gates

All integrity gates must pass:

1. exact reference finite;
2. E112 finite;
3. deterministic exact replay max abs `==0`;
4. first-layer E112 bias MSE `<=1e-24`.

A mechanism survives only if:

5. final-layer E112 bias MSE `<=1.89e-8`;
6. pooled all-layer E112 bias MSE `<=1.89e-8`;
7. final-layer E112 bias MSE is strictly below plain Gaussian bias MSE.

Failure of any of 5-7 => **TERMINAL NO-GO / DROP E112**.

A pass is **SMALL-EXACT SCIENTIFIC GO ONLY** and authorizes exactly one production-shaped synthetic gate defined after the result. It does not grant competition/public GO.

## Production cost admission

Inherited E111/E104 all-in upper:
`149,220,512,434` FLOPs.

Frozen conservative E112 increment allowance for four production late layers:

- third/fourth raw-moment reductions over existing `4096x1024` pre-ReLU arrays;
- central-moment transforms;
- skew/excess-kurtosis transforms;
- Edgeworth scalar formula;
- deterministic bookkeeping;

bounded by `500,000,000` FLOPs.

Pre-code all-in upper:

`149,720,512,434` FLOPs.

Utilization:

`149720512434 / 2^41 = 0.06808500640272541 < 0.13`.

No fresh RNG or forward trajectories are allowed.

## One-run rule

Protocol commit first. Then implementation/tests/verifier may be committed. The scientific workflow is armed once, path-isolated, and runs exactly one frozen local synthetic exact gate. No scientific rerun or parameter change under E112.
