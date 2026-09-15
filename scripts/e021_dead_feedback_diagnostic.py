"""Frozen E021 MLP0 diagnostic. No tuning/sweep/holdout/scorer."""

from __future__ import annotations

import base64
import hashlib
import json
import time
import types
import urllib.request

import flopscope as flops
import numpy as np
import whestbench


IDEMPOTENCY_KEY = "ARC-E021-DEAD-FEEDBACK-20250915"
V25_REPO = "504aldo/whest-p2-cumulant-k3"
V25_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
BUDGET = 2**41
E007_UTIL = 0.36666448
UTIL_GATE = 0.36630
SAVING_GATE = 8.0e8
ERROR_GATE = 1.0e-7
RESIDUAL_EXTRA_GATE_S = 0.005

OLD_TRANSPORT = """                if Zf_st is not None:\n                    Zf_st = fnp.matmul(WDb, Zf_st)\n"""
NEW_TRANSPORT = """                if Zf_st is not None:\n                    Zf_st = transport_feedback_without_source0(WDb, Zf_st)\n"""
IMPORT_ANCHOR = "import math\n"
IMPORT_PATCH = "import math\nfrom methods.e021_dead_feedback import transport_feedback_without_source0\n"
ZERO_BIRTH = """                    F1_b = fnp.zeros((n, rfb), dtype=f32)\n                    F2_b = F1_b\n                    R1T_b = F1_b\n                    R2T_b = F1_b\n"""


def _git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _fetch_v25_source() -> str:
    url = f"https://api.github.com/repos/{V25_REPO}/git/blobs/{V25_BLOB}"
    req = urllib.request.Request(url, headers={"User-Agent": "arc-e021-diagnostic"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("sha") != V25_BLOB:
        raise RuntimeError(f"V25 API sha mismatch: {payload.get('sha')}")
    raw = base64.b64decode(payload["content"])
    observed = _git_blob_sha(raw)
    if observed != V25_BLOB:
        raise RuntimeError(f"V25 git blob mismatch: {observed}")
    return raw.decode("utf-8")


def _module_from_source(name: str, source: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = f"<{name}>"
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def _run_predict(estimator_cls, mlp):
    estimator = estimator_cls()
    start = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, wall_time_limit_s=120.0) as budget:
        output = estimator.predict(mlp, BUDGET)
    elapsed = time.perf_counter() - start
    return (
        np.asarray(output, dtype=np.float64),
        int(budget.flops_used),
        float(budget.residual_wall_time_s),
        float(budget.wall_time_s),
        elapsed,
    )


def main() -> None:
    source = _fetch_v25_source()
    if source.count(OLD_TRANSPORT) != 1:
        raise RuntimeError(f"expected exactly one V25 Zf transport, found {source.count(OLD_TRANSPORT)}")
    if source.count(ZERO_BIRTH) != 1:
        raise RuntimeError(f"expected exactly one source-0 zero-birth block, found {source.count(ZERO_BIRTH)}")
    if source.count(IMPORT_ANCHOR) < 1:
        raise RuntimeError("V25 import anchor missing")

    candidate_source = source.replace(IMPORT_ANCHOR, IMPORT_PATCH, 1).replace(
        OLD_TRANSPORT, NEW_TRANSPORT, 1
    )
    baseline_module = _module_from_source("e021_v25_baseline", source)
    candidate_module = _module_from_source("e021_v25_candidate", candidate_source)

    ds = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
    mlp = whestbench.mlp_at(ds, INDEX)

    baseline, base_flops, base_residual, base_wall, base_elapsed = _run_predict(
        baseline_module.Estimator, mlp
    )
    candidate, cand_flops, cand_residual, cand_wall, cand_elapsed = _run_predict(
        candidate_module.Estimator, mlp
    )
    candidate_repeat, repeat_flops, repeat_residual, repeat_wall, repeat_elapsed = _run_predict(
        candidate_module.Estimator, mlp
    )

    diff = candidate - baseline
    max_abs = float(np.max(np.abs(diff)))
    denom = max(float(np.linalg.norm(baseline.ravel())), np.finfo(np.float64).tiny)
    rel_frob = float(np.linalg.norm(diff.ravel()) / denom)
    repeat_max_abs = float(np.max(np.abs(candidate_repeat - candidate)))
    finite = bool(np.isfinite(baseline).all() and np.isfinite(candidate).all())
    deterministic = bool(
        repeat_max_abs == 0.0
        and repeat_flops == cand_flops
        and np.array_equal(candidate_repeat, candidate)
    )

    saving = int(base_flops - cand_flops)
    projected_util = float(E007_UTIL - saving / BUDGET)
    residual_delta = float(cand_residual - base_residual)
    persistent_shape_unchanged = bool(candidate.shape == baseline.shape)

    gates = {
        "max_abs": max_abs <= ERROR_GATE,
        "relative_frobenius": rel_frob <= ERROR_GATE,
        "saving": saving >= SAVING_GATE,
        "projected_utilization": projected_util <= UTIL_GATE,
        "residual_resource": residual_delta <= RESIDUAL_EXTRA_GATE_S and persistent_shape_unchanged,
        "deterministic": deterministic,
        "finite": finite,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"

    result = {
        "idempotency_key": IDEMPOTENCY_KEY,
        "decision": decision,
        "v25": {
            "repo": V25_REPO,
            "commit": V25_COMMIT,
            "expected_blob": V25_BLOB,
            "observed_blob": _git_blob_sha(source.encode("utf-8")),
            "source0_zero_birth_verified": True,
            "transport_replacement_count": 1,
            "expected_source0_subsequent_transports": 15,
        },
        "dataset": {"name": DATASET, "revision": REVISION, "split": SPLIT, "index": INDEX},
        "metrics": {
            "output_max_abs": max_abs,
            "output_relative_frobenius": rel_frob,
            "baseline_flops": base_flops,
            "candidate_flops": cand_flops,
            "measured_saving_flops": saving,
            "projected_utilization": projected_util,
            "baseline_residual_s": base_residual,
            "candidate_residual_s": cand_residual,
            "residual_delta_s": residual_delta,
            "baseline_wall_s": base_wall,
            "candidate_wall_s": cand_wall,
            "baseline_elapsed_s": base_elapsed,
            "candidate_elapsed_s": cand_elapsed,
            "repeat_max_abs": repeat_max_abs,
            "repeat_flops": repeat_flops,
            "repeat_residual_s": repeat_residual,
            "repeat_wall_s": repeat_wall,
            "repeat_elapsed_s": repeat_elapsed,
            "persistent_shape_unchanged": persistent_shape_unchanged,
            "finite": finite,
            "deterministic": deterministic,
        },
        "gates": gates,
    }
    print("E021_RESULT=" + json.dumps(result, sort_keys=True))
    print("DECISION=" + decision)


if __name__ == "__main__":
    main()
