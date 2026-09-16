# E097 — persistent rank-8 kappa22 memory feasibility

Idempotency key: `ARC-E097-RANK8-K22-MEMORY-20260917`

Status: **PRE-PUBLIC / SYNTHETIC FEASIBILITY ONLY**.

## Motivation

The current exact-V29 reference lane E051 reaches `raw=2.29004485946887e-08` but uses `587262754287` billed prediction FLOPs (`util≈0.267056` at `B=2^41`). The portfolio target is `raw<=1.89e-08` and `util<=0.135`.

V29's fourth-order information is largely regenerated memorylessly from current second/third-order state. E019 tested a richer generic dense K4 residual family and closed **on production cost**, not because richer K4 information was shown useless: a generic dense feed would require at least one new dense source leg and `O(n^3)` transport. E019 explicitly leaves low-rank approximation of the dense feed as a materially new hypothesis.

Independent public research provenance published for Phase-2 reports an augmented factored-K3 teacher carrying rank-8 factors of the pairwise `kappa22` slice and a validation MSE around `1.8023e-8`. E097 does **not** load that corpus, code, factors, targets, or parameters. The public fact is used only to motivate a fixed rank `r=8` before this experiment exists.

## Hypothesis

For random He-init ReLU MLPs, the connected pairwise fourth-cumulant slice

`K22[i,j] = cum(h_i,h_i,h_j,h_j)`

has an output-relevant persistent component concentrated in a very low-dimensional symmetric subspace. If its off-diagonal Frobenius energy is already strongly rank-8-compressible on independent synthetic networks, then a later estimator can carry a rank-8 persistent K22 memory at `O(n^2 r)` transport cost instead of E019's dense `O(n^3)` feed leg.

E097 Stage A tests only the **representation premise**. It does not fit coefficients, modify V29, or claim a competition-level accuracy result.

## Provenance / non-duplication

- branch: `research/e097-rank8-k22-memory-feasibility-20260917`
- direct base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- E019 is terminal and immutable; no E019 code/data/result is changed or rerun.
- E033 coordinatewise K4 discarded cross-neuron dependence; E097 explicitly studies the cross-neuron K22 slice.
- E016 rank-1 response, E019 multimode dense residual, E026 final K4 damping, and E037 signed K3/K4 response are different mechanism classes.
- E094 is source-axis K3 compute compression; E097 is K22 accuracy memory.
- E095 is projected sampling; E097 is deterministic moment-state representation.
- E091/E092 are residual calibration lanes; E097 performs no target calibration.

## Frozen Stage-A synthetic Monte-Carlo falsifier

Use exactly two independently seeded synthetic MLPs:

- width `n=128`
- depth `L=6`
- He weights iid `Normal(0, sqrt(2/n))`, float32
- weight seeds `97097` and `97197`
- input samples per MLP `N=32768`
- input seeds `197097` and `197197`
- input distribution `N(0,I)`
- deterministic NumPy PCG64
- no benchmark/challenge/public data.

For every post-ReLU layer `l=0..5`, retain that layer's sample activation matrix only long enough to compute empirical moments, then release the previous state.

For activation samples `H`:

1. `mu = mean(H)`;
2. `Z = H-mu`;
3. `C = E[Z Z^T]`;
4. `Q = Z**2`;
5. `M22 = E[Q Q^T]`;
6. `K22 = M22 - outer(diag(C),diag(C)) - 2*(C*C)`;
7. copy `K22_off=K22` and set its diagonal exactly to zero;
8. symmetrize only for roundoff as `(K22_off+K22_off.T)/2`.

Compute the full symmetric eigenspectrum only for this small synthetic diagnostic. Order eigenvalues by absolute magnitude. The optimal symmetric rank-8 Frobenius approximation is reconstructed from the eight largest-absolute eigenpairs.

Record per layer:

- `||K22_off||_F`;
- rank-8 captured Frobenius-energy fraction;
- rank-8 relative Frobenius reconstruction error;
- spectral effective rank `exp(-sum p log p)` for `p=lambda_i^2/sum lambda^2`;
- top-1/top-4/top-8/top-16 energy fractions;
- max absolute symmetry error before explicit symmetrization;
- finite state.

Also record aggregate median/worst rank-8 energy over all 12 MLP-layer observations and separately over the final three layers of each MLP.

## Noise control

The diagnostic is not allowed to change `N`, width, depth, seeds or rank after results are seen. To avoid declaring low rank from a numerically empty K22 matrix, an observation is eligible only if

`||K22_off||_F / max(||C||_F^2, 1e-30) >= 1e-5`.

Ineligible observations are reported and count as gate failures rather than being silently dropped.

## Frozen GO gates

All gates must pass to justify a later implementation experiment:

1. all 12 observations finite and eligible;
2. median rank-8 energy fraction across all 12 observations `>=0.90`;
3. worst rank-8 energy fraction among the six final-three-layer observations `>=0.80`;
4. median rank-8 relative Frobenius error across all 12 `<=sqrt(0.10)`;
5. deterministic replay of the complete diagnostic produces identical scalar metrics to `<=1e-12` absolute;
6. a static production cost bound for transporting one rank-8 symmetric factor state through 16 width-1024 layers is `<0.01 * 2^41` scalar FLOPs, counting at least two dense `n x n` by `n x r` products per layer plus O(n r^2) factor arithmetic.

Failure of any gate => terminal `NO-GO / DROP E097` for the persistent rank-8 K22 representation premise. No rank change, alternate seed, larger sample, eigenvalue threshold, selective-layer rescue, or benchmark run is allowed under E097.

## If Stage A passes

The only admissible next experiment is a new experiment ID implementing a deterministic factorized K22 propagation/response update with fixed rank 8 and synthetic teacher comparison before any challenge data access. Stage A GO does **not** authorize public/public-mini, official scorer, holdout/full, fitting, tuning, or merge.

## Prohibited

No challenge public/public-mini/full/holdout data, official scorer, external teacher arrays, pretrained parameters, target fitting, hyperparameter search, rank sweep, seed sweep, rerun-as-rescue, E019 resurrection, canonical mutation, ledger mutation, or merge.
