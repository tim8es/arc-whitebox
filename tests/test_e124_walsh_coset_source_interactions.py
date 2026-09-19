from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "e124_walsh_coset_source_interactions.py"
SPEC = importlib.util.spec_from_file_location("e124", SCRIPT)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_walsh_rows_cancel_first_and_distinct_pair_characters():
    labels = np.array([1, 2, 3, 1], dtype=np.int64)
    h = MOD.walsh_rows(labels)
    np.testing.assert_array_equal(np.mean(h, axis=0), np.zeros(4))
    for i in range(4):
        for j in range(i + 1, 4):
            v = float(np.mean(h[:, i] * h[:, j]))
            if labels[i] == labels[j]:
                assert v == 1.0
            else:
                assert v == 0.0


def test_exact_conditional_coset_partition():
    law = MOD.conditional_walsh_law()
    assert law["distinct_coset_count"] == 4
    assert law["full_sign_vs_coset_mean_max_abs"] <= 1e-13
    assert law["degree1_max_abs"] <= 1e-15
    assert law["degree2_different_label_max_abs"] <= 1e-15
    assert law["degree2_same_label_max_abs_from_one"] <= 1e-15
    assert law["dense_coset_output_spread"] > 0.0


def test_overlapping_network_exact_reference_dimensions():
    weights, subnets = MOD.assemble_overlapping_network()
    assert weights[0].shape == (4, 8)
    assert all(w.shape == (8, 8) for w in weights[1:])
    mean, counts = MOD.exact_overlapping_mean(subnets)
    assert mean.shape == (8,)
    assert np.isfinite(mean).all()
    assert len(counts) == 4
    assert all(c > 0 for c in counts)


def test_production_flop_proof_is_frozen_and_under_cap():
    p = MOD.production_flop_proof()
    assert p["all_in_upper"] == 275297735680
    assert p["exact_formula_match"]
    assert p["utilization"] <= 0.13
    assert p["slack_flops"] > 0.0
