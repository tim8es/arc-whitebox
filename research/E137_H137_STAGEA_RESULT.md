# E137-H137 Stage-A result — CountSketch s=512

Decision: **TERMINAL NO-GO / CLOSE H137 COUNTSKETCH S=512**

Idempotency key: `ARC-E137-H137-STAGEA-COUNTSKETCH-S512-20260921`

## Frozen target

H137 was the baseline-native old-tier CountSketch patch against pinned public V25:

- V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- sketch width: `s=512`
- target-free internal D21 gate: relative pooled error `<=2.2%`
- full all-in candidate cost must be below measured V25 and within `2^41`
- deterministic replay required
- no final-MSE validation unless Stage A GO.

## Implementation

The Stage-A execution protocol was committed first:

`ce5a217eca58e8608d824c7f5ef82dab6097e98a`.

Then:

- pinned V25 vendor: `3ff7fa9b8bf6abcc22b6bd1391a9be219f4495df`
- CountSketch diagnostic helper: `01f4987c62d1a015236522ddc46e498383706f52`
- focused tests: `a973b20ecc6af590f6f6076da816650dc2f183a6`
- frozen falsifier: `dea40e2f7d7709959297e56eeae6529f66d99d67`
- workflow/scientific head: `eb21ee6bb5838255293d1b8a7ae48b1aa7b20569`.

The implementation preserved exact V25 state evolution and intended to measure the
CountSketch product only as a side-channel diagnostic.

## Sole Actions run

Run:

`35544178486`

Job:

`106167052999`

Attempt:

`1`

Focused tests completed successfully:

`5 passed in 0.15s`.

The sole target-free falsifier step then failed immediately at import:

`ModuleNotFoundError: No module named 'methods'`

from:

`scripts/e137_h137_stagea_countsketch.py:15`.

Therefore the scientific executable never reached:

- pinned-V25 runtime identity verification;
- old-tier D21 capture;
- CountSketch D21-error measurement;
- all-in cost measurement/projection;
- deterministic double replay.

No artifact was produced because artifact upload was skipped after the failed step.

## Frozen-gate interpretation

The Stage-A protocol explicitly states:

> any failed or unevaluable gate => terminal NO-GO; no rerun, rescue, alternate hash,
> sketch-width change, or seed replacement.

Accordingly, this implementation-path failure cannot be repaired under H137 Stage A.

The requested scientific quantities are **UNEVALUATED**, not failed numerically:

- pooled D21 relative error: **UNEVALUATED**
- full all-in H137 cost: **UNEVALUATED**
- deterministic replay: **UNEVALUATED**

This result does **not** establish that CountSketch s=512 is mathematically inaccurate.
It establishes that the one frozen execution failed before the mechanism could be
evaluated, and the preregistered no-rerun rule therefore closes this experiment identity.

## Firewall

No final-MSE validation occurred.

No benchmark/public MLP weights, final means, scorer, holdout, or full-suite targets were
read by the scientific falsifier.

No second Actions run, sweep, rescue, canonical mutation, ledger mutation, or merge occurred.

**H137 s=512 is terminally closed under E137-H137 Stage A.**
