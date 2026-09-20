from __future__ import annotations

import numpy as np

from methods.e134_source_k3_direct import (
    Source,
    _edgeworth_relu_mean,
    _materialize_source,
    _transform_core,
    _transport_source,
    production_cost_receipt,
    ranks_for_width,
    source_k3_direct_estimate,
)


def _sym_core(rng: np.random.Generator, r: int) -> np.ndarray:
    c = rng.standard_normal((r, r, r))
    out = np.zeros_like(c)
    perms = [
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0),
    ]
    for p in perms:
        out += np.transpose(c, p)
    return out / 6.0


def test_full_k3_linear_transport_is_exact_for_represented_source() -> None:
    rng = np.random.Generator(np.random.PCG64(134001))
    q0, _ = np.linalg.qr(rng.standard_normal((5, 2)))
    core = _sym_core(rng, 2)
    source = Source(age=2, q=q0, core=core)
    w = rng.standard_normal((5, 4))

    transported = _transport_source(source, w)
    old = _materialize_source(source)
    expected = np.einsum(
        "abc,ai,bj,ck->ijk",
        old, w, w, w, optimize=True
    )
    actual = _materialize_source(transported)
    np.testing.assert_allclose(actual, expected, atol=2e-11, rtol=2e-11)


def test_edgeworth_zero_k3_reduces_to_gaussian_relu_mean() -> None:
    mu = np.array([0.0, 0.5, -0.75], dtype=np.float64)
    sigma = np.array([1.0, 1.25, 0.8], dtype=np.float64)
    k3 = np.zeros(3, dtype=np.float64)
    out, coeff = _edgeworth_relu_mean(mu, sigma, k3)
    assert np.isfinite(out).all()
    assert np.isfinite(coeff).all()
    assert abs(out[0] - 1.0 / np.sqrt(2.0 * np.pi)) <= 1e-14


def test_small_source_path_exercises_nested_age_and_certificate() -> None:
    rng = np.random.Generator(np.random.PCG64(134002))
    weights = []
    first = rng.standard_normal((2, 8))
    weights.append(first)
    for _ in range(7):
        weights.append(rng.standard_normal((8, 8)) * 0.4)

    result = source_k3_direct_estimate(
        weights, trajectories=128, seed=134003
    )
    assert result.finite
    assert result.nested_path_exercised
    assert result.max_core_symmetry_error <= 1e-10
    assert result.max_slice_disagreement <= 1e-10
    assert result.max_birth_projection_identity_error <= 1e-12
    assert np.all(
        np.abs(result.actual_closure_residual)
        <= result.certificate_bounds + 1e-10
    )


def test_frozen_ranks_and_production_cost() -> None:
    assert ranks_for_width(32) == (1, 2, 1)
    assert ranks_for_width(1024) == (32, 48, 24)
    cost = production_cost_receipt()
    assert cost["all_in_upper"] == 189_262_033_408
    assert cost["formula_matches_frozen_total"]
    assert cost["passes_cap"]
    assert cost["utilization"] < 0.13
