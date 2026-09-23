# R249 — Phase-2 scalar metering eligibility audit

Status: **SOURCE-ONLY COMPLETE**  
Role: `phase2-scalar-compliance-independent-audit`  
Run ID: `R249-phase2-scalar-compliance-independent-audit-20260923`  
Access date: 2026-09-23 UTC

## Scope

Independent source-only audit of the Phase-2 boundary between permitted Python plumbing and numerical work that must be visible to FlopScope. R245 was read only as context; its conclusions are not used as authority.

No organizer contact, estimator/benchmark/Actions run, private/holdout access, paid compute, R223/R244 candidate output/artifact inspection, submission/leaderboard action, or canonical estimator edit was performed.

## Primary sources and pinned identities

### Competition rules / organizer publication

1. **Current Challenge Rules** (dynamic AIcrowd page, accessed 2026-09-23):  
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules  
   The page is the stated eligibility source of truth but does not expose a content hash/version identifier in the public HTML.

2. **Official Phase-2 launch announcement**, Mohanty / AIcrowd, 2026-08-23:  
   https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197  
   It states that computation outside FlopScope is prohibited; at evaluation time only the grader Python interpreter, FlopScope client API, and pure-Python stdlib for control flow/bookkeeping may be used; residual time is plumbing, and meaningful computation in residual time is a rules breach.

3. **Live evaluator version clarification**, Mohanty / AIcrowd, 2026-08-27:  
   https://discourse.aicrowd.com/t/shipped-covariance-propagation-example-trips-the-phase-2-residual-cap-locally-0-16-0-but-grades-fine-what-happens-when-the-evaluator-upgrades/18202/2  
   Organizer states live evaluators use `whestbench 0.16.0` and `flopscope[server]==flopscope[client]==0.12.0`.

### Official starter-kit — current `main`

Repository: https://github.com/AIcrowd/whest-starterkit  
Current `main` HEAD verified at audit time: `5eb9aa1455fcb3216af55994bdf25dc242b95797` (2026-09-16).

| Source | Git blob |
|---|---|
| `docs/concepts/allowed-code.md` | `525276e8e5bc7f6a7dd54e876140ab0df514be32` |
| `docs/reference/code-patterns.md` | `2d1aa532af6f160fd0942da34f78595216a596de` |
| `docs/reference/flopscope-primer.md` | `7c1478581347f362f691aa1b8023d8edcd44874d` |
| `docs/how-to/performance-tips.md` | `73a73abcf02ba367a9af681bf4bd4e0325b6c337` |
| `pyproject.toml` | `2c1d562a2073046d6912868184b52c8c593d23c5` |

Direct links:
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/code-patterns.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/flopscope-primer.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/performance-tips.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml

### FlopScope

- `v0.12.0` annotated tag resolves to commit `2b8682e354379c50bc24145675356b8bb87fe6b3`.
- `v0.12.1` annotated tag resolves to commit `b599f015b0bc005b1edb6d7a1b10e0814675e693`.
- `README.md` is Git blob `3d10edb5d6456ff7eef9c1e0f9c6f1d3d2ff8fb0` in both 0.12.0 and 0.12.1.
- `flopscope-client/src/flopscope/_remote_array.py` is Git blob `5613e824b0bba847668ee1753256ceab9089e99d` in both 0.12.0 and 0.12.1.

Links:
- https://github.com/AIcrowd/flopscope/blob/v0.12.0/README.md
- https://github.com/AIcrowd/flopscope/blob/v0.12.1/README.md
- https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/flopscope-client/src/flopscope/_remote_array.py

The starter-kit `pyproject.toml` pins development to `flopscope>=0.12.1,<0.13.0` and records that the live grader is on 0.12.0; it states the 0.12.1 pricing change is limited to non-scalar `full/full_like` fill values. That change does not affect the scalar boundary audited here.

## Classification

