from __future__ import annotations

import inspect

import numpy as np

from methods.e048_source_free_response_recurrence import (
    DEPTH,
    SEED,
    WIDTH,
    ResponseState,
    affine_cumulant3_contraction,
    build_synthetic_weights,
    projected_fullwidth_utilization,
    relu_pair_second_moment,
    relu_raw_moment,
    run_synthetic_falsifier,
)


def test_frozen_case_constants_and_rng():
    assert WIDTH == 32
    assert DEPTH == 8
    assert SEED == 48048
    a = build_synthetic_weights()
    b = build_synthetic_weights()
    assert len(a) == DEPTH
    for wa, wb in zip(a, b):
        assert wa.dtype == np.float64
        np.testing.assert_array_equal(wa, wb)
        assert wa.shape == (WIDTH, WIDTH)


def test_exact_zero_bias_angular_identities_below_1e12():
    rhos = np.array([-0.9, -0.5, 0.0, 0.25, 0.75, 0.99], dtype=np.float64)
    # Deterministic high-order angular quadrature is only a cross-check; the
    # production value is the closed-form exact kernel.
    theta = (np.arange(1 << 18, dtype=np.float64) + 0.5) * (2.0 * np.pi / (1 << 18))
    z1 = np.sqrt(2.0) * np.cos(theta)
    z2_base = np.sqrt(2.0) * np.sin(theta)
    for rho in rhos:
        # For an isotropic radial-angular decomposition E[R^2]=2, so angular
        # integration gives the exact Gaussian second ReLU moment in the limit.
        z2 = rho * z1 + np.sqrt(1.0 - rho * rho) * z2_base
        numeric = np.mean(np.maximum(z1, 0.0) * np.maximum(z2, 0.0))
        exact = relu_pair_second_moment(float(rho))
        assert abs(exact - numeric) < 2.0e-10
    expected = {
        1: 1.0 / np.sqrt(2.0 * np.pi),
        2: 0.5,
        3: np.sqrt(2.0 / np.pi),
        4: 1.5,
        5: 4.0 * np.sqrt(2.0 / np.pi),
        6: 7.5,
    }
    for order, value in expected.items():
        assert abs(relu_raw_moment(order) - value) < 1e-12


def test_exact_affine_cumulant_identity_below_1e12():
    rng = np.random.Generator(np.random.PCG64(SEED))
    n = 4
    T = rng.normal(size=(n, n, n)).astype(np.float64)
    T = sum(T.transpose(p) for p in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))) / 6.0
    W = rng.normal(size=(n, n)).astype(np.float64)
    q = rng.normal(size=n).astype(np.float64)
    lhs_tensor = np.einsum('ai,bj,ck,ijk->abc', W, W, W, T, optimize=True)
    lhs = np.einsum('a,b,c,abc->', q, q, q, lhs_tensor, optimize=True)
    rhs = affine_cumulant3_contraction(T, W.T @ q)
    assert abs(float(lhs) - float(rhs)) < 1e-12


def test_runtime_state_is_fixed_rank_and_source_free():
    state = ResponseState.zeros(WIDTH)
    assert state.d3.shape == (WIDTH,)
    assert state.d21.shape == (WIDTH, WIDTH)
    assert state.r4.shape == (WIDTH,)
    assert max(x.ndim for x in (state.d3, state.d21, state.r4)) <= 2
    source = inspect.getsource(type(state))
    assert 'source' not in source.lower()
    assert 'birth' not in source.lower()
    assert 'history' not in source.lower()


def test_frozen_synthetic_falsifier_gates():
    result = run_synthetic_falsifier()
    assert result['finite'] is True
    assert result['deterministic'] is True
    assert result['exact_identity_max_abs'] < 1e-12
    assert result['d21_max_relative_rms'] <= 0.022
    assert result['candidate_final_mse'] <= 0.25 * result['reference_final_mse']
    assert result['state_rank_max'] <= 2
    assert result['state_growth_ok'] is True
    assert result['oracle_runtime_imports'] == 0
    assert result['projected_core_utilization'] <= 0.100
    assert result['projected_total_utilization'] <= 0.125


def test_projected_fullwidth_cost_is_frozen_and_bounded():
    core, total = projected_fullwidth_utilization(width=1024, depth=16)
    assert core <= 0.100
    assert total <= 0.125
    assert core > 0.0
    assert total >= core
