# RED contract: production module must not exist before this suite is observed failing.
import numpy as np

from methods.e045_layerwise_signed_k3_sigma import (
    PAIR_COUNT,
    POINT_COUNT,
    RESPONSE_COUNT,
    canonicalize_eigenvector_signs,
    make_sigma_geometry_from_eigendecomposition,
    solve_response_antisymmetry,
    walsh_response_matrix,
)


def test_frozen_constants_are_exact():
    assert PAIR_COUNT == 1024
    assert POINT_COUNT == 2049
    assert RESPONSE_COUNT == 32
    assert POINT_COUNT == 2 * PAIR_COUNT + 1


def test_sign_canonicalization_is_deterministic_and_positive_at_pivot():
    q = np.array(
        [
            [0.0, -0.8, 0.1],
            [-0.9, 0.1, 0.2],
            [0.3, 0.2, -0.95],
        ],
        dtype=float,
    )
    got1 = canonicalize_eigenvector_signs(q)
    got2 = canonicalize_eigenvector_signs(q.copy())
    np.testing.assert_array_equal(got1, got2)
    for j in range(got1.shape[1]):
        pivot = int(np.argmax(np.abs(got1[:, j])))
        assert got1[pivot, j] >= 0.0


def test_walsh_response_matrix_has_32_orthonormal_columns():
    h = walsh_response_matrix(1024, RESPONSE_COUNT)
    assert h.shape == (1024, 32)
    gram = h.T @ h
    np.testing.assert_allclose(gram, np.eye(32), atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(np.abs(h), 1.0 / np.sqrt(1024.0), atol=0.0, rtol=0.0)


def test_2049_point_antithetic_geometry_normalizes_and_has_zero_centered_mean():
    n = 1024
    mean = np.linspace(-0.2, 0.2, n)
    evals = np.linspace(0.5, 1.5, n)
    evecs = np.eye(n)
    points, weights = make_sigma_geometry_from_eigendecomposition(mean, evals, evecs)
    assert points.shape == (POINT_COUNT, n)
    assert weights.shape == (POINT_COUNT,)
    assert np.count_nonzero(weights) == 2 * PAIR_COUNT
    np.testing.assert_allclose(weights.sum(), 1.0, atol=1e-15, rtol=0.0)
    centered_mean = weights @ (points - mean[None, :])
    np.testing.assert_allclose(centered_mean, np.zeros(n), atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(points[0], mean, atol=0.0, rtol=0.0)
    np.testing.assert_allclose(points[1 : 1 + n] + points[1 + n :], 2.0 * mean[None, :], atol=1e-12, rtol=0.0)


def test_response_antisymmetry_matches_32_third_moments_without_norm_or_mean_drift():
    # Synthetic full-rank response problem with 1024 pair directions.  The
    # frozen Walsh basis selects the 32 response coordinates in production;
    # here the resulting pair responses are represented directly.  Varying
    # magnitudes ensure first- and third-moment constraint spaces are distinct.
    rng = np.random.default_rng(4516)
    pair_response = rng.normal(size=(PAIR_COUNT, RESPONSE_COUNT))
    target = np.linspace(-0.04, 0.04, RESPONSE_COUNT)
    delta = solve_response_antisymmetry(pair_response, target)
    assert delta.shape == (PAIR_COUNT,)

    # Pair perturbations (+delta_i, -delta_i) preserve total normalization.
    # The constrained minimum-norm solve must also enforce zero first-moment
    # drift in all 32 response coordinates and match all 32 cubic responses.
    first = pair_response.T @ delta
    cubic_design = (pair_response ** 3).T
    third = cubic_design @ delta
    np.testing.assert_allclose(first, np.zeros(RESPONSE_COUNT), atol=1e-10, rtol=0.0)
    np.testing.assert_allclose(third, target, atol=1e-10, rtol=0.0)
