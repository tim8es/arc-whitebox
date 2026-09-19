from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

from methods.e119_generic_boundary_flux import build_generic_boundary_flux

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "e119_target_free_crosscheck.py"
)
SPEC = importlib.util.spec_from_file_location("e119_target_free_crosscheck", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_frozen_weight_generation_is_exactly_deterministic() -> None:
    a = MOD.make_weights(119904, 4, 3)
    b = MOD.make_weights(119904, 4, 3)
    assert len(a) == len(b) == 3
    for x, y in zip(a, b):
        assert np.array_equal(x, y)


def test_candidate_and_observable_helper_static_scan_clean() -> None:
    for path in (
        "methods/e119_generic_boundary_flux.py",
        "methods/e118_output_flux_sketch.py",
    ):
        result = MOD.scan_source(path)
        assert result["pass"], result["findings"]


def test_independent_atom_selection_reproduces_candidate() -> None:
    weights = MOD.make_weights(119904, 4, 3)
    result = build_generic_boundary_flux(weights, budget=2**41)
    independent = MOD.independent_selection(result)
    assert independent["omitted_indices_equal"]
    assert independent["kept_indices_equal"]
    assert independent["omitted_abs_flux_sum_abs_error"] <= 1e-15
    assert independent["compressed_mean_abs_error"] <= 1e-15
    assert independent["certificate_abs_error"] <= 1e-15


def test_guarded_candidate_runs_without_reference_fit_or_file_io() -> None:
    weights = MOD.make_weights(119904, 4, 3)
    result = MOD.run_guarded(weights)
    assert result.finite
