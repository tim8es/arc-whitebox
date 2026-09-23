#!/usr/bin/env python3
"""R291 evaluator-side capture helper for the frozen R288 V25 contract.

This module is standard-library only. It never imports WhestBench, FlopScope or NumPy.
At the future authorized run it is called only from evaluator-side seams after the
participant BudgetContext has closed. It snapshots already-materialized float32 arrays
with .tobytes(order="C"); it never mutates scorer arrays or computes a score.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any

PROTOCOL = "arc.whitebox.r291.capture.v1"
ROWS = 100
WIDTH = 1024
DEPTH = 16
F32_BYTES = 4
VECTOR_BYTES = WIDTH * F32_BYTES
ALL_TARGET_BYTES = DEPTH * WIDTH * F32_BYTES
RECORD_BYTES = 3 * VECTOR_BYTES
RAW_PAYLOAD_BYTES = ROWS * RECORD_BYTES
MANIFEST_MAX_BYTES = 131_072
SHA256SUMS_MAX_BYTES = 4_096
UNCOMPRESSED_MAX_BYTES = RAW_PAYLOAD_BYTES + MANIFEST_MAX_BYTES + SHA256SUMS_MAX_BYTES

EXPECTED_NAME_ORDER_SHA256 = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
EXPECTED_DATASET_METADATA_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
V25_SOURCE_COMMIT = "dff3dd65e9d2210e02418cca99e05556f6bf2c75"
V25_SOURCE_BLOB_SHA1 = "195373a110215256b759d7c172ba8c923c62e5cc"
WH_EST_VERSION = "0.16.1"
WH_EST_COMMIT = "4d08668b485c8a7d25a105c3c00d2f4fc2538f18"
WH_EST_SCORING_BLOB_SHA1 = "9cf7653a0267c4d048617c9045ac8be127f3c8bf"
FLOPSCOPE_VERSION = "0.12.1"
FLOPSCOPE_COMMIT = "b599f015b0bc005b1edb6d7a1b10e0814675e693"
PYTHON_VERSION = "3.11.16"
NUMPY_VERSION = "2.4.6"
DATASET_REPO = "aicrowd/arc-whestbench-public-2026"
DATASET_REVISION = "v2-phase2"
DATASET_SPLIT = "mini"

FAILURE_FIELDS = (
    "budget_exhausted",
    "time_exhausted",
    "residual_wall_time_exhausted",
    "combined_budget_exhausted",
)


class CaptureError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_sha256(value: str, label: str) -> str:
    value = str(value)
    if len(value) != 64:
        raise CaptureError(f"{label}: expected 64 hex chars")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise CaptureError(f"{label}: not hex") from exc
    return value.lower()


def _canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _array_bytes(obj: Any, expected_shape: tuple[int, ...]) -> bytes:
    if sys.byteorder != "little":
        raise CaptureError("R288 canonical <f4 format requires a little-endian capture host")
    shape = tuple(int(x) for x in getattr(obj, "shape", ()))
    if shape != expected_shape:
        raise CaptureError(f"shape mismatch: expected {expected_shape}, got {shape}")
    dtype = getattr(obj, "dtype", None)
    if str(dtype) != "float32":
        raise CaptureError(f"dtype mismatch: expected float32, got {dtype!r}")
    byteorder = getattr(dtype, "byteorder", "=")
    if byteorder not in ("<", "=", "|"):
        raise CaptureError(f"dtype byteorder mismatch: expected little/native, got {byteorder!r}")
    try:
        raw = obj.tobytes(order="C")
    except TypeError as exc:
        raise CaptureError("array must provide tobytes(order='C')") from exc
    expected_bytes = F32_BYTES
    for dim in expected_shape:
        expected_bytes *= dim
    if len(raw) != expected_bytes:
        raise CaptureError(f"byte length mismatch: expected {expected_bytes}, got {len(raw)}")
    return bytes(raw)


def _residual_f32le(target: bytes, pred: bytes) -> bytes:
    if len(target) != VECTOR_BYTES or len(pred) != VECTOR_BYTES:
        raise CaptureError("residual inputs must each be exactly one float32[1024] vector")
    out = bytearray(VECTOR_BYTES)
    t_iter = struct.iter_unpack("<f", target)
    p_iter = struct.iter_unpack("<f", pred)
    for i, ((t,), (p,)) in enumerate(zip(t_iter, p_iter)):
        struct.pack_into("<f", out, i * F32_BYTES, t - p)
    return bytes(out)


def _name_order_sha(names: list[str]) -> str:
    # Exact R224 canonicalization: compact JSON list, UTF-8, no trailing newline.
    return _sha(json.dumps(names, separators=(",", ":")).encode("utf-8"))


def _load_expected_panel(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    records = obj.get("records")
    if not isinstance(records, list) or len(records) != ROWS:
        raise CaptureError(f"expected-panel row count must be {ROWS}")
    names = [str(r["mlp_name"]) for r in records]
    if _name_order_sha(names) != EXPECTED_NAME_ORDER_SHA256:
        raise CaptureError("expected-panel name/order hash does not match frozen R224 identity")
    nids = [str(r["network_id"]) for r in records]
    if len(set(nids)) != ROWS:
        raise CaptureError("expected-panel network_id values are not unique")
    source = obj.get("source") or {}
    ds = source.get("dataset") or {}
    if ds.get("metadata_sha256") != EXPECTED_DATASET_METADATA_SHA256:
        raise CaptureError("expected-panel dataset metadata hash mismatch")
    return obj


def _split_roles(records: list[dict[str, Any]]) -> dict[str, str]:
    sorted_ids = sorted(str(r["network_id"]) for r in records)
    fit = set(sorted_ids[:50])
    return {nid: ("FIT" if nid in fit else "EVAL") for nid in sorted_ids}


def _zero_vector(raw: bytes) -> bool:
    return raw == (b"\x00" * VECTOR_BYTES)


class CaptureSession:
    """Stage exactly 100 R288 records without changing scorer objects or outputs."""

    def __init__(
        self,
        output_dir: Path,
        expected_panel_path: Path,
        provenance: dict[str, Any],
    ) -> None:
        self.output_dir = Path(output_dir)
        self.expected_panel_path = Path(expected_panel_path)
        self.expected = _load_expected_panel(self.expected_panel_path)
        self.records_expected = self.expected["records"]
        self.roles = _split_roles(self.records_expected)
        self.provenance = dict(provenance)
        self.rows: list[dict[str, Any]] = []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_vectors = self.output_dir / "vectors.f32le.part"
        self.vectors = self.output_dir / "vectors.f32le"
        self.partial_manifest = self.output_dir / "manifest.partial.json"
        self.manifest = self.output_dir / "manifest.json"
        self.sums = self.output_dir / "SHA256SUMS"
        for path in (self.tmp_vectors, self.vectors, self.partial_manifest, self.manifest, self.sums):
            if path.exists():
                raise CaptureError(f"refusing to overwrite existing capture path: {path}")
        self._fh = self.tmp_vectors.open("xb")

    def capture(
        self,
        *,
        scorer_mlp_index: int,
        mlp_name: str,
        final_pred: Any,
        final_target: Any,
        all_target: Any,
        budget_exhausted: bool,
        time_exhausted: bool,
        residual_wall_time_exhausted: bool,
        combined_budget_exhausted: bool,
        error_code: str | None,
        flops_used: int,
        effective_compute: float,
    ) -> None:
        idx = int(scorer_mlp_index)
        if idx != len(self.rows):
            raise CaptureError(f"capture order mismatch: expected index {len(self.rows)}, got {idx}")
        if idx >= ROWS:
            raise CaptureError("more than 100 rows supplied")
        expected = self.records_expected[idx]
        if str(mlp_name) != str(expected["mlp_name"]):
            raise CaptureError(
                f"mlp_name mismatch at row {idx}: expected {expected['mlp_name']!r}, got {mlp_name!r}"
            )

        pred = _array_bytes(final_pred, (WIDTH,))
        target = _array_bytes(final_target, (WIDTH,))
        all_target_bytes = _array_bytes(all_target, (DEPTH, WIDTH))
        observed_target_all_sha = _sha(all_target_bytes)
        expected_target_all_sha = _require_sha256(
            expected["r224_target_all_sha256"], "r224_target_all_sha256"
        )
        if observed_target_all_sha != expected_target_all_sha:
            raise CaptureError(f"R224 all-layer target hash mismatch at row {idx}")

        residual = _residual_f32le(target, pred)
        payload = pred + target + residual
        expected_offset = idx * RECORD_BYTES
        if self._fh.tell() != expected_offset:
            raise CaptureError("vectors payload offset mismatch")
        self._fh.write(payload)

        flags = {
            "budget_exhausted": bool(budget_exhausted),
            "time_exhausted": bool(time_exhausted),
            "residual_wall_time_exhausted": bool(residual_wall_time_exhausted),
            "combined_budget_exhausted": bool(combined_budget_exhausted),
        }
        zeroed = bool(error_code) or any(flags.values())
        if zeroed and not _zero_vector(pred):
            raise CaptureError(f"failure row {idx} is not the scorer's zeroed prediction")

        nid = str(expected["network_id"])
        row = {
            "scorer_mlp_index": idx,
            "mlp_name": str(mlp_name),
            "network_id": nid,
            "split_role": self.roles[nid],
            "r224_target_all_sha256_expected": expected_target_all_sha,
            "r224_target_all_sha256_observed": observed_target_all_sha,
            "final_pred_sha256": _sha(pred),
            "final_target_sha256": _sha(target),
            "residual_sha256": _sha(residual),
            "record_payload_sha256": _sha(payload),
            "budget_exhausted": flags["budget_exhausted"],
            "time_exhausted": flags["time_exhausted"],
            "residual_wall_time_exhausted": flags["residual_wall_time_exhausted"],
            "combined_budget_exhausted": flags["combined_budget_exhausted"],
            "error_code": None if error_code is None else str(error_code),
            "flops_used": int(flops_used),
            "effective_compute": float(effective_compute),
            "scored_prediction_zeroed": zeroed,
            "payload_offset_bytes": expected_offset,
        }
        self.rows.append(row)

    def stage(self) -> dict[str, Any]:
        if self._fh.closed:
            raise CaptureError("capture already staged")
        if len(self.rows) != ROWS:
            raise CaptureError(f"cannot stage incomplete capture: {len(self.rows)}/{ROWS} rows")
        self._fh.flush()
        self._fh.close()
        if self.tmp_vectors.stat().st_size != RAW_PAYLOAD_BYTES:
            raise CaptureError("raw payload size mismatch")
        self.tmp_vectors.replace(self.vectors)

        manifest = {
            "schema": PROTOCOL,
            "status": "STAGED_AWAITING_OFFICIAL_REPORT_HASH",
            "rows": ROWS,
            "dtype": "<f4",
            "vector_shape": [WIDTH],
            "axis1": ["final_pred", "final_target", "residual_target_minus_pred"],
            "residual_sign": "final_target - final_pred",
            "raw_payload_bytes": RAW_PAYLOAD_BYTES,
            "vectors_sha256": _sha(self.vectors.read_bytes()),
            "expected_name_order_sha256": EXPECTED_NAME_ORDER_SHA256,
            "dataset_metadata_sha256": EXPECTED_DATASET_METADATA_SHA256,
            "frozen_rule": {
                "split": "sort decimal network_id strings lexicographically; first 50 FIT, last 50 EVAL",
                "fit": "d = mean_FIT(target_final - v25_pred_final)",
                "eval": "pred_corrected = pred + d on EVAL only",
                "per_network_tuning": False,
            },
            "pinned": {
                "v25_source_commit": V25_SOURCE_COMMIT,
                "v25_source_blob_sha1": V25_SOURCE_BLOB_SHA1,
                "python": PYTHON_VERSION,
                "whestbench": WH_EST_VERSION,
                "whestbench_source_commit": WH_EST_COMMIT,
                "whestbench_scoring_blob_sha1": WH_EST_SCORING_BLOB_SHA1,
                "flopscope": FLOPSCOPE_VERSION,
                "flopscope_source_commit": FLOPSCOPE_COMMIT,
                "numpy": NUMPY_VERSION,
                "dataset_repo": DATASET_REPO,
                "dataset_revision": DATASET_REVISION,
                "dataset_split": DATASET_SPLIT,
            },
            "provenance": self.provenance,
            "official_report_sha256": None,
            "records": self.rows,
        }
        raw = _canonical_json_bytes(manifest)
        if len(raw) > MANIFEST_MAX_BYTES:
            raise CaptureError(f"partial manifest exceeds {MANIFEST_MAX_BYTES} bytes")
        self.partial_manifest.write_bytes(raw)
        return {
            "rows": len(self.rows),
            "vectors_sha256": manifest["vectors_sha256"],
            "raw_payload_bytes": RAW_PAYLOAD_BYTES,
            "partial_manifest_sha256": _sha(raw),
        }


def _validate_staged_payload(root: Path, manifest: dict[str, Any]) -> None:
    vectors = root / "vectors.f32le"
    raw = vectors.read_bytes()
    if len(raw) != RAW_PAYLOAD_BYTES:
        raise CaptureError("vectors.f32le size mismatch at seal")
    if _sha(raw) != manifest.get("vectors_sha256"):
        raise CaptureError("vectors.f32le SHA256 mismatch at seal")
    rows = manifest.get("records")
    if not isinstance(rows, list) or len(rows) != ROWS:
        raise CaptureError("manifest record count mismatch at seal")
    for idx, row in enumerate(rows):
        off = idx * RECORD_BYTES
        pred = raw[off : off + VECTOR_BYTES]
        target = raw[off + VECTOR_BYTES : off + 2 * VECTOR_BYTES]
        residual = raw[off + 2 * VECTOR_BYTES : off + 3 * VECTOR_BYTES]
        if _sha(pred) != row["final_pred_sha256"]:
            raise CaptureError(f"pred hash mismatch at row {idx}")
        if _sha(target) != row["final_target_sha256"]:
            raise CaptureError(f"target hash mismatch at row {idx}")
        if _sha(residual) != row["residual_sha256"]:
            raise CaptureError(f"residual hash mismatch at row {idx}")
        if _sha(pred + target + residual) != row["record_payload_sha256"]:
            raise CaptureError(f"record hash mismatch at row {idx}")
        if residual != _residual_f32le(target, pred):
            raise CaptureError(f"residual bytes mismatch at row {idx}")
        if int(row["payload_offset_bytes"]) != off:
            raise CaptureError(f"record offset mismatch at row {idx}")


def seal_staged_capture(root: Path, official_report: Path) -> dict[str, Any]:
    root = Path(root)
    partial_path = root / "manifest.partial.json"
    manifest_path = root / "manifest.json"
    sums_path = root / "SHA256SUMS"
    if manifest_path.exists() or sums_path.exists():
        raise CaptureError("refusing to overwrite a sealed capture")
    manifest = json.loads(partial_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != PROTOCOL:
        raise CaptureError("partial manifest schema mismatch")
    _validate_staged_payload(root, manifest)

    report_sha = _sha(Path(official_report).read_bytes())
    manifest["official_report_sha256"] = report_sha
    manifest["status"] = "SEALED"
    raw_manifest = _canonical_json_bytes(manifest)
    if len(raw_manifest) > MANIFEST_MAX_BYTES:
        raise CaptureError(f"manifest exceeds {MANIFEST_MAX_BYTES} bytes")
    manifest_path.write_bytes(raw_manifest)

    vectors_sha = _sha((root / "vectors.f32le").read_bytes())
    manifest_sha = _sha(raw_manifest)
    sums = (
        f"{vectors_sha}  vectors.f32le\n"
        f"{manifest_sha}  manifest.json\n"
    ).encode("ascii")
    if len(sums) > SHA256SUMS_MAX_BYTES:
        raise CaptureError("SHA256SUMS exceeds protocol limit")
    sums_path.write_bytes(sums)

    total = (root / "vectors.f32le").stat().st_size + manifest_path.stat().st_size + sums_path.stat().st_size
    if total > UNCOMPRESSED_MAX_BYTES:
        raise CaptureError("sealed capture exceeds R288 uncompressed upper bound")
    partial_path.unlink()
    return {
        "rows": ROWS,
        "vectors_sha256": vectors_sha,
        "manifest_sha256": manifest_sha,
        "sha256sums_sha256": _sha(sums),
        "official_report_sha256": report_sha,
        "uncompressed_bytes": total,
    }


def capture_from_env() -> CaptureSession | None:
    """Future integration entrypoint. Disabled unless R291_CAPTURE_DIR is set."""
    out = os.environ.get("R291_CAPTURE_DIR")
    if not out:
        return None
    panel = os.environ.get("R291_EXPECTED_PANEL")
    if not panel:
        raise CaptureError("R291_EXPECTED_PANEL is required when capture is enabled")
    provenance_keys = (
        "R291_RUN_ID",
        "R291_WORKFLOW_RUN_ID",
        "R291_CAPTURE_CODE_COMMIT",
        "R291_CAPTURE_CODE_BLOB",
    )
    provenance: dict[str, Any] = {}
    for key in provenance_keys:
        value = os.environ.get(key)
        if not value:
            raise CaptureError(f"{key} is required when capture is enabled")
        provenance[key.lower()] = value
    return CaptureSession(Path(out), Path(panel), provenance)


def _main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    seal = sub.add_parser("seal")
    seal.add_argument("--capture-dir", type=Path, required=True)
    seal.add_argument("--official-report", type=Path, required=True)
    args = ap.parse_args()
    if args.cmd == "seal":
        print(json.dumps(seal_staged_capture(args.capture_dir, args.official_report), sort_keys=True))
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(_main())
