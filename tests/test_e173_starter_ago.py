from __future__ import annotations

import math

import flopscope.numpy as fnp
import numpy as np

from methods.e164_ago import ago_estimate, parent_estimate
from methods.e173_starter_ago import (
    AGOEstimator,
    ParentEstimator,
    _run_ago,
    _run_parent,
    _to_angular,
    _to_gaussian,
    analytic_cost_receipt,
    radial_a1,
    suite_shape,
)
from whestbench.domain import MLP


def _mlp(width: int, depth: int, seed: int) -> MLP:
    rng = np.random.Generator(np.random.PCG64(seed))
    weights = [
        fnp.asarray(
            rng.normal(
                0.0,
                math.sqrt(2.0 / width),
                size=(width, width),
            ).astype(np.float32),
            dtype=fnp.float32,
        )
        for _ in range(depth)
    ]
    return MLP(
        width=width,
        depth=depth,
        weights=weights,
        seed=seed,
        name=f"synthetic-{seed}",
    )


def _row_weights_for_e164(mlp: MLP) -> list[np.ndarray]:
    return [
        np.asarray(w, dtype=np.float64).T.copy()
        for w in mlp.weights
    ]


def test_non_suite_ago_is_bitwise_parent_fallback() -> None:
    mlp = _mlp(4, 2, 173001)
    parent = ParentEstimator().predict(mlp, 2**41)
    ago = AGOEstimator().predict(mlp, 2**41)
    assert not suite_shape(mlp)
    assert np.array_equal(np.asarray(parent), np.asarray(ago))


def test_starter_orientation_matches_e164_parent() -> None:
    mlp = _mlp(7, 3, 173002)
    integrated = np.asarray(_run_parent(mlp), dtype=np.float64)
    reference = parent_estimate(_row_weights_for_e164(mlp))
    expected = np.stack(
        [state.mean for state in reference.layers],
        axis=0,
    )
    np.testing.assert_allclose(
        integrated,
        expected,
        rtol=3e-5,
        atol=3e-6,
    )


def test_small_shape_ago_final_matches_e164_clean_room() -> None:
    mlp = _mlp(8, 4, 173003)
    integrated = np.asarray(_run_ago(mlp), dtype=np.float64)
    reference = ago_estimate(_row_weights_for_e164(mlp))
    np.testing.assert_allclose(
        integrated[-1],
        reference.final_mean,
        rtol=5e-5,
        atol=5e-6,
    )


def test_gauge_roundtrip_float32() -> None:
    rng = np.random.Generator(np.random.PCG64(173004))
    n = 8
    mean_np = rng.normal(size=n).astype(np.float32)
    a = rng.normal(size=(n, n)).astype(np.float32)
    covariance_np = (a @ a.T + np.eye(n, dtype=np.float32)).astype(np.float32)
    mean = fnp.asarray(mean_np, dtype=fnp.float32)
    covariance = fnp.asarray(covariance_np, dtype=fnp.float32)
    am, ac = _to_angular(mean, covariance, n)
    gm, gc = _to_gaussian(am, ac, n)
    mean_rel = np.linalg.norm(np.asarray(gm) - mean_np) / np.linalg.norm(mean_np)
    cov_rel = (
        np.linalg.norm(np.asarray(gc) - covariance_np)
        / np.linalg.norm(covariance_np)
    )
    assert mean_rel <= 2e-6
    assert cov_rel <= 2e-6


def test_radial_identity_and_cost() -> None:
    assert abs(radial_a1(1024) - 0.9997558892135413) <= 1e-15
    c = analytic_cost_receipt()
    assert c["all_in_upper"] == 112_131_571_712
    assert c["cap_flops"] == 296_868_139_499
    assert c["passes_cap"]


def test_suite_gate_is_exact_1024x16() -> None:
    weights = [fnp.zeros((1024, 1024), dtype=fnp.float32) for _ in range(16)]
    mlp = MLP(width=1024, depth=16, weights=weights, seed=0, name="shape-only")
    assert suite_shape(mlp)

    off_depth = MLP(
        width=1024,
        depth=15,
        weights=weights[:15],
        seed=0,
        name="off-depth",
    )
    assert not suite_shape(off_depth)
