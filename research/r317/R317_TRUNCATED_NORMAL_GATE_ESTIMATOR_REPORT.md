# R317 — theory-first screen: truncated-Gaussian / orthant-moment integration for deep ReLU expectations

Status: **EVIDENCE-BASED NO_GO BEFORE IMPLEMENTATION OR EXECUTION**

- Exact base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Report-only branch: `review/r317-truncated-normal-gate-estimator-20260924`
- Capture/report time: `2026-09-24T09:59:03.377473Z` UTC
- No code, synthetic/public benchmark, dependency/data download, Actions, paid compute, holdout/full access, submission, main/PR/control edit.

## Question

Can exact or higher-fidelity truncated-multivariate-normal / orthant-moment identities provide a genuinely distinct, Phase-2-cost-feasible estimator for layerwise expected activations of width-1024, depth-16 ReLU MLPs?

## Primary mathematical sources

The relevant identities are real and classical:

1. G. M. Tallis, “The Moment Generating Function of the Truncated Multi-Normal Distribution,” *JRSS B* 23(1), 223–229 (1961), DOI https://doi.org/10.1111/j.2517-6161.1961.tb00408.x. Tallis derives the truncated multivariate-normal moment generating function and formulas for first and second moments.
2. S. Rosenbaum, “Moments of a Truncated Bivariate Normal Distribution,” *JRSS B* 23(2), 405–408 (1961), DOI https://doi.org/10.1111/j.2517-6161.1961.tb00422.x. This directly treats correlated bivariate-normal moments under truncation.
3. R. L. Plackett, “A Reduction Formula for Normal Multivariate Integrals,” *Biometrika* 41(3–4), 351–360 (1954), DOI https://doi.org/10.1093/biomet/41.3-4.351. This supplies the classical reduction structure for multivariate-normal probabilities.
4. R. Price, “A useful theorem for nonlinear devices having Gaussian inputs,” *IRE/IEEE Transactions on Information Theory* 4(2), 69–72 (1958), DOI https://doi.org/10.1109/TIT.1958.1057444. Price relates derivatives of Gaussian-input nonlinear output correlations to derivative-transformed nonlinearities; the project already used this as a Gaussian covariance-response route.

These identities make exact Gaussian orthant moments mathematically available. The R317 issue is not whether those moments exist; it is whether using them defines a new estimator family and whether retaining enough gate-conditioned information to escape Gaussian closure is production-feasible.

## Exact project deduplication

### Direct duplicate: E038 conditional-Gaussian full-covariance ReLU kernel

The closest prior work is stronger than a lexical overlap.

Authoritative branch:
`research/e038-conditional-gaussian-cov-20260915`

- protocol blob: `06993b1f3fc0670c1e6f2c08ac36e0a6242994b4`
- result blob: `665ad6ee0ef4661a2bdb76eb7cf4f0af1c4988d1`

E038 already carried exactly one multivariate Gaussian state ((\mu,C)) per layer:

[
\mu^- = W\mu,qquad C^- = W C W^T,
]

then used the exact univariate Gaussian ReLU moments

[
E[X_+] = \sigma\phi(\alpha)+\mu\Phi(\alpha),
]

[
E[X_+^2] = (\mu^2+\sigma^2)\Phi(\alpha)+\mu\sigma\phi(\alpha),
]

and computed every pairwise post-ReLU second moment with a fixed conditional-Gaussian integration kernel preserving arbitrary means and correlations. Its post-ReLU covariance was then

[
C^+ = M - \mu^+{\mu^+}^T.
]

That is the same estimator **state and closure family** that one obtains by replacing the E038 16-node conditional integral with exact Tallis/Rosenbaum/Plackett bivariate orthant moments:

[
M_{ij}
=
E[Z_i Z_j,1\{Z_i>0,Z_j>0\}],
qquad
(Z_i,Z_j)\sim N(m_{ij},\Sigma_{ij}).
]

Using a closed-form or exact bivariate-normal probability/moment evaluator instead of E038's fixed quadrature changes only how the Gaussian pair moment is numerically evaluated. It does **not** change the representation: one Gaussian mean vector plus one covariance matrix, re-Gaussianized after every ReLU.

Therefore “exact orthant moments inside a single-Gaussian layerwise closure” is a **duplicate/descendant of E038**, not a genuinely distinct R317 family.

E038 production-shape evidence also already answers cost-vs-representation:

- width/depth: 1024/16
- billed FLOPs: `174310368260`
- utilization: `0.079267178198279`
- residual wall: `0.3520044520000738 s`
- raw final-layer MSE: `1.1938567981733376e-05`
- raw accuracy gate: `1.89e-08`
- miss: about `631.67x`

