from types import SimpleNamespace

import flopscope.numpy as fnp
import numpy as np

from methods.e062_chassis_falsifier import carrier_predict, full_safety_audit


def _mlp(width=8, depth=4, seed=62062):
    rng = np.random.default_rng(seed)
    weights = [fnp.asarray(rng.normal(0.0, (2.0 / width) ** 0.5, size=(width, width)).astype(np.float32)) for _ in range(depth)]
    return SimpleNamespace(width=width, depth=depth, weights=weights, seed=seed)


def test_full_and_chassis_shapes_are_finite():
    mlp = _mlp()
    full, fs = carrier_predict(mlp, chassis=False)
    chassis, cs = carrier_predict(mlp, chassis=True)
    assert full.shape == (4, 8)
    assert chassis.shape == (4, 8)
    assert bool(fnp.all(fnp.isfinite(full)))
    assert bool(fnp.all(fnp.isfinite(chassis)))
    assert fs["n_rows"] == cs["n_rows"] == 32


def test_repeat_is_bit_deterministic():
    mlp = _mlp(seed=7)
    a, sa = carrier_predict(mlp, chassis=True)
    b, sb = carrier_predict(mlp, chassis=True)
    assert float(fnp.max(fnp.abs(a - b))) == 0.0
    assert sa == sb


def test_safety_audit_has_suffix_layers_only():
    mlp = _mlp(depth=5)
    audit = full_safety_audit(mlp)
    assert len(audit) == 3
    for item in audit:
        assert set(item) == {"dead", "on", "kink", "violation_count", "high_violation_count", "weighted_violation_num", "weighted_violation_den"}
        assert item["weighted_violation_den"] >= 0.0
