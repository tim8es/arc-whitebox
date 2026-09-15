"""E021: exact elision of the identically-zero source-0 V18 feedback transport."""

from __future__ import annotations

import flopscope.numpy as fnp


def transport_feedback_without_source0(WDb, Zf_st):
    """Transport live V18 feedback rows while preserving dead source 0 as exact zero.

    Exact V25 source 0 has F1=F2=R1T=R2T=0 at birth. Its Zf row therefore remains
    identically zero under every linear transport. E021 keeps the aligned source-0 slot
    but excludes it from the dense matmul; all source rows 1+ use the unchanged V25
    `fnp.matmul(WDb, ...)` arithmetic.
    """
    if Zf_st is None:
        return None
    if Zf_st.shape[0] == 0:
        return Zf_st
    dead0 = fnp.zeros_like(Zf_st[:1])
    if Zf_st.shape[0] == 1:
        return dead0
    live = fnp.matmul(WDb, Zf_st[1:])
    return fnp.concatenate([dead0, live], axis=0)
