#!/usr/bin/env python3
"""Independent skeptical E114 reviewer on an adversarial depth-4 network."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TOL = 1e-12
C = 2.0 / 5.0


def relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def add(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] + b[0], a[1] + b[1])


def scale(s: float, a: tuple[float, float]) -> tuple[float, float]:
    return (s * a[0], s * a[1])


def lincomb(
    weights: tuple[float, ...],
    coeffs: tuple[tuple[float, float], ...],
) -> tuple[float, float]:
    out = (0.0, 0.0)
    for w, c in zip(weights, coeffs, strict=True):
        out = add(out, scale(w, c))
    return out


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def direct_network(theta: float) -> float:
    x = math.cos(theta)
    y = math.sin(theta)

    h0 = relu(x)
    h1 = relu(-x)
    h2 = relu(y)
    h3 = relu(-y)

    a = h0 + 2.0 * h1
    b = 3.0 * h2 + 5.0 * h3

    p = relu(a - b)
    n = relu(b - a)
    s = relu(a + b)

    q = relu(p + n - C * s)
    r = relu(-p - n + C * s)
    return relu(q + r)


def sector_coeff(theta: float) -> tuple[float, float]:
    qvec = (math.cos(theta), math.sin(theta))

    l1_pre = ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0))
    l1 = tuple(c if dot(c, qvec) > 0.0 else (0.0, 0.0) for c in l1_pre)

    a = lincomb((1.0, 2.0, 0.0, 0.0), l1)
    b = lincomb((0.0, 0.0, 3.0, 5.0), l1)

    l2_pre = (
        add(a, scale(-1.0, b)),
        add(b, scale(-1.0, a)),
        add(a, b),
    )
    l2 = tuple(c if dot(c, qvec) > 0.0 else (0.0, 0.0) for c in l2_pre)

    l3_pre = (
        lincomb((1.0, 1.0, -C), l2),
        lincomb((-1.0, -1.0, C), l2),
    )
    l3 = tuple(c if dot(c, qvec) > 0.0 else (0.0, 0.0) for c in l3_pre)

    out = lincomb((1.0, 1.0), l3)
    return out if dot(out, qvec) > 0.0 else (0.0, 0.0)


def boundaries() -> list[dict[str, object]]:
    rho_low = (1.0 - C) / (1.0 + C)   # 3/7
    rho_high = (1.0 + C) / (1.0 - C)  # 7/3

    # (quadrant index, sign(x), sign(y), A coefficient, B coefficient)
    quadrants = (
        (0, 1.0, 1.0, 1.0, 3.0),
        (1, -1.0, 1.0, 2.0, 3.0),
        (2, -1.0, -1.0, 2.0, 5.0),
        (3, 1.0, -1.0, 1.0, 5.0),
    )

    out: list[dict[str, object]] = []
    for k, sx, sy, a, b in quadrants:
        out.append(
            {
                "theta": k * math.pi / 2.0,
                "origin_layer": 1,
                "kind": "axis",
                "quadrant": k + 1,
            }
        )
        specs = (
            (rho_low * a / b, 3, "outer_A_dominant"),
            (a / b, 2, "inner_A_eq_B"),
            (rho_high * a / b, 3, "outer_B_dominant"),
        )
        for ratio_y_over_x, layer, kind in specs:
            theta = math.atan2(sy * ratio_y_over_x, sx) % (2.0 * math.pi)
            out.append(
                {
                    "theta": theta,
                    "origin_layer": layer,
                    "kind": kind,
                    "quadrant": k + 1,
                }
            )

    out.sort(key=lambda x: float(x["theta"]))
    return out


def sector_integral(
    left: float,
    right: float,
    coeff: tuple[float, float],
) -> float:
    cx, cy = coeff
    return (
        cx * (math.sin(right) - math.sin(left))
        + cy * (-math.cos(right) + math.cos(left))
    )


def distinct_count(values: list[float], tol: float) -> int:
    chosen: list[float] = []
    for v in values:
        if not any(abs(v - u) <= tol for u in chosen):
            chosen.append(v)
    return len(chosen)


def run_once() -> dict[str, object]:
    bs = boundaries()
    if len(bs) != 16:
        raise RuntimeError(f"expected 16 boundaries, got {len(bs)}")

    angles = [float(x["theta"]) for x in bs]
    if any((b - a) <= 1e-10 for a, b in zip(angles, angles[1:], strict=True)):
        raise RuntimeError("non-distinct boundary angles")

    sectors: list[dict[str, object]] = []
    direct_max_abs = 0.0
    angular_integral = 0.0

    for i, left in enumerate(angles):
        right = angles[(i + 1) % len(angles)]
        if i == len(angles) - 1:
            right += 2.0 * math.pi
        mid = 0.5 * (left + right)
        coeff = sector_coeff(mid)
        qvec = (math.cos(mid), math.sin(mid))
        via_coeff = dot(coeff, qvec)
        direct = direct_network(mid)
        direct_max_abs = max(direct_max_abs, abs(via_coeff - direct))
        integral = sector_integral(left, right, coeff)
        angular_integral += integral
        sectors.append(
            {
                "left": left,
                "right": right,
                "mid": mid % (2.0 * math.pi),
                "coeff": [coeff[0], coeff[1]],
                "direct": direct,
                "via_coeff": via_coeff,
                "integral": integral,
            }
        )

    jumps: list[float] = []
    detailed_boundaries: list[dict[str, object]] = []
    normals: list[tuple[float, float]] = []

    for i, item in enumerate(bs):
        theta = float(item["theta"])
        left_coeff = tuple(float(x) for x in sectors[(i - 1) % len(sectors)]["coeff"])
        right_coeff = tuple(float(x) for x in sectors[i]["coeff"])
        tangent = (-math.sin(theta), math.cos(theta))
        jump = dot(
            (right_coeff[0] - left_coeff[0], right_coeff[1] - left_coeff[1]),
            tangent,
        )
        normal = (-math.sin(theta), math.cos(theta))
        jumps.append(jump)
        normals.append(normal)
        detailed_boundaries.append(
            {
                **item,
                "jump": jump,
                "abs_jump": abs(jump),
                "interface_normal": [normal[0], normal[1]],
            }
        )

    jump_sum = sum(jumps)
    nonzero_count = sum(abs(x) > TOL for x in jumps)
    jump_distinct = distinct_count(jumps, TOL)

    # All normals are in R^2. Rank is exactly 2 iff at least one pair is non-collinear.
    max_abs_det = 0.0
    for i, a in enumerate(normals):
        for b in normals[i + 1 :]:
            max_abs_det = max(max_abs_det, abs(a[0] * b[1] - a[1] * b[0]))
    normal_rank = 2 if max_abs_det > TOL else 1

    layer_counts = {
        "layer1": sum(int(x["origin_layer"]) == 1 for x in bs),
        "layer2": sum(int(x["origin_layer"]) == 2 for x in bs),
        "layer3": sum(int(x["origin_layer"]) == 3 for x in bs),
    }

    identity_abs_error = abs(jump_sum - angular_integral)
    gaussian_mean_from_flux = math.sqrt(math.pi / 2.0) * jump_sum / (2.0 * math.pi)
    gaussian_mean_from_sectors = (
        math.sqrt(math.pi / 2.0) * angular_integral / (2.0 * math.pi)
    )

    gates = {
        "sixteen_predicted_boundaries": len(bs) == 16,
        "origin_counts_4_4_8": layer_counts == {"layer1": 4, "layer2": 4, "layer3": 8},
        "direct_matches_sector_linearization": direct_max_abs <= TOL,
        "all_sixteen_output_jumps_nonzero": nonzero_count == 16,
        "at_least_twelve_distinct_jump_values": jump_distinct >= 12,
        "output_boundary_retention_fraction_one": nonzero_count / len(bs) == 1.0,
        "boundary_normal_rank_exactly_two": normal_rank == 2,
        "flux_identity_matches_sector_integral": identity_abs_error <= TOL,
        "gaussian_mean_paths_match": (
            abs(gaussian_mean_from_flux - gaussian_mean_from_sectors) <= TOL
        ),
    }

    if gates["flux_identity_matches_sector_integral"] is False:
        decision = "E114_EXACTNESS_FALSIFIED"
    elif all(gates.values()):
        decision = (
            "E114_EXACTNESS_SURVIVES_NAIVE_OUTPUT_THINNING_AND_LOW_RANK_NORMAL_"
            "COMPRESSION_FALSIFIED"
        )
    else:
        decision = "REVIEW_GATE_FAILURE"

    return {
        "schema": "arc.whitebox.e114.skeptical_boundary_retention.v1",
        "network": {
            "input_dimension": 2,
            "depth": 4,
            "max_width": 4,
            "zero_bias": True,
            "A_weights_on_xpos_xneg": [1.0, 2.0],
            "B_weights_on_ypos_yneg": [3.0, 5.0],
            "outer_c": C,
        },
        "boundary_count": len(bs),
        "layer_origin_counts": layer_counts,
        "nonzero_output_flux_atoms": nonzero_count,
        "output_boundary_retention_fraction": nonzero_count / len(bs),
        "distinct_jump_values_tol_1e_12": jump_distinct,
        "boundary_normal_rank": normal_rank,
        "boundary_normal_max_pair_det": max_abs_det,
        "direct_sector_max_abs": direct_max_abs,
        "jump_sum": jump_sum,
        "analytic_sector_integral": angular_integral,
        "identity_abs_error": identity_abs_error,
        "gaussian_mean_from_flux": gaussian_mean_from_flux,
        "gaussian_mean_from_sectors": gaussian_mean_from_sectors,
        "boundaries": detailed_boundaries,
        "sectors": sectors,
        "gates": gates,
        "decision": decision,
        "interpretation": {
            "exactness": "survives" if identity_abs_error <= TOL else "falsified",
            "compression_scope": (
                "scalar-output pruning and rank-2 normal span do not reduce this "
                "constructed network below 16 nonzero output flux atoms"
            ),
            "not_proved": (
                "no claim that every possible symbolic or aggregate compression is impossible"
            ),
        },
        "scope": {
            "target_free": True,
            "monte_carlo": False,
            "numerical_quadrature": False,
            "public": False,
            "benchmark": False,
            "scorer": False,
            "holdout_full": False,
            "canonical_mutation": False,
            "ledger_mutation": False,
        },
    }


def canonical(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    first = run_once()
    second = run_once()
    deterministic = canonical(first) == canonical(second)
    first["deterministic_replay_exact"] = deterministic
    first["gates"]["deterministic_replay_exact"] = deterministic

    expected = (
        "E114_EXACTNESS_SURVIVES_NAIVE_OUTPUT_THINNING_AND_LOW_RANK_NORMAL_"
        "COMPRESSION_FALSIFIED"
    )
    if first["decision"] != expected or not deterministic:
        print("E114_SKEPTICAL_REVIEW=" + canonical(first), flush=True)
        return 2

    text = json.dumps(first, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print("E114_SKEPTICAL_REVIEW=" + canonical(first), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
