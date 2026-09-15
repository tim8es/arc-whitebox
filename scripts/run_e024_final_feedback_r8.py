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
import numpy as np
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from whestbench.domain import MLP

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
MAX_MSE_RATIO = 1.0004
MIN_SAVING = 9.0e8
MAX_PROJECTED_UTIL = 0.3662552
MAX_RESIDUAL = 0.350
MAX_RESIDUAL_DELTA = 0.005


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


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"E024 patch mismatch for {label}: count={count}")
    return source.replace(old, new, 1)


def _patch_candidate(source: str) -> str:
    # Only the final-layer V18 feedback carrier is narrowed. Earlier layers are untouched.
    old = '''                if Zf_st is not None:\n                    Zf_st = fnp.matmul(WDb, Zf_st)\n'''
    new = '''                if Zf_st is not None:\n                    if last and rfb == 16:\n                        # E024: preserve rank-16 history, evaluate final D3 with prefix rank 8.\n                        Zf_last = fnp.concatenate([Zf_st[:, :, :8], Zf_st[:, :, 16:24]], axis=2)\n                        Zf_st = fnp.matmul(WDb, Zf_last)\n                    else:\n                        Zf_st = fnp.matmul(WDb, Zf_st)\n'''
    source = _replace_once(source, old, new, "final Zf transport")

    old = '''                D3, D21 = self._dslices(A_st, P_st, Z_st, L_st, w2b_list, s_list, e_list,\n                                        c1_list, c2_list, y_list, n, bufs,\n                                        r, rfb, Zf_st, R1T_st, R2T_st,\n                                        need_d21=not trim,\n                                        ka=ka, FAo=FAo, FPo=FPo, Qc=Qc,\n                                        kb=kb, FA2=FA2, FP2=FP2, U2=U)\n'''
    new = '''                if last and rfb == 16:\n                    rfb_e024 = 8\n                    R1T_e024 = R1T_st[:, :, :8]\n                    R2T_e024 = R2T_st[:, :, :8]\n                else:\n                    rfb_e024 = rfb\n                    R1T_e024 = R1T_st\n                    R2T_e024 = R2T_st\n                D3, D21 = self._dslices(A_st, P_st, Z_st, L_st, w2b_list, s_list, e_list,\n                                        c1_list, c2_list, y_list, n, bufs,\n                                        r, rfb_e024, Zf_st, R1T_e024, R2T_e024,\n                                        need_d21=not trim,\n                                        ka=ka, FAo=FAo, FPo=FPo, Qc=Qc,\n                                        kb=kb, FA2=FA2, FP2=FP2, U2=U)\n'''
    return _replace_once(source, old, new, "final dslices feedback rank")


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


def main() -> None:
    raw = urllib.request.urlopen(RAW_URL, timeout=60).read()
    blob = _git_blob_sha(raw)
    if blob != UPSTREAM_BLOB:
        raise RuntimeError(f"pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")
    candidate_source = _patch_candidate(source)

    with tempfile.TemporaryDirectory(prefix="e024_") as td_s:
        td = Path(td_s)
        base_path = td / "v25_base.py"
        cand_path = td / "v25_e024.py"
        base_path.write_text(source, encoding="utf-8")
        cand_path.write_text(candidate_source, encoding="utf-8")
        base = _load_module(base_path, "e024_v25_base")
        cand = _load_module(cand_path, "e024_v25_candidate")

        row = _load_row0()
        if int(row["mlp_id"]) != 0:
            raise RuntimeError(f"frozen diagnostic expected mlp_id=0, got {row['mlp_id']}")
        baseline = _run(base, row, metered=True)
        candidate = _run(cand, row, metered=True)
        repeat = _run(cand, row, metered=False)

    diff = candidate["pred"] - baseline["pred"]
    max_abs = float(np.max(np.abs(diff)))
    rel_frob = float(np.linalg.norm(diff) / max(np.linalg.norm(baseline["pred"]), 1e-30))
    det = float(np.max(np.abs(candidate["pred"] - repeat["pred"])))
    ratio = candidate["mse"] / baseline["mse"]
    saving = baseline["flops"] - candidate["flops"]
    projected_util = E007_UTIL - saving / BUDGET
    projected_raw = E007_RAW * ratio
    projected_adjusted = projected_raw * projected_util
    residual_delta = candidate["residual_s"] - baseline["residual_s"]

    gates = {
        "pinned_blob": blob == UPSTREAM_BLOB,
        "finite": baseline["finite"] and candidate["finite"],
        "deterministic": det == 0.0,
        "mse_ratio_le_1.0004": ratio <= MAX_MSE_RATIO,
        "saving_ge_9.0e8": saving >= MIN_SAVING,
        "projected_util_le_0.3662552": projected_util <= MAX_PROJECTED_UTIL,
        "projected_adjusted_lt_8.17e-09": projected_adjusted < TARGET,
        "residual_delta_le_5ms": residual_delta <= MAX_RESIDUAL_DELTA,
        "candidate_residual_le_0.350": candidate["residual_s"] <= MAX_RESIDUAL,
    }
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "baseline_mse": baseline["mse"],
        "candidate_mse": candidate["mse"],
        "mse_ratio": ratio,
        "baseline_flops": baseline["flops"],
        "candidate_flops": candidate["flops"],
        "saving_flops": saving,
        "baseline_residual_s": baseline["residual_s"],
        "candidate_residual_s": candidate["residual_s"],
        "residual_delta_s": residual_delta,
        "max_abs_output_difference": max_abs,
        "relative_frobenius_difference": rel_frob,
        "det_max_abs": det,
        "projected_utilization": projected_util,
        "projected_raw": projected_raw,
        "projected_adjusted": projected_adjusted,
        "gates": gates,
        "decision": "GO" if all(gates.values()) else "NO-GO",
    }
    print("E024_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e024_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
