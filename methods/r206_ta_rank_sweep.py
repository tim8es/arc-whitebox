"""R206 bounded synthetic rank sweep around the pinned R202 TA32 kernel.

Reuses the R202 rational/sparse kernel conventions, generalized only to the four
pre-registered LITA tensor dimensions. This is not a compiler.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from time import perf_counter

import numpy as np

from methods.r202_ta32_kernel import Axis, error_metrics, git_blob_sha1, sha256_file

MECHANISM_RATIO_GATE = 0.42
STABILITY_RATIO_GATE = 1.05
LITA_COMMIT = "c1dd9225df98676e385b53ae7517ff2ea0ec5779"

FROZEN_SCHEMES = (
    (26, 8052, "be5a2f9131ef77c3c3351dc1d218d21ec6845368"),
    (28, 9847, "af512cdf847f49d02c97de7d328c8b611ac1a12f"),
    (30, 11890, "0cd64a9423d228b0336b07449d65f26931c5bd35"),
    (32, 14197, "6f2dea4820245303dc2eb1fba13816436fabe54d"),
)


@dataclass(frozen=True)
class GenericScheme:
    dim: int
    rank: int
    u: Axis
    v: Axis
    w: Axis
    metadata: dict
    git_blob_sha1: str
    sha256: str


def load_generic_scheme(path: str | Path, dim: int, rank: int, expected_blob: str) -> GenericScheme:
    path = Path(path)
    raw = path.read_bytes()
    actual_blob = git_blob_sha1(raw)
    if actual_blob != expected_blob:
        raise ValueError(f"scheme Git blob mismatch: expected {expected_blob}, got {actual_blob}")
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
    scheme = GenericScheme(
        dim=dim,
        rank=rank,
        u=axes["u"],
        v=axes["v"],
        w=axes["w"],
        metadata=metadata,
        git_blob_sha1=actual_blob,
        sha256=sha256_file(path),
    )
    if metadata.get("tensor") != [dim, dim, dim] or metadata.get("rank") != rank:
        raise ValueError(f"metadata mismatch: {metadata}")
    if not (scheme.u.rows == scheme.v.rows == scheme.w.rows == rank):
        raise ValueError("axis rank mismatch")
    if any(np.any(ax.indices < 0) or np.any(ax.indices >= dim * dim)
           for ax in (scheme.u, scheme.v, scheme.w)):
        raise ValueError("scheme index outside tensor coordinate space")
    return scheme


def _blocks(x: np.ndarray, dim: int) -> np.ndarray:
    m, n = x.shape
    if m % dim or n % dim:
        raise ValueError("matrix is not padded to tensor dimension")
    bm, bn = m // dim, n // dim
    return x.reshape(dim, bm, dim, bn).transpose(0, 2, 1, 3).reshape(dim * dim, bm, bn)


def _unblocks(blocks: np.ndarray, dim: int, m: int, n: int) -> np.ndarray:
    bm, bn = m // dim, n // dim
    return blocks.reshape(dim, dim, bm, bn).transpose(0, 2, 1, 3).reshape(m, n)


def _csr(axis: Axis, dim: int, dtype: np.dtype):
    from scipy.sparse import csr_matrix

    return csr_matrix(
        (axis.coefficients(dtype), axis.indices, axis.indptr),
        shape=(axis.rows, dim * dim),
        dtype=dtype,
    )


def sweep_cost(scheme: GenericScheme, m: int, k: int, n: int) -> dict:
    d = scheme.dim
    mp = math.ceil(m / d) * d
    kp = math.ceil(k / d) * d
    np_ = math.ceil(n / d) * d
    bm, bk, bn = mp // d, kp // d, np_ // d

    u_elems, v_elems, w_elems = bm * bk, bk * bn, bm * bn
    coeff = {
        "u": scheme.u.nnz * u_elems,
        "v": scheme.v.nnz * v_elems,
        "w": scheme.w.nnz * w_elems,
    }
    additions = {
        "u": int(np.maximum(scheme.u.row_nnz() - 1, 0).sum()) * u_elems,
        "v": int(np.maximum(scheme.v.row_nnz() - 1, 0).sum()) * v_elems,
    }
    w_counts = np.bincount(scheme.w.indices, minlength=d * d)
    additions["w_reconstruction"] = int(np.maximum(w_counts - 1, 0).sum()) * w_elems

    leaf = scheme.rank * 2 * bm * bk * bn
    full = leaf + sum(coeff.values()) + sum(additions.values())
    classical = 2 * m * k * n
    return {
        "tensor_dim": d,
        "rank": scheme.rank,
        "shape": [m, k, n],
        "padded_shape": [mp, kp, np_],
        "block_shape": [bm, bk, bn],
        "nnz": {"u": scheme.u.nnz, "v": scheme.v.nnz, "w": scheme.w.nnz},
        "coefficient_multiplies": {k_: int(v) for k_, v in coeff.items()},
        "linear_combination_additions": {k_: int(v) for k_, v in additions.items()},
        "leaf_matmul_flops": int(leaf),
        "full_arithmetic_flops": int(full),
        "classical_unpadded_flops": int(classical),
        "leaf_ratio": float(leaf / classical),
        "full_ratio": float(full / classical),
        "padding_input_scalars_copied": int(
            (mp * kp + kp * np_) if (mp, kp, np_) != (m, k, n) else 0
        ),
        "crop_output_scalars_copied": int(mp * np_ if (mp, np_) != (m, n) else 0),
        "copy_flops_by_convention": 0,
        "fallback_count": 0,
        "fallback_flops": 0,
    }


def ta_matmul(a: np.ndarray, b: np.ndarray, scheme: GenericScheme) -> tuple[np.ndarray, dict]:
    if a.dtype != np.float32 or b.dtype != np.float32:
        raise TypeError("R206 probe is frozen to float32")
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError("matmul shape mismatch")
    m, k = a.shape
    _, n = b.shape
    d = scheme.dim
    mp = math.ceil(m / d) * d
    kp = math.ceil(k / d) * d
    np_ = math.ceil(n / d) * d

    ap = np.zeros((mp, kp), dtype=np.float32)
    bp = np.zeros((kp, np_), dtype=np.float32)
    ap[:m, :k] = a
    bp[:k, :n] = b
    ab, bb = _blocks(ap, d), _blocks(bp, d)
    bm, bk = ab.shape[1:]
    _, bn = bb.shape[1:]

    u, v, w = _csr(scheme.u, d, np.float32), _csr(scheme.v, d, np.float32), _csr(
        scheme.w, d, np.float32
    )
    t0 = perf_counter()
    x = np.asarray(u @ ab.reshape(d * d, -1), dtype=np.float32)
    t1 = perf_counter()
    y = np.asarray(v @ bb.reshape(d * d, -1), dtype=np.float32)
    t2 = perf_counter()
    p = np.matmul(x.reshape(scheme.rank, bm, bk), y.reshape(scheme.rank, bk, bn))
    t3 = perf_counter()
    cb = np.asarray(w.T @ p.reshape(scheme.rank, -1), dtype=np.float32)
    t4 = perf_counter()
    outp = _unblocks(cb.reshape(d * d, bm, bn), d, mp, np_)
    out = np.array(outp[:m, :n], copy=True)
    t5 = perf_counter()
    return out, {
        "u_form_seconds": t1 - t0,
        "v_form_seconds": t2 - t1,
        "leaf_seconds": t3 - t2,
        "w_reconstruct_seconds": t4 - t3,
        "crop_copy_seconds": t5 - t4,
        "total_seconds": t5 - t0,
    }


def coefficient_grid(scheme: GenericScheme) -> int:
    grid = 1
    for axis in (scheme.u, scheme.v, scheme.w):
        for den in np.unique(axis.denominators):
            grid = math.lcm(grid, int(den))
    return grid


def exact_identity(scheme: GenericScheme, a: np.ndarray, b: np.ndarray) -> dict:
    d = scheme.dim
    if a.shape != (d, d) or b.shape != (d, d):
        raise ValueError("exact fixture dimension mismatch")
    grid = coefficient_grid(scheme)
    ai, bi = [int(x) for x in a.reshape(-1)], [int(x) for x in b.reshape(-1)]

    def scaled(axis: Axis) -> list[int]:
        return [
            int(num) * (grid // int(den))
            for num, den in zip(axis.numerators.tolist(), axis.denominators.tolist())
        ]

    us, vs, ws = scaled(scheme.u), scaled(scheme.v), scaled(scheme.w)
    accum = [0] * (d * d)
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
    residual = [accum[i] - int(ref.reshape(-1)[i]) * scale for i in range(d * d)]
    max_abs = max(abs(x) for x in residual)
    return {
        "coefficient_grid": int(grid),
        "max_abs_scaled_integer_residual": int(max_abs),
        "exact_equal": bool(max_abs == 0),
    }


def stability(got: np.ndarray, parent: np.ndarray, reference64: np.ndarray) -> dict:
    cand = error_metrics(got, reference64)
    base = error_metrics(parent, reference64)
    checks = {}
    for metric in ("relative_frobenius", "max_absolute"):
        ratio = cand[metric] / base[metric] if base[metric] else math.inf
        checks[metric] = {
            "parent": base[metric],
            "candidate": cand[metric],
            "ratio_candidate_to_parent": float(ratio),
            "pass": bool(ratio <= STABILITY_RATIO_GATE),
        }
    return {"checks": checks, "pass": all(v["pass"] for v in checks.values())}
