# E151 Protocol — ARSG target-free falsifier

Status: FROZEN / NOT EXECUTED
Date: 2026-09-21
Idempotency key: `ARC-E151-ARSG-FORENSICS-20260921`

## Hypothesis

ARSG = exact angular/radial state gauge plus one exact level of Strassen for
eligible dense matrix products.

The hypothesis is **forensic**: it tests whether this representation/arithmetic
mechanism is capable of explaining a `raw < 2.1e-8`, `cost <= 0.135 B`
frontier without any of the excluded estimator families. It does not assert that
a named leaderboard participant uses ARSG.

## Firewall

The falsifier may use only:
- synthetic zero-bias ReLU MLP weights generated from frozen seeds;
- analytic chi/sphere identities;
- dense matrix arithmetic;
- deterministic exact-2D angular integration generated from the synthetic MLP.

Forbidden:
- public Phase-2 targets, mini labels, scorer, holdout, full suite, submissions;
- any benchmark target or fitted coefficient;
- V29 old-tier code or compression;
- K3 rank/basis/TT/response projection;
- CountSketch;
- MUB/Kerdock/spherical-design sampling;
- sampling control variates;
- rank/seed/threshold sweeps or post-result rescue.

## Frozen fixtures

1. `exact2d_depth8`: input dimension 2, hidden/output width 8, depth 8,
   seed `151002`. Exact expectation is obtained by activation-sector
   enumeration on the circle and analytic integration of each linear sector.
2. `dense32_depth8`: square width 32, depth 8, seed `151032`.
   Used only for samplewise homogeneity and arithmetic identities; no target MSE.
3. `adversarial16_depth8`: square width 16, depth 8, seed `151016`,
   deterministic orthogonal mixing with alternating singular values.
   Used only for samplewise homogeneity and arithmetic identities; no target MSE.

No fixture or seed replacement is allowed after execution.

## Identities to verify

For every synthetic network and every frozen probe `x != 0`, with
`Y=sqrt(n)x/||x||` and `R=||x||`:

```
f(x) = (R/sqrt(n)) f(Y).
```

For the angular input:

```
a1(n) = exp(0.5 log 2 + lgamma((n+1)/2) - lgamma(n/2) - 0.5 log n)
Cum4(Y_i,Y_i,Y_i,Y_i) = -6/(n+2).
```

For every frozen matrix pair:

```
Strassen1(A,B) == A @ B
```

up to the float64 numerical gate below.

## Exact-2D reference

The 2D zero-bias ReLU network is piecewise linear on the unit circle.
For every angular sector with fixed ReLU masks,

```
h(theta) = A [cos(theta), sin(theta)]^T.
```

All preactivation zero crossings are inserted as sector boundaries layer by
layer. The final uniform-circle mean is integrated analytically using

```
int_a^b cos(theta) dtheta = sin(b)-sin(a)
int_a^b sin(theta) dtheta = cos(a)-cos(b).
```

The Gaussian mean then equals `E[chi_2]` times the unit-circle mean.
This reference is constructed from the synthetic weights only.

## Falsifier gates

All gates are mandatory:

1. source firewall: PASS;
2. exact-2D sector reference deterministic replay: bitwise PASS;
3. samplewise homogeneity max relative error `<= 2e-12`;
4. angular fourth-cumulant scalar identity absolute error `<= 2e-15`;
5. one-level Strassen relative Frobenius error `<= 2e-12` on all frozen
   square and rectangular products;
6. one-level `1024^3` analytic FLOP ratio exactly
   `0.877197265625` under the frozen 2-FLOP multiply-add convention;
7. open-source Phase-2 total-cost ratio reproduced from immutable reported
   numbers:
   `0.695774 / 0.786835 = 0.8842692559431139`;
8. frontier transfer arithmetic:
   `0.1478860181 * ratio <= 0.135` and
   `0.1504215170 * ratio <= 0.135`;
9. exact Strassen-only eligible-work thresholds:
   required eligible fraction `<= 0.71` for the first frontier row and
   `<= 0.835` for the second;
10. no public target/scorer/holdout/full access.

The exact-2D reference is an identity guard, not a promotion target. E151 does
not claim an exact-small raw-MSE gain until a separate frozen closure-specific
candidate exists.

## Decision rule

- If any identity/cost gate fails: `E151_TERMINAL_NO_GO_ARSG`.
- If all gates pass: `E151_HYPOTHESIS_ADMISSIBLE_NOT_VALIDATED_ON_TARGETS`.

A PASS authorizes only a future protocol-first estimator lane. It does not
authorize a public run, a benchmark target run, or a claim that ARSG is the
leader mechanism.

## Execution rule

This commit freezes the falsifier but **does not execute it**. Any future E151
execution must be exactly one synthetic run of the frozen script, with no
sweep/rescue/rerun. Public targets remain forbidden.
