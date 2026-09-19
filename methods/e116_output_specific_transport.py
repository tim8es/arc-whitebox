"""E116 exact output-specific linear transport obstruction helpers."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math

import numpy as np


WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 116116
CERTIFICATE_POINT_INDICES = (0, 1, 2, 3, 4, 5, 6, 8)


def make_weights(
    *, seed: int = WEIGHT_SEED, width: int = WIDTH, depth: int = DEPTH
) -> list[np.ndarray]:
    if width <= 0 or depth <= 0:
        raise ValueError("width/depth must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    scale = math.sqrt(2.0 / float(width))
    return [
        np.asarray(rng.standard_normal((width, width)), dtype=np.float64) * scale
        for _ in range(depth)
    ]


def signed_basis_points(width: int = WIDTH) -> list[np.ndarray]:
    points: list[np.ndarray] = []
    for i in range(int(width)):
        e = np.zeros(width, dtype=np.float64)
        e[i] = 1.0
        points.append(e)
        points.append(-e)
    return points


def _fraction_matrix(a: np.ndarray) -> list[list[Fraction]]:
    return [
        [Fraction.from_float(float(a[i, j])) for j in range(a.shape[1])]
        for i in range(a.shape[0])
    ]


def _exact_forward_masks(
    weights: list[list[list[Fraction]]], point_index: int
) -> tuple[list[list[bool]], list[list[Fraction]]]:
    n = len(weights[0])
    coord = int(point_index) // 2
    sign = 1 if int(point_index) % 2 == 0 else -1
    h = [Fraction(0) for _ in range(n)]
    h[coord] = Fraction(sign)

    masks: list[list[bool]] = []
    preactivations: list[list[Fraction]] = []
    for w in weights:
        z = [
            sum((h[i] * w[i][j] for i in range(n)), Fraction(0))
            for j in range(n)
        ]
        if any(v == 0 for v in z):
            raise ArithmeticError("selected point lies on an activation boundary")
        mask = [v > 0 for v in z]
        masks.append(mask)
        preactivations.append(z)
        h = [v if active else Fraction(0) for v, active in zip(z, mask)]
    return masks, preactivations


def _exact_gradient(
    weights: list[list[list[Fraction]]], masks: list[list[bool]]
) -> list[Fraction]:
    n = len(weights[0])
    # F(h_L) = sum_j (j+1) h_L,j.
    v = [Fraction(j + 1) for j in range(n)]
    for layer in reversed(range(len(weights))):
        v = [v[j] if masks[layer][j] else Fraction(0) for j in range(n)]
        w = weights[layer]
        v = [
            sum((w[i][j] * v[j] for j in range(n)), Fraction(0))
            for i in range(n)
        ]
    return v


def fraction_determinant(matrix: list[list[Fraction]]) -> Fraction:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be nonempty and square")
    a = [row[:] for row in matrix]
    det = Fraction(1)
    sign = 1
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign *= -1
        p = a[k][k]
        det *= p
        for i in range(k + 1, n):
            factor = a[i][k] / p
            for j in range(k + 1, n):
                a[i][j] -= factor * a[k][j]
            a[i][k] = Fraction(0)
    return det if sign > 0 else -det


def float_forward_gradient(
    weights: list[np.ndarray], point: np.ndarray
) -> tuple[list[list[bool]], np.ndarray, float]:
    n = point.shape[0]
    h = np.asarray(point, dtype=np.float64).copy()
    jac = np.eye(n, dtype=np.float64)
    min_abs = math.inf
    masks: list[list[bool]] = []
    for w in weights:
        z = h @ w
        min_abs = min(min_abs, float(np.min(np.abs(z))))
        mask = z > 0.0
        masks.append([bool(v) for v in mask])
        jac = (jac @ w) * mask
        h = np.maximum(z, 0.0)
    c = np.arange(1.0, n + 1.0, dtype=np.float64)
    return masks, jac @ c, min_abs


def exact_certificate(
    weights: list[np.ndarray],
    *,
    selected_indices: tuple[int, ...] = CERTIFICATE_POINT_INDICES,
) -> dict:
    n = weights[0].shape[0]
    if len(selected_indices) != n:
        raise ValueError("need exactly width certificate points")
    wf = [_fraction_matrix(w) for w in weights]
    points = signed_basis_points(n)

    exact_rows: list[list[Fraction]] = []
    mask_strings: list[list[str]] = []
    float_rows = []
    exact_min_abs = None
    float_min_abs = math.inf
    masks_match = True

    for idx in selected_indices:
        exact_masks, preacts = _exact_forward_masks(wf, idx)
        grad = _exact_gradient(wf, exact_masks)
        exact_rows.append(grad)
        mask_strings.append(
            ["".join("1" if v else "0" for v in layer) for layer in exact_masks]
        )

        for layer in preacts:
            for value in layer:
                av = abs(value)
                if exact_min_abs is None or av < exact_min_abs:
                    exact_min_abs = av

        float_masks, float_grad, point_min_abs = float_forward_gradient(
            weights, points[idx]
        )
        float_rows.append(float_grad)
        float_min_abs = min(float_min_abs, point_min_abs)
        masks_match = masks_match and float_masks == exact_masks

    det = fraction_determinant(exact_rows)
    det_text = f"{det.numerator}/{det.denominator}"
    det_sha256 = hashlib.sha256(det_text.encode("ascii")).hexdigest()
    float_matrix = np.stack(float_rows, axis=0)
    singular_values = np.linalg.svd(float_matrix, compute_uv=False)

    return {
        "selected_point_indices": list(selected_indices),
        "exact_masks": mask_strings,
        "all_selected_exact_preactivations_nonzero": exact_min_abs is not None,
        "exact_min_abs_preactivation_float": float(exact_min_abs),
        "float_min_abs_preactivation": float_min_abs,
        "float_masks_match_exact": bool(masks_match),
        "exact_determinant": {
            "numerator": str(det.numerator),
            "denominator": str(det.denominator),
            "sha256": det_sha256,
            "nonzero": det != 0,
            "sign": 1 if det > 0 else (-1 if det < 0 else 0),
            "numerator_bits": abs(det.numerator).bit_length(),
            "denominator_bits": det.denominator.bit_length(),
            "float_value": float(det),
        },
        "float_gradient_singular_values": singular_values.tolist(),
        "float_gradient_rank_tol_1e_12": int(
            np.linalg.matrix_rank(float_matrix, tol=1e-12)
        ),
    }


def run_frozen_payload() -> dict:
    weights = make_weights()
    cert = exact_certificate(weights)
    ranks = [int(np.linalg.matrix_rank(w)) for w in weights]
    all_weights_nonzero = all(bool(np.all(w != 0.0)) for w in weights)

    gates = {
        "all_weight_matrices_rank8": ranks == [WIDTH] * DEPTH,
        "all_256_weights_nonzero": all_weights_nonzero,
        "all_selected_exact_preactivations_nonzero": cert[
            "all_selected_exact_preactivations_nonzero"
        ],
        "float_masks_match_exact": cert["float_masks_match_exact"],
        "exact_gradient_determinant_nonzero": cert["exact_determinant"]["nonzero"],
        "exact_gradient_span_rank8": cert["exact_determinant"]["nonzero"],
        "no_external_targets": True,
    }

    decision = (
        "TERMINAL_STRUCTURAL_NO_GO_FIXED_LINEAR_OUTPUT_TRANSPORT"
        if all(gates.values())
        else "INSTRUMENT_NO_GO"
    )
    return {
        "schema": "arc.whitebox.e116.output_specific_gradient_span.v1",
        "experiment": "E116",
        "idempotency_key": "ARC-E116-OUTPUT-SPECIFIC-GRADIENT-SPAN-20260919",
        "network": {
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "zero_bias": True,
            "weight_law": "iid Gaussian PCG64 then He scale sqrt(2/8)=1/2",
            "weight_ranks": ranks,
        },
        "observable": "F(x)=sum_{j=1}^8 j*h_4,j(x)",
        "theorem": (
            "If F(x)=g(U^T x), every differentiable-region gradient is "
            "orthogonal to ker(U^T), hence lies in col(U). A nonzero 8x8 "
            "gradient determinant forces rank(U)>=8."
        ),
        "certificate": cert,
        "gates": gates,
        "decision": decision,
        "scientific_go": False,
        "production_shape_authorized": False,
        "scope": {
            "small_exact_synthetic_only": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rerun": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
