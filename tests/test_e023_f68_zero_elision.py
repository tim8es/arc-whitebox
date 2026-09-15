import numpy as np

from methods.e023_f68_zero_elision import (
    generic_residual_without_y,
    transport_source0_dead_feed_columns,
)


def test_generic_residual_without_y_drops_only_zero_right_factor_column():
    rng = np.random.default_rng(23001)
    k, n, rres = 3, 11, 4
    z = rng.standard_normal((k, n, rres + 2))
    l = rng.standard_normal((k, n, rres + 2))
    l[:, :, rres + 1] = 0.0

    zq, lq = generic_residual_without_y(z, l, rres)
    full = np.einsum("kiq,kjq->kij", z, l)
    reduced = np.einsum("kiq,kjq->kij", zq, lq)

    assert zq.shape[-1] == rres + 1
    assert lq.shape[-1] == rres + 1
    np.testing.assert_array_equal(full, reduced)


def test_transport_source0_dead_feed_columns_matches_dense_when_last_two_are_zero():
    rng = np.random.default_rng(23002)
    k, n, rres = 5, 13, 4
    w = rng.standard_normal((n, n))
    z = rng.standard_normal((k, n, rres + 2))
    z[0, :, rres:] = 0.0

    got = transport_source0_dead_feed_columns(w, z, rres)
    want = np.einsum("ij,kjq->kiq", w, z)

    np.testing.assert_allclose(got, want, rtol=0.0, atol=0.0)
    np.testing.assert_array_equal(got[0, :, rres:], 0.0)


def test_transport_is_deterministic_and_does_not_mutate_input():
    rng = np.random.default_rng(23003)
    k, n, rres = 4, 9, 3
    w = rng.standard_normal((n, n))
    z = rng.standard_normal((k, n, rres + 2))
    z[0, :, rres:] = 0.0
    z0 = z.copy()

    a = transport_source0_dead_feed_columns(w, z, rres)
    b = transport_source0_dead_feed_columns(w, z, rres)

    np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(z, z0)
