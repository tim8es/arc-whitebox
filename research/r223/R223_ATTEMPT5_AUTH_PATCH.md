# R223 attempt 5 — parent-artifact auth bootstrap patch

Date: 2026-09-23
Job: `R223`
Owner: `method-research`

Attempts 1–4 remain immutable `INFRA_ERROR`; none invoked the candidate mini-100 panel.

Attempt 4 proved the exact source-provenance gate:

- pinned V25 git blob:
  `195373a110215256b759d7c172ba8c923c62e5cc`;
- current V25-LF candidate blob:
  `eb95d4ae46a031be5131eef8dd0909f2061b8749`;
- current candidate equals attempt-1 after only the documented docstring-LF and EOF-LF
  formatting normalizations;
- current candidate equals the exact preregistered pinned V25→V25-LF byte transform;
- formula/clamp tokens exact; no target access.

Attempt 4 then failed before curl executed because the workflow exported the GitHub Actions
credential as `GH_TOKEN` but referenced unset `GITHUB_TOKEN` under `set -u`.

Attempt 5 changes only that shell variable reference:

`Authorization: Bearer ${GITHUB_TOKEN}`
→
`Authorization: Bearer ${GH_TOKEN}`.

No estimator, verifier, parent hash, formula, clamp, panel, threshold, rank, source state,
toolchain or comparison logic changes.

If the exact R209 ZIP/report hashes, validation or any other pre-panel gate cannot be
proven, attempt 5 terminates as `INFRA_ERROR` before `whest run`. If all pass, exactly
one candidate mini-100 invocation is authorized; no previous R223 attempt invoked it.

No parent rerun, paid/larger runner, holdout/private, scorer, submission, canonical
change, candidate tuning or leaderboard claim.
