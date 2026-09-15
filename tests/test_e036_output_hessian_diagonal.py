from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e036_output_hessian_diagonal import (
    H,
    N_PROBES,
    centered_prediction,
    run_centered_hessian,
    static_dense_flop_envelope,
    sylvester_hadamard,
)


def test_full_hadamard_frame_is_frozen_and_orthogonal():
    q = sylvester_hadamard(np, 1024)
    assert H == 1.0
    assert N_PROBES == 1024
    assert q.shape == (1024, 1024)
    assert set(np.unique(q).tolist()) == {-1.0, 1.0}
    gram = (q.T @ q) / 1024.0
    np.testing.assert_array_equal(gram, np.eye(1024))
    np.testing.assert_array_equal(q, sylvester_hadamard(np, 1024))


def test_centered_full_frame_is_exact_for_quadratic_trace_and_zero_for_affine():
    q = sylvester_hadamard(np, 8)
    a = np.diag(np.arange(1.0, 9.0))
    b = np.arange(8.0)
    c = 3.25

    def quadratic(x):
        return np.einsum("bi,ij,bj->b", x, a, x) + x @ b + c

    plus = quadratic(q)[:, None]
    minus = quadratic(-q)[:, None]
    zero = np.asarray([c])
    pred = centered_prediction(np, plus, zero, minus)
    expected = c + np.trace(a)
    np.testing.assert_allclose(pred, [expected], rtol=0.0, atol=1e-12)

    plus_aff = (q @ b + c)[:, None]
    minus_aff = ((-q) @ b + c)[:, None]
    pred_aff = centered_prediction(np, plus_aff, zero, minus_aff)
    np.testing.assert_allclose(pred_aff, zero, rtol=0.0, atol=1e-12)


def _explicit_reference(weights):
    n = weights[0].shape[0]
    q = sylvester_hadamard(np, n)
    paths = np.concatenate([q, -q, np.zeros((1, n))], axis=0)
    rows = []
    for w in weights:
        next_paths = []
        for x in paths:
            next_paths.append(np.maximum(w @ x, 0.0))
        paths = np.stack(next_paths, axis=0)
        rows.append(centered_prediction(np, paths[:n], paths[-1], paths[n : 2 * n]))
    return np.stack(rows, axis=0)


def test_batched_network_prefix_matches_explicit_reference_and_is_deterministic():
    rng = np.random.default_rng(36036)
    weights = [rng.normal(scale=0.4, size=(8, 8)) for _ in range(3)]
    got = run_centered_hessian(np, weights)
    ref = _explicit_reference(weights)
    np.testing.assert_allclose(got, ref, rtol=0.0, atol=1e-12)
    np.testing.assert_array_equal(got, run_centered_hessian(np, weights))
    assert np.isfinite(got).all()


def test_flopscope_runtime_path_is_supported_on_synthetic_input():
    rng = np.random.default_rng(36037)
    weights_np = [rng.normal(scale=0.25, size=(8, 8)).astype(np.float32) for _ in range(2)]
    weights = [fnp.asarray(w) for w in weights_np]
    with flops.BudgetContext(flop_budget=int(1e9), wall_time_limit_s=30.0, quiet=True) as ctx:
        got = run_centered_hessian(fnp, weights)
    arr = np.asarray(got, dtype=np.float64)
    assert arr.shape == (2, 8)
    assert np.isfinite(arr).all()
    assert ctx.flops_used > 0


def test_static_cost_preflight_is_exact_and_below_gate():
    budget = 2**41
    expected = 2 * 16 * 1024**2 * 2049
    assert static_dense_flop_envelope(1024, 16) == expected == 68_753_031_168
    assert expected / budget == 0.0312652587890625
    assert expected / budget <= 0.105
