import numpy as np
import flopscope.numpy as fnp

from methods.e021_dead_feedback import transport_feedback_without_source0


def test_source0_stays_zero_and_live_rows_match_original_transport():
    rng = np.random.default_rng(7)
    n = 8
    k = 4
    r = 6
    W = fnp.asarray(rng.standard_normal((n, n), dtype=np.float32))
    Z = rng.standard_normal((k, n, r), dtype=np.float32)
    Z[0] = 0.0
    Zf = fnp.asarray(Z)

    expected = fnp.matmul(W, Zf)
    actual = transport_feedback_without_source0(W, Zf)

    np.testing.assert_array_equal(np.asarray(actual[0]), np.zeros((n, r), dtype=np.float32))
    np.testing.assert_array_equal(np.asarray(actual[1:]), np.asarray(expected[1:]))


def test_transport_is_deterministic_and_does_not_mutate_inputs():
    rng = np.random.default_rng(11)
    n = 6
    k = 3
    r = 4
    W_np = rng.standard_normal((n, n), dtype=np.float32)
    Z_np = rng.standard_normal((k, n, r), dtype=np.float32)
    Z_np[0] = 0.0
    W = fnp.asarray(W_np.copy())
    Z = fnp.asarray(Z_np.copy())

    out1 = transport_feedback_without_source0(W, Z)
    out2 = transport_feedback_without_source0(W, Z)

    np.testing.assert_array_equal(np.asarray(out1), np.asarray(out2))
    np.testing.assert_array_equal(np.asarray(W), W_np)
    np.testing.assert_array_equal(np.asarray(Z), Z_np)
