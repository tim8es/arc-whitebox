# E045 protocol — layerwise signed K3 sigma carrier

Idempotency key: `ARC-E044-START-20260916-E045`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance / firewall

- Branch: `research/e045-layerwise-signed-k3-sigma-20260916`.
- Direct parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E038–E044 are immutable and are not inherited or rescued.
- Public Phase-2 mini index 0 only for one future frozen local diagnostic.
- No holdout, scorer, rerun, tuning, sweep, canonical mutation or ledger mutation.

## Disjoint hypothesis

E044 shows that suppressing inherited K3 feedback between sparse depth checkpoints preserves the compute target but destroys accuracy. E045 therefore keeps a non-Gaussian cross-neuron carrier active at **every layer**, but changes representation class completely: no V25 per-birth source stack, no source subset/window/replay, no terminal adjoint, no Gaussian-only closure.

At each hidden layer represent the post-ReLU law by a deterministic **signed sigma ensemble** plus analytic diagonal remainder. Freeze 1024 antithetic direction pairs (`2048` endpoints) obtained from the full covariance eigenframe, with one center point. The pair geometry is rebuilt every layer from the candidate's current covariance; it is not an input-fixed angular rule.

To carry K3 information, freeze exactly 32 architecture-only Walsh response directions. Pair-weight antisymmetries are solved once per layer by the minimum-norm linear system that matches the 32 directional third central moments of the current signed ensemble after the exact ReLU point transform, subject to exact normalization and zero first-moment drift in those 32 response coordinates. No target truth enters the solve. The symmetric component continues to represent the full covariance; the analytic diagonal remainder is propagated by the Gaussian conditional ReLU marginal rule.

The complete signed ensemble is propagated through every linear layer and ReLU before the next deterministic rebuild. Thus cross-neuron non-Gaussianity is refreshed layerwise rather than transported as K3 birth tensors.

## Frozen constants

- antithetic pairs: `1024` (`2048` endpoints) plus one center;
- K3 response directions: first `32` Walsh/Sylvester-Hadamard columns;
- response solve: Moore-Penrose minimum-norm solution, no ridge;
- covariance eigensystem: deterministic descending eigenvalue order with sign canonicalization by largest-magnitude coordinate;
- negative signed weights are allowed;
- no clipping, damping, resampling or adaptive point count.

## Quantitative path

One 1024x1024-by-1024x2048 point propagation is about `2.15e9` multiply-add scale operations per layer. A full covariance rebuild from the same point matrix is of comparable order. Across 16 layers, two such dense passes per layer are about `6.9e10` primitive operations, or roughly `0.031 B`; eigensystem/32-direction response bookkeeping must keep measured utilization below the frozen `0.14` gate.

At utilization `0.14`, the adjusted target `<2.5e-09` requires raw `<1.7857143e-08`; the explicit raw gate remains the stricter project target `<=1.89e-08`, while both gates must independently pass. At utilization `<=0.132275`, raw `1.89e-08` would itself imply adjusted `<2.5e-09`.

Scientific hypothesis: layerwise rebuilding prevents the deep-transfer failure of fixed angular carriers while signed 32-direction K3 constraints preserve the cross-neuron asymmetry absent from Gaussian full-covariance E038.

## Frozen GO gates

All must pass on the future single index-0 diagnostic:

- raw final MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted `raw_mse * max(0.1, utilization) <2.5e-09`;
- failures `==0`;
- residual `<0.400 s`;
- finite outputs/state/weights;
- deterministic repeat max abs diff `==0.0`;
- point count exactly 2049 and response count exactly 32 at every rebuild;
- normalization/response constraints satisfy the preregistered numerical tolerance;
- all MLP-dependent arithmetic billed.

Any failed or unevaluable gate => **NO-GO / DROP E045**.

## Kill rule

No rescue under E045: no point-count change, response-count change, ridge, clipping, damping, alternate eigenframe, alternate Walsh set, coefficient fitting, second mini index, rerun, holdout, scorer, tuning or sweep. Any material change requires a fresh next experiment ID directly from canonical.
