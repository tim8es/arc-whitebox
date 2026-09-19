# E110 protocol — exact deep Gaussian-line Rao–Blackwellization

Idempotency key: `ARC-E110-DEEP-LINE-RB-20260919`

Status at freeze: **ONE INDEPENDENT SMALL-WIDTH LAW FALSIFIER AUTHORIZED**.

## Provenance and non-overlap

- Branch: `research/e110-deep-line-rb-20260919`.
- Direct parent: E108 terminal head
  `073c6b66064a12fdcd18ab939002ab5458f48f69`.
- E104 target-transfer is closed/failed and is not repeated.
- E109 is occupied by a deep Gaussian-Stein JVP control variate.
- E110 uses no Stein identity, no JVP control, no fitted beta, no first-layer
  exact-mean transport, no Haar/radial replacement, no benchmark target and no
  public/scorer/holdout/full data.
- Repository tree contains no AGENTS.md according to the prior E108 physical
  repository audit; no extra repository-local agent instruction is assumed.
- No tuning, sweep, rescue, rerun, canonical mutation or ledger mutation is
  authorized.

## Mechanism

Let `F:R^n -> R^n` be the fixed final-layer output of a zero-bias ReLU MLP
and let `X~N(0,I)`.

Choose one fixed unit direction `v` using weights only. Decompose

`X = Z + T v`,

where `T=v^T X ~ N(0,1)`, `Z=(I-vv^T)X`, and `T` is independent of `Z`.

Define the exact conditional estimator

`G(Z) = E_T[F(Z + T v) | Z]`.

Then

`E[G(Z)] = E[F(X)]`

and

`Var(G_j(Z)) <= Var(F_j(X))`

for every final coordinate `j`, by Rao–Blackwell.

The point of E110 is that, for a fixed `Z=z`, a finite ReLU network restricted
to the line `z+t v` is exactly piecewise affine in scalar `t`. Therefore
`G(z)` can be integrated exactly from the deep gate breakpoints, rather than
approximated by target fitting.

## Frozen direction

For width `n`, start at the final layer with

`g_L = 1/sqrt(n) * 1`.

Backpropagate a weight-only mean-gate sensitivity

`g_{l-1} = 0.5 * W_l * g_l`

for `l=L,...,1`, using the row-vector network convention `h_l=h_{l-1}W_l`.

Set

`v = g_0 / ||g_0||_2`.

A zero or non-finite norm is an integrity failure.

This direction uses all layers only to choose a fixed input axis. The exact
conditional expectation itself uses the realized deep ReLU breakpoints.

## Exact line integration

On any scalar interval `[a,b]`, every activation vector has the form

`h_l(t)=s_l t + c_l`.

For each current interval, propagate the two affine coefficient vectors through
the next weight matrix, collect every preactivation zero crossing inside that
interval, split at those roots, and apply the exact ReLU mask on each resulting
subinterval.

At the final layer each coordinate is affine,

`F_j(z+t v)=alpha_j t + beta_j`

on each interval. With standard normal density `phi` and CDF `Phi`,

`int_a^b (alpha t + beta) phi(t) dt
 = alpha [phi(a)-phi(b)] + beta [Phi(b)-Phi(a)]`.

Summing all final intervals gives `G(z)` without targets.

## Independent small-width law test

Frozen instance:

- width: `8`;
- depth: `5`;
- zero bias;
- float64 iid He-Gaussian weights `N(0,2/8)`;
- weight seed: `110104`;
- outer Gaussian samples: `96`;
- outer seed: `110105`;
- exact interval cap per conditioned sample: `20000`;
- direct numerical-law check on the first `4` conditioned samples;
- numerical integration grid: `32769` equally spaced points on `[-8,8]`;
- no target/reference labels.

For each outer draw `x_i`, form `z_i=x_i-(v^T x_i)v`.

Baseline observation:

`Y_i = F(x_i)`.

Candidate observation:

`G_i = E_T[F(z_i + T v)|z_i]`

from exact breakpoint integration.

Target-free single-sample pooled final-coordinate variances are

`V_base = mean_j sample_var_i(Y_{ij})`,
`V_cond = mean_j sample_var_i(G_{ij})`.

For an iid mean of `N` such observations, the corresponding target-free MSE
risk estimate is `V/N`.

## Independent law check

For the first four frozen `z_i`, compute a separate dense trapezoidal
standard-normal integral of `F(z_i+t v)` on `[-8,8]`.

The breakpoint integral must agree with this independent numerical integral at
max relative error `<=2e-4`.

## Budget/path diagnostic

The production E104 verification measured the 4096-trajectory 16-layer forward
core at

- layer FLOPs: `137573171200`;
- budget: `B=2^41`.

An exact line conditional sample must propagate **two affine coefficient
streams** (slope and intercept) through every active line interval. Ignoring
root finding, sorting, Gaussian integration, direction setup and input setup,
a production lower bound for `N` conditioned samples is

`F_layer_lower(N)
 = 2 * M * 137573171200 * (N/4096)`,

where `M` is the measured mean number of entering line intervals per layer
relative to the one-interval ideal.

Using the hard utilization cap `0.13`, define the optimistic sample ceiling

`N_budget_upper
 = floor(4096 * (0.13*2^41)
         / (2*M*137573171200))`.

This is intentionally optimistic because all non-layer costs are omitted.

The measurable target path diagnostic is

`R_budget = V_cond / N_budget_upper`.

The raw target scale is `1.89e-8`.

## Frozen gates

Integrity/law gates:

1. direction norm finite and positive;
2. all baseline/candidate outputs finite;
3. no interval-cap overflow;
4. final piecewise intervals form a complete ordered partition of the real line;
5. independent dense-integration max relative error `<=2e-4`;
6. `V_cond < V_base`;
7. variance ratio `V_cond/V_base <=0.80`.

Path gate:

8. optimistic budget ceiling `N_budget_upper >= 1`;
9. `R_budget <= 1.89e-8`.

All nine gates must pass for **SMALL_WIDTH_TARGET_FREE_PATH_GO**.

Any failed or unevaluable gate => **TERMINAL_NO_GO / DROP E110**. No alternate
direction, seed, width, depth, interval cap, target threshold, rerun, sweep,
public diagnostic, scorer, holdout/full or post-result rescue is allowed.

A pass would justify a separate production-shape successor only. It would not
authorize public evaluation and would not establish competition raw MSE.

## Evidence

The sole workflow must record:

- protocol/method/test/workflow SHAs;
- focused test result;
- outer sample count;
- independent-law max abs/relative error;
- baseline/candidate pooled variance and ratio;
- per-layer interval counts and mean interval multiplier;
- exact affine-matmul FLOP proxy;
- optimistic production sample ceiling under utilization 0.13;
- projected target-free risk `R_budget`;
- final verdict;
- public/scorer/holdout/full/benchmark-target access all false.

