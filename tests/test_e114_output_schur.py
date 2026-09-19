from __future__ import annotations

import numpy as np

from methods.e114_output_schur import (
    compressed_weights,
    exact_final_mean,
    exact_penultimate_preact_second_moment,
    layer2_intervals,
    make_network,
    output_weighted_diagonal,
    pooled_bias_mse,
    schur_rank_compression,
)


def test_exact_reference_and_second_moment_are_deterministic() -> None:
    w1 = make_network(seed=114201)
    w2 = make_network(seed=114201)
    for a, b in zip(w1, w2, strict=True):
        np.testing.assert_array_equal(a, b)

    i1 = layer2_intervals(w1)
    i2 = layer2_intervals(w2)
    m1 = exact_penultimate_preact_second_moment(i1, w1[2])
    m2 = exact_penultimate_preact_second_moment(i2, w2[2])
    np.testing.assert_array_equal(m1, m2)
    assert float(np.min(np.linalg.eigvalsh(m1))) >= -1e-11


def test_schur_remainder_matches_omitted_weighted_spectrum() -> None:
    weights = make_network(seed=114202)
    intervals = layer2_intervals(weights)
    m = exact_penultimate_preact_second_moment(intervals, weights[2])
    d = output_weighted_diagonal(weights[3])
    comp = schur_rank_compression(m, d, rank=2)
    assert abs(comp["remainder_bound"] - comp["omitted_eigenvalue_sum"]) <= 1e-10
    assert comp["remainder_bound"] >= -1e-12
    assert comp["min_residual_eigenvalue"] >= -1e-10


def test_exact_proxy_bias_is_bounded_by_schur_certificate() -> None:
    weights = make_network(seed=114203)
    intervals = layer2_intervals(weights)
    m = exact_penultimate_preact_second_moment(intervals, weights[2])
    d = output_weighted_diagonal(weights[3])
    comp = schur_rank_compression(m, d, rank=2)
    exact, _ = exact_final_mean(weights)
    proxy, _ = exact_final_mean(compressed_weights(weights, comp["K"]))
    actual = pooled_bias_mse(exact, proxy)
    assert actual <= comp["remainder_bound"] + 1e-12
