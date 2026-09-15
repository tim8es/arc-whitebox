# E047 Result — terminal NO-GO / DROP

Method: output-contracted connected-diagram dynamic programming for finite-width ReLU cumulants, KMAX=6, float64, fixed 32 Walsh probes, no full O(width^k) tensors for k>=3.

## Provenance

- canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- branch: `research/e047-connected-diagram-dp-20260916`
- protocol-only commit: `e2ed778c1eb9aef7bd742e5654f4e3bcb4a8ae2c`
- RED tests pre-workflow commits: `136ec9ac969e68da0e2f5f3ce3ce640e0053e2d5`, `30620f78c4a8e75f8234504d6bf4ca5048d7753e`
- focused workflow commit: `8f3f7dd3d31b88c0b5cd17a433e03ef631eeb418`
- implementation commit: `f7a4d67541e82a1906f679b9f59b27c15c0d5700`
- diagnostic script commit: `562ea41c4450633f74bb0472f2405c800710ebf8`
- one-shot diagnostic workflow commit: `808aa2973dff389690099c50dfe5be21875ffbda`

## RED

Run `35034778727`, job `104601294046`.
Expected failure only: `ModuleNotFoundError: No module named 'methods.e047_connected_diagram_dp'` during collection, exit code 2. No public data access.

## Synthetic GREEN

Run `35034893661`, job `104601660848`.
Focused explicit-vs-contracted deterministic falsifier: `6 passed in 1.33s`.

## Frozen public mini0 diagnostic

Exactly one public diagnostic workflow run:

- run: `35034982227`
- job: `104601951034`
- dataset: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- split/index: `mini[0]`
- budget: `2**41`
- artifact: `e047-public-mini0-log`
- artifact id: `10422602514`
- artifact zip SHA256: `85915e3a95cdaffe025cbe2eddcefab8da42394165f49ffed595d47af455c502`

Observed metrics:

- raw final-layer MSE: `4.608246562294362e-06` — FAIL vs `1.89e-08`
- adjusted proxy: `4.608246562294362e-07` — FAIL vs `<2.5e-09`
- FLOPs used: `107757668318`
- utilization: `0.049002514205312764` — PASS vs `<=0.125`
- core projected utilization: `0.049002514205312764` — PASS vs `<=0.100`
- failures: `0` — PASS
- residual wall time: `0.08371960699955139 s` — PASS vs `<0.400 s`
- finite: `true` — PASS
- deterministic repeat max abs diff: `0.0` — PASS
- representation_ok: `true`
- state_rank_max: `1`
- KMAX: `6`
- probe_count: `32`
- dtype: `float64`
- max_abs_connected: `5.733754696087886`
- local_go: `false`

## Terminal verdict

`NO-GO / DROP` by the preregistered one-shot kill rule. Accuracy gates fail by large margins despite bounded FLOPs, finite deterministic output, and representation/cost gates passing.

No rerun, rescue, pruning, rank/topology adaptation, tuning, sweep, holdout, full split, official scorer, canonical mutation, ledger mutation, or merge was performed.