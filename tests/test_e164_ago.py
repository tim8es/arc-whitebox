from __future__ import annotations

import math
import numpy as np

from methods.e164_ago import (
    CAP_FLOPS,
    ago_estimate,
    parent_estimate,
    production_cost,
    radial_a1,
    to_angular,
    to_gaussian,
)
from methods.e164_reference import exact_circle


def _weights(n: int, seed: int, depth: int = 8) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return [
        rng.normal(
            0.0,
            math.sqrt(2.0 / n),
            size=(n, n),
        ).astype(np.float64)
        for _ in range(depth)
    ]


def test_radial_constant_n2() -> None:
    np.testing.assert_allclose(
        radial_a1(2),
        math.sqrt(math.pi) / 2.0,
        rtol=0.0,
        atol=2e-15,
    )


def test_gauge_round_trip() -> None:
    rng = np.random.Generator(np.random.PCG64(164001))
    n = 7
    mean = rng.normal(size=n)
    a = rng.normal(size=(n, n))
    covariance = a @ a.T + np.eye(n)
    am, ac = to_angular(mean, covariance, n)
    gm, gc = to_gaussian(am, ac, n)
    np.testing.assert_allclose(gm, mean, rtol=0.0, atol=3e-14)
    np.testing.assert_allclose(gc, covariance, rtol=0.0, atol=5e-13)


def test_parent_ago_deterministic_and_cost() -> None:
    weights = _weights(16, 164011)
    p1 = parent_estimate(weights)
    p2 = parent_estimate(weights)
    a1 = ago_estimate(weights)
    a2 = ago_estimate(weights)

    assert p1.finite and p2.finite and a1.finite and a2.finite
    assert np.array_equal(p1.final_mean, p2.final_mean)
    assert np.array_equal(a1.final_mean, a2.final_mean)

    for x, y in zip(a1.layers, a2.layers):
        assert np.array_equal(x.mean, y.mean)
        assert np.array_equal(x.covariance, y.covariance)

    c = production_cost()
    assert CAP_FLOPS == 296_868_139_499
    assert c["covariance_linear_transport"] == 68_719_476_736
    assert c["mean_matvec"] == 33_554_432
    assert c["nonlinear_second_order_arithmetic"] == 402_653_184
    assert c["normal_scalar_work"] == 16_777_216
    assert c["helper_reserve"] == 42_949_672_960
    assert c["angular_gauge_overlay"] == 9_437_184
    assert c["all_in_upper"] == 112_131_571_712
    assert c["slack_flops"] == 184_736_567_787
    assert c["passes_cap"]


def test_exact_circle_identity_layer() -> None:
    ref = exact_circle([np.eye(2, dtype=np.float64)])
    expected = np.full(2, math.sqrt(2.0) / math.pi)
    np.testing.assert_allclose(
        ref.final_angular_mean,
        expected,
        rtol=0.0,
        atol=3e-14,
    )
    np.testing.assert_allclose(
        ref.first_angular_mean,
        expected,
        rtol=0.0,
        atol=3e-14,
    )
    assert ref.finite
