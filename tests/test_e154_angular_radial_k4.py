from __future__ import annotations

import math
import numpy as np

from methods.e154_angular_radial_k4 import (
    CAP_FLOPS,
    STRASSEN_LEVELS,
    angular_closure,
    gaussian_from_angular_k4,
    production_cost_receipt,
    radial_moment_factors,
    sphere_input_k4_diag,
    sphere_linear_k4_diag,
)
from methods.e154_reference import exact_circle_angular_mean, network_eval


def _weights(n: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return [
        rng.normal(0.0, math.sqrt(2.0 / n), size=(n, n)).astype(np.float64)
        for _ in range(8)
    ]


def test_radial_moments_and_input_k4() -> None:
    for n in (2, 16, 32):
        a1, a2, a3, a4 = radial_moment_factors(n)
        assert a2 == 1.0
        assert np.isclose(a3, ((n + 1.0) / n) * a1)
        assert np.isclose(a4, (n + 2.0) / n)
        # Uniform sphere coordinate raw moments.
        m1 = 0.0
        m2 = 1.0
        m3 = 0.0
        m4 = 3.0 * n / (n + 2.0)
        # Reconstruct Gaussian coordinate: fourth cumulant must be zero.
        assert abs(gaussian_from_angular_k4((m1, m2, m3, m4), n)) <= 1e-13
        assert np.isclose(sphere_input_k4_diag(n), -6.0 / (n + 2.0))


def test_linear_k4_identity_shape() -> None:
    v = np.array([0.5, 1.0, 2.0])
    got = sphere_linear_k4_diag(v, 16)
    np.testing.assert_allclose(got, -6.0 * v * v / 18.0)


def test_candidate_deterministic_and_cost() -> None:
    w = _weights(16, 154001)
    a = angular_closure(w, use_k4=True)
    b = angular_closure(w, use_k4=True)
    assert a.finite and b.finite
    assert np.array_equal(a.angular_mean, b.angular_mean)
    assert np.array_equal(a.gaussian_mean, b.gaussian_mean)
    for x, y in zip(a.layers, b.layers):
        assert np.array_equal(x.pre_k4_diag, y.pre_k4_diag)
        assert np.array_equal(x.mean, y.mean)
        assert np.array_equal(x.covariance, y.covariance)

    c = production_cost_receipt()
    assert STRASSEN_LEVELS == 0
    assert CAP_FLOPS == 296_868_139_499
    assert c["covariance_classical_two_gemm"] == 68_719_476_736
    assert c["mean_matvec"] == 33_554_432
    assert c["relu_covariance_update"] == 268_435_456
    assert c["k4_diagonal_and_wick"] == 8_388_608
    assert c["radial_scalar_helpers"] == 2_097_152
    assert c["helper_accounting_reserve"] == 42_949_672_960
    assert c["all_in_upper"] == 111_981_625_344
    assert c["slack_flops"] == 184_886_514_155
    assert c["passes_cap"]


def test_exact_circle_reference_linear_relu() -> None:
    # F(y)=ReLU(y) on the radius-sqrt(2) circle:
    # E[max(sqrt(2) cos(theta),0)] = sqrt(2)/pi.
    w = [np.eye(2, dtype=np.float64)]
    mean, sectors = exact_circle_angular_mean(w)
    np.testing.assert_allclose(
        mean,
        np.full(2, math.sqrt(2.0) / math.pi),
        rtol=0.0,
        atol=2e-14,
    )
    assert sectors >= 4

    # Reference evaluator agrees pointwise.
    y = np.array([[math.sqrt(2.0), 0.0]])
    np.testing.assert_allclose(network_eval(y, w), y)
