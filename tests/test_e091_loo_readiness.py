import numpy as np

from methods.e091_loo_readiness import (
    PHASE2_BUDGET,
    build_tiny_problem,
    dense_dot_cost,
    direct_loo_predictions,
    full_ridge_fit,
    loo_press_predictions,
    signed_influence_metrics,
)


def test_exact_rowwise_loo_identity_and_leverage():
    X, Z, _ = build_tiny_problem()
    lam = 1.0
    press, h = loo_press_predictions(X, Z, lam)
    direct = direct_loo_predictions(X, Z, lam)
    diff = press - direct
    assert np.max(np.abs(diff)) <= 1e-12
    assert np.linalg.norm(diff) / np.linalg.norm(direct) <= 1e-12
    assert np.min(1.0 - h) >= 1e-6


def test_omitted_target_invariance_and_full_fit_counterexample():
    X, Z, _ = build_tiny_problem()
    lam = 1.0
    i = 3
    delta = np.array([7.0, -5.0], dtype=np.float64)

    full0, _ = full_ridge_fit(X, Z, lam)
    loo0, _ = loo_press_predictions(X, Z, lam)

    Zp = Z.copy()
    Zp[i] += delta
    full1, _ = full_ridge_fit(X, Zp, lam)
    loo1, _ = loo_press_predictions(X, Zp, lam)

    assert np.max(np.abs(full1[i] - full0[i])) >= 1e-2
    assert np.max(np.abs(loo1[i] - loo0[i])) <= 1e-12


def test_signed_influence_gates():
    X, Z, _ = build_tiny_problem()
    metrics = signed_influence_metrics(X, Z, 1.0)
    assert metrics["max_row_l1"] <= 4.0
    assert metrics["max_negative_mass"] <= 1.5
    assert metrics["max_abs_weight"] <= 2.0
    assert metrics["max_abs_loo_prediction"] <= 4.0 * metrics["max_abs_target"]
    assert metrics["finite"] is True


def test_phase2_dense_correction_cost_gate():
    cost = dense_dot_cost(p=16, q=16384, dtype_bytes=4)
    assert cost["exact_flops"] == 507_904
    assert cost["ceiling_flops"] == 524_288
    assert cost["ceiling_fraction"] == 524_288 / PHASE2_BUDGET
    assert cost["ceiling_fraction"] <= 2.5e-7
    assert cost["coefficient_bytes"] == 1_048_576
