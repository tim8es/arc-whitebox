from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

import methods.e049_v29_upstream as v29

BUDGET = 2**41
WIDTH = 32
DEPTH = 8
SEED = 49049
UPSTREAM_GIT_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _mlp():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = 1.0 / np.sqrt(WIDTH)
    weights = [fnp.asarray(rng.standard_normal((WIDTH, WIDTH)) * scale, dtype=fnp.float32)
               for _ in range(DEPTH)]
    return SimpleNamespace(width=WIDTH, depth=DEPTH, seed=SEED, weights=weights)


def _run_once():
    est = v29.Estimator()
    est.setup(SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET, api_version="1", seed=SEED))
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as budget:
        pred = est.predict(_mlp(), BUDGET)
    est.teardown()
    return np.asarray(pred, dtype=np.float64), int(budget.flops_used)


def test_vendor_is_exact_frozen_upstream_blob():
    data = Path(v29.__file__).read_bytes()
    assert len(data) == 93422
    assert _git_blob_sha1(data) == UPSTREAM_GIT_BLOB


def test_frozen_v29_constants_are_unmodified():
    assert v29.Estimator.AGE_OLD == 4
    assert v29.Estimator.R_OLD == 384
    assert v29.Estimator.AGE_OLD2 == 7
    assert v29.Estimator.R_OLD2 == 224
    assert v29.Estimator.R_FB == 16
    assert v29.Estimator.R_RES == 16
    assert v29.STRASSEN_LEVELS == 5
    assert v29.STRASSEN_MIN == 32
    assert v29.BETA == 1.0
    assert v29.NO_REGEN is False
    assert v29.NO_FB is False
    assert v29.NO_CONFINE is False


def test_small_replay_is_finite_shape_and_deterministic():
    p1, f1 = _run_once()
    p2, f2 = _run_once()
    assert p1.shape == (DEPTH, WIDTH)
    assert np.isfinite(p1).all()
    assert np.isfinite(p2).all()
    assert np.array_equal(p1, p2)
    assert f1 == f2
    assert f1 > 0
