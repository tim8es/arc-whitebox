from __future__ import annotations

import numpy as np

from methods.e126_adversarial_fixture import (
    build_candidate_visible_fixture,
    dense_vs_latent_probe,
    positive_mix_condition_number,
)
from methods.e126_frame_certificate import (
    RMS_CAP,
    certified_simplex_frame_mean,
    production_cost_upper,
    regular_simplex_code,
    simplex_algebra_metrics,
)


def test_simplex_algebra() -> None:
    m = simplex_algebra_metrics(regular_simplex_code())
    assert m["max_vertex_norm_error"] <= 2e-14
    assert m["max_vertex_gram_error"] <= 2e-14
    assert m["vertex_sum_inf"] <= 2e-14
    assert m["second_moment_max_abs_error"] <= 2e-14


def test_dense_reparameterization_preserves_function() -> None:
    state = build_candidate_visible_fixture(
        dimension=8,
        block_seed_start=126800,
        mixing_seed=126890,
    )
    assert abs(positive_mix_condition_number(state) - 100.0) <= 1e-10
    assert dense_vs_latent_probe(state, seed=126899, samples=32) <= 1e-10


def test_target_free_certificate_smoke() -> None:
    state = build_candidate_visible_fixture(
        dimension=8,
        block_seed_start=126800,
        mixing_seed=126890,
    )
    out = certified_simplex_frame_mean(
        state.dense_weights,
        frames=8,
        seed=126900,
    )
    assert out.finite
    assert out.observed_range_violation_max_abs <= 1e-12
    assert out.rms_certificate >= out.variance_only_rms >= 0.0
    assert out.frame_contributions.shape == (8, 8)
    assert np.isfinite(out.coordinate_radii).all()


def test_production_budget_max_frames() -> None:
    p225 = production_cost_upper(225)
    p226 = production_cost_upper(226)
    assert p225["incremental_all_in_upper"] == 136_237_052_214
    assert p225["passes_cap"]
    assert not p226["passes_cap"]
    assert p225["utilization"] < 0.13
    assert RMS_CAP == (1.89e-8) ** 0.5
