import flopscope.numpy as fnp
import numpy as np

from methods.radial_fourth_moment import RadialFourthMomentEstimator


def _fixture() -> np.ndarray:
    return np.asarray(
        [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [2.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )


def test_radial_spread_preserves_gram() -> None:
    x = _fixture()
    y = np.asarray(
        RadialFourthMomentEstimator._spread_pairs(fnp.asarray(x), strength=0.75)
    )
    np.testing.assert_allclose(y.T @ y, x.T @ x, rtol=1e-6, atol=1e-6)


def test_full_strength_increases_radial_fourth_statistic() -> None:
    x = _fixture()
    y = np.asarray(
        RadialFourthMomentEstimator._spread_pairs(fnp.asarray(x), strength=1.0)
    )
    before = np.sum(np.sum(x * x, axis=1) ** 2)
    after = np.sum(np.sum(y * y, axis=1) ** 2)
    assert after > before


def test_zero_strength_is_identity() -> None:
    x = _fixture()
    y = np.asarray(RadialFourthMomentEstimator._spread_pairs(fnp.asarray(x), strength=0.0))
    np.testing.assert_array_equal(y, x)
