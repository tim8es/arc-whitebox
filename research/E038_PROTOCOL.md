# E038 protocol — positive-weight Sobol trajectory QMC

Status: **PREREGISTERED / NOT YET RUN**

Idempotency key: `ARC-E038-SOBOL-QMC-20260915`

## Provenance and firewall

- Fresh branch: `research/e038-sobol-trajectory-qmc-20260915`.
- Exact canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Public Phase-2 mini index `0` only for exactly one frozen scientific diagnostic.
- E019–E037 remain immutable. E038 inherits no code, measurements, fitted coefficients, sample points, or state from them.
- No official scorer, holdout/full split, second mini index, sample-count sweep, seed sweep, scramble sweep, tuning, post-hoc calibration, canonical mutation, or ledger mutation is authorized.

## Non-duplication

E029 used a signed, layer-1-exact angular cubature whose 3072 antipodal pairs were fitted to first-layer marginals and then failed catastrophically in the deep network. E038 does not fit moments, does not use signed weights, and does not collapse the distribution after layer 1.

E030–E037 propagated approximate low-dimensional moment/cumulant states. E038 instead propagates complete sample trajectories through every ReLU layer, so all cross-neuron and cross-layer dependencies present on the frozen sample set are retained exactly.

## Hypothesis

A positive-weight low-discrepancy Gaussian quadrature can reach the public-leader accuracy regime more efficiently than cumulant state propagation. For a deterministic ReLU network `f`, estimate every post-ReLU layer mean by equal-weight averaging of a fixed Sobol digital net mapped through the standard-normal inverse CDF.

The direct trajectory representation eliminates closure error. Its only scientific error is deterministic quadrature error.

## Frozen sample rule

- Dimension: exactly `1024`.
- Sample count: exactly `N = 8192 = 2^13`.
- Generator: `scipy.stats.qmc.Sobol(d=1024, scramble=True, seed=38038)`.
- Generate exactly `random_base2(m=13)` once in `setup()`.
- Transform each coordinate by `scipy.special.ndtri` to standard normal.
- Store samples as float32 before `predict()`.
- Equal positive weight `1/8192` for every trajectory.
- No antithetic augmentation, skipping, fast-forward, clipping, endpoint repair, rotation, permutation, resampling, adaptive scramble, or fitted control variate.
- The fixed scramble seed is experiment scope, not the grader seed.

If setup exceeds `4.5 s`, produces any nonfinite value, has shape other than `(8192,1024)`, or is not bit-deterministic on repeat construction, E038 is NO-GO before scientific data.

## Frozen prediction

For each network weight `w` in stored orientation:

`X <- relu(X @ w)`

and emit

`mean_l = mean(X, axis=0)`.

Return the stack of all 16 post-ReLU means. No covariance, K3/K4, source state, fitted correction, output calibration, clipping, sample reweighting, or other estimator term is permitted.

## Cost path

The dominant bill is 16 dense products of `(8192 x 1024) @ (1024 x 1024)`:

`C_dense = 16 * 2 * 8192 * 1024^2 = 274,877,906,944 FLOPs = 0.125 B`.

ReLU and reductions add only lower-order `O(L N n)` work. The preregistered measured utilization gate remains `<=0.14`.

At utilization `0.125`, adjusted `<2.5e-09` requires raw `<2.0e-08`; the frozen raw gate is stricter at `<=1.89e-08`.

## Focused tests before science

Before mini data are read, tests must verify:

1. sample construction has exact `(8192,1024)` shape, float32 storage, finite values, and deterministic repeat equality;
2. sample weights are implicitly equal/positive — prediction uses exactly `mean(axis=0)` and contains no signed/fitted weights;
3. a small synthetic network matches an explicit NumPy trajectory reference exactly/tightly;
4. zero weights emit zero means;
5. output shape is `(depth,width)`;
6. source inspection confirms `N=8192`, Sobol scramble seed `38038`, `random_base2(m=13)`, `ndtri`, and no covariance/K3/K4/source machinery;
7. setup-time preflight is `<=4.5 s` on the diagnostic runner.

Focused tests may iterate before any public-mini access. Once GREEN, exactly one frozen scientific diagnostic is allowed.

## Frozen scientific gates

All must pass:

- final-layer raw MSE `<=1.89e-08`;
- measured utilization `<=0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) <2.5e-09`;
- residual wall time `<0.400 s`;
- total predict wall time `<120 s`;
- setup time `<=4.5 s`;
- failures `=0`;
- finite samples/output;
- deterministic repeated setup samples bit-identical;
- deterministic repeated prediction max abs difference `==0.0`;
- exact frozen scope: dimension 1024, N=8192, scrambled Sobol seed 38038, `m=13`, ndtri, equal positive averaging, no fitted/signed/control-variate correction.

Any failed or unevaluable gate => **NO-GO / DROP E038**. No rescue or rerun under E038. Any different sample count, seed, scramble mode, transform, variance reduction, or hybrid correction requires E039+.

If E038 reaches GO, only an independent review handoff is authorized; no official scorer is launched automatically.