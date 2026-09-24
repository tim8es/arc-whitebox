# R321 — independent red-team of R317 gate-conditioned compression NO_GO

Status: **INDEPENDENT EVIDENCE-BASED NO_GO — R317 CORE COMPRESSION CLAIM NOT FALSIFIED**

- Exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Report-only branch: `review/r321-r317-compression-red-team-20260924`
- Capture/report time: `2026-09-24T10:11:42.992674Z` UTC
- Scope: targeted red-team of R317's compression claim only.
- No implementation, synthetic/public benchmark, data/dependency download, Actions, paid compute, private/holdout/full access, submission, main/PR/control edit.

## Question tested

R317's core claim was narrow:

> A genuinely distinct estimator would have to retain non-Gaussian gate/mask-conditioned information rather than collapse each layer back to one Gaussian or a fixed small mixture; no known representation was shown to compress that information to a Phase-2-feasible state for generic dense width-1024, depth-16 ReLU layers.

R321 tries to falsify that claim using primary mathematical literature. A qualifying falsifier must provide an exact or rigorously controlled approximate representation that:

1. remains valid for generic dense correlated Gaussian preactivations, not only low-rank, sparse, Markov, spatial-kernel or bounded-treewidth covariance classes unless those assumptions are established for the contest networks;
2. represents the gate-/orthant-conditioned information needed after ReLU without collapsing to the E038 single-Gaussian closure or E039 fixed small mixture;
3. has a polynomial-size propagated state and a derivable all-in cost compatible with Phase-2 budget `B=2^41=2,199,023,255,552` FLOPs and residual cap `0.4 s`;
4. supplies a rigorous approximation error bound if it is not exact.

## Red-team finding 1: a single correlated Gaussian orthant is not inherently exponential

The strongest correction to any over-broad reading of R317 comes from randomized Gaussian-volume algorithms.

### Kannan–Li (1996)

Ravi Kannan and Guangxing Li, **“Sampling According to the Multivariate Normal Density,”** FOCS 1996, pp. 204–212, DOI `10.1109/SFCS.1996.548479`.

Their primary problem is exactly approximate integration/sampling of a correlated multivariate normal over the **positive orthant**. They solve it in randomized polynomial time using rapidly mixing Markov chains.

This is already enough to reject the statement “one generic correlated Gaussian orthant probability necessarily requires exponential time.” R317 did not need that stronger claim, and R321 does not use it.

### Cousins–Vempala (2014)

Ben Cousins and Santosh Vempala, **“A Cubic Algorithm for Computing Gaussian Volume,”** SODA 2014, DOI `10.1137/1.9781611973402.90`; author version arXiv:1306.5829.

For a convex set (K\subset\mathbb R^n) satisfying the paper's roundness hypothesis (containing a unit ball), Theorem 1.1 gives, for (arepsilon,p>0), a randomized ((1+arepsilon))-approximation of Gaussian volume with probability (1-p) in

[
O!left(
n^3log n,
log^3(n/arepsilon),
log(1/p)/arepsilon^2
ight)
=O^*(n^3)
]

membership-oracle complexity.

Theorem 1.2 gives an (arepsilon)-TV approximate restricted-Gaussian sampler in (O^*(n^3)) work for the first point and (O^*(n^2)) for subsequent points.

Important scope points:

- the stated Theorem 1.1 roundness condition does **not directly match** a standard Gaussian centered at the apex of an orthant;
- the paper itself cites Kannan–Li's earlier positive-orthant polynomial-time algorithm;
- both results solve **one restricted Gaussian / one convex-set query**, not a simultaneous representation of all activation masks of a ReLU layer;
- the algorithms are randomized sampling/volume algorithms, not a finite gate-conditioned state closed under another dense ReLU layer.

Therefore these results are a real red-team counterexample to an “orthant integration is exponentially hard” argument, but **not** to R317's propagated-state compression claim.

### Phase-2 implication of the single-query theorem

At (n=1024), (n^3=1,073,741,824). Ignoring all logarithms and constants, just the explicit (1/arepsilon^2) factor in Cousins–Vempala yields:

- (arepsilon=0.1): (1.0737\times10^{11}) units, about (0.0488B), before logs/constants;
- (arepsilon=0.01): (1.0737\times10^{13}), about (4.88B), before logs/constants.

