# E107 protocol — exact spherical fourth-moment cubature bound

Idempotency key: `ARC-E107-SPHERICAL-M4-CUBATURE-BOUND-20260919`

Status at protocol freeze: **PRE-CODE ADMISSION CHECK ONLY**

## Hypothesis

After E104 analytically removes chi-radius noise and antithetic pairing removes the global odd component, replace stochastic Haar direction averaging by an exact weighted angular cubature that matches every even polynomial through degree four on `S^{d-1}`.

The hoped-for mechanism is deterministic angular moment exactness, not a fitted control variate and not a new Monte Carlo/QMC sampler.

Production constants are frozen before any implementation:

- `d = n = 1024`
- `L = 16`
- budget `B = 2^41 = 2199023255552`
- admission utilization cap `u <= 0.13`
- raw target `<= 1.89e-8`
- one true-network trajectory forward cost `C_fwd = 2 L n^2 = 33554432 = B/65536`

No public/public-mini/scorer/holdout/full target may be read for this admission check.

## Exact fourth-moment rank gate

For a direction `q in S^{d-1}`, define the symmetric rank-one matrix

`X(q) = q q^T`.

Vectorize the upper-triangular symmetric coordinates as `v(q) = vec_sym(X(q)) in R^D`, where

`D = dim Sym_d = d(d+1)/2`.

The exact spherical fourth-moment operator is

`M4 = E_q[v(q) v(q)^T]`.

For every nonzero symmetric matrix `A`,

`vec_sym(A)^T M4 vec_sym(A) = E_q[(q^T A q)^2] > 0`.

Therefore `M4` is positive definite on `Sym_d` and

`rank(M4) = D`.

Any exact weighted discrete cubature with directions `q_i` and arbitrary real weights `w_i` has fourth-moment operator

`M4_hat = sum_{i=1}^N w_i v(q_i) v(q_i)^T`.

Each summand has rank at most one, so

`rank(M4_hat) <= N`.

Exact equality `M4_hat = M4` therefore requires

`N >= D = d(d+1)/2`.

At `d=1024`:

`D = 1024*1025/2 = 524800` distinct directions minimum.

This is a necessary rank bound for exact weighted fourth-moment matching; it does not assume positive weights.

## Production cost admission

Even granting impossible free setup, free cubature weights, free reduction, and only one network forward per direction:

`F_min = 524800 * 33554432 = 17609365913600 FLOPs`.

Equivalent utilization:

`u_min = F_min / B = 524800/65536 = 8.0078125`.

Admission cap:

`u_cap = 0.13`.

Violation factor:

`u_min/u_cap = 61.59855769230769`.

The absolute `0.13B` cap allows at most

`floor(0.13*65536) = 8519`

true-network forwards even if every other operation is free.

If E104-style antithetic evenization is retained explicitly, each distinct projective direction consumes two trajectories and the forward-only floor doubles to

`u_min_antithetic = 16.015625`.

## Admission rule

Before code, E107 requires BOTH:

1. complete production utilization can be <= 0.13;
2. the exact angular mechanism has a measurable route to raw <= 1.89e-8.

The necessary cost condition fails by more than 61x before implementation. Therefore the raw gate is not executed.

## Distinctness

E107 is not:

- E100/E103/E104 stochastic orthogonal/Haar sampling or radial Rao-Blackwellization;
- E105 stochastic risk certification;
- E106 fitted cross-block quartic Haar control variates;
- E032 backward-leverage cubature;
- E042 source-column cubature;
- E003 radial fourth-moment propagation.

E107 asks whether exact deterministic fourth-angular-moment matching itself can fit the production budget.

## Frozen kill rule

Because the rank lower bound alone implies `u_min > 0.13`, E107 must terminate pre-code.

No implementation, workflow, benchmark, target access, tuning, sweep, public run, scorer, holdout, full evaluation, canonical mutation, or ledger mutation is authorized.
