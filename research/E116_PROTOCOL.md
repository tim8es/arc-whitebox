# E116 protocol — output-specific linear transport obstruction by exact gradient span

Idempotency key: `ARC-E116-OUTPUT-SPECIFIC-GRADIENT-SPAN-20260919`

Status at freeze: **ONE EXACT STRUCTURAL FALSIFIER ONLY**.

## Identity / occupancy

The requested E114 identity is already occupied and sealed by
`research/e114-activation-boundary-flux-20260919`; both E115 identities are
also occupied. This non-duplicative lane therefore uses E116.

Branch: `research/e116-output-specific-gradient-span-20260919`.

Parent: E113 terminal receipt commit
`de83981a8264748c5a6e57070c6897c1b457f77c`.

No public/public-mini, benchmark targets, scorer, holdout/full, tuning, sweep,
rescue, rerun, canonical/ledger mutation, or merge.

## Chosen class

**Output-specific transport.**

The candidate asks whether a scalar final observable of a dense zero-bias ReLU
MLP can be represented exactly through a fixed low-dimensional linear transport

`F(x) = g(U^T x)`,  `U in R^(d x k)`,  `k << d`,

without carrying the complete activation mask state and without factorizing
later-layer marginals.

The scalar observable is fixed before execution:

`F(x) = sum_{j=1}^8 j * h_{4,j}(x)`.

It is weight-independent, target-free, dense across final coordinates, and
avoids the degenerate case where one final ReLU coordinate is identically zero.

## Exact obstruction theorem

Let `F:R^d->R` be differentiable at points `x_1,...,x_m` and suppose

`F(x)=g(U^T x)`

for some arbitrary function `g` and linear map `U:R^k->R^d`.

For every `v in ker(U^T)`, `U^T(x+t v)=U^T x`, hence
`F(x+t v)=F(x)`. At every differentiability point,

`grad F(x)^T v = 0`.

Therefore every observed region gradient lies in `col(U)`, and

`rank span{grad F(x_i)} <= k`.

Consequently, if `d` differentiability points have gradients with nonzero
`d x d` determinant, every exact fixed linear output-specific transport must
have `k>=d`. There is then **no dimension reduction at all**.

This theorem does not require `g` to be differentiable.

It rules out only fixed linear projection transport for the scalar observable.
It does not rule out nonlinear/discontinuous sufficient statistics, adaptive
region-dependent transports, approximation, or boundary-flux/diagram methods.

## Frozen actual dense random MLP instance

- input width `d=8`;
- four ReLU layers, each width `8`;
- zero bias;
- every weight entry iid standard Gaussian from NumPy PCG64 seed `116116`,
  multiplied by He factor `sqrt(2/8)=1/2`;
- float64 generation;
- scalar observable `F(x)=sum_j (j+1) h_{4,j}(x)`;
- candidate points are the 16 signed coordinate vectors in fixed order
  `(+e1,-e1,+e2,-e2,...,+e8,-e8)`.

No random search is permitted after freeze.

## Exact arithmetic certificate

IEEE-754 float64 values are exact dyadic rationals. The executable converts
every frozen weight with `Fraction.from_float` and propagates the selected
points with exact rational arithmetic.

The frozen eight certificate rows are point indices

`[0,1,2,3,4,5,6,8]`

from the 16-point list.

For each selected point the executable must:

1. propagate all four layers exactly as rational numbers;
2. certify every preactivation is nonzero, so the point lies strictly inside a
   differentiable activation region;
3. backpropagate the exact scalar gradient using the certified masks;
4. form the exact `8 x 8` gradient matrix;
5. compute its determinant using exact Fraction Gaussian elimination;
6. require the determinant to be exactly nonzero.

The executable also computes the float64 forward/backward version and requires
its activation masks to match the exact rational masks.

## Frozen gates

1. all four generated weight matrices have numeric rank 8;
2. all 256 generated weights are nonzero;
3. all selected exact preactivations are nonzero;
4. float64 and exact-rational activation masks match exactly;
5. exact gradient determinant is nonzero;
6. exact gradient span rank is therefore 8;
7. deterministic replay JSON is bitwise identical;
8. no external/target access.

### Decision

If Gates 1–8 pass:

**TERMINAL STRUCTURAL NO-GO for exact dimension-reducing fixed linear
output-specific transport of this scalar observable.**

The exact certificate forces `k>=8=d` on the frozen dense random network.
Because the mechanism's intended compression is `k<d`, no production-shaped
prototype is authorized.

If any exact certificate gate fails, record **INSTRUMENT NO-GO** only. No seed,
observable, point set, certificate rows, architecture, or transport class may
be changed after execution.
