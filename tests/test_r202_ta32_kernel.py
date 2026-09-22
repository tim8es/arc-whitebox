import hashlib

import numpy as np

from methods.r202_ta32_kernel import (
    MECHANISM_RATIO_GATE,
    TA_DIM,
    TA_RANK,
    Axis,
    Scheme,
    _blocks,
    _unblocks,
    fallback_cost,
    git_blob_sha1,
    ta32_cost,
)


def _empty_axis(rows=TA_RANK):
    return Axis(
        indptr=np.zeros(rows + 1, dtype=np.int64),
        indices=np.zeros(0, dtype=np.int32),
        numerators=np.zeros(0, dtype=np.int64),
        denominators=np.ones(0, dtype=np.int64),
    )


def test_git_blob_sha1_matches_git_object_definition():
    data = b"R202"
    expected = hashlib.sha1(b"blob 4\0R202").hexdigest()
    assert git_blob_sha1(data) == expected


def test_block_roundtrip_preserves_matrix():
    x = np.arange(64 * 96, dtype=np.float32).reshape(64, 96)
    blocks = _blocks(x)
    assert blocks.shape == (TA_DIM * TA_DIM, 2, 3)
    np.testing.assert_array_equal(_unblocks(blocks, 64, 96), x)


def test_rank_14197_leaf_alone_exceeds_h185_ratio_gate():
    empty = _empty_axis()
    scheme = Scheme(empty, empty, empty, {"rank": TA_RANK, "tensor": [32, 32, 32]})
    ledger = ta32_cost(scheme, 1024, 1024, 1024)
    # This lower bound excludes every coefficient multiply and every reconstruction add.
    assert ledger["leaf_matmul_flops"] == 930_414_592
    assert ledger["leaf_ratio_to_classical_unpadded"] == TA_RANK / (TA_DIM**3)
    assert ledger["leaf_ratio_to_classical_unpadded"] > MECHANISM_RATIO_GATE


def test_fallback_is_explicit_and_fully_billed():
    ledger = fallback_cost(64, 96, 32, "TEST")
    assert ledger["fallback_count"] == 1
    assert ledger["fallback_flops"] == 2 * 64 * 96 * 32
    assert ledger["arithmetic_flops"] == ledger["fallback_flops"]
