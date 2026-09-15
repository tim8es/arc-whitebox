# E047 Protocol — output-contracted connected-diagram DP for finite-width ReLU cumulants

Status: preregistered; no implementation or public evaluation may precede the RED falsifier.

Base canonical: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
Branch: `research/e047-connected-diagram-dp-20260916`
Date: 2026-09-16

## Hypothesis

Finite-width error after Gaussian/covariance propagation is dominated by connected cumulant contributions that survive contraction into future outputs. Instead of materializing full order-k cumulant tensors, maintain only deterministic output-contracted connected states and propagate them by dynamic programming through each affine map and ReLU transform.

The method class is disjoint from E041–E046: no K3 birth stack, backward replay, checkpoint replay, source-column cubature, signed sigma carrier, harmonic-defect correction, sampling, pruning, low-rank adaptation, topology adaptation, or data-driven tuning.

## Frozen representation

- Maximum cumulant order: `KMAX = 6`.
- Arithmetic dtype: `float64`.
- Hidden width expected by the frozen public mini0 architecture: 1024.
- Only output-contracted connected states are allowed. No full `O(width^k)` tensor for any k>=3 may be constructed, stored, or transiently materialized.
- For every layer l and order k=3..6, state `C_l[k]` is represented only through contractions against a fixed set of deterministic future-output probes.
- Probe count: `PROBE_COUNT = 32`.
- Probe family: first 32 columns of a deterministic Walsh-Hadamard basis at width 1024, scaled to unit Euclidean norm; for synthetic widths, the first `min(32,width)` canonical deterministic Walsh columns are used.
- Probe signs/order are fixed by Walsh column index; no SVD, eigenselection, ranking, pruning, topology selection, or adaptation.
- Connected-state topology set is frozen to integer set partitions of k external legs whose block-incidence graph remains connected after the current ReLU vertex is inserted. All disconnected products are generated only through the moment↔cumulant identities below and are never stored as persistent states.

## Mathematical identities

For scalar random variables with moments `m_n = E[X^n]` and cumulants `kappa_n`, the exact recurrence used in the synthetic falsifier is

`m_n = sum_{pi in P(n)} prod_{B in pi} kappa_{|B|}`

and Möbius inversion

`kappa_n = sum_{pi in P(n)} (|pi|-1)! (-1)^{|pi|-1} prod_{B in pi} m_{|B|}`.

For a jointly Gaussian preactivation vector `z` with mean `mu` and covariance `Sigma`, ReLU moments needed by the local vertex are obtained from deterministic one-dimensional Gaussian quadrature after projection onto each frozen contracted direction. For each probe q and layer l, let `s = q^T z`; local raw moments through order 6 are

`M_r(q) = E[(max(s,0))^r]`, r=1..6.

The connected scalar cumulants `K_r(q)` are obtained exactly from the partition Möbius identity above. The DP propagates only these contracted connected quantities.

Affine propagation is multilinear before contraction: for an order-k connected cumulant tensor `T_k`, and future contracted vector q,

`<T'_k, q^{⊗k}> = <T_k, (W q)^{⊗k}>`.

This identity is the core reason full tensors are unnecessary. Every stored order-k state is a scalar contraction associated with a frozen probe and a deterministic future weight contraction.

At a ReLU vertex, disconnected contributions are reconstructed from lower connected orders with the partition identity, transformed by the scalar ReLU moment map, then Möbius-inverted back to the connected order-k contribution. Orders above KMAX are discarded exactly by preregistration; there is no adaptive closure.

The final mean correction is the fixed Edgeworth/connected-diagram contraction through KMAX=6 using coefficients `1/k!` for order-k connected derivatives evaluated under the Gaussian reference. No coefficients are fitted from public data.

## Synthetic falsifier

Before any public data access, focused tests must compare an explicit reference and the contracted DP on deterministic small networks.

Frozen synthetic cases:

1. Scalar width-1, depth-2 affine/ReLU network with deterministic rational weights; explicit enumeration of moments/cumulants through order 6 must equal the contracted recurrence to absolute tolerance `1e-12`.
2. Width-2, depth-2 deterministic network. Build explicit dense cumulant tensors only in the test reference for k=3..6 and contract them against two fixed output vectors. Contracted-DP results must match explicit contractions with max absolute error `<=1e-10`.
3. Width-3, depth-3 deterministic network with fixed covariance and fixed output probes. Explicit-vs-contracted final mean correction through KMAX=6 must match to `<=1e-9`.
4. Determinism: identical invocation produces bitwise-identical contracted states.
5. Representation guard: production module exposes no persistent ndarray whose rank exceeds 2 and tests reject helper outputs with tensor rank >2 for k>=3.

Synthetic GO requires all cases pass. Any failure is terminal E047 NO-GO and forbids implementation extension, public-mini access, rescue, tuning, rerun, or alternate topology.

## FLOP accounting

All MLP-dependent arithmetic is billed inside `flops.BudgetContext`, including:

- covariance/mean Gaussian reference propagation;
- future-probe contractions through every weight matrix;
- all scalar connected-state DP updates for orders 3..6;
- ReLU quadrature/moment transforms used by production;
- final connected-diagram correction assembly.

Data-independent generation of integer partitions and the 32 Walsh sign patterns may be cached outside the budget because they depend only on frozen constants, not on MLP weights or public data.

No operation may create an `O(width^k)` object for k>=3. Core projected target utilization is `<=0.100`; total final utilization gate is `<=0.125` of budget `2**41`.

## Frozen public diagnostic

Only after synthetic GREEN, exactly one diagnostic may access:

- dataset: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini`
- index: `0`
- budget: `2**41`

One identical prediction repeat is permitted solely for determinism and is excluded from score/FLOP gates.

Frozen gates:

- raw final-layer MSE `<= 1.89e-08`
- adjusted proxy `< 2.5e-09`
- utilization `<= 0.125`
- core projected utilization `<= 0.100`
- failures `== 0`
- residual wall time `< 0.400 s`
- output finite
- deterministic repeat max absolute difference `== 0.0`
- `KMAX == 6`, `PROBE_COUNT == 32`, dtype float64
- no full order-k tensors for k>=3

Adjusted proxy is frozen as `raw_final_mse * max(0.1, utilization)`.

## One-shot kill rule

Any synthetic falsifier failure or any single frozen public-mini gate failure makes E047 terminal `NO-GO / DROP`. There is no rescue, rerun, clipping, damping, pruning, topology adaptation, rank/probe adaptation, coefficient fitting, holdout, full-split evaluation, parameter sweep, or official scorer run. Canonical and ledger remain untouched.