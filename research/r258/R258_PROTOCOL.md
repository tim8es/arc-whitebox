# R258 frozen protocol — full-history checkout successor to terminal R257

Status: **FROZEN BEFORE WORKFLOW / ONE ACTIONS RUN ONLY**

Run ID: `R258-BPK2K-ONE-SHOT-20260923-A1`

## Successor scope

R258 starts from immutable R257 terminal commit
`c4b46ecacba1876613a6e11b678399d0b1fd83ba` and receipt SHA256
`4b28cfb1f912afc9cae0b98484b711ee8dde5145e5d0753b2977eadd21093cc1`.

R257 was UNEVALUATED because its ancestry guard ran under a depth-1 checkout and could
not resolve frozen protocol commit
`b63936a38bc0e3a6394b00f2ef1d484311aff9e4`.

R258 changes only that execution boundary: the workflow checkout uses
`actions/checkout@v4` with `fetch-depth: 0`. Candidate math, source hashes, parent,
fixture, seed, runtime versions, meter semantics, target-free gates, R209 identity and
public gates are identical to R257/R254.

Exactly one standard GitHub-hosted `ubuntu-24.04` workflow and one attempt are
authorized. No retry, second workflow, tuning, second method, paid/private/holdout/full
data, R223/R244 artifact access, submission, leaderboard/canonical mutation, R254/R257
history rewrite, or rank claim is permitted.

## Runtime

Pinned exactly as R257:
- Python 3.11.16
- NumPy 2.4.6, wheel SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`
- FlopScope 0.12.1, wheel SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`
- WhestBench 0.16.1, wheel SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`

## Frozen parent/candidate/fixture

Parent V25 commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
Git blob `195373a110215256b759d7c172ba8c923c62e5cc`,
SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

Fixture `R254-MONOMIAL-PATH-254001`, seed 254001, width 1024, depth 16,
weights SHA256 `199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`,
truth SHA256 `58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

Parent executes first. Candidate construction/execution is forbidden unless parent
passes. BPK2K formula/source rules are byte-identical to the R257 frozen source set.

## Target-free gates — identical to R257/R254

All must pass:
- final MSE ratio <= 0.95
- all-layer MSE ratio <= 0.98
- improved layers >= 12
- max per-layer degradation ratio <= 1.10
- candidate FLOPs <= parent FLOPs
- candidate residual wall time <= 1.05 * parent residual wall time + 0.005 s
- unchanged source/symmetry/finite/shape/parent checks

Residual timing uses reviewed typed `BudgetContext.residual_wall_time_s`;
unknown/invalid timing fails closed.

Parent/infra failure => terminal INCONCLUSIVE/INFRA_ERROR, no public.
Candidate target-free/source/cost failure => SCIENTIFIC_REJECT_TARGET_FREE, no public.

## Conditional exact R209 public panel — identical to R257

Only after target-free GO and candidate validation GO may the same workflow access
public mini. It must first verify exact R209 100-row name/order/network-id/target-SHA
identity and dataset metadata SHA256
`264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`.

If identity passes, exactly one public mini-100 candidate run is allowed. Gates:
- failures = 0
- adjusted score <= 7.761877568111363e-9
- improved rows >= 55
- paired mean gain > 2 descriptive SE
- mean FLOPs <= 806303721965
- max residual wall time < 0.4 s

No submission is authorized.

## Evidence

The sole workflow must retain runtime/wheel hashes, frozen source/hash checks, fixture
replay, target-free result/stdout/stderr/exit, generated candidate source/hash,
conditional validation/identity/public raw per-network evidence/public gates, workflow
receipt and SHA256 map.

Workflow conclusion and research/scientific status remain separate.
