#!/usr/bin/env python3
"""R299 offline analyzer supplement for a future sealed R291/R288 V25 residual capture.

Standard-library only. The CLI has no contract-override switch: production analysis is
pinned to the R288/R291 capture contract. Tests may inject a synthetic Contract object
through the Python API, but the command-line path always uses PRODUCTION_CONTRACT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROWS = 100
WIDTH = 1024
F32_BYTES = 4
VECTOR_BYTES = WIDTH * F32_BYTES
RECORD_BYTES = 3 * VECTOR_BYTES
RAW_PAYLOAD_BYTES = ROWS * RECORD_BYTES

CAPTURE_SCHEMA = "arc.whitebox.r291.capture.v1"
PANEL_SCHEMA = "arc.whitebox.r291.expected_public_mini100.v1"
EXPECTED_NAME_ORDER_SHA256 = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
EXPECTED_DATASET_METADATA_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"

PINNED = {
    "v25_source_commit": "dff3dd65e9d2210e02418cca99e05556f6bf2c75",
    "v25_source_blob_sha1": "195373a110215256b759d7c172ba8c923c62e5cc",
    "python": "3.11.16",
    "whestbench": "0.16.1",
    "whestbench_source_commit": "4d08668b485c8a7d25a105c3c00d2f4fc2538f18",
    "whestbench_scoring_blob_sha1": "9cf7653a0267c4d048617c9045ac8be127f3c8bf",
    "flopscope": "0.12.1",
    "flopscope_source_commit": "b599f015b0bc005b1edb6d7a1b10e0814675e693",
    "numpy": "2.4.6",
    "dataset_repo": "aicrowd/arc-whestbench-public-2026",
    "dataset_revision": "v2-phase2",
    "dataset_split": "mini",
}

ARITHMETIC_SUPPLEMENT = {
    "status": "PRE_DATA_DETERMINISTIC_SUPPLEMENT_TO_R278",
    "reason": (
        "R278 fixes the split and algebraic rule but not floating-point accumulation/"
        "rounding for the offline diagnostic. This supplement is frozen before any real "
        "capture is inspected and is not an official WhestBench score definition."
    ),
    "vector_ops": (
        "Decode canonical <f4. Verify stored residual as binary32(target-pred). "
        "Fit each d coordinate as binary32(math.fsum(50 decoded FIT residuals)/50). "
        "Form corrected prediction as binary32(pred+d) and corrected residual as "
        "binary32(target-corrected_pred)."
    ),
    "mse": "math.fsum(decoded_binary32_residual**2)/1024 in Python binary64",
    "paired_summary": (
        "gain=baseline_mse-corrected_mse; mean via math.fsum/n; sample SD with n-1 "
        "denominator; SE=SD/sqrt(n); median via statistics.median"
    ),
    "failure_semantics": (
        "Failure rows are never dropped or reassigned. A row is failure-zeroed iff "
        "error_code is non-null/non-empty or any frozen failure flag is true; manifest "
        "scored_prediction_zeroed must equal that predicate and its prediction bytes "
        "must be all zero."
    ),
}

ENERGY_SUPPLEMENT = {
    "status": "PRE_DATA_R278_COORDINATE_ENERGY_SUPPLEMENT",
    "formula": {
        "B_k": "math.fsum(r_ik**2 for EVAL i)",
        "C_k": "math.fsum(binary32(r_ik-d_k)**2 for EVAL i)",
        "explained_k": "1-C_k/B_k when B_k>0; null when B_k==0",
        "weighted_global_fraction": "1-sum_k(C_k)/sum_k(B_k) when sum_k(B_k)>0; null otherwise",
    },
    "zero_energy_semantics": (
        "B_k==0 makes the coordinate ratio undefined, so explained_k is JSON null and "
        "the coordinate is excluded from finite-coordinate quantiles/count. Its C_k is "
        "still included in the weighted global numerator, so adding error to a zero-energy "
        "coordinate is not hidden."
    ),
    "quantiles": {
        "probabilities": [0.10, 0.25, 0.50, 0.75, 0.90],
        "population": "finite explained_k values only (equivalently B_k>0 after finite checks)",
        "convention": (
            "Hyndman-Fan type 7 / linear interpolation: sort x; h=(n-1)p; "
            "j=floor(h); gamma=h-j; Q(p)=x[j]+gamma*(x[j+1]-x[j]), "
            "with the exact endpoint when j=n-1; zero-based indexing"
        ),
    },
    "arithmetic": (
        "Use the R298 decoded canonical binary32 residuals and binary32 fitted d. "
        "For C_k only, r_ik-d_k is rounded to binary32 before squaring; sums and "
        "ratios use Python binary64 math.fsum. This freezes the coordinate diagnostic "
        "before any real capture is inspected."
    ),
}



class AnalyzerError(RuntimeError):
    pass


@dataclass(frozen=True)
class Contract:
    name_order_sha256: str
    dataset_metadata_sha256: str
    pinned: dict[str, str]


PRODUCTION_CONTRACT = Contract(
    EXPECTED_NAME_ORDER_SHA256, EXPECTED_DATASET_METADATA_SHA256, PINNED
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalyzerError(message)


def _require_sha256(value: Any, label: str) -> str:
    _require(isinstance(value, str) and len(value) == 64, f"{label}: expected 64 hex chars")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise AnalyzerError(f"{label}: not hex") from exc
    return value.lower()


def _name_order_sha(names: list[str]) -> str:
    return _sha(json.dumps(names, separators=(",", ":")).encode("utf-8"))


def _f32(value: float) -> float:
    _require(math.isfinite(value), "non-finite arithmetic value")
    try:
        out = struct.unpack("<f", struct.pack("<f", value))[0]
    except (OverflowError, struct.error) as exc:
        raise AnalyzerError("binary32 overflow") from exc
    _require(math.isfinite(out), "non-finite binary32 arithmetic value")
    return out


def _decode_f32(raw: bytes) -> list[float]:
    _require(len(raw) == VECTOR_BYTES, "vector byte length mismatch")
    vals = [x[0] for x in struct.iter_unpack("<f", raw)]
    _require(all(math.isfinite(x) for x in vals), "non-finite vector value")
    return vals


def _residual_bytes(target: bytes, pred: bytes) -> bytes:
    _require(len(target) == VECTOR_BYTES and len(pred) == VECTOR_BYTES, "residual vector size mismatch")
    out = bytearray(VECTOR_BYTES)
    for i, ((t,), (p,)) in enumerate(zip(struct.iter_unpack("<f", target), struct.iter_unpack("<f", pred))):
        _require(math.isfinite(t) and math.isfinite(p), "non-finite vector value")
        struct.pack_into("<f", out, i * F32_BYTES, _f32(t - p))
    return bytes(out)


def _strict_sums(raw: bytes) -> dict[str, str]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise AnalyzerError("SHA256SUMS is not ASCII") from exc
    lines = text.splitlines()
    _require(len(lines) == 2, "SHA256SUMS must contain exactly two lines")
    out: dict[str, str] = {}
    for line in lines:
        parts = line.split("  ")
        _require(len(parts) == 2, "SHA256SUMS line must use two-space separator")
        digest, name = parts
        _require(name in {"vectors.f32le", "manifest.json"}, f"unexpected SHA256SUMS path: {name}")
        _require(name not in out, f"duplicate SHA256SUMS path: {name}")
        out[name] = _require_sha256(digest, f"SHA256SUMS {name}")
    _require(set(out) == {"vectors.f32le", "manifest.json"}, "SHA256SUMS file set mismatch")
    return out


def _load_panel(path: Path, contract: Contract) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        panel = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalyzerError("expected panel is not valid UTF-8 JSON") from exc
    _require(panel.get("schema") == PANEL_SCHEMA, "expected-panel schema mismatch")
    records = panel.get("records")
    _require(isinstance(records, list) and len(records) == ROWS, "expected panel must have exactly 100 rows")
    source = panel.get("source") or {}
    ds = source.get("dataset") or {}
    canon = source.get("canonicalization") or {}
    _require(ds.get("count") == ROWS, "expected-panel dataset count mismatch")
    _require(ds.get("metadata_sha256") == contract.dataset_metadata_sha256, "expected-panel dataset metadata hash mismatch")
    _require(ds.get("target_dtype") == "float32", "expected-panel target dtype mismatch")
    _require(ds.get("target_shape") == [16, WIDTH], "expected-panel target shape mismatch")
    _require(canon.get("name_order_sha256") == contract.name_order_sha256, "expected-panel declared name/order hash mismatch")
    _require(canon.get("network_id") == "decimal exact int64 mlp_seed", "expected-panel network_id rule mismatch")
    names = [str(r.get("mlp_name")) for r in records]
    _require(_name_order_sha(names) == contract.name_order_sha256, "expected-panel actual name/order hash mismatch")
    ids = [str(r.get("network_id")) for r in records]
    _require(len(set(ids)) == ROWS, "expected-panel duplicate network_id")
    for idx, row in enumerate(records):
        _require(row.get("scorer_mlp_index") == idx, f"expected-panel scorer index mismatch at {idx}")
        _require_sha256(row.get("r224_target_all_sha256"), f"expected-panel target hash row {idx}")
    return panel, raw


def _validate_manifest(manifest: dict[str, Any], panel: dict[str, Any], panel_raw: bytes,
                       vectors: bytes, contract: Contract) -> list[dict[str, Any]]:
    _require(manifest.get("schema") == CAPTURE_SCHEMA, "manifest schema mismatch")
    _require(manifest.get("status") == "SEALED", "manifest is not SEALED")
    _require(manifest.get("rows") == ROWS, "manifest row count mismatch")
    _require(manifest.get("dtype") == "<f4", "manifest dtype mismatch")
    _require(manifest.get("vector_shape") == [WIDTH], "manifest vector shape mismatch")
    _require(manifest.get("axis1") == ["final_pred", "final_target", "residual_target_minus_pred"], "manifest axis order mismatch")
    _require(manifest.get("residual_sign") == "final_target - final_pred", "manifest residual sign mismatch")
    _require(manifest.get("raw_payload_bytes") == RAW_PAYLOAD_BYTES, "manifest raw payload byte count mismatch")
    _require(manifest.get("vectors_sha256") == _sha(vectors), "manifest vectors hash mismatch")
    _require(manifest.get("expected_name_order_sha256") == contract.name_order_sha256, "manifest name/order hash mismatch")
    _require(manifest.get("dataset_metadata_sha256") == contract.dataset_metadata_sha256, "manifest dataset metadata hash mismatch")
    _require(manifest.get("expected_panel_sha256") == _sha(panel_raw), "manifest expected-panel hash mismatch")
    _require(manifest.get("pinned") == contract.pinned, "manifest pinned provenance mismatch")
    rule = manifest.get("frozen_rule") or {}
    _require(rule.get("split") == "sort decimal network_id strings lexicographically; first 50 FIT, last 50 EVAL", "manifest split rule mismatch")
    _require(rule.get("fit") == "d = mean_FIT(target_final - v25_pred_final)", "manifest fit rule mismatch")
    _require(rule.get("eval") == "pred_corrected = pred + d on EVAL only", "manifest eval rule mismatch")
    _require(rule.get("per_network_tuning") is False, "manifest per-network tuning flag mismatch")

    rows = manifest.get("records")
    _require(isinstance(rows, list) and len(rows) == ROWS, "manifest must have exactly 100 records")
    expected = panel["records"]
    ids = [str(r.get("network_id")) for r in rows]
    _require(len(set(ids)) == ROWS, "manifest duplicate network_id")
    names = [str(r.get("mlp_name")) for r in rows]
    _require(_name_order_sha(names) == contract.name_order_sha256, "manifest actual name/order hash mismatch")
    sorted_ids = sorted(ids)
    fit = set(sorted_ids[:50])

    for idx, row in enumerate(rows):
        exp = expected[idx]
        _require(row.get("scorer_mlp_index") == idx, f"scorer index mismatch at row {idx}")
        _require(str(row.get("mlp_name")) == str(exp["mlp_name"]), f"mlp_name mismatch at row {idx}")
        _require(str(row.get("network_id")) == str(exp["network_id"]), f"network_id mismatch at row {idx}")
        expected_role = "FIT" if str(row["network_id"]) in fit else "EVAL"
        _require(row.get("split_role") == expected_role, f"split_role mismatch at row {idx}")
        exp_target = _require_sha256(exp.get("r224_target_all_sha256"), f"panel target hash row {idx}")
        _require(row.get("r224_target_all_sha256_expected") == exp_target, f"expected target fingerprint mismatch at row {idx}")
        _require(row.get("r224_target_all_sha256_observed") == exp_target, f"observed target fingerprint mismatch at row {idx}")
        _require(row.get("payload_offset_bytes") == idx * RECORD_BYTES, f"payload offset mismatch at row {idx}")
        for key in ("budget_exhausted", "time_exhausted", "residual_wall_time_exhausted",
                    "combined_budget_exhausted", "scored_prediction_zeroed"):
            _require(type(row.get(key)) is bool, f"{key} must be boolean at row {idx}")
        error_code = row.get("error_code")
        _require(error_code is None or (isinstance(error_code, str) and bool(error_code)), f"invalid error_code at row {idx}")
        expected_zeroed = bool(error_code) or any(row[k] for k in (
            "budget_exhausted", "time_exhausted", "residual_wall_time_exhausted",
            "combined_budget_exhausted"))
        _require(row["scored_prediction_zeroed"] == expected_zeroed, f"failure flag/zeroed mismatch at row {idx}")
    return rows


def _vectors_and_mses(vectors: bytes, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[list[float]], list[list[float]], list[list[float]]]:
    decoded_pred: list[list[float]] = []
    decoded_target: list[list[float]] = []
    decoded_resid: list[list[float]] = []
    baseline: list[dict[str, Any]] = []
    zero = b"\x00" * VECTOR_BYTES
    for idx, row in enumerate(rows):
        off = idx * RECORD_BYTES
        pred = vectors[off:off + VECTOR_BYTES]
        target = vectors[off + VECTOR_BYTES:off + 2 * VECTOR_BYTES]
        resid = vectors[off + 2 * VECTOR_BYTES:off + 3 * VECTOR_BYTES]
        _require(_sha(pred) == row.get("final_pred_sha256"), f"prediction hash mismatch at row {idx}")
        _require(_sha(target) == row.get("final_target_sha256"), f"target hash mismatch at row {idx}")
        _require(_sha(resid) == row.get("residual_sha256"), f"residual hash mismatch at row {idx}")
        _require(_sha(pred + target + resid) == row.get("record_payload_sha256"), f"record payload hash mismatch at row {idx}")
        _require(resid == _residual_bytes(target, pred), f"residual bytes mismatch at row {idx}")
        if row["scored_prediction_zeroed"]:
            _require(pred == zero, f"failure row prediction is not zero at row {idx}")
        pv, tv, rv = _decode_f32(pred), _decode_f32(target), _decode_f32(resid)
        decoded_pred.append(pv); decoded_target.append(tv); decoded_resid.append(rv)
        mse = math.fsum(x * x for x in rv) / WIDTH
        _require(math.isfinite(mse), f"non-finite baseline MSE at row {idx}")
        baseline.append({"network_id": str(row["network_id"]), "mlp_name": str(row["mlp_name"]),
                         "split_role": row["split_role"], "baseline_mse": mse})
    return baseline, decoded_pred, decoded_target, decoded_resid


def _mean(values: list[float]) -> float:
    _require(bool(values), "empty mean")
    return math.fsum(values) / len(values)


def _sample_sd(values: list[float], mean: float) -> float:
    _require(len(values) > 1, "sample SD requires at least two values")
    return math.sqrt(math.fsum((x - mean) ** 2 for x in values) / (len(values) - 1))


def _quantile_type7(values: list[float], p: float) -> float | None:
    _require(0.0 <= p <= 1.0, "quantile probability outside [0,1]")
    if not values:
        return None
    _require(all(math.isfinite(x) for x in values), "non-finite quantile input")
    ordered = sorted(values)
    h = (len(ordered) - 1) * p
    lo = math.floor(h)
    hi = math.ceil(h)
    if lo == hi:
        return ordered[lo]
    gamma = h - lo
    return ordered[lo] + gamma * (ordered[hi] - ordered[lo])


def _coordinate_energy_summary(
    residuals: list[list[float]], eval_idx: list[int], d: list[float]
) -> dict[str, Any]:
    _require(bool(eval_idx), "coordinate energy requires EVAL rows")
    _require(len(d) == WIDTH, "coordinate energy d width mismatch")
    _require(all(len(residuals[i]) == WIDTH for i in eval_idx), "coordinate energy residual width mismatch")
    coordinates: list[dict[str, Any]] = []
    finite_explained: list[float] = []
    b_values: list[float] = []
    c_values: list[float] = []
    zero_energy_count = 0
    negative_explained_count = 0
    for k in range(WIDTH):
        b_k = math.fsum(residuals[i][k] ** 2 for i in eval_idx)
        corrected = [_f32(residuals[i][k] - d[k]) for i in eval_idx]
        c_k = math.fsum(x * x for x in corrected)
        _require(math.isfinite(b_k) and b_k >= 0.0, f"invalid B_k at coordinate {k}")
        _require(math.isfinite(c_k) and c_k >= 0.0, f"invalid C_k at coordinate {k}")
        if b_k == 0.0:
            explained = None
            zero_energy_count += 1
        else:
            explained = 1.0 - (c_k / b_k)
            _require(math.isfinite(explained), f"non-finite explained fraction at coordinate {k}")
            finite_explained.append(explained)
            if explained < 0.0:
                negative_explained_count += 1
        b_values.append(b_k)
        c_values.append(c_k)
        coordinates.append({
            "coordinate": k,
            "B_k": b_k,
            "C_k": c_k,
            "explained_fraction": explained,
        })
    total_b = math.fsum(b_values)
    total_c = math.fsum(c_values)
    _require(math.isfinite(total_b) and math.isfinite(total_c), "non-finite global coordinate energy")
    weighted = None if total_b == 0.0 else 1.0 - (total_c / total_b)
    if weighted is not None:
        _require(math.isfinite(weighted), "non-finite weighted global energy fraction")
    probs = (0.10, 0.25, 0.50, 0.75, 0.90)
    return {
        "definition": ENERGY_SUPPLEMENT,
        "eval_rows": len(eval_idx),
        "coordinate_count": WIDTH,
        "finite_coordinate_count": len(finite_explained),
        "zero_energy_coordinate_count": zero_energy_count,
        "negative_explained_coordinate_count": negative_explained_count,
        "sum_B": total_b,
        "sum_C": total_c,
        "weighted_global_explained_fraction": weighted,
        "central_quantiles_type7": {
            f"p{int(p * 100):02d}": _quantile_type7(finite_explained, p) for p in probs
        },
        "coordinates": coordinates,
    }


def analyze_capture(capture_dir: Path, expected_panel: Path,
                    contract: Contract = PRODUCTION_CONTRACT) -> dict[str, Any]:
    root = Path(capture_dir)
    required = {"vectors.f32le", "manifest.json", "SHA256SUMS"}
    _require(root.is_dir(), "capture path is not a directory")
    present = {p.name for p in root.iterdir() if p.is_file()}
    _require(required <= present, "capture is missing required sealed files")
    vectors = (root / "vectors.f32le").read_bytes()
    manifest_raw = (root / "manifest.json").read_bytes()
    sums_raw = (root / "SHA256SUMS").read_bytes()
    _require(len(vectors) == RAW_PAYLOAD_BYTES, f"vectors.f32le must be exactly {RAW_PAYLOAD_BYTES} bytes")
    sums = _strict_sums(sums_raw)
    _require(sums["vectors.f32le"] == _sha(vectors), "SHA256SUMS vectors hash mismatch")
    _require(sums["manifest.json"] == _sha(manifest_raw), "SHA256SUMS manifest hash mismatch")
    try:
        manifest = json.loads(manifest_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalyzerError("manifest is not valid UTF-8 JSON") from exc
    panel, panel_raw = _load_panel(Path(expected_panel), contract)
    rows = _validate_manifest(manifest, panel, panel_raw, vectors, contract)
    baseline_rows, preds, targets, residuals = _vectors_and_mses(vectors, rows)

    fit_idx = [i for i, r in enumerate(rows) if r["split_role"] == "FIT"]
    eval_idx = [i for i, r in enumerate(rows) if r["split_role"] == "EVAL"]
    _require(len(fit_idx) == 50 and len(eval_idx) == 50, "split is not exactly 50 FIT / 50 EVAL")
    d = [_f32(math.fsum(residuals[i][k] for i in fit_idx) / len(fit_idx)) for k in range(WIDTH)]

    per_network: list[dict[str, Any]] = []
    gains: list[float] = []
    base_eval: list[float] = []
    corrected_eval: list[float] = []
    for i in eval_idx:
        corrected_pred = [_f32(preds[i][k] + d[k]) for k in range(WIDTH)]
        corrected_resid = [_f32(targets[i][k] - corrected_pred[k]) for k in range(WIDTH)]
        corrected_mse = math.fsum(x * x for x in corrected_resid) / WIDTH
        base_mse = baseline_rows[i]["baseline_mse"]
        _require(math.isfinite(corrected_mse), f"non-finite corrected MSE at row {i}")
        gain = base_mse - corrected_mse
        base_eval.append(base_mse); corrected_eval.append(corrected_mse); gains.append(gain)
        per_network.append({
            "scorer_mlp_index": i,
            "network_id": baseline_rows[i]["network_id"],
            "mlp_name": baseline_rows[i]["mlp_name"],
            "scored_prediction_zeroed": rows[i]["scored_prediction_zeroed"],
            "baseline_mse": base_mse,
            "corrected_mse": corrected_mse,
            "paired_mse_gain": gain,
            "improved": gain > 0.0,
        })

    base_mean = _mean(base_eval); corr_mean = _mean(corrected_eval); gain_mean = _mean(gains)
    sd = _sample_sd(gains, gain_mean); se = sd / math.sqrt(len(gains))
    improved = sum(g > 0.0 for g in gains)
    base_median = statistics.median(base_eval); corr_median = statistics.median(corrected_eval)
    pct = (base_mean - corr_mean) / base_mean if base_mean > 0.0 else None
    gates = {
        "eval_mean_raw_mse_improves_at_least_2pct": pct is not None and pct >= 0.02,
        "at_least_30_of_50_eval_networks_improve": improved >= 30,
        "mean_paired_mse_gain_gt_2_descriptive_se": gain_mean > 2.0 * se,
        "median_eval_raw_mse_improves": corr_median < base_median,
    }
    coordinate_energy = _coordinate_energy_summary(residuals, eval_idx, d)
    return {
        "schema": "arc.whitebox.r299.capture_analysis.v1",
        "classification": "OFFLINE_DIAGNOSTIC_ONLY_NOT_OFFICIAL_ADJUSTED_SCORE",
        "capture_integrity": {
            "vectors_sha256": _sha(vectors),
            "manifest_sha256": _sha(manifest_raw),
            "sha256sums_sha256": _sha(sums_raw),
            "expected_panel_sha256": _sha(panel_raw),
            "rows": ROWS,
            "fit_rows": len(fit_idx),
            "eval_rows": len(eval_idx),
        },
        "frozen_rule": {
            "split": "lexicographic decimal network_id; first 50 FIT, last 50 EVAL",
            "fit": "d = mean_FIT(target-pred)",
            "eval": "p_corrected = p + d on EVAL only",
            "no_alpha_rank_sign_or_network_tuning": True,
        },
        "arithmetic_supplement": ARITHMETIC_SUPPLEMENT,
        "fit_correction": {"dtype": "<f4", "shape": [WIDTH], "sha256": _sha(b"".join(struct.pack("<f", x) for x in d))},
        "eval_summary": {
            "baseline_mean_mse": base_mean,
            "corrected_mean_mse": corr_mean,
            "relative_mean_mse_improvement": pct,
            "paired_mean_mse_gain": gain_mean,
            "paired_sample_sd": sd,
            "paired_se": se,
            "improved_count": improved,
            "improved_fraction": improved / len(gains),
            "baseline_median_mse": base_median,
            "corrected_median_mse": corr_median,
        },
        "coordinate_residual_energy": coordinate_energy,
        "materiality_gates": gates,
        "all_four_materiality_gates_pass": all(gates.values()),
        "per_network_eval": per_network,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-dir", type=Path, required=True)
    ap.add_argument("--expected-panel", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = analyze_capture(args.capture_dir, args.expected_panel)
    except (AnalyzerError, OSError) as exc:
        raise SystemExit(f"R299 analyzer error: {exc}") from exc
    print(_canonical_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
