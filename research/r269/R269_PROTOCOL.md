# R269 frozen multilevel-debiasing feasibility protocol

Job: R269  
Owner: `multilevel-debiasing-scout`  
Run: `R269-multilevel-theory-20260923`

## Scope

R269 follows exactly one abstract family retained by R265: randomized multilevel debiasing / randomized telescoping. No public/R209 benchmark access, Actions/cloud, paid compute, private/holdout/full data, tuning, per-network selection, submission, canonical edits, or leaderboard edits are authorized.

Pinned evidence:

- R265 protocol commit: `0b4406b79ba785ec716657c65ba75673dea99f92`
- R265 sealed commit: `bc287eed95df49fb41d81d157b15471a5aa73a3d`
- R265 protocol blob: `8dbb3402792aeaf553628707dc7f51aa9e004cd0`
- R265 report blob: `e9b5df06173bf70a587774f9374042962847d9e2`
- current full history blob: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- pinned V25 source commit: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- pinned V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- R223 local-feed protocol blob: `1e88341a6320bf91c8f4eff0aa60d8b6a33cf484`
- E033 source-Hutchinson protocol blob: `9c5c3a4be96153a76516c77c1d909ab2d10b2e85`
- E095 output-subspace residual-sampling protocol blob: `b4bcd9d68edc49b6d74edd0b413df2fe58a34946`

The current history is unchanged from R265: 194 E-IDs and 631 artifact records. Direct lexical checks find no prior `multilevel`, `Rhee`, `Glynn`, `Russian roulette`, `Bernoulli`, `depth-prefix`, or `layer-prefix` mechanism. Randomized source/sample compression itself is not new: E033 already uses source-axis Hutchinson compression, and E095 already tests target-free residual sampling. R223 owns the feed-local lambda axis. Rank/source-age/tensor/K3 transport/arithmetic hierarchies remain excluded by R265/full history and the R269 assignment.

Primary mathematical references inherited from R265:

- M. B. Giles, “Multilevel Monte Carlo Path Simulation,” Operations Research 56(3), 2008, DOI `10.1287/opre.1070.0496`.
- C.-H. Rhee and P. W. Glynn, “Unbiased Estimation with Square Root Convergence for SDE Models,” Operations Research 63(5), 2015, DOI `10.1287/opre.2015.1404`.

## The only non-relabeling concrete V25 telescope

For a fixed width-1024, depth-16 MLP, pinned V25 deterministically emits post-ReLU mean rows
`mu_1, ..., mu_16`.

Define:

- level 0: `Y0 = mu_15`, obtained after the exact V25 prefix through layer 15;
- level 1: `Y1 = mu_16`, obtained by continuing the same exact V25 state through the final layer;
- frozen correction probability: `p = 1/2`;
- `B ~ Bernoulli(1/2)`, independent of model arithmetic;
- final-row estimator:
  `Z = Y0 + (B/p) * (Y1 - Y0)`.
- rows 1..15 of the returned prediction remain the exact V25 rows; only row 16 is replaced by `Z`.

This uses no Richardson extrapolation, local-feed coefficient, copula, K3 transport modification, rank/basis truncation, source-age/window truncation, or approximate arithmetic. It is a pure randomized telescoping wrapper around the existing V25 depth prefix and continuation.

The identity is exact:

`E_B[Z] = Y1`.

For any fixed unknown target vector `t`,

`E_B[||Z-t||^2 / n] = ||Y1-t||^2 / n + ((1-p)/p) * ||Y1-Y0||^2 / n`.

At `p=1/2`, the added raw-MSE term is exactly `||Y1-Y0||^2 / n`. Therefore this family cannot improve expected raw MSE over deterministic V25; any possible adjusted-score gain must come solely from expected FLOP reduction.

## Metered production path

The only permitted production construction would reuse the exact pinned V25 prefix state.

Always executed under the existing FlopScope NumPy path:

