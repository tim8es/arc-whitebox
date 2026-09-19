"""Independent E123 adversarial multi-source verifier fixture.

This module intentionally does not depend on E114/E121 candidate/reference
modules. It provides a self-contained exact 2-D angular integrator and a 12-D
six-source fixture hidden behind a dense orthogonal input mixing.
"""

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
class MultiSourceFixture:
    dense_weights: tuple[np.ndarray, ...]
    latent_block_weights: tuple[np.ndarray, ...]
    mixing_q: np.ndarray
    exact_mean: np.ndarray
    block_exact_means: tuple[np.ndarray, ...]
    fixture_sha256: str


def _he_2d_subnetwork(seed: int, depth: int = 4) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    for layer in range(depth):
        fan_in = 2
        w = rng.standard_normal((2, 2)).astype(np.float64)
        w *= math.sqrt(2.0 / fan_in)
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
        if lo + _SECTOR_TOL < x < hi - _SECTOR_TOL:
            roots.append(float(x))
    return roots


def _dedup(values: Iterable[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(float(v) for v in values):
        if not out or abs(x - out[-1]) > _ROOT_TOL:
            out.append(x)
    return out


def exact_2d_gaussian_mean(weights: Sequence[np.ndarray]) -> np.ndarray:
    """Independent exact mean for a zero-bias 2-D positively homogeneous ReLU net."""
    sectors: list[Sector] = [Sector(0.0, _TWO_PI, np.eye(2, dtype=np.float64))]

    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
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
                if hi - lo <= _SECTOR_TOL:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                coeff = pre.copy()
                coeff[(pre @ q) <= 0.0, :] = 0.0
                nxt.append(Sector(lo, hi, coeff))
        sectors = nxt

    width = sectors[0].coeff.shape[0]
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

    mean_radius = math.sqrt(math.pi / 2.0)
    return mean_radius * angular / _TWO_PI


def _block_diag(blocks: Sequence[np.ndarray]) -> np.ndarray:
    n = 2 * len(blocks)
    out = np.zeros((n, n), dtype=np.float64)
    for i, block in enumerate(blocks):
        lo = 2 * i
        out[lo : lo + 2, lo : lo + 2] = np.asarray(block, dtype=np.float64)
    return out


def _orthogonal_mixing(seed: int, d: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    a = rng.standard_normal((d, d)).astype(np.float64)
    q, r = np.linalg.qr(a)
    diag = np.diag(r)
    signs = np.where(diag < 0.0, -1.0, 1.0)
    q = q * signs[None, :]
    # Deterministic column sign canonicalization.
    for j in range(d):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _hash_fixture(
    dense_weights: Sequence[np.ndarray],
    exact_mean: np.ndarray,
) -> str:
    h = hashlib.sha256()
    for w in dense_weights:
        arr = np.ascontiguousarray(w, dtype=np.float64)
        h.update(arr.shape[0].to_bytes(4, "little"))
        h.update(arr.shape[1].to_bytes(4, "little"))
        h.update(arr.tobytes())
    h.update(np.ascontiguousarray(exact_mean, dtype=np.float64).tobytes())
    return h.hexdigest()


def build_adversarial_12d_fixture() -> MultiSourceFixture:
    block_seeds = (123300, 123301, 123302, 123303, 123304, 123305)
    subnetworks = [_he_2d_subnetwork(seed, depth=4) for seed in block_seeds]

    latent_layers = []
    for layer in range(4):
        latent_layers.append(_block_diag([sub[layer] for sub in subnetworks]))

    q = _orthogonal_mixing(123390, 12)
    dense_layers = [q @ latent_layers[0], *latent_layers[1:]]

    block_means = tuple(
        exact_2d_gaussian_mean(sub) for sub in subnetworks
    )
    exact_mean = np.concatenate(block_means).astype(np.float64, copy=False)

    return MultiSourceFixture(
        dense_weights=tuple(np.asarray(w, dtype=np.float64) for w in dense_layers),
        latent_block_weights=tuple(
            np.asarray(w, dtype=np.float64) for w in latent_layers
        ),
        mixing_q=np.asarray(q, dtype=np.float64),
        exact_mean=exact_mean,
        block_exact_means=block_means,
        fixture_sha256=_hash_fixture(dense_layers, exact_mean),
    )


def forward_batch(x: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for raw_w in weights:
        h = h @ np.asarray(raw_w, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def dense_vs_latent_probe_error(
    fixture: MultiSourceFixture,
    *,
    seed: int = 123399,
    samples: int = 64,
) -> float:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    x = rng.standard_normal((samples, 12)).astype(np.float64)
    dense = forward_batch(x, fixture.dense_weights)
    latent_x = x @ fixture.mixing_q
    latent = forward_batch(latent_x, fixture.latent_block_weights)
    return float(np.max(np.abs(dense - latent)))


def fixture_replay_equal(a: MultiSourceFixture, b: MultiSourceFixture) -> bool:
    if a.fixture_sha256 != b.fixture_sha256:
        return False
    if not np.array_equal(a.exact_mean, b.exact_mean):
        return False
    if not np.array_equal(a.mixing_q, b.mixing_q):
        return False
    if len(a.dense_weights) != len(b.dense_weights):
        return False
    return all(
        np.array_equal(x, y)
        for x, y in zip(a.dense_weights, b.dense_weights)
    )


@dataclass(frozen=True)
class CandidateVisibleFixture:
    dense_weights: tuple[np.ndarray, ...]
    _latent_block_weights: tuple[np.ndarray, ...]
    _subnetworks: tuple[tuple[np.ndarray, ...], ...]
    _mixing_q: np.ndarray
    fixture_weights_sha256: str


def build_candidate_visible_12d_fixture() -> CandidateVisibleFixture:
    """Build candidate-visible dense weights without materializing exact means."""
    block_seeds = (123300, 123301, 123302, 123303, 123304, 123305)
    subnetworks_list = [
        _he_2d_subnetwork(seed, depth=4) for seed in block_seeds
    ]
    latent_layers = [
        _block_diag([sub[layer] for sub in subnetworks_list])
        for layer in range(4)
    ]
    q = _orthogonal_mixing(123390, 12)
    dense_layers = [q @ latent_layers[0], *latent_layers[1:]]

    h = hashlib.sha256()
    for w in dense_layers:
        h.update(np.ascontiguousarray(w, dtype=np.float64).tobytes())

    return CandidateVisibleFixture(
        dense_weights=tuple(
            np.asarray(w, dtype=np.float64) for w in dense_layers
        ),
        _latent_block_weights=tuple(
            np.asarray(w, dtype=np.float64) for w in latent_layers
        ),
        _subnetworks=tuple(
            tuple(np.asarray(w, dtype=np.float64) for w in sub)
            for sub in subnetworks_list
        ),
        _mixing_q=np.asarray(q, dtype=np.float64),
        fixture_weights_sha256=h.hexdigest(),
    )


def materialize_exact_reference_after_candidate(
    state: CandidateVisibleFixture,
) -> np.ndarray:
    """Verifier-only exact reference; call only after candidate execution."""
    block_means = [
        exact_2d_gaussian_mean(sub) for sub in state._subnetworks
    ]
    return np.concatenate(block_means).astype(np.float64, copy=False)


def candidate_visible_dense_latent_probe_error(
    state: CandidateVisibleFixture,
    *,
    seed: int = 123399,
    samples: int = 64,
) -> float:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    x = rng.standard_normal((samples, 12)).astype(np.float64)
    dense = forward_batch(x, state.dense_weights)
    latent_x = x @ state._mixing_q
    latent = forward_batch(latent_x, state._latent_block_weights)
    return float(np.max(np.abs(dense - latent)))
