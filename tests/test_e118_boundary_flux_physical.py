from __future__ import annotations

from methods.e118_boundary_flux_physical import (
    compressed_physical_estimate,
    full_exact_reference,
    make_network,
)


def test_exact_reference_flux_matches_sector_integral() -> None:
    weights = make_network(118118, width=8, depth=4)
    ref = full_exact_reference(weights)
    assert ref["flux_sector_abs_diff"] <= 1e-12
    assert ref["final_interval_count"] > 0


def test_physical_remainder_contains_actual_error() -> None:
    weights = make_network(118118, width=8, depth=4)
    ref = full_exact_reference(weights)
    cand = compressed_physical_estimate(weights, expansion_cap=62)
    error = abs(cand["estimate"] - ref["mean"])
    assert cand["expansions"] <= 62
    assert error <= cand["remainder_certificate"] + 1e-12


def test_deterministic_replay() -> None:
    weights = make_network(118118, width=8, depth=4)
    a = compressed_physical_estimate(weights, expansion_cap=62)
    b = compressed_physical_estimate(weights, expansion_cap=62)
    assert a == b