1. exact V25 setup and layers 1..15;
2. one Bernoulli decision sourced from the estimator's existing `fnp.random.default_rng(ctx.seed)` setup path;
3. if `B=1`, continue the exact pinned V25 final layer, including the V19 mean-only final path (`W @ mu`, `C @ w32` diagonal variance, source-stack transport, D3-only source contraction, Wick/nonlinear term program, pK->K mean assembly);
4. combine the final row using only metered `fnp` vector subtraction, scalar multiplication, and addition.

No Python-side numeric substitute, unmetered packing, or external arithmetic is admissible.

Let `C0` be the exact metered prefix cost through layer 15 and `C16` the incremental exact final-layer continuation cost. Then:

- full parent cost: `C1 = C0 + C16`;
- candidate worst-case cost: `C1 + O(n)` for the final vector combine;
- candidate expected cost at `p=1/2`: `C0 + 0.5*C16 + O(n)`.

R265 records the strongest compatible V25 measured mean cost as `806303721965` FLOPs/network. The pinned V25 source also calls its operation stream data-independent, but its docstring only gives an approximate older cost (`~1.83e12`). R269 does not promote either number into a new static proof of `C0` or `C16`: there is no separately committed meter decomposition for the exact layer-15 prefix/final-layer increment. Therefore a nontrivial honest pre-execution expected-production FLOP upper bound for this telescope is unavailable. The only safe bound inherited from the full parent is the full-parent worst-case path plus O(n), which does not quantify the expected saving required by the hypothesis.

This fails the mandatory pre-execution cost-bound gate independently of the correction-decay gate.

## Frozen deterministic synthetic target-free falsifier

The falsifier is frozen for discrimination but MUST NOT execute unless the theory/rationale and cost-bound gates above pass.

Fixture `R269-DEPTH-TELESCOPE-W32-D6-v1`:

- width `n=32`, depth `L=6`;
- dtype `float64` for fixture generation, cast to `float32` at estimator boundary;
- no external targets;
- deterministic weights:
  `W_l[i,j] = sqrt(2/n) * cos((l+1)*(i+1)*(j+1))`
  for zero-based `l,i,j`;
- no bias;
- input law is the estimator's standard Gaussian input assumption;
- no seed search, network selection, or parameter sweep.

The same V25 mechanism is evaluated only to expose its own predicted means and metered cost.

Define:
- `D5 = mu_5 - mu_4`;
- `D6 = mu_6 - mu_5`;
- correction-energy ratio `rho_V = ||D6||_2^2 / max(||D5||_2^2, 2^-100)`;
- incremental cost ratio `rho_C = (C6-C5) / max(C5-C4, 1)`;
- p=1/2 Bernoulli variance for the final correction `V6 = ||D6||_2^2 / n`.

Frozen discriminating gate:
- exact deterministic replay of `mu_4,mu_5,mu_6` and costs;
- finite values;
- `rho_V < 1`;
- `rho_V * max(rho_C,1) <= 0.5`, requiring correction energy to decay materially faster than incremental cost grows;
- the production cost decomposition must already have a valid static upper bound before this local test is allowed to run.

This is a target-free correction-decay/cost falsifier, not an accuracy benchmark.

## Pre-execution decision

NO_GO before local execution.

Two independent mandatory gates fail:

1. **No target-free mechanism rationale.** `mu_15` and `mu_16` are means of different neuron layers under different weight matrices. They share vector dimension but not coordinate identity. Nothing in the pinned V25 construction or history establishes that `mu_l` is an L2-convergent approximation sequence to the fixed final-layer vector as depth increases. The finite telescoping identity is algebraically true, but the correction-decay premise required by multilevel debiasing is unsupported. Running the fixture merely to discover whether an arbitrary depth difference happens to be small would be method fishing.

2. **No honest nontrivial production expected-cost bound.** The exact parent path is known and metered historically, but the exact prefix/final-increment decomposition required for `C0 + p*C16` has no committed static or metered bound. The source's `~1.83e12` comment is approximate and cannot be treated as a rigorous bound. R269 may not execute simply to manufacture the missing cost evidence because the theory gate already failed.

Accordingly the frozen synthetic falsifier remains unexecuted.
