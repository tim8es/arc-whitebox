# E118 protocol — independent activation-boundary-flux deployability audit

Idempotency key: ARC-E118-BOUNDARY-FLUX-DEPLOYABILITY-AUDIT-20260919

Status: PREREGISTERED / REVIEW-ONLY / NO PRODUCTION AUTHORIZATION.

## Provenance

- Review branch: review/e118-boundary-flux-deployability-audit-20260919.
- Parent: sealed E114 activation-boundary-flux head b9f64030f65da9b32fc7718d04fb108ee1a73dab.
- Owner branch: research/e114-activation-boundary-flux-20260919.
- Owner production_go=false is preserved unless both E118 gates pass.
- No public/public-mini, scorer, benchmark targets, holdout/full, tuning, rescue, production execution, canonical mutation, or ledger mutation.

## Audit question

Does the E114 repository implementation constitute a deployable weight-driven mechanism, or only an oracle-coded proof fixture?

E118 separates:

A. exact small-width mathematical correctness;
B. production deployability, including remainder certification and all-in cost.

Production may be authorized only if BOTH pass.

## Gate A — independent exact small-width correctness

Do not use E114's hard-coded kink angles or piecewise coefficients as the truth engine.

From the frozen owner weights only:

    W1 = [[1,0],[0,1]]
    W2 = [[1,1],[-2,0]]
    W3 = [[2],[-1]]

construct the complete unit-circle activation partition generically:

1. begin with the full angular interval and identity input coefficient matrix;
2. on each current sector, propagate affine/homogeneous coefficient matrices from weights;
3. solve all preactivation zeros a*cos(theta)+b*sin(theta)=0 inside that sector;
4. split exactly at those zeros;
5. propagate masks and final scalar linear coefficients;
6. analytically integrate every final sector;
7. independently form derivative jumps from adjacent final sector coefficients and sum them;
8. convert the angular integral/flux to the N(0,I_2) Gaussian mean.

PASS requires:
- finite=true;
- sector integral vs flux sum abs error <=1e-12;
- generic reference mean vs owner closed-form mean abs error <=1e-12;
- deterministic repeat max_abs=0.

This gate verifies the identity, not deployability.

## Gate B — deployability / oracle-free / remainder / all-in cost

A deployable E114 mechanism must accept weights/network state and itself construct or approximate the output-relevant boundary flux.

The owner executable fails the oracle-free criterion if any of the following are true:
- downstream kink angle is hard-coded analytically;
- final region coefficients are hard-coded rather than derived from weights;
- boundary list is hard-coded;
- there is no generic weight-driven boundary enumerator/compressor;
- no flopscope BudgetContext covers boundary construction/integration/certificate work.

For an approximate production representation, define omitted signed flux for output coordinate j:

    R_flux,j = sum_{Gamma omitted} integral_Gamma J_Gamma.

The induced deterministic mean error is exactly

    e_j = E[R] / (|S^{d-1}| (d-1)) * R_flux,j.

A production approximation must provide a computable certificate on the omitted signed flux such that the final mean-error vector satisfies

    (1/n) sum_j e_j^2 <= 1.89e-8.

A sufficient uniform per-coordinate bound is

    |e_j| <= sqrt(1.89e-8) = 1.374772708486752e-4.

At n=1024 an equivalent vector sufficient bound is

    ||e||_2 <= sqrt(1024*1.89e-8) = 0.004399272667157606.

Absence of a computable omitted-flux/remainder certificate is a Gate-B failure.

## All-in FLOP accounting

Competition production budget for this audit:

    B = 2^41
    utilization cap = 0.13
    F_max = floor(0.13 B) = 285873023221.

If layered on the authoritative accounting-complete E104 base:

    F_base = 149114620592,
    incremental headroom = 136758402629.

The boundary-flux production bill must include ALL of:
- boundary/state discovery or compression;
- geometric/root/interface construction;
- derivative-jump or flux evaluation;
- boundary integration/sampling;
- RNG if any;
- helper/materialization operations;
- omitted-flux/remainder certificate;
- error-estimator/certificate reductions;
- fallback path if required.

Core-only, oracle-supplied-boundary, or uninstrumented standard-library fixture cost is not admissible.

Gate B PASS requires:
1. generic weight-driven mechanism present;
2. no oracle-supplied boundary constants;
3. computable remainder certificate meeting the 1.89e-8 requirement;
4. physically billed all-in production-shaped or rigorously bounded cost <=285873023221 standalone and <=136758402629 incremental if layered on E104;
5. helper and certificate costs explicitly included.

If any item is absent, production authorization = false.

## Decision rule

- Gate A FAIL => E118 verifier failure; do not interpret deployability.
- Gate A PASS and Gate B FAIL => DEPLOYABILITY NO-GO / ORACLE FIXTURE ONLY; E114 identity remains mathematically valid but no production authorization.
- Gate A PASS and Gate B PASS => only then may E118 record production-admission PASS. No actual production run is authorized by this audit alone.
