# E109+ archive staging area

This directory is reserved for **future verified E109+ evidence artifacts**.

It is intentionally empty of experiment claims at creation time.

## Admission for an archived artifact

Every added receipt must identify:

- experiment ID and exact mechanism identity;
- authoritative branch and head/receipt commit SHA;
- protocol SHA and ancestry/base;
- run/job/artifact ID and digest when execution occurred;
- measured metrics and frozen gates;
- terminal disposition or explicit `UNEXECUTED` gaps;
- scope flags for public/public-mini/scorer/holdout/full;
- canonical/ledger mutation state.

Same-ID collisions must be stored as separate identities. Chat-only summaries are not repository evidence.

The presence of this directory does not allocate E109 or any later ID.
