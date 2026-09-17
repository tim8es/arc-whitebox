# E100 result — local Stage-A GO, scientific GO not granted

Idempotency key: `ARC-E100-ORTHOGONAL-GAUSSIAN-ANTITHETIC-20260918`

Branch: `research/e100-orthogonal-gaussian-antithetic-20260918`

Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Protocol commit: `e94a485b80a3e89bcb564dd43106727bea77450f`

Implementation commit: `4f28d642eb3db9197c9e48a87279ed126fbeadda`

Frozen arm commit: `c03b268bc57da4a353760412fc8ca46eed12cb4d`

## Sole frozen Stage-A evidence

- run: `35286592051`
- job: `105420177508`
- conclusion: `success`
- artifact: `e100-stage-a`
- artifact ID: `10525165155`
- artifact ZIP SHA256: `33388d2725f15af959039110995815dca52edf4f02c76060266b9cbcaf9aa8a6`
- artifact size: `1431` bytes
- no benchmark/public/scorer/holdout/full data and no target fitting.

Frozen synthetic design:

- width/depth: `32/6`
- network seeds: `100000..100007`
- high-sample iid-antithetic reference: `65536` trajectories
- candidate and comparator: `2048` trajectories each
- orthogonal candidate: Haar-QR directions with independent chi radii plus exact antithetic partners
- comparator: ordinary iid-antithetic Gaussian pairs.

## Metrics

Pooled final-layer coordinate mean error:

- iid-antithetic MSE: `1.1734719982468077e-04`
- Haar-orthogonal antithetic MSE: `2.209970715494368e-05`
- orthogonal / iid ratio: `0.1883275202813626`
- relative MSE reduction: about `81.17%`

Robustness:

- orthogonal wins: `8/8`
- worst per-network orthogonal / iid ratio: `0.4780911047150302`
- deterministic replay max abs scalar delta: `0.0`
- all outputs finite: true.

Per-network orthogonal / iid ratios:

- 100000: `0.2807247744610772`
- 100001: `0.3134002944889802`
- 100002: `0.06326111949887449`
- 100003: `0.4780911047150302`
- 100004: `0.20225087402924177`
- 100005: `0.22541049258640136`
- 100006: `0.18737356352825277`
- 100007: `0.15319442358071586`

Conservative production cost ceiling at width=1024, depth=16, N=4096:

- dense forward FLOPs: `137438953472`
- two square QR blocks: `2863311531`
- radial scaling + reduction: `16777216`
- total: `140319042219`
- utilization vs `2^41`: `0.06380971272801617`

All preregistered Stage-A gates pass.

## Decision

**E100 = LOCAL STAGE-A GO only.**

This is strong synthetic evidence for cross-trajectory Haar orthogonalization as an unbiased variance-reduction mechanism. It is not a competition-level accuracy result and does not establish raw final-layer MSE <=1.89e-8 on ARC production/public distribution.

`scientific_go = false`.

Per project firewall, the next action is independent review of the marginal-law proof, cost accounting, QR sign convention, reference independence, and the claim that the observed gain is not a hidden distribution change. No public/public-mini, scorer, holdout/full, tuning, sample-count sweep, alternate block construction, merge, canonical mutation, or ledger mutation is authorized from this receipt.
