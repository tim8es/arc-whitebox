# arc-whitebox

Research project for the **ARC White-Box Estimation Challenge 2026 — Phase 2**.

## Objective

Build a FLOP-efficient estimator that predicts per-neuron expected post-ReLU activations of a random ReLU MLP under standard-normal input, with primary focus on minimizing **final-layer MSE** under the official compute model.

Phase 2 target architecture:
- width: 1024
- depth: 16
- per-MLP budget: `2**41` FLOPs
- CPU-only grading

## Research budget

Hard experimental budget: **$100 total**.

The project uses staged spending. No expensive research branch should consume the reserve until it demonstrates a reproducible local gain over the current baseline.

Suggested allocation:
- $20 — literature/frontier mapping and cheap hypothesis screening
- $25 — broad local experiments
- $35 — replication + ablations on the best 1–2 methods
- $20 — reserve for final optimization/submission iteration

## Operating rule

Every research idea must become a falsifiable experiment:

`hypothesis -> implementation -> benchmark -> compare -> ablate -> keep/drop`

No method is promoted on theoretical plausibility alone.

## Current priority tracks

1. Adaptive/network-dependent sampling
2. Control variates and residual estimation
3. Hybrid covariance/moment propagation + sampling correction
4. Antithetic / quasi-Monte-Carlo sampling
5. Adaptive allocation of compute by layer/network difficulty
6. Higher-order or mixture moment closure only when justified by measured residual structure

## Repository plan

- `estimator.py` — submission-compatible estimator entry point
- `examples/` — selected official baselines for local comparison
- `research/HYPOTHESES.md` — ranked research hypotheses
- `research/ledger.csv` — experiment ledger
- `research/FRONTIER.md` — public-state-of-the-art notes and known dead ends
- `scripts/` — repeatable evaluation helpers

## Rule

Before submission, always validate against the current official Phase 2 starter kit and rules. Phase 2 code restrictions differ from Phase 1.
