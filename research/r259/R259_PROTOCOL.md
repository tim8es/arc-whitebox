# R259 frozen protocol — fixture-manifest path successor to terminal R258

Status: **FROZEN / UNARMED / COORDINATOR INSPECTION REQUIRED BEFORE TRIGGER**

Run ID: `R259-BPK2K-ONE-SHOT-20260923-A1`

## Successor scope

R259 starts from immutable R258 terminal commit
`d99a52d0d3cf0f1c946de78173588bc258e74b54` and receipt SHA256
`60e0ed2e62a400c5738a1da63c88b59c47352c5e872ec8f1e7935f60091472ef`.

R258 proved full-history checkout, ancestry/source hashes, runtime/wheels, pinned V25
source, and fixture generation/replay. It failed only because its workflow expected
`R254_RUNTIME_FIXTURE_MANIFEST.json`, while immutable generator
`research/r254/r254_fixture.py` blob
`141466b6c4aae6cc61fe086860dc0766a08d6968` line 102 writes exactly
`R254_FIXTURE_RUNTIME_MANIFEST.json`.

R259 makes only two execution-infrastructure changes:
1. workflow expectation is corrected to `R254_FIXTURE_RUNTIME_MANIFEST.json`;
2. before setup/science, a static preflight parses the immutable generator source and
   fails unless the sole emitted manifest filename equals the workflow expectation.

No fixture generator, BPK2K source/math, V25 parent, telemetry helper, hashes, seeds,
thresholds, meter semantics, R209 data, or public gate is changed.

The branch must remain **unarmed** until a separate coordinator instruction after
inspection of this protocol/workflow/preflight.

## Runtime and frozen science

Identical to R258:
- standard free `ubuntu-24.04`
- full history checkout, `fetch-depth: 0`
- Python 3.11.16
- NumPy 2.4.6 SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`
- FlopScope 0.12.1 SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`
- WhestBench 0.16.1 SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`

Parent V25 and exact fixture remain unchanged:
seed 254001; weights SHA256
`199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`;
truth SHA256
`58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

Parent must execute first. BPK2K may be constructed/executed only after exact fixture
replay and parent PASS.

## Target-free gates — byte-for-byte semantics unchanged

- final MSE ratio <= 0.95
- all-layer MSE ratio <= 0.98
- improved layers >= 12
- max per-layer degradation ratio <= 1.10
- candidate FLOPs <= parent FLOPs
- candidate residual <= 1.05 * parent + 0.005 s
- unchanged source/symmetry/finite/shape/parent checks
- missing/invalid timing fails closed

Any infra/parent failure stops before public. Candidate target-free failure is
SCIENTIFIC_REJECT_TARGET_FREE and skips public.

## Conditional R209 mini-100 — unchanged

Only target-free + validation GO permits exact R209 identity check and public mini-100.
The same frozen identity/hash and public gates apply:
failures=0; adjusted <=7.761877568111363e-9; >=55 improved rows;
paired gain >2 descriptive SE; mean FLOPs <=806303721965; max residual <0.4 s.

No submission is authorized.

## One-shot discipline

Exactly one path-filtered arm push may trigger exactly one workflow/attempt after
coordinator approval. No retry/second workflow, tuning, paid/private/holdout/full,
R223/R244 artifact access, submission, leaderboard/canonical edit, or history rewrite.
