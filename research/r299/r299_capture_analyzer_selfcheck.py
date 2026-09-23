#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r299_analyzer", HERE / "r299_capture_analyzer.py")
assert SPEC and SPEC.loader
a = importlib.util.module_from_spec(SPEC)
sys.modules["r299_analyzer"] = a
SPEC.loader.exec_module(a)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fvec(value: float) -> bytes:
    return struct.pack("<f", value) * a.WIDTH


def write_sums(root: Path) -> None:
    v = (root / "vectors.f32le").read_bytes()
    m = (root / "manifest.json").read_bytes()
    (root / "SHA256SUMS").write_text(
        f"{sha(v)}  vectors.f32le\n{sha(m)}  manifest.json\n", encoding="ascii"
    )


def rewrite_manifest(root: Path, mutate) -> None:
    p = root / "manifest.json"
    obj = json.loads(p.read_text())
    mutate(obj)
    p.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")
    write_sums(root)


def build_fixture(root: Path) -> tuple[Path, a.Contract]:
    names = [f"synthetic-{i:03d}" for i in range(a.ROWS)]
    name_hash = sha(json.dumps(names, separators=(",", ":")).encode())
    metadata_hash = sha(b"synthetic-r298-metadata")
    contract = a.Contract(name_hash, metadata_hash, a.PINNED)

    records = []
    for i, name in enumerate(names):
        records.append({
            "scorer_mlp_index": i,
            "mlp_name": name,
            "network_id": str(10000 + i),
            "r224_target_all_sha256": sha(f"target-all-{i}".encode()),
        })
    panel = {
        "schema": a.PANEL_SCHEMA,
        "source": {
            "dataset": {
                "count": a.ROWS,
                "metadata_sha256": metadata_hash,
                "target_dtype": "float32",
                "target_shape": [16, a.WIDTH],
            },
            "canonicalization": {
                "name_order_sha256": name_hash,
                "network_id": "decimal exact int64 mlp_seed",
                "target_sha256": "SHA256 C-contiguous raw float32 all_layer_means bytes",
            },
        },
        "records": records,
    }
    panel_path = root / "panel.json"
    panel_path.write_text(json.dumps(panel, sort_keys=True, separators=(",", ":")) + "\n")
    panel_raw = panel_path.read_bytes()

    ids = [r["network_id"] for r in records]
    fit = set(sorted(ids)[:50])
    payload = bytearray()
    manifest_rows = []
    for i, row in enumerate(records):
        role = "FIT" if row["network_id"] in fit else "EVAL"
        failure = i == 75
        if role == "FIT":
            pred, target = fvec(1.0), fvec(2.0)
        else:
            pred, target = (fvec(0.0) if failure else fvec(2.0)), fvec(3.0)
        residual = a._residual_bytes(target, pred)
        rec = pred + target + residual
        off = len(payload)
        payload.extend(rec)
        manifest_rows.append({
            "scorer_mlp_index": i,
            "mlp_name": row["mlp_name"],
            "network_id": row["network_id"],
            "split_role": role,
            "r224_target_all_sha256_expected": row["r224_target_all_sha256"],
            "r224_target_all_sha256_observed": row["r224_target_all_sha256"],
            "final_pred_sha256": sha(pred),
            "final_target_sha256": sha(target),
            "residual_sha256": sha(residual),
            "record_payload_sha256": sha(rec),
            "budget_exhausted": False,
            "time_exhausted": False,
            "residual_wall_time_exhausted": False,
            "combined_budget_exhausted": False,
            "error_code": "SYNTHETIC_EXCEPTION" if failure else None,
            "flops_used": 0 if failure else 123,
            "effective_compute": 0.0 if failure else 123.0,
            "scored_prediction_zeroed": failure,
            "payload_offset_bytes": off,
        })
    cap = root / "capture"
    cap.mkdir()
    (cap / "vectors.f32le").write_bytes(bytes(payload))
    manifest = {
        "schema": a.CAPTURE_SCHEMA,
        "status": "SEALED",
        "rows": a.ROWS,
        "dtype": "<f4",
        "vector_shape": [a.WIDTH],
        "axis1": ["final_pred", "final_target", "residual_target_minus_pred"],
        "residual_sign": "final_target - final_pred",
        "raw_payload_bytes": a.RAW_PAYLOAD_BYTES,
        "vectors_sha256": sha(bytes(payload)),
        "expected_name_order_sha256": name_hash,
        "dataset_metadata_sha256": metadata_hash,
        "frozen_rule": {
            "split": "sort decimal network_id strings lexicographically; first 50 FIT, last 50 EVAL",
            "fit": "d = mean_FIT(target_final - v25_pred_final)",
            "eval": "pred_corrected = pred + d on EVAL only",
            "per_network_tuning": False,
        },
        "metering_boundary": "synthetic",
        "pinned": a.PINNED,
        "provenance": {"synthetic": True},
        "expected_panel_sha256": sha(panel_raw),
        "official_report_sha256": sha(b"synthetic-report"),
        "records": manifest_rows,
    }
    (cap / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
    write_sums(cap)
    return panel_path, contract


def expect_reject(label: str, root: Path, panel: Path, contract: a.Contract) -> None:
    try:
        a.analyze_capture(root, panel, contract)
    except a.AnalyzerError:
        return
    raise AssertionError(f"{label}: corruption was accepted")


def clone_capture(src: Path, dst: Path) -> Path:
    dst.mkdir()
    for name in ("vectors.f32le", "manifest.json", "SHA256SUMS"):
        (dst / name).write_bytes((src / name).read_bytes())
    return dst


def main() -> int:
    checks = {}
    with tempfile.TemporaryDirectory(prefix="r299-selfcheck-") as td:
        root = Path(td)
        panel, contract = build_fixture(root)
        cap = root / "capture"
        result = a.analyze_capture(cap, panel, contract)
        checks["valid_fixture"] = result["capture_integrity"]["rows"] == 100
        checks["split_50_50"] = result["capture_integrity"]["fit_rows"] == 50 and result["capture_integrity"]["eval_rows"] == 50
        checks["frozen_rule_only"] = result["frozen_rule"]["no_alpha_rank_sign_or_network_tuning"] is True
        checks["failure_retained"] = len(result["per_network_eval"]) == 50 and any(r["scored_prediction_zeroed"] for r in result["per_network_eval"])
        checks["materiality_gates_exercised"] = result["all_four_materiality_gates_pass"] is True
        checks["offline_label"] = result["classification"] == "OFFLINE_DIAGNOSTIC_ONLY_NOT_OFFICIAL_ADJUSTED_SCORE"
        checks["production_pins_frozen"] = a.PRODUCTION_CONTRACT.name_order_sha256 == a.EXPECTED_NAME_ORDER_SHA256 and a.PRODUCTION_CONTRACT.dataset_metadata_sha256 == a.EXPECTED_DATASET_METADATA_SHA256

        c = clone_capture(cap, root / "bad-sums")
        raw = c.joinpath("SHA256SUMS").read_text()
        c.joinpath("SHA256SUMS").write_text("0" * 64 + raw[64:])
        expect_reject("bad sums", c, panel, contract); checks["reject_bad_sums"] = True

        c = clone_capture(cap, root / "dup-id")
        rewrite_manifest(c, lambda m: m["records"][1].__setitem__("network_id", m["records"][0]["network_id"]))
        expect_reject("duplicate id", c, panel, contract); checks["reject_duplicate_id"] = True

        c = clone_capture(cap, root / "bad-split")
        rewrite_manifest(c, lambda m: m["records"][0].__setitem__("split_role", "EVAL"))
        expect_reject("split mismatch", c, panel, contract); checks["reject_split_mismatch"] = True

        c = clone_capture(cap, root / "bad-target")
        rewrite_manifest(c, lambda m: m["records"][0].__setitem__("r224_target_all_sha256_observed", "0" * 64))
        expect_reject("target fingerprint", c, panel, contract); checks["reject_target_fingerprint"] = True

        c = clone_capture(cap, root / "bad-failure")
        rewrite_manifest(c, lambda m: m["records"][75].__setitem__("scored_prediction_zeroed", False))
        expect_reject("failure flags", c, panel, contract); checks["reject_failure_flag_mismatch"] = True

        c = clone_capture(cap, root / "bad-residual")
        v = bytearray(c.joinpath("vectors.f32le").read_bytes())
        v[2 * a.VECTOR_BYTES] ^= 1
        c.joinpath("vectors.f32le").write_bytes(v)
        rewrite_manifest(c, lambda m: m.__setitem__("vectors_sha256", sha(bytes(v))))
        expect_reject("residual corruption", c, panel, contract); checks["reject_residual_corruption"] = True

        energy_residuals = [
            [0.0, -1.0] + [1.0] * (a.WIDTH - 2),
            [0.0, -1.0] + [1.0] * (a.WIDTH - 2),
        ]
        energy_d = [1.0] * a.WIDTH
        energy = a._coordinate_energy_summary(energy_residuals, [0, 1], energy_d)
        checks["zero_energy_null"] = (
            energy["coordinates"][0]["B_k"] == 0.0
            and energy["coordinates"][0]["C_k"] == 2.0
            and energy["coordinates"][0]["explained_fraction"] is None
            and energy["zero_energy_coordinate_count"] == 1
            and energy["finite_coordinate_count"] == a.WIDTH - 1
        )
        checks["negative_explained"] = (
            energy["coordinates"][1]["B_k"] == 2.0
            and energy["coordinates"][1]["C_k"] == 8.0
            and energy["coordinates"][1]["explained_fraction"] == -3.0
            and energy["negative_explained_coordinate_count"] == 1
        )
        expected_global = 1.0 - (10.0 / (2.0 + 2.0 * (a.WIDTH - 2)))
        checks["weighted_global_includes_zero_energy_penalty"] = (
            energy["weighted_global_explained_fraction"] == expected_global
        )
        q = [0.0, 10.0, 20.0, 30.0]
        checks["type7_quantile_convention"] = (
            a._quantile_type7(q, 0.10) == 3.0
            and a._quantile_type7(q, 0.25) == 7.5
            and a._quantile_type7(q, 0.50) == 15.0
            and a._quantile_type7(q, 0.75) == 22.5
            and a._quantile_type7(q, 0.90) == 27.0
        )
        checks["energy_output_present"] = (
            result["coordinate_residual_energy"]["coordinate_count"] == a.WIDTH
            and set(result["coordinate_residual_energy"]["central_quantiles_type7"])
            == {"p10", "p25", "p50", "p75", "p90"}
        )

    checks["pass"] = all(checks.values())
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0 if checks["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
