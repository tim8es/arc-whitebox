# ARC control update — E164 standalone clean-room AGO / E165 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E164-STANDALONE-AGO-E165-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@23fc900e2ca1cbdc77408860b8199006a8ee412d`

Status: **ACTIVE OWNER ALLOCATION / APPEND-ONLY CONTROL / FAIL-CLOSED**.

This receipt closes E162 procedurally and allocates E164/E165. It does not reopen E154/E157 or authorize public/public-mini targets, scorer/holdout/full, sweeps, rescue, reruns, canonical mutation, ledger mutation, merge, or status-only promotion.

## Immutable closed state

The following remain closed:

- **E154** — terminal K4 scientific NO-GO;
- **E157** — terminal AIK4-1 scientific NO-GO;
- **E159** — terminal one-run NO-GO;
- **E162** — terminal procedural NO-GO before science.

No K4 rescue, renamed K4 continuation, E154/E157 repair, or E162 repair/rerun is admissible.

E163 is closed unused as the obsolete E162 verifier reservation.

## E162 — terminal procedural NO-GO before science

Authoritative branch:

`research/e162-owner-ago-gauge-only-20260921@a4df31374afad377bd539560e0b1631bc5e441f7`

Frozen physical tuple:

- owner protocol commit/blob: `81debd79362dbd822391a07598aad5cb507fe331 / 32a5b809ddfc9bbcc1426f6076a7ed4362101a47`;
- candidate commit/blob: `2034e9d015c4efd5d83e1eb76907cb3d41dceb6f / 4c30094d53fc16a2523edf0e97e2a1be5a36d2fa`;
- reference commit/blob: `011474a653a4e65561011103a2ae60f9b43e9c8b / f131f8f442d5931424f548bbea39966b98168e7a`;
- tests commit/blob: `a3522c76cf7b71e355374cc6918a6061e9e5b9dc / f83d1690948fea563666a76e2ce5c85a074a1a2a`;
- falsifier commit/blob: `c3f0560ff8b0c61602038e8a1b766b5eebbeaa8b / 06cd18c2412c23a5f436909ca97b1f60d36cea95`;
- workflow commit/blob: `24495dcad0e84f3b3247ca1797876efd380eb0cd / 71a7a161dea758490256519079aaaf49fcd0dea8`;
- arm/executed head: `177ce09b6649a7db9c4b4dd97da48a4272b66fdc`;
- run/job/attempt: `35603072598 / 106343552228 / 1`;
- artifact: `10639349777`, `e162-ago`;
- artifact SHA256: `b4ec57438f8b36e856f3e620dc50fcffbee6119340d23250ac32fa652f385810`;
- decision: `E162_TERMINAL_NO_GO_CLOSE_AGO`.

Failure class:

`ENVIRONMENT_INSTALL_FAILURE_BEFORE_SCIENCE`.

The sole authorized run failed at:

`python -m pip install -e .`

because repository root contains neither `setup.py` nor `pyproject.toml`.

Therefore syntax checks, focused tests, target-free falsifier, gauge identities, parent-vs-AGO MSE, deterministic replay and executable cost reconciliation were not scientifically evaluated.

**No E162 rerun, packaging repair, workflow repair, dependency-path repair, rescue, or reinterpretation.**

## E164 namespace checkpoint

Fresh branch search at intake finds:

`research/e164-cleanroom-ago-20260921@7a0034088ebbffbd74b441e1797c272e9d33cbff`.

The branch currently has **no E164 delta/files relative to its branch point** and no E164 Actions run is observed. Treat it as an empty namespace reservation only, not protocol/science/progress.

E165: no branch observed and no Actions run observed.

## E164 — sole active scientific owner

Allocate:

**E164 — separate clean-room Angular Gauge Only (AGO), standalone execution.**

E164 is the only active scientific owner under this receipt.

E164 is a new experiment identity, not an E162 rescue. It may reuse the mathematical H160/AGO hypothesis and cite E160 support, but it must not copy, import, patch, execute, or depend on E162 candidate/reference/test/falsifier/workflow code or E162 run artifacts.

### Mechanism boundary

The scientific mechanism remains H160 AGO only:

1. one exact K1/K2 Gaussian-to-angular gauge conversion at one protocol-frozen first activation state:
   - `m_A=m_G/a1`;
   - `C_A=C_G-(a1^-2-1)m_Gm_G^T`;
2. identical frozen non-K4 parent closure thereafter;
3. exact final radial mean readout `m_G_out=a1*m_A_out`.

Forbidden:

- K4 tensor/factor/state;
- D4/D22;
- scalar `c4`;
- recurrent K4;
- K4-derived Wick correction;
- E154/E157 candidate/artifact reuse;
- E159 recurrent-K4 path;
- E162 implementation/workflow/reference/test/falsifier reuse;
- candidate-specific parent refit/rerank/retuning.

### Standalone execution contract

