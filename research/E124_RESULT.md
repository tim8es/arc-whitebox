# E124 result — Chow–Liu gate-amplitude linked-cluster closure

Idempotency key: `ARC-E124-CHOWLIU-GATE-AMPLITUDE-CLUSTER-20260920`

Decision: **TERMINAL NO-GO / DROP E124**

## Mechanism

E124 tested a new late-ReLU dependence closure from a clean
`research/bootstrap` parent.

For the penultimate hidden sources `H_i>=0`, it keeps every marginal gate
law and active-amplitude mean, then builds a deterministic maximum-mutual-
information Chow–Liu tree over the binary gates.

Every selected tree edge retains the complete 2x2 gate joint law plus
pair-state conditional endpoint amplitudes. Those pair statistics enter a
second-order linked-cluster expansion of the final ReLU mean.

There is no Gaussian plug-in, full mask table, shared source orbit, boundary
enumeration, target fit, or control variate.

## Exact falsifier

Frozen corpus:

- input dimension: 2
- width: 8
- depth: 4
- zero bias
- He-normal float64 weights
- seeds: `124200..124207`
- exact piecewise angular integration
- analytic Gaussian radial factor
- no Monte Carlo or numerical quadrature.

All integrity gates passed:

- exact partitions finite/complete;
- 2x2 pair laws nonnegative and normalized;
- pair marginals reconstruct single gate probabilities;
- marginal and pair-conditional amplitude statistics reconstruct exact source
  means within `1e-12`;
- every tree has 7 edges and is connected/acyclic;
- candidate and reference finite;
- deterministic replay bitwise exact.

## Scientific measurements

Independence-only pooled final-layer bias MSE:

`0.0030963942590008548`

E124 tree-linked pooled bias MSE:

`0.002257850564666443`

Ratio:

`0.7291870400880431`

So the explicit cross-source pair terms reduce pooled deterministic bias by
about `27.08%`.

They improve 6 of 8 frozen networks, satisfying the preregistered dependence-
signal gate.

However the raw target is:

`1.89e-8`.

E124 pooled bias is:

`119462.99283949434 x` the raw target.

The worst frozen network has MSE:

`0.009329195913704572`.

Thus both absolute scientific gates fail by orders of magnitude.

This is a scientific closure failure, not an implementation or accounting
failure: pairwise tree dependence captures a real effect, but it is nowhere
near enough to represent the high-order cross-source structure created by
late dense ReLUs.

## Production FLOP proof

Frozen production shape:

- width: 1024
- depth: 16
- trajectories: 4096
- propagate exact sampled trajectories through layers 1..15 only;
- construct all gate pair counts;
- build one Chow–Liu tree;
- accumulate tree-edge conditional amplitudes;
- replace the sampled final ReLU average with the analytic linked-cluster
  closure.

Conservative all-in upper:

`143,078,584,832 FLOPs`

Budget:

`2^41 = 2,199,023,255,552`

Utilization:

`0.06506460742093623 <= 0.13`

Headroom:

`142,794,438,389.76 FLOPs`

Compute therefore passes comfortably and is not the blocker.

## Execution evidence

- protocol: `e61bc531414c100688603086fa65d5923948a498`
- implementation: `93e073bafdd1995e4e7cf24404fa1daaaec56924`
- tests: `ac71c618723874be9765eda8f2dfe39d1de1324f`
- falsifier: `d7abe2ad468b68f25f864253703b5d09a41a394c`
- executed head: `430f32b270a843ecdc8580864abbf6cc14b96b9f`
- run/job: `35473469592 / 105978529834`
- run attempt: `1`
- focused tests: `4 passed in 0.16s`
- deterministic payload SHA256:
  `12b9d36a3e3c887c2d44a2fc01a10a3119365acddc12612496854ea65de8cec1`
- artifact: `e124-chowliu-gate-amplitude`
- artifact ID: `10594021621`
- artifact ZIP SHA256:
  `98d170d46fa5b2d3e5b6ab8a923414a656ba25b8aafc449dcfd02ddae00d3542`.

## Formal verdict

**E124 is closed.**

The experiment establishes that pairwise cross-source gate/amplitude
dependence is materially relevant, but a tree of pair interactions leaves
roughly five orders of magnitude too much deterministic late-ReLU bias.

No alternate tree, added edges, higher state count, amplitude binning,
Gaussian residual, calibration, rerun, rescue, production scientific run,
public/public-mini, scorer, holdout/full access, canonical mutation, ledger
mutation, or merge occurred.
