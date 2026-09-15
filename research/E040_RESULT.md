# E040 result — exact late-source K3 window

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-E037-RESEARCH-20260915-E040`

## Provenance

- Branch: `research/e040-late-source-exact-window-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `a25129c1c7043d8bc4ff20a9673c5a930e5d653b`
- Wrapper implementation: `031094d96086c30dfd2da71a3cd2cf0bca35d2e6`
- Pre-science arithmetic correction only: protocol `f0654426f0175bfdf054cef6a72a113e3031c158`, tests `6c2495b66c580d8f95648c9b913f00379689aa9d`
- Frozen harness: `e0ba38056f4364193f40eb5d5e2e68bacfad497a`
- Frozen scientific commit: `ea64f2b5826083c361e460bbf1e8dcb3e7ab03df`
- Public Phase-2 mini index: `0` only
- Frozen scientific run: `35012502474`
- Job: `104527676668`

## Focused TDD

- RED: run `35012080901`, job `104526263636`, expected missing E040 module; no public data.
- First implementation run: `35012184848`, job `104526612682`: 4/5 passed. The only failure exposed a pre-science arithmetic typo in the stated utilization projection. Formula and cutoff were unchanged; corrected projection is `0.1228326008`.
- Focused GREEN: run `35012335497`, job `104527116909`: all 5 tests passed.
- Frozen scientific run repeated focused tests: `5 passed in 0.07s`.

## Frozen diagnostic outcome

The single authorized public-mini index-0 diagnostic did not produce candidate MSE/FLOPs/utilization/residual metrics. During the metered candidate execution it failed with:

`ValueError: cannot reshape array of size 1024 into shape (8,1,1024)`

The failure occurs inside pinned V25 `_dslices` after the frozen patch retained only 8 dense A/P source records while untouched per-source metadata lists still contained entries for all births. The one-line insertion predicate therefore changed stack cardinality without atomically changing the complete source record cardinality.

This is a structural implementation failure of the preregistered E040 mechanism. Per the frozen kill rule, an unevaluable scientific gate is terminal NO-GO. No candidate numerical score may be inferred from the partial execution.

Verified before the failure:

- pinned V25 blob identity check passed;
- focused tests passed;
- public split was mini index 0 only;
- the run was the single authorized scientific diagnostic.

## Decision

**NO-GO / DROP E040.**

No rescue or rerun is allowed. In particular, E040 will not be repaired by filtering the metadata lists, altering the cutoff/window, changing source weights, enabling old-source confinement, or using another public index. A source-record-consistent selection mechanism requires a fresh experiment ID from canonical.

No scorer, holdout, tuning, sweep, canonical mutation, or `research/ledger.csv` mutation occurred.
