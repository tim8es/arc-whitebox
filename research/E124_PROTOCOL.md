# E124 protocol — conditional Walsh-coset source-interaction stratification

Idempotency key: `ARC-E124-WALSH-COSET-SOURCE-INTERACTIONS-20260920`

Status at freeze: **ONE FROZEN EXACT SMALL FALSIFIER + PRODUCTION FLOP PROOF AUTHORIZED**.

## Disjoint provenance

- Branch: `research/e124-walsh-coset-source-interactions-20260920`.
- Direct parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E104–E121 mechanisms are closed and are not reopened, renamed, tuned or rescued.

E124 is not:
- radial/Haar Rao–Blackwell or antithetic direction sampling;
- fitted control variates, Stein/JVP, covariance-response fitting or `cov/var` division;
- Gaussian late-layer plug-in or marginal moment closure;
- cumulant/Hermite/message/treewidth closure;
- mask/sign-cone/boundary enumeration or boundary-flux compression;
- Gaussian-line conditioning/breakpoint integration;
- Haar-plane cyclic source memory;
- polynomial/Gaussian cubature matching.

E124 conditions on **actual coordinate magnitudes** and stratifies only the
discrete source-sign group with a random coset. Every candidate node is then
propagated through the exact realized late ReLUs.

## Exact Gaussian source decomposition

For `X~N(0,I_d)`, write coordinatewise

`X_j = R_j S_j`,

where
- `R_j=|G_j|` are iid half-normal;
- `S_j` are iid Rademacher;
- `R` and `S` are independent.

No hidden-layer distributional approximation is introduced.

## Frozen Walsh-coset candidate

Use `k=2`, hence `M=2^k=4` Walsh rows per magnitude vector.

The three nonzero labels in `GF(2)^2` are
`1=(0,1)`, `2=(1,0)`, `3=(1,1)`.

For each outer orbit `p`:

1. draw `g_p~N(0,I_d)`, set `r_p=|g_p|`;
2. draw an iid Rademacher coset shift `b_p in {+1,-1}^d`;
3. assign source labels `ell_{p,j} in {1,2,3}` by a target-free balanced
   random permutation: shuffle coordinates with the frozen candidate RNG and
   cycle labels `1,2,3,1,2,3,...`;
4. for every Walsh row `z in GF(2)^2`, define
   `h_z(j)=(-1)^{<z,ell_{p,j}>}`;
5. propagate
   `x_{p,z}=r_p .* b_p .* h_z`
   through the complete zero-bias ReLU network.

Estimator:
`m_hat=(1/P) sum_p (1/4) sum_z F(x_{p,z})`.

Production constants:
- `P=2048` outer magnitude vectors;
- `M=4`;
- total deep propagations `N=8192`.

No adaptive relabeling from outputs, gates, targets or reference error.

## Exact unbiasedness

For every fixed Walsh row `z`, `b_p .* h_z` is an iid uniform Rademacher
vector because `b_p` is. Therefore each `x_{p,z}` is exactly
`N(0,I_d)`.

Hence for every measurable integrable network `F`:

`E[m_hat]=E[F(X)]`.

The four within-orbit nodes are dependent by design; that dependence is the
variance-reduction mechanism.

## Cross-source dependence law

For two source coordinates `i,j`, conditional on `r,b,ell`:

`(1/4) sum_z h_z(i) h_z(j)`
equals
- `0` if `ell_i != ell_j`;
- `1` if `ell_i = ell_j`.

Thus every differently labelled source pair has its exact second-order Walsh
sign character integrated out **before the late ReLUs are averaged**.

The network itself still evaluates the full joint source vector. No pairwise
Gaussian approximation, covariance surrogate or marginal re-Gaussianization
is used. Higher-order sign interactions remain present unless annihilated by
the same exact character rule.

With balanced random relabeling over many independent outer orbits, a fixed
source pair is separated with probability approximately `2/3`, without
using any output information.

## Frozen exact small falsifier

### A. Exact dense conditional-Walsh law test

- input dimension `d=4`;
- width `8`;
- depth `4`;
- zero bias;
- iid He-normal float64 weights;
- network seed `124104`;
- fixed positive magnitude vector from `abs(N(0,I4))`, seed `124105`;
- fixed labels `[1,2,3,1]`.

