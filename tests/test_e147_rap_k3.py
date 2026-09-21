from __future__ import annotations

import numpy as np

from methods.e147_rap_k3 import (
    CAP_FLOPS,
    production_cost_receipt,
    ranks_for_width,
    rap_k3_estimate,
)


def _weights(n: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    return [
        rng.normal(0.0, np.sqrt(2.0 / n), size=(n, n)).astype(np.float64)
        for _ in range(8)
    ]


def test_frozen_ranks() -> None:
    assert ranks_for_width(32) == (8, 4)
    assert ranks_for_width(16) == (8, 4)
    assert ranks_for_width(1024) == (96, 48)


def test_production_cost_matches_protocol() -> None:
    c = production_cost_receipt()
    assert CAP_FLOPS == 296_868_139_499
    assert c["retained_low_order_public_style_allowance"] == 81_604_378_624
    assert c["backward_response_basis_dense"] == 4_529_848_320
    assert c["thin_qr_sign_canonicalization"] == 1_415_577_600
    assert c["projected_k3_core_transport"] == 3_185_049_600
    assert c["d21_response_and_surrogate"] == 15_099_494_400
    assert c["direct_projected_nonlinear_k3_birth"] == 93_616_865_280
    assert c["error_certificate"] == 60_397_977_600
    assert c["helper_accounting_reserve"] == 21_474_836_480
    assert c["all_in_upper"] == 281_324_027_904
    assert c["slack_flops"] == 15_544_111_595
    assert c["formula_matches_frozen_total"]
    assert c["passes_cap"]


def test_candidate_deterministic_and_pullback_closed() -> None:
    w = _weights(16, 147001)
    a = rap_k3_estimate(w, final_basis_seed=147101)
    b = rap_k3_estimate(w, final_basis_seed=147101)
    assert a.finite
    assert b.finite
    assert np.array_equal(a.final_mean, b.final_mean)
    for xa, xb in zip(a.layers, b.layers):
        assert np.array_equal(xa.core, xb.core)
        assert np.array_equal(xa.d3, xb.d3)
        assert np.array_equal(xa.d21, xb.d21)
        assert xa.rho == xb.rho
    assert max(
        max(x.pullback_residual_u, x.pullback_residual_v)
        for x in a.layers
    ) <= 1e-12
