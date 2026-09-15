# RED contract: production module must not exist before this suite is observed failing.
from __future__ import annotations

import math
import numpy as np

from methods.e047_connected_diagram_dp import (
    KMAX,
    PROBE_COUNT,
    contracted_connected_states,
    cumulants_to_moments,
    explicit_connected_states,
    moments_to_cumulants,
    propagate_contracted_network,
    propagate_explicit_network,
)


def test_frozen_constants():
    assert KMAX == 6
    assert PROBE_COUNT == 32


def test_scalar_partition_mobius_roundtrip_through_order_6():
    cumulants = np.array([0.0, 0.31, 1.17, -0.08, 0.14, -0.03, 0.02], dtype=np.float64)
    moments = cumulants_to_moments(cumulants, KMAX)
    recovered = moments_to_cumulants(moments, KMAX)
    np.testing.assert_allclose(recovered[1:], cumulants[1:], atol=1e-12, rtol=0.0)


def _case_width1():
    weights = [
        np.array([[0.75]], dtype=np.float64),
        np.array([[-1.25]], dtype=np.float64),
    ]
    mean = np.array([0.2], dtype=np.float64)
    cov = np.array([[0.9]], dtype=np.float64)
    probes = np.array([[1.0]], dtype=np.float64)
    return weights, mean, cov, probes


def _case_width2():
    weights = [
        np.array([[0.8, -0.3], [0.25, 1.1]], dtype=np.float64),
        np.array([[1.2, 0.2], [-0.4, 0.7]], dtype=np.float64),
    ]
    mean = np.array([0.15, -0.2], dtype=np.float64)
    cov = np.array([[1.0, 0.2], [0.2, 0.7]], dtype=np.float64)
    probes = np.array([[1.0, 0.0], [0.6, -0.8]], dtype=np.float64)
    return weights, mean, cov, probes


def _case_width3_depth3():
    weights = [
        np.array([[0.9, -0.2, 0.1], [0.3, 0.8, -0.4], [-0.1, 0.25, 1.05]], dtype=np.float64),
        np.array([[0.7, 0.15, -0.25], [-0.2, 1.0, 0.35], [0.4, -0.3, 0.85]], dtype=np.float64),
        np.array([[1.1, -0.1, 0.2], [0.05, 0.95, -0.15], [-0.3, 0.2, 0.75]], dtype=np.float64),
    ]
    mean = np.array([0.05, -0.1, 0.2], dtype=np.float64)
    cov = np.array([[1.0, 0.15, -0.05], [0.15, 0.8, 0.1], [-0.05, 0.1, 1.2]], dtype=np.float64)
    probes = np.array([[1.0, 0.0, 0.0], [0.5, -0.5, np.sqrt(0.5)]], dtype=np.float64)
    return weights, mean, cov, probes


def test_width1_depth2_explicit_matches_contracted_states():
    weights, mean, cov, probes = _case_width1()
    explicit = propagate_explicit_network(weights, mean, cov, probes, kmax=KMAX)
    contracted = propagate_contracted_network(weights, mean, cov, probes, kmax=KMAX)
    for order in range(3, KMAX + 1):
        np.testing.assert_allclose(contracted[order], explicit[order], atol=1e-12, rtol=0.0)


def test_width2_depth2_explicit_dense_tensors_match_contractions():
    weights, mean, cov, probes = _case_width2()
    explicit = propagate_explicit_network(weights, mean, cov, probes, kmax=KMAX)
    contracted = propagate_contracted_network(weights, mean, cov, probes, kmax=KMAX)
    for order in range(3, KMAX + 1):
        assert contracted[order].shape == (probes.shape[0],)
        np.testing.assert_allclose(contracted[order], explicit[order], atol=1e-10, rtol=0.0)


def test_width3_depth3_final_correction_matches_explicit_to_1e9():
    weights, mean, cov, probes = _case_width3_depth3()
    explicit = propagate_explicit_network(weights, mean, cov, probes, kmax=KMAX)
    contracted = propagate_contracted_network(weights, mean, cov, probes, kmax=KMAX)
    coeff = np.array([1.0 / math.factorial(k) for k in range(3, KMAX + 1)], dtype=np.float64)
    explicit_corr = sum(coeff[k - 3] * explicit[k] for k in range(3, KMAX + 1))
    contracted_corr = sum(coeff[k - 3] * contracted[k] for k in range(3, KMAX + 1))
    np.testing.assert_allclose(contracted_corr, explicit_corr, atol=1e-9, rtol=0.0)


def test_helpers_match_and_are_deterministic_without_rank_gt_2_outputs():
    weights, mean, cov, probes = _case_width2()
    a = contracted_connected_states(weights[0], mean, cov, probes, kmax=KMAX)
    b = contracted_connected_states(weights[0], mean, cov, probes, kmax=KMAX)
    for order in range(3, KMAX + 1):
        np.testing.assert_array_equal(a[order], b[order])
        assert np.asarray(a[order]).ndim <= 2

    ref = explicit_connected_states(weights[0], mean, cov, probes, kmax=KMAX)
    for order in range(3, KMAX + 1):
        np.testing.assert_allclose(a[order], ref[order], atol=1e-10, rtol=0.0)
