# E113 protocol — top-2 gate-conditioned non-Gaussian moment closure

Idempotency key: ARC-E113-TOP2-GATE-CONDITIONAL-MOMENTS-20260919

Status: PREREGISTERED / EXACT SMALL FALSIFIER ONLY.

## Provenance and non-duplication

- Branch: research/e113-top2-gate-conditional-moments-20260919.
- Parent: E104 accounting-complete head dc4c1f8edfae07841b0c32be4004c352c8dcd1dd.
- E111 global Gaussian-ReLU plug-in is terminal because later-layer bias is large.
- E112 exact full-mask message passing is a separate exact-state/treewidth lane.
- E113 does not enumerate full masks in production. It conditions each output neuron only on two target-free upstream gate signs chosen from its current weight column.

No benchmark/public/public-mini targets, scorer, holdout/full, tuning, sweep, rescue, canonical mutation, ledger mutation, or merge.

## Candidate

For later layer l and output neuron j with current weight column W[:,j]:

1. Choose gate indices i1,i2 as the two largest |W[i,j]| values, stable tie-break by lower index.
2. Let s1=1[h_prev_pre[i1]>0], s2=1[h_prev_pre[i2]>0].
3. Partition the law of current preactivation z_j into the four groups (s1,s2).
4. In each group retain only conditional mean and variance of z_j.
5. Replace that conditional non-Gaussian law by a Gaussian with the same first two moments.
6. Compute conditional ReLU mean and second moment analytically:
   m = sigma*phi(alpha) + mu*Phi(alpha), alpha=mu/sigma.
7. Mix the four conditional outputs with exact group probabilities.

Layer 1 has no previous gates and uses the ordinary exact Gaussian-ReLU formula.

This is a fixed target-free conditional-moment rule. No residual labels or target fitting are used.

## Frozen exact falsifier

- input X ~ N(0,I_2);
- width 8;
- depth 4;
- zero bias;
- PCG64 seed 113113;
- first layer W0 shape (2,8), iid N(0,1)*sqrt(2/2), float64;
- later W shape (8,8), iid N(0,1)*sqrt(2/8), float64.

Reference is exact piecewise angular integration with analytic Rayleigh radial moments:
- E[R]=sqrt(pi/2);
- E[R^2]=2;
- recursively split angular intervals at exact preactivation zeros;
- on each fixed-mask interval all activations are exactly a*cos(theta)+b*sin(theta);
- integrate first and second moments analytically;
- no Monte Carlo and no numerical quadrature.

For E113 candidate evaluation, exact previous-layer angular cells are used only as the truth engine to aggregate the four top-2 gate groups exactly. The production estimator is defined by the same four groups estimated from the already-existing E104 trajectories and does not require explicit full-region enumeration.

## Decisive gates

Raw target: 1.89e-8.

PASS requires:
1. all exact/candidate values finite;
2. deterministic replay max_abs == 0;
3. layer-1 bias MSE <=1.89e-8;
4. every later-layer candidate mean-bias MSE <=1.89e-8;
5. final-layer mean-bias MSE <=1.89e-8;
6. conservative production all-in utilization <=0.13.

Variance-bias MSE/max_abs are recorded but are non-decisive.

Any bias gate failure => TERMINAL E113 BIAS NO-GO. No changing gate count, selected gates, seed, width/depth, threshold, precision, conditioning rule, rescue or rerun.

## Production cost extrapolation

Inherit measured E104 base:
- 149114620592 FLOPs;
- width 1024, depth 16, N=4096;
- Gaussian/chi-square RNG, QR/sign/radial helpers, all forwards/ReLUs/reductions already billed.

E113 production successor would apply the conditional rule on exactly the last 4 layers and reuse existing trajectories:
- no fresh RNG;
- no extra dense forward trajectories;
- gate signs are available from previous ReLU activations;
- current z is available immediately after the already-billed matmul.

Conservative arithmetic envelope per late layer:
- top-2 gate scan: <=6*n^2 scalar FLOPs;
- main + two independent-block group code/count/sum/sumsq accumulation: <=32*N*n scalar FLOPs;
- three sets of four-group Gaussian-ReLU formula evaluations are measured with flopscope at production n;
- final disagreement/error reduction <=8*n FLOPs.

Double the complete incremental envelope once more as a safety factor. No credit is taken for any E104 operation that E113 might replace.

GO on cost requires:
E104_measured + safety_factored_E113_increment <= floor(0.13*2^41).

Scientific PASS would only authorize a separate production-shaped protocol, not a benchmark run.
