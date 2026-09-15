from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import types
import urllib.request

import numpy as np
import whestbench

from methods.e031_source_axis_moment import compute_floor, source_basis

V25_REPO = "504aldo/whest-p2-cumulant-k3"
V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0
AGG_GATE = 0.010
WORST_GATE = 0.022
UTIL_GATE = 0.14
# Officially verified exact E021 source-0 Zf transport saving on the same V25 source.
E021_EXACT_SAVING_FLOPS = 935_657_472
U_FLOPS = 2 * 1024**3
ZERO_BIRTH = """                    F1_b = fnp.zeros((n, rfb), dtype=f32)\n                    F2_b = F1_b\n                    R1T_b = F1_b\n                    R2T_b = F1_b\n"""
Z_F_TRANSPORT = """                if Zf_st is not None:\n                    Zf_st = fnp.matmul(WDb, Zf_st)\n"""


def _git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()


def _fetch_v25_source() -> str:
    url = f"https://api.github.com/repos/{V25_REPO}/git/blobs/{V25_BLOB}"
    req = urllib.request.Request(url, headers={"User-Agent": "arc-e031-preflight"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("sha") != V25_BLOB:
        raise RuntimeError(f"V25 API sha mismatch: {payload.get('sha')}")
    raw = base64.b64decode(payload["content"])
    observed = _git_blob_sha(raw)
    if observed != V25_BLOB:
        raise RuntimeError(f"V25 git blob mismatch: {observed}")
    return raw.decode("utf-8")


def _module_from_source(source: str) -> types.ModuleType:
    module = types.ModuleType("e031_v25_reference")
    module.__file__ = "<e031_v25_reference>"
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def _joint_gram(a_st, p_st) -> np.ndarray:
    a = np.asarray(a_st, dtype=np.float32)
    p = np.asarray(p_st, dtype=np.float32)
    k = a.shape[0]
    af = a.reshape(k, -1)
    pf = p.reshape(k, -1)
    # Diagnostic-only NumPy BLAS: does not alter or bill the estimator trajectory.
    return (af @ af.T).astype(np.float64) + (pf @ pf.T).astype(np.float64)


def main() -> None:
    source = _fetch_v25_source()
    zero_birth_count = source.count(ZERO_BIRTH)
    zf_transport_count = source.count(Z_F_TRANSPORT)
    if zero_birth_count != 1 or zf_transport_count != 1:
        raise RuntimeError(
            f"exact E021 structural provenance missing: zero={zero_birth_count} transport={zf_transport_count}"
        )

    reference = _module_from_source(source)
    measurements: list[dict[str, float | int]] = []

    class InstrumentedEstimator(reference.Estimator):
        def _dslices(self, A_st, P_st, *args, **kwargs):  # noqa: N803 - upstream names
            need_d21 = bool(kwargs.get("need_d21", True))
            if need_d21:
                gram = _joint_gram(A_st, P_st)
                k = int(gram.shape[0])
                q = source_basis(k)
                total = float(np.trace(gram))
                kept = float(np.trace(q.T @ gram @ q))
                lost = max(0.0, total - kept)
                eps = float(np.sqrt(lost / total)) if total > 0.0 else 0.0
                measurements.append({"k": k, "total": total, "lost": lost, "eps": eps})
            return super()._dslices(A_st, P_st, *args, **kwargs)

    ds = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
    mlp = whestbench.mlp_at(ds, INDEX)
    estimator = InstrumentedEstimator()
    output = np.asarray(estimator.predict(mlp, 2**41), dtype=np.float64)

    if not measurements:
        raise RuntimeError("no D21-capable source-stack measurements captured")
    total_energy = float(sum(float(x["total"]) for x in measurements))
    total_lost = float(sum(float(x["lost"]) for x in measurements))
    aggregate_rms = float(np.sqrt(total_lost / total_energy))
    worst_rms = float(max(float(x["eps"]) for x in measurements))

    saving_u = E021_EXACT_SAVING_FLOPS / float(U_FLOPS)
    floor = compute_floor(proven_exact_saving_u=saving_u)
    finite = bool(
        np.isfinite(output).all()
        and np.isfinite(aggregate_rms)
        and np.isfinite(worst_rms)
        and all(np.isfinite(float(v)) for v in floor.values())
    )
    gates = {
        "aggregate_source_axis_rms": aggregate_rms <= AGG_GATE,
        "worst_layer_rms": worst_rms <= WORST_GATE,
        "compute_path": floor["projected_util"] <= UTIL_GATE,
        "finite": finite,
        "scope": zero_birth_count == 1 and zf_transport_count == 1,
    }
    result = {
        "branch": "research/e031-source-axis-moment-closure-20260915",
        "canonical_base": "29bee3f8d23fc620b77aaed414b1b7a928af4b83",
        "v25_blob": V25_BLOB,
        "dataset": DATASET,
        "revision": REVISION,
        "index": INDEX,
        "basis_degree": 2,
        "basis_rank_max": 3,
        "d21_calls": len(measurements),
        "layer_measurements": measurements,
        "aggregate_source_axis_rms": aggregate_rms,
        "worst_layer_rms": worst_rms,
        "proven_exact_saving": {
            "mechanism": "E021 exact source-0 Zf dead-feedback transport elision only",
            "flops_per_mlp": E021_EXACT_SAVING_FLOPS,
            "u": saving_u,
            "e023_excluded": "structural-zero attempt changed floating reduction trajectory and was DROP",
        },
        "compute_floor": floor,
        "output_finite": bool(np.isfinite(output).all()),
        "output_shape": list(output.shape),
        "gates": gates,
        "go": bool(all(gates.values())),
    }
    Path("e031_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["go"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
