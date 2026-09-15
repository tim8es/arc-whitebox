from __future__ import annotations

import numpy as np

from methods.e031_k22_memory import (
    RANK,
    best_rank,
    instrument_v25_source,
    transported_relative_error,
)


def test_best_rank_is_exact_for_rank8_matrix() -> None:
    rng = np.random.default_rng(31)
    left = rng.standard_normal((24, 8))
    right = rng.standard_normal((8, 24))
    matrix = left @ right
    approx, retained = best_rank(matrix, RANK)
    assert np.linalg.norm(matrix - approx) / np.linalg.norm(matrix) < 1e-12
    assert retained > 1.0 - 1e-12


def test_transport_error_zero_for_rank8_residual() -> None:
    rng = np.random.default_rng(32)
    left = rng.standard_normal((20, 8))
    right = rng.standard_normal((8, 20))
    residual = left @ right
    w2 = rng.standard_normal((20, 20)) ** 2
    approx, _ = best_rank(residual, RANK)
    err = transported_relative_error(w2, residual, approx)
    assert err < 1e-12


def test_instrumentation_is_single_reversible_append() -> None:
    source = (
        "            if regen:\n"
        "                k22row = K22 @ ones_n\n"
        "                g_prev = ((K4v + k22row) * float(st[\"cA\"])\n"
        "                          + (fnp.sum(K4v) + fnp.sum(k22row)) * float(st[\"cI\"]))\n"
        "                var_prev = K2v\n"
        "                lam_prev = float(LAM[min(li, len(LAM) - 1)])\n"
    )
    patched, marker = instrument_v25_source(source)
    assert patched.count(marker) == 1
    assert patched.replace(marker, "", 1) == source
    assert RANK == 8
    forbidden = ("clip(", "pinv", "jitter", "ridge", "fallback")
    assert not any(token in marker for token in forbidden)
