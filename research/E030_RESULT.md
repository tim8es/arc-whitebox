# E030 result — rank-8 conditional-Gaussian latent carrier

Status: **DONE / NO-GO / DROP**

## Provenance

- Branch: `research/e030-r8-conditional-gaussian-carrier-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `aca8d805c9417cf03749e68432a883434b5c488c`
- RED tests commit: `774925982f10b00fdb35207cd35c3f1de19c3d98`
- RED workflow commit: `74a57d053d8f8dbd9c33aa2249cc133bb0bcab21`
- Implementation commit: `d6d88e89acf4a038d5cd6266622913e55fef06fb`
- Frozen diagnostic harness commit: `5f24326c26f837eccee4dbffeec3ec64f9ed63f3`
- Harness-only dataset orientation fix: `34a0fdf5104e23d53ee92f4b7024562a7252dca6`
- Single frozen diagnostic launch commit: `728b1779160de3da2af42d040ef39c721176f06b`

The orientation fix changed only the diagnostic's interpretation of the dataset weight storage (`W = w.T`) before any scientific run. It did not change rank, probes, cubature, closure, gates, or method algebra.

## TDD evidence

- RED run `34995771846`, job `104471487382`: expected collection failure, `ModuleNotFoundError: No module named 'methods.e030_conditional_gaussian'`.
- GREEN run `34995887811`, job `104471880157`: `3 passed in 0.37s`.
- Frozen scientific run `34997319946`, job `104476715939`: focused tests `3 passed in 0.46s`, then the one allowed diagnostic executed and failed scientifically.

## Frozen diagnostic outcome

The diagnostic entered the preregistered rank-8 Nyström / conditional-Gaussian path on public mini index 0. During the first scientific execution it emitted an invalid-value warning at a square root and subsequently failed at the conditional carrier eigendecomposition with:

`numpy.linalg.LinAlgError: Eigenvalues did not converge`

No `e030_result.json` artifact was produced because the frozen method became non-finite before summary metrics could be computed.

This is a terminal scientific failure under the protocol, not an infrastructure retry condition. The preregistered protocol states that any non-positive/nonfinite required Gram spectrum or carried diagonal residual is an immediate NO-GO, and that any failed or unevaluable gate is NO-GO with no clipping, jitter, fallback, alternate probes, rank change, rescue, or rerun.

Therefore raw MSE, adjusted proxy, utilization, and deterministic-repeat metrics are **unevaluable for the frozen candidate**; the candidate failed earlier on the finite/PSD carrier requirement.

## Decision

**NO-GO / DROP E030.**

Do not rerun E030 and do not rescue it with jitter, clipping, pseudoinverse, changed probes, changed rank, alternate cubature, or a second mini index. Any such mechanism is a new experiment and must receive a new lane/protocol.

No official scorer, holdout, tuning, sweep, or canonical mutation was performed.