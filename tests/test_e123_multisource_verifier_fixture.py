from __future__ import annotations

import numpy as np

from methods.e123_multisource_verifier_fixture import (
    build_adversarial_12d_fixture,
    dense_vs_latent_probe_error,
    fixture_replay_equal,
)


def test_adversarial_fixture_is_dense_and_exactly_replayable() -> None:
    a = build_adversarial_12d_fixture()
    b = build_adversarial_12d_fixture()

    assert fixture_replay_equal(a, b)
    assert a.exact_mean.shape == (12,)
    assert len(a.dense_weights) == 4
    assert all(w.shape == (12, 12) for w in a.dense_weights)
    assert np.count_nonzero(np.abs(a.dense_weights[0]) > 1e-14) > 120
    assert np.isfinite(a.exact_mean).all()


def test_mixing_is_orthogonal_and_dense_forward_matches_latent_blocks() -> None:
    fixture = build_adversarial_12d_fixture()
    gram = fixture.mixing_q.T @ fixture.mixing_q
    assert float(np.max(np.abs(gram - np.eye(12)))) <= 2e-12
    assert dense_vs_latent_probe_error(fixture) <= 1e-12
