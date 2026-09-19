from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "e114_observability_flux_residual.py"
)
SPEC = importlib.util.spec_from_file_location(
    "e114_observability_flux_residual", SCRIPT
)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_one_layer_relu_boundary_flux_matches_known_gaussian_mean():
    weights = [np.eye(2, dtype=np.float64)]
    segments, counts = MOD.propagate_angular_partition(weights)
    assert counts == [4]
    assert MOD.partition_ok(segments)

    flux = MOD.boundary_flux_gaussian_mean(segments)
    expected = np.full(2, 1.0 / math.sqrt(2.0 * math.pi))
    assert np.max(np.abs(flux["flux_mean"] - expected)) <= 2e-15
    assert np.max(
        np.abs(flux["flux_mean"] - flux["sector_mean"])
    ) <= 2e-15


def test_radial_rb_pair_mean_matches_boundary_flux_on_relu_identity():
    weights = [np.eye(2, dtype=np.float64)]
    segments, _ = MOD.propagate_angular_partition(weights)
    flux = MOD.boundary_flux_gaussian_mean(segments)
    rb = MOD.exact_radial_rb_moments(segments)
    assert np.max(np.abs(rb["mean"] - flux["flux_mean"])) <= 2e-15
    assert np.min(np.linalg.eigvalsh(rb["covariance"])) >= -1e-14


def test_random_partition_reproduces_network_on_dense_angle_grid():
    weights = MOD.make_weights(2, 5, 3, 991141)
    segments, _ = MOD.propagate_angular_partition(weights)
    assert MOD.partition_ok(segments)

    for theta in np.linspace(0.0, MOD.TWO_PI, 257, endpoint=False):
        direct = MOD.forward(weights, MOD.qvec(float(theta)))
        coeff = MOD.coeff_at(segments, float(theta))
        piecewise = MOD.qvec(float(theta)) @ coeff
        assert np.max(np.abs(direct - piecewise)) <= 2e-11


def test_observability_projector_is_weight_only_orthogonal_projector():
    weights = MOD.make_weights(2, 6, 4, 991142)
    obs = MOD.observability_projector(weights, 2)
    p = obs["projector"]
    assert obs["relative_eigengap"] > 0.0
    assert np.max(np.abs(p - p.T)) <= 1e-12
    assert np.max(np.abs(p @ p - p)) <= 1e-12
    assert np.linalg.norm(p, 2) <= 1.0 + 1e-12


def test_exact_angular_second_moment_formula():
    m = MOD.angular_second_moment(0.0, 2.0 * math.pi)
    expected = math.pi * np.eye(2)
    assert np.max(np.abs(m - expected)) <= 2e-15
