"""Exact ReLU mean-backbone plus certified kink-remainder helpers."""

from __future__ import annotations

import numpy as np


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(np.asarray(x, dtype=np.float64), 0.0)


def certified_kink_remainder(
    z: np.ndarray, anchor: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return exact affine-remainder and its certified support mask.

    The anchor is broadcast across sample rows. The derivative convention is
    s(m)=1[m>0].
    """
    zz = np.asarray(z, dtype=np.float64)
    m = np.asarray(anchor, dtype=np.float64)
    if zz.ndim != 2 or m.shape != (zz.shape[1],):
        raise ValueError("expected z=(N,width), anchor=(width,)")

    gate = (m > 0.0).astype(np.float64)
    remainder = relu(zz) - relu(m)[None, :] - (zz - m[None, :]) * gate[None, :]
    support = ((m[None, :] > 0.0) & (zz < 0.0)) | (
        (m[None, :] <= 0.0) & (zz > 0.0)
    )
    return remainder, support


def explicit_kink_remainder(z: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    zz = np.asarray(z, dtype=np.float64)
    m = np.asarray(anchor, dtype=np.float64)
    out = np.zeros_like(zz)
    pos_anchor = m > 0.0
    if np.any(pos_anchor):
        cols = np.where(pos_anchor)[0]
        block = zz[:, cols]
        out[:, cols] = np.where(block < 0.0, -block, 0.0)
    nonpos_anchor = ~pos_anchor
    if np.any(nonpos_anchor):
        cols = np.where(nonpos_anchor)[0]
        block = zz[:, cols]
        out[:, cols] = np.where(block > 0.0, block, 0.0)
    return out


def layer_hybrid_identity(
    h_prev: np.ndarray, weight: np.ndarray
) -> tuple[np.ndarray, dict[str, object]]:
    """Propagate one ReLU layer and verify the exact finite-cloud mean identity."""
    h0 = np.asarray(h_prev, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)
    if h0.ndim != 2 or w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise ValueError("bad shapes")
    if h0.shape[1] != w.shape[1]:
        raise ValueError("width mismatch")

    z = h0 @ w.T
    h = relu(z)

    previous_mean = np.mean(h0, axis=0, dtype=np.float64)
    anchor = previous_mean @ w.T
    z_mean = np.mean(z, axis=0, dtype=np.float64)

    backbone = relu(anchor)
    remainder, support = certified_kink_remainder(z, anchor)
    explicit = explicit_kink_remainder(z, anchor)
    gate = (anchor > 0.0).astype(np.float64)

    pointwise_reconstructed = (
        backbone[None, :]
        + (z - anchor[None, :]) * gate[None, :]
        + remainder
    )
    direct_mean = np.mean(h, axis=0, dtype=np.float64)
    hybrid_mean = backbone + np.mean(remainder, axis=0, dtype=np.float64)

    offsupport = np.where(support, 0.0, remainder)
    support_count = int(np.count_nonzero(support))
    total = int(support.size)

    h_energy = float(np.sum(h * h))
    rem_energy = float(np.sum(remainder * remainder))
    stats = {
        "anchor_vs_direct_preactivation_mean_max_abs": float(
            np.max(np.abs(anchor - z_mean))
        ),
        "pointwise_identity_max_abs": float(
            np.max(np.abs(pointwise_reconstructed - h))
        ),
        "mean_reconstruction_max_abs": float(
            np.max(np.abs(hybrid_mean - direct_mean))
        ),
        "piecewise_remainder_max_abs": float(
            np.max(np.abs(remainder - explicit))
        ),
        "offsupport_remainder_max_abs": float(np.max(np.abs(offsupport))),
        "remainder_min": float(np.min(remainder)),
        "support_count": support_count,
        "total_entries": total,
        "support_fraction": support_count / total,
        "remainder_energy_fraction_vs_activation": (
            rem_energy / h_energy if h_energy > 0.0 else 0.0
        ),
        "direct_mean_l2": float(np.linalg.norm(direct_mean)),
        "backbone_l2": float(np.linalg.norm(backbone)),
        "remainder_mean_l2": float(np.linalg.norm(np.mean(remainder, axis=0))),
    }
    return h, stats
