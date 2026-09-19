# ARC White-Box Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish reproducible Phase 2 baselines, then test residual control-variate estimation under a $100 research budget.

**Architecture:** Keep `estimator.py` submission-compatible while research implementations live in focused modules. All promotion decisions are driven by the official scorer and recorded in `research/ledger.csv`.

**Tech Stack:** Python 3.10+, `whestbench 0.16.x`, `flopscope 0.12.x`, NumPy-compatible FLOP-metered operations, pytest, ruff.

**Spec:** `docs/superpowers/specs/2026-09-09-arc-whitebox-research-design.md`

## Global Constraints

- Hard external research budget: $100.
- Phase 2 MLP shape: width 1024, depth 16.
- Per-MLP compute budget: `2**41` FLOPs.
- Dataset revision must be `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`.
- Final estimator must pass `whest validate` and Phase 2 restrictions.
- Promote methods only after a preregistered holdout result.

---

### Task 1: Reproduce the official harness and covariance baseline

**Files:**
- Create: `baselines/covariance_propagation.py`
- Create: `tests/test_baseline_contract.py`
- Modify: `research/ledger.csv`

**Interfaces:**
- Consumes: official `MLP`, `BaseEstimator`, and FLOP budget contract.
- Produces: `CovarianceEstimator(BaseEstimator)` returning `(mlp.depth, mlp.width)` means.

- [ ] **Step 1: Write the contract test**

```python
from baselines.covariance_propagation import CovarianceEstimator


def test_covariance_estimator_is_submission_estimator():
    assert hasattr(CovarianceEstimator, "predict")
```

- [ ] **Step 2: Run the test and verify RED**

Run: `pytest tests/test_baseline_contract.py -v`

Expected: import failure because `baselines/covariance_propagation.py` does not exist.

- [ ] **Step 3: Vendor the official Phase 2 covariance example**

Copy the current MIT-licensed implementation from `AIcrowd/whest-starterkit/examples/03_covariance_propagation.py`, rename its class to `CovarianceEstimator`, and add an attribution header with the upstream URL and commit/blob SHA used.

- [ ] **Step 4: Verify GREEN and official contract**

Run:

```bash
pytest tests/test_baseline_contract.py -v
whest validate --estimator baselines/covariance_propagation.py
```

Expected: PASS.

- [ ] **Step 5: Score on Phase 2 mini**

Run:

```bash
whest run --estimator baselines/covariance_propagation.py \
  --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 \
  --split mini --runner local
```

Record raw MSE, adjusted score, utilization and failures as `E000`.

---

### Task 2: Build a reproducible whitened-antithetic sampling baseline

**Files:**
- Create: `methods/whitened_antithetic.py`
- Create: `tests/test_whitened_antithetic.py`
- Modify: `research/ledger.csv`

**Interfaces:**
- Produces: `WhitenedAntitheticEstimator(BaseEstimator)`.

- [ ] **Step 1: Write a deterministic seed test**

```python
def test_same_mlp_seed_produces_same_prediction(sample_mlp):
    est = WhitenedAntitheticEstimator()
    a = est.predict(sample_mlp, 2**41)
    b = est.predict(sample_mlp, 2**41)
    assert (a == b).all()
```

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_whitened_antithetic.py -v`.

Expected: estimator import failure.

- [ ] **Step 3: Implement the minimal sampler**

Generate half-samples with the per-MLP seeded RNG, whiten them so empirical covariance is identity, append antithetic negatives, propagate the paired batch through all layers, and return layerwise sample means. Select sample count so measured utilization stays near but below the score floor where possible.

- [ ] **Step 4: Verify GREEN and contract**

Run tests plus `whest validate --estimator methods/whitened_antithetic.py`.

- [ ] **Step 5: Score and freeze baseline**

Run on Phase 2 mini, record metrics and the exact sample count in the ledger. Do not tune against the holdout split.

---

### Task 3: Test residual control-variate estimation

**Files:**
- Create: `methods/residual_control_variate.py`
- Create: `tests/test_control_variate.py`
- Modify: `research/ledger.csv`

**Interfaces:**
- Consumes: deterministic covariance predictions and whitened-antithetic samples.
- Produces: `ResidualControlVariateEstimator(BaseEstimator)`.

- [ ] **Step 1: Write the identity-limit test**

For a zero correction coefficient, assert the method exactly returns the deterministic branch.

```python
def test_zero_residual_weight_equals_deterministic_branch(sample_mlp):
    hybrid = ResidualControlVariateEstimator(residual_weight=0.0)
    expected = CovarianceEstimator().predict(sample_mlp, 2**41)
    actual = hybrid.predict(sample_mlp, 2**41)
    assert_allclose(actual, expected)
```

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_control_variate.py -v`.

Expected: missing implementation.

- [ ] **Step 3: Implement residual estimation**

Compute a deterministic analytic prediction, use paired/whitened trajectories to estimate a correction correlated with the deterministic error, and combine them without exceeding the official compute accounting.

- [ ] **Step 4: Development-set sweep**

Evaluate only a small preregistered grid of residual weights or regression rules. Record every attempted setting.

- [ ] **Step 5: Promotion gate**

Promote only if development MSE improves by >=15% at comparable adjusted compute. Otherwise mark `E001=DROP` and move to Task 4 without consuming replication budget.

---

### Task 4: Preregister and run the holdout

**Files:**
- Create: `research/HOLDOUT_PROTOCOL.md`
- Modify: `research/ledger.csv`

- [ ] **Step 1: Freeze the candidate**

Record commit SHA, estimator path, all hyperparameters, dataset split/seed policy and acceptance criterion before execution.

- [ ] **Step 2: Run the holdout once**

Use the official scorer. No parameter changes after seeing holdout metrics.

- [ ] **Step 3: Decide**

KEEP if >=15% MSE reduction with no material failure/tail regression; otherwise DROP or REWORK with a new experiment ID.

---

### Task 5: Package the strongest lawful submission

**Files:**
- Modify: `estimator.py`
- Create: `research/SUBMISSION_EVIDENCE.md`

- [ ] **Step 1: Write a parity test**

Assert `estimator.Estimator` matches the promoted research implementation on a deterministic smoke MLP.

- [ ] **Step 2: Verify RED before promotion**

The parity test must fail while `estimator.py` still contains the zero baseline.

- [ ] **Step 3: Promote only the validated implementation**

Keep the production entry point minimal and remove research-only instrumentation.

- [ ] **Step 4: Validate and package**

Run:

```bash
ruff check .
pytest -q
whest validate --estimator estimator.py
whest package --estimator estimator.py
```

Expected: all checks pass and a valid package is produced.

- [ ] **Step 5: Record evidence**

Store exact commit SHA, scorer metrics, FLOP utilization, package validation result, known limitations and AI-use disclosure notes in `research/SUBMISSION_EVIDENCE.md`.
