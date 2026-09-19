# E115 protocol — dense Hermite chaos transport with certified remainder

Idempotency key: `ARC-E115-HERMITE-CHAOS-CERTIFIED-TAIL-20260919`

Status: **PREREGISTERED / BUDGET-FIRST EXACT FALSIFIER ONLY**.

## Provenance and non-duplication

- Branch: `research/e115-hermite-chaos-certified-tail-20260919`.
- Parent: `research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`.
- E104-E110 sampler/control/moment/Haar/Stein/line mechanisms are not reused.
- E111's mechanism was a Gaussian-ReLU late-layer plug-in; E115 instead represents non-Gaussian dependence in a common Gaussian latent basis using multivariate probabilists' Hermite polynomials.
- E112 mask/treewidth, E114 activation-boundary flux, QMC/cubature, latent mixtures, target fitting, public/scorer/holdout/full execution are excluded.

## Mechanism

For standard Gaussian latent `X in R^d`, represent each activation by the total-degree Hermite expansion

`f(X) = sum_{|alpha|>=0} c_alpha He_alpha(X)`.

Orthogonality gives the exact Parseval identity

`E[(f-P_p f)^2] = sum_{|alpha|>p} alpha! c_alpha^2`

for the degree-`p` projection `P_p`. Thus truncation carries an exact L2 remainder certificate rather than an unmeasured Gaussian-shape assumption.

The full dense basis through degree `p` has

`B(d,p) = C(d+p,p)`

states per scalar activation.

## Exact scalar ReLU falsifier

Let `Z ~ N(0,1)` and `f(Z)=ReLU(Z)`. For probabilists' Hermites,

- `c0 = E[f] = 1/sqrt(2*pi)`,
- `c1 = E[f He1] = 1/2`,
- `c2 = E[f He2]/2! = 1/(2*sqrt(2*pi))`,
- `E[f^2]=1/2`.

Therefore the exact certified tails are

`R1 = E[(f-P1 f)^2] = 1/4 - 1/(2*pi)`,

`R2 = E[(f-P2 f)^2] = 1/4 - 3/(4*pi)`.

No Monte Carlo or numerical quadrature is allowed.

## Production-shaped admission lower bound

Freeze `d=1024`, width `w=1024`, and only **two** late dense layers. Before any nonlinear reprojection, normalization, bookkeeping, or inherited estimator cost, transporting a dense chaos coefficient matrix through one width-`w` linear layer costs at least

`2*w*w*B(d,p)` FLOPs

(counting multiply+add as 2 FLOPs). The two-layer lower bound is therefore

`F_min(p) = 4*w^2*B(d,p)`.

Budget: `2^41`. Admission cap: utilization `<=0.13`.

This lower bound is intentionally favorable to E115: it excludes every nonlinear projection cost and all base-estimator work.

## Frozen gates

The sole executable must deterministically verify:

1. exact closed-form `R1` and `R2`;
2. `R1 > 1.89e-8` and `R2 > 1.89e-8`;
3. exact basis counts `B(1024,1)=1025`, `B(1024,2)=525825`;
4. exact two-layer transport lower bounds and utilization;
5. degree 1 passes `<=0.13` admission;
6. degree 2 fails `<=0.13` admission;
7. deterministic replay is bitwise-identical JSON.

## Frozen decision

- If degree 1 is scientifically sufficient, the lane may proceed.
- Else if degree 2 passes budget admission, a richer exact small-width implementation would be admissible.
- If degree 1 fails the exact scalar remainder gate **and** degree 2 fails the favorable two-layer cost lower bound, record **TERMINAL NO-GO for dense total-degree Hermite chaos transport**.

This verdict does not rule out a different low-rank/tensorized chaos mechanism; that would require a new experiment identity and an explicit rank-growth certificate.
