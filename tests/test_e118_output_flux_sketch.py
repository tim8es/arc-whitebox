from __future__ import annotations

import math

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference
from methods.e118_output_flux_sketch import (
    output_observable,
    run_flux_sketch,
)


def _reference_atoms(ref, c: np.ndarray, cells: int) -> np.ndarray:
    h = 2.0 * math.pi / cells
    sin_mid = math.sin(0.5 * h)
    cos_mid = math.cos(0.5 * h)
    defects = np.zeros((cells, 2), dtype=np.float64)

    scalar_jumps = np.asarray(ref.boundary_jumps, dtype=np.float64) @ c
    for theta, jump in zip(ref.boundary_angles, scalar_jumps):
        theta = float(theta)
        if abs(theta) <= 1e-14:
            cell = cells - 1
            r = 0.0
        else:
            cell = int(math.floor(theta / h))
            cell = min(max(cell, 0), cells - 1)
            r = (cell + 1) * h - theta
        defects[cell, 0] += float(jump) * math.sin(r)
        defects[cell, 1] += float(jump) * math.cos(r)

    return sin_mid * defects[:, 0] + cos_mid * defects[:, 1]


def test_flux_sketch_matches_exact_boundary_projection_on_e114_fixture() -> None:
    weights = [
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64),
        np.array([[1.0, 1.0], [-2.0, 0.0]], dtype=np.float64),
        np.array([[2.0], [-1.0]], dtype=np.float64),
    ]
    cells = 128
    ref = build_exact_reference(weights)
    candidate = run_flux_sketch(weights, cells=cells)
    c = output_observable(1)
    atoms_ref = _reference_atoms(ref, c, cells)

    np.testing.assert_allclose(candidate.atoms, atoms_ref, atol=1e-12, rtol=0.0)
    assert candidate.flops["exact_reconciliation"]
    assert candidate.finite


def test_flux_sketch_deterministic() -> None:
    rng = np.random.Generator(np.random.PCG64(118118))
    weights = []
    w0 = rng.standard_normal((2, 4)).astype(np.float64)
    w0 *= math.sqrt(2.0 / 2.0)
    weights.append(w0)
    for _ in range(2):
        w = rng.standard_normal((4, 4)).astype(np.float64)
        w *= math.sqrt(2.0 / 4.0)
        weights.append(w)

    a = run_flux_sketch(weights, cells=64)
    b = run_flux_sketch(weights, cells=64)
    assert a.mean == b.mean
    assert np.array_equal(a.atoms, b.atoms)
    assert np.array_equal(a.state_residual, b.state_residual)
    assert a.flops == b.flops
