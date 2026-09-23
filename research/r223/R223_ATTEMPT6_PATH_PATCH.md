# R223 attempt 6 — frozen-path guard repair only

Date: 2026-09-23
Job: `R223`
Owner: `method-research`

Attempts 1–5 remain immutable `INFRA_ERROR`; none invoked the candidate mini-100 panel.

Attempt 6 changes only the workflow's frozen-file references:

- retain immutable `research/r223/R223_ATTEMPT4_PROVENANCE_PATCH.md` at blob
  `e5c92d45e638bc85b66753c00c909e1f00aa9345`;
- include `research/r223/R223_ATTEMPT5_AUTH_PATCH.md` at blob
  `82cb86a6d2a175c0dcaf2358f70d6d33206cd486`;
- retain the already repaired artifact Authorization header using `${GH_TOKEN}`.

The candidate remains blob `eb95d4ae46a031be5131eef8dd0909f2061b8749`;
the exact-transform verifier remains blob
`961e5afb052e2cfdc15e1284de49e57ba1514a73`.

No formula, clamp, panel, threshold, parent hash, toolchain, ranks/source state,
comparison logic or candidate tuning changes.

If any pre-panel gate fails, attempt 6 terminates `INFRA_ERROR`. If all pass, exactly one
candidate mini-100 invocation is authorized; no prior R223 attempt invoked it.

No parent rerun, paid/larger runner, holdout/private, scorer, submission, canonical
change or leaderboard claim.
