#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

EXPECTED_DATASET_META_SHA = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAME_ORDER_SHA = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
R209_MEAN_ADJUSTED = 8.170397440117225e-9
R209_MEAN_FLOPS = 806303721965.0
MAX_ADJUSTED = 0.95 * R209_MEAN_ADJUSTED


def canonical_name_hash(names: list[str]) -> str:
    return hashlib.sha256(
        json.dumps(names, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-report", required=True)
    ap.add_argument("--r209", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    report = json.loads(Path(args.candidate_report).read_text())
    r209 = json.loads(Path(args.r209).read_text())
    rows = report["results"]["per_mlp"]
    base = r209["per_network"]

    names = [r["mlp_name"] for r in rows]
    base_names = [r["name"] for r in base]
    name_hash = canonical_name_hash(names)

    ds = report.get("run_config", {}).get("dataset", {})
    ds_text = json.dumps(ds, sort_keys=True)
    dataset_identity = (
        EXPECTED_DATASET_META_SHA in ds_text
        or ds.get("metadata_sha256") == EXPECTED_DATASET_META_SHA
        or ds.get("sha256") == EXPECTED_DATASET_META_SHA
    )
    identity = (
        len(rows) == 100
        and names == base_names
        and name_hash == EXPECTED_NAME_ORDER_SHA
        and dataset_identity
    )

    cand_scores = [float(r["adjusted_final_layer_score"]) for r in rows]
    base_scores = [float(r["official_adjusted_score"]) for r in base]
    diffs = [b - c for b, c in zip(base_scores, cand_scores)]
    mean_gain = sum(diffs) / len(diffs)
    if len(diffs) > 1:
        mean = mean_gain
        var = sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1)
        se = math.sqrt(var / len(diffs))
    else:
        se = float("nan")

    failures = int(report["results"]["n_failed_mlps"])
    mean_adjusted = float(report["results"]["adjusted_final_layer_score"])
    mean_flops = sum(float(r["flops_used"]) for r in rows) / len(rows)
    max_residual = max(float(r["residual_wall_time_s"]) for r in rows)
    improved = sum(c < b for c, b in zip(cand_scores, base_scores))

    gates = {
        "identity": identity,
        "zero_failures": failures == 0,
        "mean_adjusted_le_0p95_r209": mean_adjusted <= MAX_ADJUSTED,
        "improved_rows_ge_55": improved >= 55,
        "paired_gain_gt_2se": mean_gain > 2.0 * se,
        "mean_flops_le_r209": mean_flops <= R209_MEAN_FLOPS,
        "max_residual_lt_0p4": max_residual < 0.4,
    }
    out = {
        "schema": "arc.r252.public_gate.v1",
        "dataset_field": ds,
        "name_order_sha256": name_hash,
        "expected_name_order_sha256": EXPECTED_NAME_ORDER_SHA,
        "dataset_identity": dataset_identity,
        "row_count": len(rows),
        "mean_adjusted_score": mean_adjusted,
        "max_allowed_adjusted_score": MAX_ADJUSTED,
        "mean_flops": mean_flops,
        "improved_rows": improved,
        "paired_mean_gain": mean_gain,
        "paired_descriptive_se": se,
        "max_residual_wall_time_s": max_residual,
        "n_failed_mlps": failures,
        "gates": gates,
        "go": all(gates.values()),
        "rank_or_comparability_claim": False,
    }
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["go"] else 41


if __name__ == "__main__":
    raise SystemExit(main())
