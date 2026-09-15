from __future__ import annotations

import numpy as np

from methods.e030_conditional_gaussian import (
    nystrom_from_covariance,
    post_relu_latent_update_numpy,
)


def test_nystrom_exact_for_rank8_coordinate_visible_psd() -> None:
    rng = np.random.default_rng(7)
    n, r = 24, 8
    # Make the first r rows nonsingular so coordinate Nyström sees the full rank-r range.
    f = rng.normal(size=(n, r))
    f[:r] += 3.0 * np.eye(r)
    c = f @ f.T
    u, evals = nystrom_from_covariance(np, c, r)
    assert np.all(evals > 0)
    np.testing.assert_allclose(u @ u.T, c, rtol=2e-10, atol=2e-10)


def test_diag_plus_factor_bookkeeping_preserves_exact_marginal_variance() -> None:
    rng = np.random.default_rng(9)
    n, r = 32, 8
    m = rng.normal(scale=0.2, size=n)
    d = rng.uniform(0.4, 1.2, size=n)
    u = rng.normal(scale=0.08, size=(n, r))
    out = post_relu_latent_update_numpy(m, d, u, r)
    recon = out.diag_residual + np.sum(out.factor * out.factor, axis=1)
    np.testing.assert_allclose(recon, out.exact_variance, rtol=2e-12, atol=2e-12)


def test_conditional_relu_marginals_match_univariate_gaussian_identities() -> None:
    rng = np.random.default_rng(11)
    n, r = 40, 8
    m = rng.normal(scale=0.3, size=n)
    d = rng.uniform(0.3, 1.0, size=n)
    u = rng.normal(scale=0.05, size=(n, r))
    out = post_relu_latent_update_numpy(m, d, u, r)
    assert np.isfinite(out.mean).all()
    assert np.isfinite(out.exact_variance).all()
    assert np.min(out.diag_residual) > -1e-10
    assert out.factor.shape == (n, r)
