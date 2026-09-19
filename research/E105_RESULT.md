# E105 terminal result — target-free two-Haar production risk

Idempotency key: `ARC-E105-TWO-HAAR-RISK-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Provenance

- Branch: `research/e105-two-haar-risk-cert-20260919`
- Canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `a4fe51e28ae60d4bc84b7af159d4434c30204589`
- RED test commit: `bff89b811b259c3b0665c3a4a5f7b60132c23a88`
- RED workflow commit: `2d335bb2640c5995f0c826b9f65c08ede61c2b68`
- Frozen implementation commit: `c6145365b7ecedfaef1555bb9da261c518250e79`

## TDD evidence

RED:
- run `35446784621`
- job `105906975299`
- expected `ModuleNotFoundError: No module named 'methods.e105_two_haar_risk'`
- scientific diagnostic step skipped.

GREEN + sole frozen production diagnostic:
- run `35446946998`
- job `105907403331`
- `4 passed in 0.23s`
- workflow/job conclusion: success
- no rerun.

Artifact:
- name: `e105-two-haar-risk`
- ID: `10584569937`
- size: `1363` bytes
- ZIP SHA256: `03c6e16adc09da1ad09db6ea1cec4cfd0ca755a45f8cca567e43405cb58a2698`
- expiry: `2026-12-18T13:50:28Z`

## Frozen production-shape measurement

Shape/law:
- width/depth: `1024 x 16`
- trajectories: `4096`
- exactly two Haar blocks + antipodes
- analytic `E[chi_1024]` radius
- weight seed: `104104`
- direction seed: `104105`
- no public/public-mini/scorer/holdout/full targets.

Measured target-free raw-MSE risk estimator:

`Rhat = mean((B1-B2)^2)/4 = 8.604586912926751e-06`

This is an unbiased estimator of the direction-randomness coordinate MSE of the frozen
two-block E104 estimate for the fixed synthetic production network. It is not a benchmark
target MSE.

Competition raw gate:
- target: `<=1.89e-08`
- observed risk: `8.604586912926751e-06`
- ratio to target: approximately `455.27x`
- gate: **FAIL**

Fully billed compute:
- input construction: `11,541,346,992` FLOPs
- 16 layers: `137,573,171,200` FLOPs
- finalization: `32,768` FLOPs
- total/reconciled: `149,114,550,960` FLOPs
- utilization: `0.06780944702768466`
- exact accounting reconciliation: true
- score multiplier: `0.1`

Adjusted-risk proxy:
- `8.604586912926751e-07`
- gate `<2.5e-09`: **FAIL**

Other gates:
- prediction hash exactly matches frozen E104 production output:
  `ae0bfae00c7379673320a3a098c716272c7d9164588bcc73bd59bc7516c017e0`
- exact antithetic pair max abs: `0.0`
- block re-composition max abs: `0.0`
- prediction repeat max abs: `0.0`
- risk repeat abs: `0.0`
- FLOP ledger repeat exact: true
- finite: true
- first wall: `1.9421148459999813 s`
- second wall: `1.9064790940000194 s`

## Interpretation

E104 production transfer is exact and cheap, but the two-Haar-block stochastic variance is
orders of magnitude too large for the winning raw target. Increasing sample count within
the `util<=0.14` budget cannot close a ~455x variance gap. E104/E105 sampling as-is is
closed as a competition path.

No official scorer, public/public-mini, holdout/full, tuning, sweep, rescue, canonical
mutation, ledger mutation, or merge occurred.
