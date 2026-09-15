# RED contract: production module must not exist before this suite is observed failing.
import numpy as np

from methods.e046_harmonic_defect_control import (
    EPS,
    GH_ORDER,
    HARMONIC_DEGREE,
    HARMONIC_RANK,
    canonicalize_column_signs,
    gauss_hermite_standard_normal,
    hermite6,
    reconstruct_harmonic_correction,
    walsh_response_matrix,
)


def test_frozen_constants_are_exact():
    assert HARMONIC_DEGREE == 6
    assert HARMONIC_RANK == 64
    assert GH_ORDER == 12
    assert EPS == 1e-12


def test_walsh_response_matrix_has_64_orthonormal_columns():
    q = walsh_response_matrix(1024, HARMONIC_RANK)
    assert q.shape == (1024, 64)
    np.testing.assert_allclose(q.T @ q, np.eye(64), atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(
        np.abs(q), 1.0 / np.sqrt(1024.0), atol=0.0, rtol=0.0
    )


def test_sign_canonicalization_is_deterministic_and_positive_at_pivot():
    q = np.array(
        [
            [0.0, -0.8, 0.1],
            [-0.9, 0.1, 0.2],
            [0.3, 0.2, -0.95],
        ],
        dtype=float,
    )
    got1 = canonicalize_column_signs(q)
    got2 = canonicalize_column_signs(q.copy())
    np.testing.assert_array_equal(got1, got2)
    for j in range(got1.shape[1]):
        pivot = int(np.argmax(np.abs(got1[:, j])))
        assert got1[pivot, j] >= 0.0


def test_degree6_hermite_is_normalized_by_frozen_12_node_rule():
    nodes, weights = gauss_hermite_standard_normal(GH_ORDER)
    assert nodes.shape == (12,)
    assert weights.shape == (12,)
    np.testing.assert_allclose(weights.sum(), 1.0, atol=1e-15, rtol=0.0)
    h6 = hermite6(nodes)
    np.testing.assert_allclose(weights @ h6, 0.0, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(weights @ (h6 * h6), 720.0, atol=1e-9, rtol=0.0)


def test_zero_defect_identity_and_linear_reconstruction():
    directions = walsh_response_matrix(1024, HARMONIC_RANK)
    coeff = np.linspace(-0.02, 0.03, HARMONIC_RANK)
    zero = np.zeros(HARMONIC_RANK)
    got_zero = reconstruct_harmonic_correction(directions, zero, coeff)
    np.testing.assert_array_equal(got_zero, np.zeros(1024))

    defects = np.linspace(-0.1, 0.1, HARMONIC_RANK)
    got = reconstruct_harmonic_correction(directions, defects, coeff)
    doubled = reconstruct_harmonic_correction(directions, 2.0 * defects, coeff)
    np.testing.assert_allclose(doubled, 2.0 * got, atol=1e-15, rtol=0.0)
