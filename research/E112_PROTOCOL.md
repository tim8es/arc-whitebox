# E112 protocol — exact activation-mask message passing treewidth/rank falsifier

Idempotency key: `ARC-E112-EXACT-MASK-MESSAGE-TREEWIDTH-20260919`

Status at freeze: **CHEAP STRUCTURAL FALSIFIER ONLY**

## Motivation and non-duplication

E111 established that an exact first-two-moment Gaussian-ReLU plug-in develops large deterministic bias immediately after ReLU. E112 therefore models the non-Gaussian dependence explicitly rather than Gaussianizing it.

E112 is **not a control variate**, sampler, moment plug-in, cumulant correction, QMC/cubature lane, or target fit.

Candidate family: exact finite-state sum-product / junction-tree propagation over binary ReLU activation masks.

Closed lanes excluded: E038, E100, E104/E105, E106, E107, E108, E109, E110, E111.

No public/public-mini, benchmark targets, scorer, holdout/full, tuning, sweep, rescue, canonical/ledger mutation, or merge.

## Candidate estimator

At layer `l`, represent the activation-cone state by the binary mask

`s_l in {0,1}^n`.

Conditioned on a complete upstream mask history, a zero-bias ReLU network is linear on its polyhedral cone. An exact finite-state estimator can therefore attach an exact cone probability / moment payload to each feasible mask state and propagate it through factors induced by the next dense affine map.

For a next-layer unit

`z_{l+1,j} = sum_i W_{l+1}[j,i] h_{l,i}`,

the sign/moment factor has scope containing every prior mask coordinate `s_{l,i}` for which `W_{l+1}[j,i] != 0`.

The primal graph connects any pair of mask variables that co-occur in a factor. If one factor has all `n` variables in its scope, the primal graph contains `K_n`; for a fully dense layer every factor has full scope, so the primal graph is exactly `K_n`.

Exact junction-tree message passing over binary variables then requires a bag of size at least

`treewidth(K_n)+1 = n`

and therefore an explicit message table with at least `2^n` entries.

This is a representation lower bound for the **frozen E112 estimator family**. It does not claim that every possible symbolic cone algorithm must enumerate `2^n` states.

## Why rank is part of the gate

For the first square dense layer, if `W_1` is full rank, the map `x -> W_1 x` is onto. Hence every orthant of preactivation space is reachable, so all `2^n` first-layer sign masks are feasible. There is no pruning of the first separator by infeasible masks.

For an iid continuous Gaussian square matrix, full rank holds with probability one. The exact small falsifier additionally measures rank directly.

Thus the candidate needs **both** a low-width separator and a low-rank/reachability collapse to avoid exponential explicit mask state. Dense full-rank layers provide neither.

## Frozen cheap falsifier

Synthetic exact structural family only:

- widths `n = 2,3,4,5,6,7,8`;
- depth `4`;
- zero bias;
- iid Gaussian square weights, He scale `sqrt(2/n)`;
- PCG64 seed `112000+n` per width;
- float64;
- no trajectory simulation and no network target outputs.

For every width and layer:

1. construct factor scopes from exact nonzero weight support;
2. construct the mask-variable primal graph;
3. compute exact treewidth by exhaustive elimination-order search (at `n<=8`, at most `8! = 40320` orders);
4. compute numeric matrix rank;
5. record minimum absolute weight and support density.

Independent unit tests must validate the treewidth routine on empty, path, star, cycle, and clique graphs.

## Frozen gates

Integrity gates:

1. every generated weight/support/rank/treewidth value finite;
2. every weight matrix is fully dense (support density exactly `1.0`);
3. every weight matrix has numeric rank exactly `n`;
4. exact treewidth routine returns `n-1` for every dense-layer primal graph;
5. all `2^n` first-layer masks are certified feasible by the full-rank onto argument;
6. deterministic replay gives identical JSON payload;
7. no external/target access.

Mechanism admission gate:

8. production explicit-state lower bound must fit the competition budget under the maximally favorable assumption of **one FLOP per message-table entry**.

Frozen production shape is `n=1024`, budget `2^41`, utilization cap `0.13`.

Thus a viable bag size `b` must satisfy

`2^b <= 0.13 * 2^41`.

Equivalently `b <= floor(41 + log2(0.13)) = 38`.

For a dense layer E112's exact structural theorem gives `b=n=1024`, so the candidate lower bound is `2^1024` table entries before any cone integration arithmetic.

### Decision rule

If small exact results confirm full support, full rank, and treewidth `n-1` through width 8, the dense-layer theorem applies and E112 is **TERMINAL STRUCTURAL NO-GO / DROP** for production-width exact finite-state mask message passing.

A production-shaped prototype is forbidden because its representation lower bound already exceeds the budget.

If, unexpectedly, the frozen small family exhibits a reproducible structural collapse (non-full support, rank deficiency, or treewidth materially below the dense theorem), E112 may only record **SMALL STRUCTURAL GO**; a separate admission commit would then be required before any larger prototype.

No seed change, sparsification, low-rank projection, approximate pruning, state hashing, moment compression, tensor-network truncation, or rescue after the frozen falsifier.
