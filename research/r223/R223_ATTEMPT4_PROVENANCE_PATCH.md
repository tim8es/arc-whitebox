# R223 attempt 4 — exact-byte provenance completion

Date: 2026-09-23
Job: `R223`
Owner: `method-research`

Attempts 1–3 remain immutable `INFRA_ERROR` and none invoked the mini-100 candidate
panel.

Attempt 4 changes no scientific configuration. It completes the source-provenance repair
required by the user's instruction that the pinned V25→V25-LF transform be byte-verifiable.

## Exact formatting repairs now represented

Relative to the immutable attempt-1 candidate:

1. the literal two-character docstring sequence `\n` is replaced by one LF;
2. the single terminal LF present in the pinned V25 parent blob is restored at EOF.

No executable token changes in these two repairs.

The terminal-LF commit `3efd6ea32dbc0418cba76d9dae5fce45545bdde8`
shows only Git's `No newline at end of file` marker disappearing. Current candidate
git blob:

`eb95d4ae46a031be5131eef8dd0909f2061b8749`.

The exact-transform verifier is versioned at commit
`8b4d5e545ccb6806a4af6671144ef37e1555618f`, blob
`961e5afb052e2cfdc15e1284de49e57ba1514a73`. It must prove both:

- current candidate = attempt-1 candidate after exactly the two non-arithmetic formatting
  normalizations above;
- current candidate bytes = pinned V25 bytes after exactly the preregistered V25-LF
  arithmetic transform plus the R223 documentation line.

## Frozen science

Unchanged from `R223_PROTOCOL.md` and `R223_ATTEMPT2_PROTOCOL.md`:

- K4→K3 feed-local lambda formula;
- scalar V25 lambda transport;
- clamp `[0.5,2]`;
- mean-one normalization;
- ranks/ages/source state;
- exact R209 parent artifact and mini-100 panel;
- cost and all scientific thresholds;
- no parent rerun and no tuning.

If any pre-panel gate fails, attempt 4 ends `INFRA_ERROR`. If they all pass, exactly one
candidate mini-100 invocation is authorized. No earlier R223 attempt invoked that panel.

No paid/larger runner, holdout/private, scorer, submission, canonical change or
leaderboard claim.
