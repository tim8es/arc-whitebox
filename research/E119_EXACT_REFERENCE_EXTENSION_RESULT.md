# E119 exact-reference extension — PASS

Role: **exact reference engineer**.

Branch:
`review/e119-exact-reference-extension-20260919`

This is a support/review extension of the completed E119 owner lane. It does
not modify the frozen E119 deployability verdict.

## What changed

The reusable 2-D angular reference harness now supports arbitrary dense
zero-bias weight chains with heterogeneous small widths through
`dense_he_weights(seed, widths=...)`, plus layerwise sector enumeration and
direct network evaluation on angular directions.

A reusable comparator
`methods/e119_exact_reference_compare.py` checks the generic E119 boundary
implementation against the exact reference at the level of:

- layerwise region counts;
- final interval endpoints;
- final sector coefficient matrices;
- direct raw-network values at three interior points per sector;
- boundary angles;
- scalar boundary jumps;
- sector-integrated scalar Gaussian mean;
- boundary-flux scalar Gaussian mean.

## Reusable tests

`tests/test_e119_exact_reference_extension.py` covers:

- `2 -> 3`
- `2 -> 5 -> 2`
- `2 -> 4 -> 6 -> 3`
- `2 -> 8 -> 5 -> 7 -> 2`
- `2 -> 3 -> 8 -> 4 -> 6`
- one hand-specified fully dense rectangular chain
  `2 -> 3 -> 2 -> 1`
- deterministic replay.

Focused CI result:

`7 passed in 0.38s`.

## Evidence run

Workflow commit:
`781510a0684dd5ae7320b8e2ea07174d825a3d3f`

Run/job:
`35458239376 / 105937257716`

Artifact:
`e119-exact-reference-extension`

Artifact ID:
`10589800043`

Artifact ZIP SHA256:
`723f467cb56301dea0b6daa76dd5dab72b0c08e31648a237e7f21227b0dd3266`

Workflow conclusion:
`success`.

## Frozen heterogeneous corpus result

Six dense architectures were evaluated. Maximum exact final region count was
`39`.

Worst discrepancies over the full corpus:

- layerwise region counts: exact match on every layer;
- final region counts: exact match;
- final sector lower-endpoint error: `0.0`;
- final sector upper-endpoint error: `0.0`;
- final sector coefficient max abs error: `0.0`;
- boundary-angle wrapped error: `0.0`;
- scalar boundary-jump max abs error:
  `2.220446049250313e-16`;
- exact-reference direct raw-network interior error:
  `8.881784197001252e-16`;
- generic-sector direct raw-network interior error:
  `8.881784197001252e-16`;
- generic full scalar mean vs exact sector reference:
  `4.440892098500626e-16`;
- exact boundary-flux mean vs exact sector mean:
  `4.440892098500626e-16`;
- partition max gap: `0.0`;
- partition max overlap: `0.0`;
- deterministic replay: exact.

All weight matrices in the frozen corpus were fully dense/nonzero.

## Decision

**E119_EXACT_REFERENCE_EXTENSION_PASS**

The generic E119 weight-driven boundary implementation agrees with the extended
exact angular-sector reference on arbitrary heterogeneous dense small networks
through width 8 / depth 4, down to sector coefficient state and direct
network evaluation.

This validates the small-width reference/implementation bridge. It does not
change the existing E119 deployment conclusion: the exact construction is
correct, while useful nonzero-atom compression remains the unresolved blocker.

No benchmark/public/scorer/holdout/full target, tuning, production scientific
run, canonical mutation, or ledger mutation was used.
