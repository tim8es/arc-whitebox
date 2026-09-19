# E110 — deep-sensitivity Householder orbit sampling

Tracking ID: `ARC-E110-DEEP-HOUSEHOLDER-ORBIT-20260919`

Status: **PROTOCOL-ONLY / PRE-EXECUTION**.

Owner role: **research owner** — implementation and exactly one frozen synthetic production-shape execution.

Verifier role: **independent verifier** — after the owner result exists, create `review/e110-independent-verifier-20260919` from the immutable candidate result tip and verify identity, marginal-law proof, target independence, billing and gates without executing a second scientific run.

## Portfolio reason

E108 proves that using an exact first-layer mean fluctuation as a transported linear control variate barely touches the deep-error problem: only 0.275% measured risk reduction. E105 places the remaining E104 stochastic-risk scale roughly 455x above target.

E110 therefore does **not** fit or transport a control coefficient. It changes only the joint coupling of otherwise marginally Haar directions, using a deterministic network-derived deep sensitivity axis.

This is disjoint from:
- E106 fitted quartic cross-fit control;
- E107 exact fourth-moment cubature;
- E108 first-layer exact-mean transported control;
- E109 network-agnostic Hadamard moment balancing.

## Frozen mechanism

For each fixed synthetic MLP, derive one target-free input-space unit vector `v` from weights only.

Let `g_D = ones(n) / sqrt(n)`. Traverse the frozen network weights backward using the all-gates-half linearization:

`g_{l-1} = 0.5 * W_l.T @ g_l`.

After the first layer, set `v = g_0 / ||g_0||_2`, with deterministic sign canonicalization (largest-magnitude component non-negative).

Define the Householder reflection

`R_v = I - 2 v v.T`.

For one Haar matrix `Q`, use the two bases:

- `Q`;
- row-wise reflected `Q R_v`.

Apply analytic `E[chi_1024]` radius and exact antipodes. Total trajectories remain exactly 4096.

For fixed network weights, `R_v` is deterministic and orthogonal. Since each Haar row is uniform on the sphere, its reflected row has the same marginal law. The average remains target-free and unbiased; only the cross-direction coupling changes.

The hypothesis is that reflecting each angular sample across the network's frozen deep linearized sensitivity axis creates stronger cancellation of the dominant deep directional component than a second independent Haar basis.

## Frozen comparison

Use four synthetic zero-bias production-shape networks:

- width `1024`, depth `16`;
- weight seeds `110104, 110204, 110304, 110404`;
- He-normal float32 weights.

For each network compute two independent full realizations A/B of:

- authoritative E104 two-independent-Haar-basis baseline;
- E110 `Q + Q R_v` Householder-orbit candidate.

Root direction seeds:

- A: `1_100_000 + weight_seed`;
- B: `2_100_000 + weight_seed`.

Target-free stochastic risk:

`Rhat = mean_j((M_A[j] - M_B[j])**2) / 2`.

No benchmark/reference target is read.

## Pre-code gates

Before implementation, owner must commit:

- exact derivation code for `v`;
- proof/check that `R_v.T @ R_v = I` to numerical tolerance;
- complete accounting for sensitivity backprop, one QR, reflection products, analytic radius, all forwards/reductions/finalization;
- conservative all-in utilization `<=0.13`.

If the bound exceeds `0.13`, if `||g_0||` is non-finite/zero on any frozen network, or if the reflection orthogonality check fails, E110 is terminal pre-code NO-GO.

## Frozen execution gates

All must pass:

1. finite outputs and finite sensitivity vector;
2. exact antipodal pairing;
3. bitwise deterministic replay;
4. Householder orthogonality max error `<=1e-10`;
5. complete flopscope ledger exact reconciliation;
6. measured utilization `<=0.13`;
7. no public/public-mini/scorer/holdout/full target access;
8. aggregate target-free risk ratio `E110 / matched E104 <=0.35`;
9. E110 risk < matched E104 risk on at least `3/4` networks;
10. worst per-network E110/E104 risk ratio `<=0.80`;
11. no fitted coefficient, target-dependent axis, alternate Jacobian gate, seed/sample sweep or adaptive rescue.

Any failed gate => **TERMINAL NO-GO / DROP E110**. No alternative sensitivity definition, multiple reflections, coefficient fitting, seed changes, extra samples, rescue or rerun under E110.

## Scope

No public/public-mini, official scorer, holdout/full, benchmark labels, tuning/sweep, canonical mutation, ledger mutation, merge or E104/E108 reopening is authorized.
