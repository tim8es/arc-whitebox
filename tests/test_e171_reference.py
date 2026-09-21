from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np

from methods.e171_reference_streaming import (
    homogeneity_error,
    streaming_reference,
)


def _weights(n: int, seed: int, depth: int = 3) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return [
        rng.normal(
            0.0,
            math.sqrt(2.0 / n),
            size=(n, n),
        ).astype(np.float64)
        for _ in range(depth)
    ]


def test_streaming_reference_deterministic() -> None:
    weights = _weights(8, 171001)
    a = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=171512,
    )
    b = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=171512,
    )
    assert a.finite and b.finite
    assert a.sample_count == 512
    assert a.batch_count == 8
    assert a.batch_size == 64
    assert np.array_equal(a.angular_mean, b.angular_mean)
    assert np.array_equal(a.batch_angular_means, b.batch_angular_means)


def test_batch_average_reconciles() -> None:
    weights = _weights(8, 171002)
    ref = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=171513,
    )
    np.testing.assert_allclose(
        np.mean(ref.batch_angular_means, axis=0),
        ref.angular_mean,
        rtol=0.0,
        atol=2e-15,
    )


def test_homogeneity() -> None:
    weights = _weights(8, 171003)
    assert homogeneity_error(
        weights,
        n=8,
        seed=171700,
        rays=32,
    ) <= 2e-12


def test_npy_file_hash_is_stable(tmp_path: Path) -> None:
    arr = np.arange(24, dtype=np.float64).reshape(3, 8)
    p = tmp_path / "payload.npy"
    np.save(p, arr, allow_pickle=False)
    first = hashlib.sha256(p.read_bytes()).hexdigest()
    second = hashlib.sha256(p.read_bytes()).hexdigest()
    assert first == second
    loaded = np.load(p, allow_pickle=False)
    assert np.array_equal(arr, loaded)
