# R238 — RSRF-V25 terminal result

Status: **INCONCLUSIVE — frozen base-executability prerequisite failed**

Run ID: `R238-v25-rsrf-exact-small-20260923`

## Frozen family

R238 selected exactly one ledger-novel family: **RSRF-V25 recycled-start range finder**.
The candidate would have changed only the start block of V25's tier-1 shared-basis
range finder after the first join:

`Omega = W_slice + Qp`

instead of `Omega = W_slice`, while preserving rank, age gates and exactly one
weighted-Gram application. No coefficient/rank/seed/age sweep, oversampling,
Richardson/DRRE, response alignment, source-axis compression or target fitting was
authorized.

Frozen artifacts before execution:

- novelty audit commit `9138548194e0a20ef6ec70af439b28441081e766`;
- cost proof commit `81fca8a43ea9223690561a26d2fba1cceef8fb08`;
- protocol commit `5bcd090dfb13df51c05415135ada71b3deefc420`;
- falsifier commit `b31450cb2d795f54288db1c460b1d51b0e297693`;
- workflow commit `12c595f3dec66e4616f76ca688b1f5339b5bdf24`;
- queue start revision 166, commit `0dc2f1ca005765e11d9af4594a07c4d48171adfb`;
- sole trigger commit `37610aeb8f93ab6975d4fef996ebf6f20a81367f`.

## Sole permitted execution

GitHub Actions:

- run: `35808859764`;
- job: `107015629065`;
- attempt: `1`;
- head: `37610aeb8f93ab6975d4fef996ebf6f20a81367f`;
- conclusion: `success` for the fail-closed workflow;
- artifact: `10728444220`, name `r238-v25-rsrf`;
- GitHub artifact digest:
  `sha256:761783a92ac967758dbcee9a6d9fadb146280d89fa6f782cfcbc9a927083ef2a`;
- independently downloaded ZIP SHA256:
  `761783a92ac967758dbcee9a6d9fadb146280d89fa6f782cfcbc9a927083ef2a`.

Runtime was Python 3.11.16, NumPy 2.4.6, flopscope 0.12.1+np2.4.6 and
whestbench 0.16.1 on standard `ubuntu-24.04`.

The run verified the frozen R238 blobs and fetched the exact pinned upstream V25:

- upstream commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- V25 git blob `195373a110215256b759d7c172ba8c923c62e5cc`;
- downloaded source SHA256
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

## Base prerequisite result

The protocol required the **unchanged pinned V25 source** to execute all four frozen
synthetic fixtures before candidate source could be constructed.

It failed on the first fixture before producing a valid parent prediction:

```
flopscope.errors.SymmetryError:
Tensor not symmetric along axes (0, 1): max deviation = nan
```

Terminal site in the pinned source:

`r238-estimator-v25.py:929 — C = flops.as_symmetric(C, symmetry=(0, 1))`.

Frozen falsifier result:

- decision: `R238_BASE_INCONCLUSIVE`;
- exit code: `20`;
- `base_executable=false`;
- `candidate_constructed=false`;
- `candidate_file_exists=false`;
- `small_scientific_go=false`;
- validation: not executed;
- mini-100: not authorized and not executed.

This is the same failure class that motivated the explicit R238 base-executability
gate after R232. The gate therefore did its intended job: no candidate result is
confounded with a fixture on which the unchanged parent itself is non-finite.

## Scientific interpretation

**No RSRF accuracy measurement exists.** RSRF was neither validated nor scientifically
falsified because candidate construction was forbidden after the parent prerequisite
failed.

Per the frozen protocol there is no seed replacement, fixture resizing, scale change,
precision change, clipping, retry, rescue or second Actions run. R238 terminates
**INCONCLUSIVE**.

No mini-100/public benchmark target was accessed by R238, no private/holdout data or
submission was used, no paid compute was used, and canonical V25 was not edited.

## Durable evidence

`research/r238/R238_ACTIONS_EVIDENCE.json` records the Actions/run/artifact identity,
frozen blobs, parent identity, exact error, disposition, and artifact-internal SHA256
manifest.

The immutable workflow artifact remains the authoritative raw execution evidence.
