# E112 result — exact activation-mask message passing is structurally inadmissible

Idempotency key: `ARC-E112-EXACT-MASK-MESSAGE-TREEWIDTH-20260919`

Decision: **TERMINAL STRUCTURAL NO-GO / DROP**

## Mechanism

E112 tested a genuinely non-Gaussian estimator family rather than another control variate or Gaussian moment plug-in.

The candidate represents each ReLU layer by its binary activation mask and propagates exact cone probabilities / moments with finite-state sum-product or junction-tree messages.

For a dense next-layer row,

`z_j = sum_i W[j,i] h_i`,

the exact sign/moment factor depends on every previous mask bit. Hence the mask-variable primal graph is `K_n`, with treewidth `n-1`.

If the first square layer is full rank, `x -> W_1 x` is onto, so every preactivation orthant is reachable and all `2^n` first-layer masks are feasible. Thus infeasible-state pruning does not remove the first exponential separator.

This lower bound applies specifically to the frozen explicit finite-state mask-message estimator family. It is not a claim that every symbolic activation-cone algorithm must enumerate all masks.

## Frozen exact falsifier

Widths `2..8`, depth `4`, zero bias, dense He-Gaussian square weights, one frozen PCG64 seed per width.

For every width and every layer:

- support density = `1.0`;
- numeric rank = `n`;
- primal graph = complete;
- exact treewidth = `n-1`.

Measured law:

| width | exact treewidth | bag bits | explicit states |
|---:|---:|---:|---:|
| 2 | 1 | 2 | 4 |
| 3 | 2 | 3 | 8 |
| 4 | 3 | 4 | 16 |
| 5 | 4 | 5 | 32 |
| 6 | 5 | 6 | 64 |
| 7 | 6 | 7 | 128 |
| 8 | 7 | 8 | 256 |

The exact treewidth implementation was independently tested on empty, path, star, cycle, and clique graphs.

Focused tests: `5 passed in 3.53s`.

Deterministic replay is bitwise identical:
`28b4ef994001dda695defea0652d03894dd76f1de46d439129486d0817192a6b`.

## Production admission lower bound

Production width is `1024`.

For a dense layer:

- exact primal treewidth = `1023`;
- required binary bag size = `1024`;
- explicit message table = `2^1024 ~= 10^308.2547` entries.

Competition budget:

- total budget = `2^41 = 2,199,023,255,552` FLOPs;
- utilization cap = `0.13`;
- allowed candidate FLOPs = `285,873,023,221.76`.

Even granting the physically impossible optimistic lower bound of exactly **one FLOP per table entry**, the budget can support at most

`floor(41 + log2(0.13)) = 38`

binary bag bits.

E112 needs `1024`.

The one-FLOP/state utilization lower bound has

- `log2(util) = 983`;
- `log10(util) = 295.91248573769354`.

Therefore the representation itself fails admission before any cone-integration arithmetic.

## Execution evidence

- protocol: `20cbcc3c80c1ec25f9263a7d343a09e80346103b`
- method: `eeddcc1084654dee87bad9afdf7e8a91f035d73d`
- tests: `017ff6e9bc26f7c8b8a55f2cf34ac8883ad30e0b`
- falsifier: `17d40e381d28831d29332d0f55b44c95b9bf9f79`
- executed head: `b7b606aa9846d609e7c84ce67a8264d2bfb904f1`
- workflow run/job: `35455011080 / 105928633045`
- run attempt: `1`
- conclusion: `success`
- artifact: `e112-mask-message-treewidth`
- artifact ID: `10588420977`
- artifact ZIP SHA256: `f6f1173527c3d659e9a3faea78e42b531d94c5423ec4b5ebb539b3f87e8bcfff`.

No production-shaped forward pass was executed.

## Scientific interpretation

E111 showed that collapsing post-ReLU distributions to Gaussian first-two moments is far too biased. E112 tested the opposite extreme: retain the activation-mask dependence exactly.

That exact representation is structurally correct but explodes immediately for the dense architecture. There is no admissible exact finite-state mask-message path to width 1024 under the competition budget.

A useful successor must therefore compress non-Gaussian dependence **without** carrying the full activation mask: for example, a certified low-dimensional sufficient statistic or an approximation with an explicit remainder certificate.

No public/public-mini, benchmark target, scorer, holdout/full, tuning, sweep, rescue, canonical/ledger mutation, or merge occurred.
