from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "e113_deep_folded_ridge_residual.py"
)
SPEC = importlib.util.spec_from_file_location(
    "e113_deep_folded_ridge_residual", SCRIPT
)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_exact_spherical_projection_moments():
    # On S^1, E|cos(theta)| = 2/pi.
    assert abs(MOD.sphere_abs_projection_mean(2) - 2.0 / math.pi) <= 1e-15

    for n in (2, 3, 8, 16):
        m = MOD.sphere_abs_projection_mean(n)
        second = 1.0 / n - m * m
        assert 0.0 < m < 1.0
        assert second > 0.0
        # R and Q are independent in X=RQ, so E[R] E|Q1| = E|N(0,1)|.
        assert abs(
            MOD.chi_mean(n) * m - math.sqrt(2.0 / math.pi)
        ) <= 2e-14


def test_deep_probe_gradient_matches_finite_difference():
    weights = MOD.make_weights(5, 4, 99113)
    v, diag = MOD.deep_probe_direction(weights)
    assert diag["gradient_norm"] > 1e-12
    assert diag["unit_norm_error"] <= 1e-12
    assert diag["probe_min_abs_preactivation"] > 1e-8

    n = 5
    probe = np.ones(n, dtype=np.float64) / math.sqrt(n)
    direction = np.array([0.3, -0.2, 0.5, -0.1, 0.7], dtype=np.float64)
    direction /= np.linalg.norm(direction)

    _, _, masks = MOD.forward_with_masks(weights, probe)
    g = np.ones(n, dtype=np.float64) / math.sqrt(n)
    for w, mask in zip(reversed(weights), reversed(masks)):
        g = (g * mask.astype(np.float64)) @ w.T

    eps = 1e-7
    f_plus = float(np.sum(MOD.forward(weights, probe + eps * direction)) / math.sqrt(n))
    f_minus = float(np.sum(MOD.forward(weights, probe - eps * direction)) / math.sqrt(n))
    fd = (f_plus - f_minus) / (2.0 * eps)
    exact = float(g @ direction)
    assert abs(fd - exact) <= 2e-8


def test_folded_control_exactly_removes_one_dimensional_even_ridge():
    # F(x1,x2)=(ReLU(x1),0).  With v=e1, the antithetic radial-RB
    # contribution is exactly proportional to |q1|, so E113 must make it
    # constant for every q, not merely in expectation.
    weights = [
        np.array(
            [
                [1.0, 0.0],
                [0.0, 0.0],
            ],
            dtype=np.float64,
        )
    ]
    v = np.array([1.0, 0.0], dtype=np.float64)
    a = MOD.deterministic_ray_coefficient(weights, v)
    mu = MOD.chi_mean(2)
    m = MOD.sphere_abs_projection_mean(2)

    theta = np.linspace(0.0, 2.0 * math.pi, 41, endpoint=False)
    q = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    _, candidate, centered = MOD.block_contributions(
        weights, q, v, a, mu, m
    )

    expected = np.array([0.5 * mu * m, 0.0], dtype=np.float64)
    assert np.max(np.abs(candidate - expected[None, :])) <= 2e-15
    assert np.max(np.abs(centered)) < 1.0


def test_haar_is_orthogonal_and_seed_deterministic():
    rng_a = np.random.Generator(np.random.PCG64(99114))
    rng_b = np.random.Generator(np.random.PCG64(99114))
    qa, ea = MOD.canonical_haar(rng_a, 8)
    qb, eb = MOD.canonical_haar(rng_b, 8)
    assert np.array_equal(qa, qb)
    assert ea <= 1e-12
    assert eb <= 1e-12


def test_small_estimator_replay_is_exact():
    weights = MOD.make_weights(4, 3, 99115)
    v, _ = MOD.deep_probe_direction(weights)
    a = MOD.deterministic_ray_coefficient(weights, v)

    first = MOD.estimator_realizations(weights, v, a, 99116, 32)
    second = MOD.estimator_realizations(weights, v, a, 99116, 32)

    assert np.array_equal(first["baseline"], second["baseline"])
    assert np.array_equal(first["candidate"], second["candidate"])
    assert first["max_haar_orthogonality_error"] <= 1e-12
    assert first["max_abs_centered_control"] < 1.0
