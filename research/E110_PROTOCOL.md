# E110 protocol — deep-Jacobian output-specific fourth-harmonic control

Idempotency key: `ARC-E110-DEEP-JACOBIAN-H4-20260919`

Status at protocol freeze: **SMALL EXACT FALSIFIER ONLY**

## Provenance / non-duplication

- Branch: `research/e110-deep-jacobian-fourth-harmonic-20260919`
- Direct parent: terminal E108 branch `research/e108-firstlayer-exactmean-transport-cv-20260919`
- E108 blocker: a first-layer exact-mean fluctuation propagated linearly through a fixed downstream `0.5` Jacobian reduced production-shaped target-free risk by only `0.2751713739%`.
- E109 is already reserved as `research/e109-deep-stein-jvp-cv-20260919`; E110 does not reuse that lane.
- Closed lanes excluded: E038 Sobol/QMC, E100 shrinkage, E105 risk-only certificate, E106 first-layer-weight quartic cross-fit, E107 exact fourth-moment cubature, E108 first-layer exact-mean transported CV.

E110 targets a different component: the **deep network output's fourth angular harmonic**, with a separate control direction for every final output coordinate derived from the full depth Jacobian.

No public/public-mini, benchmark targets, official scorer, holdout/full, tuning, seed/rank/sample sweep, rescue, canonical mutation, ledger mutation, or merge.

## Candidate mechanism

For row-vector input `x`, the frozen mean-field linearization of a depth-`L` zero-bias ReLU network is

`J = (0.5 W1.T)(0.5 W2.T)...(0.5 WL.T)`.

For final coordinate `j`, let `u_j = J[:,j] / ||J[:,j]||`.

For a unit spherical direction `q in S^(n-1)`, define

`z_j(q) = (q^T u_j)^4 - 3/(n(n+2))`.

This has exact spherical expectation zero for every fixed network-derived `u_j`.

Unlike E106, which used 256 normalized **first-layer weight rows** as generic quartic features for every output, E110 uses exactly one **full-depth output-specific sensitivity direction** per final coordinate.

For each E104 Haar block, average `z_j(q)` over its positive orthogonal directions. Antipodes need not be recomputed because the feature is even.

At production shape, one scalar coefficient per final output is fitted on one independent Haar block and applied only to the other; the symmetric cross-fit estimator remains unbiased.

## Stage S — exact small falsifier

Frozen small network:

- width `n=2`
- depth `L=4`
- zero bias
- iid Gaussian weights scaled by `sqrt(2/n)`
- weight seed `110004`
- float64 scientific calculation.

In two dimensions one Haar block is an orthonormal basis determined by one angle `theta`. Including antipodes, the block estimate for final coordinate `j` is

`B_j(theta) = [f_j(theta)+f_j(theta+pi/2)+f_j(theta+pi)+f_j(theta+3pi/2)]/4`.

Because a bias-free ReLU network is piecewise linear in the input, on each angular sector

`f_j(theta) = a_j cos(theta) + b_j sin(theta)`.

The falsifier must recursively enumerate all ReLU sign-sector boundaries through all four layers. On each final sector, the representation above is exact up to float64 root arithmetic.

For `n=2`, the Haar-block average of the E110 quartic control is exactly

`Z_j(theta) = (1/8) cos(4(theta-phi_j))`

where `phi_j = atan2(u_j[1],u_j[0])`.

The script must integrate, analytically and sector-by-sector over `theta in [0,pi/2]`:

- `E[B_j]`
- `Var(B_j)`
- `Cov(B_j,Z_j)`
- `Var(Z_j)=1/128`.

The oracle scalar-control residual variance is

`Vres_j = Var(B_j) - Cov(B_j,Z_j)^2 / Var(Z_j)`.

This oracle coefficient is used **only as a mechanistic exact falsifier**. It is not a production coefficient and uses no competition target.

Aggregate exact gate:

`pooled_ratio = sum_j Vres_j / sum_j Var(B_j)`.

### Stage-S gates

All must pass to authorize any production-shaped prototype:

1. recursive sector partition validates against direct network evaluation at deterministic interior check points with max absolute error `<=1e-10`;
2. all sector integrals finite;
3. all nondegenerate output block variances positive;
4. analytic control mean is exactly zero by formula;
5. `pooled_ratio <= 0.50` (at least 2x exact block-variance reduction);
6. every nondegenerate output has residual variance ratio `<=0.80`;
7. no external/benchmark/public/scorer/holdout/full access.

If any Stage-S gate fails, E110 terminates **NO-GO / DROP**. No production prototype, rescue, alternate seed, alternate harmonic, or rerun.

## Conditional production admission

Production is **not authorized at this protocol commit**.

Only after a single successful Stage-S execution may a successor commit evaluate the following frozen budget admission before arming production:

- width `1024`, depth `16`
- E104/E105 base estimate: `149,114,550,960` FLOPs
- full mean-field Jacobian product: at most 15 dense `1024^3` matmuls at `2n^3` each = `32,212,254,720` FLOPs
- projection of 2048 positive Haar directions onto 1024 output-specific directions: `4,294,967,296` FLOPs
- normalization/quartic/reductions/cross-fit/finalization reserve: `4,000,000,000` FLOPs
- conservative conditional total: `189,621,772,976` FLOPs
- conditional utilization: `0.086229294... < 0.13`.

A production-shaped prototype may be armed only if Stage-S passes and the implementation-specific frozen admission remains `<=0.13`.

## Production scientific gate if later authorized

A production-shaped prototype, if authorized, must use one frozen synthetic `1024x16` network and exactly two independent E104 estimator realizations plus deterministic replay. It must compare candidate vs baseline target-free A/B risk on identical Haar blocks. No benchmark target may be read.

Production GO would require all of:

- measured utilization `<=0.13`;
- exact FLOP reconciliation;
- candidate risk < baseline risk;
- candidate target-free raw risk `<=1.89e-8`;
- adjusted-risk proxy `<2.5e-9`;
- finite / deterministic / exact antithetic structural gates.

Any failure => terminal DROP, no rerun/rescue.