These are **orientation calculations only**, not FlopScope bounds. The theorem is in an oracle/random-walk cost model; the paper's executable description contains very large theoretical mixing constants. It gives no derivation of a (<0.4) s residual path. More importantly, there is no theorem connecting one orthant's relative probability error (arepsilon) to the final mean-MSE after 16 dense ReLU layers.

Applying a polynomial single-orthant routine separately to every active mask still leaves up to (2^{1024}) mask queries in an explicit gate-conditioned representation. Replacing explicit masks by restricted-Gaussian samples instead gives a finite-support sampling representation, not the requested distinct compact moment state.

## Red-team finding 2: genuinely fast TMVN moment algorithms exist, but require structural covariance assumptions absent for generic dense layers

This was the most serious candidate to falsify R317.

### Huang et al. (2021), Part I

Jingfang Huang, Jian Cao, Fuhui Fang, Marc G. Genton, David E. Keyes, George Turkiyyah, **“An O(N) algorithm for computing expectation of N-dimensional truncated multi-variate normal distribution I: fundamentals,”** *Advances in Computational Mathematics* 47, 65 (2021), DOI `10.1007/s10444-021-09888-1`.

They consider

[
phi(a,b;A)
=
int_a^b H(x) f(x\mid A),dx,
qquad A=\Sigma^{-1},
]

and obtain overall (O(N)) complexity under explicit structure:

- (H(x)) is low-rank;
- variables can be properly clustered;
- precision (A) has low-rank blocks and low-dimensional features;
- the rigorous simple cases are tridiagonal precision / exponential covariance;
- their exposition uses off-diagonal block rank (K=1) and at most two effective variables.

The paper states that the prefactor is controlled by off-diagonal block rank and the number of effective variables.

### Zheng et al. (2022), Part II

Chaowen Zheng, Zhuochao Tang, Jingfang Huang, Yichao Wu, **“An O(N) algorithm for computing expectation of N-dimensional truncated multi-variate normal distribution II: computing moments and sparse grid acceleration,”** *Advances in Computational Mathematics* 48, 71 (2022), DOI `10.1007/s10444-022-09988-6`.

The same structural assumptions remain: low-rank (H), low-rank blocks in both covariance/precision, and low-dimensional features.

Under the tridiagonal/exponential cases with (K=1), effective-variable count (P\le2), the paper gives simultaneous calculation of all moments of total order at most (M) in:

[
O(N^M),quad M\ge2,
]

and first-order moments in

[
O(N\log N).
]

For higher-rank/effective-dimension cases, sparse grids target roughly (K+P\approx5\ldots20). The paper explicitly states that when (K+P>20), practical tools for 20 truly independent variables are unavailable.

### Why these theorems do not apply to generic dense contest layers

The required structure is not invariant under an arbitrary dense covariance transport.

For any SPD current covariance (C) and any SPD target matrix (S), an invertible dense matrix

[
W=S^{1/2} C^{-1/2}
]

satisfies

[
W C W^T=S.
]

Thus, over generic dense (W), affine propagation can produce an arbitrary SPD covariance. No uniform guarantee of tridiagonal precision, exponential/spatial covariance, bounded off-diagonal hierarchical rank, bounded (K+P), sparsity, or conditional independence follows from the dense architecture.

No R317/R321 project evidence establishes those structural assumptions for the contest networks. Under the user's rule, they therefore cannot be used to claim Phase-2 applicability.

Consequently the attractive (O(N)), (O(N\log N)), and (O(N^2)) moment complexities are **conditional theorems**, not generic-dense bounds.

## Red-team finding 3: hierarchical low-rank approximation is fast but not rigorously controlled for the generic case

Jian Cao, Marc G. Genton, David E. Keyes, George M. Turkiyyah, **“Hierarchical-block conditioning approximations for high-dimensional multivariate normal probabilities,”** *Statistics and Computing* 29, 585–598 (2019), DOI `10.1007/s11222-018-9825-3`.

The method combines hierarchical covariance approximations with (d)-dimensional conditioning and reports a major cost of (O(n\log n)). But the primary paper explicitly states:

