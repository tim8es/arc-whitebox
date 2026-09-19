"""E122 Haar-8 antipodal-simplex multi-source estimator.

The candidate keeps an eight-dimensional common source coefficient state and
compresses it to a fixed 18-codeword antipodal regular simplex per Haar frame.
It consumes only realized network weights and random source frames.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

PRODUCTION_DIM = 1024
PRODUCTION_WIDTH = 1024
PRODUCTION_DEPTH = 16
SOURCE_DIM = 8
SIMPLEX_VERTICES = SOURCE_DIM + 1
CODEWORDS = 2 * SIMPLEX_VERTICES
PRODUCTION_FRAMES = 224
PRODUCTION_DIRECTIONS = PRODUCTION_FRAMES * CODEWORDS
PRODUCTION_CAP_FLOPS = 136_758_472_261


@dataclass(frozen=True)
class SimplexSourceEstimate:
    mean: np.ndarray
    frame_orthogonality_max_abs: float
    source_direction_norm_max_abs: float
    ledger: dict
    finite: bool


def mean_chi(d: int) -> float:
    if d <= 0:
        raise ValueError("d must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma(0.5 * (d + 1.0)) - math.lgamma(0.5 * d)
    )


def regular_simplex_code(k: int = SOURCE_DIM) -> np.ndarray:
    """Return 2*(k+1) antipodal unit regular-simplex codewords in R^k."""
    if k <= 1:
        raise ValueError("k must be >1")
    helmert = np.zeros((k + 1, k), dtype=np.float64)
    for j in range(k):
        den = math.sqrt((j + 1.0) * (j + 2.0))
        helmert[: j + 1, j] = 1.0 / den
        helmert[j + 1, j] = -(j + 1.0) / den
    vertices = math.sqrt((k + 1.0) / k) * helmert
    return np.concatenate((vertices, -vertices), axis=0)


def simplex_algebra_metrics(code: np.ndarray) -> dict:
    c = np.asarray(code, dtype=np.float64)
    if c.ndim != 2 or c.shape[0] != 2 * (c.shape[1] + 1):
        raise ValueError("unexpected antipodal simplex shape")
    k = int(c.shape[1])
    m = k + 1
    vertices = c[:m]
    gram = vertices @ vertices.T
    target = np.full((m, m), -1.0 / k, dtype=np.float64)
    np.fill_diagonal(target, 1.0)
    second = (c.T @ c) / float(c.shape[0])
    return {
        "k": k,
        "codewords": int(c.shape[0]),
        "max_vertex_norm_error": float(
            np.max(np.abs(np.linalg.norm(vertices, axis=1) - 1.0))
        ),
        "max_vertex_gram_error": float(np.max(np.abs(gram - target))),
        "vertex_sum_inf": float(np.max(np.abs(np.sum(vertices, axis=0)))),
        "second_moment_max_abs_error": float(
            np.max(np.abs(second - np.eye(k, dtype=np.float64) / float(k)))
        ),
    }


def _validate_weights(weights: Sequence[np.ndarray]) -> tuple[int, int]:
    if not weights:
        raise ValueError("weights must be non-empty")
    first = np.asarray(weights[0])
    if first.ndim != 2:
        raise ValueError("weights must be matrices")
    input_dim = int(first.shape[0])
    if input_dim < SOURCE_DIM:
        raise ValueError(f"E122 requires input dimension >= {SOURCE_DIM}")
    previous = input_dim
    for idx, raw in enumerate(weights):
        w = np.asarray(raw)
        if w.ndim != 2 or w.shape[0] != previous or w.shape[1] <= 0:
            raise ValueError(
                f"weight {idx} has shape {w.shape}; expected ({previous}, next)"
            )
        if not np.isfinite(w).all():
            raise ValueError(f"weight {idx} contains non-finite values")
        previous = int(w.shape[1])
    return input_dim, previous


def _haar_k_frame(
    rng: np.random.Generator,
    d: int,
    k: int = SOURCE_DIM,
) -> tuple[np.ndarray, float]:
    if d < k:
        raise ValueError("d must be >= k")
    z = rng.standard_normal((d, k)).astype(np.float64)
    q = np.zeros((d, k), dtype=np.float64)
    for j in range(k):
        v = z[:, j].copy()
        for i in range(j):
            v -= q[:, i] * float(q[:, i] @ v)
        nv = float(np.linalg.norm(v))
        if not math.isfinite(nv) or nv <= 1e-15:
            raise RuntimeError("degenerate Haar frame column")
        q[:, j] = v / nv
    gram = q.T @ q
    orth = float(np.max(np.abs(gram - np.eye(k, dtype=np.float64))))
    return q, orth


def _propagate_batch(q: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(q, dtype=np.float64)
    for raw in weights:
        h = h @ np.asarray(raw, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def _candidate_ledger(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
    k: int = SOURCE_DIM,
) -> dict:
    d, out_width = _validate_weights(weights)
    j = 2 * (k + 1)
    n = frames * j

    simplex_setup = 8 * k * (k + 1) + 256
    frame_setup = frames * (d * (2 * k * k + 17 * k) + 64 * k)
    source_materialization = frames * (2 * d * k * j)

    layer_flops = []
    previous = d
    for raw in weights:
        out = int(np.asarray(raw).shape[1])
        layer = n * (2 * previous * out + 2 * out)
        layer_flops.append(int(layer))
        previous = out

    final_reduction = n * out_width + 2 * n + 5 * out_width
    total = int(
        simplex_setup
        + frame_setup
        + source_materialization
        + sum(layer_flops)
        + final_reduction
    )
    return {
        "simplex_setup_upper": int(simplex_setup),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source_materialization),
        "deep_layer_flops": layer_flops,
        "deep_propagation_upper": int(sum(layer_flops)),
        "final_reduction_radial_upper": int(final_reduction),
        "all_in_upper": total,
        "operation_classes_complete": [
            "static_helmert_simplex_and_antipodal_code",
            "haar8_gaussian_rng_norms_mgs_normalization",
            "dense_frame_times_source_code_materialization",
            "all_dense_layer_matmuls",
            "all_relu_operations",
            "final_output_reduction",
            "radial_mean_scaling",
        ],
    }


def haar8_antipodal_simplex_mean(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
    seed: int,
) -> SimplexSourceEstimate:
    d, out_width = _validate_weights(weights)
    if frames <= 0:
        raise ValueError("frames must be positive")

    code = regular_simplex_code(SOURCE_DIM)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    total = np.zeros(out_width, dtype=np.float64)
    orth_max = 0.0
    norm_max = 0.0

    for _ in range(frames):
        u, orth = _haar_k_frame(rng, d, SOURCE_DIM)
        orth_max = max(orth_max, orth)
        q = code @ u.T
        norms = np.linalg.norm(q, axis=1)
        norm_max = max(norm_max, float(np.max(np.abs(norms - 1.0))))
        y = _propagate_batch(q, weights)
        total += np.sum(y, axis=0, dtype=np.float64)

    n = frames * code.shape[0]
    mean = mean_chi(d) * total / float(n)
    ledger = _candidate_ledger(weights, frames=frames, k=SOURCE_DIM)
    finite = bool(
        np.isfinite(mean).all()
        and math.isfinite(orth_max)
        and math.isfinite(norm_max)
        and math.isfinite(float(ledger["all_in_upper"]))
    )
    return SimplexSourceEstimate(
        mean=mean,
        frame_orthogonality_max_abs=orth_max,
        source_direction_norm_max_abs=norm_max,
        ledger=ledger,
        finite=finite,
    )


def iid_spherical_mean(
    weights: Sequence[np.ndarray],
    *,
    samples: int,
    seed: int,
) -> np.ndarray:
    """Verifier comparator only; not part of the E122 candidate."""
    d, _ = _validate_weights(weights)
    if samples <= 0:
        raise ValueError("samples must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    z = rng.standard_normal((samples, d)).astype(np.float64)
    norms = np.linalg.norm(z, axis=1)
    if np.any(norms <= 0.0) or not np.isfinite(norms).all():
        raise RuntimeError("invalid iid direction norm")
    q = z / norms[:, None]
    return mean_chi(d) * np.mean(_propagate_batch(q, weights), axis=0, dtype=np.float64)


def production_cost_receipt() -> dict:
    d = PRODUCTION_DIM
    n = PRODUCTION_WIDTH
    l = PRODUCTION_DEPTH
    k = SOURCE_DIM
    j = CODEWORDS
    p = PRODUCTION_FRAMES
    trajectories = PRODUCTION_DIRECTIONS

    simplex_setup = 8 * k * (k + 1) + 256
    frame_setup = p * (d * (2 * k * k + 17 * k) + 64 * k)
    source = p * (2 * d * k * j)
    deep = trajectories * l * (2 * n * n + 2 * n)
    final = trajectories * n + 2 * trajectories + 5 * n
    total = simplex_setup + frame_setup + source + deep + final

    return {
        "dimension": d,
        "width": n,
        "depth": l,
        "source_dimension": k,
        "codewords_per_frame": j,
        "frames": p,
        "directions": trajectories,
        "simplex_setup_upper": int(simplex_setup),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source),
        "deep_propagation_upper": int(deep),
        "final_reduction_radial_upper": int(final),
        "all_in_upper": int(total),
        "hard_cap_flops": PRODUCTION_CAP_FLOPS,
        "slack_flops": int(PRODUCTION_CAP_FLOPS - total),
        "passes_cap": bool(total <= PRODUCTION_CAP_FLOPS),
    }
