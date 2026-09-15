from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import urllib.request
from pathlib import Path

import flopscope.numpy as fnp
import numpy as np
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from whestbench.domain import MLP

from methods.e031_k22_memory import RANK, best_rank, instrument_v25_source

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
UPSTREAM_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
RAW_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/estimators/estimator_v25.py"
)
DATA_REPO = "aicrowd/arc-whestbench-public-2026"
DATA_REV = "v2-phase2"
DATA_FILE = "data/mini-00000-of-00007.parquet"
METRIC_C = 2.0
EPS = np.finfo(np.float64).tiny


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


def _make_mlp(row: dict) -> MLP:
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(16, 1024, 1024)
    return MLP(
        width=1024,
        depth=16,
        weights=[fnp.asarray(w) for w in weights],
        seed=int(row.get("mlp_seed", 0)),
    )


def _predict(module, row: dict) -> np.ndarray:
    est = module.Estimator()
    est.setup(_Ctx())
    return np.asarray(est.predict(_make_mlp(row), 2**41), dtype=np.float64)


def _layer_metrics(k22: np.ndarray, g_prev: np.ndarray, next_weight: np.ndarray) -> dict:
    k22 = np.asarray(k22, dtype=np.float64)
    g_prev = np.asarray(g_prev, dtype=np.float64)
    ml = (METRIC_C / 6.0) * (g_prev[:, None] + g_prev[None, :])
    np.fill_diagonal(ml, 0.0)
    residual = k22 - ml
    approx, retained = best_rank(residual, RANK)
    w2 = np.asarray(next_weight, dtype=np.float64).T ** 2
    exact_t = w2 @ residual @ w2.T
    approx_t = w2 @ approx @ w2.T
    tnorm = float(np.linalg.norm(exact_t))
    terr = float(np.linalg.norm(exact_t - approx_t) / max(tnorm, EPS))
    knorm = float(np.linalg.norm(k22))
    rnorm = float(np.linalg.norm(residual))
    return {
        "materiality": rnorm / max(knorm, EPS),
        "rank8_retained_energy": float(retained),
        "transported_relative_error": terr,
        "residual_norm": rnorm,
        "k22_norm": knorm,
        "transport_norm": tnorm,
    }


def main() -> None:
    raw = urllib.request.urlopen(RAW_URL, timeout=60).read()
    blob = _git_blob_sha(raw)
    if blob != UPSTREAM_BLOB:
        raise RuntimeError(f"pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")
    patched, marker = instrument_v25_source(source)
    patch_scope = patched.count(marker) == 1 and patched.replace(marker, "", 1) == source
    if not patch_scope:
        raise RuntimeError("instrumentation scope check failed")

    row = _load_row0()
    weights = np.asarray(row["weights"], dtype=np.float32).reshape(16, 1024, 1024)

    with tempfile.TemporaryDirectory(prefix="e031_") as td_s:
        td = Path(td_s)
        base_path = td / "v25_base.py"
        inst_path = td / "v25_e031.py"
        base_path.write_text(source, encoding="utf-8")
        inst_path.write_text(patched, encoding="utf-8")
        base = _load_module(base_path, "e031_v25_base")
        inst = _load_module(inst_path, "e031_v25_inst")

        os.environ.pop("E031_DEBUG", None)
        baseline = _predict(base, row)
        os.environ["E031_DEBUG"] = "1"
        try:
            instrumented = _predict(inst, row)
        finally:
            os.environ.pop("E031_DEBUG", None)

        debug = [d for d in inst.DEBUG if "e031_layer" in d]

    parity_max_abs = float(np.max(np.abs(baseline - instrumented)))
    layers = []
    for d in debug:
        li = int(d["e031_layer"])
        if li >= 15:
            continue
        m = _layer_metrics(np.asarray(d["K22"]), np.asarray(d["g_prev"]), weights[li + 1])
        m["layer"] = li
        layers.append(m)

    if len(layers) != 15:
        raise RuntimeError(f"expected 15 captured non-final layers, got {len(layers)}")

    materiality = np.asarray([x["materiality"] for x in layers], dtype=np.float64)
    retained = np.asarray([x["rank8_retained_energy"] for x in layers], dtype=np.float64)
    terr = np.asarray([x["transported_relative_error"] for x in layers], dtype=np.float64)

    # Algebra determinism check on captured layer 0 only; no estimator rerun.
    d0 = debug[0]
    first_a = _layer_metrics(np.asarray(d0["K22"]), np.asarray(d0["g_prev"]), weights[1])
    first_b = _layer_metrics(np.asarray(d0["K22"]), np.asarray(d0["g_prev"]), weights[1])
    algebra_deterministic = first_a == first_b

    finite = bool(
        np.isfinite(materiality).all()
        and np.isfinite(retained).all()
        and np.isfinite(terr).all()
        and np.isfinite(baseline).all()
        and np.isfinite(instrumented).all()
    )
    med_materiality = float(np.median(materiality))
    med_retained = float(np.median(retained))
    med_terr = float(np.median(terr))
    worst_terr = float(np.max(terr))
    gates = {
        "pinned_blob": blob == UPSTREAM_BLOB,
        "patch_scope": patch_scope,
        "prediction_parity": parity_max_abs == 0.0,
        "materiality_median_ge_0.05": med_materiality >= 0.05,
        "rank8_retained_median_ge_0.90": med_retained >= 0.90,
        "transport_error_median_le_0.05": med_terr <= 0.05,
        "transport_error_worst_le_0.12": worst_terr <= 0.12,
        "finite": finite,
        "algebra_deterministic": algebra_deterministic,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    summary = {
        "mlp_id": int(row["mlp_id"]),
        "pinned_blob": blob,
        "rank": RANK,
        "captured_layers": len(layers),
        "prediction_parity_max_abs": parity_max_abs,
        "median_materiality": med_materiality,
        "median_rank8_retained_energy": med_retained,
        "median_transported_relative_error": med_terr,
        "worst_transported_relative_error": worst_terr,
        "finite": finite,
        "algebra_deterministic": algebra_deterministic,
        "layers": layers,
        "gates": gates,
        "decision": decision,
    }
    print("E031_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
    Path("e031_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
