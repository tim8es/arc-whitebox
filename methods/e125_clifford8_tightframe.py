"""E125 Clifford-8 rational signed-permutation multi-source estimator.

The candidate uses one independent spherical base direction per frame and an
exact algebraic family of eight signed-permutation Clifford operators.  No
iterative frame orthogonalization is used.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


K = 8
J = 16
DEFAULT_FRAMES = 252
HARD_CAP_FLOPS = 136_758_472_261

_I2 = np.array([[1, 0], [0, 1]], dtype=np.int8)
_X2 = np.array([[0, 1], [1, 0]], dtype=np.int8)
_Z2 = np.array([[1, 0], [0, -1]], dtype=np.int8)
_J2 = np.array([[0, 1], [-1, 0]], dtype=np.int8)

_BASE = {"I": _I2, "X": _X2, "Z": _Z2, "J": _J2}
_STRINGS = ("III", "IIJ", "IJX", "XJZ", "ZJZ", "JIZ", "JXX", "JZX")


@dataclass(frozen=True)
class FrameDiagnostics:
    base_norm_abs_error: float
    gram_max_abs_error: float


@dataclass(frozen=True)
class EstimateResult:
    prediction: np.ndarray
    max_base_norm_abs_error: float
    max_frame_gram_abs_error: float
    operation_ledger: dict


def _kron_string(code: str) -> np.ndarray:
    out = np.array([[1]], dtype=np.int8)
    for ch in code:
        out = np.kron(out, _BASE[ch]).astype(np.int8, copy=False)
    return out


def clifford8_integer_operators() -> tuple[np.ndarray, ...]:
    return tuple(_kron_string(code) for code in _STRINGS)


def exact_clifford_algebra_report() -> dict:
    ops = clifford8_integer_operators()
    eye = np.eye(8, dtype=np.int64)
    signed_permutation = True
    orthogonal = True
    skew_nonidentity = True
    square_minus_identity = True
    anticommute = True

    for i, raw in enumerate(ops):
        a = raw.astype(np.int64)
        signed_permutation &= bool(
            np.all(np.sum(np.abs(a), axis=0) == 1)
            and np.all(np.sum(np.abs(a), axis=1) == 1)
            and np.all((a == 0) | (a == 1) | (a == -1))
        )
        orthogonal &= np.array_equal(a.T @ a, eye)
        if i == 0:
            skew_nonidentity &= np.array_equal(a, eye)
        else:
            skew_nonidentity &= np.array_equal(a.T, -a)
            square_minus_identity &= np.array_equal(a @ a, -eye)

    for i in range(1, K):
        ai = ops[i].astype(np.int64)
        for j in range(i + 1, K):
            aj = ops[j].astype(np.int64)
            anticommute &= np.array_equal(ai @ aj, -(aj @ ai))

    return {
        "strings": list(_STRINGS),
        "entries_integer_zero_plusminus_one": all(
            np.all((a == 0) | (a == 1) | (a == -1)) for a in ops
        ),
        "signed_permutation_all": bool(signed_permutation),
        "orthogonal_all": bool(orthogonal),
        "identity_a0_and_skew_nonidentity": bool(skew_nonidentity),
        "square_minus_identity_nonidentity": bool(square_minus_identity),
        "pairwise_anticommutation_nonidentity": bool(anticommute),
        "pass": bool(
            signed_permutation
            and orthogonal
            and skew_nonidentity
            and square_minus_identity
            and anticommute
        ),
    }


def _operator_permutation_sign(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rows = np.asarray(a, dtype=np.int8)
    perm = np.argmax(np.abs(rows), axis=1).astype(np.int64)
    signs = rows[np.arange(8), perm].astype(np.float64)
    return perm, signs


def _positive_frame_from_unit_q(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    d = int(q.size)
    if d <= 0 or d % 8:
        raise ValueError("E125 requires dimension divisible by 8")
    blocks = q.reshape(d // 8, 8)
    rows = []
    for a in clifford8_integer_operators():
        perm, signs = _operator_permutation_sign(a)
        transformed = blocks[:, perm] * signs[None, :]
        rows.append(transformed.reshape(d))
    return np.stack(rows, axis=0)


def source_frame_from_unit_q(q: np.ndarray) -> tuple[np.ndarray, FrameDiagnostics]:
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    norm = float(np.linalg.norm(q))
    positives = _positive_frame_from_unit_q(q)
    gram = positives @ positives.T
    target = np.eye(K, dtype=np.float64) * (norm * norm)
    gram_error = float(np.max(np.abs(gram - target)))
    sources = np.concatenate((positives, -positives), axis=0)
    return sources, FrameDiagnostics(
        base_norm_abs_error=abs(norm - 1.0),
        gram_max_abs_error=gram_error,
    )


def mean_chi_radius(d: int) -> float:
    if d <= 0:
        raise ValueError("dimension must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma((d + 1.0) / 2.0) - math.lgamma(d / 2.0)
    )


def propagate_zero_bias_relu(
    directions: np.ndarray,
    weights: Sequence[np.ndarray],
) -> np.ndarray:
    h = np.asarray(directions, dtype=np.float64)
    if h.ndim != 2:
        raise ValueError("directions must be 2-D")
    previous = h.shape[1]
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError(
                f"weight {idx} shape {w.shape} incompatible with width {previous}"
            )
        if not np.isfinite(w).all():
            raise ValueError("non-finite weight")
        h = h @ w
        np.maximum(h, 0.0, out=h)
        previous = w.shape[1]
    return h


def estimate(
    weights: Sequence[np.ndarray],
    *,
    seed: int,
    frames: int = DEFAULT_FRAMES,
) -> EstimateResult:
    if not weights:
        raise ValueError("weights must be non-empty")
    d = int(np.asarray(weights[0]).shape[0])
    if d % 8:
        raise ValueError("input dimension must be divisible by 8")
    if frames <= 0:
        raise ValueError("frames must be positive")

    rng = np.random.Generator(np.random.PCG64(int(seed)))
    final_width = int(np.asarray(weights[-1]).shape[1])
    total = np.zeros(final_width, dtype=np.float64)
    max_norm_error = 0.0
    max_gram_error = 0.0

    for _ in range(frames):
        g = rng.standard_normal(d).astype(np.float64)
        g_norm = float(np.linalg.norm(g))
        if not math.isfinite(g_norm) or g_norm <= 0.0:
            raise FloatingPointError("invalid Gaussian base norm")
        q = g / g_norm
        sources, diag = source_frame_from_unit_q(q)
        values = propagate_zero_bias_relu(sources, weights)
        total += np.mean(values, axis=0, dtype=np.float64)
        max_norm_error = max(max_norm_error, diag.base_norm_abs_error)
        max_gram_error = max(max_gram_error, diag.gram_max_abs_error)

    prediction = mean_chi_radius(d) * total / float(frames)
    if not np.isfinite(prediction).all():
        raise FloatingPointError("non-finite E125 prediction")

    return EstimateResult(
        prediction=prediction,
        max_base_norm_abs_error=max_norm_error,
        max_frame_gram_abs_error=max_gram_error,
        operation_ledger=production_operation_ledger(),
    )


def per_output_unit_sphere_bound(weights: Sequence[np.ndarray]) -> np.ndarray:
    if not weights:
        raise ValueError("weights must be non-empty")
    w0 = np.asarray(weights[0], dtype=np.float64)
    if w0.ndim != 2:
        raise ValueError("weight 0 must be 2-D")
    bound = np.sqrt(np.sum(w0 * w0, axis=0, dtype=np.float64))
    previous = w0.shape[1]

    for idx, raw in enumerate(weights[1:], start=1):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError(
                f"weight {idx} shape {w.shape} incompatible with width {previous}"
            )
        bound = np.abs(w).T @ bound
        previous = w.shape[1]

    if not np.isfinite(bound).all() or np.any(bound < 0.0):
        raise FloatingPointError("invalid deterministic output bound")
    return bound


def finite_sample_mse_certificate(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
    delta: float,
) -> dict:
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must lie in (0,1)")
    if frames <= 0:
        raise ValueError("frames must be positive")
    d = int(np.asarray(weights[0]).shape[0])
    bound = per_output_unit_sphere_bound(weights)
    n = int(bound.size)
    log_term = math.log((2.0 * n) / delta)
    factor = math.sqrt(log_term / (2.0 * frames))
    coordinate_bounds = mean_chi_radius(d) * bound * factor
    mse_bound = float(np.mean(coordinate_bounds * coordinate_bounds))
    return {
        "dimension": d,
        "output_width": n,
        "frames": int(frames),
        "delta": float(delta),
        "mean_chi_radius": mean_chi_radius(d),
        "log_term": log_term,
        "unit_sphere_output_bound": bound,
        "coordinate_abs_error_bound": coordinate_bounds,
        "mse_bound": mse_bound,
    }


def production_operation_ledger(
    *,
    d: int = 1024,
    n: int = 1024,
    depth: int = 16,
    k: int = K,
    j: int = J,
    frames: int = DEFAULT_FRAMES,
) -> dict:
    directions = frames * j
    static_clifford = 70_000
    base_rng = frames * (16 * d)
    base_norm_normalize = frames * (3 * d + 64)
    source_materialization = frames * (16 * d)
    runtime_gram = frames * (2 * d * k * k + k * k)
    deep_propagation = directions * depth * (2 * n * n + 2 * n)
    final_reduction = directions * n + 2 * directions + 5 * n
    all_in = (
        static_clifford
        + base_rng
        + base_norm_normalize
        + source_materialization
        + runtime_gram
        + deep_propagation
        + final_reduction
    )
    return {
        "dimension": int(d),
        "width": int(n),
        "depth": int(depth),
        "source_dimension": int(k),
        "codewords_per_frame": int(j),
        "frames": int(frames),
        "directions": int(directions),
        "static_clifford_algebra_upper": int(static_clifford),
        "base_gaussian_rng_upper": int(base_rng),
        "base_norm_and_normalization_upper": int(base_norm_normalize),
        "signed_permutation_source_materialization_upper": int(source_materialization),
        "runtime_frame_gram_norm_orthogonality_upper": int(runtime_gram),
        "deep_propagation_upper": int(deep_propagation),
        "final_reduction_radial_upper": int(final_reduction),
        "all_in_upper": int(all_in),
        "hard_cap_flops": int(HARD_CAP_FLOPS),
        "slack_flops": int(HARD_CAP_FLOPS - all_in),
        "gate_passed": bool(all_in <= HARD_CAP_FLOPS),
    }
