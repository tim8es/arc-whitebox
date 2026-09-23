# R257 frozen protocol — repaired-harness BPK2K one-shot

Status: **FROZEN BEFORE WORKFLOW / ONE ACTIONS RUN ONLY**

Run ID: `R257-BPK2K-ONE-SHOT-20260923-A1`

## Ancestry and scope

R257 starts from reviewed R256 receipt commit
`f1e458952f2274ca375f97125ba3d181c494ad40`. It evaluates exactly the unchanged
`V25-BPK2K-BALANCED-CUMULANT-REDUCTION` candidate through the reviewed R256
typed telemetry boundary. R254 history is immutable.

Exactly one standard GitHub-hosted `ubuntu-24.04` Actions workflow and one attempt are
authorized. No retry, second workflow, tuning, second method, paid/private/holdout/full
data, R223/R244 artifact access, submission, leaderboard/canonical mutation or rank
claim is permitted.

## Runtime

Pinned:
- Python 3.11.16
- NumPy 2.4.6, wheel SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`
- FlopScope 0.12.1, wheel SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`
- WhestBench 0.16.1, wheel SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`

## Frozen parent, candidate and fixture

Parent: V25 commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
Git blob `195373a110215256b759d7c172ba8c923c62e5cc`,
SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

Fixture: `R254-MONOMIAL-PATH-254001`, seed 254001, width 1024, depth 16,
weights SHA256 `199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`,
truth SHA256 `58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

The unchanged parent executes first. Candidate construction/execution is forbidden
unless the parent gate passes. Candidate formula/source rules are exactly those frozen
by R254; R257 changes no BPK2K coefficient, term, rank, source, order-list, network rule
or target fit.

## Target-free gates — unchanged from R254

All must pass:
- final MSE ratio <= 0.95
- all-layer MSE ratio <= 0.98
- improved layers >= 12
- max per-layer degradation ratio <= 1.10
- candidate FLOPs <= parent FLOPs
- candidate residual wall time <= 1.05 * parent residual wall time + 0.005 s
- source/symmetry/finite/shape/parent checks from the frozen harness

Residual timing uses the reviewed typed
`BudgetContext.residual_wall_time_s`. Unknown/invalid timing fails closed; it is never
converted to zero.

Any parent/infra failure => terminal INCONCLUSIVE/INFRA_ERROR and no public access.
Any candidate target-free/source/cost gate failure => terminal
SCIENTIFIC_REJECT_TARGET_FREE and no public access.

## Conditional exact R209 public panel

Only after target-free GO and candidate validation GO may the workflow access the
public mini dataset. Before the candidate public run, it must verify exact equality to
the frozen R209 100-row name/order/network-id/target-SHA sequence and dataset metadata
SHA256 `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`.

Then, and only then, the same workflow may execute exactly the public mini-100 candidate
run. Frozen public gates:
- failures = 0
- adjusted score <= 7.761877568111363e-9
- improved rows >= 55
- paired mean gain > 2 descriptive SE
- mean FLOPs <= 806303721965
- max residual wall time < 0.4 s

No public submission is authorized.

## Evidence

The sole workflow must retain:
- runtime and wheel hashes
- frozen source/blob/hash checks
- fixture replay evidence
- complete target-free JSON/stdout/stderr/exit
- generated candidate source and hash
- validation evidence if reached
- exact R209 identity evidence if reached
- full raw public JSON report if reached, including all per-network rows
- extracted per-network JSON and its hash if reached
- public gate evidence if reached
- immutable workflow receipt and SHA256 map of every artifact file

Workflow conclusion and research/scientific status must be reported separately.
