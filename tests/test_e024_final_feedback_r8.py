import numpy as np

from methods.e024_final_feedback_r8 import select_feedback_rank


def _fixture():
    zf = np.arange(2 * 3 * 32, dtype=np.float32).reshape(2, 3, 32)
    r1 = (1000 + np.arange(2 * 5 * 16, dtype=np.float32)).reshape(2, 5, 16)
    r2 = (2000 + np.arange(2 * 5 * 16, dtype=np.float32)).reshape(2, 5, 16)
    return zf, r1, r2


def test_final_layer_keeps_prefix8_of_each_feedback_half():
    zf, r1, r2 = _fixture()
    zf_use, r1_use, r2_use, rank = select_feedback_rank(zf, r1, r2, is_last=True)

    expected_zf = np.concatenate([zf[..., :8], zf[..., 16:24]], axis=-1)
    np.testing.assert_array_equal(zf_use, expected_zf)
    np.testing.assert_array_equal(r1_use, r1[..., :8])
    np.testing.assert_array_equal(r2_use, r2[..., :8])
    assert rank == 8


def test_nonfinal_layer_retains_rank16_feedback_unchanged():
    zf, r1, r2 = _fixture()
    zf_use, r1_use, r2_use, rank = select_feedback_rank(zf, r1, r2, is_last=False)

    np.testing.assert_array_equal(zf_use, zf)
    np.testing.assert_array_equal(r1_use, r1)
    np.testing.assert_array_equal(r2_use, r2)
    assert rank == 16


def test_selection_is_deterministic_and_does_not_mutate_inputs():
    zf, r1, r2 = _fixture()
    before = tuple(x.copy() for x in (zf, r1, r2))

    first = select_feedback_rank(zf, r1, r2, is_last=True)
    second = select_feedback_rank(zf, r1, r2, is_last=True)

    for got, again in zip(first[:3], second[:3]):
        np.testing.assert_array_equal(got, again)
    for got, orig in zip((zf, r1, r2), before):
        np.testing.assert_array_equal(got, orig)
