"""Independent exact 2-D angular reference for E134 falsification only."""

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
class ExactReference:
    mean: np.ndarray
    layer_sector_counts: tuple[int, ...]
    final_sector_count: int
    finite: bool


def he_weights(seed: int, *, width: int, depth: int) -> list[np.ndarray]:
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
    out: list[float] = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + SECTOR_TOL < root < hi - SECTOR_TOL:
            out.append(float(root))
    return out


def _dedup(values: Iterable[float]) -> list[float]:
    out: list[float] = []
    for value in sorted(float(v) for v in values):
        if not out or abs(value - out[-1]) > ROOT_TOL:
            out.append(value)
    return out


def build_exact_reference(weights: Sequence[np.ndarray]) -> ExactReference:
    if not weights:
        raise ValueError("weights required")
    sectors: list[Sector] = [
        Sector(0.0, TWO_PI, np.eye(2, dtype=np.float64))
    ]
    previous = 2
    counts: list[int] = []

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError("incompatible weights")
        nxt: list[Sector] = []
        for sector in sectors:
            pre = w.T @ sector.coeff
            bounds = [sector.lo, sector.hi]
            for row in pre:
                bounds.extend(
                    _roots(
                        float(row[0]),
                        float(row[1]),
                        sector.lo,
                        sector.hi,
                    )
                )
            bounds = _dedup(bounds)
            for lo, hi in zip(bounds[:-1], bounds[1:]):
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
        counts.append(len(sectors))

    angular = np.zeros(previous, dtype=np.float64)
    for sector in sectors:
        b = np.array(
            [
                math.sin(sector.hi) - math.sin(sector.lo),
                -math.cos(sector.hi) + math.cos(sector.lo),
            ],
            dtype=np.float64,
        )
        angular += sector.coeff @ b

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
    return ExactReference(
        mean=mean,
        layer_sector_counts=tuple(counts),
        final_sector_count=len(sectors),
        finite=finite,
    )
