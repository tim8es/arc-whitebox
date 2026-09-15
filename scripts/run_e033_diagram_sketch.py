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

from methods.e033_diagram_sketch import best_symmetric_rank_capture, offdiag

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
LEAN_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/lean/lean_k3_aug.py"
)
EXPECTED_LEAN_BLOB = "8fdaa96fd68f30ce9020e6534626e97ebf71d291"
DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
N = 1024
BUDGET = 2**41
RAW_GATE = 1.89e-8
UTIL_GATE = 0.14
ADJUSTED_GATE = 2.646e-9
RANK4 = 32
SOURCE_PROBES = 4
NON_SOURCE_UTIL = 0.095
SCORED_LAYERS = tuple(range(8, 15))
LAM_BASE = np.asarray(
    [
        4.9895e-03,
        8.0876e-03,
        9.8291e-03,
        1.0549e-02,
        1.0851e-02,
        1.0828e-02,
        1.0589e-02,
        1.0048e-02,
        9.6483e-03,
        9.1720e-03,
        8.7730e-03,
        8.3938e-03,
        8.0555e-03,
        7.6770e-03,
        7.2588e-03,
        7.2588e-03,
    ],
    dtype=np.float64,
) * 0.95
REF_R = np.asarray(
    [
        6.58815e-03,
        8.18414e-03,
        8.53136e-03,
        8.38859e-03,
        8.10153e-03,
        7.74287e-03,
        7.35951e-03,
        6.91093e-03,
        6.55752e-03,
        6.17892e-03,
        5.83953e-03,
        5.56824e-03,
        5.32459e-03,
        5.05165e-03,
        4.77181e-03,
    ],
    dtype=np.float64,
)


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324


def _instrument_source(source: str) -> str:
    sig = '                    age_rank=None, age_eig="exact"):'
    if sig not in source:
        raise RuntimeError("lean signature marker not found")
    source = source.replace(
        sig,
        '                    age_rank=None, age_eig="exact", pre_g_hook=None):',
        1,
    )
    marker = (
        "            else:\n"
        "                G = W @ G @ W.T\n"
        "                G = 0.5 * (G + G.T)\n"
    )
    if marker not in source:
        raise RuntimeError("dense K4 transport marker not found")
    replacement = marker + (
        "            if pre_g_hook is not None:\n"
        "                G = pre_g_hook(l, G, C)\n"
    )
    return source.replace(marker, replacement, 1)


def _load_lean_module():
    with urllib.request.urlopen(LEAN_URL, timeout=30) as response:  # noqa: S310
        data = response.read()
    blob = _git_blob_sha(data)
    if blob != EXPECTED_LEAN_BLOB:
        raise RuntimeError(f"lean blob mismatch: {blob} != {EXPECTED_LEAN_BLOB}")
    patched = _instrument_source(data.decode("utf-8"))
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    try:
        temp.write(patched)
        temp.close()
        spec = importlib.util.spec_from_file_location("e033_lean_k3_aug", temp.name)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import patched lean module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.torch.set_num_threads(2)
        return module, blob
    finally:
        Path(temp.name).unlink(missing_ok=True)


def _load_row0() -> tuple[np.ndarray, np.ndarray, int]:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    row = pq.read_table(path).slice(0, 1).to_pylist()[0]
    weights = np.asarray(row["weights"], dtype=np.float64).reshape(16, N, N)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(N)
    return weights, gt, int(row["mlp_id"])


def _lambda_for_pre_layer(layer: int, dg: np.ndarray, var: np.ndarray) -> float:
    if layer <= 0:
        return 0.0
    idx = min(layer - 1, len(REF_R) - 1)
    mean_var = float(np.mean(var, dtype=np.float64))
    rr = float(np.mean(dg, dtype=np.float64)) / mean_var
    scale = float(np.clip(rr / REF_R[idx], 0.5, 2.0))
    return float(LAM_BASE[min(layer - 1, len(LAM_BASE) - 1)] * scale)


