import math

import numpy as np

from methods.e032_backward_cubature import (
    apply_reflections,
    backward_probes,
    build_base_points,
    gaussian_radius_mean,
)


def test_small_support_has_four_bases_and_antipodal_second_moment():
    n = 16
    base = build_base_points(np, n)
    assert base.shape == (4 * n, n)
    norms = np.sqrt(np.sum(base * base, axis=1))
    assert np.max(np.abs(norms - 1.0)) < 1e-12
    second = (base.T @ base) / base.shape[0]
    assert np.max(np.abs(second - np.eye(n) / n)) < 1e-12


def test_reflections_preserve_norms_and_second_moment():
    n = 16
    base = build_base_points(np, n)
    probes = np.zeros((2, n), dtype=np.float64)
    probes[0, :2] = [1.0, -2.0]
    probes[1, 2:5] = [3.0, 1.0, -1.0]
    probes /= np.sqrt(np.sum(probes * probes, axis=1, keepdims=True))
    rotated = apply_reflections(np, base, probes)
    assert np.max(np.abs(np.sum(rotated * rotated, axis=1) - 1.0)) < 1e-12
    second = (rotated.T @ rotated) / rotated.shape[0]
    assert np.max(np.abs(second - np.eye(n) / n)) < 1e-12


def test_backward_probes_use_all_layers_and_are_deterministic():
    n = 8
    w0 = np.eye(n, dtype=np.float64) * 2.0
    w1 = np.eye(n, dtype=np.float64) * 3.0
    a = backward_probes(np, [w0, w1], n_probes=4)
    b = backward_probes(np, [w0, w1], n_probes=4)
    c = backward_probes(np, [w0, np.eye(n)], n_probes=4)
    assert a.shape == (4, n)
    assert np.max(np.abs(a - b)) == 0.0
    assert np.max(np.abs(a - c)) > 0.0
    assert np.max(np.abs(np.sqrt(np.sum(a * a, axis=1)) - 1.0)) < 1e-12


def test_phase2_support_count_and_radius_formula():
    base = build_base_points(np, 1024)
    assert base.shape == (4096, 1024)
    assert 2 * base.shape[0] == 8192
    for n in (1, 2, 8, 16):
        expected = math.sqrt(2.0) * math.exp(
            math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0)
        )
        assert abs(gaussian_radius_mean(n) - expected) < 1e-14
