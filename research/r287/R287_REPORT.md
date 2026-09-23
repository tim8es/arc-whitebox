# R287 — Phase-2 free public-runner audit

Status: **WAITING_INPUT**

Job: R287  
Owner: `phase2-free-runner-audit`  
Run: `R287-free-runner-audit-20260923`

## Question

Can one future public-development V25 residual-capture job use the existing GitHub-hosted runner path with **zero incremental charge**, while preserving the pinned Python/WhestBench/FlopScope stack, public mini dataset, 8 GB scorer process cap, timeout constraints, and the R278/R282 capture seam?

No Actions were triggered and no packages/data were downloaded or installed in this audit.

## Exact repository/runtime evidence

Repository metadata for `tim8es/arc-whitebox` currently reports:

- `private=false`
- `visibility=public`
- repository not archived/disabled.

### R209 successful V25 path

Pinned workflow blob: `4dea7107d9c7677659898e661b6ac5c306c68f7b` at run head `dff3dd65e9d2210e02418cca99e05556f6bf2c75`.

The workflow uses:

- `runs-on: ubuntu-latest`
- `timeout-minutes: 330`
- `actions/setup-python@v5`, `python-version: "3.11"`
- public dataset `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- `--split mini --streaming --n-mlps 100`
- `--runner local`
- `--flop-budget 2199023255552`
- `--wall-time-limit 120`
- `--residual-wall-time-limit 0.4`
- `--max-threads 1`.

R209 archive evidence records the observed stack:

- Python `3.11.16`
- NumPy `2.4.6`
- WhestBench `0.16.1`
- FlopScope `0.12.1+np2.4.6`.

Actions job `106167659234` completed successfully. The live jobs API reports label `ubuntu-latest`, runner group `GitHub Actions`, runner name `GitHub Actions 1000004666`; it ran from 2026-09-20T23:22:09Z to 2026-09-21T00:26:31Z (~64m22s), well below the 330-minute workflow timeout.

### R223 public standard-runner confirmation

R223 attempt 6 workflow blob `d24e3f63e8ce447188868846e9b3e4ef755b395e` uses:

- `runs-on: ubuntu-24.04`
- `timeout-minutes: 100`
- explicit `numpy==2.4.6`, `whestbench==0.16.1`, `flopscope>=0.12.1,<0.13.0`
- the same public mini streaming path and `--runner local`.

Job `107020553482` is reported by GitHub as label `ubuntu-24.04`, runner group `GitHub Actions`, runner name `GitHub Actions 1000005130`, and completed in ~58m47s.

For a future exact Python 3.11 capture, the safe recipe is therefore to retain R223's explicit package pins **and** R209's explicit `actions/setup-python@v5 python-version: "3.11"`; do not rely on the image's default Python.

## Official GitHub runner and pricing facts

First-party sources:

- GitHub Actions billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- GitHub-hosted runners reference: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Choosing the runner for a job: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- Workflow syntax / timeout: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Included usage by plan: https://docs.github.com/en/billing/reference/product-usage-included

GitHub documents that **standard GitHub-hosted runners are free and unlimited for public repositories**. It separately states that larger runners are charged even for public repositories.

For public repositories, standard `ubuntu-latest` and `ubuntu-24.04` are documented as x64 Linux VMs with:

- 4 CPU
- 16 GB RAM
- 14 GB SSD.

The exact observed run labels and `GitHub Actions` runner group match the standard-hosted path; no larger-runner label/group is present.

Therefore **runner compute minutes for this exact public standard-runner class are documented at $0 incremental charge**. Private-repository monthly minute quotas do not apply to this public standard-runner use.

## 8 GB and timeout feasibility

WhestBench 0.16.1 source commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`, `scoring.py` blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`, defines:

- participant process memory limit: `8192 MB`
- predict wall limit: `120 s`
- residual wall limit: `0.4 s`.

The documented public Ubuntu VM has 16 GB RAM, so the scorer's 8 GB participant cap fits inside the host VM while leaving host-side headroom. This is also empirically supported by successful R209/R223 100-network public-mini runs on standard GitHub-hosted runners.

GitHub's workflow syntax documents a job timeout default of 360 minutes. R209 explicitly used 330 minutes and completed V25 in ~64 minutes; R223 used 100 minutes and completed in ~59 minutes. The future capture seam is runner-side after estimator prediction/failure semantics and does not require extending participant predict limits.

The dataset path uses `--streaming`; the successful runs therefore establish that the public Mini can be consumed on this runner path without staging the full ~6.9 GB prepared dataset onto the 14 GB runner disk.

## Capture storage size

R282's minimally sufficient coordinate payload is either one signed residual `float32[1024]` per network or both final prediction and target vectors.

For 100 networks:

- residual-only raw payload: `100 * 1024 * 4 = 409,600` bytes (~0.391 MiB);
- prediction + target raw payload: `100 * 2 * 1024 * 4 = 819,200` bytes (~0.781 MiB);

plus small identity/hash metadata.

This is negligible relative to runner SSD capacity. It is **not**, however, enough to prove zero billing for durable Actions artifact storage.

## Account-specific unknown that blocks a zero-total-cost proof

GitHub's billing documentation treats Actions artifact storage separately from public standard-runner minutes. Artifact storage has a plan-dependent included allowance (at least 500 MB on GitHub Free; larger on higher plans), is shared with GitHub Packages storage, and usage above the included amount is billable. If no valid payment method is available, over-quota usage can instead be blocked.

The allowed public repository evidence does **not** reveal:

1. repository-owner `tim8es` current GitHub plan;
2. current account-wide shared Actions-artifact + GitHub-Packages storage usage/accrual;
3. remaining included storage allowance at the intended execution time;
4. any account budget / stop-usage setting that would block overage rather than bill it.

Existing public runs prove Actions execution eligibility historically, but they do not prove the current billing/storage state.

Because a faithful durable residual capture would normally create a new retained artifact, **zero incremental total charge cannot be proven from public evidence alone**.

## Exact missing input

Coordinator/account owner must provide one current billing-dashboard fact immediately before authorization:

> **Remaining included GitHub Actions shared artifact/GitHub Packages storage allowance for owner `tim8es` is at least 1 MiB, with no metered storage overage already active for that pool.**

Equivalent evidence is acceptable if it proves that the proposed capture artifact will remain entirely inside the included storage allowance. No payment method details need to be disclosed.

If the coordinator instead approves a durable capture path that does not consume metered Actions artifact storage, that path must be separately audited before execution.

## Preflight recipe once the missing fact is supplied

No execution is authorized by R287. The compatible future job should use:

1. public `tim8es/arc-whitebox`;
2. standard `ubuntu-24.04` (or pinned standard Ubuntu label), never a larger runner;
3. `actions/setup-python@v5` with Python 3.11;
4. NumPy 2.4.6, WhestBench 0.16.1, FlopScope 0.12.1;
5. exact V25 source blob `195373a110215256b759d7c172ba8c923c62e5cc`;
6. public `v2-phase2` Mini, streaming, 100 networks, `--runner local`;
7. unchanged 8 GB / 120 s / 0.4 s scoring constraints;
8. R278/R282 capture seam after failure-zeroing and `pred_np/final_pred/final_target` binding, before MSE aggregation;
9. a hashed residual capture under the already-frozen R278 split/fit rule.

## Verdict

**WAITING_INPUT.**

- Compute-minute cost on the exact public standard-runner class: **documented $0**.
- Hardware/timeout/pinned-stack feasibility: **supported by docs and prior successful exact-panel runs**.
- Complete zero-incremental-cost durable capture: **not proven**, solely because current account-wide artifact-storage allowance/billing state is not observable from the permitted public evidence.
