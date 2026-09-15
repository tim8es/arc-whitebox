# E039 result — two-component half-space Gaussian location mixture

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-E039-OWNER-20260915`

## Provenance

- Branch: `research/e039-halfspace-gaussian-mixture-20260915`
- Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `15653d3d4a58cb8b29a5b3325c2b24995529141f`
- RED tests commit: `dd391ba843c2f9f71b73a1f8cbc15862b44064cf`
- RED workflow head: `1cf2f715cdcb2b050663ec98e5b1ec108e743979`
- Frozen implementation commit: `816078fda3d6092cf162c7ebc733fc27f595918a`
- Frozen diagnostic harness commit: `5ab9d55a8df7c001f5ead634c2371d4d86d4a7d1`
- Frozen diagnostic arm commit: `5b789a6ec56d35e68393adb727474a40e1e39fcf`
- Public Phase-2 mini index: `0` only

No scorer, holdout/full split, tuning, sweep, canonical mutation, or ledger mutation was used.

## TDD evidence

RED:
- run `35012546874`
- job `104527825633`
- expected failure: `ModuleNotFoundError: No module named 'methods.e039_halfspace_gaussian_mixture'`
- no public-mini data accessed.

GREEN:
- run `35012681427`
- job `104528280429`
- focused suite: success.

The harness-only commit produced tests-only run `35012795165`; that run used the old workflow snapshot and did **not** contain a scientific diagnostic. It is not a second scientific run.

## Single frozen diagnostic

- run `35012834692`
- job `104528786158`
- scientific head `5b789a6ec56d35e68393adb727474a40e1e39fcf`
- focused tests immediately before science: `5 passed in 1.68s`
- artifact `10414172282` (`e039-frozen-result`)
- artifact ZIP SHA256 `decd5326a4ca5b429a3524fab0d7ba932e80b17a11aedf959b360168bccd1b1c`

Observed metrics:
- final-layer raw MSE: `4.502602651621096e-06`
- billed FLOPs: `137956982784`
- utilization: `0.06273557245731354`
- adjusted proxy: `4.502602651621096e-07`
- failures: `0`
- residual wall time: `0.02845103200067456 s`
- wall time: `2.7975508709999986 s`
- initialization weighted-mean error: `0.0`
- initialization covariance reconstruction error: `0.0`
- covariance diagonal max abs error: `1.3877787807814457e-17`
- deterministic repeat max abs difference: `7.993605777301127e-15`
- finite: `true`
- scope: pass.

PASS:
- utilization `<=0.14`
- failures `=0`
- residual `<0.400s`
- finite
- initialization mean/covariance gates
- covariance diagonal identity
- exact two components and 0.5/0.5 weights
- scope.

FAIL:
- raw MSE `<=1.89e-08`: observed `4.502602651621096e-06`
- adjusted `<2.5e-09`: observed `4.502602651621096e-07`
- deterministic repeat diff `==0.0`: observed `7.993605777301127e-15`.

## Decision

**NO-GO / DROP E039.**

The frozen two-component half-space location mixture is cheap and numerically stable but far outside the target accuracy regime and also misses exact bitwise determinism. No alternate split direction, weights, extra components, per-component covariance persistence, damping, K3/K4 add-back, rerun, second index, scorer, holdout, tuning, or sweep is permitted under E039.
