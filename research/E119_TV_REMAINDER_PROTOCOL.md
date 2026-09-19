# E119 mathematical scout — output-specific omitted-flux TV certificate

Idempotency key: `ARC-E119-OUTPUT-FLUX-TV-REMAINDER-20260919`

Status at freeze: **ONE EXACT SMALL-WIDTH CERTIFICATE FALSIFIER AUTHORIZED**.

## Identity and non-duplication

This is a separate E119 mathematical-scout lane from
`research/e119-generic-boundary-flux-certificate-20260919`.

Parent:
`research/e118-output-specific-flux-sketch-20260919@5db88d151cef14fa32bfbc146188a0cdf10e0f4f`.

E118 established a 1024-cell scalar boundary-flux sketch with very small exact
bias on the frozen width-8/depth-4 corpus, but did not provide a deployable
rigorous omitted-boundary remainder.

This lane derives the cheapest weight-only computable total-variation upper
bound I know for the omitted scalar boundary flux. It uses no exact boundary
locations or reference mean in candidate construction.

No E104-E118 mechanism is reopened. No public/public-mini, benchmark target,
scorer, holdout/full, production scientific run, tuning, sweep, rescue,
canonical/ledger mutation or merge.

## Scalar observable and E118 sketch error identity

Use the same normalized dense output-specific observable as E118:

`c_j=(j+1)/sqrt(sum_{r=1}^n r^2)`.

For the scalar homogeneous piecewise-linear output `F_c`, write its
restriction to the circle as `f(theta)`. Let the derivative jumps at true
activation boundaries be `Delta_k`.

E118 uses a uniform `M=1024` angular grid. For a boundary in one cell, let
`epsilon_k` be its displacement from that cell midpoint, so

`|epsilon_k| <= pi/M`.

The exact flux contribution is `Delta_k`; the E118 midpoint atom contributes

`Delta_k cos(epsilon_k)`.

Therefore the exact omitted-flux error is

`err = g * sum_k Delta_k [cos(epsilon_k)-1]`

with

`g=sqrt(pi/2)/(2*pi)`.

Hence

`|err| <= g * eta_M * TV(F_c)`

where

`eta_M = 1-cos(pi/M)`

and

`TV(F_c)=sum_k |Delta_k|`.

For `M=1024` and requested scalar RMS/absolute scale

`T = 1.3747727085e-4`,

a sufficient condition is

`TV_bound <= T/(g*eta_M)`.

The frozen threshold implied by this identity is approximately `146.4473`.

## Weight-only total-variation recursion

For any continuous homogeneous piecewise-linear scalar function on R^2, let

`mu_f = f'' + f`

on the unit circle in the distributional sense and define

`V(f)=||mu_f||_TV=sum |derivative jumps|`.

For a nonnegative activation `h), also define

`A(h)=integral_0^{2pi} h(theta) dtheta`.

### First ReLU layer

For one first-layer neuron

`h(theta)=ReLU(w^T q(theta))`,

both quantities are exact:

`A(h)=V(h)=2||w||_2`.

Thus initialize vectors

`A_1[j]=V_1[j]=2||W_1[:,j]||_2`.

### Dense affine combination

For

`z_j=sum_i W[i,j] h_i`,

because `h_i>=0`,

`A(ReLU(z_j)) <= sum_i max(W[i,j],0) A(h_i)`.

Also by linearity of the boundary measure and triangle inequality,

`V(z_j) <= sum_i |W[i,j]| V(h_i)`.

### ReLU boundary creation

On each positive connected component of `z_j`, integrating
`z_j''+z_j=mu_z` shows that the total slope entering/leaving the component is
at most its positive-area integral plus the inherited variation inside the
component.

Therefore the output ReLU variation obeys the computable bound

`V(ReLU(z_j)) <= A(ReLU(z_j)) + 2 V(z_j)`.

Combining the previous inequalities gives the recursive candidate certificate

`A_next <= W_+^T A`

`V_next <= A_next + 2 |W|^T V`.

For the final scalar observable,

`TV(F_c) <= |c|^T V_L`.

The deployable omitted-boundary mean certificate is therefore

`B_abs = g * eta_M * |c|^T V_L`.

This requires only matrix-vector absolute/positive-weight propagation. It does
not enumerate masks, regions, boundaries, roots or exact flux atoms.

## Frozen exact corpus

Reuse E118 unchanged:

- input dimension: 2
- width: 8
- depth: 4
- zero bias
- iid He-normal float64 weights
- seeds: 114200, 114201, 114202, 114203
- cells: 1024
- RMS gate: `1.3747727085e-4`.

The E114 exact angular reference is verifier-only.

For every network the verifier records:

1. weight-only `A_l,V_l` recurrence;
2. final `TV_bound`;
3. computable `B_abs`;
4. exact scalar total variation `TV_exact=sum |boundary_jumps @ c|`;
5. exact E118 sketch bias;
6. exact inequality checks `TV_exact<=TV_bound` and `|bias|<=B_abs`.

## Frozen decision gate

Integrity requires:

- all candidate arrays finite;
- exact-reference flux identity remains valid;
- `TV_exact <= TV_bound + 1e-12` for every network;
- exact E118 sketch absolute bias `<= B_abs + 1e-12` for every network;
- deterministic replay exactly equal;
- no target/public/scorer/holdout/full access.

Scientific gate:

`RMS_bound = sqrt(mean_seed B_abs(seed)^2) <= 1.3747727085e-4`.

If the scientific gate fails:

**TERMINAL MATHEMATICAL NO-GO / CLOSE THIS OMITTED-FLUX CERTIFICATE.**

No alternate norm, empirical calibration factor, boundary-count correction,
cell count, seed, width/depth, observable, cancellation heuristic or rescue
under this E119 identity.

If it passes, only a separately preregistered production certificate
implementation would be authorized.

## Production-cost note

The recurrence requires two dense matrix-vector style accumulations per later
layer plus first-layer column norms. At width 1024/depth 16 this is negligible
relative to E118's frozen production upper `73,719,476,736` FLOPs and cannot
be the limiting gate. E119's decisive question is certificate tightness, not
compute.
