import numpy as np

from methods.fourth_moment_antithetic import FourthMomentAntitheticEstimator
from methods.whitened_antithetic import WhitenedAntitheticEstimator


class TinyMLP:
    width = 4
    depth = 2
    seed = 12345
    weights = (
        np.asarray(
            [
                [0.2, -0.1, 0.3, 0.4],
                [0.1, 0.5, -0.2, 0.3],
                [-0.4, 0.2, 0.1, 0.2],
                [0.3, -0.3, 0.2, 0.1],
            ],
            dtype=np.float32,
        ),
        np.asarray(
            [
                [0.2, 0.1, -0.2, 0.3],
                [-0.1, 0.4, 0.2, 0.1],
                [0.3, -0.2, 0.5, -0.1],
                [0.1, 0.2, 0.1, 0.4],
            ],
            dtype=np.float32,
        ),
    )


def test_same_mlp_seed_produces_same_prediction() -> None:
    est = FourthMomentAntitheticEstimator(target_utilization=0.05, min_samples=32)
    mlp = TinyMLP()
    a = np.asarray(est.predict(mlp, 2**24))
    b = np.asarray(est.predict(mlp, 2**24))
    np.testing.assert_array_equal(a, b)


def test_prediction_has_layer_by_width_shape() -> None:
    est = FourthMomentAntitheticEstimator(target_utilization=0.05, min_samples=32)
    out = np.asarray(est.predict(TinyMLP(), 2**24))
    assert out.shape == (TinyMLP.depth, TinyMLP.width)


def test_competition_shape_uses_fewer_samples_to_pay_for_radial_correction() -> None:
    budget = 2**41
    width = 1024
    depth = 16
    radial = FourthMomentAntitheticEstimator()
    frozen = WhitenedAntitheticEstimator()

    assert radial.sample_count(budget, width, depth) == 4810
    assert radial.sample_count(budget, width, depth) < frozen.sample_count(
        budget, width, depth
    )
