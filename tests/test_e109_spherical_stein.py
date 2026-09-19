from __future__ import annotations

import math

import numpy as np

from methods.e109_spherical_stein import mean_chi_radius


def test_mean_chi_radius_positive_and_sub_sqrt_n():
    r = mean_chi_radius(1024)
    assert math.isfinite(r)
    assert 31.9 < r < 32.0


def test_spherical_stein_identity_for_quadratic_by_monte_carlo():
    n = 8
    rng = np.random.Generator(np.random.PCG64(109001))
    q = rng.standard_normal((200000, n))
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    v = rng.standard_normal(n)
    v /= np.linalg.norm(v)
    u = rng.standard_normal(n)
    u /= np.linalg.norm(u)
    vq = q @ v
    uq = q @ u
    a = vq * vq
    grad_dot_u = 2.0 * vq * ((u @ v) - vq * uq)
    c = grad_dot_u - (n - 1.0) * uq * a
    assert abs(float(np.mean(c))) < 2.5e-3


def test_antithetic_tangent_sign_convention():
    n = 7
    rng = np.random.Generator(np.random.PCG64(109002))
    q = rng.standard_normal(n)
    q /= np.linalg.norm(q)
    u = rng.standard_normal(n)
    u /= np.linalg.norm(u)
    ut = u - float(q @ u) * q
    assert np.max(np.abs(ut + (-ut))) == 0.0
    assert abs(float(q @ ut)) < 1e-12
