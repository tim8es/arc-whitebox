# ARC White-Box Research Project Design

## Goal

Build a disciplined, reproducible research project for ARC White-Box Estimation Challenge 2026 Phase 2 that can spend at most $100 on experiments and prioritize methods with measurable expected-value rather than speculative complexity.

## Success criteria

The first research cycle succeeds if it produces at least one of:

1. a reproducible estimator that improves adjusted final-layer MSE by >=15% over the strongest baseline we can faithfully reproduce at comparable compute; or
2. a validated algorithmic contribution with a clearly measured new result worth submitting for the contribution prize; or
3. a strong negative result that closes a meaningful method family cheaply enough to redirect the remaining budget.

A leaderboard submission is not itself success unless the result is reproducible locally.

## Architecture

The project has four layers:

1. **Official harness layer** — pinned `whestbench`/`flopscope`, exact Phase 2 dataset revision, contract validation and packaging.
2. **Estimator layer** — a single submission-compatible `Estimator` entry point. Experimental methods remain outside the production entry point until promoted.
3. **Research layer** — hypotheses, public frontier notes, experiment ledger, preregistered acceptance criteria and negative-result archive.
4. **Verification layer** — CI contract checks plus official scorer runs on recorded development/holdout subsets.

## Research strategy

Prioritize network-dependent hybrid estimation rather than static cubature or blind closure refinement.

Order of attack:

1. reproduce the official covariance baseline and a strong public sampling baseline;
2. implement residual/control-variate estimation around the deterministic predictor;
3. test adaptive analytic/sampling blending using cheap network-derived features;
4. test low-cost higher-moment constraints on whitened antithetic sampling;
5. only then investigate low-rank QMC or a third-cumulant predictor as a stronger control variate.

## Budget policy

Hard cap: **$100**.

- $20 frontier mapping and cheap screening
- $25 broad experiments
- $35 replication/ablation of the best one or two branches
- $20 reserve

A branch may enter the $35 replication pool only after a measured gain on the development set. The reserve is not spent on rescuing a method with no positive signal.

## Evidence policy

Every claim must be tagged as one of:

- **Measured** — produced by the official/local scorer and stored in the ledger.
- **Derived** — mathematically follows from measured values or documented rules.
- **Hypothesis** — not yet experimentally validated.

Hyperparameters and decision rules are frozen before the holdout run. Failed experiments stay in the ledger.

## Constraints

- Phase 2 architecture: width 1024, depth 16.
- Per-MLP budget: `2**41` FLOPs.
- Use the explicit `v2-phase2` dataset revision.
- Grading is CPU-only with no network access.
- Phase 2 code restrictions differ from Phase 1; final submission must be checked against the current official rules.
- Primary optimization target is final-layer MSE under the challenge's compute multiplier.

## Deliverables

- reproducible baseline(s)
- experiment ledger with cost and evidence
- ranked hypothesis backlog
- one submission-ready best estimator
- write-up-ready evidence package if an algorithmic contribution emerges
