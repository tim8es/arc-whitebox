from __future__ import annotations

import numpy as np
import pytest

from methods.e114_exact_angular_reference import dense_he_weights
from methods.e119_exact_reference_compare import compare_generic_boundary_to_exact


def _assert_exact_match(weights: list[np.ndarray]) -> None:
    result = compare_generic_boundary_to_exact(weights)

    assert result.finite
    assert result.partition_complete
    assert result.partition_ordered
    assert result.max_partition_gap <= 1e-11
    assert result.max_partition_overlap <= 1e-11
    assert (
        result.layer_region_counts_generic
        == result.layer_region_counts_reference
    )
    assert result.final_region_count_generic == result.final_region_count_reference
    assert result.max_sector_lo_error <= 1e-12
    assert result.max_sector_hi_error <= 1e-12
    assert result.max_sector_coeff_abs_error <= 1e-12
    assert result.max_reference_direct_eval_abs_error <= 1e-12
    assert result.max_generic_direct_eval_abs_error <= 1e-12
    assert result.max_boundary_angle_wrapped_error <= 1e-10
    assert result.max_scalar_jump_abs_error <= 1e-10
    assert result.generic_vs_reference_mean_abs_error <= 1e-10
    assert result.reference_flux_vs_sector_mean_abs_error <= 1e-10


@pytest.mark.parametrize(
    ("seed", "widths"),
    [
        (119501, (3,)),
        (119502, (5, 2)),
        (119503, (4, 6, 3)),
        (119504, (8, 5, 7, 2)),
        (119505, (3, 8, 4, 6)),
    ],
)
def test_arbitrary_dense_he_width_chains_match_exact_reference(
    seed: int,
    widths: tuple[int, ...],
) -> None:
    weights = dense_he_weights(seed, widths=widths)
    _assert_exact_match(weights)


def test_hand_specified_dense_rectangular_chain_matches_exact_reference() -> None:
    weights = [
        np.array(
            [
                [1.0, -2.0, 0.5],
                [0.75, 1.25, -1.5],
            ],
            dtype=np.float64,
        ),
        np.array(
            [
                [1.0, -0.5],
                [-1.25, 2.0],
                [0.8, 0.6],
            ],
            dtype=np.float64,
        ),
        np.array(
            [
                [1.2],
                [-0.7],
            ],
            dtype=np.float64,
        ),
    ]
    assert all(np.count_nonzero(w) == w.size for w in weights)
    _assert_exact_match(weights)


def test_reference_comparator_is_deterministic() -> None:
    weights = dense_he_weights(119506, widths=(7, 4, 8, 3))
    a = compare_generic_boundary_to_exact(weights)
    b = compare_generic_boundary_to_exact(weights)
    assert a == b
