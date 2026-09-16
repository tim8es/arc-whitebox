# E091 Measured All-In Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the E091 readiness evidence gap by producing an actual flopscope-measured synthetic-only all-in deploy bill, component bills, deterministic parity, and an append-only receipt bound to the implementation/run/artifact SHA.

**Architecture:** Keep the already frozen corpus, feature map, preprocessing, and ridge lambda unchanged. Add one flopscope-only measurement helper for the existing tiny deploy path (`base + target_free_features @ B`) and extend the existing synthetic falsifier to record measured component/all-in FLOPs and utilization. No benchmark/public/scorer/holdout/full data or target is read.

**Tech Stack:** Python 3.11, NumPy, flopscope 0.12.x, pytest, GitHub Actions.

**Spec:** `research/E091_EXECUTION_PROTOCOL.md`

## Global Constraints

- Work only on `research/e091-loo-ridge-readiness-20260916`.
- Preserve committed `E091_FREEZE.json` and `E091_SYNTHETIC_CORPUS.json` byte-for-byte.
- No public-mini, scorer, holdout, full-suite, canonical, or ledger mutation.
- No tuning, sweep, rerun rescue, feature/rank/lambda change, clipping, jitter, or pseudoinverse.
- New receipt evidence is append-only.

---

### Task 1: RED test for measured deploy accounting

**Files:**
- Modify: `tests/test_e091_loo_readiness.py`

**Interfaces:**
- Consumes: frozen `build_tiny_problem()`, `full_ridge_fit()`, `PHASE2_BUDGET`.
- Produces expected API: `measure_tiny_deploy(inputs: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, dict]`.

- [ ] Add a focused test importing `measure_tiny_deploy` and asserting output parity with `tiny_relu_base(inputs) + target_free_features(inputs) @ B`, positive measured component FLOPs, exact utilization identity, component-sum parity, and bitwise-deterministic repeat.
- [ ] Push only the test change and require the E091 workflow to fail because `measure_tiny_deploy` does not yet exist.

### Task 2: GREEN minimal measurement helper

**Files:**
- Modify: `methods/e091_loo_readiness.py`

**Interfaces:**
- Produces: `measure_tiny_deploy(inputs, B)` using only flopscope primitives inside fresh `BudgetContext`s for base, features, correction dot, output add, and all-in execution.

- [ ] Implement flopscope equivalents of the already frozen tiny base and feature formulas without changing their arithmetic semantics.
- [ ] Measure component FLOPs and one all-in path; return actual `flops_used`, residual/wall times, utilization vs `2**41`, and output.
- [ ] Re-run focused tests; require all tests green.

### Task 3: Extend exactly one bounded synthetic diagnostic

**Files:**
- Modify: `scripts/run_e091_readiness_falsifier.py`

**Interfaces:**
- Consumes: `measure_tiny_deploy`, the existing frozen ridge coefficient `B`, frozen corpus/hash/freeze checks.
- Produces: artifact JSON fields `measured_deploy.component_flops`, `measured_deploy.all_in_flops`, `measured_deploy.actual_all_in_utilization`, output parity, and repeat determinism.

- [ ] Add actual measurement after the existing algebraic gates; do not alter corpus/freeze constants.
- [ ] Gate measured output parity `<=1e-12`, deterministic repeat diff `==0`, repeat FLOPs equality, and `all_in_flops == sum(component_flops)`.
- [ ] Push implementation+diagnostic change once; use the single resulting workflow run as GREEN + bounded diagnostic evidence.

### Task 4: Immutable readiness receipt

**Files:**
- Modify: `research/E091_READINESS_RECEIPT.jsonl`

**Interfaces:**
- Consumes: exact implementation HEAD, workflow run/job/artifact IDs and artifact SHA256, measured diagnostic metrics.
- Produces: one new `arc.whitebox.readiness.receipt.v3` JSONL line.

- [ ] Read terminal workflow logs/artifact and verify the exact branch HEAD and all gates.
- [ ] Append one v3 receipt line; never edit prior lines.
- [ ] Re-fetch branch/canonical and verify canonical is still `29bee3f8d23fc620b77aaed414b1b7a928af4b83` and forbidden scopes remain false.
