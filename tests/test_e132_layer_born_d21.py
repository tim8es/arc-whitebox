from __future__ import annotations

import math

import numpy as np

from methods.e132_exact_angular_reference import build_exact_reference, he_weights
from methods.e132_layer_born_d21 import (
    PROD_CAP,
    layer_born_d21_estimate,
    production_cost_receipt,
)


def test_exact_angular_identity_relu_mean() -> None:
    weights = [
        np.eye(2, dtype=np.float64),
        np.eye(2, dtype=np.float64),
    ]
    ref = build_exact_reference(weights)
    target = np.full(2, 1.0 / math.sqrt(2.0 * math.pi), dtype=np.float64)
    np.testing.assert_allclose(ref.mean, target, atol=1e-13, rtol=0.0)
    assert ref.finite


def test_candidate_deterministic_nested_and_birth_identity() -> None:
    weights = he_weights(132001, width=8, depth=8)
    a = layer_born_d21_estimate(
        weights,
        pilot=64,
        evaluation=128,
        seed=132777,
    )
    b = layer_born_d21_estimate(
        weights,
        pilot=64,
        evaluation=128,
        seed=132777,
    )

    assert np.array_equal(a.mean, b.mean)
    assert np.array_equal(a.baseline_mean, b.baseline_mean)
    assert np.array_equal(a.d21_correction, b.d21_correction)
    assert a.certificate_mse == b.certificate_mse
    assert a.ledger == b.ledger
    assert a.diagnostics == b.diagnostics
    assert a.nested_path_exercised
    assert a.birth_identity_max_abs <= 1e-12
    assert a.diagnostics["d21_correction_diag_max_abs"] == 0.0
    assert a.finite


def test_production_cost_exact_protocol_receipt() -> None:
    cost = production_cost_receipt()
    assert cost["width"] == 1024
    assert cost["depth"] == 16
    assert cost["pilot"] == 256
    assert cost["evaluation"] == 2048
    assert cost["r_y"] == 32
    assert cost["r_s"] == 48
    assert cost["r_n"] == 24
    assert cost["all_in_upper"] == 120_722_404_352
    assert cost["hard_cap_flops"] == PROD_CAP == 136_758_472_261
    assert cost["slack_flops"] == 16_036_067_909
    assert cost["passes_cap"]
