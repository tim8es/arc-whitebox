# E119 protocol — generic weight-driven boundary flux with omitted-flux certificate

Idempotency key: `ARC-E119-GENERIC-BOUNDARY-FLUX-CERT-20260919`

Status at freeze: **ONE FROZEN GENERIC CONSTRUCTION/CERTIFICATE RUN AUTHORIZED**.

## Purpose and provenance

E118 established a target-free output-specific boundary-flux sketch on the
verified E114 small corpus. E119 is the deployability bridge requested next:
remove any reliance on a hand-written fixture description and construct the
actual boundary/region state mechanically from arbitrary zero-bias weights for

- input dimension exactly `2`;
- width `<=8`;
- ReLU depth `<=4`.

Branch:
`research/e119-generic-boundary-flux-certificate-20260919`.

Direct parent:
`research/e118-output-specific-flux-sketch-20260919@5db88d151cef14fa32bfbc146188a0cdf10e0f4f`.

No Gaussian plug-in, target fitting, benchmark/public labels, scorer,
holdout/full, production scientific run, tuning, sweep, rescue, canonical
mutation or ledger mutation.

## Frozen scalar observable

For final width `n`:

`c_j=(j+1)/sqrt(sum_{r=1}^n r^2)`.

This is the same deterministic normalized dense observable class used by E118.
It depends only on output coordinate index, not on targets or exact reference.

## Generic weight-driven state construction

Start from one angular sector on the unit circle with coefficient state

`A_0=I_2`,

so `x(theta)=A_0[cos theta,sin theta]^T`.

For every layer weight matrix `W_l` and every current sector `[a,b]`:

1. propagate preactivation coefficients mechanically:
   `P=W_l^T A`;
2. for every neuron row `p=(p_1,p_2)`, solve all roots of
   `p_1 cos(theta)+p_2 sin(theta)=0` lying strictly inside the sector;
3. split the sector at all deduplicated roots;
4. evaluate the midpoint sign of every row to obtain the local ReLU mask;
5. zero inactive rows of `P` and carry the resulting affine coefficient
   matrix to the next layer.

No fixture-specific boundary angle, mask, region coefficient, downstream
adjoint or jump is hard coded.

At final depth, for every adjacent final region pair, construct the scalar
observable derivative jump mechanically:

`Delta_k = c^T (A_right-A_left) t(theta_k)`,

where `t(theta)=(-sin theta,cos theta)`.

Include the periodic `2pi -> 0` boundary.

The generic exact scalar E114 mean is

`mu_full = g * sum_k Delta_k`,

with

`g=sqrt(pi/2)/(2*pi)`.

## Smallest representation under a computable omission certificate

The frozen raw MSE scale is

`E=1.89e-8`.

Therefore an absolute scalar-mean error certificate must satisfy

`B_abs <= sqrt(E)=0.0001374772708486752`.

Since

`|g * sum_{k in omitted} Delta_k|
 <= g * sum_{k in omitted}|Delta_k|`,

define the allowed omitted flux L1 budget

`L = sqrt(E)/g = 0.000689208828456787`.

Sort atoms by the deterministic key

`(|Delta_k|, theta_k, original_index)`.

Omit the longest prefix whose cumulative absolute flux does not exceed `L`.
Retain all remaining atoms.

This is the **minimum retained atom count obtainable by the frozen L1
triangle-inequality certificate**: any set omitting one more atom must have
omitted absolute-flux sum greater than `L`.

The compressed representation stores only the retained pairs
`(theta_k,Delta_k)`.

Its mean is

`mu_kept = g * sum_{retained} Delta_k`.

The computable target-free remainder certificate is

`B_abs = g * sum_{omitted}|Delta_k|`.

By construction,

`|mu_kept-mu_full| <= B_abs`.

No exact reference output mean is used to choose retained atoms.

## Independent exact gate

The existing E114 reusable exact angular harness is used only after generic
construction to independently verify:

- final region count and ordered partition;
- scalar boundary angles;
- scalar derivative jumps;
- full scalar E114 mean.

Matching is performed after deterministic angular ordering with the periodic
zero-angle boundary canonicalized consistently.

## FLOP accounting

The generic constructor runs under `flopscope.BudgetContext`.

Flopscope directly bills all dense coefficient propagation matrix
multiplications used to construct region states.

Scalar geometry that flopscope does not intercept — `atan2`, root
bookkeeping, midpoint trigonometry, comparisons, sorting and scalar jump/cert
arithmetic — is recorded separately in a deterministic conservative manual
operation ledger.

Both are reported:

- `flopscope_dense_flops`: actual BudgetContext count;
- `manual_geometry_flop_equivalent`: conservative explicit scalar count;
- `all_in_accounted_flops = dense + manual`.

The manual ledger uses fixed frozen charges:

- root solve candidate: 32 FLOP-equivalent;
- midpoint sin/cos pair: 32;
- midpoint row sign: 4 per neuron;
- coefficient mask application: 2 per neuron coefficient (two angular coefficients);
- boundary tangent sin/cos pair: 32;
- scalar jump row evaluation: 5 per output coordinate plus 4;
- sort comparison equivalent: conservative `8*N*ceil(log2(max(N,2)))`;
- omission/certificate arithmetic: 6 per boundary.

This is deliberately conservative and deterministic; it does not claim that
transcendentals are one hardware FLOP.

## Frozen corpus

Reuse the verified E114/E118 corpus unchanged:

- width `8`;
- depth `4`;
- input dimension `2`;
- zero bias;
- iid He-normal float64;
- seeds `114200,114201,114202,114203`.

Focused tests must additionally instantiate one width-4/depth-3 random network
to verify generic dimension handling.

No width/depth/seed/certificate sweep.

## Frozen gates

### Generic construction

1. all generic regions/atoms finite;
2. every final region partition is ordered/complete with max gap/overlap
   `<=1e-11`;
3. generic final region count equals independent E114 reference count;
4. generic scalar boundary angle max wrapped error `<=1e-10`;
5. generic scalar jump max abs error vs independent E114 reference
   `<=1e-10`;
6. generic full scalar mean vs independent E114 exact mean
   absolute error `<=1e-10`;
7. deterministic replay max abs `==0`.

### Remainder certificate

8. `abs(mu_kept-mu_full) <= B_abs + 1e-15` on every network;
9. `B_abs^2 <= 1.89e-8` on every network;
10. exact-reference compressed-mean bias MSE `<=1.89e-8` on every network;
11. the retained set is frozen-L1-minimal: adding the next omitted atom to the
    omitted set would exceed `L`, unless all atoms are omitted.

### Accounting / scope

12. BudgetContext dense ledger reconciles exactly;
13. manual geometry ledger deterministic;
14. all-in accounted cost deterministic;
15. no target/public/scorer/holdout/full access.

If any generic construction gate or any remainder-certificate gate fails:

**E119 TERMINAL NO-GO / CLOSE DEPLOYABILITY BRIDGE.**

If all gates pass:

**E119 GENERIC BOUNDARY-FLUX CERTIFICATE GO**.

This authorizes only the mathematical/engineering bridge on width<=8/depth<=4.
It does not authorize a production or benchmark run.

Exactly one frozen workflow run is allowed. No post-result change to the
observable, error scale, omission ordering, charge schedule, seeds, width or
depth.
