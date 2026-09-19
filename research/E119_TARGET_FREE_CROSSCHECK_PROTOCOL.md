# E119 target-free cross-check protocol

Idempotency key: `ARC-E119-TARGET-FREE-CROSSCHECK-20260919`

Status at freeze: **ONE FROZEN TARGET-FREE DATAFLOW CROSS-CHECK AUTHORIZED**.

## Purpose

E119 generic boundary-flux construction already passed its mathematical and
engineering gates. This audit does **not** rerun or retune the E119 scientific
experiment. It verifies a narrower property requested for estimator hygiene:

> the generic boundary-flux candidate must depend only on frozen network
> weights and preregistered constants, with no benchmark targets, no tuning,
> no post-result fitting, no unstable covariance/variance division, and no
> hidden dependence on the exact-reference verifier.

Branch:
`review/e119-target-free-crosscheck-20260919`.

Parent sealed E119 head:
`de346277894ccb89ceef39e76ca6d8f12853b2ee`.

No public/public-mini, scorer, holdout/full, production scientific run,
benchmark labels, canonical mutation or ledger mutation.

## Objects under audit

Candidate constructor:
`methods/e119_generic_boundary_flux.py::build_generic_boundary_flux`.

Weight-only observable helper:
`methods/e118_output_flux_sketch.py::output_observable`.

Original executed arm:
`d731e845c96d401ac001da82c8998c06a03ec484`.

The independent reference module
`methods/e114_exact_angular_reference.py` is verifier-only and is not allowed
to contribute to candidate construction or atom selection.

## Frozen small cross-check fixture

Use one new disjoint synthetic network:

- input dimension: 2;
- width: 4;
- depth: 3;
- zero bias;
- deterministic iid He-normal float64 weights;
- seed: `119904`;
- budget passed to candidate: `2^41`.

Weights are generated in-memory from the frozen algorithm. No file, benchmark,
target array, target mean, reference covariance, or score is loaded.

## Cross-check A — poisoned oracle/reference boundary

Before calling the candidate, monkeypatch the following verifier/fitting
functions to raise immediately if invoked:

- `methods.e114_exact_angular_reference.build_exact_reference`;
- `numpy.linalg.lstsq`;
- `numpy.linalg.solve`;
- `numpy.linalg.pinv`;
- `numpy.polyfit`;
- `numpy.cov`;
- `numpy.var`.

Then call `build_generic_boundary_flux(weights)`.

Pass condition: candidate construction succeeds and returns a finite result.
This proves the executed path does not require the exact reference or the
listed fitting/covariance primitives.

## Cross-check B — explicit forbidden-I/O guard

During candidate construction, monkeypatch:

- `builtins.open`;
- `pathlib.Path.open`;
- `pathlib.Path.read_text`;
- `pathlib.Path.read_bytes`;
- `numpy.load`;
- `numpy.loadtxt`;
- `numpy.genfromtxt`.

Every guarded function raises if called.

Pass condition: candidate construction succeeds. Since the only input is the
in-memory weight list, this is a runtime proof that the candidate path reads no
benchmark/target/reference file.

## Cross-check C — independent atom-selection recomputation

The candidate's retained/omitted atom set must be reproducible from only:

- candidate scalar jumps;
- candidate boundary angles;
- frozen constants:
  `RAW_MSE_GATE=1.89e-8`,
  `GAUSSIAN_FACTOR=sqrt(pi/2)/(2*pi)`,
  `OMITTED_FLUX_L1_BUDGET=sqrt(RAW_MSE_GATE)/GAUSSIAN_FACTOR`.

Independently recompute the deterministic ordering

`(|Delta_i|, theta_i, i)`

and omit the longest prefix whose cumulative absolute jump is within the frozen
L1 budget.

Pass conditions:

- independently recomputed omitted indices equal candidate omitted indices;
- retained indices equal;
- omitted L1 sum equal to `<=1e-15`;
- compressed mean equal to `<=1e-15`;
- certificate equal to `<=1e-15`.

No exact/reference mean enters this recomputation.

## Cross-check D — source-level forbidden dependency scan

Parse the candidate module and observable helper with Python `ast`.

Candidate/helper scientific code must contain none of these forbidden
dependency roots or fitting calls:

- modules/names: `whestbench`, `datasets`, `build_exact_reference`,
  `oracle_flux_basis`, `projection_metrics`, `observable_metrics`;
- calls/attributes: `lstsq`, `solve`, `pinv`, `polyfit`, `cov`,
  `var`, `least_squares`;
- target/data file APIs: `load`, `loadtxt`, `genfromtxt`, `read_csv`,
  `read_parquet`.

The scan is limited to executable AST names/imports/calls; comments/docstrings
do not fail the gate.

## Cross-check E — post-result immutability

Using frozen Git object identities, verify that the scientific files executed at
arm `d731e845...` have the same blobs as the sealed E119 head
`de346277...`:

- `methods/e119_generic_boundary_flux.py`;
- `methods/e118_output_flux_sketch.py`;
- `scripts/e119_generic_boundary_flux_certificate.py`;
- `tests/test_e119_generic_boundary_flux.py`;
- `.github/workflows/e119-generic-boundary-flux-certificate.yml`;
- `research/E119_PROTOCOL.md`;
- `research/E119_RUN_ARM.json`.

This audit workflow stores the expected arm/sealed blob SHA pairs in a frozen
JSON manifest committed before execution. Every pair must be identical.

Result/receipt Markdown/JSON files created after the arm are excluded because
they are evidence, not candidate scientific code.

## Cross-check F — deterministic replay

Run the guarded candidate twice from independently regenerated copies of the
same frozen weights.

Require exact equality of:

- boundary angles;
- scalar jumps;
- retained/omitted indices;
- full/compressed means;
- remainder certificate;
- FLOP ledger.

## Frozen verdict

All cross-checks A-F pass:

**E119 TARGET-FREE ESTIMATOR HYGIENE VERIFIED.**

Any failed or unevaluable check:

**E119 TARGET-FREE HYGIENE NO-GO.**

No post-result change to the fixture seed, width/depth, forbidden-call list,
manifest blobs, tolerance, omission rule or gate is allowed. No rerun or rescue.

This receipt makes no new claim about material compression or competition
accuracy.
