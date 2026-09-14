import numpy as np

from methods.e017_quadratic_deim import (
    gappy_reconstruct,
    leverage_rows,
    quadratic_probe_basis,
    relative_rms,
)


def test_quadratic_probe_basis_and_rows_are_deterministic():
    rng = np.random.default_rng(7)
    q, _ = np.linalg.qr(rng.normal(size=(24, 4)))

    u1 = quadratic_probe_basis(q, basis_rank=8, seed=17017)
    u2 = quadratic_probe_basis(q, basis_rank=8, seed=17017)
    i1 = leverage_rows(u1, sample_rows=12)
    i2 = leverage_rows(u2, sample_rows=12)

    assert np.array_equal(u1, u2)
    assert np.array_equal(i1, i2)
    assert len(np.unique(i1)) == 12


def test_gappy_reconstruction_recovers_vectors_in_basis_span():
    rng = np.random.default_rng(11)
    q, _ = np.linalg.qr(rng.normal(size=(32, 3)))
    u = quadratic_probe_basis(q, basis_rank=6, seed=17018)
    rows = leverage_rows(u, sample_rows=10)

    coeff = rng.normal(size=(u.shape[1], 5))
    truth = u @ coeff
    recon, cond = gappy_reconstruct(u, rows, truth[rows])

    assert np.isfinite(cond)
    assert relative_rms(recon, truth) < 1e-10
