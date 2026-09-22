#!/usr/bin/env python3
"""R231 deterministic descriptive audit for R209 V25 mini-100.

This script performs arithmetic only. It does not import or run an estimator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742"
EXPECTED_NAME_ORDER_SHA256 = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
EXPECTED_N = 100
EXPECTED_BUDGET = 2**41
TARGET_SCORE = 2.1e-9


def qlinear(xs: list[float], q: float) -> float:
    """NumPy-default-style linear quantile for a sorted 1-D sample."""
    if not 0.0 <= q <= 1.0:
        raise ValueError(q)
    if q == 0.0:
        return xs[0]
    if q == 1.0:
        return xs[-1]
    h = (len(xs) - 1) * q
    lo = int(h)
    hi = min(lo + 1, len(xs) - 1)
    f = h - lo
    return xs[lo] * (1.0 - f) + xs[hi] * f


def gini_nonnegative(xs: list[float]) -> float:
    ys = sorted(xs)
    total = sum(ys)
    n = len(ys)
    weighted = sum((i + 1) * x for i, x in enumerate(ys))
    return 2.0 * weighted / (n * total) - (n + 1.0) / n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json", type=Path)
    ap.add_argument("--csv", type=Path, default=None)
    args = ap.parse_args()

    raw = args.input_json.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"input SHA256 mismatch: {digest}")

    data = json.loads(raw)
    rows = data["per_network"]
    if len(rows) != EXPECTED_N:
        raise SystemExit(f"expected {EXPECTED_N} rows, got {len(rows)}")

    names = [r["name"] for r in rows]
    ids = [str(r["network_id"]) for r in rows]
    target_shas = [r["target_sha256"] for r in rows]
    if len(set(names)) != EXPECTED_N or len(set(ids)) != EXPECTED_N:
        raise SystemExit("name/network_id uniqueness gate failed")
    if any(len(x) != 64 for x in target_shas) or len(set(target_shas)) != EXPECTED_N:
        raise SystemExit("target_sha256 gate failed")
    name_order_sha = hashlib.sha256(
        json.dumps(names, separators=(",", ":")).encode()
    ).hexdigest()
    if name_order_sha != EXPECTED_NAME_ORDER_SHA256:
        raise SystemExit(f"name-order SHA256 mismatch: {name_order_sha}")
    if data["panel"]["shape"] != [16, 1024]:
        raise SystemExit("shape gate failed")
    if {int(r["budget_flops"]) for r in rows} != {EXPECTED_BUDGET}:
        raise SystemExit("budget gate failed")
    if any(r["status"] != "ok" or r.get("failure_reasons") for r in rows):
        raise SystemExit("status/failure gate failed")

    mses = [float(r["final_mse"]) for r in rows]
    total = sum(mses)
    mean = total / EXPECTED_N
    ordered = sorted(mses)

    max_formula_error = 0.0
    factors = []
    for r in rows:
        factor = max(0.1, float(r["measured_flops"]) / float(r["budget_flops"]))
        factors.append(factor)
        recomputed = float(r["final_mse"]) * factor
        max_formula_error = max(
            max_formula_error,
            abs(recomputed - float(r["official_adjusted_score"])),
        )
    if max_formula_error != 0.0:
        raise SystemExit(f"stored score mismatch: max abs error={max_formula_error}")

    ranked = sorted(
        enumerate(rows),
        key=lambda p: float(p[1]["final_mse"]),
        reverse=True,
    )
    top_shares = {
        str(k): sum(float(r["final_mse"]) for _, r in ranked[:k]) / total
        for k in (1, 5, 10, 20)
    }

    loo = []
    cumulative = 0.0
    table_rows = []
    for rank, (original_index, r) in enumerate(ranked, start=1):
        mse = float(r["final_mse"])
        cumulative += mse
        loo_mean = (total - mse) / (EXPECTED_N - 1)
        loo_delta = loo_mean - mean
        loo.append((abs(loo_delta), loo_delta, loo_mean, r))
        table_rows.append(
            {
                "tail_rank": rank,
                "original_index": original_index,
                "name": r["name"],
                "network_id": r["network_id"],
                "target_sha256": r["target_sha256"],
                "final_mse": format(mse, ".17g"),
                "share_total_raw_mse": format(mse / total, ".17g"),
                "cumulative_share_total_raw_mse": format(cumulative / total, ".17g"),
                "leave_one_out_mean_raw_mse": format(loo_mean, ".17g"),
                "leave_one_out_delta_from_full_mean": format(loo_delta, ".17g"),
                "measured_flops": r["measured_flops"],
                "budget_flops": r["budget_flops"],
                "compute_factor": format(factors[original_index], ".17g"),
            }
        )

    loo.sort(reverse=True, key=lambda x: x[0])
    floor_score = 0.1 * mean
    target_raw_at_floor = TARGET_SCORE / 0.1
    reduction_abs = mean - target_raw_at_floor
    reduction_frac = reduction_abs / mean

    summary = {
        "input_sha256": digest,
        "name_order_sha256": name_order_sha,
        "n": EXPECTED_N,
        "shape": data["panel"]["shape"],
        "budget_flops": EXPECTED_BUDGET,
        "unique_measured_flops": sorted({int(r["measured_flops"]) for r in rows}),
        "mean_raw_mse": mean,
        "median_raw_mse": qlinear(ordered, 0.5),
        "quantiles_linear": {
            str(q): qlinear(ordered, q)
            for q in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0)
        },
        "top_share_total_raw_mse": top_shares,
        "gini_raw_mse": gini_nonnegative(mses),
        "leave_one_out": {
            "mean_min": min((total - x) / (EXPECTED_N - 1) for x in mses),
            "mean_max": max((total - x) / (EXPECTED_N - 1) for x in mses),
            "max_abs_delta_from_full_mean": loo[0][0],
            "most_influential_name": loo[0][3]["name"],
            "most_influential_network_id": loo[0][3]["network_id"],
        },
        "score": {
            "mean_observed_adjusted_score": sum(
                float(r["official_adjusted_score"]) for r in rows
            ) / EXPECTED_N,
            "compute_factor_min": min(factors),
            "compute_factor_max": max(factors),
            "score_floor_at_fixed_observed_raw_mse": floor_score,
            "numerical_target_score": TARGET_SCORE,
            "required_mean_raw_mse_at_0.1_floor": target_raw_at_floor,
            "absolute_mean_raw_mse_reduction_needed": reduction_abs,
            "relative_mean_raw_mse_reduction_needed": reduction_frac,
        },
    }

    if args.csv is not None:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(table_rows[0]))
            writer.writeheader()
            writer.writerows(table_rows)

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
