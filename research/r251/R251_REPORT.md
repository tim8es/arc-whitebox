# R251 — terminal parent-gate infrastructure report

Status: **INCONCLUSIVE — parent not executed**  
Run ID: `R251-global-accuracy-full-history-method-20260923`

## Result

R251 stopped fail-closed at the mandatory unchanged-parent prerequisite. The frozen
production-shape fixture and GFNP hypothesis were preregistered before measurement, but
the exact Phase-2 development runtime required to execute the unchanged parent was not
available in this session.

Observed local runtime:

- Python `3.13.5`;
- NumPy `2.3.5`;
- `flopscope`: not installed;
- `whestbench`: not installed;
- `python3.11`: not present.

The R209/Phase-2 development provenance used Python 3.11.16, NumPy 2.4.6,
FlopScope 0.12.1 and WhestBench 0.16.1. Official PyPI identities were independently
resolved before any execution attempt:

- FlopScope 0.12.1 wheel SHA256
  `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`,
  source commit `b599f015b0bc005b1edb6d7a1b10e0814675e693`;
- WhestBench 0.16.1 wheel SHA256
  `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`,
  source commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`;
- NumPy 2.4.6 CPython-3.13 Linux wheel SHA256
  `a7830bab239b79cda9c08c2da014761cafb48da6150e1da17ac06283f43b6089`.

A direct install attempt of the official FlopScope wheel failed before installation
with:

`Failed to establish a new connection: [Errno -3] Temporary failure in name resolution`

after pip exhausted retries. The local execution container has no usable outbound DNS.
No package bytes were installed.

## Frozen work completed before the blocker

Full-history deduplication used `research/history.json` (194 experiment IDs; blob
`8f94f371572fedbd8c1ebd9d19cc48ca837592fb`) and the legacy ledger, plus the
required R231/R232/R238/R239/R245/R249/R250 evidence. R230 was used only for its
documented conclusion that leader methods are undisclosed; no leader mechanism was
invented.

Exactly one distinct hypothesis was frozen: **V25-GFNP**, an analytic Gaussian
fixed-point null projection of the already-existing 16x13 V25 mean-rider coefficient
table. It performs no target fit, no parameter sweep and no per-network selection.
The exact projected table is in `R251_GFNP_SPEC.json`.

The single production-configuration target-free fixture was also frozen before any
parent execution: width 1024, depth 16, seed/id 251001, positive monomial float32
weights. Exact dense concatenated weight SHA256 is
`3b94abf468e6d829c5caf55096cbb13946a3ed042a92815eb718c5c8c501ff1a`; exact
layer-mean truth SHA256 is
`8e326c2c124ac70b41afb64ada24317430bb18c0a459428044094b1d954b0876`.

## Stop-rule application

The frozen protocol requires the **unchanged parent on this exact production-shaped
fixture first**. If that gate cannot be completed, R251 must finish INCONCLUSIVE and
must not construct or execute the candidate.

Accordingly:

- unchanged V25 parent scientific execution: **not run**;
- parent per-layer measurements: **none** (no fabricated checkpoints);
- GFNP estimator file: **not constructed**;
- GFNP falsifier: **not run**;
- estimator/benchmark/Actions: **not run**;
- public R209 mini-100: **not accessed/run**;
- no retry, substitute runtime, resize/rescale/reseed, second fixture or second method;
- no R223/R244 candidate outputs/artifacts;
- no private/holdout, paid compute, submission, leaderboard mutation or canonical V25 edit.

This is an infrastructure-limited **INCONCLUSIVE**, not evidence for or against GFNP
accuracy and not a scientific rejection of the V25 parent.

## Frozen artifacts

- `research/r251/R251_PROTOCOL.md`
- `research/r251/R251_NOVELTY_AUDIT.json`
- `research/r251/R251_GFNP_SPEC.json`
- `research/r251/R251_FIXTURE_MANIFEST.json`
- `research/r251/r251_fixture.py`
- `research/r251/R251_RUNTIME_BLOCKER.json`

## Primary package sources

- https://pypi.org/project/flopscope/0.12.1/
- https://pypi.org/project/whestbench/0.16.1/
- https://pypi.org/project/numpy/2.4.6/
