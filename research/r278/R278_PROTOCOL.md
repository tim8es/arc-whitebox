# R278 Protocol — global output-space residual direction diagnostic

Job: R278  
Owner: `residual-structure-diagnostic`

## Pinned inputs

- V25 source commit: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- R209 normalized mini:all-100 blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- evaluator: `whestbench 0.16.1`
- meter: `flopscope 0.12.1+np2.4.6`
- panel: public development `mini:all-100`
- R276 report blob: `4970614c1ac789b008260d726a2bbd5272116434`
- R276 receipt blob: `56f40cc6b109d769e521c9ba0cf363c7683ef5ab`

## Frozen split

Before inspecting or computing any raw residual vectors, split the immutable 100 network IDs as follows:

1. Convert each `network_id` to its decimal string exactly as stored.
2. Sort ascending lexicographically.
3. First 50 IDs = FIT.
4. Last 50 IDs = EVAL.

This rule is target/prediction independent and fixed for the whole task. No network may change fold after residual inspection.

## Frozen global fit/evaluation rule

For each network, let `p_i` be V25's final-layer 1024-vector and `y_i` the official target final-layer 1024-vector, both captured faithfully from the same pinned runner/evaluator path.

FIT residuals: `r_i = y_i - p_i`.

Fit exactly one network-agnostic output-space correction vector:

`d = mean_{i in FIT}(r_i)`.

No per-network scalar, sign, rank, selector, feature, normalization, or tuning is allowed.

Evaluate on EVAL only:

`p_i_corrected = p_i + d`.

Primary diagnostic quantities on EVAL:
- baseline and corrected final-layer MSE per network;
- paired MSE delta, mean delta, sample SD and SE across the 50 EVAL networks;
- fraction of EVAL networks improved;
- coordinate-wise residual energy explained by the fixed vector, summarized globally and by central quantiles;
- failures and vector provenance.

A score impact may be reported only if the correction is inserted into an honestly metered estimator path under the pinned evaluator/meter. An offline NumPy addition is diagnostic only and must not be called an official adjusted score.

## Materiality gate

Evidence for a meaningful common global residual direction requires all of:
- EVAL mean raw MSE improves by at least 2.0%;
- at least 30/50 EVAL networks improve;
- mean paired MSE gain > 2 descriptive SE;
- median EVAL raw MSE improves (not merely a few outliers).

Otherwise classify as no material common direction for this exact rule.

## Execution bound

At most one bounded diagnostic after instrumentation is validated. No Actions, no paid compute, no private/holdout/full data, no submission, no leaderboard/canonical edits, and no per-network tuning.

If raw vectors cannot be obtained faithfully on the available local resource, stop with a precise blocker and do not infer the diagnostic result.
