from __future__ import annotations

import numpy as np

from methods.e125_clifford8_tightframe import (
    clifford8_integer_operators,
    exact_clifford_algebra_report,
    finite_sample_mse_certificate,
    production_operation_ledger,
)


def test_exact_integer_clifford_algebra() -> None:
    report = exact_clifford_algebra_report()
    assert report["pass"]
    assert report["entries_integer_zero_plusminus_one"]
    assert report["signed_permutation_all"]
    assert report["orthogonal_all"]
    assert report["identity_a0_and_skew_nonidentity"]
    assert report["square_minus_identity_nonidentity"]
    assert report["pairwise_anticommutation_nonidentity"]

    ops = clifford8_integer_operators()
    assert len(ops) == 8
    assert all(a.shape == (8, 8) for a in ops)
    assert all(a.dtype == np.int8 for a in ops)


def test_frozen_production_ledger_exact() -> None:
    ledger = production_operation_ledger()
    assert ledger["directions"] == 4032
    assert ledger["static_clifford_algebra_upper"] == 70_000
    assert ledger["base_gaussian_rng_upper"] == 4_128_768
    assert ledger["base_norm_and_normalization_upper"] == 790_272
    assert ledger["signed_permutation_source_materialization_upper"] == 4_128_768
    assert ledger["runtime_frame_gram_norm_orthogonality_upper"] == 33_046_272
    assert ledger["deep_propagation_upper"] == 135_423_590_400
    assert ledger["final_reduction_radial_upper"] == 4_141_952
    assert ledger["all_in_upper"] == 135_469_896_432
    assert ledger["slack_flops"] == 1_288_575_829
    assert ledger["gate_passed"]


def test_weight_only_certificate_is_deterministic_without_source_evaluation() -> None:
    weights = [
        np.array(
            [[1.0, -0.5], [0.25, 2.0], [-1.5, 0.75], [0.6, -0.8],
             [0.4, 0.3], [-0.2, 1.1], [0.9, -1.2], [1.4, 0.2]],
            dtype=np.float64,
        ),
        np.array([[0.8, -0.3], [1.1, 0.7]], dtype=np.float64),
    ]
    a = finite_sample_mse_certificate(weights, frames=252, delta=1.25e-7)
    b = finite_sample_mse_certificate(weights, frames=252, delta=1.25e-7)
    assert a["mse_bound"] == b["mse_bound"]
    assert np.array_equal(a["unit_sphere_output_bound"], b["unit_sphere_output_bound"])
    assert np.array_equal(a["coordinate_abs_error_bound"], b["coordinate_abs_error_bound"])
    assert a["mse_bound"] > 0.0