The verifier exhaustively enumerates all `2^4=16` source-sign vectors for the
fixed magnitudes and propagates them through the dense depth-4 ReLU network.

It then:
1. computes the exact conditional full-sign mean;
2. evaluates every distinct Walsh coset average induced by the fixed labels;
3. verifies the average over all cosets equals the exact full-sign mean;
4. directly verifies degree-1 Walsh characters are zero within each coset;
5. directly verifies degree-2 characters are zero exactly for all
   differently-labelled source pairs and nonzero only for same-label pairs;
6. records the dense network output variation across cosets, proving the test
   is not a trivial linear fixture.

This is an exact finite-state verifier only. The candidate never enumerates
all sign states.

### B. Exact Gaussian-mean risk falsifier with overlapping sources

Construct one sparse-but-deep `d=4 -> width=8 -> width=8` depth-4 network
from four width-2/depth-4 zero-bias subnetworks with independent seeds

`124200,124201,124202,124203`.

Branches use overlapping input source pairs:

`(0,1), (1,2), (2,3), (3,0)`.

Each branch is propagated independently inside the shared width-8 network, so
the candidate sees only the assembled weights, not the branch map.

Because each branch receives a standard 2-D Gaussian marginal, its exact final
mean is computed independently by an analytic 2-D angular-sector reference.
Concatenating the four branch means gives the exact width-8 Gaussian output
mean despite source sharing across branches.

Candidate:
- `P=2048, M=4, N=8192`;
- frozen estimator seeds `124300,124301,124302,124303`.

Comparator:
- exactly `8192` iid standard-Gaussian inputs;
- seeds `124400,124401,124402,124403`.

Both receive identical assembled weights. Reference is verifier-only.

## Frozen gates

### Law/integrity
1. all exact and candidate outputs finite;
2. exact dense conditional full-sign/coset mean max abs discrepancy
   `<=1e-13`;
3. all degree-1 Walsh character averages max abs `<=1e-15`;
4. all differently-labelled degree-2 Walsh character averages max abs
   `<=1e-15`;
5. same-label pair character check equals one to `<=1e-15`;
6. dense conditional coset-output spread is strictly positive;
7. assembled-network exact analytic 2-D references finite;
8. deterministic replay bitwise exact for candidate predictions and accounting;
9. candidate source audit shows no benchmark/reference/target read.

### Scientific
10. pooled candidate MSE versus exact Gaussian mean is strictly below pooled
    same-node iid MSE;
11. pooled candidate/iid MSE ratio `<=0.90`;
12. candidate wins on at least `3/4` frozen estimator seeds.

Failure of any gate => **E124 TERMINAL NO-GO / CLOSE WALSH-COSET SOURCE-INTERACTION LANE**.

Pass => **E124 LOCAL SCIENTIFIC GO — CROSS-SOURCE WALSH STRATIFICATION**.

No seed, label count, Walsh rank, P/M allocation, network, comparator or gate
may change after the run.

## Frozen production FLOP proof

Production shape:
- `d=n=1024`;
- depth `L=16`;
- `P=2048`;
- `M=4`;
- `N=8192`;
- budget `B=2^41=2199023255552`;
- utilization cap `0.13`.

Conservative all-in charges:

1. full deep propagation:
   `N*L*(2*n^2+2*n) = 275146342400`;
2. outer Gaussian RNG, abs and magnitude bookkeeping:
   `P*(20*d+64) = 42074112`;
3. coset signs, balanced label shuffle/assignment:
   `P*(16*d+64) = 33685504`;
4. Walsh parity/sign application and source materialization:
   `N*(8*d+16) = 67239936`;
5. final reduction/materialization:
   `N*n+5*n = 8393728`.

All-in frozen upper bound:

`275297735680 FLOPs`.

Utilization:

`275297735680 / 2^41 = 0.125190916005522 < 0.13`.

Frozen slack below cap:

`10575287541.76 FLOPs`.

The executable must recompute these integers independently and report every
operation class. Any accounting mismatch or omitted candidate operation class
is terminal.

## Run discipline

1. protocol-only commit;
2. implementation/tests/falsifier;
3. workflow arm;
4. exactly one GitHub Actions scientific run;
5. immutable JSON receipt commit.

No public/public-mini/scorer/holdout/full, no benchmark targets, no tuning,
sweep, rescue, rerun, canonical/ledger mutation or merge.
