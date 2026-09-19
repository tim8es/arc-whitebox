# E124 protocol — Chow–Liu gate-amplitude linked-cluster closure

Idempotency key: `ARC-E124-CHOWLIU-GATE-AMPLITUDE-CLUSTER-20260920`

Status at freeze: **ONE EXACT SMALL-WIDTH FALSIFIER AUTHORIZED**.

## Identity / ancestry / exclusions

Branch:
`research/e124-chowliu-gate-amplitude-cluster-20260920`.

Direct parent:
`research/bootstrap`.

This lane is deliberately cut from bootstrap rather than from E104–E121 ancestry.

Forbidden and not reopened:

- E104–E121, including renamed rescue variants;
- Haar/radial Rao–Blackwellization, orthogonal/QMC/cubature samplers;
- transported/Stein/control-variate families;
- Gaussian-ReLU moment plug-ins and Edgeworth/cumulant repairs;
- explicit full activation-mask message passing;
- top-k gate-conditioned Gaussian closure;
- activation-boundary enumeration/flux sketches/remainders;
- shared source orbits / shared-latent trajectory memory.

No public/public-mini, benchmark target, scorer, holdout/full, target fitting,
tuning, sweep, rescue, canonical mutation, ledger mutation, or merge.

## New mechanism

E124 attacks the late-ReLU failure mode at the **source aggregation law**.

For the penultimate hidden vector `H in R_+^n` and final dense row
`w_j`, the final preactivation is

`Z_j = sum_i w_ij H_i`.

The failure of marginal Gaussian closure is that the `H_i` are not
independent and their gate/amplitude dependence survives deep ReLUs.

E124 compresses that dependence into:

1. every marginal gate law `G_i=1[H_i>0]`;
2. every marginal active amplitude mean;
3. a deterministic maximum-mutual-information spanning tree over gate
   variables;
4. for each tree edge, the complete 2x2 gate joint law and the two
   edge-state conditional amplitude means.

No full gate-mask state is stored.

### Marginal representation

Let

`q_i=P(G_i=1)`,
`m_i=E[H_i]`.

Define the two-state marginal source surrogate

`Y_i(0)=0`,
`Y_i(1)=m_i/q_i`

when `q_i>0`.

Then `E[Y_i]=m_i` exactly.

For output `j`, define

`mu_j=sum_i w_ij m_i`

and centered one-source perturbation

`xi_ij(a)=w_ij(Y_i(a)-m_i)`.

The one-source linked-cluster term is

`S_ij = E_a ReLU(mu_j+xi_ij(a))`.

The independence-only first-order closure is

`C_ind,j = ReLU(mu_j)
          + sum_i [S_ij-ReLU(mu_j)]`.

### Cross-source tree

For every source pair `(i,k)`, compute the Bernoulli mutual information from
the exact/estimated 2x2 gate probabilities.

Build one Chow–Liu maximum spanning tree `T` using deterministic Prim
selection:

- start vertex 0;
- maximize mutual information;
- ties broken lexicographically by `(u,v)`.

For each tree edge and gate state `(a,b)`, retain

`p_ik(a,b)`,
`M_i^{ab}=E[H_i | G_i=a,G_k=b]`,
`M_k^{ab}=E[H_k | G_i=a,G_k=b]`.

These are genuine cross-source statistics. They are not fitted to final
targets.

For output `j`, the edge-state two-source perturbation is

`xi_ijk^{ab}
 = w_ij(M_i^{ab}-m_i) + w_kj(M_k^{ab}-m_k)`.

Define

`P_ijk = sum_ab p_ik(a,b) ReLU(mu_j+xi_ijk^{ab})`.

The second-order tree-linked correction is

`D_ijk = P_ijk - S_ij - S_kj + ReLU(mu_j)`.

The E124 final-layer closure is

`C_124,j = C_ind,j + sum_(i,k in T) D_ijk`.

This is a finite linked-cluster expansion around the exact source means.
It preserves selected cross-source gate/amplitude dependence explicitly and
uses no Gaussian approximation.

## Why this is disjoint

E124 is not E112 finite-state message passing: it never represents the full
mask and never performs junction-tree inference over a global binary state.

E124 is not E113 gate-conditioned Gaussian closure: it uses no conditional
Gaussian and no top-k parents. All source marginals contribute, while
cross-source dependence enters through a single global Chow–Liu tree.

E124 is not E121 source-memory/orbit propagation: no shared source trajectory
is preserved through the late ReLU. The compressed object is a set of
marginal and pair source statistics.

## Frozen exact falsifier

Synthetic only.

