"""Import the pinned E174 receipt without evaluating or modifying an estimator."""
import json
from pathlib import Path
from arc_control import ROOT, encoded, git, score_record

COMMIT = "c2dde864c51d1fe54f176dd9dbd2e84bc78c10a7"
PATH = "research/E174_E173_INDEPENDENT_VERIFIER_RECEIPT.json"


def main():
    receipt = json.loads(git("show", f"{COMMIT}:{PATH}"))
    networks = receipt["seed_separation"]["mlps"]
    metrics = receipt["independent_numeric_recomputation"]["per_mlp"]
    by_name = {n["name"]: n for n in networks}
    url = f"https://github.com/tim8es/arc-whitebox/blob/{COMMIT}/{PATH}"
    for arm in ("parent", "ago"):
        record = {
            "id": f"E173-{arm}", "hypothesis_id": "AGO", "experiment_id": "E173",
            "attempt_id": "35621103274", "parent_id": "E173-parent" if arm == "ago" else None,
            "code_commit": receipt["execution_evidence"]["valid_scientific_run"]["head_sha"],
            "source_receipt_commit": COMMIT, "receipt_url": url,
            "evidence_level": "IMPORTED_VERIFIER_RECEIPT",
            "verification_note": "Receipt read from pinned Git object; arrays not rerun by importer.",
            "panel": {"dataset": receipt["seed_separation"]["dataset"],
                "revision": "v2-phase2; target content identified per-network by SHA256",
                "split": "mini:first-5", "stage": "development", "count": 5,
                "shape": [16, 1024], "dtype": "float32", "evaluator": "whestbench 0.16.1",
                "meter": "flopscope 0.12.1"},
            "per_network": [],
        }
        for row in metrics:
            network = by_name[row["name"]]
            record["per_network"].append({"network_id": network["input_mlp_seed_exact"],
                "name": row["name"], "target_sha256": network["target_raw_sha256"],
                "final_mse": row[f"{arm}_mse"],
                "measured_flops": receipt["cost"][f"official_metered_{arm}_flops_per_mlp"],
                "budget_flops": receipt["cost"]["budget_flops"], "status": "ok"})
        if arm == "ago":
            record["analytic_flops_upper"] = receipt["cost"]["deployed_analytic_all_in"]
        score_record(record)
        target = ROOT / "research/results" / f"{record['id']}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded(record), encoding="utf-8")
    print("Imported E173-parent and E173-ago from pinned E174; no scientific run.")


if __name__ == "__main__":
    main()
