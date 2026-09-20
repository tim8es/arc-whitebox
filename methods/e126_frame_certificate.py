"""E126 target-free finite-sample certificate for algebraic Haar-frame estimators."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

SOURCE_DIM = 8
CODEWORDS = 18
DELTA = 0.05
RAW_MSE_CAP = 1.89e-8
RMS_CAP = math.sqrt(RAW_MSE_CAP)
PRODUCTION_BASE_FLOPS = 149_114_550_960
TOTAL_BUDGET = 2**41
TOTAL_CAP_FLOPS = math.floor(0.13 * TOTAL_BUDGET)
INCREMENTAL_CAP_FLOPS = TOTAL_CAP_FLOPS - PRODUCTION_BASE_FLOPS


@dataclass(frozen=True)
class CertifiedFrameEstimate:
    mean: np.ndarray
    frame_contributions: np.ndarray
    sample_variance: np.ndarray
    frobenius_range: np.ndarray
    coordinate_radii: np.ndarray
    rms_certificate: float
    variance_only_rms: float
    frame_orthogonality_max_abs: float
    source_direction_norm_max_abs: float
    observed_range_violation_max_abs: float
    ledger: dict
    finite: bool


def mean_chi(d: int) -> float:
    if d <= 0:
        raise ValueError("d must be positive")
    return math.sqrt(2.0) * math.exp(
        math.lgamma(0.5 * (d + 1.0)) - math.lgamma(0.5 * d)
    )


def regular_simplex_code(k: int = SOURCE_DIM) -> np.ndarray:
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
    k = int(c.shape[1])
    m = k + 1
    vertices = c[:m]
    gram = vertices @ vertices.T
    target = np.full((m, m), -1.0 / k, dtype=np.float64)
    np.fill_diagonal(target, 1.0)
    second = (c.T @ c) / float(c.shape[0])
    return {
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
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2:
        raise ValueError("weights must be matrices")
    d = int(first.shape[0])
    if d < SOURCE_DIM:
        raise ValueError("input dimension must be >= 8")
    previous = d
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous or w.shape[1] <= 0:
            raise ValueError(f"bad weight shape at layer {idx}: {w.shape}")
        if not np.isfinite(w).all():
            raise ValueError("non-finite weight")
        previous = int(w.shape[1])
    return d, previous


def _haar_frame(
    rng: np.random.Generator,
    d: int,
    k: int = SOURCE_DIM,
) -> tuple[np.ndarray, float]:
    z = rng.standard_normal((d, k)).astype(np.float64)
    q = np.zeros((d, k), dtype=np.float64)
    for j in range(k):
        v = z[:, j].copy()
        for i in range(j):
            v -= q[:, i] * float(q[:, i] @ v)
        nv = float(np.linalg.norm(v))
        if not math.isfinite(nv) or nv <= 1e-15:
            raise RuntimeError("degenerate Haar frame")
        q[:, j] = v / nv
    orth = float(
        np.max(np.abs(q.T @ q - np.eye(k, dtype=np.float64)))
    )
    return q, orth


def _forward_batch(x: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for raw in weights:
        h = h @ np.asarray(raw, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def frobenius_range_envelope(weights: Sequence[np.ndarray]) -> np.ndarray:
    d, out_width = _validate_weights(weights)
    if len(weights) == 1:
        prefix = 1.0
    else:
        prefix = 1.0
        for raw in weights[:-1]:
            prefix *= float(np.linalg.norm(np.asarray(raw, dtype=np.float64), ord="fro"))
    last = np.asarray(weights[-1], dtype=np.float64)
    column_norm = np.sqrt(np.sum(last * last, axis=0, dtype=np.float64))
    envelope = mean_chi(d) * prefix * column_norm
    if envelope.shape != (out_width,):
        raise RuntimeError("range shape mismatch")
    return envelope


def spectral_range_envelope_verifier_only(
    weights: Sequence[np.ndarray],
) -> np.ndarray:
    """Tightness diagnostic only; production cost does not assume free SVDs."""
    d, out_width = _validate_weights(weights)
    prefix = 1.0
    if len(weights) > 1:
        for raw in weights[:-1]:
            prefix *= float(np.linalg.norm(np.asarray(raw, dtype=np.float64), ord=2))
    last = np.asarray(weights[-1], dtype=np.float64)
    column_norm = np.sqrt(np.sum(last * last, axis=0, dtype=np.float64))
    envelope = mean_chi(d) * prefix * column_norm
    if envelope.shape != (out_width,):
        raise RuntimeError("range shape mismatch")
    return envelope


def _generic_cost_ledger(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
) -> dict:
    d, out_width = _validate_weights(weights)
    k = SOURCE_DIM
    j = CODEWORDS
    ntraj = frames * j

    simplex = 8 * k * (k + 1) + 256
    frame_setup = frames * (d * (2 * k * k + 17 * k) + 64 * k)
    source = frames * (2 * d * k * j)

    deep_layers: list[int] = []
    previous = d
    for raw in weights:
        out = int(np.asarray(raw).shape[1])
        deep_layers.append(ntraj * (2 * previous * out + 2 * out))
        previous = out

    final = ntraj * out_width + 2 * ntraj + 5 * out_width

    orth_diag_per_frame = 2 * d * k * k + 3 * k * k
    source_norm_per_frame = j * (2 * d + 5)
    diagnostics = frames * (orth_diag_per_frame + source_norm_per_frame)

    range_cost = 0
    for raw in weights[:-1]:
        w = np.asarray(raw)
        range_cost += 2 * int(w.shape[0]) * int(w.shape[1]) + 8
    last = np.asarray(weights[-1])
    range_cost += 2 * int(last.shape[0]) * int(last.shape[1]) + 8 * int(last.shape[1])

    cert_stats = frames * ((j + 8) * out_width) + 32 * out_width

    total = (
        simplex
        + frame_setup
        + source
        + sum(deep_layers)
        + final
        + diagnostics
        + range_cost
        + cert_stats
    )
    return {
        "simplex_setup_upper": int(simplex),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source),
        "deep_layer_flops": [int(x) for x in deep_layers],
        "deep_propagation_upper": int(sum(deep_layers)),
        "final_reduction_radial_upper": int(final),
        "orthogonality_source_norm_diagnostics_upper": int(diagnostics),
        "frobenius_range_envelope_upper": int(range_cost),
        "certificate_frame_stats_upper": int(cert_stats),
        "all_in_upper": int(total),
    }


def certified_simplex_frame_mean(
    weights: Sequence[np.ndarray],
    *,
    frames: int,
    seed: int,
    delta: float = DELTA,
) -> CertifiedFrameEstimate:
    d, out_width = _validate_weights(weights)
    if frames <= 1:
        raise ValueError("frames must be >1")
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must lie in (0,1)")

    code = regular_simplex_code(SOURCE_DIM)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    frame_values = np.empty((frames, out_width), dtype=np.float64)

    orth_max = 0.0
    norm_max = 0.0
    radial = mean_chi(d)

    for p in range(frames):
        u, orth = _haar_frame(rng, d, SOURCE_DIM)
        orth_max = max(orth_max, orth)
        q = code @ u.T
        qnorm = np.linalg.norm(q, axis=1)
        norm_max = max(norm_max, float(np.max(np.abs(qnorm - 1.0))))
        y = _forward_batch(q, weights)
        frame_values[p] = radial * np.mean(y, axis=0, dtype=np.float64)

    mean = np.mean(frame_values, axis=0, dtype=np.float64)
    sample_variance = np.var(frame_values, axis=0, ddof=1)
    envelope = frobenius_range_envelope(weights)

    logterm = math.log(4.0 * float(out_width) / float(delta))
    variance_term = np.sqrt(2.0 * sample_variance * logterm / float(frames))
    range_term = 7.0 * envelope * logterm / (3.0 * float(frames - 1))
    radii = variance_term + range_term

    rms_certificate = float(np.sqrt(np.mean(radii * radii)))
    variance_only_rms = float(
        np.sqrt(np.mean(variance_term * variance_term))
    )

    observed_max = np.max(frame_values, axis=0)
    observed_min = np.min(frame_values, axis=0)
    range_violation = max(
        float(np.max(observed_max - envelope)),
        float(np.max(-observed_min)),
        0.0,
    )

    ledger = _generic_cost_ledger(weights, frames=frames)
    finite = bool(
        np.isfinite(mean).all()
        and np.isfinite(frame_values).all()
        and np.isfinite(sample_variance).all()
        and np.isfinite(envelope).all()
        and np.isfinite(radii).all()
        and math.isfinite(rms_certificate)
        and math.isfinite(variance_only_rms)
    )
    return CertifiedFrameEstimate(
        mean=mean,
        frame_contributions=frame_values,
        sample_variance=sample_variance,
        frobenius_range=envelope,
        coordinate_radii=radii,
        rms_certificate=rms_certificate,
        variance_only_rms=variance_only_rms,
        frame_orthogonality_max_abs=orth_max,
        source_direction_norm_max_abs=norm_max,
        observed_range_violation_max_abs=range_violation,
        ledger=ledger,
        finite=finite,
    )


def production_cost_upper(frames: int) -> dict:
    d = n = out_width = 1024
    l = 16
    k = SOURCE_DIM
    j = CODEWORDS
    p = int(frames)
    ntraj = p * j

    simplex = 8 * k * (k + 1) + 256
    frame_setup = p * (d * (2 * k * k + 17 * k) + 64 * k)
    source = p * (2 * d * k * j)
    deep = ntraj * l * (2 * n * n + 2 * n)
    final = ntraj * out_width + 2 * ntraj + 5 * out_width

    orth_diag_per_frame = 2 * d * k * k + 3 * k * k
    source_norm_per_frame = j * (2 * d + 5)
    diagnostics = p * (orth_diag_per_frame + source_norm_per_frame)

    range_cost = l * (2 * n * n) + 8 * ((l - 1) + n)
    cert_stats = p * ((j + 8) * out_width) + 32 * out_width

    increment = (
        simplex
        + frame_setup
        + source
        + deep
        + final
        + diagnostics
        + range_cost
        + cert_stats
    )
    total = PRODUCTION_BASE_FLOPS + increment
    return {
        "frames": p,
        "directions": ntraj,
        "incremental_cap_flops": INCREMENTAL_CAP_FLOPS,
        "simplex_setup_upper": int(simplex),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source),
        "deep_propagation_upper": int(deep),
        "final_reduction_radial_upper": int(final),
        "orthogonality_source_norm_diagnostics_upper": int(diagnostics),
        "frobenius_range_envelope_upper": int(range_cost),
        "certificate_frame_stats_upper": int(cert_stats),
        "incremental_all_in_upper": int(increment),
        "incremental_slack": int(INCREMENTAL_CAP_FLOPS - increment),
        "total_with_e104_base": int(total),
        "utilization": float(total / TOTAL_BUDGET),
        "passes_cap": bool(increment <= INCREMENTAL_CAP_FLOPS),
    }
