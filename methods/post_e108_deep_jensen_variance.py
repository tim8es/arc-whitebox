"""Post-E108 target-free final-layer Jensen residual variance helpers."""

from __future__ import annotations

import flopscope.numpy as fnp


def _two_block_means(values, width: int):
    """Return means for the two Haar blocks, including each block's antipodes."""
    n = int(width)
    x = fnp.asarray(values, dtype=fnp.float32)
    if x.shape != (4 * n, n):
        raise ValueError(f"expected shape {(4 * n, n)}, got {x.shape}")

    p0 = fnp.mean(x[:n], axis=0, dtype=fnp.float64)
    p1 = fnp.mean(x[n : 2 * n], axis=0, dtype=fnp.float64)
    m0 = fnp.mean(x[2 * n : 3 * n], axis=0, dtype=fnp.float64)
    m1 = fnp.mean(x[3 * n : 4 * n], axis=0, dtype=fnp.float64)

    b0 = fnp.multiply(fnp.add(p0, m0), 0.5)
    b1 = fnp.multiply(fnp.add(p1, m1), 0.5)
    return b0, b1


def final_layer_jensen_decomposition_billed(
    penultimate, final_activation, last_weight, width: int
):
    """Exact final-ReLU block decomposition Y_b = G_b + J_b.

    G_b is ReLU(mean(H_{L-1,b}) @ W_L.T), and J_b is the realized Jensen
    residual. All quantities are target-free and use only realized network
    state plus frozen weights.
    """
    n = int(width)
    hprev = fnp.asarray(penultimate, dtype=fnp.float32)
    hfinal = fnp.asarray(final_activation, dtype=fnp.float32)
    w = fnp.asarray(last_weight, dtype=fnp.float32)
    if hprev.shape != (4 * n, n) or hfinal.shape != (4 * n, n):
        raise ValueError("unexpected trajectory-state shape")
    if w.shape != (n, n):
        raise ValueError("last_weight must be square width x width")

    hbar0, hbar1 = _two_block_means(hprev, n)
    y0, y1 = _two_block_means(hfinal, n)

    g0 = fnp.matmul(hbar0, fnp.swapaxes(w, 0, 1))
    g1 = fnp.matmul(hbar1, fnp.swapaxes(w, 0, 1))
    g0 = fnp.maximum(g0, fnp.float64(0.0))
    g1 = fnp.maximum(g1, fnp.float64(0.0))

    j0 = fnp.subtract(y0, g0)
    j1 = fnp.subtract(y1, g1)

    dy = fnp.subtract(y0, y1)
    dg = fnp.subtract(g0, g1)
    dj = fnp.subtract(j0, j1)

    r_y = fnp.multiply(
        fnp.mean(fnp.multiply(dy, dy), dtype=fnp.float64), 0.25
    )
    r_g = fnp.multiply(
        fnp.mean(fnp.multiply(dg, dg), dtype=fnp.float64), 0.25
    )
    r_j = fnp.multiply(
        fnp.mean(fnp.multiply(dj, dj), dtype=fnp.float64), 0.25
    )
    cross = fnp.multiply(
        fnp.mean(fnp.multiply(dg, dj), dtype=fnp.float64), 0.5
    )

    return {
        "y0": y0,
        "y1": y1,
        "g0": g0,
        "g1": g1,
        "j0": j0,
        "j1": j1,
        "r_y": r_y,
        "r_g": r_g,
        "r_j": r_j,
        "cross": cross,
    }
