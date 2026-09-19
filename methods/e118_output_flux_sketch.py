"""E118 output-specific angular-cell boundary-flux sketch.

The candidate uses only scalar observable values and input gradients on a fixed
angular grid. It never enumerates activation regions or boundary roots.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


@dataclass(frozen=True)
class FluxSketchResult:
    mean: float
    atoms: np.ndarray
    state_residual: np.ndarray
    values: np.ndarray
    angular_derivatives: np.ndarray
    flops: dict
    finite: bool


def output_observable(width: int) -> np.ndarray:
    if width <= 0:
        raise ValueError("width must be positive")
    c = np.arange(1, width + 1, dtype=np.float64)
    c /= np.linalg.norm(c)
    return c


def fixed_angular_stencil(cells: int) -> tuple[np.ndarray, np.ndarray]:
    """Static compile-time q/tangent table; intentionally outside online billing."""
    if cells <= 0:
        raise ValueError("cells must be positive")
    theta = (2.0 * math.pi / cells) * np.arange(cells, dtype=np.float64)
    q = np.stack((np.cos(theta), np.sin(theta)), axis=1)
    tangent = np.stack((-np.sin(theta), np.cos(theta)), axis=1)
    return q, tangent


def run_flux_sketch(
    weights: Sequence[np.ndarray],
    *,
    cells: int = 1024,
    budget: int = 2**41,
) -> FluxSketchResult:
    if not weights:
        raise ValueError("weights must be non-empty")

    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2 or first.shape[0] != 2:
        raise ValueError("E118 requires two-dimensional input")
    width = int(first.shape[1])
    previous = 2
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError(f"weight {idx} has incompatible shape {w.shape}")
        previous = int(w.shape[1])
    if previous != width:
        raise ValueError("frozen E118 candidate requires equal hidden/final width")

    q_np, tangent_np = fixed_angular_stencil(cells)
    c_np = output_observable(width)

    hstep = 2.0 * math.pi / cells
    cos_h = float(math.cos(hstep))
    sin_h = float(math.sin(hstep))
    sin_mid = float(math.sin(0.5 * hstep))
    cos_mid = float(math.cos(0.5 * hstep))
    gaussian_factor = float(math.sqrt(math.pi / 2.0) / (2.0 * math.pi))

    with flops.BudgetContext(flop_budget=budget, quiet=True) as ctx:
        start = int(ctx.flops_used)
        h = fnp.asarray(q_np, dtype=fnp.float64)
        q_done = int(ctx.flops_used)

        gates = []
        billed_weights = []
        for raw in weights:
            w = fnp.asarray(np.asarray(raw, dtype=np.float64), dtype=fnp.float64)
            billed_weights.append(w)
            pre = fnp.matmul(h, w)
            gate = pre > fnp.float64(0.0)
            h = fnp.maximum(pre, fnp.float64(0.0))
            gates.append(gate)
        forward_done = int(ctx.flops_used)

        c = fnp.asarray(c_np, dtype=fnp.float64)
        values = fnp.sum(h * c[None, :], axis=1, dtype=fnp.float64)
        observable_done = int(ctx.flops_used)

        lam = fnp.ones((cells, width), dtype=fnp.float64) * c[None, :]
        for layer in range(len(weights) - 1, -1, -1):
            delta = lam * gates[layer]
            back = fnp.matmul(delta, fnp.swapaxes(billed_weights[layer], 0, 1))
            if layer == 0:
                grad = back
            else:
                lam = back
        reverse_done = int(ctx.flops_used)

        tangent = fnp.asarray(tangent_np, dtype=fnp.float64)
        angular_derivative = fnp.sum(
            grad * tangent, axis=1, dtype=fnp.float64
        )
        derivative_done = int(ctx.flops_used)

        values_next = fnp.concatenate((values[1:], values[:1]), axis=0)
        deriv_next = fnp.concatenate(
            (angular_derivative[1:], angular_derivative[:1]), axis=0
        )

        predicted_value = (
            fnp.float64(cos_h) * values
            + fnp.float64(sin_h) * angular_derivative
        )
        predicted_deriv = (
            -fnp.float64(sin_h) * values
            + fnp.float64(cos_h) * angular_derivative
        )
        d0 = values_next - predicted_value
        d1 = deriv_next - predicted_deriv

        atoms = (
            fnp.float64(sin_mid) * d0
            + fnp.float64(cos_mid) * d1
        )
        state_residual = (
            fnp.float64(cos_mid) * d0
            - fnp.float64(sin_mid) * d1
        )
        flux_sum = fnp.sum(atoms, dtype=fnp.float64)
        mean = fnp.float64(gaussian_factor) * flux_sum
        sketch_done = int(ctx.flops_used)
        total = int(ctx.flops_used)

    atoms_np = np.asarray(atoms, dtype=np.float64).copy()
    residual_np = np.asarray(state_residual, dtype=np.float64).copy()
    values_np = np.asarray(values, dtype=np.float64).copy()
    derivative_np = np.asarray(angular_derivative, dtype=np.float64).copy()
    mean_float = float(np.asarray(mean))

    categories = {
        "input_wrap": q_done - start,
        "forward": forward_done - q_done,
        "observable": observable_done - forward_done,
        "reverse": reverse_done - observable_done,
        "angular_derivative": derivative_done - reverse_done,
        "sketch": sketch_done - derivative_done,
    }
    reconciled = sum(categories.values())

    finite = bool(
        math.isfinite(mean_float)
        and np.isfinite(atoms_np).all()
        and np.isfinite(residual_np).all()
        and np.isfinite(values_np).all()
        and np.isfinite(derivative_np).all()
    )

    return FluxSketchResult(
        mean=mean_float,
        atoms=atoms_np,
        state_residual=residual_np,
        values=values_np,
        angular_derivatives=derivative_np,
        flops={
            **categories,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization_vs_2pow41": total / float(2**41),
            "static_stencil_generation_billed": False,
        },
        finite=finite,
    )