- the runtime depends on a diagonal block size (m) and conditioning dimension (d);
- blocks of the covariance are replaced by low-rank approximations;
- (d) trades accuracy for expensive lower-dimensional computations;
- the method has **no internal estimate of approximation error** for tuning;
- its ~1% reported errors are empirical results on 2D spatial-statistics covariance problems.

Therefore it does not provide the controlled approximation theorem required by R321, and its structural covariance assumptions are not guaranteed for a generic dense ReLU layer.

## Red-team finding 4: tile-low-rank QMC has error guarantees but is both structurally conditional and a sampling method

Jian Cao, Marc G. Genton, David E. Keyes, George M. Turkiyyah, **“Exploiting Low Rank Covariance Structures for Computing High-Dimensional Normal and Student-t Probabilities,”** *Statistics and Computing* 31, 2 (2021), DOI `10.1007/s11222-020-09978-y`.

The method combines:

- a tile-low-rank covariance representation,
- block reordering,
- quasi-Monte Carlo / Monte Carlo probability estimation.

It handles very high-dimensional **spatial-statistics** examples and is presented as a probability estimator with error guarantees. It still requires useful low-rank covariance blocks, which generic dense contest propagation does not guarantee. If used without a persistent gate-conditioned representation, its state is samples/QMC points and it belongs to the already occupied stochastic/cubature family recorded by R308 rather than a new orthant-state compression family.

## Red-team finding 5: moment recurrences are not a compressed deep state

Raymond Kan and Cesare Robotti, **“On Moments of Folded and Truncated Multivariate Normal Distributions,”** *Journal of Computational and Graphical Statistics* 26(4), 930–934 (2017), DOI `10.1080/10618600.2017.1322092`.

They derive recurrence relations and explicit low-order moment expressions for folded/truncated multivariate normals. This is valuable for evaluating moments of **one specified truncated distribution**. It does not supply a theorem that merges all ReLU masks into a polynomial-size non-Gaussian state that remains closed after the next generic dense layer.

Thus it improves local moment evaluation but does not falsify the state-compression part of R317.

## Exact-closure barrier: useful supporting theorem, but not a direct contest impossibility proof

Jan Macdonald and Stephan Wäldchen, **“A Complete Characterisation of ReLU-Invariant Distributions,”** AISTATS 2022, PMLR 151:1457–1484.

Their Theorem 2.6 states that for a continuous (n)-parameter family (p:\Omega\to\mathcal D(\mathbb R^d)) invariant under the paper's full class

[
x\mapsto \operatorname{ReLU}(Wx+b),
]

at least one must hold:

1. (d=1);
2. every distribution has finite support;
3. the parametrization is not locally Lipschitz.

This is strong evidence that a regular finite-parameter **exactly closed** distribution family is not available in ordinary multidimensional ReLU networks, except for finite-support sampling or pathological parametrizations.

However, R321 does **not** use this as a formal impossibility proof for the contest because:

- the theorem's invariance class includes arbitrary biases, while the relevant ARC lanes use bias-free ReLU MLPs;
- it concerns exact invariance, not controlled approximation;
- it does not supply a FLOP lower bound.

It is supporting context, not the decisive no-go.

## Required distinction: one-query tractability versus propagated-state compression

The literature screen separates three different questions that must not be conflated.

| Problem | Literature status | R321 relevance |
|---|---|---|
| One correlated Gaussian orthant probability | randomized polynomial-time algorithms exist | disproves any blanket “orthant = exponential” claim |
| Moments of one structured TMVN | (O(N)), (O(N\log N)), (O(N^M)) algorithms under hierarchical/low-rank assumptions | assumptions not guaranteed for generic dense ARC covariance |
| All gate-conditioned information propagated through generic dense ReLU layers | no qualifying exact or rigorously controlled polynomial-size representation found | this is the actual R317 claim; not falsified |

The output-size issue also remains: an explicit mask-indexed state has one component for every material sign pattern. A single-query algorithm can avoid enumerating masks **for that query**, but no primary theorem located here supplies a reusable compressed object from which the required non-Gaussian conditionals can be propagated through the next arbitrary dense (W) while retaining a rigorous global approximation bound.

## Deduplication against project lanes

### E038

