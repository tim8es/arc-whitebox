# E036 result — centered output-Hessian diagonal heat-kernel estimator

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-E036-IMPLEMENT-20260915`

## Provenance

- Branch: `research/e036-output-hessian-diagonal-20260915`
- Direct-parent canonical: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only root: `83f8c4b3cefe985cc79b6bf61392098ea210911b`
- Protocol gate/probe amendment: `56b33744aeb63e5f9968d260867f27fe1d9e51b2`
- Protocol arithmetic correction: `4c1c2a3c7d377518f142ada43d35e9bd4ee2111b`
- RED tests/workflow head: `5d35f4f3cc5c98bc72e29913a0e9b21b02458e15`
- Implementation commit: `bac2309bb174481e5b9cb34a024298dfe2ed8246`
- Frozen harness commit: `7c5814e5c11fbc25e966d4695d59a5876a4d5f14`
- Frozen measurement arm commit: `4a4a37709f47778be77bace206607a3363ab791c`
- Public Phase-2 mini index: `0` only.

No scorer, holdout/full split, tuning, sweep, canonical mutation, or ledger mutation was used.

## Protocol audit

Before implementation the raw gate was strengthened from `2.45e-08` to `1.89e-08`, with mandatory adjusted `<2.5e-09`, utilization `<=0.105`, failures `=0`, residual `<0.400 s`, finite output, and exact determinism. The frozen probe set was fully specified as all 1024 rows of the unpermuted Sylvester-Hadamard matrix with `h=1.0` and correction coefficient `0.5`.

The corrected static dense-forward envelope was `68,753,031,168` FLOPs, exactly `0.0312652587890625 B` for `B=2^41`.

## Focused TDD

RED:

- run `35009481236`
- job `104517539132`
- expected failure: `ModuleNotFoundError: No module named 'methods.e036_output_hessian_diagonal'`
- no public-mini data accessed.

GREEN:

- run `35009581059`
- job `104517881892`
- `4 passed in 1.46s`.

The frozen scientific run reran the same focused suite and obtained `4 passed in 1.33s` before the diagnostic.

## Authoritative single frozen diagnostic

The authoritative frozen run is the first arm-created scientific run only:

- run `35009736536`
- job `104518410100`
- frozen measurement commit `4a4a37709f47778be77bace206607a3363ab791c`

Observed metrics on public mini index 0:

- final-layer MSE: `1.2310937871082808`
- billed FLOPs: `137652996092`
- utilization: `0.0625973353144218`
- adjusted proxy: `0.12310937871082808`
- residual wall time: `0.0049460790000068755 s`
- total wall time: `1.3299151989999984 s`
- max absolute correction: `4.892882024738672`
- max absolute output difference versus deterministic zero baseline: `4.892882024738672`
- deterministic repeat max absolute difference: `0.0`
- failures: `0`
- finite: `true`
- exact `h=1.0`: pass
- exact 1024-probe count: pass
- exact Hadamard orthogonality: pass
- frozen scope check: pass.

The measured FLOP count is roughly twice the simple dense-envelope estimate but remains well inside the preregistered utilization gate.

## Gates

PASS:

- utilization `0.0625973353144218 <= 0.105`
- failures `=0`
- residual `0.0049460790000068755 < 0.400 s`
- finite output
- deterministic repeat `=0.0`
- exact `h`, probe count, Hadamard frame, and frozen scope.

FAIL:

- raw MSE `<=1.89e-08`: observed `1.2310937871082808`
- adjusted proxy `<2.5e-09`: observed `0.12310937871082808`.

The failure is scientific, not computational: the complete orthogonal Rademacher frame is cheap and deterministic, but the centered second-order heat-kernel approximation around the ReLU kink produces O(1) error. The correction amplitude reaches `4.89`, so this representation is not a near-frontier perturbation.

## Concurrency exclusion

After the measurement arm commit, a concurrent test-only preflight commit (`eac68f431af1f683ce8ab6ad32a1b8ba93bfba42`) landed while the workflow was already armed. GitHub therefore started run `35009763182` / job `104518501488`, whose workflow snapshot also contained the scientific step. This is an **accidental duplicate**, not an authorized rerun. It is excluded permanently from scientific evidence and no metrics from it may be used, compared, selected, or interpreted. The authoritative result remains run `35009736536` only.

## Decision

**NO-GO / DROP E036.**

No alternate radial scaling, `h`, probe count, row/sign permutation, coefficient, baseline, stencil, K3/K4/covariance add-back, second index, rerun, scorer, holdout, tuning, or rescue is permitted under E036. Any successor must use a fresh experiment ID and fresh protocol from canonical.
