from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts import e051_public_mini0_reproduction as repro
from scripts.e051_v29_exact_loader import EXPECTED_BLOB, fetch_exact_source, git_blob_sha1, load_exact_v29


def test_exact_upstream_blob_and_no_source_transform():
    data = fetch_exact_source()
    assert git_blob_sha1(data) == EXPECTED_BLOB
    source = data.decode("utf-8")
    assert "f32 = fnp.float32" in source
    assert "riders = (n == 1024 and L == len(CORR_BETA))" in source


def test_v29_frozen_constants_and_phase2_shape_gate():
    mod, data = load_exact_v29("e051_preflight_v29")
    assert git_blob_sha1(data) == EXPECTED_BLOB
    assert repro.WIDTH == 1024
    assert repro.DEPTH == 16
    assert len(mod.CORR_BETA) == 16
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
    assert repro.WIDTH == 1024 and repro.DEPTH == len(mod.CORR_BETA)
    assert mod.Estimator.R_OLD < repro.WIDTH
    assert mod.Estimator.R_OLD2 < mod.Estimator.R_OLD


def test_metric_and_determinism_instrumentation_is_finite_and_metered():
    a = np.arange(32, dtype=np.float32).reshape(2, 16) / np.float32(100.0)
    target = a[-1].copy()
    raw, metric_flops = repro.metric_flops_and_mse(a, target)
    det, det_flops = repro.determinism_metric(a, a.copy())
    assert np.isfinite(raw)
    assert raw == 0.0
    assert np.isfinite(det)
    assert det == 0.0
    assert metric_flops > 0
    assert det_flops > 0


def test_harness_has_no_estimator_mutation_or_precision_override():
    text = Path(repro.__file__).read_text(encoding="utf-8")
    loader_text = Path("scripts/e051_v29_exact_loader.py").read_text(encoding="utf-8")
    forbidden = (
        "float64)",
        "dtype=fnp.float64",
        "astype(fnp.float64",
        "V17_LAM_SCALE",
        "V25_BETA",
        "V21_R_OLD",
        "V24_R_OLD2",
        "V26_STRASSEN",
        "clip(",
        "jitter",
        "psd",
        "damping",
    )
    lowered = (text + "\n" + loader_text).lower()
    for token in forbidden:
        assert token.lower() not in lowered
    assert "predict_flops + metric_flops" in text
    assert "repeat_predict_flops" in text
    assert "determinism_max_abs_diff" in text
