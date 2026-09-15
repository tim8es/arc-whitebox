# E019 — terminal result

Status: **DONE / NO-GO / DROP before frozen scientific validation**

Branch: `research/e019-multimode-k4-20260915`

Protocol commit: `c4890d9776fe7fa5e63e7497d9e517c972cafc0c`.

Focused contract implementation: `56cddf5b8949c6f535819de53b03fc28277f954c`.

## TDD evidence

RED:

- workflow run `34913288436`, job `104205330034`
- expected failure: `ModuleNotFoundError: No module named 'methods.e019_multimode_k4'`

GREEN:

- workflow run `34913368299`, job `104205572698`
- `3 passed in 0.16s`

No frozen scientific validation, official scorer, holdout, tuning, subset search or sweep was run.

## Why the diagnostic was killed before measurement

The preregistered score path assumed that the eight extra live K4 modes could be accumulated with E016-class `O(n^2)` work and then consumed by the existing memoryless K4 machinery. The public source shows this assumption is false for the **feed**, which is the part that carries the accuracy gain.

F68 establishes both facts:

1. C-only regeneration works because
   `G_pre = diag(dG) + lambda*C_pre_off`
   has a special K4->K3 feed factorization. The V17 source writes
   `X3 = d(w1) G_pre d(w1) = lambda A d(w1) + P d(w1^2 dG)`,
   so the feed folds into A/P legs that are already transported; extra n^3 cost is zero.
2. The feed is essential: the upstream F68 ablation reports that dropping K4->K3 feed worsens raw MSE to about `9.23e-08`. Therefore E019 cannot be evaluated as a use-side-only correction.

For a generic E019 residual

`H = sum_m gamma_m B_m`

with full-rank modes such as `C*C`, `Sym(mu K21^T)`, `Sym(K31)`, `K22`, and `Sym(mu C)`, the feed contains

`d(w1) H d(w1)`.

Unlike `lambda*C_off`, this dense matrix is not a column scaling of the existing A/P legs. To preserve its contribution after birth, at least one additional dense source leg must be transported through subsequent layers (and a usable hub contraction adds further dense work). The eight modes may be summed before the feed, so this is a lower bound of **one** additional dense leg, not eight; it is still too expensive.

## Frozen cost lower bound

E019 was frozen to layers 8..14. A new dense feed leg born at layer 8 has six later transports, layer 9 has five, ..., layer 13 has one. This is

`6+5+4+3+2+1 = 21`

additional dense source-layer transports before counting any matching hub contraction.

At width 1024 the upstream cost ledger defines one unit as `2*n^3` FLOPs, i.e. one ordinary dense `n x n` matmul scale. Thus the absolute optimistic lower bound is about `21` units; including the necessary contraction makes the natural bound about `42` units.

E007 utilization `0.36666448` corresponds to a budget of 1024 such units. Even granting the **entire** upstream nine-mode oracle raw gain of about 1.1%, the maximum extra cost that can remain score-positive is only

`0.36666448 * (1/0.989 - 1) * 1024 = 4.176` units.

But the feed lower bound is already `21` units, >5x the break-even budget. Numerically:

- 21-unit lower bound -> extra utilization `0.0205078125`; with a full 1.1% raw gain, adjusted-score ratio vs E007 is about `1.0443` (4.4% worse).
- 42-unit transport+contraction estimate -> extra utilization `0.041015625`; with the same full oracle raw gain, score ratio is about `1.0996` (10.0% worse).

A frozen-table transfer was expected by upstream F88 to capture **less** than the 1.1% oracle ceiling, so these are optimistic bounds.

## Decision

**NO-GO / DROP E019.**

The multi-mode closure has measurable oracle error headroom but no score-positive production path in the current factorized K3 representation. Running the preregistered validation after this cost proof would be cosmetic: even a perfect transfer of the oracle gain cannot pay for the minimum dense feed state required by the mechanism.

Do not rescue E019 by dropping modes, choosing a cheap subset, restricting layers, approximating the dense feed, adding low-rank fits, changing lambda, or tuning coefficients. Any such mechanism is a new hypothesis and must receive a new experiment identifier.
