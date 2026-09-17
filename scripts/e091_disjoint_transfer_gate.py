#!/usr/bin/env python3
"""E091 disjoint-transfer falsifier.

Evaluates the frozen ridge transfer gate q_B > v_B / 2 from an immutable,
root-disjoint evidence package.  If the package is absent, proves that the
current repository state does not contain admissible production-transfer data
instead of silently reusing the legacy local/LOO synthetic corpora.

Exit codes:
  0  transfer gate PASS
  1  transfer gate FAIL or invalid/leaky evidence
  2  admissible disjoint evidence absent
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "research" / "E091_PRODUCTION_BRIDGE_FREEZE.json"
RECEIPT = ROOT / "research" / "E091_PRODUCTION_BRIDGE_RECEIPT.jsonl"
LEGACY_MANIFEST = ROOT / "research" / "E091_CORPUS_MANIFEST.json"
DEFAULT_EVIDENCE = ROOT / "research" / "E091_DISJOINT_TRANSFER_EVIDENCE.json"

EXPECTED_FREEZE_COMMIT = "c8c214b5f41d25516ad71118fa787bb4aa704f7e"
EXPECTED_BASE_COMMIT = "d0108f7faccaa656d3908f5afeaa90e056881c71"
EXPECTED_FEATURE_MAP = "final_layer_coordinate_features_v1"
EXPECTED_LAMBDA = 1.0


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _load_last_jsonl(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise AssertionError(f"empty receipt: {path}")
    return rows[-1]


def _base_checks() -> tuple[dict, dict, dict]:
    freeze = _load_json(FREEZE)["payload"]
    receipt = _load_last_jsonl(RECEIPT)
    legacy = _load_json(LEGACY_MANIFEST)

    assert freeze["status"] == "PRE_TARGET_FREEZE"
    assert freeze["selection_policy"]["selected_experiment"] == "E043"
    assert freeze["selection_policy"]["selected_commit"] == EXPECTED_BASE_COMMIT
    assert freeze["feature_map"]["name"] == EXPECTED_FEATURE_MAP
    assert float(freeze["feature_map"]["ridge"]["lambda"]) == EXPECTED_LAMBDA
    assert freeze["corpus_policy"]["new_calibration_targets_materialized_before_this_freeze"] is False
    assert legacy["purpose"] == "local_reproducibility_only"
    return freeze, receipt, legacy


def _absence_result(receipt: dict, legacy: dict, evidence_path: Path) -> dict:
    accuracy = receipt.get("accuracy", {})
    expected_unexecuted = {
        "new_disjoint_production_corpus": "UNEXECUTED",
        "ridge_fit": "UNEXECUTED",
        "synthetic_network_holdout": "UNEXECUTED",
    }
    observed = {k: accuracy.get(k) for k in expected_unexecuted}
    receipt_proves_unexecuted = observed == expected_unexecuted

    return {
        "schema": "arc.whitebox.e091.disjoint_transfer_gate.v1",
        "experiment": "E091",
        "verdict": "DATA_ABSENT_NO_GATE_EVALUATION",
        "scientific_go": False,
        "gate": "q_B > v_B/2",
        "evidence_path": str(evidence_path.relative_to(ROOT)),
        "evidence_exists": False,
        "proof": {
            "production_freeze_commit": EXPECTED_FREEZE_COMMIT,
            "selected_base_commit": EXPECTED_BASE_COMMIT,
            "production_receipt_accuracy": observed,
            "receipt_proves_transfer_unexecuted": receipt_proves_unexecuted,
            "legacy_manifest_purpose": legacy.get("purpose"),
            "legacy_manifest_schema": legacy.get("schema"),
            "legacy_corpus_admissible_for_disjoint_transfer": False,
            "reason": (
                "The only committed generated corpus manifest is frozen for local reproducibility/LOO readiness, "
                "while the production receipt explicitly records the new disjoint production corpus, ridge fit, "
                "and synthetic-network holdout as UNEXECUTED. Re-splitting that already-materialized corpus now "
                "would make corpus membership post-target and violate the E091 freeze."
            ),
        },
        "required_next_artifact": "research/E091_DISJOINT_TRANSFER_EVIDENCE.json",
    }


def _validate_evidence(e: dict) -> None:
    if e.get("schema") != "arc.whitebox.e091.disjoint_transfer_evidence.v1":
        raise AssertionError("unexpected evidence schema")
    if e.get("experiment") != "E091":
        raise AssertionError("wrong experiment")
    if e.get("production_freeze_commit") != EXPECTED_FREEZE_COMMIT:
        raise AssertionError("production freeze mismatch")
    if e.get("base_commit") != EXPECTED_BASE_COMMIT:
        raise AssertionError("base commit mismatch")
    if e.get("feature_map") != EXPECTED_FEATURE_MAP:
        raise AssertionError("feature map mismatch")
    if float(e.get("ridge_lambda")) != EXPECTED_LAMBDA:
        raise AssertionError("ridge lambda mismatch")

    for key in (
        "beta_frozen_before_B",
        "feature_preprocessing_frozen_before_B",
        "lambda_frozen_before_B",
        "corpus_membership_frozen_before_targets",
    ):
        if e.get(key) is not True:
            raise AssertionError(f"leakage/freeze gate failed: {key}")

    roots_a = set(map(str, e.get("root_ids_A", [])))
    roots_b = set(map(str, e.get("root_ids_B", [])))
    if not roots_a or not roots_b:
        raise AssertionError("root identity sets must both be non-empty")
    overlap = sorted(roots_a & roots_b)
    if overlap:
        raise AssertionError(f"A/B root overlap: {overlap[:8]}")
    if e.get("calibration_corpus_id") == e.get("evaluation_corpus_id"):
        raise AssertionError("A/B corpus ids must differ")


def _evaluate(e: dict) -> dict:
    _validate_evidence(e)
    r = np.asarray(e["residual_B"], dtype=np.float64)
    s = np.asarray(e["correction_B"], dtype=np.float64)
    if r.shape != s.shape or r.size == 0:
        raise AssertionError(f"shape mismatch/empty: residual={r.shape}, correction={s.shape}")
    if not np.isfinite(r).all() or not np.isfinite(s).all():
        raise AssertionError("non-finite transfer evidence")

    rr = r.reshape(-1)
    ss = s.reshape(-1)
    q_b = float(np.mean(rr * ss))
    v_b = float(np.mean(ss * ss))
    threshold = 0.5 * v_b
    delta = 2.0 * q_b - v_b
    mse0 = float(np.mean(rr * rr))
    mse1 = float(np.mean((rr - ss) ** 2))
    identity_error = abs((mse0 - mse1) - delta)
    tol = 64.0 * np.finfo(np.float64).eps * max(1.0, abs(mse0), abs(mse1), abs(delta))
    if identity_error > tol:
        raise AssertionError(f"MSE identity mismatch: {identity_error} > {tol}")

    passed = bool(q_b > threshold)
    return {
        "schema": "arc.whitebox.e091.disjoint_transfer_gate.v1",
        "experiment": "E091",
        "verdict": "PASS" if passed else "FAIL",
        "scientific_go": False,
        "gate": "q_B > v_B/2",
        "q_B": q_b,
        "v_B": v_b,
        "v_B_over_2": threshold,
        "delta_B": delta,
        "baseline_mse_B": mse0,
        "corrected_mse_B": mse1,
        "mse_identity_abs_error": identity_error,
        "n_scalar_coordinates": int(rr.size),
        "root_overlap": [],
        "notes": "PASS here establishes only disjoint transfer of the frozen correction; it is not public/scorer/holdout scientific GO.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args()
    evidence_path = args.evidence if args.evidence.is_absolute() else ROOT / args.evidence

    _, receipt, legacy = _base_checks()
    if not evidence_path.exists():
        result = _absence_result(receipt, legacy, evidence_path)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    try:
        result = _evaluate(_load_json(evidence_path))
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({
            "schema": "arc.whitebox.e091.disjoint_transfer_gate.v1",
            "experiment": "E091",
            "verdict": "INVALID_EVIDENCE",
            "scientific_go": False,
            "error": str(exc),
        }, indent=2, sort_keys=True))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
