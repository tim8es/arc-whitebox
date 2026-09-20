"""E137-H137 Stage-A helpers: target-free CountSketch diagnostic for pinned V25."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Any

import numpy as np

PINNED_V25_GIT_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
SKETCH_WIDTH = 512
WIDTH = 1024
BUDGET = 2**41
D21_REL_GATE = 0.022


def git_blob_sha1_bytes(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def balanced_countsketch_plan(n: int, s: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    if n != 2 * s:
        raise ValueError("frozen H137 plan requires n == 2*s")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    perm = rng.permutation(n).reshape(s, 2)
    signs = rng.integers(0, 2, size=n, dtype=np.int8).astype(np.float64)
    signs = signs * 2.0 - 1.0
    return perm.astype(np.int64), signs


def sketch_last_axis(x: np.ndarray, perm: np.ndarray, signs: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    if a.shape[-1] != signs.shape[0]:
        raise ValueError("last axis does not match sketch plan")
    left = a[..., perm[:, 0]] * signs[perm[:, 0]]
    right = a[..., perm[:, 1]] * signs[perm[:, 1]]
    return left + right


def sketched_product(x: np.ndarray, y: np.ndarray, *, layer: int, s: int = SKETCH_WIDTH) -> np.ndarray:
    """Approximate sum_k X[k] @ Y[k].T with a frozen balanced CountSketch."""
    xx = np.asarray(x, dtype=np.float64)
    yy = np.asarray(y, dtype=np.float64)
    if xx.ndim != 3 or yy.ndim != 3:
        raise ValueError("expected rank-3 stacked operands")
    if xx.shape[0] != yy.shape[0] or xx.shape[2] != yy.shape[2]:
        raise ValueError("incompatible contraction operands")
    n = int(xx.shape[2])
    perm, signs = balanced_countsketch_plan(n, s, 137_512_000 + int(layer))
    xs = sketch_last_axis(xx, perm, signs)
    ys = sketch_last_axis(yy, perm, signs)
    return np.einsum("kis,kqs->iq", xs, ys, optimize=False)


def contraction_flops_exact(k: int, n: int, q: int) -> int:
    return int(2 * k * n * q * n)


def contraction_flops_sketch(k: int, n: int, q: int, s: int = SKETCH_WIDTH) -> int:
    # Frozen conservative charge from Stage-A protocol.
    return int(3 * k * n * n + 3 * k * q * n + 2 * k * n * q * s)


@dataclass
class LayerRecord:
    layer: int
    ka: int
    kb: int
    factor_rel_error: float
    lifted_rel_error: float
    exact_norm_sq: float
    error_norm_sq: float
    exact_contract_formula_flops: int
    sketch_contract_upper_flops: int


class H137Hook:
    def __init__(self) -> None:
        self.records: list[LayerRecord] = []

    def exact_einsum(self, fnp: Any, flops: Any, x: Any, y: Any) -> Any:
        with flops.namespace("e137_old_exact"):
            return fnp.einsum("kij,kqj->iq", x, y)

    def capture(
        self,
        *,
        k: int,
        LA: Any,
        LP: Any,
        FAo: Any,
        FPo: Any,
        FA2: Any,
        FP2: Any,
        U2: Any,
        Qc: Any,
        kb: int,
        ka: int,
        exact_inner: Any,
    ) -> None:
        layer = int(k)
        la = np.asarray(LA, dtype=np.float64)
        lp = np.asarray(LP, dtype=np.float64)
        qc = np.asarray(Qc, dtype=np.float64)
        exact = np.asarray(exact_inner, dtype=np.float64)

        approx: np.ndarray | None = None
        exact_formula = 0
        sketch_formula = 0
        n = int(la.shape[1])

        if ka > kb:
            fa = np.asarray(FAo, dtype=np.float64)
            fp = np.asarray(FPo, dtype=np.float64)
            k1 = int(ka - kb)
            q1 = int(fa.shape[1])
            a = sketched_product(la[kb:ka], fa, layer=layer)
            p = sketched_product(lp[kb:ka], fp, layer=layer)
            approx = a + p
            exact_formula += 2 * contraction_flops_exact(k1, n, q1)
            sketch_formula += 2 * contraction_flops_sketch(k1, n, q1)

        if kb > 0:
            fa2 = np.asarray(FA2, dtype=np.float64)
            fp2 = np.asarray(FP2, dtype=np.float64)
            u2 = np.asarray(U2, dtype=np.float64)
            k2 = int(kb)
            q2 = int(fa2.shape[1])
            a2 = sketched_product(la[:kb], fa2, layer=layer)
            p2 = sketched_product(lp[:kb], fp2, layer=layer)
            lifted = (a2 + p2) @ u2.T
            approx = lifted if approx is None else approx + lifted
            exact_formula += 2 * contraction_flops_exact(k2, n, q2)
            sketch_formula += 2 * contraction_flops_sketch(k2, n, q2)

        if approx is None:
            raise RuntimeError("capture called without old-tier sources")

        err = approx - exact
        exact_norm = float(np.linalg.norm(exact))
        err_norm = float(np.linalg.norm(err))
        factor_rel = err_norm / max(exact_norm, 2.0 ** -100)

        exact_lifted = exact @ qc.T
        approx_lifted = approx @ qc.T
        lift_err = approx_lifted - exact_lifted
        lifted_norm = float(np.linalg.norm(exact_lifted))
        lifted_err_norm = float(np.linalg.norm(lift_err))
        lifted_rel = lifted_err_norm / max(lifted_norm, 2.0 ** -100)

        self.records.append(
            LayerRecord(
                layer=layer,
                ka=int(ka),
                kb=int(kb),
                factor_rel_error=float(factor_rel),
                lifted_rel_error=float(lifted_rel),
                exact_norm_sq=float(lifted_norm * lifted_norm),
                error_norm_sq=float(lifted_err_norm * lifted_err_norm),
                exact_contract_formula_flops=int(exact_formula),
                sketch_contract_upper_flops=int(sketch_formula),
            )
        )


def patch_v25_source(source: str) -> str:
    """Instrument pinned V25 in memory without changing exact state evolution."""
    marker = '            D21 = inner @ Qc.T\n'
    if source.count(marker) != 1:
        raise RuntimeError(f"expected one old-tier D21 marker, got {source.count(marker)}")

    # Namespace the four old-tier exact factor contractions so their actual flopscope bill
    # is observable. Arithmetic is unchanged.
    replacements = {
        'fnp.einsum("kij,kqj->iq", LA[kb:ka], FAo)':
            'E137_HOOK.exact_einsum(fnp, flops, LA[kb:ka], FAo)',
        'fnp.einsum("kij,kqj->iq", LP[kb:ka], FPo)':
            'E137_HOOK.exact_einsum(fnp, flops, LP[kb:ka], FPo)',
        'fnp.einsum("kij,kqj->iq", LA[:kb], FA2)':
            'E137_HOOK.exact_einsum(fnp, flops, LA[:kb], FA2)',
        'fnp.einsum("kij,kqj->iq", LP[:kb], FP2)':
            'E137_HOOK.exact_einsum(fnp, flops, LP[:kb], FP2)',
    }
    patched = source
    for old, new in replacements.items():
        if old not in patched:
            raise RuntimeError(f"missing pinned V25 anchor: {old}")
        patched = patched.replace(old, new, 1)

    inject = (
        '            E137_HOOK.capture(k=k, LA=LA, LP=LP, FAo=FAo, FPo=FPo, '
        'FA2=FA2, FP2=FP2, U2=U2, Qc=Qc, kb=kb, ka=ka, exact_inner=inner)\n'
        '            D21 = inner @ Qc.T\n'
    )
    return patched.replace(marker, inject, 1)


def summarize_records(records: list[LayerRecord]) -> dict[str, float | int | bool]:
    if not records:
        return {
            "measurement_count": 0,
            "pooled_relative_d21_error": math.inf,
            "max_layer_relative_d21_error": math.inf,
            "max_factor_vs_lifted_rel_error_gap": math.inf,
            "exact_contract_formula_flops": 0,
            "sketch_contract_upper_flops": 0,
            "finite": False,
        }
    exact_sq = sum(r.exact_norm_sq for r in records)
    err_sq = sum(r.error_norm_sq for r in records)
    pooled = math.sqrt(err_sq / max(exact_sq, 2.0 ** -200))
    return {
        "measurement_count": len(records),
        "pooled_relative_d21_error": float(pooled),
        "max_layer_relative_d21_error": float(max(r.lifted_rel_error for r in records)),
        "max_factor_vs_lifted_rel_error_gap": float(
            max(abs(r.factor_rel_error - r.lifted_rel_error) for r in records)
        ),
        "exact_contract_formula_flops": int(sum(r.exact_contract_formula_flops for r in records)),
        "sketch_contract_upper_flops": int(sum(r.sketch_contract_upper_flops for r in records)),
        "finite": bool(
            all(
                math.isfinite(r.factor_rel_error)
                and math.isfinite(r.lifted_rel_error)
                and math.isfinite(r.exact_norm_sq)
                and math.isfinite(r.error_norm_sq)
                for r in records
            )
        ),
    }
