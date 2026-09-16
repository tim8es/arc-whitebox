"""E062: deterministic structure-aware Walsh/antithetic forward estimator.

All predict-time numerical work stays on the flopscope surface.  The official
Phase-2 schedule is frozen in research/E062_PROTOCOL.md: two signed Walsh
bases (2048 line representatives), antipodal closure, a reused 256-line pilot,
and dead/on/kink routing only in the final three layers.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

OFFICIAL_WIDTH = 1024
OFFICIAL_DEPTH = 16
OFFICIAL_LINES = 2048
PILOT_LINES = 256
RADIAL_RATIO_1024 = 0.9997558892134077  # E||N(0,I_1024)|| / sqrt(1024)


def fwht_rows(matrix: fnp.ndarray) -> fnp.ndarray:
    """Unnormalised Walsh-Hadamard transform along axis 0.

    The input row count must be a power of two.  Each butterfly add/subtract is
    a flopscope.numpy operation and therefore billed.
    """
    n = int(matrix.shape[0])
    if n <= 0 or (n & (n - 1)):
        raise ValueError("FWHT row count must be a positive power of two")
    x = matrix
    span = 1
    trailing = tuple(int(v) for v in matrix.shape[1:])
    while span < n:
        y = fnp.reshape(x, (-1, 2, span) + trailing)
        a = y[:, 0]
        b = y[:, 1]
        x = fnp.reshape(fnp.stack((a + b, a - b), axis=1), (n,) + trailing)
        span *= 2
    return x


def _parity_signs(width: int) -> fnp.ndarray:
    # Target-independent discrete carrier metadata only.  No MLP-dependent work
    # is performed outside flopscope.
    vals = [1.0 if (i.bit_count() & 1) == 0 else -1.0 for i in range(width)]
    return fnp.asarray(vals, dtype=fnp.float32)


def signed_walsh_products(weight: fnp.ndarray) -> fnp.ndarray:
    """Return the two frozen signed Walsh blocks times ``weight``."""
    width = int(weight.shape[0])
    block0 = fwht_rows(weight)
    signs = _parity_signs(width)
    block1 = fwht_rows(signs[:, None] * weight)
    return fnp.concatenate((block0, block1), axis=0)


def compact_exact_zero_columns(
    activations: fnp.ndarray, weight: fnp.ndarray
) -> tuple[fnp.ndarray, fnp.ndarray, int]:
    """Support-exact zero-column compaction for the next dense product."""
    zero = fnp.max(fnp.abs(activations), axis=0) == fnp.asarray(0.0, dtype=activations.dtype)
    skipped = int(fnp.sum(fnp.asarray(zero, dtype=fnp.int32)))
    if skipped == 0:
        return activations, weight, 0
    keep = fnp.logical_not(zero)
    return activations[:, keep], weight[keep, :], skipped


def antithetic_next_preact(
    z_positive: fnp.ndarray,
    h_positive: fnp.ndarray,
    weight: fnp.ndarray,
    z_times_weight: fnp.ndarray,
) -> tuple[fnp.ndarray, fnp.ndarray]:
    """Exact one-step fold from ReLU(-z)=ReLU(z)-z."""
    positive = h_positive @ weight
    negative = positive - z_times_weight
    return positive, negative


class Estimator(BaseEstimator):
    """Deterministic E062 estimator."""

    def __init__(self) -> None:
        self.last_stats: dict[str, object] = {}

    def setup(self, ctx: SetupContext) -> None:
        self.last_stats = {"setup_width": int(ctx.width), "setup_depth": int(ctx.depth)}

    @staticmethod
    def _radial_ratio(width: int) -> float:
        if width == OFFICIAL_WIDTH:
            return RADIAL_RATIO_1024
        # Small-shape tests only.  Official prediction never takes this path.
        # The test path intentionally omits a radial correction because identity,
        # finite, and determinism tests do not use it as an accuracy estimator.
        return 1.0

    def _suffix_relu(
        self,
        pre: fnp.ndarray,
        n_lines: int,
        pilot_lines: int,
    ) -> tuple[fnp.ndarray, tuple[int, int, int]]:
        pilot = fnp.concatenate(
            (pre[:pilot_lines], pre[n_lines : n_lines + pilot_lines]), axis=0
        )
        pmax = fnp.max(pilot, axis=0)
        pmin = fnp.min(pilot, axis=0)
        zero = fnp.asarray(0.0, dtype=pre.dtype)
        dead = pmax <= zero
        on = pmin >= zero
        kink = fnp.logical_not(fnp.logical_or(dead, on))
        out = fnp.where(dead[None, :], zero, fnp.where(on[None, :], pre, fnp.maximum(pre, zero)))
        counts = (
            int(fnp.sum(fnp.asarray(dead, dtype=fnp.int32))),
            int(fnp.sum(fnp.asarray(on, dtype=fnp.int32))),
            int(fnp.sum(fnp.asarray(kink, dtype=fnp.int32))),
        )
        return out, counts

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        width = int(mlp.width)
        depth = int(mlp.depth)
        if width <= 0 or (width & (width - 1)):
            raise ValueError("E062 requires power-of-two width")
        if depth <= 0:
            raise ValueError("E062 requires positive depth")

        n_lines = 2 * width
        pilot_lines = min(PILOT_LINES, width)
        zero = fnp.asarray(0.0, dtype=fnp.float32)
        scale = fnp.asarray(self._radial_ratio(width) / float(2 * n_lines), dtype=fnp.float32)

        w0 = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
        z_pos = signed_walsh_products(w0)
        h_pos = fnp.maximum(z_pos, zero)
        h_neg = fnp.maximum(-z_pos, zero)
        activations = fnp.concatenate((h_pos, h_neg), axis=0)
        rows = [fnp.sum(activations, axis=0) * scale]

        skipped_by_layer: list[int] = [0]
        suffix_counts: list[tuple[int, int, int]] = []

        if depth >= 2:
            w1 = fnp.asarray(mlp.weights[1], dtype=fnp.float32)
            # Exact antithetic fold: z_pos @ W1 is evaluated by first forming
            # W0@W1 then applying the same signed Walsh carrier.
            w01 = w0 @ w1
            z_w1 = signed_walsh_products(w01)
            pos_pre, neg_pre = antithetic_next_preact(z_pos, h_pos, w1, z_w1)
            pre = fnp.concatenate((pos_pre, neg_pre), axis=0)
            if 1 >= depth - 3:
                activations, counts = self._suffix_relu(pre, n_lines, pilot_lines)
                suffix_counts.append(counts)
            else:
                activations = fnp.maximum(pre, zero)
            rows.append(fnp.sum(activations, axis=0) * scale)
            skipped_by_layer.append(0)

        for layer in range(2, depth):
            weight = fnp.asarray(mlp.weights[layer], dtype=fnp.float32)
            compact_a, compact_w, skipped = compact_exact_zero_columns(activations, weight)
            pre = compact_a @ compact_w
            if layer >= depth - 3:
                activations, counts = self._suffix_relu(pre, n_lines, pilot_lines)
                suffix_counts.append(counts)
            else:
                activations = fnp.maximum(pre, zero)
            rows.append(fnp.sum(activations, axis=0) * scale)
            skipped_by_layer.append(skipped)

        self.last_stats.update(
            {
                "n_lines": n_lines,
                "n_rows": 2 * n_lines,
                "pilot_lines": pilot_lines,
                "zero_skipped_by_layer": tuple(skipped_by_layer),
                "suffix_dead_on_kink": tuple(suffix_counts),
            }
        )
        return fnp.stack(rows, axis=0)
