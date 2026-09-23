# R245 — independent static Phase-2 compliance audit of frozen R244 MP-R16

## Scope and evidence boundary

This is a read-only static audit. It inspects only the frozen R244 protocol, estimator source, and one-shot workflow at `f8548d77bdc27b643734f0ce1e9bc6fb243fb56a`, plus official/public rules and FlopScope documentation. It does **not** inspect the R244 candidate artifact/output, execute the estimator, run a benchmark or Actions workflow, access private/holdout data, spend compute, submit, or mutate a leaderboard.

Frozen R244 source identities:

- `research/r244/R244_PROTOCOL.md`: Git blob `0cd8e63fb4184a816e653b7507bf8ba9b1bb10e7`, SHA256 `963b12b66df5a1b3f60d4e7ce8186b25ba0381f4e99e5c777236e051a0043d5e`.
- `methods/r244_estimator_v25_marginal_rres.py`: Git blob `d034aee83c766d6eb613b71a1a22c30241cd172a`, SHA256 `7987d43f6eb79bee50805bf1474d43e0a09a29737b86e3aab22b34ca97385859`.
- `.github/workflows/r244-mp-r16.yml`: Git blob `32a3bb0d5d45a2acb79151560d132d97876f4ee4`, SHA256 `32b04a7e3f7f442b2ada3b3b82d5d502cf6dd418ade8009ca54e5845aa49d87b`.

Frozen source: https://github.com/tim8es/arc-whitebox/tree/f8548d77bdc27b643734f0ce1e9bc6fb243fb56a

## Official rule baseline

The AIcrowd starter kit says the official Challenge Rules are the eligibility source of truth. Its Phase-2 summary says: (1) the allowed execution surface is the grader Python interpreter, the FlopScope client API, and pure-Python stdlib; (2) `flopscope.numpy as fnp` is the only array path and its operations are billed; (3) stdlib such as `math` is available for control flow, bookkeeping, and loading; and (4) residual time is plumbing, not a free compute budget — meaningful computation outside metered FlopScope work is a rules breach/disqualifiable.

Pinned official source: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md
Git blob `525276e8e5bc7f6a7dd54e876140ab0df514be32`, SHA256 `fb6384e63deeec6dd579ed679e2dafaffcd0343511dd24638199362cf3ddbcdf`.

The official code-patterns page states that Python operators `+ - * / @` on `fnp.ndarray` are tracked, and explicitly lists `fnp.sqrt` and `fnp.divide` as billed operations. Its normal-distribution example uses `fnp.sqrt`, not `math.sqrt`, for numerical work on estimator values.

Pinned official source: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/code-patterns.md
Git blob `2d1aa532af6f160fd0942da34f78595216a596de`, SHA256 `7460fcb736eb34c42293c6f8446de1d031554edeacb68f6e9ee5aa7752553157`.

The official FlopScope primer likewise lists elementwise `/` and `fnp.sqrt` in the 1x billed tier and says estimator predictions run inside a `BudgetContext`.

Pinned official source: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/flopscope-primer.md
Git blob `7c1478581347f362f691aa1b8023d8edcd44874d`, SHA256 `7a5fdcbcbbb5e4000b91ad7158fceb4d4cd5ca6c7e5006f04acbab2423a23b41`.

Official Challenge Rules: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules

## Findings

### Confirmed violation: output-affecting `math.sqrt` bypasses the metered path

Frozen estimator line 945 is:

`u0 = ones_n * (1.0 / math.sqrt(float(n)))`

`n` is the MLP width. `math.sqrt(float(n))` executes in CPython's stdlib, not through FlopScope, and therefore contributes no FlopScope FLOPs. The result is not control-flow/bookkeeping metadata: it numerically defines the normalized all-ones vector used by the R244 MP-R16 construction (`a0`, `b0`, `c0`, `M0`, and the two preserved marginal columns). The official Phase-2 summary restricts stdlib use to control flow/bookkeeping/loading and says meaningful unmetered computation is a breach. A directly metered primitive, `fnp.sqrt`, exists and is explicitly billed. On that source-backed reading, this is a **confirmed static Phase-2 compliance violation**.

This finding is candidate-specific: the frozen public V25 parent imports `math` but has no `math.*` call; the MP-R16 replacement introduces this `math.sqrt` use.

### Confirmed metering bypass, eligibility boundary not explicit: Python scalar division/coefficient arithmetic

