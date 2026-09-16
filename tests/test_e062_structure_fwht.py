from __future__ import annotations

from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

from methods.e062_structure_fwht import (
    Estimator,
    antithetic_next_preact,
    compact_exact_zero_columns,
    fwht_rows,
)


def _hadamard(n: int) -> np.ndarray:
    h = np.asarray([[1.0]], dtype=np.float32)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]]).astype(np.float32)
    return h


def test_fwht_matches_explicit_hadamard() -> None:
    rng = np.random.default_rng(62062)
    x = rng.normal(size=(8, 5)).astype(np.float32)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        got = np.asarray(fwht_rows(fnp.asarray(x)))
    want = _hadamard(8) @ x
    rel = np.sqrt(np.mean((got - want) ** 2)) / max(np.sqrt(np.mean(want**2)), 1e-30)
    assert rel <= 1e-6


def test_antithetic_fold_identity() -> None:
    rng = np.random.default_rng(62062)
    z = rng.normal(size=(16, 8)).astype(np.float32)
    w = rng.normal(size=(8, 8)).astype(np.float32)
    h = np.maximum(z, 0.0)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        p, n = antithetic_next_preact(
            fnp.asarray(z), fnp.asarray(h), fnp.asarray(w), fnp.asarray(z @ w)
        )
    direct_p = h @ w
    direct_n = np.maximum(-z, 0.0) @ w
    assert np.max(np.abs(np.asarray(p) - direct_p)) <= 1e-5
    assert np.max(np.abs(np.asarray(n) - direct_n)) <= 1e-5


def test_zero_skip_is_support_exact() -> None:
    rng = np.random.default_rng(62062)
    a = rng.normal(size=(16, 8)).astype(np.float32)
    a[:, [1, 5]] = 0.0
    w = rng.normal(size=(8, 6)).astype(np.float32)
    with flops.BudgetContext(flop_budget=10**8, quiet=True):
        ca, cw, skipped = compact_exact_zero_columns(fnp.asarray(a), fnp.asarray(w))
        got = np.asarray(ca @ cw)
    assert skipped == 2
    assert np.max(np.abs(got - a @ w)) <= 1e-5


def test_small_predict_finite_and_bit_deterministic() -> None:
    rng = np.random.default_rng(62062)
    width, depth = 8, 4
    weights = [
        rng.normal(scale=np.sqrt(2.0 / width), size=(width, width)).astype(np.float32)
        for _ in range(depth)
    ]
    mlp = SimpleNamespace(width=width, depth=depth, weights=weights, seed=62062)

    def run():
        est = Estimator()
        est.setup(SetupContext(width=width, depth=depth, flop_budget=10**9, api_version="1", seed=62062))
        with flops.BudgetContext(flop_budget=10**9, quiet=True):
            out = np.asarray(est.predict(mlp, 10**9))
        return out, est.last_stats

    a, stats_a = run()
    b, stats_b = run()
    assert np.isfinite(a).all()
    assert np.isfinite(b).all()
    assert np.max(np.abs(a - b)) == 0.0
    assert stats_a == stats_b
    assert stats_a["n_rows"] == 32
