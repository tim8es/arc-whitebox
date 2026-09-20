# E127 protocol — sparse higher-order hypergraph closure with certified omitted-cluster tail

Idempotency key: `ARC-E127-SPARSE-HYPERGRAPH-CERTIFIED-TAIL-20260920`

Status at freeze: **ONE EXACT SMALL-WIDTH FALSIFIER AUTHORIZED**.

## Identity / ancestry / exclusions

Branch:
`research/e127-sparse-hypergraph-certified-tail-20260920`.

Direct parent:
`research/bootstrap`.

E127 is an alternative to the closed E124 Chow–Liu pair-tree lane. It does **not**
modify the E124 tree, add tree edges, change the tree score, add amplitude bins,
or otherwise rescue pairwise tree closure.

Forbidden:

- E124 pair-tree rescue variants;
- target fitting or post-result threshold tuning;
- benchmark/public/public-mini/scorer/holdout/full access;
- Gaussian plug-in, Edgeworth/cumulant patch, control variate, transported CV;
- explicit full activation-mask state as the production representation;
- rerun/sweep after observing the scientific payload;
- canonical estimator or ledger mutation.

The small-width exact angular geometry is only a verifier/falsifier device.

## Mechanism

Let the penultimate activations be `H_i >= 0` and let output row `j` have
weights `w_ij`.

For every source subset `S`, define the subset observable

`F_j(S) = E[ ReLU(sum_{i in S} w_ij H_i) ]`,

with `F_j(empty)=0`.

Define its Möbius cluster coefficient

`Delta_j(S) = sum_{T subseteq S} (-1)^(|S|-|T|) F_j(T)`.

Then, for the full source set `V`,

`F_j(V) = sum_{S subseteq V} Delta_j(S)`.

This identity is exact for **arbitrary joint dependence** among the sources.
No independence, Gaussian, tree, or pairwise factorization is used.

A sparse hypergraph closure keeps a downward-closed family `A` of clusters and
returns

`C_A,j = sum_{S in A} Delta_j(S)`.

The omitted error is exactly

`R_A,j = sum_{S not in A} Delta_j(S)`.

### Certified target-free tail envelope

For a fixed realization define `x_i = w_ij H_i` and
`g(x)=ReLU(sum_i x_i)`.

Because ReLU is 1-Lipschitz, the mixed finite difference satisfies for every
nonempty `S`

`|Delta_S g| <= 2^(|S|-1) min_{i in S} |x_i|`.

Taking expectations gives the target-free cluster envelope

`|Delta_j(S)| <= b_j(S)`

where

`b_j(S) = 2^(|S|-1) min_{i in S} |w_ij| E[H_i]`.

The exact omitted-tail certificate is therefore

`T_A,j = sum_{S not in A} b_j(S)`

and

`|R_A,j| <= T_A,j`.

Vector RMS certificate:

`T_A,RMS = sqrt(mean_j T_A,j^2)`.

The small-width falsifier gives this mechanism the **optimistic advantage** of
exact penultimate means `E[H_i]` derived from weights. Production would have
to replace these with certified upper means, so failure of this optimistic
certificate is terminal for this E127 mechanism.

### Sparse-family necessary lower bound

All `b_j(S)` are nonnegative. Therefore

`T_A,RMS >= mean_j T_A,j
           = sum_{S not in A} a(S)`

where

`a(S)=mean_j b_j(S)`.

Thus any sparse family with `T_A,RMS <= epsilon` must retain enough clusters
that the sum of `a(S)` over omitted clusters is at most `epsilon`.

Sorting higher-order clusters by decreasing `a(S)` gives an optimistic
necessary lower bound on the number of clusters any sparse selector must keep.
This lower bound ignores downward-closure helper cost and is therefore
deliberately favorable to E127.

## Frozen exact small-width identity / falsifier

Synthetic only:

- Gaussian input dimension: `2`;
- width: `8`;
- depth: `4`;
- zero bias;
- iid He-normal float64 weights;
- seeds: `127200..127207`;
- exact piecewise angular integration;
- exact Gaussian radial factor `E[R]=sqrt(pi/2)`;
- no Monte Carlo;
- no numerical quadrature;
- no final-target input to candidate/certificate.

For each frozen network:

1. enumerate the exact penultimate angular sectors;
2. derive exact penultimate means;
3. for every nonempty subset `S subseteq {0..7}` and every final output,
   compute `F_j(S)` exactly from the same joint source law;
4. Möbius-transform all subset observables to `Delta_j(S)`;
5. independently propagate the full final layer and integrate its exact mean;
6. verify the full-order identity
   `sum_S Delta_j(S) == exact_final_j` within `1e-12`;
7. compute order-truncated closures `r=1..8` and certified tails
   `T_r`;
8. construct one frozen sparse family under the normalized production budget
   below;
9. score that sparse candidate only after it and its certificate are frozen;
10. emit one deterministic payload.

Evaluating all `r=1..8` inside this one payload is the preregistered adaptive
order diagnostic, not a tuning sweep. No second scientific run is authorized.

