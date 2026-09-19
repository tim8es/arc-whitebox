# E108 terminal result — exact-mean first-layer transported control variate

Idempotency key: `ARC-E108-FIRSTLAYER-EXACTMEAN-TRANSPORT-CV-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Repository instruction check

The requested `AGENTS.md` is absent from the complete recursive repository tree at the executed head (tree `4d03dc0f37a039cee2854faebf252729de294ac3`, GitHub response `truncated=false`, zero matching paths). The local runtime also had no checkout and direct clone was blocked by DNS resolution of github.com, so repository work was performed through the connected GitHub API. Existing frozen ARC protocols/results were used as the operative process convention.

## Admission first

The frozen pre-code admission estimate was `184,474,289,328` FLOPs, utilization `0.0838891944 <= 0.13`, so implementation was authorized.

Measured complete billing was `187,819,635,376` FLOPs, utilization `0.0854104816`. The pre-code estimate was therefore low by `3,345,346,048` FLOPs (1.8134%), despite being described as conservative. The hard admission conclusion remains valid: measured headroom to `0.13 * 2^41` is about `98.05B` FLOPs.

## Mechanism

E108 uses the exact first-layer spherical/analytic-radius mean

`mu1_j = ||row_j(W1)|| / sqrt(2*pi)`

and the fixed downstream mean-field transport

`T = (0.5 W2.T)(0.5 W3.T)...(0.5 W16.T)`.

For each Haar direction/antipode pair, `(a-mu1) @ T` is an exact-zero-mean target-free control. One scalar coefficient per final output coordinate is fit on the opposite independent Haar block and cross-applied symmetrically. No ridge, clipping, fitted benchmark targets, tuning, rank/sample/seed sweep, or rescue.

## Frozen execution

- Protocol commit: `142a4b69f92855c06061daa1e2a2e5eebe9536fa`
- Method commit: `78fcbde20227c80bfb8ec1aca5e994641a6c305f`
- Tests commit: `39d9c5dbafd0bcfd3aa9a4cc331e7ceb3087964e`
- Falsifier commit: `2982a8b26ed195e4daa43f1af6bb5bec6d44a435`
- Executed workflow head: `b0ec00990cf3f4553b91d1c337025bd46e724a46`
- Run/job: `35449335693 / 105913650102`
- Focused tests: `5 passed in 0.23s`
- Run attempt: 1; no rerun.
- Artifact: `e108-firstlayer-transport-cv`, ID `10585484463`, ZIP SHA256 `bb2910bc89dca2bcc880732877c887273c3fa4ef29ab094f5f76894fad6c5546`.

Frozen production-shape synthetic instance: width/depth `1024/16`, 4096 trajectories per estimator, weight seed `108104`, independent direction seeds `108105` and `108106`.

## Measured target-free risk

- E104-style baseline: `1.004403426538555e-05`
- E108 candidate: `1.0016395958298237e-05`
- candidate / baseline: `0.9972482862605754`
- reduction: `0.2751713739%`
- candidate / raw target scale `1.89e-8`: `529.968x`
- adjusted-risk proxy: `1.0016395958298238e-06`
- adjusted target: `2.5e-9`; miss factor `400.656x`.

The control is therefore active, but it explains only a negligible fraction of the dominant final-layer angular error.

## Structural/accounting checks

PASS: utilization `<=0.13`, exact FLOP reconciliation, exact antithetic pairs, finite outputs/coefficients, candidate risk below baseline, bitwise deterministic predictions, zero risk replay difference, and no target/public/scorer/holdout/full access.

FAIL: raw-risk gate and adjusted-risk gate.

## Verdict

**E108 is terminal NO-GO / DROP.**

The precise scientific blocker is that the final-layer Haar error is not materially correlated with a first-layer mean fluctuation propagated through a fixed linear `0.5` Jacobian. E108 cannot be rescued by changing coefficients, seeds, sample count, or transport after seeing this result. A successor must target a genuinely later/deeper nonlinear error component while retaining target-free unbiasedness and the `<=0.13` production budget.

No public/public-mini, official scorer, holdout/full, benchmark targets, tuning, sweep, canonical/ledger mutation, or merge occurred.
