from __future__ import annotations

import numpy as np


def generic_residual_without_y(
    z_st: np.ndarray, l_st: np.ndarray, rres: int
) -> tuple[np.ndarray, np.ndarray]:
    """Drop the F68 transported-y column whose static right factor is identically zero."""
    if z_st.ndim != 3 or l_st.ndim != 3 or z_st.shape != l_st.shape:
        raise ValueError("z_st and l_st must be same-shape rank-3 arrays")
    if z_st.shape[2] != rres + 2:
        raise ValueError("expected residual rank plus u/y columns")
    if not np.array_equal(l_st[:, :, rres + 1], np.zeros_like(l_st[:, :, rres + 1])):
        raise ValueError("transported-y right factor must be exactly zero")
    return z_st[:, :, : rres + 1], l_st[:, :, : rres + 1]


def transport_source0_dead_feed_columns(
    w: np.ndarray, z_st: np.ndarray, rres: int
) -> np.ndarray:
    """Dense transport with source-0 F68 u/y columns preserved as exact zeros.

    This NumPy helper is a focused algebraic reference. The production diagnostic patches
    the pinned flopscope V25 source with the same split transport so billed FLOPs are measured.
    """
    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise ValueError("w must be square")
    if z_st.ndim != 3 or z_st.shape[1] != w.shape[0] or z_st.shape[2] != rres + 2:
        raise ValueError("bad z_st shape")
    if not np.array_equal(z_st[0, :, rres:], np.zeros_like(z_st[0, :, rres:])):
        raise ValueError("source-0 u/y feed columns must be exactly zero")

    main = np.einsum("ij,kjq->kiq", w, z_st[:, :, :rres])
    if z_st.shape[0] == 1:
        tail = np.zeros((1, w.shape[0], 2), dtype=z_st.dtype)
    else:
        active = np.einsum("ij,kjq->kiq", w, z_st[1:, :, rres:])
        tail = np.concatenate(
            [np.zeros((1, w.shape[0], 2), dtype=z_st.dtype), active], axis=0
        )
    return np.concatenate([main, tail], axis=2)
