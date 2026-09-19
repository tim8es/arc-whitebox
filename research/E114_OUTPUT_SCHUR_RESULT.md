# E114 output-specific Schur final-mean compression — terminal NO-GO

Idempotency key: `ARC-E114-OUTPUT-SCHUR-FINALMEAN-20260919`

Decision: **TERMINAL NO-GO / DROP OUTPUT-SCHUR VARIANT**

## Identity firewall

This result belongs only to:

`research/e114-output-schur-finalmean-20260919`

It is a collision-isolated successor of the already-verified activation-boundary-flux E114 branch and does not overwrite that positive closure.

Parent E114 activation-flux head:

`b9f64030f65da9b32fc7718d04fb108ee1a73dab`

This variant is explicitly not:

- E112 factorized cumulants;
- E112 full-mask/treewidth message passing;
- E113 top-k/top-gate conditioning;
- E110 deep-line Rao-Blackwellization;
- E111 Gaussian-ReLU plug-in;
- a sampler/control-variate lane.

## Mechanism

For penultimate preactivation `z` and final output

`y = ReLU(W_4 ReLU(z))`,

the variant compresses only the dependence needed for the final mean vector.

Let

`M = E[z z^T]`.

For rank-r observations `U^T z`, the minimum-second-moment linear reconstruction has Schur residual

`M_res = M - M U (U^T M U)^+ U^T M`.

For final row `w_j`, ReLU 1-Lipschitz plus weighted Cauchy-Schwarz gives

`|E[y_j]-E[yhat_j]|^2 <= ||w_j||_1 tr(D_j M_res)`

with `D_j=diag(|w_j|)`.

Pooling final coordinates produces

`pooled final-mean bias MSE <= tr(D_pool M_res)`.

The frozen rank-r basis is the optimal one for this bound: the top-r eigenspace of

`B = M^(1/2) D_pool M^(1/2)`.

Thus the exact certificate equals the omitted weighted spectrum.

## Protocol / implementation provenance

- protocol-first commit:
  `3926781c8109d6329aac064e453ecbc4a2d7986b`
- implementation commit:
  `557afab80a82a564fc1528c418c45e061c78e491`
- exact algebra tests commit:
  `19f4a2b79fd512526bb4e4893fb1f1237a94c786`
- frozen falsifier commit:
  `1a84f597dd9a583ee6dc8ec3662522ebedc96fb6`
- sole scientific arm:
  `08d5a5e2a6d5f8f03d3881e0c6c4f002734ad4de`

## Exact small-width gate

Frozen:

- Gaussian input dimension: 2
- width: 8
- depth: 4
- rank: 2
- zero bias
- seeds: `114201,114202,114203,114204`
- exact analytic angular sector integration
- no Monte Carlo truth
- no numerical quadrature

Workflow:

- run: `35456264281`
- job: `105931961172`
- exact algebra tests: success
- scientific falsifier step: success
- terminal workflow conclusion: failure only because the frozen result exit code was `2`
- rerun: none

Artifact:

- name: `e114-output-schur`
- ID: `10587988095`
- GitHub ZIP SHA256:
  `bfe043ca060c73698dd370c8b3b17c346630f75e953f5d3ff629402ed847fd65`
- independently downloaded ZIP SHA256: identical
- extracted JSON SHA256:
  `de0b0684192913c0da7dd382a7c6c72c0603c3b34da5e497086c8f0d6bab833e`
- artifact size: `7819` bytes
- deterministic replay max abs: `0.0`

## Exact measurements

Competition target scale:

`T = 1.89e-8`.

Per seed:

| seed | exact Schur remainder bound | bound / target | exact proxy bias MSE | actual / target |
|---|---:|---:|---:|---:|
| 114201 | 0.8985395646910943 | 47,541,775.91x | 0.0005896295050116321 | 31,197.33x |
| 114202 | 1.071166459149392 | 56,675,474.03x | 0.005552944247388847 | 293,806.57x |
| 114203 | 0.9031161443928742 | 47,783,922.98x | 0.0036427976667961093 | 192,740.62x |
| 114204 | 0.19689557900128055 | 10,417,755.50x | 0.001107923832193606 | 58,620.31x |

Aggregate:

- pooled Schur remainder bound:
  `0.7674294368086603`
- pooled bound / target:
  **`40,604,732.11x`**
- max-seed bound:
  `1.071166459149392`
- pooled exact proxy bias MSE:
  `0.0027233238128475485`
- pooled actual / target:
  **`144,091.21x`**
- max exact proxy bias MSE:
  `0.005552944247388847`

For every seed the actual exact bias satisfied the preregistered certificate:

`actual_bias_mse <= Schur_remainder_bound + 1e-12`.

The Schur remainder matrices were PSD within frozen numerical tolerance, and the trace certificate matched the omitted weighted eigenvalue sum to approximately `4e-14` or better.

## Production cost admission

Pre-code production upper remained feasible:

- inherited complete base: `149,114,620,592` FLOPs
- frozen all-in upper: `184,614,620,592` FLOPs
- budget: `2^41`
- utilization upper:
  `0.08395300964912167`
- cap: `0.13`
- cost admission: **PASS**

No production execution was performed.

## Scientific interpretation

The failure is decisive before production.

The requested output-specific rank-2 Schur compression does identify a mathematically valid low-dimensional dependence and its explicit remainder bound is correct. However, the residual dependence left after optimal rank-2 compression is many orders of magnitude too large.

This is not merely a loose-bound artifact: the exact angular proxy itself has pooled final-mean bias MSE about `1.44e5` times the target. The rigorous remainder certificate is even larger, about `4.06e7` times target.

Therefore this mechanism has no target-scale path under the frozen rank/compression definition.

## Verdict

**TERMINAL NO-GO / DROP E114 OUTPUT-SCHUR VARIANT.**

Per protocol there is no rank change, seed change, different compression point, alternate weighting, pseudoinverse threshold change, rescue, sweep, rerun, or production prototype.

The original activation-boundary-flux E114 positive closure remains separately valid; this result only closes the output-specific low-rank/Schur-complement compression variant.

No public/public-mini, scorer, holdout/full, benchmark target, tuning, production run, canonical mutation, ledger mutation, or merge occurred.
