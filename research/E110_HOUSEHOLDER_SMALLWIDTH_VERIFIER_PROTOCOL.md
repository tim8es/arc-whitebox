# E110 independent verifier — exact small-width Householder-orbit law test

Tracking ID: `ARC-E110-HOUSEHOLDER-SMALLWIDTH-VERIFIER-20260919`

Status: **VERIFIER-FROZEN / EXACTLY ONE SYNTHETIC SMALL-WIDTH WORKFLOW AUTHORIZED**.

## Provenance

- Candidate lane: `research/e110-deep-householder-orbit-20260919`
- Candidate protocol tip: `ca6d9430644e745d174c46cbc27334332671d1f0`
- Verifier branch: `review/e110-householder-smallwidth-exact-verifier-20260919`
- This verifier does not mutate or execute the owner production lane.
- No E104 rerun, public/public-mini, official scorer, holdout, full suite, benchmark labels, tuning, sweep, rescue, canonical mutation, or ledger mutation.

## Frozen candidate

Use the candidate protocol's weight-only deep sensitivity axis:

`g_L = ones(n)/sqrt(n)`,
`g_{l-1} = 0.5 W_l.T g_l`,
`v = g_0 / ||g_0||`.

The sign of `v` is irrelevant to the reflection.

`R_v = I - 2 v v.T`.

For one Haar basis `Q`, the candidate uses `Q` and `Q R_v`, analytic `E[chi_n]` radius, and exact antipodes. The matched baseline uses two independent Haar bases with the same total number of trajectories.

## Exact verifier instance

- width: 2
- depth: 4
- zero bias
- float64 iid He-Gaussian weights `N(0, 2/n)`
- frozen weight seed: `110104`
- billed candidate Haar seed: `110105`
- billed second baseline Haar seed: `110106`
- no target/reference labels.

The seed is inherited from the first frozen production-network seed in the candidate protocol. No seed search is permitted.

## Exact reference law

For a zero-bias ReLU network and unit input `q(theta)=(cos(theta),sin(theta))`, recursively enumerate all exact ReLU angular sectors on `[0,2pi]`. On each sector the final output is exactly

`F(theta)=a cos(theta)+b sin(theta)`.

For a 2D Haar basis including antipodes, define

`B(theta) = [F(theta)+F(theta+pi/2)+F(theta+pi)+F(theta+3pi/2)]/4`.

`B` has period `pi/2` and is piecewise linear in `cos(theta),sin(theta)`.

If `v=(cos(alpha),sin(alpha))`, reflection maps the basis orientation to

`theta' = 2 alpha - theta (mod pi/2)`.

Hence the Householder estimator is

`C(theta) = [B(theta)+B(theta')]/2`.

The exact reference integrates all means, variances and cross-moments analytically on the common angular partition.

The matched two-independent-basis baseline variance is

`Var_ind = Var(B)/2`.

The coupled candidate variance is

`Var_house = Var(C)`.

Because the network is positively homogeneous and `R=||X||` is independent of direction for `X~N(0,I_2)`, the exact Gaussian output mean is

`E[F(X)] = E[chi_2] * E_theta[F(q(theta))]`.

This full-circle sector integral is computed independently from the block-period integral. Candidate exact mean bias is measured against that reference.

## Frozen scientific gates

All integrity gates must pass:

1. exact sector representation vs direct network evaluation max abs <= `1e-11`;
2. exact block representation vs direct four-direction evaluation max abs <= `1e-11`;
3. Householder orthogonality max abs <= `1e-12`;
4. reflected block representation validation max abs <= `1e-11`;
5. at least one nondegenerate final output coordinate;
6. exact candidate Gaussian-mean max abs bias <= `1e-12`;
7. reflected marginal mean max abs difference <= `1e-12`;
8. candidate pooled exact variance ratio `sum Var_house / sum Var_ind <= 0.80`;
9. candidate does not increase variance on any nondegenerate output;
10. deterministic exact replay bitwise/equality checks pass;
11. billed candidate replay is bitwise deterministic and FLOP ledgers match;
12. exact antithetic input pairs;
13. full candidate and baseline flopscope ledgers reconcile exactly;
14. no target/public/scorer/holdout/full access.

Gate 8 is a mechanistic breakthrough gate only; it is not competition raw MSE.

Any failed gate => verifier **NO-GO / BREAKTHROUGH NOT CONFIRMED**. No alternate seed, width, depth, reflection, sensitivity rule or rerun.

## FLOP scope

The exact angular integration is verifier-only reference work and is not competition estimator compute. The harness separately executes one fully billed small-width candidate estimator realization and one matched baseline realization under flopscope. Their ledgers include all estimator numerical work: sensitivity backprop, normalization, Householder construction, Gaussian RNG, QR/sign canonicalization, reflection matmul, analytic-radius scaling, antipodal construction, all ReLU forwards and final reduction.

## One-shot execution

The workflow is triggered only by creating
`research/E110_HOUSEHOLDER_SMALLWIDTH_VERIFIER_RUN_ARM.json`
with this tracking ID on the verifier branch. The arm file is created once after protocol/script/tests/workflow are frozen.
