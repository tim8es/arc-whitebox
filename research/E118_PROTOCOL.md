# E118 Protocol — physical scalar activation-boundary-flux compression

Idempotency key: `ARC-E118-BOUNDARY-FLUX-PHYSICAL-COMPRESSION-20260919`

Status: **PREREGISTERED / ONE EXACT SMALL-WIDTH RUN ONLY**.

## Provenance

- Branch: `research/e118-boundary-flux-physical-compression-20260919`.
- Parent: verified E114 activation-boundary-flux branch
  `research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`.
- E114 exact identity is reused only as truth/reference infrastructure.
- E118 must construct an actual explicit boundary-state algorithm. It may not use the exact final boundary list, exact final flux contributions, benchmark targets, or post-hoc oracle ranking to choose retained states.

No reopening of E104-E111, no Gaussian plug-in, no mask-table/treewidth closure, no top-k gate conditioning, no sampler/control variant, no public/scorer/holdout/full.

## Scalar observable

For width `n`, define the single final scalar observable

`s(x) = 1/sqrt(n) * sum_j h_L,j(x)`.

Only `E[s(X)]` is estimated.

For `X=RQ`, `Q` uniform on the unit circle in the frozen small-width gate and zero-bias positive homogeneity,

`E[s(X)] = E[R]/(2*pi) * integral s(q(theta)) dtheta`.

E114's boundary-flux identity makes this equal to the sum of final scalar tangent-derivative jumps. E118 materializes the same piecewise-linear angular state physically but is allowed to stop before full refinement and must certify the unresolved remainder.

## Physical boundary state

A state after layer `ell` is exactly

`(ell, theta_lo, theta_hi, A_ell)`

where on that angular cell

`h_ell(q(theta)) = A_ell q(theta)`.

The state therefore stores real hidden linear coefficients, not only a mask id or an oracle boundary score.

To expand one state:

1. compute `P = W_{ell+1} A_ell`;
2. find every exact root of every row `p_i^T q(theta)=0` inside the current interval;
3. split at those roots;
4. choose each child mask from an interior angle;
5. zero inactive rows of `P`;
6. materialize each child state explicitly.

At `ell=L`, the scalar coefficient is
`a = ones^T A_L/sqrt(n)` and its sector integral is analytic.

The exact reference performs this refinement to exhaustion. The candidate does not.

## Deterministic best-first compression

The candidate maintains a priority queue of unresolved physical states.

For state `I=(ell,lo,hi,A)`, define the target-free observable envelope

`U(I) = E[R]/(2*pi) * (hi-lo) * ||A||_F * prod_{m=ell+1..L} ||W_m||_F`.

This is rigorous because ReLU is 1-Lipschitz,

`||A||_2 <= ||A||_F`,

and the final observable vector has Euclidean norm one.

Thus if an unresolved state is replaced by zero, its absolute contribution to the scalar mean is at most `U(I)`.

Frozen rule:

- initialize with the full circle state;
- repeatedly expand the unresolved state with largest `U(I)`;
- final-layer children are integrated exactly and removed from the queue;
- stop after exactly the frozen transition cap or when the queue is empty;
- candidate estimate = sum of exact resolved final-sector integrals;
- remainder certificate = sum of `U(I)` over all unresolved states.

No exact-reference value or exact final-boundary contribution enters queue ordering.

Therefore

`|candidate_mean - exact_mean| <= remainder_certificate`

must hold.

## Frozen small-width run

- input dimension: 2;
- width: 8;
- depth: 4;
- zero bias;
- He Gaussian float64 weights;
- PCG64 weight seed: `118118`;
- observable: normalized final-coordinate sum;
- exact reference: full angular refinement;
- candidate expansion cap: `62`;
- no numerical quadrature;
- no Monte Carlo truth;
- no rerun.

Required artifact fields include:

- exact final mean;
- exact final interval count;
- exact boundary-flux jump sum and sector-integral agreement;
- candidate mean;
- actual absolute error;
- certified unresolved remainder;
- all physical state counts by layer;
- total expansions;
- total child states materialized;
- max live queue;
- unresolved state count;
- serialized coefficient-state bytes;
- root/helper counts;
- deterministic replay.

## Error gate

Frozen total RMS/absolute scalar error limit:

`E_max = 1.37477270849e-4`.

All must pass:

1. exact boundary-flux sum agrees with exact sector integral to `<=1e-12`;
2. actual candidate error `<= remainder + 1e-12`;
3. remainder certificate `<= E_max`;
4. actual absolute error `<= E_max`;
5. deterministic replay max absolute difference `==0`;
6. all values finite.

Failure of 3 or 4 => **TERMINAL NO-GO**. No expansion-cap/seed/network/bound change or rerun.

## Production incremental budget

Hard incremental budget:

`F_inc_max = 136,758,472,261` FLOPs.

A single exact production region-state propagation must materialize

`W A`, with `W,A in R^(1024x1024)`, costing at least

`F_transition = 2*1024^3 = 2,147,483,648` FLOPs.

Freeze:

- maximum region expansions: `62`;
- 62 dense transitions:
  `133,143,986,176` FLOPs;
- reserved all-in helpers/state materialization/remainder accounting:
  `3,600,000,000` FLOPs;
- frozen all-in incremental ceiling:
  `136,743,986,176` FLOPs;
- remaining margin:
  `14,486,085` FLOPs.

This is already an optimistic ceiling: production high-dimensional cone splitting may require more than the helper reserve. Therefore E118 production physicality requires both:

A. the exact small-width 62-expansion remainder gate passes; and  
B. a concrete high-dimensional cone/materialization implementation can fit the frozen helper reserve.

If A fails, E118 is terminal immediately and B is not pursued.

## Production state lower bound

Each live production state must at minimum store its dense linear map
`A in R^(1024x1024)`:

- float32 coefficient bytes/state: `4,194,304`;
- this excludes cone facets, masks, queue metadata and helper buffers.

The small-width artifact must report the maximum live-state count, so the corresponding production dense-state memory lower bound is explicit.

## Verdict

If the frozen small exact run passes all integrity and error gates, E118 receives only **SMALL-EXACT PHYSICAL REPRESENTATION GO**, and the next gate is a production cone/materialization-cost proof under the remaining helper reserve.

Otherwise:

**TERMINAL NO-GO / DROP E118.**

No rescue, rerun, tuning, public evaluation, canonical mutation, or ledger mutation.
