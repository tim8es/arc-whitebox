from __future__ import annotations

from methods.e051_v29_adapter import DEPTH, EXPECTED_BLOB, WIDTH, fetch_exact_source, git_blob_sha1, load_exact_v29


def test_exact_upstream_blob_and_f32_source():
    data = fetch_exact_source()
    assert git_blob_sha1(data) == EXPECTED_BLOB
    source = data.decode("utf-8")
    assert "f32 = fnp.float32" in source
    assert "riders = (n == 1024 and L == len(CORR_BETA))" in source


def test_phase2_shape_and_frozen_constants():
    mod, data = load_exact_v29("e051_preflight_v29")
    assert git_blob_sha1(data) == EXPECTED_BLOB
    assert WIDTH == 1024 and DEPTH == 16 and len(mod.CORR_BETA) == 16
    assert mod.Estimator.AGE_OLD == 4
    assert mod.Estimator.R_OLD == 384
    assert mod.Estimator.AGE_OLD2 == 7
    assert mod.Estimator.R_OLD2 == 224
    assert mod.Estimator.QPASS2 == 2
    assert mod.Estimator.R_FB == 16
    assert mod.Estimator.R_RES == 16
    assert mod.STRASSEN_LEVELS == 5
    assert mod.STRASSEN_MIN == 32
    assert mod.BETA == 1.0
    assert mod.NO_REGEN is False
    assert mod.NO_FB is False
    assert mod.NO_CONFINE is False
