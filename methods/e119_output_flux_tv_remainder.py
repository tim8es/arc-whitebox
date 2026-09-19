"""E119 weight-only total-variation remainder certificate for E118 flux sketch."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class TVRemainderCertificate:
    area_bounds: tuple[np.ndarray, ...]
    variation_bounds: tuple[np.ndarray, ...]
    scalar_tv_bound: float
    angular_factor: float
    gaussian_factor: float
    absolute_mean_bound: float
    finite: bool


def output_observable(width: int) -> np.ndarray:
    if width <= 0:
        raise ValueError("width must be positive")
    c = np.arange(1, width + 1, dtype=np.float64)
    c /= np.linalg.norm(c)
    return c


def _validate_weights(weights: Sequence[np.ndarray]) -> tuple[int, int]:
    if not weights:
        raise ValueError("weights must be non-empty")
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2 or first.shape[0] != 2:
        raise ValueError("E119 TV certificate requires 2-D input")
    width = int(first.shape[1])
    if width <= 0:
        raise ValueError("width must be positive")
    previous = 2
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous or w.shape[1] != width:
            raise ValueError(
                f"weight {idx} has shape {w.shape}; expected ({previous},{width})"
            )
        if not np.isfinite(w).all():
            raise ValueError(f"weight {idx} is non-finite")
        previous = width
    return width, len(weights)


def weight_only_tv_bound(
    weights: Sequence[np.ndarray],
    observable: np.ndarray | None = None,
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...], float]:
    """Bound sum of absolute scalar derivative jumps using weights only.

    For nonnegative hidden activations h, track:
      A_j >= integral h_j(theta) dtheta
      V_j >= ||(h_j'' + h_j)||_TV.

    First layer is exact: A=V=2*||w_j||.
    Later:
      A_next <= W_+^T A
      V_next <= A_next + 2*|W|^T V.
    """
    width, _ = _validate_weights(weights)
    c = (
        output_observable(width)
        if observable is None
        else np.asarray(observable, dtype=np.float64).reshape(-1)
    )
    if c.shape != (width,):
        raise ValueError(f"observable must have shape ({width},)")
    if not np.isfinite(c).all():
        raise ValueError("observable is non-finite")

    w0 = np.asarray(weights[0], dtype=np.float64)
    area = 2.0 * np.linalg.norm(w0, axis=0)
    variation = area.copy()

    areas = [area.copy()]
    variations = [variation.copy()]

    for raw_w in weights[1:]:
        w = np.asarray(raw_w, dtype=np.float64)
        area_next = np.maximum(w, 0.0).T @ area
        inherited_variation = np.abs(w).T @ variation
        variation_next = area_next + 2.0 * inherited_variation

        area = np.asarray(area_next, dtype=np.float64)
        variation = np.asarray(variation_next, dtype=np.float64)
        areas.append(area.copy())
        variations.append(variation.copy())

    scalar_tv = float(np.abs(c) @ variation)
    return tuple(areas), tuple(variations), scalar_tv


def sketch_remainder_certificate(
    weights: Sequence[np.ndarray],
    *,
    cells: int = 1024,
    observable: np.ndarray | None = None,
) -> TVRemainderCertificate:
    if cells <= 0:
        raise ValueError("cells must be positive")
    areas, variations, scalar_tv = weight_only_tv_bound(weights, observable)
    angular_factor = float(1.0 - math.cos(math.pi / cells))
    gaussian_factor = float(math.sqrt(math.pi / 2.0) / (2.0 * math.pi))
    absolute_mean_bound = gaussian_factor * angular_factor * scalar_tv
    finite = bool(
        math.isfinite(scalar_tv)
        and math.isfinite(absolute_mean_bound)
        and all(np.isfinite(x).all() for x in areas)
        and all(np.isfinite(x).all() for x in variations)
    )
    return TVRemainderCertificate(
        area_bounds=areas,
        variation_bounds=variations,
        scalar_tv_bound=scalar_tv,
        angular_factor=angular_factor,
        gaussian_factor=gaussian_factor,
        absolute_mean_bound=absolute_mean_bound,
        finite=finite,
    )


def production_overhead_upper_flops(
    *, width: int = 1024, depth: int = 16
) -> int:
    """Conservative scalar-op envelope for the weight-only recursion.

    Later layers charge 6*n^2 + 4*n operations:
    positive/abs transforms plus two matrix-vector reductions and vector combine.
    First-layer column norms/final observable reduction get a generous 1e6 reserve.
    """
    if width <= 0 or depth <= 0:
        raise ValueError("width/depth must be positive")
    later = max(depth - 1, 0) * (6 * width * width + 4 * width)
    return int(later + 1_000_000)
