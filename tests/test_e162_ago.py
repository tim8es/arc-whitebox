from __future__ import annotations

import math
import numpy as np

from methods.e162_ago import (
    CAP_FLOPS,
    ago_candidate,
    angular_to_gaussian_state,
    gaussian_parent,
    gaussian_to_angular_state,
    production_cost_receipt,
    radial_a1,
)
from methods.e162_reference import exact_circle_reference


def _weights(n: int, seed: int, depth: int = 8) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return [
        rng.normal(
            0.0,
            math.sqrt(2.0 / n),
            size=(n, n),
        ).astype(np.float64)
        for _ in range(depth)
    ]


def test_radial_a1_n2() -> None:
    assert abs(radial_a1(2) - math.sqrt(math.pi) / 2.0) <= 1e-14


def test_gauge_roundtrip() -> None:
    rng = np.random.Generator(np.random.PCG64(162001))
    n = 8
    mean = rng.normal(size=n)
    a = rng.normal(size=(n, n))
    cov = a @ a.T + np.eye(n)
    ma, ca = gaussian_to_angular_state(mean, cov, n)
    mg, cg = angular_to_gaussian_state(ma, ca, n)
    np.testing.assert_allclose(mg, mean, rtol=0.0, atol=2e-14)
    np.testing.assert_allclose(cg, cov, rtol=0.0, atol=5e-13)


def test_parent_candidate_deterministic_and_cost() -> None:
    weights = _weights(16, 162011)
    p1 = gaussian_parent(weights)
    p2 = gaussian_parent(weights)
    a1 = ago_candidate(weights)
    a2 = ago_candidate(weights)

    assert p1.finite and p2.finite and a1.finite and a2.finite
    assert np.array_equal(p1.final_mean, p2.final_mean)
    assert np.array_equal(a1.final_mean, a2.final_mean)

    for x, y in zip(a1.layers, a2.layers):
        assert np.array_equal(x.mean, y.mean)
        assert np.array_equal(x.covariance, y.covariance)

    c = production_cost_receipt()
    assert CAP_FLOPS == 296_868_139_499
    assert c["covariance_linear_transport"] == 68_719_476_736
    assert c["mean_dense_matvec"] == 33_554_432
    assert c["k2_relu_arithmetic"] == 402_653_184
    assert c["wick_scalar_work"] == 16_777_216
    assert c["parent_helper_reserve"] == 42_949_672_960
    assert c["ago_gauge_overlay"] == 9_437_184
    assert c["all_in_upper"] == 112_131_571_712
    assert c["slack_flops"] == 184_736_567_787
    assert c["passes_cap"]


def test_exact_circle_identity_network() -> None:
    weights = [np.eye(2, dtype=np.float64)]
    ref = exact_circle_reference(weights)
    expected = np.full(2, math.sqrt(2.0) / math.pi)
    np.testing.assert_allclose(
        ref.final_angular_mean,
        expected,
        rtol=0.0,
        atol=2e-14,
    )
    np.testing.assert_allclose(
        ref.first_angular_mean,
        expected,
        rtol=0.0,
        atol=2e-14,
    )
    assert ref.finite