class CaptureHook:
    def __init__(self):
        self.rows: list[dict] = []

    def __call__(self, layer, g, c):
        if layer not in SCORED_LAYERS:
            return g
        g_np = np.asarray(g.detach().cpu().numpy(), dtype=np.float64)
        c_np = np.asarray(c.detach().cpu().numpy(), dtype=np.float64)
        dg = np.diag(g_np).copy()
        var = np.diag(c_np).copy()
        lam = _lambda_for_pre_layer(layer, dg, var)
        residual = offdiag(g_np) - lam * offdiag(c_np)
        capture = best_symmetric_rank_capture(residual, RANK4)
        self.rows.append(
            {
                "layer": int(layer),
                "lambda": float(lam),
                "rank32_energy_capture": float(capture),
            }
        )
        return g


class NoopHook:
    def __call__(self, layer, g, c):
        del layer, c
        return g


def _run_oracle(module, weights: np.ndarray, statics, hook):
    out = module.lean_k3_predict(
        weights,
        statics=statics,
        k4_aug=True,
        pre_g_hook=hook,
    )
    return np.asarray(out.detach().cpu().numpy(), dtype=np.float64)


def _proxy_once() -> tuple[int, float]:
    rng = np.random.default_rng(33033)
    w = fnp.asarray(rng.standard_normal((N, N), dtype=np.float32))
    state = fnp.asarray(rng.standard_normal((N, RANK4 + SOURCE_PROBES), dtype=np.float32))
    with flops.BudgetContext(
        flop_budget=20_000_000_000,
        wall_time_limit_s=60.0,
        quiet=True,
    ) as ctx:
        for _ in range(16):
            state = w @ state
            state = state * 0.5
        used = int(ctx.flops_used)
    return used, float(ctx.residual_wall_time_s)


def main() -> None:
    t0 = time.perf_counter()
    module, blob = _load_lean_module()
    weights, gt, mlp_id = _load_row0()
    statics = module.build_static_coefs(N)

    capture_hook = CaptureHook()
    oracle = _run_oracle(module, weights, statics, capture_hook)
    repeat = _run_oracle(module, weights, statics, NoopHook())

    oracle_mse = float(np.mean((oracle[-1] - gt) ** 2))
    det_max_abs = float(np.max(np.abs(oracle - repeat)))
    finite = bool(np.isfinite(oracle).all())
    captures = [row["rank32_energy_capture"] for row in capture_hook.rows]
    capture_mean = float(np.mean(captures)) if captures else float("nan")
    capture_worst = float(np.min(captures)) if captures else float("nan")

    proxy_flops, proxy_residual = _proxy_once()
    projected_util = NON_SOURCE_UTIL + proxy_flops / BUDGET
    adjusted = oracle_mse * max(0.1, projected_util)

    gates = {
        "oracle_raw_le_1.89e-08": oracle_mse <= RAW_GATE,
        "rank32_mean_ge_0.95": capture_mean >= 0.95,
        "rank32_worst_ge_0.90": capture_worst >= 0.90,
        "projected_util_le_0.14": projected_util <= UTIL_GATE,
        "adjusted_le_2.646e-09": adjusted <= ADJUSTED_GATE,
        "proxy_residual_lt_0.400s": proxy_residual < 0.400,
        "finite": finite and np.isfinite(capture_mean) and np.isfinite(capture_worst),
        "deterministic": det_max_abs == 0.0,
        "pinned_blob": blob == EXPECTED_LEAN_BLOB,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "experiment": "E033",
        "decision": decision,
        "mlp_id": mlp_id,
        "oracle_final_mse": oracle_mse,
        "rank32_mean_energy_capture": capture_mean,
        "rank32_worst_energy_capture": capture_worst,
        "rank32_rows": capture_hook.rows,
        "proxy_flops": proxy_flops,
        "proxy_residual_s": proxy_residual,
        "projected_utilization": projected_util,
        "adjusted_proxy": adjusted,
        "det_max_abs": det_max_abs,
        "finite": finite,
        "lean_blob": blob,
        "gates": gates,
        "wall_s_total": time.perf_counter() - t0,
    }
    print("E033_SUMMARY " + json.dumps(summary, sort_keys=True, allow_nan=False), flush=True)
    Path("e033_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if decision != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
