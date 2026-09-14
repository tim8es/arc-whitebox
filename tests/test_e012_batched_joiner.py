from __future__ import annotations

import numpy as np

from methods.e012_batched_joiner import (
    candidate_scratch_bytes,
    joiner_batched,
    joiner_separate,
)


def _small_inputs():
    rng = np.random.default_rng(20260914)
    ap = rng.standard_normal((2, 16, 16), dtype=np.float32)
    weights = rng.standard_normal((2, 16, 1), dtype=np.float32)
    omega = rng.standard_normal((16, 6), dtype=np.float32)
    return ap, weights, omega


def test_pair_batched_matches_separate_path() -> None:
    ap, weights, omega = _small_inputs()
    separate = np.asarray(joiner_separate(ap, weights, omega))
    batched = np.asarray(joiner_batched(ap, weights, omega))
    rel = np.linalg.norm(batched - separate) / np.linalg.norm(separate)
    assert rel <= 5e-7


def test_candidate_scratch_is_only_two_batched_nr_buffers() -> None:
    expected = 2 * 2 * 1024 * 384 * 4
    assert candidate_scratch_bytes(n=1024, rank=384, dtype_bytes=4) == expected
    assert candidate_scratch_bytes(n=1024, rank=384, dtype_bytes=4) <= 8 * 1024**2
