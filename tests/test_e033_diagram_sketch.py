import itertools

import numpy as np

from methods.e033_diagram_sketch import (
    best_symmetric_rank_capture,
    hutchinson_bilinear,
    offdiag,
)


def test_offdiag_zeroes_only_diagonal():
    x = np.arange(25, dtype=np.float64).reshape(5, 5)
    y = offdiag(x)
    assert np.array_equal(np.diag(y), np.zeros(5))
    mask = ~np.eye(5, dtype=bool)
    assert np.array_equal(y[mask], x[mask])


def test_best_symmetric_rank_capture_is_exact_on_rank_two():
    u = np.array([1.0, -2.0, 0.5, 1.5])
    v = np.array([0.25, 1.0, -1.0, 2.0])
    q, _ = np.linalg.qr(np.stack([u, v], axis=1))
    a = 5.0 * np.outer(q[:, 0], q[:, 0]) - 2.0 * np.outer(q[:, 1], q[:, 1])
    assert abs(best_symmetric_rank_capture(a, 1) - 25.0 / 29.0) < 1e-12
    assert abs(best_symmetric_rank_capture(a, 2) - 1.0) < 1e-12


def test_hutchinson_source_identity_is_unbiased_over_all_signs():
    rng = np.random.default_rng(3301)
    k, n = 3, 5
    a = rng.standard_normal((k, n))
    p = rng.standard_normal((k, n))
    exact = sum(np.outer(a[s], p[s]) for s in range(k))
    estimates = []
    for bits in itertools.product((-1.0, 1.0), repeat=k):
        signs = np.asarray(bits, dtype=np.float64)[None, :]
        estimates.append(hutchinson_bilinear(a, p, signs))
    mean = np.mean(estimates, axis=0)
    assert np.max(np.abs(mean - exact)) < 1e-12


def test_four_probe_shape_and_determinism():
    rng = np.random.default_rng(3302)
    a = rng.standard_normal((7, 8))
    p = rng.standard_normal((7, 8))
    signs = np.asarray(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, -1, 1, -1, 1, -1, 1],
            [1, 1, -1, -1, 1, 1, -1],
            [1, -1, -1, 1, 1, -1, -1],
        ],
        dtype=np.float64,
    )
    x = hutchinson_bilinear(a, p, signs)
    y = hutchinson_bilinear(a, p, signs)
    assert x.shape == (8, 8)
    assert np.array_equal(x, y)
