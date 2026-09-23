# R254 frozen protocol — V25-BR13 balanced mean-rider reduction

Status: **FROZEN BEFORE SOLE ACTIONS TRIGGER**  
Owner: `one-shot-accuracy-research`  
Run ID: `R254-one-shot-global-accuracy-20260923`

## Evidence and novelty

R254 is a fresh accuracy-first attempt. It does not rerun R251 or R252.

The immutable history index at the authoritative pre-R254 control head contains 194
experiment IDs. Exact history searches found zero occurrences of `pairwise sum`,
`pairwise summ`, `compensated`, `kahan`, `neumaier`, `summation order`,
`reduction tree`, or `einsum accumulation`. Queue evidence for
R231/R232/R238/R239/R245/R249/R250/R251/R252/R253 and the explicit R247/R248
exclusions was read before freezing this method.

Excluded and not reused: R251 GFNP; both R252 D21-CWG and unauthorized CFSP4;
R232 DRRE descendants; R238 RSRF descendants; R247 2:4 sparsity; R248 Kronecker
transport; R250 LEG2-R1; R244 MP-R16; R223 V25-LF; and all closed/rejected history
families. No R223/R244 outputs or artifacts are read. R230's negative disclosure
finding is not used to invent a leader method.

Closest evidence is R239's numerical-stability audit and the unexecuted E050 float64
protocol. BR13 is distinct: it changes neither dtype nor mathematical estimator
formula. It changes only the float32 parenthesization of one already-existing 13-term
V25 rider reduction.

## Exactly one hypothesis: V25-BR13

Pinned parent:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
`estimators/estimator_v25.py`, Git blob
`195373a110215256b759d7c172ba8c923c62e5cc`, SHA256
`c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

Parent source anchor, verified once pre-trigger:
`delta = feats @ beta_rows[li]`.

BR13 keeps the 13 features, all 16x13 coefficients, every V25 K3/K4/source/rank/lambda
operation and every gate unchanged. It computes the same real-arithmetic dot product
using a fixed balanced binary tree:

- 13 elementwise products;
- six adjacent pair sums;
- three pair-pair sums;
- two next-level sums, one joining term 12;
- one final sum.

Thus parent and candidate both have semantically 13 multiplies + 12 adds per output.
No fitted coefficient, target, network ID, seed choice, branch, clipping, damping,
rank change or per-network rule exists. The hypothesis is purely that a shorter fixed
float32 reduction depth reduces cancellation/roundoff in the existing global V25 rider
enough to improve raw accuracy.

The source delta contains no `math.*`, scalar numerical algorithm, division,
transcendental, external library or unmetered numerical reduction. Numerical products
and additions remain `fnp.ndarray` operators. Static FLOP direction is equal; measured
FlopScope candidate <= parent is mandatory.

## Deterministic production-shape target-free fixture

Fixture `R254-MONOMIAL-PATH-254001`: width 1024, depth 16, float32, zero bias.

Each output column has exactly one nonzero weight. For layer l/output j:
- row = `((2*l+1)*j + (37*l+254001)%1024) % 1024`;
- magnitude = `(768 + ((j*(2*l+5)+254001+97*l)%513))/1024`;
- layer 0 sign is negative iff `(17*j+254001)%7==0`; later signs are positive.

All magnitudes are dyadic and exactly representable in float32. Exact mean truth uses
no BLAS/matvec/reduction:
- layer 0: `abs(scale)*0.3989422804014327`;
- later: one scalar multiply `scale*previous_truth[row]`.

Frozen hashes are in `R254_FIXTURE_MANIFEST.json`.
Concatenated weights SHA256:
`199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`.
Truth SHA256:
`58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

Before workflow creation two independently written reconstruction paths were executed
and agreed on every layer hash, concatenated hash and truth hash. The committed runtime
fixture generator repeats both implementations and fails closed on any mismatch.

## Sole workflow / runtime identity

Exactly one push-triggered workflow is authorized, on standard GitHub-hosted
`ubuntu-24.04`; no retry/rerun/second workflow.

Pinned:
- Python 3.11.16;
- NumPy 2.4.6 wheel SHA256
  `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`;
- FlopScope 0.12.1 wheel SHA256
  `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
- WhestBench 0.16.1 wheel SHA256
  `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`.

Wheel hashes are checked before installation/science. Runtime versions are read with
`importlib.metadata.version`. WhestBench must equal `0.16.1`. FlopScope distribution
version is normalized by removing only a `+...` local suffix *after* its wheel hash
passes, and the normalized value must equal `0.12.1`. This explicitly avoids R252's
module-`__version__` trap.

## Mandatory unchanged-parent gate

The first estimator execution is the byte-identical pinned V25 parent on the frozen
fixture. An external wrapper around `flops.as_symmetric` records, before delegating:
call order, shape, all-finite, max-abs and max `|A-A.T|`. Per-layer returned prediction
finite/max-abs is also retained.

Parent PASS requires exact source/runtime/fixture identities; shape (16,1024); all
predictions/checkpoints finite; at least 16 symmetry checkpoints; every square 2D
checkpoint residual <= `1e-6 + 1e-5*max_abs`; positive measured FLOPs <= 2**41; no
exception/budget/wall failure.

Any parent failure => terminal **INCONCLUSIVE**, candidate is not constructed, public
data is not accessed, and there is no retry.

## Candidate target-free falsifier

Only after parent PASS, replace exactly the one frozen source anchor by BR13. No other
source text may change.

Mandatory candidate gates:
- source diff exactly the frozen replacement and R249-compliant delta;
- fixture dual replay hashes exact;
- finite shape (16,1024), no exception;
- final-layer truth MSE <= 0.95 * parent;
- all-layer truth MSE <= 0.98 * parent;
- >=12/16 layer MSEs strictly improve;
- maximum layer degradation ratio <=1.10;
- same symmetry diagnostic gate;
- measured candidate FLOPs <= parent;
- residual wall time <= 1.05*parent + 0.005 s.

Any failed or unevaluable target-free/source/cost gate => terminal scientific NO-GO
and public data is skipped.

## Conditional exact R209 mini-100

Only if all pre-public gates pass, the same workflow first independently re-extracts
the exact public mini dataset identity from
`aicrowd/arc-whestbench-public-2026@v2-phase2`: metadata SHA256
`264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`,
100-row order/name, decimal int64 `mlp_seed` as network_id, and SHA256 of
C-contiguous raw float32 `all_layer_means` bytes. Every row must equal the normalized
R209 record before candidate scoring.

Then run candidate once on exactly mini-100. Public GO requires:
- exact R209 row/order/network/target hashes;
- zero failures;
- mean adjusted score <= 0.95 * R209 = `7.761877568111363e-9`;
- >=55/100 rows improved;
- paired parent-minus-candidate gain >2 descriptive SE;
- mean FLOPs <= `806303721965`;
- max residual wall time <0.4 s.

No rank/same-panel leaderboard claim follows.

## Absolute stop rules

No second R254 workflow/run/retry/method; no gate relaxation; no paid/larger/private
runner; no private/holdout/full; no submission/leaderboard/canonical edits; no R223/R244
outputs/artifacts; no R252 workflow/trigger edits; no per-network tuning.
