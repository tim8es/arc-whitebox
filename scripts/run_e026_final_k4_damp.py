from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import urllib.request

import flopscope as flops
import flopscope.numpy as fnp
from huggingface_hub import hf_hub_download
import numpy as np
import pyarrow.parquet as pq
from whestbench.domain import MLP

from methods.e026_final_k4_damp import FINAL_K4_DAMP, patch_v25_source

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
UPSTREAM_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
RAW_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/estimators/estimator_v25.py"
)
DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
BUDGET = 2**41
E007_RAW = 2.23e-8
E007_UTIL = 0.36666448
TARGET = 8.17e-9
MSE_RATIO_GATE = 0.99919
UTIL_GATE = 0.3666655
FLOP_DELTA_GATE = 1.0e7
RESIDUAL_DELTA_GATE = 0.005
RESIDUAL_CAP = 0.400


class _Ctx:
    seed = 0


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to construct module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_row0() -> dict:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    return pq.read_table(path).slice(0, 1).to_pylist()[0]


def _make_mlp(row: dict) -> tuple[MLP, np.ndarray]:
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(16, 1024, 1024)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(1024)
    ws = [fnp.asarray(w) for w in weights]
    return MLP(width=1024, depth=16, weights=ws, seed=0), gt


def _run(module, row: dict, *, metered: bool) -> dict:
    mlp, gt = _make_mlp(row)
    est = module.Estimator()
    est.setup(_Ctx())
    t0 = time.perf_counter()
    if metered:
        with flops.BudgetContext(
            flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True
        ) as ctx:
            pred = est.predict(mlp, BUDGET)
            used = float(ctx.flops_used)
        residual = float(ctx.residual_wall_time_s)
    else:
        pred = est.predict(mlp, BUDGET)
        used = float("nan")
        residual = float("nan")
    wall = time.perf_counter() - t0
    p = np.asarray(pred, dtype=np.float64)
    return {
        "pred": p,
        "mse": float(np.mean((p[-1] - gt) ** 2)),
        "flops": used,
        "residual_s": residual,
        "wall_s": wall,
        "finite": bool(np.isfinite(p).all()),
    }


def _patch_scope_ok(source: str, candidate_source: str) -> bool:
    source_lines = source.splitlines()
    candidate_lines = candidate_source.splitlines()
    if len(source_lines) != len(candidate_lines):
        return False
    changed = [
        (a, b) for a, b in zip(source_lines, candidate_lines, strict=True) if a != b
    ]
    return changed == [
        (
            "                    g4row = dG * METRIC_C",
            "                    g4row = dG * METRIC_C * (0.95 if last else 1.0)",
        )
    ]


def main() -> None:
    raw = urllib.request.urlopen(RAW_URL, timeout=60).read()
    blob = _git_blob_sha(raw)
    if blob != UPSTREAM_BLOB:
        raise RuntimeError(f"pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")
    candidate_source = patch_v25_source(source)
    scope_ok = _patch_scope_ok(source, candidate_source)

    with tempfile.TemporaryDirectory(prefix="e026_") as td_s:
        td = Path(td_s)
        base_path = td / "v25_base.py"
        cand_path = td / "v25_e026.py"
        base_path.write_text(source, encoding="utf-8")
        cand_path.write_text(candidate_source, encoding="utf-8")
        base = _load_module(base_path, "e026_v25_base")
        cand = _load_module(cand_path, "e026_v25_candidate")

        row = _load_row0()
        baseline = _run(base, row, metered=True)
        candidate = _run(cand, row, metered=True)
        candidate_repeat = _run(cand, row, metered=False)

    diff = candidate["pred"] - baseline["pred"]
    max_abs = float(np.max(np.abs(diff)))
    det_max_abs = float(
        np.max(np.abs(candidate["pred"] - candidate_repeat["pred"]))
    )
    mse_ratio = candidate["mse"] / baseline["mse"]
    flop_delta = candidate["flops"] - baseline["flops"]
    projected_util = E007_UTIL + flop_delta / BUDGET
    projected_adjusted = E007_RAW * mse_ratio * projected_util
    residual_delta = candidate["residual_s"] - baseline["residual_s"]

    gates = {
        "mse_ratio_le_0.99919": mse_ratio <= MSE_RATIO_GATE,
        "projected_adjusted_lt_8.17e-09": projected_adjusted < TARGET,
        "projected_util_le_0.3666655": projected_util <= UTIL_GATE,
        "flop_delta_le_1e7": flop_delta <= FLOP_DELTA_GATE,
        "residual_delta_le_5ms": residual_delta <= RESIDUAL_DELTA_GATE,
        "candidate_residual_lt_0.400s": candidate["residual_s"] < RESIDUAL_CAP,
        "finite": baseline["finite"] and candidate["finite"],
        "deterministic": det_max_abs == 0.0,
        "patch_scope": scope_ok,
        "pinned_blob": blob == UPSTREAM_BLOB,
        "frozen_damp_0.95": FINAL_K4_DAMP == 0.95,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "damping": FINAL_K4_DAMP,
        "baseline_mse": baseline["mse"],
        "candidate_mse": candidate["mse"],
        "mse_ratio": mse_ratio,
        "max_abs_output_difference": max_abs,
        "baseline_flops": baseline["flops"],
        "candidate_flops": candidate["flops"],
        "flop_delta": flop_delta,
        "baseline_residual_s": baseline["residual_s"],
        "candidate_residual_s": candidate["residual_s"],
        "residual_delta_s": residual_delta,
        "baseline_wall_s": baseline["wall_s"],
        "candidate_wall_s": candidate["wall_s"],
        "det_max_abs": det_max_abs,
        "projected_utilization": projected_util,
        "projected_adjusted": projected_adjusted,
        "scope_ok": scope_ok,
        "pinned_blob": blob,
        "gates": gates,
        "decision": decision,
    }
    print("E026_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e026_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
