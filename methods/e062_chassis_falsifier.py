"""E062 scout falsifier: FULL carrier versus pilot dead/on/kink CHASSIS.

Both paths use identical deterministic Walsh/antithetic carrier points and exact
implementation aids.  CHASSIS differs only by the frozen suffix pilot routing and
physical removal of pilot-dead input columns from the following dense GEMM.
All MLP-dependent numerical work uses flopscope.numpy.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import SetupContext

from methods.e062_structure_fwht import (
    OFFICIAL_DEPTH,
    OFFICIAL_WIDTH,
    PILOT_LINES,
    RADIAL_RATIO_1024,
    antithetic_next_preact,
    signed_walsh_products,
)

N_LINES = 2 * OFFICIAL_WIDTH
N_ROWS = 2 * N_LINES
SUFFIX_LAYERS = 3


@dataclass(frozen=True)
class RunReceipt:
    prediction: object
    flops: int
    residual_s: float
    wall_s: float
    stats: dict[str, object]


def _radial_ratio(width: int) -> float:
    return RADIAL_RATIO_1024 if width == OFFICIAL_WIDTH else 1.0


def _pilot_parts(pre: fnp.ndarray, n_lines: int, pilot_lines: int):
    pilot = fnp.concatenate((pre[:pilot_lines], pre[n_lines:n_lines + pilot_lines]), axis=0)
    evaluation = fnp.concatenate((pre[pilot_lines:n_lines], pre[n_lines + pilot_lines:2 * n_lines]), axis=0)
    return pilot, evaluation


def _classify(pre: fnp.ndarray, n_lines: int, pilot_lines: int):
    pilot, evaluation = _pilot_parts(pre, n_lines, pilot_lines)
    zero = fnp.asarray(0.0, dtype=pre.dtype)
    pmax = fnp.max(pilot, axis=0)
    pmin = fnp.min(pilot, axis=0)
    dead = pmax <= zero
    on = pmin >= zero
    kink = fnp.logical_not(fnp.logical_or(dead, on))
    return dead, on, kink, evaluation


def _safety_stats(pre: fnp.ndarray, next_weight, n_lines: int, pilot_lines: int) -> dict[str, object]:
    dead, on, kink, evaluation = _classify(pre, n_lines, pilot_lines)
    zero = fnp.asarray(0.0, dtype=pre.dtype)
    vdead = fnp.logical_and(evaluation > zero, dead[None, :])
    von = fnp.logical_and(evaluation < zero, on[None, :])
    violation = fnp.logical_or(vdead, von)
    classified = fnp.logical_or(dead, on)

    if next_weight is None:
        mass = fnp.ones((pre.shape[1],), dtype=pre.dtype)
    else:
        w = fnp.asarray(next_weight, dtype=pre.dtype)
        mass = fnp.sum(w * w, axis=1)
    mean_mass = fnp.mean(mass)
    high = mass >= (fnp.asarray(2.0, dtype=pre.dtype) * mean_mass)
    high_classified = fnp.logical_and(high, classified)
    high_violation = fnp.logical_and(violation, high_classified[None, :])

    abs_pre = fnp.abs(evaluation)
    weights = abs_pre * mass[None, :]
    numerator = fnp.sum(weights * fnp.asarray(violation, dtype=pre.dtype))
    denominator = fnp.sum(weights * fnp.asarray(classified[None, :], dtype=pre.dtype))

    return {
        "dead": int(fnp.sum(fnp.asarray(dead, dtype=fnp.int32))),
        "on": int(fnp.sum(fnp.asarray(on, dtype=fnp.int32))),
        "kink": int(fnp.sum(fnp.asarray(kink, dtype=fnp.int32))),
        "violation_count": int(fnp.sum(fnp.asarray(violation, dtype=fnp.int32))),
        "high_violation_count": int(fnp.sum(fnp.asarray(high_violation, dtype=fnp.int32))),
        "weighted_violation_num": float(numerator),
        "weighted_violation_den": float(denominator),
    }


def _exact_zero_mask(activations: fnp.ndarray) -> fnp.ndarray:
    zero = fnp.asarray(0.0, dtype=activations.dtype)
    return fnp.max(fnp.abs(activations), axis=0) == zero


def _dense_step(activations: fnp.ndarray, weight: fnp.ndarray, remove_mask=None):
    exact_zero = _exact_zero_mask(activations)
    if remove_mask is None:
        removed = exact_zero
        pilot_removed = fnp.zeros(exact_zero.shape, dtype=fnp.bool_)
    else:
        pilot_removed = fnp.logical_and(remove_mask, fnp.logical_not(exact_zero))
        removed = fnp.logical_or(exact_zero, remove_mask)
    n_removed = int(fnp.sum(fnp.asarray(removed, dtype=fnp.int32)))
    n_pilot_removed = int(fnp.sum(fnp.asarray(pilot_removed, dtype=fnp.int32)))
    if n_removed:
        keep = fnp.logical_not(removed)
        pre = activations[:, keep] @ weight[keep, :]
    else:
        pre = activations @ weight
    return pre, n_removed, n_pilot_removed


def _apply_chassis(pre: fnp.ndarray, n_lines: int, pilot_lines: int):
    dead, on, kink, _ = _classify(pre, n_lines, pilot_lines)
    zero = fnp.asarray(0.0, dtype=pre.dtype)
    relu = fnp.maximum(pre, zero)
    out = fnp.where(dead[None, :], zero, fnp.where(on[None, :], pre, relu))
    return out, dead, (int(fnp.sum(fnp.asarray(dead, dtype=fnp.int32))), int(fnp.sum(fnp.asarray(on, dtype=fnp.int32))), int(fnp.sum(fnp.asarray(kink, dtype=fnp.int32))))


def carrier_predict(mlp, *, chassis: bool) -> tuple[object, dict[str, object]]:
    width = int(mlp.width)
    depth = int(mlp.depth)
    if width <= 0 or (width & (width - 1)):
        raise ValueError("E062 requires power-of-two width")
    if depth < 2:
        raise ValueError("E062 falsifier requires depth >= 2")

    n_lines = 2 * width
    pilot_lines = min(PILOT_LINES, width)
    zero = fnp.asarray(0.0, dtype=fnp.float32)
    scale = fnp.asarray(_radial_ratio(width) / float(2 * n_lines), dtype=fnp.float32)

    w0 = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
    z_pos = signed_walsh_products(w0)
    h_pos = fnp.maximum(z_pos, zero)
    h_neg = fnp.maximum(-z_pos, zero)
    activations = fnp.concatenate((h_pos, h_neg), axis=0)
    rows = [fnp.sum(activations, axis=0) * scale]

    exact_zero_removed = [0]
    pilot_dead_removed = [0]
    removed_gemm_flops = 0
    suffix_counts: list[tuple[int, int, int]] = []
    pending_dead = None

    w1 = fnp.asarray(mlp.weights[1], dtype=fnp.float32)
    w01 = w0 @ w1
    z_w1 = signed_walsh_products(w01)
    pos_pre, neg_pre = antithetic_next_preact(z_pos, h_pos, w1, z_w1)
    pre = fnp.concatenate((pos_pre, neg_pre), axis=0)
    if 1 >= depth - SUFFIX_LAYERS:
        if chassis:
            activations, pending_dead, counts = _apply_chassis(pre, n_lines, pilot_lines)
            suffix_counts.append(counts)
        else:
            activations = fnp.maximum(pre, zero)
    else:
        activations = fnp.maximum(pre, zero)
    rows.append(fnp.sum(activations, axis=0) * scale)
    exact_zero_removed.append(0)
    pilot_dead_removed.append(0)

    for layer in range(2, depth):
        weight = fnp.asarray(mlp.weights[layer], dtype=fnp.float32)
        pre, removed, pilot_removed = _dense_step(activations, weight, pending_dead if chassis else None)
        exact_zero_removed.append(removed - pilot_removed)
        pilot_dead_removed.append(pilot_removed)
        if pilot_removed:
            removed_gemm_flops += int(2 * activations.shape[0] * pilot_removed * weight.shape[1])
        pending_dead = None

        if layer >= depth - SUFFIX_LAYERS:
            if chassis:
                activations, pending_dead, counts = _apply_chassis(pre, n_lines, pilot_lines)
                suffix_counts.append(counts)
            else:
                activations = fnp.maximum(pre, zero)
        else:
            activations = fnp.maximum(pre, zero)
        rows.append(fnp.sum(activations, axis=0) * scale)

    return fnp.stack(rows, axis=0), {
        "n_lines": n_lines,
        "n_rows": 2 * n_lines,
        "pilot_lines": pilot_lines,
        "exact_zero_removed": tuple(exact_zero_removed),
        "pilot_dead_removed": tuple(pilot_dead_removed),
        "removed_gemm_flops": int(removed_gemm_flops),
        "suffix_counts": tuple(suffix_counts),
    }


def full_safety_audit(mlp) -> list[dict[str, object]]:
    """Run FULL carrier and return disjoint pilot/eval sign-safety telemetry.

    This intentionally recomputes the full carrier under the caller's metering
    context. It is diagnostic work, never credited as estimator savings.
    """
    width = int(mlp.width)
    depth = int(mlp.depth)
    n_lines = 2 * width
    pilot_lines = min(PILOT_LINES, width)
    zero = fnp.asarray(0.0, dtype=fnp.float32)
    w0 = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
    z_pos = signed_walsh_products(w0)
    h_pos = fnp.maximum(z_pos, zero)
    h_neg = fnp.maximum(-z_pos, zero)
    activations = fnp.concatenate((h_pos, h_neg), axis=0)

    w1 = fnp.asarray(mlp.weights[1], dtype=fnp.float32)
    w01 = w0 @ w1
    z_w1 = signed_walsh_products(w01)
    pos_pre, neg_pre = antithetic_next_preact(z_pos, h_pos, w1, z_w1)
    pre = fnp.concatenate((pos_pre, neg_pre), axis=0)
    audits: list[dict[str, object]] = []
    if 1 >= depth - SUFFIX_LAYERS:
        nxt = mlp.weights[2] if depth > 2 else None
        audits.append(_safety_stats(pre, nxt, n_lines, pilot_lines))
    activations = fnp.maximum(pre, zero)

    for layer in range(2, depth):
        w = fnp.asarray(mlp.weights[layer], dtype=fnp.float32)
        pre, _, _ = _dense_step(activations, w, None)
        if layer >= depth - SUFFIX_LAYERS:
            nxt = mlp.weights[layer + 1] if layer + 1 < depth else None
            audits.append(_safety_stats(pre, nxt, n_lines, pilot_lines))
        activations = fnp.maximum(pre, zero)
    return audits


def run_metered(mlp, *, chassis: bool, budget: int) -> RunReceipt:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=budget, quiet=True) as ctx:
        pred, stats = carrier_predict(mlp, chassis=chassis)
    return RunReceipt(pred, int(ctx.flops_used), float(ctx.residual_wall_time_s), time.perf_counter() - started, stats)


def setup_context() -> SetupContext:
    return SetupContext(width=OFFICIAL_WIDTH, depth=OFFICIAL_DEPTH, flop_budget=2**41, api_version="1", seed=62062)
