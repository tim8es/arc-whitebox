from __future__ import annotations

import hashlib
import numpy as np

from methods.e137_h137_countsketch import (
    balanced_countsketch_plan,
    contraction_flops_exact,
    contraction_flops_sketch,
    git_blob_sha1_bytes,
    sketch_last_axis,
    sketched_product,
)


def test_git_blob_sha1_matches_git_object_rule() -> None:
    data = b"hello\n"
    expected = hashlib.sha1(b"blob 6\0hello\n").hexdigest()
    assert git_blob_sha1_bytes(data) == expected


def test_balanced_plan_is_deterministic_and_uses_every_column_once() -> None:
    p1, s1 = balanced_countsketch_plan(16, 8, 137512007)
    p2, s2 = balanced_countsketch_plan(16, 8, 137512007)
    assert np.array_equal(p1, p2)
    assert np.array_equal(s1, s2)
    assert sorted(p1.reshape(-1).tolist()) == list(range(16))
    assert set(np.unique(s1).tolist()) <= {-1.0, 1.0}


def test_sketch_last_axis_matches_manual_pairing() -> None:
    x = np.arange(16, dtype=np.float64).reshape(1, 1, 16)
    perm, signs = balanced_countsketch_plan(16, 8, 5)
    got = sketch_last_axis(x, perm, signs)
    want = (
        x[..., perm[:, 0]] * signs[perm[:, 0]]
        + x[..., perm[:, 1]] * signs[perm[:, 1]]
    )
    assert np.array_equal(got, want)


def test_sketch_product_is_deterministic() -> None:
    rng = np.random.Generator(np.random.PCG64(17))
    x = rng.standard_normal((3, 5, 16))
    y = rng.standard_normal((3, 4, 16))
    a = sketched_product(x, y, layer=7, s=8)
    b = sketched_product(x, y, layer=7, s=8)
    assert np.array_equal(a, b)


def test_frozen_cost_formula_s512_is_cheaper_than_exact_for_v25_tiers() -> None:
    n, s = 1024, 512
    for q in (384, 224):
        for k in (1, 3, 7):
            assert contraction_flops_sketch(k, n, q, s) < contraction_flops_exact(k, n, q)
