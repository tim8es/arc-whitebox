#!/usr/bin/env python3
"""One-shot E091 Phase-2-shape disjoint transfer measurement.

Synthetic networks only. No public/scorer/holdout/full-suite labels are read.
The A/B seed split, E043 base, V29 teacher, feature map, and lambda are frozen
in research/E091_PHASE2_TRANSFER_FREEZE.json before this script exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
import urllib.request
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import MLP, SetupContext

from methods.e091_production_bridge import FEATURE_P, final_layer_coordinate_features

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research" / "E091_PHASE2_TRANSFER_FREEZE.json"
BUDGET = 2**41

E043_COMMIT = "d0108f7faccaa656d3908f5afeaa90e056881c71"
E043_ADAPTER_BLOB = "8777dde2b848dd8ae855f9040ca27b4c6f235989"
E043_ADAPTER_URL = (
    "https://raw.githubusercontent.com/tim8es/arc-whitebox/"
    + E043_COMMIT
    + "/methods/e043_terminal_adjoint_k3.py"
)
E051_COMMIT = "642b6b0f5ec549a3c0f9e3fdb54fbae09a000133"
E051_ADAPTER_BLOB = "513677e2257c22951a6fa96c603a6d66707d3700"
E051_ADAPTER_URL = (
    "https://raw.githubusercontent.com/tim8es/arc-whitebox/"
    + E051_COMMIT
    + "/methods/e051_v29_adapter.py"
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\\0".encode("ascii") + data).hexdigest()


def payload_sha256(payload: dict) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def fetch_exact(url: str, expected_blob: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    observed = git_blob_sha(data)
    if observed != expected_blob:
        raise RuntimeError(f"blob mismatch for {url}: {observed} != {expected_blob}")
    return data


def exec_module(source: bytes | str, name: str) -> types.ModuleType:
    text = source.decode("utf-8") if isinstance(source, bytes) else source
    mod = types.ModuleType(name)
    mod.__file__ = f"<{name}>"
    sys.modules[name] = mod
    exec(compile(text, mod.__file__, "exec"), mod.__dict__)
    return mod


def load_base_module() -> tuple[types.ModuleType, dict]:
    adapter_bytes = fetch_exact(E043_ADAPTER_URL, E043_ADAPTER_BLOB)
    adapter = exec_module(adapter_bytes, "e091_frozen_e043_adapter")
    patched, provenance = adapter.fetch_and_patch_pinned_source()
    module = exec_module(patched, "e091_frozen_e043_base")
    return module, {
        "adapter_blob": git_blob_sha(adapter_bytes),
        "upstream_blob": provenance["blob_sha"],
        "patch_counts": provenance["patch_counts"],
    }


def load_teacher_module() -> tuple[types.ModuleType, dict]:
    adapter_bytes = fetch_exact(E051_ADAPTER_URL, E051_ADAPTER_BLOB)
    adapter = exec_module(adapter_bytes, "e091_frozen_e051_adapter")
    module, source = adapter.load_exact_v29("e091_frozen_v29_teacher")
    return module, {
        "adapter_blob": git_blob_sha(adapter_bytes),
        "upstream_blob": adapter.git_blob_sha1(source),
    }


def build_mlp(width: int, depth: int, seed: int) -> MLP:
    rng = fnp.random.default_rng(seed)
    scale = (2.0 / width) ** 0.5
    weights = [
        fnp.array((rng.standard_normal((width, width)) * scale).astype(fnp.float32))
        for _ in range(depth)
    ]
    return MLP(width=width, depth=depth, weights=weights, seed=seed)


def run_estimator(module: types.ModuleType, mlp: MLP, setup_seed: int = 0):
    estimator = module.Estimator()
    estimator.setup(
        SetupContext(
            width=mlp.width,
            depth=mlp.depth,
            flop_budget=BUDGET,
            api_version="1",
            seed=setup_seed,
        )
    )
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        prediction = estimator.predict(mlp, BUDGET)
    estimator.teardown()
    arr = np.asarray(prediction, dtype=np.float64)
    if arr.shape != (mlp.depth, mlp.width):
        raise RuntimeError(f"unexpected prediction shape {arr.shape}")
    if not np.isfinite(arr).all():
        raise FloatingPointError("non-finite estimator prediction")
    return arr, int(ctx.flops_used)


def materialize_network(
    seed: int,
    width: int,
    depth: int,
    base_module: types.ModuleType,
    teacher_module: types.ModuleType,
) -> dict:
    mlp = build_mlp(width, depth, seed)
    base, base_flops = run_estimator(base_module, mlp)
    teacher, teacher_flops = run_estimator(teacher_module, mlp)
    last_weight = np.asarray(mlp.weights[-1], dtype=np.float64)
    X = final_layer_coordinate_features(base, last_weight)
    residual = teacher[-1] - base[-1]
    if X.shape != (width, FEATURE_P):
        raise AssertionError(f"unexpected feature shape {X.shape}")
    if residual.shape != (width,) or not np.isfinite(residual).all():
        raise AssertionError("invalid residual target")
    return {
        "seed": int(seed),
        "X": X,
        "residual": residual,
        "base_flops": base_flops,
        "teacher_flops": teacher_flops,
        "baseline_mse_to_teacher": float(np.mean(residual * residual)),
    }


def transfer_metrics(X: np.ndarray, residual: np.ndarray, beta: np.ndarray) -> dict:
    s = X @ beta
    q = float(np.mean(residual * s))
    v = float(np.mean(s * s))
    delta = float(2.0 * q - v)
    baseline = float(np.mean(residual * residual))
    corrected = float(np.mean((residual - s) ** 2))
    identity_error = float(abs((baseline - corrected) - delta))
    return {
        "n_rows": int(residual.size),
        "q": q,
        "v": v,
        "v_over_2": float(v / 2.0),
        "delta": delta,
        "baseline_mse_to_teacher": baseline,
        "corrected_mse_to_teacher": corrected,
        "mse_ratio": float(corrected / baseline) if baseline > 0.0 else None,
        "relative_improvement": float(delta / baseline) if baseline > 0.0 else None,
        "identity_error": identity_error,
        "gate": bool(q > v / 2.0 and corrected < baseline),
    }


def run(output: Path) -> dict:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    payload = freeze["payload"]
    if payload_sha256(payload) != freeze["payload_sha256"]:
        raise AssertionError("freeze payload hash mismatch")
    if payload["schema"] != "arc.whitebox.e091.phase2_disjoint_transfer_freeze.v1":
        raise AssertionError("unexpected freeze schema")
    if payload["status"] != "PRE_TARGET_FREEZE":
        raise AssertionError("freeze status is not PRE_TARGET_FREEZE")
    if any(
        payload["scope"][k]
        for k in ("public", "official_scorer", "holdout", "full_suite", "benchmark_labels")
    ):
        raise AssertionError("forbidden evidence source enabled")

    width = int(payload["network_generator"]["width"])
    depth = int(payload["network_generator"]["depth"])
    A_seeds = [int(x) for x in payload["split"]["A_fit_seeds"]]
    B_seeds = [int(x) for x in payload["split"]["B_transfer_seeds"]]
    if set(A_seeds) & set(B_seeds):
        raise AssertionError("A/B network seeds overlap")
    if width != 1024 or depth != 16:
        raise AssertionError("transfer corpus is not exact Phase-2 shape")
    if float(payload["feature_and_fit"]["ridge_lambda"]) != 1.0:
        raise AssertionError("unexpected ridge lambda")

    base_module, base_provenance = load_base_module()
    teacher_module, teacher_provenance = load_teacher_module()
    if base_provenance["adapter_blob"] != payload["base"]["adapter_blob"]:
        raise AssertionError("E043 adapter drift")
    if base_provenance["upstream_blob"] != payload["base"]["upstream_v25_blob"]:
        raise AssertionError("E043 upstream drift")
    if not all(v == 1 for v in base_provenance["patch_counts"].values()):
        raise AssertionError("E043 patch drift")
    if teacher_provenance["adapter_blob"] != payload["teacher"]["adapter_blob"]:
        raise AssertionError("E051 adapter drift")
    if teacher_provenance["upstream_blob"] != payload["teacher"]["upstream_v29_blob"]:
        raise AssertionError("V29 teacher drift")

    A_rows = [
        materialize_network(seed, width, depth, base_module, teacher_module)
        for seed in A_seeds
    ]
    X_A = np.vstack([row["X"] for row in A_rows])
    r_A = np.concatenate([row["residual"] for row in A_rows])
    gram = X_A.T @ X_A + np.eye(FEATURE_P, dtype=np.float64)
    beta = np.linalg.solve(gram, X_A.T @ r_A)
    if not np.isfinite(beta).all():
        raise FloatingPointError("non-finite frozen beta")
    A_metrics = transfer_metrics(X_A, r_A, beta)

    B_rows = [
        materialize_network(seed, width, depth, base_module, teacher_module)
        for seed in B_seeds
    ]
    X_B = np.vstack([row["X"] for row in B_rows])
    r_B = np.concatenate([row["residual"] for row in B_rows])
    B_metrics = transfer_metrics(X_B, r_B, beta)
    per_network = [
        {
            "seed": row["seed"],
            **transfer_metrics(row["X"], row["residual"], beta),
            "base_flops": row["base_flops"],
            "teacher_flops": row["teacher_flops"],
        }
        for row in B_rows
    ]

    tol = float(payload["transfer_gate"]["identity_tolerance"])
    identity_ok = bool(
        A_metrics["identity_error"] <= tol
        and B_metrics["identity_error"] <= tol
        and all(row["identity_error"] <= tol for row in per_network)
    )
    per_network_direction = bool(all(row["delta"] > 0.0 for row in per_network))
    finite = bool(
        np.isfinite(X_A).all()
        and np.isfinite(r_A).all()
        and np.isfinite(X_B).all()
        and np.isfinite(r_B).all()
        and np.isfinite(beta).all()
    )
    gate = bool(B_metrics["gate"] and identity_ok and per_network_direction and finite)

    result = {
        "schema": "arc.whitebox.e091.phase2_disjoint_transfer_result.v1",
        "experiment": "E091",
        "freeze_payload_sha256": freeze["payload_sha256"],
        "scope": payload["scope"],
        "base_provenance": base_provenance,
        "teacher_provenance": teacher_provenance,
        "shape": {"width": width, "depth": depth},
        "A_fit_seeds": A_seeds,
        "B_transfer_seeds": B_seeds,
        "ridge_lambda": 1.0,
        "beta": beta.tolist(),
        "beta_l2": float(np.linalg.norm(beta)),
        "A": A_metrics,
        "B": B_metrics,
        "B_per_network": per_network,
        "A_base_flops": [row["base_flops"] for row in A_rows],
        "A_teacher_flops": [row["teacher_flops"] for row in A_rows],
        "B_base_flops": [row["base_flops"] for row in B_rows],
        "B_teacher_flops": [row["teacher_flops"] for row in B_rows],
        "identity_ok": identity_ok,
        "per_network_direction_required": True,
        "per_network_direction_ok": per_network_direction,
        "finite": finite,
        "transfer_gate_q_gt_v_over_2": bool(B_metrics["q"] > B_metrics["v_over_2"]),
        "decision": "TRANSFER_GO" if gate else "TERMINAL_NO_GO",
        "scientific_go": gate,
        "public_targets_read": False,
        "benchmark_labels_read": False,
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("E091_PHASE2_TRANSFER_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("e091-phase2-transfer-result.json")
    )
    args = parser.parse_args()
    result = run(args.output)
    if result["decision"] != "TRANSFER_GO":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