The same line performs `1.0 / <Python float>` in CPython before multiplying the result into `ones_n`. It is therefore also unmetered. Separately, `_statics(n)` at lines 341–345 is called from `predict()` at line 429 and performs Python-scalar arithmetic/divisions to derive `P2`, `cA`, and `cI`, which later scale estimator arrays. Several later `float(st[...] * metric2)` / `float(n * st["P2"])` expressions similarly prepare Python scalar coefficients before an `fnp` array operation.

These are **confirmed unmetered numeric operations**. Their independent eligibility status is less explicit than `math.sqrt`: FlopScope v0.12.1's own README demonstrates `fnp.sqrt(2 / width)`, where the shape-derived `2 / width` is a Python scalar division before the metered square root. Thus the public materials do not establish a blanket rule that every shape-derived scalar arithmetic operation is forbidden. R245 therefore records these scalar divisions/coefficient calculations as **UNKNOWN as standalone eligibility violations**, not as additional confirmed violations. This ambiguity does not rescue the separate `math.sqrt` finding.

FlopScope v0.12.1 source identity: commit `b599f015b0bc005b1edb6d7a1b10e0814675e693`; README Git blob `3d10edb5d6456ff7eef9c1e0f9c6f1d3d2ff8fb0`, SHA256 `3b7f3a50fe96fcba90d250c7b39799ad05acd068009a291045052026e6033914`.
Source: https://github.com/AIcrowd/flopscope/blob/v0.12.1/README.md

### Confirmed non-violations / covered paths

- The frozen estimator imports no NumPy/SciPy/BLAS, FFI, threading, multiprocessing, subprocess, asyncio, Torch, or JAX in the grader import path. Its numerical array imports are `flopscope` / `flopscope.numpy` plus whestbench contract types.
- Static search found no `float(fnp...)`, `bool(fnp...)`, or `int(fnp...)` materialization of FlopScope values.
- Array-valued `+`, `-`, `*`, `/`, `@`, `w1 ** 3`, `fnp.sum/mean/sqrt/power/clip/einsum`, and `fnp.linalg.qr` stay on the FlopScope array/operator surface. Official code-patterns documentation says operators on `fnp.ndarray` are tracked; the primer documents these operation families as billed.
- `rb = r - 2`, index/rank bounds using `min/max/int/len`, loop counters, shape tests, and environment-string parsing are control/shape/bookkeeping rather than array numerical estimation.
- The `local_engine` import is under `if __name__ == "__main__":`; it is not reached when the grader imports the estimator class. R245 does not claim that an external static packaging scanner will ignore unreachable imports; that scanner behavior is **UNKNOWN** from the audited sources.

### Workflow provenance and meter-version check

The frozen one-shot workflow uses `ubuntu-24.04` and installs `numpy==2.4.6`, `whestbench==0.16.1`, `flopscope==0.12.1` for development validation. Its candidate invocation uses `whest run --runner local` with Phase-2 `B=2**41`, 120 s wall cap, 0.4 s residual cap, and one thread.

The official starter-kit `pyproject.toml` at commit `5eb9aa1455fcb3216af55994bdf25dc242b95797` pins `whestbench>=0.16.1,<0.17.0` and `flopscope>=0.12.1,<0.13.0`, while documenting that the live grader is `whestbench 0.16.0` + `flopscope 0.12.0`. It explicitly states that the only 0.12.1 pricing change is `full/full_like` with a non-scalar fill value. Static inspection of the R244 estimator finds **zero** `fnp.full` or `fnp.full_like` calls. Therefore the patch-level meter difference is a **confirmed non-issue for the operation family changed by 0.12.1**, while this static audit does not claim byte-for-byte remote execution equivalence for every backend detail.

Pinned source: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml
Git blob `2c1d562a2073046d6912868184b52c8c593d23c5`.

Organizer confirmation of live evaluator versions (2026-08-27): https://discourse.aicrowd.com/t/shipped-covariance-propagation-example-trips-the-phase-2-residual-cap-locally-0-16-0-but-grades-fine-what-happens-when-the-evaluator-upgrades/18202/2

## Verdict

**STATIC COMPLIANCE NO-GO — confirmed unmetered output-affecting `math.sqrt` in the frozen MP-R16 `predict()` path.**

This is independent of R244's already-terminal DEVELOPMENT NO-GO and does not alter that result. It is not a leaderboard or submission claim. The Python-scalar division/coefficient cases are recorded separately as confirmed metering bypasses whose standalone eligibility boundary is not explicit in the audited official materials.

## Concrete next step

Do not modify or rerun R244. For any future distinct candidate, freeze a source-level compliance gate before science: no output-affecting `math.*` in `predict()`; use metered `fnp.sqrt`/FlopScope array operations for numerical estimator work, and obtain organizer clarification before relying on nontrivial Python-scalar arithmetic as free numerical computation.
