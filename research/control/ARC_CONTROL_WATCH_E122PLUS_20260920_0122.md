# ARC control watch baseline — 2026-09-20 01:22 +03

Control key: `ARC-CONTROL-WATCH-E122PLUS-20260920-0122`

Status: **FAIL-CLOSED MONITOR / APPEND-ONLY CONTROL**.

This receipt is control-only. It does not authorize canonical or ledger mutation, scientific execution, public/public-mini, scorer, holdout/full, tuning, rescue, rerun, merge, or speculative status integration.

## Frozen terminal/control facts

- **E119: CLOSED.** No new E119 scientific or verifier variants are admissible.
- **E121: TERMINAL NO-GO.** Authoritative scientific run remains `35460988924`, job `105944694427`, artifact `10588818925`, SHA256 `fb49a9be2945d0ffb3c8aaad3ae59600fd7cdc7493fd8959666319284632d836`. No rescue/rerun/re-keyed E121 mechanism is admissible.
- **E128 canonical-ledger mutation violation: already recorded** at control commit `54faf66781dc79ddd971e8570b10a92c9f296af9`. The violating integration path does not authorize successor science or further ledger mutation.

Observed canonical state is `research/bootstrap@7a0034088ebbffbd74b441e1797c272e9d33cbff`; observed `research/ledger.csv` blob is `040e52efe01efd7280180b7e2d72901b4c2f0532`. These values are evidence only, not approval of the E128 mutation. This control branch must not modify either.

## E122+ collision surface at baseline

Live branch search:

- E122: no dedicated branch;
- E123: no dedicated branch;
- E124: no dedicated branch;
- E125: no dedicated branch;
- E126: no dedicated branch;
- E127: no dedicated branch;
- E128: **occupied/collided** by
  `research/e128-owner-integrator-20260919` and
  `research/e128-integrate-e121-20260919`;
- E129: no dedicated branch observed.

Canonical contains `research/E122_PROTOCOL.md` and `research/E128_ID_REGISTRY.json` from the E128 integration. They are governance residue from the already-recorded mutation and must not be treated as run-backed scientific status.

In particular:

- the canonical E122 file explicitly says protocol-only and no scientific run authorized;
- E123-E127 registry entries are unexecuted reservations only;
- no E122-E127 ledger row is admissible without a collision-free owner identity, protocol-first provenance, and physical run-backed receipt;
- E128 is not available as a fresh scientific ID.

## Admission rule for any new E122+ scientific lane

A lane is admissible for observation/verification only if all are true before implementation/execution:

1. experiment ID has no competing scientific owner branch, incompatible protocol identity, or prior terminal fingerprint;
2. first owner commit is protocol-only;
3. protocol freezes mechanism, provenance/base, deterministic corpus/seeds, comparator, all-in cost accounting, numerical GO/NO-GO gates, target-access audit, one-run/no-rescue discipline, and terminal kill rule;
4. implementation/workflow comes only after the protocol commit;
5. no public/public-mini/scorer/holdout/full access unless separately and explicitly authorized;
6. no canonical/ledger mutation;
7. no ledger/status integration from protocol text, branch existence, accepted command, issue/comment, workflow creation, or other status-only claim;
8. scientific status requires physical run/job evidence and an immutable result receipt.

Any lane failing these checks is fail-closed and must be re-keyed or stopped before scientific execution.

## Fresh-run watermark

At this baseline, the newest repository Actions run observed is:

- run `35464849858`;
- branch `research/bootstrap`;
- head `7a0034088ebbffbd74b441e1797c272e9d33cbff`;
- created `2026-09-19T19:36:11Z`;
- conclusion `failure`.

This and all older runs are **pre-baseline** and must not trigger a new verifier dispatch.

A **fresh run** is the first Actions run created after this baseline/watermark on an admissible collision-free protocol-first E122+ scientific owner branch. Canonical CI, governance/integration workflows, control receipts, closed E119/E121 activity, duplicate/collided IDs, or status-only workflows do not qualify.

## Single next gate

**WAIT FOR FIRST QUALIFYING FRESH SCIENTIFIC RUN.**

When one appears:

1. freeze its experiment ID, owner branch, protocol SHA, executed head, run ID, job ID and artifact/digest if emitted;
2. verify protocol-first ancestry and collision freedom before interpreting the result;
3. immediately designate exactly one independent verifier identity that descends from or pins the executed owner evidence without modifying/substituting the owner candidate;
4. verifier is review-only and must not rerun/rescue/tune the owner mechanism;
5. append a control receipt recording the owner→verifier handoff;
6. do not add or endorse any canonical ledger row until the run-backed scientific receipt and independent verifier receipt both exist and a later explicit control decision authorizes ledger mutation.

Until that trigger occurs, the correct control action is **no scientific mutation and no status promotion**.
