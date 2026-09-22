import numpy as np

from methods.r202_ta32_kernel import Axis
from methods.r206_ta_rank_sweep import (
    FROZEN_SCHEMES,
    MECHANISM_RATIO_GATE,
    GenericScheme,
    _blocks,
    _unblocks,
    sweep_cost,
)


def _empty_axis(rank):
    return Axis(
        indptr=np.zeros(rank + 1, dtype=np.int64),
        indices=np.zeros(0, dtype=np.int32),
        numerators=np.zeros(0, dtype=np.int64),
        denominators=np.ones(0, dtype=np.int64),
    )


def test_frozen_sweep_is_exactly_four_preregistered_points():
    assert FROZEN_SCHEMES == (
        (26, 8052, "be5a2f9131ef77c3c3351dc1d218d21ec6845368"),
        (28, 9847, "af512cdf847f49d02c97de7d328c8b611ac1a12f"),
        (30, 11890, "0cd64a9423d228b0336b07449d65f26931c5bd35"),
        (32, 14197, "6f2dea4820245303dc2eb1fba13816436fabe54d"),
    )


def test_generic_block_roundtrip():
    for dim in (26, 28, 30, 32):
        x = np.arange((2 * dim) * (3 * dim), dtype=np.float32).reshape(2 * dim, 3 * dim)
        np.testing.assert_array_equal(_unblocks(_blocks(x, dim), dim, *x.shape), x)


def test_every_frozen_leaf_lower_bound_misses_mechanism_gate_at_1024():
    for dim, rank, blob in FROZEN_SCHEMES:
        axis = _empty_axis(rank)
        scheme = GenericScheme(dim, rank, axis, axis, axis, {}, blob, "")
        cost = sweep_cost(scheme, 1024, 1024, 1024)
        assert cost["leaf_ratio"] > MECHANISM_RATIO_GATE
        assert cost["full_ratio"] >= cost["leaf_ratio"]
