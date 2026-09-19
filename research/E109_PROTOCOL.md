# E109 — coupled Haar + Walsh-Hadamard angular design

Tracking ID: `ARC-E109-COUPLED-HAAR-HADAMARD-20260919`

Status: **PROTOCOL-ONLY / PRE-EXECUTION**.

Owner role: **research owner** — implementation and exactly one frozen synthetic production-shape execution.

Verifier role: **independent verifier** — after the owner result exists, create `review/e109-independent-verifier-20260919` from the immutable candidate result tip and verify identity, law, billing, run/job/artifact digest and gates without executing a second scientific run.

## Portfolio reason

E105 certifies that the current two-Haar E104 estimator remains roughly 455x above the project raw-risk target at production shape. E106 quartic fitted control variates worsen risk; E107 exact spherical fourth-moment cubature is cost-infeasible; E108 first-layer transported control reduces risk by only 0.275%.

E109 therefore attacks the **deep angular integration error itself**, without target fitting or more trajectories.

It is not an E104/E106/E107/E108 rescue: the sampling law is a new fixed coupling of two spherical bases and has its own experiment ID and terminal gates.

## Frozen mechanism

Production width is `n=1024`.

For each estimator realization:

1. generate one Haar orthogonal matrix `Q` using the same sign-canonicalized Gaussian-QR convention as the verified E100/E104 family;
2. construct the normalized Walsh-Hadamard matrix `H` of order 1024;
3. use the two spherical bases `Q` and `H @ Q`;
4. multiply all directions by the exact analytic `E[chi_1024]` radius;
5. include exact antipodes.

Total trajectories remain exactly `4096 = 2 bases * 1024 rows * 2 antipodes`.

Because `H` is fixed orthogonal and `Q` is Haar, both `Q` and `H Q` have Haar-distributed rows marginally. The estimator is the equal average over the two dependent bases and their antipodes. No target/reference quantity enters construction.

The scientific hypothesis is that deliberately coupling the two bases by a dense orthogonal Hadamard transform reduces low-order angular-moment discrepancy and therefore deep directional variance more than two independent Haar bases at identical forward-pass count.

## Frozen comparison

Use four synthetic zero-bias production-shape networks:

- width `1024`, depth `16`;
- weight seeds `109104, 109204, 109304, 109404`;
- He-normal float32 weights, exactly as the established synthetic production harness.

For each network compute **two independent full estimator realizations** A/B for:

- baseline: authoritative E104 two-independent-Haar-basis law;
- candidate: E109 coupled `Q + H Q` law.

Root direction seeds are frozen as:

- realization A: `1_000_000 + weight_seed`;
- realization B: `2_000_000 + weight_seed`.

For either estimator, target-free stochastic risk is

`Rhat = mean_j((M_A[j] - M_B[j])**2) / 2`.

No benchmark/reference target is read.

## Pre-code gates

Before implementation, owner must commit an analytic accounting table proving:

- exactly 4096 forward trajectories;
- one QR plus one normalized FWHT/Hadamard mixing path;
- complete RNG, QR, mixing, radius, forward, reduction and finalization billing;
- conservative all-in utilization `<=0.13`.

If the bound exceeds `0.13`, E109 is terminal pre-code NO-GO.

## Frozen execution gates

All must pass:

1. finite outputs;
2. exact antipodal pairing;
3. bitwise deterministic replay;
4. complete flopscope ledger reconciles exactly;
5. measured utilization `<=0.13`;
6. no public/public-mini/scorer/holdout/full target access;
7. aggregate target-free risk ratio `E109 / matched E104 <= 0.35`;
8. E109 risk < matched E104 risk on at least `3/4` networks;
9. worst per-network E109/E104 risk ratio `<=0.80`;
10. empirical second-moment isotropy error of both candidate bases `<=1e-6` in float64 construction;
11. no target-dependent choice, fitting, coefficient estimation, seed/sample sweep or adaptive transform.

Any failed gate => **TERMINAL NO-GO / DROP E109**. No alternate Hadamard ordering, extra random signs, additional bases, seed changes, sample-count changes, blending, rescue or rerun under E109.

## Scope

No public/public-mini, official scorer, holdout/full, benchmark labels, tuning/sweep, canonical mutation, ledger mutation, merge or reuse of E104/E108 terminal execution is authorized.