## Frozen sparse production budget

Competition budget:

`B = 2^41 = 2,199,023,255,552 FLOPs`.

Utilization cap:

`0.13`.

Integer cap:

`floor(0.13 B) = 285,873,023,221 FLOPs`.

Production shape:

- width `n=1024`;
- depth `L=16`;
- penultimate trajectories `N=4096`;
- prefix propagated through layers 1..15 only.

Billed baseline:

- prefix dense propagation:
  `N*(L-1)*(2n^2+2n) = 128,974,848,000`;
- input RNG/materialization:
  `32*N*n = 134,217,728`;
- penultimate mean reductions:
  `8*N*n = 33,554,432`;
- absolute/source-stat reductions:
  `8*N*n = 33,554,432`;
- general helper/accounting reserve:
  `5,000,000,000`.

Baseline total:

`134,176,174,592 FLOPs`.

Remaining headroom under the 0.13 cap:

`151,696,848,629 FLOPs`.

For a retained non-singleton cluster of order `k`, an optimistic all-output
trajectory evaluation of `F(S)` costs at least

`c_k = 2*N*n*(k+1)`

FLOPs (dense `N x k` by `k x n`, ReLU/reduction included only at this
optimistic floor).

Normalize cluster work by `2*N*n`. Production allows at most

`151,696,848,629 / (2*N*n) = 18,083.673552... units`

or

`17.659837453... units per source`.

The width-8 homologous sparse budget is therefore frozen as

`floor(8 * 17.65983745327685) = 141 cluster units`

with each retained non-singleton cluster charging `|S|+1` units.

This admits at most 47 pair-cost clusters even if every retained cluster were
incorrectly billed at the cheapest non-singleton cost. That 47 count is an
optimistic necessary cap, not the actual helper-aware cap.

## Frozen sparse selector

Singles are always retained and free in the cluster-unit budget because their
expectations are obtained from the already billed source means.

For higher-order clusters:

1. compute `a(S)=mean_j b_j(S)`;
2. rank by decreasing `a(S)`, tie-break by increasing
   `(|S|, lexicographic S)`;
3. greedily add a cluster only when all missing non-singleton proper faces can
   also be added and the total face cost
   `sum_{S retained, |S|>=2} (|S|+1)`
   remains at most 141;
4. retained faces form one deterministic downward-closed simplicial complex.

No candidate error, exact final target, or post-score information enters this
selection.

## Frozen gates

Raw final-layer MSE target:

`1.89e-8`.

Raw RMS target:

`sqrt(1.89e-8) = 1.374772708486752e-4`.

Integrity gates:

1. exact angular partitions finite, ordered, complete;
2. all source means and subset observables finite;
3. Möbius full-order reconstruction max abs error `<=1e-12`;
4. direct exact full-subset observable agrees with independently propagated
   final exact mean within `1e-12`;
5. all cluster envelope inequalities
   `|Delta_j(S)| <= b_j(S)+1e-12` hold;
6. sparse selector is deterministic and downward closed;
7. sparse units `<=141`;
8. candidate/certificate never read exact final means before scoring;
9. deterministic replay is bitwise-identical JSON;
10. no target/public/scorer/holdout/full access.

Scientific/admission gates:

11. sparse certified RMS tail `<=1.374772708486752e-4` on every network;
12. pooled sparse candidate bias MSE `<=1.89e-8`;
13. every-network sparse candidate bias MSE `<=1.89e-8`;
14. the necessary optimistic retained-cluster lower bound for a passing
    certificate is `<=47` on every network;
15. if the sparse gate 11 fails and only a full-order truncation would certify,
    the minimum passing truncation order `r` is reported together with its
    production full-order FLOP upper; this is a diagnostic blocker, not an
    independent veto of a sparse family that already passes gate 11;
16. production accounting formula and width-8 normalized cluster budget match
    this protocol.

Any failed or unevaluable gate =>

**E127 TERMINAL NO-GO / sparse higher-order hypergraph closure cannot certify
the required tail under the FLOP cap.**

If all gates pass, the branch receives only a local small-width GO; production
scientific execution would require a new separately frozen protocol.

## Production full-order comparison

For diagnostic order `r`, the number of non-singleton faces is

`M_r(n)=sum_{k=2}^r C(n,k)`.

Even before helper overhead, the optimistic cluster work is

`C_r(n)=sum_{k=2}^r C(n,k) * 2*N*n*(k+1)`.

The falsifier reports `C_r(1024)` and utilization for every `r=2..8`.

This comparison is not used to tune `r`. It is diagnostic evidence when the
budgeted sparse family fails its certificate. A sparse family that satisfies
all sparse scientific gates is not rejected merely because the corresponding
all-clusters order truncation would be unaffordable.

## Run discipline

Immutable order:

1. this protocol-only commit;
2. implementation + focused tests + falsifier script;
3. workflow arm;
4. exactly one GitHub Actions scientific run;
5. append-only result/receipt commit.

No scientific rerun, rescue, seed change, threshold change, order change,
selector change, or production/public execution under E127.
