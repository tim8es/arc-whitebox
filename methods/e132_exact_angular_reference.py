"""Independent exact 2-D angular reference for E132 falsification only."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np


TWO_PI = 2.0 * math.pi
ROOT_TOL = 2.0 ** -40
SECTOR_TOL = 1e-13


@dataclass(frozen=True)
class Sector:
    lo: float
    hi: float
    coeff: np.ndarray


@dataclass(frozen=True)
class ExactAngularReference:
    mean: np.ndarray
    sectors: tuple[Sector, ...]
    layer_sector_counts: tuple[int, ...]
    finite: bool


def he_weights(seed: int, *, width: int, depth: int) -> list[np.ndarray]:
    if width <= 0 or depth <= 0:
        raise ValueError("positive width/depth required")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    first = rng.standard_normal((2, width)).astype(np.float64)
    first *= math.sqrt(2.0 / 2.0)
    out.append(first)
    for _ in range(depth - 1):
        w = rng.standard_normal((width, width)).astype(np.float64)
        w *= math.sqrt(2.0 / float(width))
        out.append(w)
    return out


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + SECTOR_TOL < x < hi - SECTOR_TOL:
            roots.append(float(x))
    return roots


def _dedup(values: Iterable[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(float(v) for v in values):
        if not out or abs(x - out[-1]) > ROOT_TOL:
            out.append(x)
    return out


def build_exact_reference(weights: Sequence[np.ndarray]) -> ExactAngularReference:
    if not weights:
        raise ValueError("weights required")
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2 or first.shape[0] != 2:
        raise ValueError("E132 exact reference requires input dimension 2")

    sectors: list[Sector] = [
        Sector(0.0, TWO_PI, np.eye(2, dtype=np.float64))
    ]
    layer_counts: list[int] = []
    previous = 2

    for layer, raw_w in enumerate(weights, start=1):
        w = np.asarray(raw_w, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError(f"incompatible weight at layer {layer}")
        nxt: list[Sector] = []
        for sector in sectors:
            pre = w.T @ sector.coeff
            boundaries = [sector.lo, sector.hi]
            for row in pre:
                boundaries.extend(
                    _roots(
                        float(row[0]),
                        float(row[1]),
                        sector.lo,
                        sector.hi,
                    )
                )
            boundaries = _dedup(boundaries)

            for lo, hi in zip(boundaries[:-1], boundaries[1:]):
                if hi - lo <= SECTOR_TOL:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.array(
                    [math.cos(mid), math.sin(mid)],
                    dtype=np.float64,
                )
                coeff = pre.copy()
                coeff[(pre @ q) <= 0.0, :] = 0.0
                nxt.append(Sector(lo, hi, coeff))
        sectors = nxt
        previous = int(w.shape[1])
        layer_counts.append(len(sectors))

    angular = np.zeros(previous, dtype=np.float64)
    for sector in sectors:
        basis = np.array(
            [
                math.sin(sector.hi) - math.sin(sector.lo),
                -math.cos(sector.hi) + math.cos(sector.lo),
            ],
            dtype=np.float64,
        )
        angular += sector.coeff @ basis

    mean = math.sqrt(math.pi / 2.0) * angular / TWO_PI
    finite = bool(
        np.isfinite(mean).all()
        and all(
            np.isfinite(s.coeff).all()
            and math.isfinite(s.lo)
            and math.isfinite(s.hi)
            for s in sectors
        )
    )
    return ExactAngularReference(
        mean=mean,
        sectors=tuple(sectors),
        layer_sector_counts=tuple(layer_counts),
        finite=finite,
    )