Thus the single-Gaussian full-covariance family was computationally feasible but scientifically far from the required accuracy. The result explicitly concluded that missing information is higher-order/non-Gaussian cross-neuron structure, not merely a more nonlinear Gaussian covariance transform.

An exact bivariate orthant evaluator might change E038's numerical quadrature error, but there is no evidence that it changes the representation error, and under the novelty rule it is still the same family.

### E036 Price covariance is the same Gaussian-response axis

Branch:
`research/e036-price4-covariance-20260915`

- protocol blob: `fd191c7b88ce8af759bf8467b2db0e052a36d2c0`
- result blob: `fc27202a39e5fa825754ea50e11366bb7ef3b1be`

E036 propagated full covariance and used the first four Price-series terms for Gaussian cross-neuron ReLU covariance. It measured raw MSE `4.9459251622589696e-05` at utilization `0.05915499703587557`; increasing the Gaussian covariance-response fidelity from the first Price term to order four did not materially solve the error.

R317 exact Tallis/Rosenbaum pair moments are best viewed as the non-series completion of this same Gaussian pair-response object; E038 already implemented that full nonlinear Gaussian-response lane.

### E111 independently isolates the Gaussian-closure bias

Branch:
`research/e111-late4-gaussian-relu-plugin-cost-20260919`

Terminal receipt blob:
`91d8ce0c2314c5356456e05dc646a6630751788d`

E111 gave the Gaussian ReLU plug-in **exact pre-ReLU first two moments** on an exact width-8/depth-4 zero-bias reference. Layer 1, where the preactivation is genuinely Gaussian, was exact to floating point. Immediately after the first ReLU, the Gaussian plug-in bias became large:

- layer-2 mean-bias MSE: `2.460899425463496e-3`
- final layer mean-bias MSE: `1.6698051697168073e-3`
- competition raw target: `1.89e-8`
- final bias/target: `88349.48x`

The terminal interpretation is directly relevant: exact first two moments do not restore Gaussianity after ReLU gating. This is a representation-bias obstruction that exact Gaussian orthant moments cannot remove if the state is collapsed back to one Gaussian after each layer.

### Half-space Gaussian-mixture lane is already occupied

The historical `research/e038-halfspace-gaussian-mixture-20260915` protocol (blob `95797eff05392d01d080ca69d737b8dec4344dd8`) was re-keyed as authoritative E039:

- E039 protocol blob: `c7d96d16e2e75500277d6892a6f8c9c1ac0f5674`
- E039 result blob: `7556cdfda8227bfc0ee1936c2a463d48d9c73d2f`

It propagated two gate-conditioned Gaussian location components plus shared full covariance. The family was cheap and stable but measured raw MSE `4.502602651621096e-06`, still far outside the target.

Therefore retaining only a small fixed number of truncated/half-space Gaussian components is also not a new R317 family.

### E030 already tested conditional-Gaussian latent-state integration

Branch:
`research/e030-r8-conditional-gaussian-carrier-20260915`

- protocol blob: `ef37753b1fe0e39abb82663dbec6fcd10ca9e38d`
- result blob: `a8a3b0b104ee7e04cbdcb480142915a91a58d13b`

E030 explicitly integrated ReLU means conditionally over a Gaussian latent carrier while analytically marginalizing diagonal Gaussian noise. It is another already-occupied conditional-Gaussian moment family and terminated NO-GO when its frozen covariance carrier became non-finite.

### E104 is adjacent but not the same mechanism

Branch:
`research/e104-haar-radial-raoblackwell-20260918`

- protocol blob: `61d5abb0ce7f773fdc05ee5b0ab787a6f2237930`
- result blob: `e896296de3c487a88f522d3fca3182645205ef86`

E104 is an exact Rao–Blackwellization of random Gaussian radii conditional on Haar directions, using positive homogeneity. It is a sampling-variance reduction family, not layerwise truncated-normal moment propagation. R317 therefore does not duplicate E104 specifically, but E104 prevents relabeling “conditional expectation under Gaussian structure” as novelty by itself.

## Requested recent R2xx deduplication

The recent evidence does not create an unused version of the R317 idea:

