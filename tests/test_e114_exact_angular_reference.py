from __future__ import annotations

import math

import numpy as np

from methods.e114_exact_angular_reference import (
    build_exact_reference,
    he_weights,
    oracle_flux_basis,
    partition_diagnostics,
    projection_metrics,
)


def test_original_e114_scalar_fixture_reproduced() -> None:
    weights = [
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64),
        np.array([[1.0, 1.0], [-2.0, 0.0]], dtype=np.float64),
        np.array([[2.0], [-1.0]], dtype=np.float64),
    ]
    ref = build_exact_reference(weights)
    expected = (math.sqrt(17.0) - 3.0) / (2.0 * math.sqrt(2.0 * math.pi))

    assert partition_diagnostics(ref.sectors)["complete"]
    assert abs(float(ref.mean[0]) - expected) <= 1e-14
    assert abs(float(ref.flux_mean[0]) - expected) <= 1e-14
    assert abs(float(ref.mean[0] - ref.flux_mean[0])) <= 1e-14
    assert ref.covariance.shape == (1, 1)
    assert ref.covariance[0, 0] >= -1e-14


def test_projection_remainder_identities() -> None:
    weights = he_weights(114199, width=4, depth=3)
    ref = build_exact_reference(weights)

    identity = np.eye(4, dtype=np.float64)
    keep_all = projection_metrics(ref, identity)
    assert keep_all["bias_l2"] <= 1e-12
    assert keep_all["remainder_mse_total"] <= 1e-12
    assert keep_all["relative_flux_energy_residual"] <= 1e-12

    keep_none = projection_metrics(ref, np.zeros((4, 0), dtype=np.float64))
    np.testing.assert_allclose(
        keep_none["residual_second_moment"],
        ref.second_moment,
        atol=1e-12,
        rtol=0.0,
    )
    assert abs(
        keep_none["remainder_mse_total"] - float(np.trace(ref.second_moment))
    ) <= 1e-12


def test_oracle_flux_projectors_are_nested_in_energy() -> None:
    weights = he_weights(114198, width=4, depth=3)
    ref = build_exact_reference(weights)
    values = []
    for rank in (1, 2, 4):
        basis = oracle_flux_basis(ref, rank)
        metrics = projection_metrics(ref, basis)
        assert metrics["projector_symmetry_max_abs"] <= 1e-12
        assert metrics["projector_idempotence_max_abs"] <= 1e-12
        values.append(metrics["relative_flux_energy_residual"])
    assert values[1] <= values[0] + 1e-12
    assert values[2] <= values[1] + 1e-12