E164 must be independently runnable from a clean repository checkout without installing the repository as a Python package.

The frozen workflow/runner must:

1. **not** execute `pip install -e .`, `pip install .`, `python setup.py`, or depend on repository packaging metadata;
2. invoke the E164 owner runner directly as a standalone path/module whose imports are limited to explicitly frozen runtime dependencies and E164-local clean-room code;
3. not import `methods/e162_ago.py`, `methods/e162_reference.py`, `scripts/e162_ago_falsifier.py`, E162 tests, or E162 artifacts;
4. perform a pre-science standalone import/compile/self-check inside the same sole physical run before scientific evaluation;
5. record the exact interpreter and dependency versions used;
6. fail closed if any required import/dependency/environment check fails.

An environment or dependency failure still consumes E164's one physical run. No repair/rerun.

### Mandatory protocol-first freeze

Before implementation/workflow execution, E164's first scientific owner commit must freeze:

1. exact clean branch point/parent and E160 support provenance;
2. explicit clean-room separation from E162 code/artifacts;
3. exact standalone runtime/dependency contract;
4. exact K4-free parent mechanism;
5. exact AGO transform location and final radial readout;
6. deterministic synthetic/analytic target-free fixtures and seeds;
7. independent exact-small/analytic reference capable of falsifying AGO;
8. exact gauge identity/parity gates with numerical thresholds;
9. one frozen target-free scientific improvement/error gate;
10. a computable target-free residual/error certificate with frozen threshold;
11. complete all-in parent+gauge production cost, including parent arithmetic, gauge conversion/readout, diagnostics/helpers/RNG/normalization/materialization/certificate/reference/setup and every charged operation class;
12. combined production cost `<=0.135 * 2^41` FLOPs;
13. deterministic replay;
14. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
15. terminal kill rule;
16. exactly one physical target-free owner run;
17. no sweep, tuning, rescue, rerun, retry, seed/fixture/threshold/parent/source/mechanism substitution or post-result repair.

Public benchmark numbers in E160 remain provenance only and may not be E164 fitting data, thresholds, fixtures, references, or scientific evidence.

### One-run authorization

After a valid protocol-first freeze, E164 may implement its own minimum standalone clean-room parent/candidate/reference/tests/falsifier/workflow and execute **exactly one** target-free physical scientific run.

Any failed or unevaluable mandatory gate — including standalone import/dependency/environment failure — consumes the one-run authorization and closes E164 absent later explicit control.

No second run.

## E165 — sole independent verifier

E165 is reserved as exactly one independent review-only verifier for E164.

Do not create or execute E165 before a complete admissible E164 owner tuple exists.

After the sole E164 physical run, freeze:

- E164 branch/experiment ID;
- protocol SHA/blob;
- clean branch point and E160 support provenance;
- standalone runtime/dependency manifest;
- parent/candidate/reference/test/falsifier/workflow SHAs/blobs;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner result/terminal receipt SHA;
- E162-separation evidence;
- no-K4 evidence;
- gauge identity/parity metrics;
- target-free scientific/certificate metrics;
- complete all-in parent+gauge cost;
- deterministic replay;
- target/public firewall evidence.

Only if that tuple is complete and survives all owner gates may E165 execute one independent verification.

E165 must independently verify/recompute:

1. protocol-first ancestry and experiment identity;
2. clean-room separation from E162 and closed K4 lanes;
3. standalone execution without repository-package installation;
4. exact H160 K1/K2 gauge algebra and radial readout;
5. explicit absence of K4/D4/D22/c4/recurrent-K4;
6. exact-small/analytic reference and scientific gate;
7. target-free residual/error certificate;
8. complete parent+gauge all-in cost;
9. deterministic replay;
10. zero public/public-mini target/scorer/holdout/full/submission access;
11. frozen run/artifact provenance and no post-result changes.

E165 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, or publicly validate E164.

Exactly one verifier execution/receipt. No nested/second verifier.

Premature E165 activity fails closed.

## Hard rejection rules

Reject and fail closed:

- E162 rerun/repair/rescue;
- any E154/E157/K4 rescue or renamed K4 continuation;
- any K4 state/correction in E164;
- reuse/patching/import of E162 scientific implementation as E164;
- repository-package installation as a prerequisite for E164 standalone execution;
- public/public-mini benchmark target scientific access;
- benchmark-target scoring/evaluation as an owner gate;
- official scorer, holdout/full or submission access;
- target fitting;
- rank/order/seed/fixture/threshold/basis/certificate/parent/source/mechanism sweeps;
- owner rerun/retry or post-result repair;
- duplicate/colliding experiment IDs;
- speculative status or ledger rows;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Single next gate

Wait for one **protocol-first E164 standalone clean-room AGO** owner freeze on the already reserved empty E164 branch.

After exactly one complete admissible target-free E164 physical result, dispatch exactly one independent verifier under **E165**.
