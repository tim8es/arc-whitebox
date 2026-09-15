# E036 — output-Hessian diagonal heat-kernel estimator

Idempotency key: `ARC-ACTION-E036-20260915`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e036-output-hessian-diagonal-20260915`
- Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- This lane is re-keyed from the previously empty/conflicting E031 reservation only; it inherits no commits, code, measurements, or state from E031, E032, E033, E034, or E035.
- E035 remains independently active and must not be modified, duplicated, or interpreted through E036.
- Public Phase-2 mini index **0 only** is permitted for the single local scientific diagnostic.
- No official scorer, holdout/full split, second mini index, parameter tuning, sweep, adaptive search, canonical mutation, or ledger mutation is authorized under E036.

## Hypothesis

The final prediction error may be dominated by a small second-order curvature correction to the deterministic mean trajectory that is not efficiently represented by persistent K3/K4 or source-stack state. E036 tests whether a frozen diagonal approximation to the Gaussian-smoothed output Hessian can recover that correction at low billed cost.

For a deterministic network map `f(x)` evaluated around the canonical Gaussian mean trajectory, use the second-order heat-kernel approximation

`E[f(X)] ~= f(mu) + 0.5 * sum_i Var[X_i] * d2 f / dx_i^2`,

with the Hessian diagonal estimated by centered finite differences along a fixed, preregistered deterministic coordinate/sign probe set.

This is an output-curvature estimator only. It carries no persistent covariance/K3/K4/source representation between layers and is not a rescue of E029–E035.

## Frozen mechanism

1. Use the canonical public-mini index-0 input statistics and canonical estimator provenance.
2. Evaluate the baseline deterministic mean-path output `f(mu)`.
3. Freeze a centered finite-difference scale `h = 1.0` in standardized input coordinates.
4. Freeze a deterministic probe set before any scientific measurement. The implementation must define this set in code/tests without using mini-data outcomes, scorer feedback, or parameter search.
5. For each frozen signed probe direction `v`, estimate the directional second derivative with

   `D2_v f = (f(mu + h v) - 2 f(mu) + f(mu - h v)) / h^2`.

6. Combine the fixed directional estimates into a diagonal-Hessian trace proxy using only preregistered deterministic weights and the known input diagonal variance.
7. Add exactly one second-order correction to the baseline output. No fitted coefficient, damping, clipping, learned calibration, adaptive step size, probe reselection, higher-order correction, K3/K4 term, covariance carrier, D21/source-stack term, or post-hoc sign choice is permitted.

## Structural preflight

Before any public-mini scientific diagnostic, focused tests must establish:

1. centered finite differences are exact on synthetic quadratic functions to numerical tolerance;
2. constant and affine functions produce zero second-order correction;
3. frozen probe generation is deterministic and independent of mini outputs;
4. probe normalization/sign conventions are exact and repeatable;
5. the implementation applies exactly one second-order output correction and no hidden fitted scalar;
6. all evaluated outputs are finite;
7. the estimated billed utilization path is `<= 0.105` before the scientific run. If this cost preflight is not satisfied, E036 is terminal NO-GO without a mini diagnostic.

## Single frozen public diagnostic

If and only if structural preflight and focused GREEN tests pass, run exactly one local scientific diagnostic on public Phase-2 mini index `0` under the normal billed FLOP accounting. One identical unmetered repeat is allowed solely to verify determinism.

Record exactly:

- raw final-layer MSE;
- billed FLOPs;
- utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- residual wall time and total wall time;
- maximum absolute output difference versus the baseline candidate;
- deterministic repeat maximum absolute difference;
- finite-status check;
- exact frozen-probe/scale/scope checks.

## Quantitative GO gates

All gates are mandatory:

- raw final-layer MSE `<= 2.45e-08`;
- adjusted proxy `< 2.5e-09`;
- measured utilization `<= 0.105`;
- residual wall time `< 0.400 s`;
- all outputs and intermediate correction values finite;
- deterministic repeat maximum absolute difference `== 0`;
- frozen scale exactly `h = 1.0`;
- exact frozen probe set and correction scope unchanged from preregistration;
- no scorer/holdout/tuning/sweep/second-index access.

A GO requires every gate to pass. Passing only compute or only accuracy is insufficient.

## Kill rule

Any failed or unevaluable structural preflight or quantitative gate is **NO-GO / DROP E036**.

After a terminal NO-GO there is no rescue under E036: no alternate `h`, more/fewer probes, different probe geometry, learned/fitted scalar, clipping, damping, covariance/K3/K4 add-back, alternate finite-difference stencil, second mini index, rerun, scorer, holdout, or tuning. Any materially different mechanism requires a fresh experiment ID from the then-current canonical.

If E036 reaches GO, the only next step is review handoff and at most one scorer handoff; no automatic scorer execution or canonical merge is authorized.