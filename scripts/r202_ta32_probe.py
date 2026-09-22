"""R202 one-kernel TA32 probe.

Synthetic only: no benchmark targets, scorer, holdout, submission, or public accuracy data.
The decision metric is the frozen H185 kernel cost ratio plus exact/float32 identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter

import numpy as np

from methods.r202_ta32_kernel import (
    MECHANISM_RATIO_GATE,
    SCHEME_COMMIT,
    SCHEME_GIT_BLOB_SHA1,
    SCHEME_PATH,
    error_metrics,
    exact_scalar_block_identity,
    load_scheme,
    sha256_file,
    ta32_matmul,
)


def _array_sha256(x: np.ndarray) -> str:
    y = np.ascontiguousarray(x)
    return hashlib.sha256(y.view(np.uint8)).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheme", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=202)
    parser.add_argument("--n", type=int, default=1024)
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    receipt = {
        "schema": "arc.whitebox.r202.ta32_kernel.v1",
        "experiment": "R202",
        "hypothesis": "H185 exact TA32 kernel",
        "mode": "MINIMAL_KERNEL_PROTOTYPE_SYNTHETIC_ONLY",
        "git": {
            "branch": os.environ.get("GITHUB_REF_NAME"),
            "head_sha": os.environ.get("GITHUB_SHA"),
        },
        "target_firewall": {
            "benchmark_targets_read": False,
            "reference_means_read": False,
            "scorer_read": False,
            "holdout_read": False,
            "submission_attempted": False,
            "inputs": "deterministic synthetic matrices only",
        },
        "scheme": {
            "provider": "khoruzhii/lita",
            "commit": SCHEME_COMMIT,
            "path": SCHEME_PATH,
            "git_blob_sha1_expected": SCHEME_GIT_BLOB_SHA1,
            "local_sha256": sha256_file(args.scheme),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "blas_threads": {
                k: os.environ.get(k)
                for k in (
                    "OPENBLAS_NUM_THREADS",
                    "OMP_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS",
                    "NUMEXPR_NUM_THREADS",
                )
            },
        },
        "seed": args.seed,
        "shape": [args.n, args.n, args.n],
        "attempt": 1,
    }

    try:
        import scipy

        receipt["environment"]["scipy"] = scipy.__version__
        scheme = load_scheme(args.scheme)
        receipt["scheme"]["metadata"] = scheme.metadata
        receipt["scheme"]["nnz"] = {
            "u": scheme.u.nnz,
            "v": scheme.v.nnz,
            "w": scheme.w.nnz,
        }

        rng = np.random.default_rng(args.seed)
        a_exact = rng.integers(-2, 3, size=(32, 32), dtype=np.int64)
        b_exact = rng.integers(-2, 3, size=(32, 32), dtype=np.int64)
        t0 = perf_counter()
        exact = exact_scalar_block_identity(scheme, a_exact, b_exact)
        exact["seconds"] = perf_counter() - t0
        exact["a_sha256"] = _array_sha256(a_exact)
        exact["b_sha256"] = _array_sha256(b_exact)
        receipt["exact_scalar_block"] = exact

        if not exact["exact_equal"]:
            receipt["decision"] = {
                "status": "TECHNICAL_FAILURE_EXACT_IDENTITY",
                "kernel_go": False,
                "cost_gate": None,
                "float32_gate": None,
            }
            out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            print(json.dumps(receipt, indent=2, sort_keys=True))
            return 2

        n = args.n
        # Draw once in float32.  Float64 reference uses exactly the same represented inputs.
        scale = np.float32(1.0 / np.sqrt(n))
        a32 = (rng.standard_normal((n, n), dtype=np.float32) * scale).astype(np.float32)
        b32 = (rng.standard_normal((n, n), dtype=np.float32) * scale).astype(np.float32)
        a64 = a32.astype(np.float64)
        b64 = b32.astype(np.float64)

        t0 = perf_counter()
        ref64 = a64 @ b64
        ref64_seconds = perf_counter() - t0

        t0 = perf_counter()
        parent32 = a32 @ b32
        parent32_seconds = perf_counter() - t0

        candidate32, cost, timing = ta32_matmul(a32, b32, scheme)

        parent_err = error_metrics(parent32, ref64)
        candidate_err = error_metrics(candidate32, ref64)
        float32_checks = {
            metric: {
                "parent": parent_err[metric],
                "candidate": candidate_err[metric],
                "ratio_candidate_to_parent": (
                    candidate_err[metric] / parent_err[metric]
                    if parent_err[metric] != 0.0
                    else (0.0 if candidate_err[metric] == 0.0 else float("inf"))
                ),
                "limit_ratio": 1.05,
                "pass": (
                    candidate_err[metric] <= 1.05 * parent_err[metric]
                    if parent_err[metric] != 0.0
                    else candidate_err[metric] == 0.0
                ),
            }
            for metric in ("relative_frobenius", "max_absolute")
        }
        float32_pass = all(x["pass"] for x in float32_checks.values())

        cost_gate_pass = cost["ratio_to_classical_unpadded"] <= MECHANISM_RATIO_GATE
        leaf_gate_pass = cost["leaf_ratio_to_classical_unpadded"] <= MECHANISM_RATIO_GATE

        receipt["float32"] = {
            "reference64_seconds": ref64_seconds,
            "parent32_seconds": parent32_seconds,
            "candidate_timing": timing,
            "checks": float32_checks,
            "pass": float32_pass,
            "input_a_sha256": _array_sha256(a32),
            "input_b_sha256": _array_sha256(b32),
            "reference64_sha256": _array_sha256(ref64),
            "parent32_sha256": _array_sha256(parent32),
            "candidate32_sha256": _array_sha256(candidate32),
        }
        receipt["cost"] = {
            **cost,
            "mechanism_ratio_gate": MECHANISM_RATIO_GATE,
            "leaf_only_gate_pass": leaf_gate_pass,
            "complete_arithmetic_gate_pass": cost_gate_pass,
            "interpretation": (
                "ratio denominator is a classical same-shape matmul. The frozen V29 "
                "dense path is classical-or-faster (Strassen on dominant families), so "
                "failure even against the classical denominator is a conservative H185 NO-GO."
            ),
        }

        kernel_go = bool(exact["exact_equal"] and float32_pass and cost_gate_pass)
        if not cost_gate_pass:
            status = "TERMINAL_NO_GO_COST"
        elif not float32_pass:
            status = "TERMINAL_NO_GO_FLOAT32"
        else:
            status = "KERNEL_GO_REQUIRES_SEPARATE_COMPILER_AUTHORIZATION"
        receipt["decision"] = {
            "status": status,
            "kernel_go": kernel_go,
            "exact_gate": bool(exact["exact_equal"]),
            "float32_gate": bool(float32_pass),
            "cost_gate": bool(cost_gate_pass),
            "full_compiler_authorized": False,
            "scientific_run_authorized": False,
            "submission_authorized": False,
        }
    except Exception as exc:
        receipt["decision"] = {
            "status": "INFRA_ERROR",
            "kernel_go": False,
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }
        out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        raise

    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
