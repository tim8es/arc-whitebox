from __future__ import annotations

import numpy as np


BASE_RANK = 16
FINAL_RANK = 8


def select_feedback_rank(
    zf: np.ndarray,
    r1: np.ndarray,
    r2: np.ndarray,
    *,
    is_last: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Select the frozen E024 feedback coordinates without mutating inputs."""
    if not is_last:
        return zf, r1, r2, BASE_RANK

    if zf.shape[-1] != 2 * BASE_RANK:
        raise ValueError(f"expected {2 * BASE_RANK} feedback columns, got {zf.shape[-1]}")
    if r1.shape[-1] != BASE_RANK or r2.shape[-1] != BASE_RANK:
        raise ValueError("expected rank-16 static feedback factors")

    zf_use = np.concatenate(
        [zf[..., :FINAL_RANK], zf[..., BASE_RANK : BASE_RANK + FINAL_RANK]],
        axis=-1,
    )
    return zf_use, r1[..., :FINAL_RANK], r2[..., :FINAL_RANK], FINAL_RANK
