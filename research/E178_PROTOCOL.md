# E178 OWNER PROTOCOL — H177 higher-order AGO gauge

Date: 2026-09-21

Status: **PROTOCOL FROZEN / ONE TARGET-FREE RUN AUTHORIZED AFTER IMPLEMENTATION FREEZE**

Branch:

`research/e178-h177-higher-order-ago-gauge-20260921`

Protocol ancestry:

- E177 audit commit: `e1536d36a5e2d641ab3596892847e2fcf41e83ab`
- E177 frozen hypothesis: **H177 higher-order AGO gauge**
- E176 is closed terminal NO-GO and is not an implementation/runtime ancestor.
- E164 AGO identity source is conceptual only; no E176 rescue/rerun is permitted.

Pinned public closure source:

- repository: `504aldo/whest-p2-cumulant-k3`
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- V17 blob: `estimators/estimator_v17.py@9c60c5a0bd92729f27bde23eeb619944e71beabe`
- frozen memoryless K4 law: `G_off = lambda_l C_off`
- frozen layer-0 post-ReLU coefficient: `lambda_0 = 1.9516e-3`
- no lambda rescale/refit/adaptation is allowed.

## 1. Single hypothesis

H177 only:

For a zero-bias positively homogeneous ReLU network, write the Gaussian-input
activation vector as

`X_G = S X_A`,  `S = R/sqrt(n)`,

with `R ~ chi_n` independent of the angular activation state.  Raw moments obey

`M_k^G = a_k(n) M_k^A`,

where

`a_k(n) = n^{-k/2} 2^{k/2} Gamma((n+k)/2) / Gamma(n/2)`.

The candidate converts the complete order-1..4 cumulant state through raw
moments into the angular gauge, applies the **unchanged** V17 memoryless closure
`G_off=lambda C_off`, and uses exact radial moments for the inverse gauge.

No rank change, source drop, seed sweep, fixture replacement, lambda refit,
threshold change, output correction, public target, scorer, submission, or
leaderboard operation is part of E178.

## 2. Exact-small algebra gate

One frozen synthetic state dimension: `n=4`.

The implementation must support full dense cumulant tensors through order 4:

- K1: `k1[i]`
- K2: `k2[i,j]`
- K3: `k3[i,j,k]`
- K4: `k4[i,j,k,l]`

Conversion is performed only by the exact moment/cumulant partition identities:

1. cumulants -> raw moments;
2. divide/multiply raw moment order k by `a_k(n)`;
3. raw moments -> cumulants.

Mandatory float64 round-trip gates, both `G -> A -> G` and `A -> G -> A`:

- full K1 relative max error <= `2e-12`;
- full K2 relative max error <= `2e-12`;
- D3 slice `k3[i,i,i]` relative max error <= `2e-12`;
- D21 slice `k3[i,i,j]`, off diagonal, relative max error <= `2e-12`;
- K4 full tensor relative max error <= `2e-12`;
- K4(4), K4(3,1), K4(2,2) slice relative max error <= `2e-12`.

Any failure is terminal.

## 3. Exactly one target-free closure falsifier

Fixture is frozen before execution:

- width/input `n=4`;
- depth `3`;
- zero bias;
- weights: NumPy PCG64 `default_rng(178177)`, iid Normal(0, sqrt(2/n));
- angular support: exactly 24 equally weighted radius-`sqrt(n)` vectors:
  all 16 sign vectors in `{-1,+1}^4`, plus the 8 signed coordinate axes
  `+/-sqrt(n)e_i`;
- evaluate the fixed ReLU network exactly on this finite support;
- closure state is the post-ReLU activation state after layer 2 (zero-index 1).

The finite support is the entire reference distribution; there is no Monte Carlo
target and no sampling error.  Gaussian-gauge raw moments are obtained from the
same angular raw moments using exact radial factors `a_k(4)`.

For a full symmetric fourth cumulant tensor `K4`, define the public r=1
harmonic matrix core by the exact trace projection

`A_ij = sum_k K4[i,j,k,k]`

`G = 6/(n+4) A - 3/((n+2)(n+4)) trace(A) I`.

This is the full-tensor form corresponding to the public AUGMENT projection
coefficients `cA=6/(n+4)`, `cI=-3/((n+2)(n+4))`.

Parent closure error is measured in Gaussian gauge:

`Ghat_G = diag(diag(G_G)) + lambda_0 * offdiag(C_G)`.

H177 closure error is measured after exact higher-order conversion to angular gauge:

`Ghat_A = diag(diag(G_A)) + lambda_0 * offdiag(C_A)`.

The unchanged frozen `lambda_0` is used in both arms.  No fit is allowed.

Metric:

`mse_off = mean((offdiag(Ghat)-offdiag(G_exact))^2)`
over the 12 ordered off-diagonal entries.

Scientific closure GO gate:

`mse_off_H177 <= 0.98 * mse_off_parent`.

This is one falsifier.  Recomputing the same fixture inside the same process for
bitwise replay is a replay check, not a second scientific experiment.

## 4. Replay and immutable evidence

Within the sole Actions run:

1. compute the frozen fixture and both arms;
2. freeze vector/state hashes;
3. recompute the identical fixture;
4. require byte-identical arrays and identical JSON-normalized metrics;
5. write immutable evidence under
   `research/e178_evidence/<GITHUB_RUN_ID>/`:
   - `vectors.npz`;
   - `result.json`;
   - `replay.json`;
   - `manifest.json`;
   - `E178_TERMINAL_RECEIPT.json`.

The manifest must SHA-256 every payload file.  The workflow must upload the same
directory as a GitHub Actions artifact and commit the evidence back to this
branch.  The result commit must not retrigger the run.

## 5. Full production cost gate

Phase-2 budget:

`B = 2^41 = 2,199,023,255,552 FLOPs`.

Required cap:

`floor(0.135 B) = 296,868,139,499 FLOPs`.

The unchanged public V17 K3-simple + memoryless-K4 estimator is already measured
at `C/B = 0.4921` in the pinned public ablation record.  Therefore the frozen
parent lower bound is

`0.4921 B = 1,082,139,344,057.1392 FLOPs`,

before any H177 gauge overlay.  E178 will also report a conservative O(n^2)
one-shot gauge-overlay ledger, but the **full** cost gate is

`public_V17_cost + H177_overlay <= 0.135 B`.

No cost rescue, Strassen substitution, source compression, rank change, final
trim substitution, or parent replacement is authorized under E178.

Consequently, if the public lower bound is confirmed, the production gate is
terminal NO-GO even if the target-free scientific closure gate passes.

## 6. Execution firewall

Forbidden:

- public Mini/full/holdout run;
- WhestBench scorer;
- submission;
- leaderboard mutation;
- rank/seed/fixture sweep;
- lambda fit/rescale/adaptation;
- rerun after scientific failure;
- workflow repair after the armed scientific run;
- canonical baseline or ledger mutation.

The workflow is triggered only by the arm-file path
`research/E178_RUN_ARM.json`.  Protocol, implementation, and workflow commits
must precede the arm commit.

## 7. Terminal decision

Decision precedence:

1. algebra/identity failure -> `TERMINAL_NO_GO_IDENTITY`;
2. deterministic replay/integrity failure -> `TERMINAL_NO_GO_REPLAY`;
3. closure gate failure -> `TERMINAL_NO_GO_CLOSURE`;
4. full cost gate failure -> `TERMINAL_NO_GO_COST`;
5. only if every gate passes -> `GO_TARGET_FREE_H177`.

No E178 result authorizes external submission or a public benchmark run.
