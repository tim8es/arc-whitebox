from __future__ import annotations

from fractions import Fraction

import numpy as np

from methods.e116_output_specific_transport import (
    CERTIFICATE_POINT_INDICES,
    canonical_json,
    exact_certificate,
    fraction_determinant,
    make_weights,
    run_frozen_payload,
)


def test_fraction_determinant_exact():
    m = [
        [Fraction(1), Fraction(2), Fraction(3)],
        [Fraction(0), Fraction(4), Fraction(5)],
        [Fraction(1), Fraction(0), Fraction(6)],
    ]
    assert fraction_determinant(m) == Fraction(22)


def test_frozen_weight_shapes_and_ranks():
    weights = make_weights()
    assert len(weights) == 4
    assert all(w.shape == (8, 8) for w in weights)
    assert [np.linalg.matrix_rank(w) for w in weights] == [8, 8, 8, 8]


def test_exact_certificate_is_full_rank_and_interior():
    cert = exact_certificate(make_weights())
    assert cert["selected_point_indices"] == list(CERTIFICATE_POINT_INDICES)
    assert cert["all_selected_exact_preactivations_nonzero"]
    assert cert["float_masks_match_exact"]
    assert cert["exact_determinant"]["nonzero"]
    assert cert["float_gradient_rank_tol_1e_12"] == 8


def test_frozen_payload_is_deterministic_and_terminal():
    a = run_frozen_payload()
    b = run_frozen_payload()
    assert canonical_json(a) == canonical_json(b)
    assert all(a["gates"].values())
    assert a["decision"] == (
        "TERMINAL_STRUCTURAL_NO_GO_FIXED_LINEAR_OUTPUT_TRANSPORT"
    )