E038 (result blob `665ad6ee0ef4661a2bdb76eb7cf4f0af1c4988d1`) is the single-Gaussian full-covariance layerwise closure. Any scheme that uses orthant routines only to recover a mean/covariance and then re-Gaussianizes is E038 territory and is excluded.

### E039

E039 (result blob `7556cdfda8227bfc0ee1936c2a463d48d9c73d2f`) is a fixed two-component half-space Gaussian mixture. Replacing two components by another fixed small number does not answer R321 and is excluded.

### E114–E119

E114 provides an exact deep activation-boundary flux representation. E119 (result blob `b31551896b7138309da1cf17fe651674b1a5a9c5`) made the state weight-driven on exact small networks but its rigorous omission certificate retained approximately 98.18%–98.80% of boundary atoms and omitted no nonzero-flux atom. R321 found no primary Gaussian-orthant theorem that turns this already-occupied boundary state into a generic dense polynomial-size exact/controlled representation.

### R308 / R317

R308 already marks sampling/QMC/cubature, conditional-Gaussian, mixtures, low-rank carriers and boundary-flux as occupied families. R321 therefore does not relabel:

- restricted-Gaussian random-walk samples as “gate-conditioned compression”;
- tile-low-rank QMC as a new family;
- single-Gaussian moment propagation as exact orthant closure;
- a fixed small component mixture as a new truncated-Gaussian family.

R317's report blob is `102854932f111e793657747a4aa227b23f19e7fc`.

## All-in Phase-2 implications

### Exact explicit mask state

If all mask-conditioned first/second moments are stored explicitly, worst-case state is at least

[
\Theta(2^n n)
]

for first moments or

[
\Theta(2^n n^2)
]

with full conditional covariances, before depth compounding. At (n=1024), this is not Phase-2 feasible.

This is an explicit-state output-size statement, not a claim that one orthant integral itself needs exponential work.

### Polynomial single-query random-walk methods

They avoid explicit enumeration for one convex-set probability or restricted sample, but:

- are stochastic;
- have accuracy/failure parameters and polylog/error factors;
- have no theorem converting their oracle complexity into the contest's FlopScope/residual limits;
- do not create a reusable all-mask state;
- sample-based propagation falls into an already occupied estimator family.

No (<2^{41}) all-in bound and no (<0.4) s residual bound can be derived honestly from these papers for the 16-layer task.

### Hierarchical low-rank TMVN methods

When their structural assumptions hold, their asymptotics are excellent. For the generic dense contest case, however, (K), (P), hierarchical block ranks and conditioning dimension are uncontrolled. Therefore their stated complexity cannot be instantiated into a valid production upper bound.

## Independent verdict

**R321 = EVIDENCE-BASED INDEPENDENT NO_GO. R317's core compression claim is not falsified.**

The red-team did find one substantive correction:

> High-dimensional correlated Gaussian orthant integration itself has randomized polynomial-time algorithms. Therefore the no-go must not rest on “a single orthant probability is exponential.”

But no primary-source theorem found here supplies the required stronger object:

> an exact or rigorously controlled, polynomial-size, non-sampling representation of gate/mask-conditioned moments that remains valid through arbitrary dense width-1024 ReLU layers and carries a derivable Phase-2 FLOP/residual bound.

The closest fast TMVN results require hierarchical low-rank / low-effective-dimensional covariance or precision structure; the contest's generic dense linear maps do not guarantee that structure. The generic polynomial Gaussian-volume results answer one restricted-distribution query, not the deep propagated-state problem.

Therefore no qualifying theorem falsifies R317.

## What would falsify this verdict

A future paper/theorem would need to provide all of:

1. validity for arbitrary or provably contest-realized dense SPD covariance, without bounded-rank/treewidth/spatial-kernel assumptions;
2. a compressed non-Gaussian state that survives (x\mapsto\operatorname{ReLU}(Wx)) without enumerating (2^n) masks, collapsing to one Gaussian, or using a fixed small mixture;
3. an exact identity or a composable approximation bound controlling layer-to-layer expectation error;
4. a polynomial state/work bound whose constants and accuracy dependence permit an all-in (<2^{41}) FLOP derivation and a credible (<0.4) s residual path.

None of the primary results audited in R321 satisfies all four.
