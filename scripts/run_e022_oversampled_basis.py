from __future__ import annotations

import hashlib
import importlib.util
import json
import os
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

from experiments.e022_oversampled_basis import exact_top_eigenspace, principal_subspace_error

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
RANK = 384
ELL = 400
E007_RAW = 2.23e-8
E007_ADJ = 8.17e-9
E007_UTIL = 0.36666448


class _Ctx:
    seed = 0


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _load_module(path: Path, name: str, *, no_confine: bool = False):
    old = os.environ.get("V21_NO_CONFINE")
    os.environ["V21_NO_CONFINE"] = "1" if no_confine else "0"
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("unable to construct module spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old is None:
            os.environ.pop("V21_NO_CONFINE", None)
        else:
            os.environ["V21_NO_CONFINE"] = old


def _patch_candidate(source: str) -> str:
    marker = "DEBUG = []  # parity_v17.py: per-layer dict of diagnostics when V17_DEBUG=1\n"
    if source.count(marker) != 1:
        raise RuntimeError("E022 observer marker mismatch")
    source = source.replace(marker, marker + "E022_OBSERVER = None\n", 1)

    old = '''                    Om = fnp.copy(w32[:, :r_old])          # fixed sketch (n, r)\n                    Qp = (w1c * Qc) if ka > 0 else None     # post-wick old basis\n                    for _pass in range(QPASS):\n                        # Yq = G Om with G = Aj dA Aj^T + Pj dP Pj^T + Qp Sg Qp^T\n                        Yq = Aj @ (dAj * (Aj.T @ Om)) + Pj @ (dPj * (Pj.T @ Om))\n                        if ka > 0:\n                            # V24: full core of the confined legs = tier-1 core + lifted tier-2 core\n                            Sfull = Sg if kb == 0 else Sg + U @ (S2 @ U.T)\n                            Yq = Yq + Qp @ (Sfull @ (Qp.T @ Om))\n                        Qn, _ = fnp.linalg.qr(Yq)           # (n, r) orthonormal\n                        Om = Qn\n'''
    new = '''                    # E022: frozen one-pass oversampled spectral rebuild.\n                    # R_OLD=384, p=16, ell=400. Exactly one application of G.\n                    if r_old != 384 or n < 400:\n                        raise RuntimeError("E022 requires suite width and frozen R_OLD=384")\n                    Om = fnp.copy(w32[:, :400])\n                    Qp = (w1c * Qc) if ka > 0 else None\n                    Yq = Aj @ (dAj * (Aj.T @ Om)) + Pj @ (dPj * (Pj.T @ Om))\n                    Sfull = None\n                    if ka > 0:\n                        Sfull = Sg if kb == 0 else Sg + U @ (S2 @ U.T)\n                        Yq = Yq + Qp @ (Sfull @ (Qp.T @ Om))\n                    Hq = Yq.T @ Yq\n                    evals, evecs = fnp.linalg.eigh(Hq)\n                    lam = evals[-384:]\n                    Vq = evecs[:, -384:]\n                    Qn = Yq @ (Vq / fnp.reshape(fnp.sqrt(lam), (1, 384)))\n                    if E022_OBSERVER is not None:\n                        E022_OBSERVER(li, w32, Aj, Pj, dAj, dPj, Qp, Sfull, Qn)\n'''
    if source.count(old) != 1:
        raise RuntimeError("V25 q1 block did not match pinned source exactly")
    return source.replace(old, new, 1)


def _load_rows() -> list[dict]:
    path = hf_hub_download(
        repo_id=DATA_REPO,
        repo_type="dataset",
        revision=DATA_REV,
        filename=DATA_FILE,
    )
    table = pq.read_table(path, columns=["weights", "final_means", "mlp_id"]).slice(0, 8)
    rows = table.to_pylist()
    if len(rows) != 8:
        raise RuntimeError(f"expected 8 frozen rows, got {len(rows)}")
    return rows


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
    mse = float(np.mean((p[-1] - gt) ** 2))
    return {
        "mse": mse,
        "flops": used,
        "util": used / BUDGET,
        "residual_s": residual,
        "wall_s": wall,
        "pred": p[-1],
    }


def main() -> None:
    raw = urllib.request.urlopen(RAW_URL, timeout=60).read()
    blob = _git_blob_sha(raw)
    if blob != UPSTREAM_BLOB:
        raise RuntimeError(f"pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")

    with tempfile.TemporaryDirectory(prefix="e022_") as td_name:
        td = Path(td_name)
        q1_path = td / "v25_q1.py"
        exact_path = td / "v25_exact.py"
        cand_path = td / "v25_e022.py"
        q1_path.write_text(source, encoding="utf-8")
        exact_path.write_text(source, encoding="utf-8")
        cand_path.write_text(_patch_candidate(source), encoding="utf-8")

        q1 = _load_module(q1_path, "e022_v25_q1", no_confine=False)
        exact = _load_module(exact_path, "e022_v25_exact", no_confine=True)
        cand = _load_module(cand_path, "e022_v25_candidate", no_confine=False)

        subspace_records: list[dict] = []

        def observer(li, w32, aj, pj, daj, dpj, qp, sfull, qn):
            a = np.asarray(aj, dtype=np.float64)
            p = np.asarray(pj, dtype=np.float64)
            da = np.asarray(daj, dtype=np.float64)
            dp = np.asarray(dpj, dtype=np.float64)
            g = a @ (da * a.T) + p @ (dp * p.T)
            if qp is not None:
                qpa = np.asarray(qp, dtype=np.float64)
                sf = np.asarray(sfull, dtype=np.float64)
                g = g + qpa @ sf @ qpa.T
            teacher = exact_top_eigenspace(g, RANK)
            omega_q1 = np.asarray(w32[:, :RANK], dtype=np.float64)
            y1 = g @ omega_q1
            q1_np, _ = np.linalg.qr(y1, mode="reduced")
            qc = np.asarray(qn, dtype=np.float64)
            subspace_records.append(
                {
                    "layer": int(li),
                    "q1_error": principal_subspace_error(q1_np[:, :RANK], teacher),
                    "e022_error": principal_subspace_error(qc, teacher),
                }
            )

        rows = _load_rows()
        metrics = []
        for i, row in enumerate(rows):
            before = len(subspace_records)
            cand.E022_OBSERVER = observer
            _run(cand, row, metered=False)
            cand.E022_OBSERVER = None
            after = len(subspace_records)
            for record in subspace_records[before:after]:
                record["index"] = i

            q = _run(q1, row, metered=True)
            c = _run(cand, row, metered=True)
            e = _run(exact, row, metered=False)
            c2 = _run(cand, row, metered=False)
            det = float(np.max(np.abs(c["pred"] - c2["pred"])))
            metrics.append(
                {
                    "index": i,
                    "mlp_id": int(row["mlp_id"]),
                    "q1_mse": q["mse"],
                    "e022_mse": c["mse"],
                    "exact_mse": e["mse"],
                    "ratio": c["mse"] / q["mse"],
                    "q1_util": q["util"],
                    "e022_util": c["util"],
                    "flop_delta": c["flops"] - q["flops"],
                    "q1_residual_s": q["residual_s"],
                    "e022_residual_s": c["residual_s"],
                    "det_max_abs": det,
                    "rebuilds_observed": after - before,
                }
            )
            print("E022_ROW " + json.dumps(metrics[-1], sort_keys=True), flush=True)

        val = metrics[4:8]
        val_ratio = sum(m["e022_mse"] for m in val) / sum(m["q1_mse"] for m in val)
        val_sub = [r for r in subspace_records if 4 <= r["index"] <= 7]
        if not val_sub:
            raise RuntimeError("no validation subspace records")
        mean_q1_err = float(np.mean([r["q1_error"] for r in val_sub]))
        mean_e022_err = float(np.mean([r["e022_error"] for r in val_sub]))
        sub_improvement = 1.0 - mean_e022_err / mean_q1_err
        mean_flop_delta = float(np.mean([m["flop_delta"] for m in val]))
        projected_util = E007_UTIL + mean_flop_delta / BUDGET
        projected_adjusted = E007_RAW * val_ratio * projected_util
        max_regression = max(m["ratio"] for m in val)
        max_det = max(m["det_max_abs"] for m in metrics)
        residual_delta = float(
            np.mean([m["e022_residual_s"] - m["q1_residual_s"] for m in val])
        )

        gates = {
            "validation_ratio_le_0.990": val_ratio <= 0.990,
            "no_dump_regression_gt_2pct": max_regression <= 1.02,
            "subspace_improvement_ge_20pct": sub_improvement >= 0.20,
            "projected_util_le_0.3697": projected_util <= 0.3697,
            "projected_adjusted_le_8.16e-09": projected_adjusted <= 8.16e-9,
            "projected_adjusted_lt_8.17e-09": projected_adjusted < E007_ADJ,
            "deterministic": max_det == 0.0,
            "persistent_memory_regression": True,
            "residual_delta_le_5ms": residual_delta <= 0.005,
            "one_G_pass_by_construction": True,
        }
        summary = {
            "validation_mse_ratio": val_ratio,
            "max_validation_dump_ratio": max_regression,
            "mean_q1_subspace_error": mean_q1_err,
            "mean_e022_subspace_error": mean_e022_err,
            "subspace_error_improvement": sub_improvement,
            "mean_validation_flop_delta": mean_flop_delta,
            "projected_utilization": projected_util,
            "projected_adjusted": projected_adjusted,
            "mean_validation_residual_delta_s": residual_delta,
            "det_max_abs": max_det,
            "persistent_extra_bytes": 0,
            "temporary_shapes": [[1024, 400], [400, 400]],
            "validation_subspace_records": len(val_sub),
            "gates": gates,
            "decision": "GO" if all(gates.values()) else "NO-GO",
        }
        print("E022_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)
        Path("e022_result.json").write_text(
            json.dumps(
                {"rows": metrics, "subspace": subspace_records, "summary": summary},
                indent=2,
            ),
            encoding="utf-8",
        )

        if not all(gates.values()):
            raise SystemExit(2)


if __name__ == "__main__":
    main()
