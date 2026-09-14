# arc-whitebox

Research project for the **ARC White-Box Estimation Challenge 2026 — Phase 2**.

## Objective

Build a FLOP-efficient estimator that predicts per-neuron expected post-ReLU activations of a random ReLU MLP under standard-normal input, with primary focus on minimizing **final-layer MSE** under the official compute model.

Phase 2 target architecture:
- width: 1024
- depth: 16
- per-MLP budget: `2**41` FLOPs
- CPU-only grading
- public dataset revision: `v2-phase2`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . ruff pytest

ruff check .
whest validate --estimator estimator.py
bash scripts/eval_phase2.sh mini local
```

For grader-like process isolation:

```bash
bash scripts/eval_phase2.sh mini subprocess
```

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

1. Residual/control-variate estimation
2. Adaptive/network-dependent analytic/sampling blending
3. Whitened antithetic sampling with higher-moment correction
4. Network-dependent low-rank QMC/cubature
5. Stronger deterministic predictors as control variates

## Repository map

- `estimator.py` — submission-compatible estimator entry point
- `research/HYPOTHESES.md` — ranked research hypotheses
- `research/ledger.csv` — experiment ledger and cost gates
- `research/FRONTIER.md` — public state of the art and known dead ends
- `scripts/eval_phase2.sh` — repeatable official Phase 2 evaluation path
- `docs/superpowers/specs/` — project design
- `docs/superpowers/plans/` — executable research plan

## Current gate

1. Reproduce official Phase 2 covariance baseline.
2. Reproduce whitened-antithetic sampling.
3. Test residual control variates.
4. Spend replication budget only after a measured positive signal.

## Rule

Before submission, always validate against the current official Phase 2 starter kit and rules. Phase 2 code restrictions differ from Phase 1.
