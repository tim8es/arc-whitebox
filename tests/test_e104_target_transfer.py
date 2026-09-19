from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "e104_target_transfer.py"
SPEC = importlib.util.spec_from_file_location("e104_target_transfer", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_chi_radius_variance_is_positive_and_stable_at_production_width():
    var = MOD.chi_radius_variance(1024)
    assert 0.49 < var < 0.51


def test_small_haar_directions_are_deterministic_and_orthogonal():
    first = MOD.reference_haar_directions_numpy(8, 16, 4104)
    second = MOD.reference_haar_directions_numpy(8, 16, 4104)
    assert np.array_equal(first, second)
    assert first.shape == (8, 8)
    assert MOD.haar_block_orthogonality_max_abs(first, 8) <= 1e-12


def test_small_relu_network_respects_positive_homogeneity():
    weights = MOD.make_weights(8, 3, 5104)
    q = MOD.reference_haar_directions_numpy(8, 16, 6104)[0]
    assert MOD.homogeneity_relative_error(weights, q) <= 2e-6


def test_conditional_radial_mse_formula_matches_manual_identity():
    pairs = np.array(
        [[0.25, 0.5, 0.75], [1.0, 0.5, 0.25], [0.3, 0.2, 0.1]],
        dtype=np.float64,
    )
    chi_width = 8
    mu = MOD.mean_chi_radius(chi_width)
    rel_var = (chi_width - mu * mu) / (mu * mu)
    expected = rel_var * float(np.sum(pairs * pairs)) / (
        pairs.shape[0] ** 2 * pairs.shape[1]
    )
    observed = MOD.conditional_radial_mse_from_scaled_pairs(pairs, chi_width)
    assert observed == expected
    assert observed > 0.0


def test_pair_mean_equals_full_antithetic_mean_at_small_shape():
    width = 8
    depth = 3
    trajectories = 16
    weights = MOD.make_weights(width, depth, 7104)
    directions = MOD.reference_haar_directions_numpy(width, trajectories, 8104)
    mu = MOD.mean_chi_radius(width)
    positive = (mu * directions).astype(np.float32)
    samples = np.concatenate((positive, -positive), axis=0)

    h = samples
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)

    half = trajectories // 2
    full_mean = np.mean(h, axis=0, dtype=np.float64)
    pair_mean = np.mean(
        0.5 * (h[:half].astype(np.float64) + h[half:].astype(np.float64)),
        axis=0,
        dtype=np.float64,
    )
    assert np.max(np.abs(full_mean - pair_mean)) <= 1e-15
