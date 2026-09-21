from __future__ import annotations

import numpy as np

from methods.e142_response_aligned_d21 import (
    MODULE_CAP_FLOPS,
    ResidualState,
    TierFactors,
    adaptive_response_sequence,
    canonical_qr,
    orientation_certificate,
    production_cost_receipt,
    residual_left_action,
    residual_right_action,
)


def _orth(rng: np.random.Generator, rows: int, cols: int) -> np.ndarray:
    q, _ = np.linalg.qr(rng.standard_normal((rows, cols)))
    return q[:, :cols]


def _tier(
    rng: np.random.Generator,
    k: int,
    n: int,
    q: int,
) -> TierFactors:
    return TierFactors(
        la=rng.standard_normal((k, n, n)),
        lp=rng.standard_normal((k, n, n)),
        fa=rng.standard_normal((k, q, n)),
        fp=rng.standard_normal((k, q, n)),
    )


def _materialize(t: TierFactors) -> np.ndarray:
    out = np.zeros((t.la.shape[1], t.fa.shape[1]), dtype=np.float64)
    for s in range(t.la.shape[0]):
        out += t.la[s] @ t.fa[s].T
        out += t.lp[s] @ t.fp[s].T
    return out


def test_right_left_actions_equal_exact_materialization() -> None:
    rng = np.random.Generator(np.random.PCG64(142001))
    n, q1, q2, r = 8, 5, 3, 2
    qc = _orth(rng, n, q1)
    u2 = _orth(rng, q1, q2)
    shared = _tier(rng, 3, n, q1)
    nested = _tier(rng, 2, n, q2)
    state = ResidualState(q_c=qc, u2=u2, shared=shared, nested=nested)

    c = _materialize(shared) + _materialize(nested) @ u2.T
    d = c @ qc.T

    s = rng.standard_normal((n, r))
    t = rng.standard_normal((n, r))
    np.testing.assert_allclose(
        residual_right_action(state, s).value,
        d @ s,
        rtol=0.0,
        atol=2e-11,
    )
    np.testing.assert_allclose(
        residual_left_action(state, t).value,
        d.T @ t,
        rtol=0.0,
        atol=2e-11,
    )


def test_orientation_certificate_is_sourcewise_sharper() -> None:
    rng = np.random.Generator(np.random.PCG64(142002))
    n, q1, q2 = 8, 5, 3
    state = ResidualState(
        q_c=_orth(rng, n, q1),
        u2=_orth(rng, q1, q2),
        shared=_tier(rng, 3, n, q1),
        nested=_tier(rng, 2, n, q2),
    )
    e = rng.standard_normal((n, 2))
    orient, norm_only = orientation_certificate(state, e)
    assert np.isfinite(orient)
    assert np.isfinite(norm_only)
    assert orient <= norm_only + 1e-12 * max(1.0, norm_only)


def test_adaptive_response_is_deterministic() -> None:
    rng = np.random.Generator(np.random.PCG64(142003))
    n, q1, q2, r = 8, 5, 3, 2
    state = ResidualState(
        q_c=_orth(rng, n, q1),
        u2=_orth(rng, q1, q2),
        shared=_tier(rng, 3, n, q1),
        nested=_tier(rng, 2, n, q2),
    )
    retained = rng.standard_normal((n, n))
    omega = canonical_qr(rng.standard_normal((n, r)))
    a = adaptive_response_sequence(retained, state, omega)
    b = adaptive_response_sequence(retained, state, omega)
    for name in ("y1", "q1", "z1", "y2", "q2", "b"):
        assert np.array_equal(getattr(a, name), getattr(b, name))


def test_production_module_cost_exact_protocol() -> None:
    cost = production_cost_receipt()
    assert MODULE_CAP_FLOPS == 296_868_139_499
    assert cost["left_factor_build_upper"] == 17_179_869_184
    assert cost["shared_response_actions_upper"] == 94_489_280_512
    assert cost["nested_response_actions_upper"] == 83_751_862_272
    assert cost["basis_lifts_upper"] == 981_467_136
    assert cost["adaptive_qr_upper"] == 67_108_864
    assert cost["adaptive_query_products_upper"] == 134_217_728
    assert cost["certificate_norms_upper"] == 8_858_370_048
    assert cost["helper_reserve"] == 20_000_000_000
    assert cost["all_in_upper"] == 225_462_175_744
    assert cost["slack_to_module_cap"] == 71_405_963_755
    assert cost["passes_cap"]
