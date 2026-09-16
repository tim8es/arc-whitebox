from __future__ import annotations

from e052_v29_r256 import EXPECTED_BLOB, fetch_exact_source, git_blob_sha1, load_e052, load_v29


def test_exact_source_hash_and_single_delta():
    data = fetch_exact_source()
    assert git_blob_sha1(data) == EXPECTED_BLOB
    base, _ = load_v29("e052_test_base")
    cand, _ = load_e052("e052_test_cand")
    assert base.Estimator.R_OLD2 == 224
    assert cand.Estimator.R_OLD2 == 256


def test_all_other_frozen_v29_constants_match():
    base, _ = load_v29("e052_test_base_constants")
    cand, _ = load_e052("e052_test_cand_constants")
    attrs = ("AGE_OLD", "R_OLD", "AGE_OLD2", "QPASS2", "R_FB", "R_RES")
    for name in attrs:
        if name == "R_OLD2":
            continue
        assert getattr(base.Estimator, name) == getattr(cand.Estimator, name)
    assert base.Estimator.AGE_OLD == cand.Estimator.AGE_OLD == 4
    assert base.Estimator.R_OLD == cand.Estimator.R_OLD == 384
    assert base.Estimator.AGE_OLD2 == cand.Estimator.AGE_OLD2 == 7
    assert base.Estimator.QPASS2 == cand.Estimator.QPASS2 == 2
    assert base.Estimator.R_FB == cand.Estimator.R_FB == 16
    assert base.Estimator.R_RES == cand.Estimator.R_RES == 16
    assert base.STRASSEN_LEVELS == cand.STRASSEN_LEVELS == 5
    assert base.STRASSEN_MIN == cand.STRASSEN_MIN == 32
    assert base.BETA == cand.BETA == 1.0
    assert base.NO_REGEN is cand.NO_REGEN is False
    assert base.NO_FB is cand.NO_FB is False
    assert base.NO_CONFINE is cand.NO_CONFINE is False
