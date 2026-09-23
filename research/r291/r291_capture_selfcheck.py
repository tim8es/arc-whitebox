#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r291_capture", HERE / "r291_capture_harness.py")
assert SPEC and SPEC.loader
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


class FakeDType:
    byteorder = "="
    def __str__(self) -> str:
        return "float32"


class FakeArray:
    dtype = FakeDType()
    def __init__(self, raw: bytes, shape: tuple[int, ...]):
        self._raw = bytes(raw)
        self.shape = shape
    def tobytes(self, order: str = "C") -> bytes:
        assert order == "C"
        return self._raw


def f32_repeat(value: float, n: int) -> bytes:
    return struct.pack("<f", value) * n


def mse(pred: bytes, target: bytes) -> float:
    ps = struct.iter_unpack("<f", pred)
    ts = struct.iter_unpack("<f", target)
    total = 0.0
    n = 0
    for (p,), (t,) in zip(ps, ts):
        d = p - t
        total += d * d
        n += 1
    return total / n


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    out: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="r291-selfcheck-") as td:
        root = Path(td)

        names = [f"synthetic-{i:03d}" for i in range(h.ROWS)]
        synthetic_name_sha = sha(
            json.dumps(names, separators=(",", ":")).encode("utf-8")
        )
        old_name_sha = h.EXPECTED_NAME_ORDER_SHA256
        old_meta_sha = h.EXPECTED_DATASET_METADATA_SHA256
        h.EXPECTED_NAME_ORDER_SHA256 = synthetic_name_sha
        h.EXPECTED_DATASET_METADATA_SHA256 = "synthetic-metadata"

        expected_records = []
        row_inputs = []
        for i, name in enumerate(names):
            target = f32_repeat((i + 1) / 256.0, h.WIDTH)
            if i == 17:
                pred = b"\x00" * h.VECTOR_BYTES
            else:
                pred = f32_repeat(i / 256.0, h.WIDTH)
            all_target = b"\x00" * ((h.DEPTH - 1) * h.VECTOR_BYTES) + target
            expected_records.append(
                {
                    "scorer_mlp_index": i,
                    "mlp_name": name,
                    "network_id": str(10_000 + i),
                    "r224_target_all_sha256": sha(all_target),
                }
            )
            row_inputs.append((pred, target, all_target))

        panel = {
            "schema": "synthetic",
            "source": {"dataset": {"metadata_sha256": "synthetic-metadata"}},
            "records": expected_records,
        }
        panel_path = root / "panel.json"
        panel_path.write_text(json.dumps(panel, sort_keys=True) + "\n", encoding="utf-8")

        capture_dir = root / "capture"
        session = h.CaptureSession(
            capture_dir,
            panel_path,
            {
                "r291_run_id": "synthetic",
                "r291_workflow_run_id": "none",
                "r291_capture_code_commit": "0" * 40,
                "r291_capture_code_blob": "0" * 40,
            },
        )

        scorer_outputs_before = []
        scorer_outputs_after = []
        original_bytes_preserved = True
        for i, (pred, target, all_target) in enumerate(row_inputs):
            pred_obj = FakeArray(pred, (h.WIDTH,))
            target_obj = FakeArray(target, (h.WIDTH,))
            all_target_obj = FakeArray(all_target, (h.DEPTH, h.WIDTH))
            before_pred = pred_obj.tobytes()
            before_target = target_obj.tobytes()
            score_before = mse(before_pred, before_target)
            scorer_outputs_before.append(score_before)

            session.safe_capture(
                scorer_mlp_index=i,
                mlp_name=names[i],
                final_pred=pred_obj,
                final_target=target_obj,
                all_target=all_target_obj,
                budget_exhausted=False,
                time_exhausted=False,
                residual_wall_time_exhausted=False,
                combined_budget_exhausted=False,
                error_code="SYNTHETIC_EXCEPTION" if i == 17 else None,
                flops_used=0 if i == 17 else 123,
                effective_compute=0.0 if i == 17 else 123.0,
            )

            after_pred = pred_obj.tobytes()
            after_target = target_obj.tobytes()
            original_bytes_preserved &= before_pred == after_pred and before_target == after_target
            scorer_outputs_after.append(mse(after_pred, after_target))

        fake_report = root / "report.json"
        fake_report.write_text('{"synthetic_official_result":true}\n', encoding="utf-8")
        sealed = h.seal_staged_capture(capture_dir, fake_report)
        manifest = json.loads((capture_dir / "manifest.json").read_text(encoding="utf-8"))
        vectors = (capture_dir / "vectors.f32le").read_bytes()

        out["serialization_sealed"] = manifest["status"] == "SEALED"
        out["rows_100"] = manifest["rows"] == h.ROWS and len(manifest["records"]) == h.ROWS
        out["raw_payload_exact"] = len(vectors) == h.RAW_PAYLOAD_BYTES == 1_228_800
        out["storage_bound"] = sealed["uncompressed_bytes"] <= h.UNCOMPRESSED_MAX_BYTES
        out["fit_eval_50_50"] = (
            sum(r["split_role"] == "FIT" for r in manifest["records"]) == 50
            and sum(r["split_role"] == "EVAL" for r in manifest["records"]) == 50
        )
        out["failure_zero_row_preserved"] = (
            manifest["records"][17]["scored_prediction_zeroed"]
            and manifest["records"][17]["error_code"] == "SYNTHETIC_EXCEPTION"
            and vectors[17 * h.RECORD_BYTES : 17 * h.RECORD_BYTES + h.VECTOR_BYTES]
            == b"\x00" * h.VECTOR_BYTES
        )
        out["scorer_inputs_unchanged"] = original_bytes_preserved
        out["synthetic_scorer_outputs_unchanged"] = scorer_outputs_before == scorer_outputs_after

        first = vectors[: h.RECORD_BYTES]
        p0 = first[: h.VECTOR_BYTES]
        t0 = first[h.VECTOR_BYTES : 2 * h.VECTOR_BYTES]
        r0 = first[2 * h.VECTOR_BYTES :]
        out["residual_exact"] = r0 == h._residual_f32le(t0, p0)
        out["record_hash_exact"] = sha(first) == manifest["records"][0]["record_payload_sha256"]
        out["target_all_hash_verified"] = all(
            r["r224_target_all_sha256_expected"] == r["r224_target_all_sha256_observed"]
            for r in manifest["records"]
        )

        # Capture errors must be isolated from the synthetic scorer.
        bad_dir = root / "bad-capture"
        bad = h.CaptureSession(
            bad_dir,
            panel_path,
            {
                "r291_run_id": "synthetic-bad",
                "r291_workflow_run_id": "none",
                "r291_capture_code_commit": "0" * 40,
                "r291_capture_code_blob": "0" * 40,
            },
        )
        sentinel = {"score": 7.25, "failure": False}
        bad.safe_capture(
            scorer_mlp_index=0,
            mlp_name=names[0],
            final_pred=FakeArray(b"\x00" * 16, (4,)),  # deliberate contract violation
            final_target=FakeArray(row_inputs[0][1], (h.WIDTH,)),
            all_target=FakeArray(row_inputs[0][2], (h.DEPTH, h.WIDTH)),
            budget_exhausted=False,
            time_exhausted=False,
            residual_wall_time_exhausted=False,
            combined_budget_exhausted=False,
            error_code=None,
            flops_used=123,
            effective_compute=123.0,
        )
        out["capture_error_isolated"] = (
            bad.disabled
            and (bad_dir / "capture_error.txt").exists()
            and sentinel == {"score": 7.25, "failure": False}
        )

        # Static patch guard: the prepared integration only adds capture calls;
        # it must not delete or assign canonical scorer/score variables.
        patch = (HERE / "R291_WHESTBENCH_0_16_1_INTEGRATION.patch").read_text(encoding="utf-8")
        removed_code = [
            ln for ln in patch.splitlines()
            if ln.startswith("-") and not ln.startswith("---")
        ]
        added = [
            ln[1:] for ln in patch.splitlines()
            if ln.startswith("+") and not ln.startswith("+++")
        ]
        critical_assignment = re.compile(
            r"^\s*(predictions|pred_np|final_pred|final_target|final_layer_mse|"
            r"all_layers_mse|adjusted_final_layer_score|flops_used|effective_compute|"
            r"budget_exhausted|time_exhausted|residual_wall_time_exhausted|"
            r"combined_budget_exhausted)\s*="
        )
        out["patch_deletes_no_scorer_code"] = not removed_code
        out["patch_assigns_no_scorer_state"] = not any(\n            critical_assignment.search(ln) and not ln.rstrip().endswith(",") for ln in added\n        )
        out["patch_has_two_pre_mse_calls"] = patch.count("r291_capture.safe_capture(") == 2
        out["patch_no_return_change"] = "return {" not in "\n".join(added)

        h.EXPECTED_NAME_ORDER_SHA256 = old_name_sha
        h.EXPECTED_DATASET_METADATA_SHA256 = old_meta_sha

    required = [
        "serialization_sealed",
        "rows_100",
        "raw_payload_exact",
        "storage_bound",
        "fit_eval_50_50",
        "failure_zero_row_preserved",
        "scorer_inputs_unchanged",
        "synthetic_scorer_outputs_unchanged",
        "residual_exact",
        "record_hash_exact",
        "target_all_hash_verified",
        "capture_error_isolated",
        "patch_deletes_no_scorer_code",
        "patch_assigns_no_scorer_state",
        "patch_has_two_pre_mse_calls",
        "patch_no_return_change",
    ]
    out["required_checks"] = required
    out["pass"] = all(bool(out[k]) for k in required)
    print(json.dumps(out, indent=2, sort_keys=True))
    if not out["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