| Category | Classification | Source-backed boundary |
|---|---|---|
| Ordinary arithmetic operators on `fnp.ndarray` (`+ - * / @`) | **CONFIRMED_ALLOWED** | Official code-patterns says these operators on `fnp.ndarray` are FLOP-tracked and equivalent to `fnp.add/multiply/divide/matmul`. Allowed-code identifies `flopscope.numpy as fnp` as the permitted array path. This is not permission for separately prohibited fair-accounting tricks such as packing independent values. |
| `fnp` numerical primitives such as `fnp.sqrt`, `fnp.divide`, reductions, einsum, linalg | **CONFIRMED_ALLOWED** | Code-patterns/primer list them as billed FlopScope operations; `fnp.sqrt` and `fnp.divide` are explicit 1× operations. Eligibility remains subject to the separate Phase-2 fair-accounting rules. |
| Trivial **shape-derived Python scalar arithmetic** used to form an argument to a metered `fnp` op, specifically the documented pattern `fnp.sqrt(2.0 / mlp.width)` | **CONFIRMED_ALLOWED — NARROWLY** | Official starter-kit performance-tips recommends this exact expression inside an estimator and describes the one-time operation as about 2 FLOPs total. FlopScope 0.12.0/0.12.1 README independently uses `fnp.sqrt(2 / width)`. The narrow conclusion is that this exact kind of trivial shape-derived scalar preparation is within the published intended usage. It is **not** a blanket exemption for arbitrary scalar numerical algorithms. |
| Output-affecting `math.*` numerical work (for example `math.sqrt` used to compute an estimator coefficient) | **CONFIRMED_PROHIBITED** | Phase-2 announcement says all computation must be through FlopScope; stdlib is for control flow/bookkeeping. Allowed-code similarly describes `math`/stdlib as available for control flow, bookkeeping and loading, and says meaningful computation outside metered FlopScope work is disqualifiable. A numerical `math.sqrt` that changes predictions is therefore outside the stated permitted role. |
| General Python scalar coefficient arithmetic/division that changes predictions but is not merely the documented trivial shape-derived case | **UNKNOWN** | It is definitely **unmetered** before the value enters FlopScope, but the official sources do not publish a mechanical/de-minimis threshold separating trivial argument shaping from “meaningful computation.” The official `fnp.sqrt(2.0 / mlp.width)` example prevents a blanket claim that every Python scalar division is prohibited; the “all computation through FlopScope / meaningful computation outside is prohibited” rule prevents a blanket claim that arbitrary coefficient algebra is allowed. Clearly substantial scalar numerical algorithms fall on the prohibited side, but the general middle category is unresolved from published primary sources alone. |
| Control flow, indexing/looping, bookkeeping, shape handling, and loading shipped data | **CONFIRMED_ALLOWED** | The Phase-2 launch announcement explicitly reserves residual Python for looping, indexing, bookkeeping and deciding which FlopScope ops to call. Allowed-code adds shaping arguments, walking layers and loading tables/files as plumbing; shipped data files are explicitly permitted. These uses cannot be repurposed as an unmetered arithmetic lane. |

## Exact metering interpretation of `fnp.sqrt(2 / width)`

The expression has two different execution domains:

1. Python evaluates `2 / width` first. That arithmetic occurs in CPython before the FlopScope call.
2. The resulting Python scalar is passed to `fnp.sqrt(...)`.
3. FlopScope meters the `sqrt` operation. Its 0.12.0/0.12.1 README budget summary shows one scalar `sqrt` call charged while no separate Python-division operation appears.
4. The 0.12.0/0.12.1 client source `_encode_arg` explicitly fast-paths exact Python `float` and `int` values and sends them as scalar arguments; therefore arithmetic that produced the scalar before dispatch is not retroactively visible to the FlopScope meter.

**Eligibility conclusion:** the prior Python division is unmetered, but the exact shape-derived pattern is nevertheless a published official usage pattern. The safe inference stops there.

## Practical source-compliance rule for future ARC research

- Keep array-valued numerical work and transcendental/numerical primitives on `fnp`/FlopScope.
- Treat output-affecting `math.*` as prohibited.
- Treat `fnp.sqrt(2.0 / mlp.width)`-style trivial shape-derived scalar preparation as allowed by the published examples.
- Do **not** generalize that example into permission for arbitrary Python scalar coefficient pipelines. If the scalar arithmetic is algorithmically meaningful rather than argument/shape plumbing, the published rules either prohibit it or leave its exact boundary unresolved; for source-only preregistration, classify the unresolved middle as **UNKNOWN** and avoid relying on it.

## Evidence limits

- The current AIcrowd Challenge Rules page is dynamic and exposes no immutable public content hash in the retrieved HTML. This audit therefore uses the dated official Phase-2 launch announcement for verbatim public rule language and the current official starter-kit commit for versioned implementation guidance.
- No first-party organizer clarification located in the audited sources gives a blanket rule specifically for arbitrary Python scalar coefficient arithmetic.
- FlopScope pricing/source proves what is metered; it does **not** by itself decide competition eligibility. The starter-kit explicitly says Challenge Rules override pricing documentation on eligibility.
- This report makes no claim about any R223/R244 candidate implementation or output.

## Verdict

The official source boundary is **not** “all Python scalar arithmetic is free” and also **not** “every Python scalar arithmetic operation is forbidden.”

The supported classification is:

- `fnp.ndarray` operators: **CONFIRMED_ALLOWED**
- `fnp` primitives: **CONFIRMED_ALLOWED**
- trivial shape-derived scalar preparation such as `2.0 / mlp.width` immediately passed to `fnp.sqrt`: **CONFIRMED_ALLOWED, narrow scope**
- output-affecting `math.*`: **CONFIRMED_PROHIBITED**
- general output-affecting Python scalar coefficient/division arithmetic: **UNKNOWN** unless it is clearly substantial enough to be “meaningful computation,” in which case the Phase-2 prohibition applies
- control/bookkeeping/loading: **CONFIRMED_ALLOWED**
