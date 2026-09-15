# E033 result — diagonal four-cumulant Edgeworth carrier

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915`

## Provenance

- Branch: `research/e033-diagonal-edgeworth-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Frozen diagnostic commit: `6a39ef26de1fb91d01cc4add9ed2957d6fc06f43`
- Public Phase-2 mini index: `0` only
- Workflow run: `35002270096`
- Job: `104493295184`

Protocol-first E033 carries only four O(n) vectors `(mu, var, k3, k4)`, uses coordinate-independence cumulant transport, and applies the fixed embedded 16-node standard-normal Gauss-Hermite Edgeworth ReLU update. No covariance/source tensor, rank, fit, damping, clipping, alternate quadrature, or output calibration was used.

## TDD / focused validation

- RED workflow: run `35001970602` on pre-implementation HEAD `66a379cb2e1dd8cce0f7b2e4990b51dae268b8a2` — expected failure before the method existed.
- GREEN workflow: run `35002127638` on implementation HEAD `07ed01e54c9e087773bea392b338f82f18baa023` — success.
- Frozen scientific run focused tests: `4 passed in 1.57s`.

## Frozen local diagnostic

Observed on the single allowed public-mini index-0 diagnostic:

- final-layer MSE: `1.2314415630438802`
- billed FLOPs: `332737028`
- utilization: `0.00015131128202483524`
- adjusted proxy: `0.12314415630438802`
- residual wall: `0.028135634999728154 s`
- wall time: `0.47854621000001885 s`
- max absolute standardized skew: `0.022236497432030298`
- max absolute standardized kurtosis: `0.008953300328354057`
- deterministic repeat max abs difference: `0.0`
- normal-rule max moment error: `4.440892098500626e-16`
- finite: `true`
- frozen scope check: `true`

## Gates

PASS:

- utilization `<=0.14`
- residual `<0.400 s`
- finite state/output
- deterministic repeat
- embedded rule accuracy
- frozen scope

FAIL:

- raw MSE `<=1.89e-08`: observed `1.2314415630438802`
- adjusted proxy `<2.5e-09`: observed `0.12314415630438802`

The raw miss is about `6.52e7` times the target scale. Compute is not the limiting factor; discarding cross-neuron dependence destroys the deep-network mean prediction despite carrying coordinatewise skew and connected kurtosis.

## Decision

**NO-GO / DROP E033.**

No alternate node count, variance floor, clipping, damping, coefficient change, covariance add-back, second mini index, rerun, official scorer, holdout, tuning, sweep, or rescue is allowed under E033. Any method retaining additional dependence is a new E034+ experiment.

Canonical was not changed and no official scorer was launched.
