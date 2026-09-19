from __future__ import annotations

import numpy as np

from methods.e122_haar8_simplex_source import (
    PRODUCTION_CAP_FLOPS,
    SOURCE_DIM,
    haar8_antipodal_simplex_mean,
    production_cost_receipt,
    regular_simplex_code,
    simplex_algebra_metrics,
)


def test_simplex_algebra_exact_gate() -> None:
    code = regular_simplex_code()
    metrics = simplex_algebra_metrics(code)
    assert code.shape == (18, 8)
    assert metrics["k"] == 8
    assert metrics["codewords"] == 18
    assert metrics["max_vertex_norm_error"] <= 2e-14
    assert metrics["max_vertex_gram_error"] <= 2e-14
    assert metrics["vertex_sum_inf"] <= 2e-14
    assert metrics["second_moment_max_abs_error"] <= 2e-14


def test_candidate_deterministic_and_frame_exact() -> None:
    weights = [np.eye(8, dtype=np.float64)]
    a = haar8_antipodal_simplex_mean(weights, frames=3, seed=122001)
    b = haar8_antipodal_simplex_mean(weights, frames=3, seed=122001)
    assert np.array_equal(a.mean, b.mean)
    assert a.ledger == b.ledger
    assert a.frame_orthogonality_max_abs <= 2e-12
    assert a.source_direction_norm_max_abs <= 2e-12
    assert a.mean.shape == (SOURCE_DIM,)
    assert a.finite


def test_production_cost_frozen_exact() -> None:
    cost = production_cost_receipt()
    assert cost["directions"] == 4032
    assert cost["simplex_setup_upper"] == 832
    assert cost["haar_frame_rng_mgs_upper"] == 60_669_952
    assert cost["source_code_materialization_upper"] == 66_060_288
    assert cost["deep_propagation_upper"] == 135_423_590_400
    assert cost["final_reduction_radial_upper"] == 4_141_952
    assert cost["all_in_upper"] == 135_554_463_424
    assert cost["hard_cap_flops"] == PRODUCTION_CAP_FLOPS
    assert cost["slack_flops"] == 1_204_008_837
    assert cost["passes_cap"]
