"""Minimal executable TA32 kernel for R202/H185.

This is intentionally a kernel probe, not the full H185 compiler.  It consumes the
pinned rational LITA 32x32x32 rank-14197 scheme, applies one outer TA stage, and
accounts coefficient arithmetic, reconstruction additions, leaf matmuls, padding,
cropping, and explicit fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from time import perf_counter

import numpy as np

TA_DIM = 32
TA_RANK = 14197
SCHEME_GIT_BLOB_SHA1 = "6f2dea4820245303dc2eb1fba13816436fabe54d"
SCHEME_COMMIT = "c1dd9225df98676e385b53ae7517ff2ea0ec5779"
SCHEME_PATH = "schemes/32x32x32_r14197.npz"
LITA_GRID_N32 = 96 * (TA_DIM // 2 - 2) ** 2 * (TA_DIM // 2 - 3)
MECHANISM_RATIO_GATE = 0.42


@dataclass(frozen=True)
class Axis:
    indptr: np.ndarray
    indices: np.ndarray
    numerators: np.ndarray
    denominators: np.ndarray

    @property
    def nnz(self) -> int:
        return int(self.indices.size)

    @property
    def rows(self) -> int:
        return int(self.indptr.size - 1)

    def row_nnz(self) -> np.ndarray:
        return np.diff(self.indptr).astype(np.int64, copy=False)

    def coefficients(self, dtype: np.dtype) -> np.ndarray:
        return (self.numerators.astype(dtype) / self.denominators.astype(dtype)).astype(
            dtype, copy=False
        )


@dataclass(frozen=True)
class Scheme:
    u: Axis
    v: Axis
    w: Axis
    metadata: dict

    @property
    def rank(self) -> int:
        return self.u.rows


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_scheme(path: str | Path) -> Scheme:
    path = Path(path)
    raw = path.read_bytes()
    actual_blob = git_blob_sha1(raw)
    if actual_blob != SCHEME_GIT_BLOB_SHA1:
        raise ValueError(f"scheme Git blob mismatch: {actual_blob}")

    with np.load(path, allow_pickle=False) as z:
        metadata = json.loads(str(z["metadata_json"]))
        axes = {}
        for name in ("u", "v", "w"):
            axes[name] = Axis(
                indptr=np.asarray(z[f"{name}_indptr"], dtype=np.int64),
                indices=np.asarray(z[f"{name}_indices"], dtype=np.int32),
                numerators=np.asarray(z[f"{name}_numerators"], dtype=np.int64),
                denominators=np.asarray(z[f"{name}_denominators"], dtype=np.int64),
            )

    scheme = Scheme(axes["u"], axes["v"], axes["w"], metadata)
    if metadata.get("tensor") != [TA_DIM, TA_DIM, TA_DIM]:
        raise ValueError(f"unexpected tensor {metadata.get('tensor')}")
    if metadata.get("rank") != TA_RANK or scheme.rank != TA_RANK:
        raise ValueError(f"unexpected rank {metadata.get('rank')} / {scheme.rank}")
    if not (scheme.u.rows == scheme.v.rows == scheme.w.rows):
        raise ValueError("axis row-count mismatch")
    if any(np.any(ax.indices < 0) or np.any(ax.indices >= TA_DIM * TA_DIM)
           for ax in (scheme.u, scheme.v, scheme.w)):
        raise ValueError("scheme index outside 32x32 coordinate space")
    return scheme


def _blocks(x: np.ndarray) -> np.ndarray:
    m, n = x.shape
    if m % TA_DIM or n % TA_DIM:
        raise ValueError("padded matrix dimensions must be divisible by 32")
    bm, bn = m // TA_DIM, n // TA_DIM
    return (
        x.reshape(TA_DIM, bm, TA_DIM, bn)
        .transpose(0, 2, 1, 3)
        .reshape(TA_DIM * TA_DIM, bm, bn)
    )


def _unblocks(blocks: np.ndarray, m: int, n: int) -> np.ndarray:
    bm, bn = m // TA_DIM, n // TA_DIM
    return (
        blocks.reshape(TA_DIM, TA_DIM, bm, bn)
        .transpose(0, 2, 1, 3)
        .reshape(m, n)
    )


def _axis_csr(axis: Axis, dtype: np.dtype):
    try:
        from scipy.sparse import csr_matrix
    except ImportError as exc:  # explicit technical fallback boundary
        raise RuntimeError("TA32_EXECUTION_REQUIRES_SCIPY") from exc
    return csr_matrix(
        (axis.coefficients(dtype), axis.indices, axis.indptr),
        shape=(axis.rows, TA_DIM * TA_DIM),
        dtype=dtype,
    )


def ta32_cost(scheme: Scheme, m: int, k: int, n: int) -> dict:
    mp = math.ceil(m / TA_DIM) * TA_DIM
    kp = math.ceil(k / TA_DIM) * TA_DIM
    np_ = math.ceil(n / TA_DIM) * TA_DIM
    bm, bk, bn = mp // TA_DIM, kp // TA_DIM, np_ // TA_DIM

    u_elems = bm * bk
    v_elems = bk * bn
    w_elems = bm * bn

    coeff_mult_u = scheme.u.nnz * u_elems
    coeff_mult_v = scheme.v.nnz * v_elems
    coeff_mult_w = scheme.w.nnz * w_elems

    add_u = int(np.maximum(scheme.u.row_nnz() - 1, 0).sum()) * u_elems
    add_v = int(np.maximum(scheme.v.row_nnz() - 1, 0).sum()) * v_elems

    w_col_counts = np.bincount(scheme.w.indices, minlength=TA_DIM * TA_DIM)
    add_w = int(np.maximum(w_col_counts - 1, 0).sum()) * w_elems

    leaf_matmul = scheme.rank * 2 * bm * bk * bn
    arithmetic = (
        coeff_mult_u + coeff_mult_v + coeff_mult_w + add_u + add_v + add_w + leaf_matmul
    )
    classical_padded = 2 * mp * kp * np_
    classical_unpadded = 2 * m * k * n

    # Copies are not FLOPs under the project/flopscope convention, but are retained
    # explicitly so they cannot disappear from the receipt.
    padding_input_scalars = mp * kp + kp * np_ if (mp, kp, np_) != (m, k, n) else 0
    crop_output_scalars = mp * np_ if (mp, np_) != (m, n) else 0

    return {
        "shape": [m, k, n],
        "padded_shape": [mp, kp, np_],
        "block_shape": [bm, bk, bn],
        "rank": scheme.rank,
        "nnz": {"u": scheme.u.nnz, "v": scheme.v.nnz, "w": scheme.w.nnz},
        "coefficient_multiplies": {
            "u": int(coeff_mult_u),
            "v": int(coeff_mult_v),
            "w": int(coeff_mult_w),
        },
        "linear_combination_additions": {
            "u": int(add_u),
            "v": int(add_v),
            "w_reconstruction": int(add_w),
        },
        "leaf_matmul_flops": int(leaf_matmul),
        "arithmetic_flops": int(arithmetic),
        "classical_padded_flops": int(classical_padded),
        "classical_unpadded_flops": int(classical_unpadded),
        "ratio_to_classical_unpadded": float(arithmetic / classical_unpadded),
        "leaf_ratio_to_classical_unpadded": float(leaf_matmul / classical_unpadded),
        "padding_input_scalars_copied": int(padding_input_scalars),
        "crop_output_scalars_copied": int(crop_output_scalars),
        "fallback_flops": 0,
        "fallback_count": 0,
        "copy_flops_by_convention": 0,
    }


def fallback_cost(m: int, k: int, n: int, reason: str) -> dict:
    flops = 2 * m * k * n
    return {
        "shape": [m, k, n],
        "route": "PARENT_FALLBACK",
        "reason": reason,
        "fallback_count": 1,
        "fallback_flops": int(flops),
        "arithmetic_flops": int(flops),
    }


def ta32_matmul(
    a: np.ndarray,
    b: np.ndarray,
    scheme: Scheme,
    *,
    allow_fallback: bool = False,
) -> tuple[np.ndarray, dict, dict]:
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError("matmul shape mismatch")
    m, k = a.shape
    _, n = b.shape
    if a.dtype != b.dtype or a.dtype not in (np.dtype("float32"), np.dtype("float64")):
        if not allow_fallback:
            raise TypeError("TA32 supports matched float32/float64 only")
        t0 = perf_counter()
        out = a @ b
        return out, fallback_cost(m, k, n, "UNSUPPORTED_DTYPE"), {
            "total_seconds": perf_counter() - t0
        }

    mp = math.ceil(m / TA_DIM) * TA_DIM
    kp = math.ceil(k / TA_DIM) * TA_DIM
    np_ = math.ceil(n / TA_DIM) * TA_DIM
    ap = np.zeros((mp, kp), dtype=a.dtype)
    bp = np.zeros((kp, np_), dtype=b.dtype)
    ap[:m, :k] = a
    bp[:k, :n] = b

    ab = _blocks(ap)
    bb = _blocks(bp)
    bm, bk = ab.shape[1:]
    _, bn = bb.shape[1:]

    u = _axis_csr(scheme.u, a.dtype)
    v = _axis_csr(scheme.v, a.dtype)
    w = _axis_csr(scheme.w, a.dtype)

    t0 = perf_counter()
    x = np.asarray(u @ ab.reshape(TA_DIM * TA_DIM, -1), dtype=a.dtype)
    t1 = perf_counter()
    y = np.asarray(v @ bb.reshape(TA_DIM * TA_DIM, -1), dtype=a.dtype)
    t2 = perf_counter()
    products = np.matmul(x.reshape(scheme.rank, bm, bk), y.reshape(scheme.rank, bk, bn))
    t3 = perf_counter()
    cb = np.asarray(w.T @ products.reshape(scheme.rank, -1), dtype=a.dtype)
    t4 = perf_counter()
    outp = _unblocks(cb.reshape(TA_DIM * TA_DIM, bm, bn), mp, np_)
    out = np.array(outp[:m, :n], copy=True)
    t5 = perf_counter()

    timing = {
        "u_form_seconds": t1 - t0,
        "v_form_seconds": t2 - t1,
        "leaf_seconds": t3 - t2,
        "w_reconstruct_seconds": t4 - t3,
        "crop_copy_seconds": t5 - t4,
        "total_seconds": t5 - t0,
    }
    return out, ta32_cost(scheme, m, k, n), timing


def exact_scalar_block_identity(
    scheme: Scheme, a: np.ndarray, b: np.ndarray, grid: int = LITA_GRID_N32
) -> dict:
    if a.shape != (TA_DIM, TA_DIM) or b.shape != (TA_DIM, TA_DIM):
        raise ValueError("exact scalar-block fixture must be 32x32")
    ai = [int(x) for x in a.reshape(-1)]
    bi = [int(x) for x in b.reshape(-1)]

    def scaled_coeffs(axis: Axis) -> list[int]:
        out = []
        for num, den in zip(axis.numerators.tolist(), axis.denominators.tolist()):
            if grid % int(den):
                raise AssertionError(f"denominator {den} does not divide LITA grid {grid}")
            out.append(int(num) * (grid // int(den)))
        return out

    us = scaled_coeffs(scheme.u)
    vs = scaled_coeffs(scheme.v)
    ws = scaled_coeffs(scheme.w)
    accum = [0] * (TA_DIM * TA_DIM)

    for row in range(scheme.rank):
        u0, u1 = int(scheme.u.indptr[row]), int(scheme.u.indptr[row + 1])
        v0, v1 = int(scheme.v.indptr[row]), int(scheme.v.indptr[row + 1])
        w0, w1 = int(scheme.w.indptr[row]), int(scheme.w.indptr[row + 1])
        left = sum(us[p] * ai[int(scheme.u.indices[p])] for p in range(u0, u1))
        right = sum(vs[p] * bi[int(scheme.v.indices[p])] for p in range(v0, v1))
        prod = left * right
        for p in range(w0, w1):
            accum[int(scheme.w.indices[p])] += ws[p] * prod

    ref = np.asarray(a, dtype=object) @ np.asarray(b, dtype=object)
    scale = grid**3
    residual = [accum[i] - int(ref.reshape(-1)[i]) * scale for i in range(TA_DIM * TA_DIM)]
    max_abs = max(abs(x) for x in residual)
    return {
        "grid": int(grid),
        "scale_grid_cubed": int(scale),
        "max_abs_scaled_integer_residual": int(max_abs),
        "exact_equal": bool(max_abs == 0),
    }


def error_metrics(got: np.ndarray, reference64: np.ndarray) -> dict:
    diff = got.astype(np.float64) - reference64
    denom = max(float(np.linalg.norm(reference64)), 1e-300)
    return {
        "relative_frobenius": float(np.linalg.norm(diff) / denom),
        "max_absolute": float(np.max(np.abs(diff))),
    }
