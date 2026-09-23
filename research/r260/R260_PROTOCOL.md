# R260 frozen protocol — fixture replay-schema successor to terminal R259

Status: **FROZEN / UNARMED / COORDINATOR INSPECTION REQUIRED BEFORE TRIGGER**

Run ID: `R260-BPK2K-ONE-SHOT-20260923-A1`

## Successor scope

R260 starts from immutable R259 terminal commit
`be1f8e92dbf3a2adb4d5dcd75c2ff345454ac47b` and receipt SHA256
`dd1c5c0d9941941cb00153e076c09cb51743966f0486579de85ac70f97af1fe1`.

R259 proved full-history checkout, source/hash pins, static manifest-path preflight,
runtime/wheel pins, V25 source hash, and fixture generation. It failed only because its
workflow asserted a nonexistent nested field
`independent_replay.all_layer_hashes_equal`.

The immutable R254 generator and sealed R259 runtime manifest define the actual schema:
- top-level `replay_equal = true`;
- top-level `layer_sha256` has exactly 16 hashes;
- `independent_replay.layer_sha256` has exactly 16 hashes and equals the top-level list;
- top-level and nested `weights_concat_sha256` both equal the frozen fixture hash;
- top-level and nested `truth_sha256` both equal the frozen truth hash;
- `independent_replay` contains exactly `layer_sha256`,
  `weights_concat_sha256`, and `truth_sha256`;
- no `all_layer_hashes_equal` field exists or is expected.

R260 changes only this workflow-side replay-schema validation. Candidate math, parent,
fixture generator/seed/hashes, R256 telemetry, runtime pins, target-free gates and
conditional R209 public gates remain unchanged.

The branch must remain **unarmed** until a separate coordinator inspection/approval.

## Static pre-arm schema verification

Committed preflight:
`research/r260/r260_fixture_schema_preflight.py`.

It parses the immutable generator source and validates the sealed R259 runtime manifest
against the exact schema above. The workflow runs the same preflight before setup/science
against the sealed manifest and again after generating the fresh R260 runtime manifest,
before parent execution.

Any schema/hash mismatch is fail-closed and stops before parent.

## Runtime and science — unchanged

- standard free `ubuntu-24.04`;
- full history checkout, `fetch-depth: 0`;
- Python 3.11.16;
- NumPy 2.4.6 SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`;
- FlopScope 0.12.1 SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
- WhestBench 0.16.1 SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`.

Pinned V25 parent and exact fixture are unchanged:
seed 254001; weights SHA256
`199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`; truth SHA256
`58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

Parent executes first. BPK2K construction/execution is allowed only after exact replay
schema/hash validation and parent PASS.

## Target-free gates — unchanged from R254/R259

All must pass:
- final MSE ratio <= 0.95
- all-layer MSE ratio <= 0.98
- improved layers >= 12
- max per-layer degradation <= 1.10
- candidate FLOPs <= parent FLOPs
- candidate residual <= 1.05 * parent + 0.005 s
- unchanged source/symmetry/finite/shape/parent checks
- unknown/invalid residual timing fails closed

Any pre-parent/parent infrastructure failure stops before public. Candidate scientific
gate failure is terminal target-free rejection and also skips public.

## Conditional R209 mini-100 — unchanged

Only target-free + validation GO permits exact R209 identity validation and public
mini-100 in the same workflow. Frozen public gates remain:
failures=0; adjusted <=7.761877568111363e-9; >=55 improved rows;
paired gain >2 descriptive SE; mean FLOPs <=806303721965; max residual <0.4 s.

No submission is authorized.

## One-shot discipline

Exactly one path-filtered arm push may trigger exactly one standard/free Actions
workflow attempt **only after separate coordinator approval**. No retry/second workflow,
tuning, paid/private/holdout/full, R223/R244 artifact access, submission,
leaderboard/canonical edit, or history rewrite.
