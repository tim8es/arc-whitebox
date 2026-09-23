# R239 — read-only numerical-stability audit of R232/R238 synthetic V25 base failures

Status: **DIAGNOSTIC COMPLETE (read-only)**  
Queue run: `R239-v25-synthetic-numerical-stability-audit-20260923`

## Scope

This audit diagnoses only retained evidence from the frozen R232 and R238 exact-small
runs. It did **not** execute Python/estimator code, regenerate or resize fixtures, launch
Actions, access benchmark/holdout/private data, construct a candidate, or edit R232,
R238, R223, or canonical estimator source.

R223 attempt 6 was left untouched.

## Pinned sources

Governance:
- `AGENTS.md` blob `6d9c61537a282a7d141af316dd8be438d1015a49`
  ([source](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/AGENTS.md)).
- `research/RESEARCH_PROCESS.md` blob
  `bf5a4676d8f36100e2dfdde32d544a39661eba8d`
  ([source](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/RESEARCH_PROCESS.md)).

R232:
- frozen protocol blob `6c75bb19781eac65838c7997933627abeef32ee0`
  ([source](https://github.com/tim8es/arc-whitebox/blob/d7acd05ee8b8caa71e6463f0e8dab6eb17fb829b/research/r232/R232_PROTOCOL.md));
- exact-small script blob `c3339f4ffb773570dfda36635bebb7a447ce567d`
  ([source](https://github.com/tim8es/arc-whitebox/blob/b6f7b4692563a1520ef4992201cfbe027a04226c/scripts/r232_drre_exact_small.py));
- workflow blob `6393b724c89411524cb41ece1f9b2afb5dbed4ad`
  ([source](https://github.com/tim8es/arc-whitebox/blob/b6f7b4692563a1520ef4992201cfbe027a04226c/.github/workflows/r232-drre-exact-small.yml));
- terminal receipt blob `c6aa858bd083c86067160325015032d9d7208343`,
  receipt SHA256 `d4183c402f8c77165b1c268fc402dd67d1d7bb986105b5bcebee48d046db47fd`
  ([source](https://github.com/tim8es/arc-whitebox/blob/d7acd05ee8b8caa71e6463f0e8dab6eb17fb829b/research/r232/R232_TERMINAL_RECEIPT_ATTEMPT2.json));
- Actions run/job `35803857969 / 107000109847`, artifact `10727365072`,
  ZIP SHA256 `fd8d0afe6f48eab3e4f3b9bf9c4d6e947f599497911016ea59bf1daed94383ca`
  ([run](https://github.com/tim8es/arc-whitebox/actions/runs/35803857969)).

R238:
- frozen protocol blob `757e3f67741b9e05b709a247eae5c9a921d787e6`
  ([source](https://github.com/tim8es/arc-whitebox/blob/a8bb06f23f416ea4a1c01c655756477849234c74/research/r238/R238_PROTOCOL.md));
- exact-small script blob `17b6cd77afeca3387bb6f06c3577194f1dae6f0c`
  ([source](https://github.com/tim8es/arc-whitebox/blob/12c595f3dec66e4616f76ca688b1f5339b5bdf24/scripts/r238_rsrf_exact_small.py));
- workflow blob `adae8a650a0f2c9c05c0b4354258e55f6e90a7db`
  ([source](https://github.com/tim8es/arc-whitebox/blob/12c595f3dec66e4616f76ca688b1f5339b5bdf24/.github/workflows/r238-rsrf.yml));
- terminal receipt blob `869742557a86d88ba136736954d4755fa40a19be`,
  receipt SHA256 `361a6f9b50a8e4211df7a9cf43cbd1740932c7b21650dc2ffbbf97437e2467cd`
  ([source](https://github.com/tim8es/arc-whitebox/blob/a8bb06f23f416ea4a1c01c655756477849234c74/research/r238/R238_TERMINAL_RECEIPT.json));
- Actions run/job `35808859764 / 107015629065`, artifact `10728444220`,
  ZIP SHA256 `761783a92ac967758dbcee9a6d9fadb146280d89fa6f782cfcbc9a927083ef2a`
  ([run](https://github.com/tim8es/arc-whitebox/actions/runs/35808859764)).

Common V25:
- upstream `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- `estimators/estimator_v25.py` git blob
  `195373a110215256b759d7c172ba8c923c62e5cc`;
- downloaded source SHA256 in retained evidence
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`
  ([source](https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v25.py)).

Matching flopscope:
- package version in both runs: `0.12.1+np2.4.6`, NumPy `2.4.6`, Python `3.11.16`;
- PyPI 0.12.1 maps to source commit
  `AIcrowd/flopscope@b599f015b0bc005b1edb6d7a1b10e0814675e693`;
- wheel SHA256
  `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
- relevant source blobs:
  `_pointwise.py=5d8f9210ff23979ef9658897d8cd1a02127b33c4`,
  `_einsum.py=8075275290c1a8649dc48319c26f5f5e30b4c781`,
  `_symmetric.py=73c796835c586fcdb5c763bc30dd7ce4cb7277a4`,
  `_budget.py=f4d32d9d6a10b7292ba2e3c6fdbd8c68955248b8`
  ([pointwise](https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/_pointwise.py),
  [einsum](https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/_einsum.py),
  [symmetric](https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/src/flopscope/_symmetric.py)).

## Observations

### 1. The two failures are materially different

**R232** fails during the first frozen fixture's high-rank call at V25 line 514:

`C_pre = fnp.einsum("ij,ia,jb->ab", C, w32, w32)`.

The Actions log contains **no RuntimeWarning for overflow/invalid/non-finite** before the
exception. The exception is raised in flopscope
`_pointwise._validate_result_symmetry`, reported as
`SymmetryError(... max_deviation=inf)`.

In flopscope v0.12.1, that function first evaluates
`np.all(np.isfinite(result_arr))`. If any result entry is non-finite it returns
`False` **without raising this SymmetryError**. Only a finite result that then fails
the symmetry generator `np.allclose` check reaches the hard-coded
`max_deviation=float("inf")` raise.

Therefore, the R232 `inf` is a **sentinel**, not a measured tensor infinity.
Retained evidence establishes a **finite symmetry-validation failure**, not a NaN/Inf
origin.

Mathematically, with symmetric `C` and the same `w32` on both contracted legs,
the exact expression is symmetric in output indices `a,b`. The retained record is
insufficient to distinguish float32 cancellation/rounding from a flopscope symmetric
einsum implementation/path issue.

**R238** reaches a different failure. Its log first records:

1. `RuntimeWarning: overflow encountered in multiply` at flopscope's counted backend
   wrapper (`_budget.py:540`);
2. `RuntimeWarning: overflow encountered in multiply` from NumPy's einsum backend;
3. then V25 line 929
   `C = flops.as_symmetric(C, symmetry=(0, 1))`
   raises `SymmetryError(... max_deviation=nan)`.

Here flopscope's direct `as_symmetric` validation computes the actual
`max(abs(C-C.T))`; a NaN result is consistent with a non-finite `C`, and the two
immediately preceding overflow warnings independently prove that numerical overflow
occurred before the symmetry claim.

The **earliest retained non-finite evidence for R238** is therefore the first generic
multiply warning. The exact V25 source operation and layer that emitted it are **not
retained**: the warning points only to the generic flopscope wrapper, not its caller.

### 2. “Unchanged V25 base” means unchanged source, not production configuration

Both runs verified the same V25 source blob, but both scripts deliberately override
class attributes for their small synthetic fixtures.

R232:
- width/depth `9/10`;
- seeds `232900..232903`;
- only the first two input rows are live;
- first layer uses unscaled standard normal entries;
- later layers use `sqrt(2/9)`;
- `R_OLD=8`, high `R_OLD2=7`, low `R_OLD2=6`, ages `4/7`.

R238:
- width/depth `12/10`;
- seeds `238120..238123`;
- only the first two input rows are live;
- first layer is scaled by `0.50`;
- later layers use `0.65*sqrt(2/12)`;
- `R_OLD=8`, `R_OLD2=6`, ages `4/7`.

V25 itself sets `riders = (n == 1024 and L == 16)`, so both fixtures run the
off-suite shape-generic path; the suite-only regenerated K4 rider is disabled. But
`confine = (R_OLD < n)` remains true for both small widths. These runs therefore do
not demonstrate instability of the canonical width-1024/depth-16 production trajectory.

### 3. A plausible amplification path exists, but is not proven

V25 floors variance at `1e-10`, then forms `sigma=sqrt(var)` and inverse powers
through `sigma^-6` before constructing the Wick matrix and high-order products.
If a synthetic trajectory drives one or more approximate variances near the floor,
large finite inverse powers can amplify cancellation and later products can overflow.

The two-dimensional-live first layer also makes the synthetic dependence structure
highly constrained relative to the ambient width. That is a plausible reason these
fixtures stress the shape-generic closure differently from the Phase-2 suite.

This is **inference only**. Neither Actions artifact retained the per-layer `var`,
`sigma`, Wick matrix, `PK1/PK2`, `C`, or an operation log sufficient to prove
that this particular path caused either failure.

## Missing raw inputs / limits of diagnosis

The R232 workflow artifact retained stdout, exit code, version/hash files, protocol,
cost/novelty files and the falsifier script. It did **not** retain generated fixture
weight tensors or per-layer V25 state.

R238 similarly retained the parent source, falsifier JSON/logs and metadata, but no
generated fixture weights or per-layer numerical checkpoints. Its candidate file was
not created because the base gate failed.

The scripts and seeds make the fixtures reproducible in principle, but R239 is explicitly
forbidden to recreate them. Consequently this audit cannot establish:

- the exact layer of R232's finite symmetry mismatch;
- the numerical `max|C_pre-C_pre.T|` in R232;
- the exact layer/V25 operation that first overflowed in R238;
- the first tensor element that became Inf/NaN;
- whether R232's finite mismatch is purely float32 cancellation or a flopscope 0.12.1
  symmetric-einsum implementation effect.

No stronger root-cause claim is supported by retained evidence.

## One safe future protocol guard

For a **separately preregistered future method only**, require a retained
**parent-stability checkpoint** before candidate construction:

> Save the exact synthetic fixture tensor bytes + SHA256 and, for the unchanged parent,
> retain per-layer finite/max-abs diagnostics and symmetry residuals immediately before
> every symmetry claim (at minimum `var`, `sigma`, `W_all`, `PK1/PK2`,
> `C_pre`/assembled `C`). Abort before candidate construction on the first
> non-finite value or symmetry residual above the runtime tolerance.

This is an evidence guard, not a repair or authorization to rerun R232/R238.

## Diagnostic conclusion

- **R232:** retained evidence proves a finite, tolerance-level symmetry validation
  failure in the symmetric `C_pre` einsum; it does **not** prove a NaN/Inf.
- **R238:** retained evidence proves numerical overflow before assembled covariance
  symmetry validation; the exact originating V25 operation is unknown.
- The two failures should not be collapsed into one “V25 NaN bug.”
- No candidate-science conclusion follows from either base failure, and no production
  V25 stability claim is made here.