- **R209** archive blob `7fec90369227839a9902c7cceb9f3519acb66cb8`: clean V25 reference, 100/100 valid, mean raw MSE `2.228303490170447e-8`, mean measured FLOPs `806303721965`, max residual `0.19043814401743475 s`.
- **R223** protocol blob `1e88341a6320bf91c8f4eff0aa60d8b6a33cf484`; later normalized result blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`: local K4->K3 feed-lambda family, not an orthant-moment lane and slightly worse than R209 on the compatible panel.
- **R231** report blob `f617d1991f576a48261d329ad237be24d0a811b7`: V25 error is broad-based rather than tail-dominated; a useful replacement must improve the central bulk under one global rule.
- **R238** protocol/result blobs `757e3f67741b9e05b709a247eae5c9a921d787e6` / `0c0be7f5bd2bb25f7f106fc2721b6307baf2d8ad`: recycled-start range finder; distinct and unrelated.
- **R265** report blob `e9b5df06173bf70a587774f9374042962847d9e2`: its full-history inventory explicitly lists covariance, conditional-Gaussian, mixture, cumulant, gate-conditioned and exact-mask closures as already occupied.
- **R269** report blob `8ea0fdf39e80483d005b0a9828f75a4eae291ee3`: randomized depth-prefix multilevel telescope; unrelated and rejected pre-execution.
- **R276** report blob `4970614c1ac789b008260d726a2bbd5272116434`: again records conditional-Gaussian/mixture closures as occupied and finds no remaining concrete global accuracy family.
- **R308** report blob `e07ddccdf3744c741a571556d7597ac15b460c4b`: full-history theory scout concludes that Gaussian/mixture/cumulant and adjacent closure families are already represented and refuses to relabel them.

## Could full orthant-conditioned moments escape the duplicate?

There is one mathematically distinct interpretation: do **not** collapse each layer back to one Gaussian. For a Gaussian preactivation (Z\in\mathbb R^n), decompose by activation mask (s\in\{0,1\}^n):

[
p_s=P(\operatorname{sign}(Z)=s),
]

and carry the exact moments of the truncated Gaussian

[
Z\mid \operatorname{sign}(Z)=s.
]

After ReLU, each mask supplies one gate-conditioned component. Tallis/Rosenbaum/Plackett identities can support moments/probabilities for such truncated Gaussian pieces.

This would indeed retain information that single-Gaussian E038 discards. R321 independently red-teamed the compression claim and narrows the obstruction: **do not infer that one correlated Gaussian orthant/convex-set query is inevitably exponential.** Kannan–Li (FOCS 1996, DOI `10.1109/SFCS.1996.548479`) and Cousins–Vempala (SODA 2014, DOI `10.1137/1.9781611973402.90`) give randomized polynomial-time algorithms for relevant Gaussian restricted-volume/sampling queries.

The production blocker is instead the persistent state needed to compose through further generic dense ReLU layers:

1. if mask-conditioned first moments are stored explicitly, the output-size lower bookkeeping is `Θ(2^n n)`; with one full conditional covariance per mask it is `Θ(2^n n^2)`;
2. a randomized polynomial-time algorithm for **one** orthant/convex-set probability or restricted-Gaussian sample does not materialize a reusable non-Gaussian all-mask state, does not by itself compose through the next arbitrary dense `W`, and supplies no contest-level propagated-error or FlopScope/residual guarantee for the 16-layer estimator;
3. collapsing the conditional information back to one mean/covariance returns to E038;
4. retaining only a fixed small mixture returns to the already-occupied E039/half-space-mixture family unless a genuinely new compression theorem is supplied.

The project's exact non-Gaussian alternative reaches the same obstruction from a different representation. E114 established an exact activation-boundary-flux identity for deep zero-bias ReLU expectations; E119 later built the boundary state mechanically on width<=8/depth<=4 but its rigorous omission certificate retained about 98.18%–98.80% of boundary atoms and could not safely discard even one nonzero atom on the frozen corpus. That is direct project evidence against assuming a compact exact gate/boundary representation without a new structural theorem.

## Complexity / Phase-2 feasibility

Two cases must be separated.

### A. Single-Gaussian exact pair moments

State:
((\mu,C)), with full (n\times n) covariance.

Per layer:
- affine covariance transport: (O(n^3));
- exact pairwise ReLU second moments: (O(n^2)) bivariate orthant-moment evaluations;
- memory: (O(n^2)).

At (n=1024,L=16), this order is compatible with the FLOP budget in principle; E038 already measured `174.31e9` billed FLOPs, only `0.0793 B`. Its residual `0.3520 s` was already close to the `0.4 s` cap, and R317 has no measured or source-proven residual cost for a vectorized exact bivariate-normal CDF/moment primitive.

This case is **cost-plausible but duplicate and accuracy-obstructed**.

### B. Exact gate-conditioned truncated-Gaussian mixture

State:
all materially relevant orthants/activation regions and their truncated moments.

For an **explicit all-mask representation**, the output-size state per dense layer is at least

- `Θ(2^n n)` if each mask carries its conditional first moment;
- `Θ(2^n n^2)` if each mask carries a full conditional covariance.

These are explicit-state sizes, not lower bounds on the complexity of a single orthant integral. R321 verified that randomized polynomial-time single-query Gaussian-volume/sampling algorithms exist. What R321 did **not** find is a reusable polynomial-size non-Gaussian state that preserves the required gate-conditioned information, composes through arbitrary dense layers, has a rigorous propagated approximation bound, and admits a derived Phase-2 FLOP/residual bound.

This case is therefore **mathematically distinct but not plausibly cost-feasible** for (n=1024,L=16) under the Phase-2 FLOP/residual caps on the audited evidence.

## Boundary-integral variant

Gaussian boundary/Price identities do not create a third route:

- using the boundary derivative only to reconstruct **Gaussian pair moments** is E036/E038 territory;
- using the actual deep network activation boundaries to avoid Gaussian closure is the E114–E119 boundary-flux family, whose current blocker is representation size/compressibility rather than the validity of the identity.

Thus “boundary integral” is either a duplicate Gaussian moment evaluator or an already-occupied exact boundary-geometry family.

## R324 clarification from independent R321 red-team

R321 independently audited this exact compression claim on branch `review/r321-r317-compression-red-team-20260924`, head `774aac4105bfe1a171f40f7272fc4267aae6c2f8`, report blob `b0b71f4d74596c4744d0353d1654ac5726aeb2bb`, receipt blob `2c3d9f881d669ee924cecca106611c6c295a7243`.

Its result **confirms the narrow R317 NO_GO but adds an important caveat**:

- one generic correlated Gaussian orthant/convex-set query can have randomized polynomial-time approximation/sampling algorithms (Kannan–Li 1996; Cousins–Vempala 2014);
- therefore R317 must not claim that a single orthant query is inevitably exponential;
- the unresolved production object is a **reusable polynomial-size non-Gaussian all-mask state** that survives repeated generic dense ReLU transforms;
- explicit state has output size `Θ(2^n n)` for per-mask first moments or `Θ(2^n n^2)` for per-mask full covariances;
- single-query randomized sampling/volume computation does not create that persistent state and gives no theorem mapping its query error/work to final 16-layer activation-mean error, `<2^41` billed FLOPs, and `<0.4 s` residual time.

R321 additionally screened fast structured TMVN algorithms, including hierarchical/low-rank methods, but their rank/sparsity/conditional-structure assumptions are not guaranteed by generic dense contest covariance transport. No qualifying generic-dense compression theorem was found.

## Decision

**R317 = NO_GO_BEFORE_IMPLEMENTATION.**

Reason:

1. The production-feasible version — exact Tallis/Rosenbaum/Plackett bivariate orthant moments inside a single-Gaussian layerwise closure — is not a new estimator family. It is a direct numerical refinement/descendant of authoritative E038 conditional-Gaussian full-covariance propagation, with E036 and E111 supplying additional negative evidence that Gaussian-response fidelity is not the missing representation.
2. The genuinely distinct version — retaining gate-conditioned truncated-Gaussian information across layers — has an explicit all-mask output size of `Θ(2^n n)` for conditional means or `Θ(2^n n^2)` for full conditional covariances. R321 confirms that this must **not** be confused with the complexity of one orthant query: randomized polynomial-time single-query algorithms exist. The blocker is that no audited theorem supplies a reusable polynomial-size non-Gaussian state with rigorous propagated error and credible `<2^{41}` FLOP / `<0.4 s` residual bounds for generic dense layers.
3. A boundary-integral escape route is already represented by E114–E119 and currently lacks material certified compression.

No gain is predicted. No estimator is preregistered, implemented, or run, because the novelty/cost gate fails at theory screen.

## Re-entry condition

A future task would need a **new theorem or representation**, not a different single-query Gaussian integral evaluator: specifically, a target-free reusable compression of gate-conditioned orthant/boundary state with a proved polynomial-size state bound, composable layer-to-layer error control, and an all-in Phase-2 FLOP/residual bound. Without that, exact orthant moments either collapse back to E038/E039 or require an explicit all-mask state of exponential output size; polynomial-time single-query Gaussian-volume/sampling algorithms do not by themselves solve that persistent-state problem.
