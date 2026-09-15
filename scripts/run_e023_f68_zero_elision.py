from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import urllib.request

import numpy as np
import pyarrow.parquet as pq
import flopscope as flops
import flopscope.numpy as fnp
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
MIN_SAVING = 6.60e8


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
    if source.count(old) != 1:
        raise RuntimeError(f"E023 patch mismatch for {label}: count={source.count(old)}")
    return source.replace(old, new, 1)


def _patch_candidate(source: str) -> str:
    # 1) Source-0 u/y columns are exact zeros; transport sources 1+ only for those two cols.
    old = "                Z_st = fnp.matmul(WDb, Z_st)\n"
    new = '''                # E023: residual rank columns transport normally; source-0 F68 u/y are exact zero.\n                Zm = fnp.matmul(WDb, Z_st[:, :, :r])\n                if Z_st.shape[0] > 1:\n                    Zfeed = fnp.matmul(WDb, Z_st[1:, :, r:])\n                    Zfeed = fnp.concatenate([fnp.zeros((1, n, 2), dtype=f32), Zfeed], axis=0)\n                else:\n                    Zfeed = fnp.zeros((1, n, 2), dtype=f32)\n                Z_st = fnp.concatenate([Zm, Zfeed], axis=2)\n'''
    source = _replace_once(source, old, new, "Z_st transport")

    # 2) The transported-y column has an identically zero static L factor and is absent from M.
    old = '        MP = fnp.einsum("kiq,kjq->kij", Z_st, L_st, out=bufs["mp"][:k])\n'
    new = '        MP = fnp.einsum("kiq,kjq->kij", Z_st[:, :, :rres + 1], L_st[:, :, :rres + 1], out=bufs["mp"][:k])\n'
    source = _replace_once(source, old, new, "MP zero-L column")

    # 3) Source 0 has c1=c2=y=u=w1sq=0, so run the F68 feed algebra only on sources 1+.
    old = '''        C1 = fnp.stack(c1_list, axis=0)                 # (k, n) static column scalings\n        C2 = fnp.stack(c2_list, axis=0)\n        Yk = Z_st[:, :, rres + 1]                        # (k, n) transported y = P(l) y\n        R = fnp.einsum("kij,kj->ki", AP, C1) + fnp.einsum("kij,kj->ki", PP, C2)\n        D3 = D3 + fnp.einsum("ki,ki->i", R, Yk)\n        if not need_d21:\n            return D3, None\n        fnp.multiply(P_st, fnp.reshape(C2, (k, 1, n)), out=MP)\n        fnp.multiply(A_st, fnp.reshape(C1, (k, 1, n)), out=T)\n        fnp.add(T, MP, out=T)\n        fnp.multiply(T, fnp.reshape(Yk * (2.0 / 3.0), (k, n, 1)), out=T)\n        fnp.add(LP, T, out=LP)\n'''
    new = '''        if k > 1:\n            C1_e23 = fnp.stack(c1_list[1:], axis=0)\n            C2_e23 = fnp.stack(c2_list[1:], axis=0)\n            Yk_e23 = Z_st[1:, :, rres + 1]\n            R_e23 = (fnp.einsum("kij,kj->ki", AP[1:], C1_e23)\n                     + fnp.einsum("kij,kj->ki", PP[1:], C2_e23))\n            D3 = D3 + fnp.einsum("ki,ki->i", R_e23, Yk_e23)\n        if not need_d21:\n            return D3, None\n        if k > 1:\n            fnp.multiply(P_st[1:], fnp.reshape(C2_e23, (k - 1, 1, n)), out=MP[1:])\n            fnp.multiply(A_st[1:], fnp.reshape(C1_e23, (k - 1, 1, n)), out=T[1:])\n            fnp.add(T[1:], MP[1:], out=T[1:])\n            fnp.multiply(T[1:], fnp.reshape(Yk_e23 * (2.0 / 3.0), (k - 1, n, 1)), out=T[1:])\n            fnp.add(LP[1:], T[1:], out=LP[1:])\n'''
    source = _replace_once(source, old, new, "source0 F68 feed")

    old = '            D21 = D21 + fnp.einsum("ki,kc->ic", R, Yk) * (1.0 / 3.0)\n'
    new = '''            if k > 1:\n                D21 = D21 + fnp.einsum("ki,kc->ic", R_e23, Yk_e23) * (1.0 / 3.0)\n'''
    source = _replace_once(source, old, new, "old-tier F68 outer")

    old = '''            D21 = (fnp.einsum("kij,kcj->ic", LA, A_st)\n                   + fnp.einsum("kij,kcj->ic", LP, P_st)\n                   + fnp.einsum("ki,kc->ic", R, Yk) * (1.0 / 3.0))\n'''
    new = '''            D21 = (fnp.einsum("kij,kcj->ic", LA, A_st)\n                   + fnp.einsum("kij,kcj->ic", LP, P_st))\n            if k > 1:\n                D21 = D21 + fnp.einsum("ki,kc->ic", R_e23, Yk_e23) * (1.0 / 3.0)\n'''
    source = _replace_once(source, old, new, "young-tier F68 outer")

    old = '''        PPL = fnp.einsum("kij,kjq->kiq", PP, L_st)\n        D21 = D21 + fnp.einsum("kiq,kcq->ic", PPL, Z_st) * (1.0 / 3.0)\n'''
    new = '''        PPL = fnp.einsum("kij,kjq->kiq", PP, L_st[:, :, :rres + 1])\n        D21 = D21 + fnp.einsum("kiq,kcq->ic", PPL, Z_st[:, :, :rres + 1]) * (1.0 / 3.0)\n'''
    source = _replace_once(source, old, new, "PPL zero-L column")
    return source


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
        with flops.BudgetContext(flop_budget=int(1e14), wall_time_limit_s=1200.0, quiet=True) as ctx:
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

    with tempfile.TemporaryDirectory(prefix="e023_") as td_s:
        td = Path(td_s)
        base_path = td / "v25_base.py"
        cand_path = td / "v25_e023.py"
        base_path.write_text(source, encoding="utf-8")
        cand_path.write_text(candidate_source, encoding="utf-8")
        base = _load_module(base_path, "e023_v25_base")
        cand = _load_module(cand_path, "e023_v25_candidate")

        row = _load_row0()
        b = _run(base, row, metered=True)
        c = _run(cand, row, metered=True)
        c2 = _run(cand, row, metered=False)

    diff = c["pred"] - b["pred"]
    max_abs = float(np.max(np.abs(diff)))
    rel_frob = float(np.linalg.norm(diff) / max(np.linalg.norm(b["pred"]), 1e-30))
    det = float(np.max(np.abs(c["pred"] - c2["pred"])))
    ratio = c["mse"] / b["mse"]
    saving = b["flops"] - c["flops"]
    projected_util = E007_UTIL - saving / BUDGET
    projected_adjusted = E007_RAW * projected_util
    residual_delta = c["residual_s"] - b["residual_s"]

    gates = {
        "max_abs_le_1e-7": max_abs <= 1e-7,
        "rel_frob_le_1e-7": rel_frob <= 1e-7,
        "mse_ratio_frozen_band": 0.999999 <= ratio <= 1.000001,
        "saving_ge_6.60e8": saving >= MIN_SAVING,
        "projected_util_le_0.3663677": projected_util <= 0.3663677,
        "projected_adjusted_lt_8.17e-09": projected_adjusted < TARGET,
        "residual_delta_le_5ms": residual_delta <= 0.005,
        "finite": b["finite"] and c["finite"],
        "deterministic": det == 0.0,
        "pinned_blob": blob == UPSTREAM_BLOB,
    }
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "baseline_mse": b["mse"],
        "candidate_mse": c["mse"],
        "mse_ratio": ratio,
        "max_abs_output_error": max_abs,
        "relative_frobenius_error": rel_frob,
        "baseline_flops": b["flops"],
        "candidate_flops": c["flops"],
        "saving_flops": saving,
        "baseline_residual_s": b["residual_s"],
        "candidate_residual_s": c["residual_s"],
        "residual_delta_s": residual_delta,
        "projected_utilization": projected_util,
        "projected_adjusted": projected_adjusted,
        "det_max_abs": det,
        "gates": gates,
        "decision": "GO" if all(gates.values()) else "NO-GO",
    }
    print("E023_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e023_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
