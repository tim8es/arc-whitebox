from __future__ import annotations

from pathlib import Path

import numpy as np

from methods.e038_sobol_trajectory_qmc import (
    DIMENSION,
    M_POWER,
    N_SAMPLES,
    SCRAMBLE_SEED,
    build_samples,
    run_trajectories,
)


def test_frozen_samples_are_exact_shape_dtype_finite_and_deterministic():
    a = build_samples()
    b = build_samples()
    assert DIMENSION == 1024
    assert N_SAMPLES == 8192
    assert M_POWER == 13
    assert SCRAMBLE_SEED == 38038
    assert a.shape == (8192, 1024)
    assert a.dtype == np.float32
    assert np.isfinite(a).all()
    np.testing.assert_array_equal(a, b)


def test_small_network_matches_explicit_numpy_trajectory_reference():
    samples = np.asarray(
        [[-1.0, 0.5, 2.0], [1.5, -0.25, -2.0], [0.25, 0.75, -0.5]],
        dtype=np.float32,
    )
    w0 = np.asarray([[0.5, -0.25, 1.0], [1.0, 0.5, -0.5], [-0.5, 0.75, 0.25]], dtype=np.float32)
    w1 = np.asarray([[1.0, 0.0, -0.5], [-0.25, 0.75, 0.5], [0.5, -1.0, 0.25]], dtype=np.float32)
    out = run_trajectories(np, samples, [w0, w1])

    x = samples.copy()
    ref = []
    for w in (w0, w1):
        x = np.maximum(x @ w, 0.0)
        ref.append(np.mean(x, axis=0))
    ref = np.stack(ref, axis=0)
    np.testing.assert_allclose(out, ref, rtol=0.0, atol=1e-7)


def test_zero_weights_emit_zero_and_shape_is_depth_by_width():
    samples = np.ones((5, 4), dtype=np.float32)
    weights = [np.zeros((4, 4), dtype=np.float32) for _ in range(3)]
    out = run_trajectories(np, samples, weights)
    assert out.shape == (3, 4)
    np.testing.assert_array_equal(out, np.zeros((3, 4), dtype=np.float32))


def test_source_scope_is_positive_equal_weight_qmc_only():
    src = Path("methods/e038_sobol_trajectory_qmc.py").read_text(encoding="utf-8")
    assert "N_SAMPLES = 8192" in src
    assert "DIMENSION = 1024" in src
    assert "M_POWER = 13" in src
    assert "SCRAMBLE_SEED = 38038" in src
    assert "qmc.Sobol" in src
    assert "scramble=True" in src
    assert "random_base2(m=M_POWER)" in src
    assert "ndtri" in src
    assert ".mean(axis=0)" in src or "xp.mean(x, axis=0)" in src
    forbidden = ("covariance", "k3", "k4", "control_variate", "antithetic", "reweight")
    lower = src.lower()
    assert all(word not in lower for word in forbidden)
