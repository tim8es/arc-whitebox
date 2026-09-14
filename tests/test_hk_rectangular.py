from __future__ import annotations

import numpy as np

from methods.hk_rectangular import (
    SparseBilinearScheme,
    SparseColumn,
    dense_matmul_flops,
    terminal_old_tier_shapes,
)


def _naive_scheme(n: int, m: int, p: int) -> SparseBilinearScheme:
    u = []
    v = []
    w = []
    for i in range(n):
        for j in range(m):
            for k in range(p):
                u.append(SparseColumn((i * m + j,), (1,)))
                v.append(SparseColumn((j * p + k,), (1,)))
                w.append(SparseColumn((i * p + k,), (1,)))
    return SparseBilinearScheme(n, m, p, n * m * p, tuple(u), tuple(v), tuple(w))


def _eval_scalar_scheme(scheme: SparseBilinearScheme, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    af = a.reshape(-1)
    bf = b.reshape(-1)
    out = np.zeros(scheme.n * scheme.p, dtype=np.float64)
    for rank in range(scheme.rank):
        left = sum(c * af[i] for i, c in zip(scheme.u[rank].indices, scheme.u[rank].coeffs, strict=True))
        right = sum(c * bf[i] for i, c in zip(scheme.v[rank].indices, scheme.v[rank].coeffs, strict=True))
        product = left * right
        for i, c in zip(scheme.w[rank].indices, scheme.w[rank].coeffs, strict=True):
            out[i] += c * product
    return out.reshape(scheme.n, scheme.p)


def test_two_cyclic_shifts_preserve_matrix_product() -> None:
    scheme = _naive_scheme(2, 3, 4).cyclic_shift().cyclic_shift()
    assert (scheme.n, scheme.m, scheme.p) == (4, 2, 3)

    rng = np.random.default_rng(7)
    a = rng.standard_normal((4, 2))
    b = rng.standard_normal((2, 3))
    np.testing.assert_allclose(_eval_scalar_scheme(scheme, a, b), a @ b, rtol=0, atol=1e-12)


def test_tier1_dense_leaf_cost_is_frozen() -> None:
    assert dense_matmul_flops(128, 48, 128) == 1_556_480
    hk_rank_products = 3 * 392
    hk_product_flops = hk_rank_products * dense_matmul_flops(8, 8, 8)
    assert hk_product_flops == 1_128_960
    assert int(0.85 * 1_556_480) - hk_product_flops == 194_048


def test_v29_old_tier_terminal_shapes_are_frozen() -> None:
    assert terminal_old_tier_shapes() == (
        (128, 48, 128),
        (128, 128, 48),
        (256, 56, 256),
        (256, 256, 56),
    )
