from __future__ import annotations

import math
import numpy as np

from methods.e169_reference_streaming import (
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


def test_streaming_reference_is_deterministic() -> None:
    weights = _weights(8, 169001)
    a = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=169512,
    )
    b = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=169512,
    )
    assert a.finite and b.finite
    assert a.batch_size == 64
    assert np.array_equal(a.angular_mean, b.angular_mean)
    assert np.array_equal(a.batch_angular_means, b.batch_angular_means)


def test_batch_average_reconciles_to_global_mean() -> None:
    weights = _weights(8, 169002)
    ref = streaming_reference(
        weights,
        n=8,
        total_samples=512,
        batch_count=8,
        seed=169513,
    )
    np.testing.assert_allclose(
        np.mean(ref.batch_angular_means, axis=0),
        ref.angular_mean,
        rtol=0.0,
        atol=2e-15,
    )


def test_homogeneity_is_exact_to_roundoff() -> None:
    weights = _weights(8, 169003)
    assert homogeneity_error(
        weights,
        n=8,
        seed=169700,
        rays=32,
    ) <= 2e-12
