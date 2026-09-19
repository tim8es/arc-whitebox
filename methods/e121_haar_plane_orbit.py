"""E121 Haar-plane cyclic-orbit source-memory estimator.

No activation regions, roots, masks tables, targets, or exact-reference objects
are consumed by this candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

PRODUCTION_DIM = 1024
PRODUCTION_DEPTH = 16
PRODUCTION_FRAMES = 128
PRODUCTION_PHASES = 64
PRODUCTION_BUDGET = 2**41
PRODUCTION_UTIL_CAP = 0.13


@dataclass(frozen=True)
class OrbitEstimate:
    mean: np.ndarray
    frame_orthogonality_max_abs: float
    ledger: dict
    finite: bool


def mean_chi(d: int) -> float:
    if d <= 0:
        raise ValueError("d must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma(0.5 * (d + 1.0)) - math.lgamma(0.5 * d)
    )


def _validate_weights(weights: Sequence[np.ndarray]) -> tuple[int, int]:
    if not weights:
        raise ValueError("weights must be non-empty")
    input_dim = int(np.asarray(weights[0]).shape[0])
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


def _haar_two_frame(
    rng: np.random.Generator,
    d: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    z = rng.standard_normal((d, 2)).astype(np.float64)
    u = z[:, 0]
    nu = float(np.linalg.norm(u))
    if not math.isfinite(nu) or nu <= 0.0:
        raise RuntimeError("degenerate first frame vector")
    u = u / nu

    v = z[:, 1] - u * float(u @ z[:, 1])
    nv = float(np.linalg.norm(v))
    if not math.isfinite(nv) or nv <= 1e-15:
        raise RuntimeError("degenerate second frame vector")
    v = v / nv

    gram = np.array(
        [[float(u @ u), float(u @ v)], [float(v @ u), float(v @ v)]],
        dtype=np.float64,
    )
    orth_error = float(np.max(np.abs(gram - np.eye(2, dtype=np.float64))))
    return u, v, orth_error


def _propagate_batch(
    q: np.ndarray,
    weights: Sequence[np.ndarray],
) -> np.ndarray:
    h = np.asarray(q, dtype=np.float64)
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        h = h @ w
        h = np.maximum(h, 0.0)
    return h


def _candidate_ledger(
    weights: Sequence[np.ndarray],
    frames: int,
    phases: int,
) -> dict:
    d, out_width = _validate_weights(weights)
    n = frames * phases

    frame_setup = frames * (32 * d + 64)
    phase_source = n * (64 + 3 * d)

    layer_flops = []
    previous = d
    for raw_w in weights:
        out = int(np.asarray(raw_w).shape[1])
        # Matmul: 2*in*out per trajectory. ReLU: conservative 2*out.
        layer = n * (2 * previous * out + 2 * out)
        layer_flops.append(int(layer))
        previous = out

    final_reduction = n * out_width + 5 * out_width
    total = int(frame_setup + phase_source + sum(layer_flops) + final_reduction)
    return {
        "frame_setup_upper": int(frame_setup),
        "phase_source_materialization_upper": int(phase_source),
        "deep_layer_flops": layer_flops,
        "deep_propagation_upper": int(sum(layer_flops)),
        "final_reduction_materialization_upper": int(final_reduction),
        "all_in_upper": total,
        "utilization_vs_2pow41": total / float(PRODUCTION_BUDGET),
        "operation_classes_complete": [
            "frame_rng_norm_projection_normalization",
            "phase_trigonometry_and_source_materialization",
            "all_dense_layer_matmuls",
            "all_relu_operations",
            "final_output_reduction",
            "radial_mean_scaling",
        ],
    }


def haar_plane_orbit_mean(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
    phases: int,
    seed: int,
) -> OrbitEstimate:
    d, out_width = _validate_weights(weights)
    if frames <= 0 or phases <= 0 or phases % 2:
        raise ValueError("frames>0 and positive even phases required")

    rng = np.random.Generator(np.random.PCG64(int(seed)))
    theta = (2.0 * math.pi / phases) * np.arange(phases, dtype=np.float64)
    ct = np.cos(theta)
    st = np.sin(theta)

    total = np.zeros(out_width, dtype=np.float64)
    orth_max = 0.0

    for _ in range(frames):
        u, v, orth_error = _haar_two_frame(rng, d)
        orth_max = max(orth_max, orth_error)
        q = ct[:, None] * u[None, :] + st[:, None] * v[None, :]
        y = _propagate_batch(q, weights)
        total += np.sum(y, axis=0, dtype=np.float64)

    n = frames * phases
    mean = mean_chi(d) * (total / float(n))
    ledger = _candidate_ledger(weights, frames, phases)
    finite = bool(
        np.isfinite(mean).all()
        and math.isfinite(orth_max)
        and all(math.isfinite(float(v)) for v in [
            ledger["all_in_upper"],
            ledger["utilization_vs_2pow41"],
        ])
    )
    return OrbitEstimate(
        mean=mean,
        frame_orthogonality_max_abs=orth_max,
        ledger=ledger,
        finite=finite,
    )


def iid_spherical_mean(
    weights: Sequence[np.ndarray],
    *,
    samples: int,
    seed: int,
) -> np.ndarray:
    """Target-free same-node iid spherical comparator; not the E121 candidate."""
    d, _ = _validate_weights(weights)
    if samples <= 0:
        raise ValueError("samples must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    z = rng.standard_normal((samples, d)).astype(np.float64)
    norms = np.linalg.norm(z, axis=1)
    if np.any(norms <= 0.0) or not np.isfinite(norms).all():
        raise RuntimeError("invalid iid direction norm")
    q = z / norms[:, None]
    y = _propagate_batch(q, weights)
    return mean_chi(d) * np.mean(y, axis=0, dtype=np.float64)


def production_cost_receipt() -> dict:
    """Frozen all-in production upper recomputed independently of a run."""
    d = PRODUCTION_DIM
    p = PRODUCTION_FRAMES
    m = PRODUCTION_PHASES
    n = p * m
    l = PRODUCTION_DEPTH

    frame_setup = p * (32 * d + 64)
    phase_source = n * (64 + 3 * d)
    per_layer = n * (2 * d * d + 2 * d)
    deep = l * per_layer
    final = n * d + 5 * d
    total = frame_setup + phase_source + deep + final
    cap_flops = PRODUCTION_UTIL_CAP * PRODUCTION_BUDGET

    return {
        "dimension": d,
        "depth": l,
        "frames": p,
        "phases": m,
        "directions": n,
        "frame_setup_upper": int(frame_setup),
        "phase_source_materialization_upper": int(phase_source),
        "per_layer_deep_upper": int(per_layer),
        "deep_propagation_upper": int(deep),
        "final_reduction_materialization_upper": int(final),
        "all_in_upper": int(total),
        "budget": PRODUCTION_BUDGET,
        "utilization": total / float(PRODUCTION_BUDGET),
        "utilization_cap": PRODUCTION_UTIL_CAP,
        "cap_flops": cap_flops,
        "slack_flops": cap_flops - total,
        "passes_cap": bool(total <= cap_flops),
    }
