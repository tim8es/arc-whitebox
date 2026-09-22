#!/usr/bin/env python3
"""R229: reproducible read-only paired decomposition of R209 V25/V29 mini-100.

Standard library only. Does not run an estimator. It verifies exact input SHA256,
row alignment, stored official scoring, and writes a row-level CSV plus summary JSON.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

EXPECTED = {
    "v25": "f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742",
    "v29": "1c22e2a951b4a3f7647421fe50090d7172c29a05b7f64426055d042d0af20751",
}

PANEL_FIELDS = ("count", "dataset", "dtype", "evaluator", "meter", "revision", "shape", "split", "stage")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(xs):
    return sum(xs) / len(xs)


def quantile_linear(xs, p):
    ys = sorted(xs)
    pos = (len(ys) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ys[lo]
    return ys[lo] * (hi - pos) + ys[hi] * (pos - lo)


def stats(xs):
    out = {
        "n": len(xs),
        "mean": mean(xs),
        "min": min(xs),
        "q25": quantile_linear(xs, 0.25),
        "median": quantile_linear(xs, 0.50),
        "q75": quantile_linear(xs, 0.75),
        "max": max(xs),
    }
    if len(xs) > 1:
        out["sd"] = statistics.stdev(xs)
        out["se"] = out["sd"] / math.sqrt(len(xs))
    else:
        out["sd"] = None
        out["se"] = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v25", type=Path, default=Path("research/results/R209-v25-mini100.json"))
    ap.add_argument("--v29", type=Path, default=Path("research/results/R209-v29-mini100.json"))
    ap.add_argument("--csv", type=Path, default=Path("research/r229/R229_PAIRED_ROWS.csv"))
    ap.add_argument("--summary", type=Path, default=Path("research/r229/R229_SUMMARY.json"))
    args = ap.parse_args()

    got25, got29 = sha256(args.v25), sha256(args.v29)
    assert got25 == EXPECTED["v25"], (got25, EXPECTED["v25"])
    assert got29 == EXPECTED["v29"], (got29, EXPECTED["v29"])

    v25 = json.loads(args.v25.read_text(encoding="utf-8"))
    v29 = json.loads(args.v29.read_text(encoding="utf-8"))
    a, b = v25["per_network"], v29["per_network"]
    assert len(a) == len(b) == 100
    for key in PANEL_FIELDS:
        assert v25["panel"][key] == v29["panel"][key], key
    assert v25["source"]["raw_prediction_tensors_archived"] is False
    assert v29["source"]["raw_prediction_tensors_archived"] is False

    paired = []
    for i, (x, y) in enumerate(zip(a, b)):
        assert x["name"] == y["name"], i
        assert x["network_id"] == y["network_id"], i
        assert x["target_sha256"] == y["target_sha256"], i
        assert x["budget_flops"] == y["budget_flops"], i

        if x["status"] == "ok":
            expected = x["final_mse"] * max(0.1, x["measured_flops"] / x["budget_flops"])
            assert expected == x["official_adjusted_score"], (i, "v25")
        if y["status"] == "ok":
            expected = y["final_mse"] * max(0.1, y["measured_flops"] / y["budget_flops"])
            assert expected == y["official_adjusted_score"], (i, "v29")
        else:
            # Failure rows preserve the evaluator's official penalty, not the success cost factor.
            assert y["official_adjusted_score"] == y["final_mse"], (i, "v29-failure-penalty")

        paired.append({
            "row": i,
            "name": x["name"],
            "network_id": x["network_id"],
            "target_sha256": x["target_sha256"],
            "v25_status": x["status"],
            "v29_status": y["status"],
            "v25_final_mse": x["final_mse"],
            "v29_final_mse": y["final_mse"],
            "delta_mse_v29_minus_v25": y["final_mse"] - x["final_mse"],
            "v25_official_adjusted_score": x["official_adjusted_score"],
            "v29_official_adjusted_score": y["official_adjusted_score"],
            "delta_score_v29_minus_v25": y["official_adjusted_score"] - x["official_adjusted_score"],
            "budget_flops": x["budget_flops"],
            "v25_measured_flops": x["measured_flops"],
            "v29_measured_flops": y["measured_flops"],
            "v25_residual_wall_time_s": x["residual_wall_time_s"],
            "v29_residual_wall_time_s": y["residual_wall_time_s"],
            "v25_wall_time_s": x["wall_time_s"],
            "v29_wall_time_s": y["wall_time_s"],
            "v29_failure_reasons": ";".join(y.get("failure_reasons", [])),
        })

    common = [r for r in paired if r["v25_status"] == "ok" and r["v29_status"] == "ok"]
    failed = [r for r in paired if r["v29_status"] != "ok"]
    assert len(common) == 43 and len(failed) == 57
    assert all(r["v29_failure_reasons"] == "residual_wall_time_exhausted" for r in failed)

    mean25 = mean([r["v25_official_adjusted_score"] for r in paired])
    mean29 = mean([r["v29_official_adjusted_score"] for r in paired])
    total_gap = mean29 - mean25
    fail_contrib = sum(r["delta_score_v29_minus_v25"] for r in failed) / len(paired)
    common_contrib = sum(r["delta_score_v29_minus_v25"] for r in common) / len(paired)
    assert math.isclose(total_gap, fail_contrib + common_contrib, rel_tol=0.0, abs_tol=5e-16)

    summary = {
        "input_sha256": {"v25": got25, "v29": got29},
        "panel_n": 100,
        "common_success_n": len(common),
        "v29_failed_n": len(failed),
        "aggregate_scores": {
            "v25_mean": mean25,
            "v29_mean": mean29,
            "gap_v29_minus_v25": total_gap,
            "ratio_v29_over_v25": mean29 / mean25,
        },
        "exact_gap_partition": {
            "v29_failure_rows_contribution_to_panel_mean_gap": fail_contrib,
            "common_success_rows_contribution_to_panel_mean_gap": common_contrib,
        },
        "common_success": {
            "paired_mse_delta_v29_minus_v25": stats([r["delta_mse_v29_minus_v25"] for r in common]),
            "paired_score_delta_v29_minus_v25": stats([r["delta_score_v29_minus_v25"] for r in common]),
            "v29_lower_mse_count": sum(r["delta_mse_v29_minus_v25"] < 0 for r in common),
            "v29_lower_score_count": sum(r["delta_score_v29_minus_v25"] < 0 for r in common),
        },
        "runtime": {
            "v29_common_success_residual_wall_time_s": stats([r["v29_residual_wall_time_s"] for r in common]),
            "v29_failed_residual_wall_time_s": stats([r["v29_residual_wall_time_s"] for r in failed]),
            "all_common_success_residual_lt_0_4": all(r["v29_residual_wall_time_s"] < 0.4 for r in common),
            "all_failed_residual_ge_0_4": all(r["v29_residual_wall_time_s"] >= 0.4 for r in failed),
        },
        "limits": {
            "raw_prediction_tensors_archived": False,
            "size_association": "not estimable: fixed panel shape [16,1024], constant budget, no per-network size field",
            "uncertainty": "paired SE is descriptive across the 43 observed common-success networks; not a held-out significance test",
        },
    }

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(paired[0]))
        w.writeheader()
        w.writerows(paired)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
