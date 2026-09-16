from types import SimpleNamespace

from methods.e053_v29_adapter import (
    AGE_OLD2,
    DEPTH,
    EXPECTED_BLOB,
    R_OLD2,
    WIDTH,
    fetch_exact_source,
    git_blob_sha1,
    load_e053,
    load_v29,
)


def test_package_safe_import_and_exact_source() -> None:
    data = fetch_exact_source()
    assert git_blob_sha1(data) == EXPECTED_BLOB


def test_frozen_defaults_and_only_two_constant_delta() -> None:
    base, _ = load_v29()
    cand, _ = load_e053()
    assert (base.Estimator.AGE_OLD, base.Estimator.R_OLD) == (4, 384)
    assert (base.Estimator.AGE_OLD2, base.Estimator.R_OLD2) == (7, 224)
    assert (base.Estimator.QPASS2, base.Estimator.R_FB, base.Estimator.R_RES) == (2, 16, 16)
    assert (cand.Estimator.AGE_OLD, cand.Estimator.R_OLD) == (4, 384)
    assert (cand.Estimator.AGE_OLD2, cand.Estimator.R_OLD2) == (AGE_OLD2, R_OLD2) == (6, 256)
    assert (cand.Estimator.QPASS2, cand.Estimator.R_FB, cand.Estimator.R_RES) == (2, 16, 16)


def test_official_shape_synthetic_smoke_object() -> None:
    mlp = SimpleNamespace(width=WIDTH, depth=DEPTH, weights=[None] * DEPTH)
    assert mlp.width == 1024
    assert mlp.depth == 16
    assert len(mlp.weights) == 16