- Gaussian input dimension: `2`;
- width: `8`;
- depth: `4`;
- zero bias;
- iid He-normal float64 weights;
- seeds: `124200..124207`;
- exact angular piecewise-linear reference;
- no Monte Carlo;
- no numerical quadrature;
- no target labels.

For each network:

1. recursively enumerate the exact angular partition through layer 3;
2. integrate penultimate marginal gate probabilities and means exactly;
3. integrate every 2x2 gate joint probability exactly;
4. integrate pair-state conditional source means exactly;
5. construct the frozen Chow–Liu tree from those gate probabilities;
6. evaluate `C_ind` and `C_124` analytically from the finite states;
7. independently enumerate layer 4 and integrate the exact final Gaussian
   mean vector.

The radial factor is exact:
`E[R]=sqrt(pi/2)` for two-dimensional standard Gaussian input.

The candidate never reads the exact final mean until scoring.

## Frozen integrity gates

All must pass:

1. exact angular partitions finite and complete;
2. all marginal probabilities lie in `[0,1]`;
3. all pair 2x2 probabilities are nonnegative and sum to one within `1e-12`;
4. pair marginals agree with single gate marginals within `1e-12`;
5. marginal surrogate reconstructs every `E[H_i]` within `1e-12`;
6. pair-state conditional means reconstruct both endpoint source means within
   `1e-12`;
7. Chow–Liu tree contains exactly 7 edges, is connected and acyclic;
8. all candidate/exact values finite;
9. deterministic replay is bitwise-identical JSON;
10. no target/public/scorer/holdout/full access.

## Frozen scientific gates

Raw final-layer target scale:

`1.89e-8`.

Per network define vector bias MSE

`MSE = mean_j (candidate_j-exact_j)^2`.

E124 survives only if all hold:

11. pooled E124 final-layer bias MSE across all 8 networks
    `<=1.89e-8`;
12. every network E124 bias MSE `<=1.89e-8`;
13. pooled E124 MSE is strictly below pooled independence-only
    `C_ind` MSE;
14. E124 improves over `C_ind` on at least 6 of 8 networks;
15. frozen production FLOP upper utilization `<=0.13`.

Any failed or unevaluable gate =>

**E124 TERMINAL NO-GO / DROP CHOW–LIU GATE-AMPLITUDE CLUSTER.**

No state-count change, alternate tree score, output-specific tree, extra edges,
amplitude bins, Gaussian residual, clipping, empirical calibration, seed
change, width/depth change, rerun or rescue.

Passing all gates would authorize only a separately frozen production-shaped
scientific run. It would not authorize public/scorer/holdout/full.

## Production FLOP proof

Frozen deployable shape:

- width `n=1024`;
- depth `L=16`;
- `N=4096` iid Gaussian trajectories;
- float32 dense propagation, float64 reductions;
- propagate trajectories through layers 1..15 only;
- construct the tree/statistics on the penultimate activations;
- replace the sampled layer-16 ReLU average by the E124 analytic cluster
  closure.

The proof deliberately over-bills helper work.

### Prefix propagation

Per trajectory per square ReLU layer:

`2n^2+2n = 2,099,200` FLOPs.

For 4096 trajectories and 15 layers:

`128,974,848,000`.

### Input RNG/materialization

Conservative:

`32*N*n = 134,217,728`.

### Complete gate co-occurrence matrix

One dense `G^T G` count product:

`2*N*n^2 = 8,589,934,592`.

### Marginal reductions

`8*N*n = 33,554,432`.

### Mutual-information matrix

Conservative:

`64*n^2 = 67,108,864`.

### Deterministic maximum spanning tree

Conservative:

`32*n^2 = 33,554,432`.

### Tree-edge conditional amplitude statistics

Conservative:

`32*N*n = 134,217,728`.

### Final all-output linked-cluster arithmetic

Mean preactivations + all single-source + all tree-pair four-state terms:

`106*n^2 = 111,149,056`.

### General helper/accounting reserve

`5,000,000,000`.

### All-in frozen upper

`143,078,584,832` FLOPs.

Competition budget:

`2^41 = 2,199,023,255,552`.

Frozen utilization upper:

`0.06506460742093623`.

Cap:

`0.13`.

Headroom:

`142,794,438,389.76` FLOPs.

Thus the pre-code production cost gate passes by a large margin. Scientific
bias is the decisive unknown.

## Run discipline

Immutable order:

1. this protocol-only commit;
2. implementation + focused tests + exact falsifier;
3. workflow arm;
4. exactly one Actions scientific run;
5. immutable receipt/result commit.

No rerun, rescue, tuning, sweep, or production/public execution under E124.
