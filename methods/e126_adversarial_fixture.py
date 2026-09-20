"""Verifier-only adversarial dense fixtures for E126."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Iterable, Sequence

import numpy as np

_TWO_PI = 2.0 * math.pi
_ROOT_TOL = 2.0 ** -40
_SECTOR_TOL = 1e-13


@dataclass(frozen=True)
class Sector:
    lo: float
    hi: float
    coeff: np.ndarray


@dataclass(frozen=True)
class CandidateVisibleFixture:
    dimension: int
    dense_weights: tuple[np.ndarray, ...]
    _latent_weights: tuple[np.ndarray, ...]
    _subnetworks: tuple[tuple[np.ndarray, ...], ...]
    _mixing_q: np.ndarray
    _positive_mix: np.ndarray
    fixture_weights_sha256: str


def _he_2d_subnetwork(seed: int, depth: int = 4) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out = []
    for _ in range(depth):
        w = rng.standard_normal((2, 2)).astype(np.float64)
        w *= math.sqrt(2.0 / 2.0)
        out.append(w)
    return out


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + _SECTOR_TOL < x < hi - _SECTOR_TOL:
            out.append(float(x))
    return out


def _dedup(values: Iterable[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(float(v) for v in values):
        if not out or abs(x - out[-1]) > _ROOT_TOL:
            out.append(x)
    return out


def exact_2d_gaussian_mean(weights: Sequence[np.ndarray]) -> np.ndarray:
    sectors = [Sector(0.0, _TWO_PI, np.eye(2, dtype=np.float64))]
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        nxt = []
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
                if hi - lo <= _SECTOR_TOL:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                coeff = pre.copy()
                coeff[(pre @ q) <= 0.0, :] = 0.0
                nxt.append(Sector(lo, hi, coeff))
        sectors = nxt

    width = int(sectors[0].coeff.shape[0])
    angular = np.zeros(width, dtype=np.float64)
    for sector in sectors:
        basis = np.array(
            [
                math.sin(sector.hi) - math.sin(sector.lo),
                -math.cos(sector.hi) + math.cos(sector.lo),
            ],
            dtype=np.float64,
        )
        angular += sector.coeff @ basis
    return math.sqrt(math.pi / 2.0) * angular / _TWO_PI


def _block_diag(blocks: Sequence[np.ndarray]) -> np.ndarray:
    d = 2 * len(blocks)
    out = np.zeros((d, d), dtype=np.float64)
    for i, block in enumerate(blocks):
        lo = 2 * i
        out[lo : lo + 2, lo : lo + 2] = np.asarray(block, dtype=np.float64)
    return out


def _orthogonal(seed: int, d: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    a = rng.standard_normal((d, d)).astype(np.float64)
    q, r = np.linalg.qr(a)
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    q = q * signs[None, :]
    for j in range(d):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _positive_dense_mix(d: int, rho: float = 0.99) -> np.ndarray:
    if not (0.0 < rho < 1.0):
        raise ValueError("rho must lie in (0,1)")
    return (1.0 - rho) * np.eye(d, dtype=np.float64) + (
        rho / float(d)
    ) * np.ones((d, d), dtype=np.float64)


def _forward(x: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for raw in weights:
        h = h @ np.asarray(raw, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def build_candidate_visible_fixture(
    *,
    dimension: int,
    block_seed_start: int,
    mixing_seed: int,
    rho: float = 0.99,
) -> CandidateVisibleFixture:
    d = int(dimension)
    if d not in (8, 16) or d % 2:
        raise ValueError("frozen E126 dimensions are 8 and 16")

    blocks = d // 2
    subnetworks = [
        _he_2d_subnetwork(block_seed_start + i, depth=4)
        for i in range(blocks)
    ]
    latent = [
        _block_diag([sub[layer] for sub in subnetworks])
        for layer in range(4)
    ]

    q = _orthogonal(mixing_seed, d)
    a = _positive_dense_mix(d, rho=rho)
    a_inv = np.linalg.inv(a)

    dense = [
        q @ latent[0],
        a,
        a_inv @ latent[1],
        a,
        a_inv @ latent[2],
        a,
        a_inv @ latent[3],
    ]

    h = hashlib.sha256()
    for w in dense:
        h.update(np.ascontiguousarray(w, dtype=np.float64).tobytes())

    return CandidateVisibleFixture(
        dimension=d,
        dense_weights=tuple(np.asarray(w, dtype=np.float64) for w in dense),
        _latent_weights=tuple(np.asarray(w, dtype=np.float64) for w in latent),
        _subnetworks=tuple(
            tuple(np.asarray(w, dtype=np.float64) for w in sub)
            for sub in subnetworks
        ),
        _mixing_q=np.asarray(q, dtype=np.float64),
        _positive_mix=np.asarray(a, dtype=np.float64),
        fixture_weights_sha256=h.hexdigest(),
    )


def dense_vs_latent_probe(
    state: CandidateVisibleFixture,
    *,
    seed: int,
    samples: int = 128,
) -> float:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    x = rng.standard_normal((samples, state.dimension)).astype(np.float64)
    dense = _forward(x, state.dense_weights)
    latent_x = x @ state._mixing_q
    latent = _forward(latent_x, state._latent_weights)
    return float(np.max(np.abs(dense - latent)))


def materialize_exact_reference_after_candidate(
    state: CandidateVisibleFixture,
) -> np.ndarray:
    means = [exact_2d_gaussian_mean(sub) for sub in state._subnetworks]
    return np.concatenate(means).astype(np.float64, copy=False)


def positive_mix_condition_number(state: CandidateVisibleFixture) -> float:
    return float(np.linalg.cond(state._positive_mix))


def all_weights_dense_fraction(state: CandidateVisibleFixture) -> list[float]:
    out = []
    for w in state.dense_weights:
        arr = np.asarray(w, dtype=np.float64)
        out.append(float(np.count_nonzero(np.abs(arr) > 1e-14) / arr.size))
    return out
