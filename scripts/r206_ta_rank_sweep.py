"""Execute the single frozen R206 synthetic-only TA rank sweep."""

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

from methods.r206_ta_rank_sweep import (
    FROZEN_SCHEMES,
    LITA_COMMIT,
    MECHANISM_RATIO_GATE,
    STABILITY_RATIO_GATE,
    exact_identity,
    load_generic_scheme,
    stability,
    sweep_cost,
    ta_matmul,
)


def _sha(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x).view(np.uint8)).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scheme-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, default=1024)
    p.add_argument("--seed", type=int, default=206)
    args = p.parse_args()

    scheme_dir = Path(args.scheme_dir)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    receipt = {
        "schema": "arc.whitebox.r206.ta_rank_sweep.v1",
        "experiment": "R206",
        "parent": "R202@df9cca77f9885644c6058dc4307acc187a2a2dcb",
        "git": {
            "branch": os.environ.get("GITHUB_REF_NAME"),
            "head_sha": os.environ.get("GITHUB_SHA"),
        },
        "protocol": {
            "frozen_points": [
                {"dim": d, "rank": r, "git_blob_sha1": blob}
                for d, r, blob in FROZEN_SCHEMES
            ],
            "mechanism_ratio_gate": MECHANISM_RATIO_GATE,
            "stability_ratio_gate": STABILITY_RATIO_GATE,
            "seed": args.seed,
            "shape": [args.n, args.n, args.n],
        },
        "target_firewall": {
            "synthetic_only": True,
            "benchmark_targets_read": False,
            "holdout_read": False,
            "scorer_read": False,
            "submission_attempted": False,
            "compiler_built": False,
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
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
        "lita_commit": LITA_COMMIT,
        "points": [],
    }

    try:
        import scipy
        receipt["environment"]["scipy"] = scipy.__version__

        rng = np.random.default_rng(args.seed)
        n = args.n
        scale = np.float32(1.0 / np.sqrt(n))
        a32 = (rng.standard_normal((n, n), dtype=np.float32) * scale).astype(np.float32)
        b32 = (rng.standard_normal((n, n), dtype=np.float32) * scale).astype(np.float32)
        a64, b64 = a32.astype(np.float64), b32.astype(np.float64)

        t0 = perf_counter()
        reference64 = a64 @ b64
        ref_seconds = perf_counter() - t0
        t0 = perf_counter()
        parent32 = a32 @ b32
        parent_seconds = perf_counter() - t0

        receipt["fixture"] = {
            "a32_sha256": _sha(a32),
            "b32_sha256": _sha(b32),
            "reference64_sha256": _sha(reference64),
            "parent32_sha256": _sha(parent32),
            "reference64_seconds": ref_seconds,
            "parent32_seconds": parent_seconds,
        }

        for dim, rank, blob in FROZEN_SCHEMES:
            path = scheme_dir / f"{dim}x{dim}x{dim}_r{rank}.npz"
            scheme = load_generic_scheme(path, dim, rank, blob)

            exact_rng = np.random.default_rng(args.seed * 1000 + dim)
            ae = exact_rng.integers(-2, 3, size=(dim, dim), dtype=np.int64)
            be = exact_rng.integers(-2, 3, size=(dim, dim), dtype=np.int64)
            t0 = perf_counter()
            exact = exact_identity(scheme, ae, be)
            exact["seconds"] = perf_counter() - t0
            exact["a_sha256"] = _sha(ae)
            exact["b_sha256"] = _sha(be)

            candidate, timing = ta_matmul(a32, b32, scheme)
            stab = stability(candidate, parent32, reference64)
            cost = sweep_cost(scheme, n, n, n)

            point = {
                "dim": dim,
                "rank": rank,
                "scheme": {
                    "git_blob_sha1": scheme.git_blob_sha1,
                    "sha256": scheme.sha256,
                    "metadata": scheme.metadata,
                },
                "exact": exact,
                "cost": cost,
                "runtime": {
                    **timing,
                    "ratio_candidate_to_parent32": timing["total_seconds"] / parent_seconds,
                },
                "float32": {
                    **stab,
                    "candidate_sha256": _sha(candidate),
                },
                "gates": {
                    "exact": bool(exact["exact_equal"]),
                    "leaf_cost": bool(cost["leaf_ratio"] <= MECHANISM_RATIO_GATE),
                    "full_cost": bool(cost["full_ratio"] <= MECHANISM_RATIO_GATE),
                    "stability": bool(stab["pass"]),
                },
            }
            point["gates"]["joint_full_cost_and_stability"] = bool(
                point["gates"]["full_cost"] and point["gates"]["stability"]
            )
            receipt["points"].append(point)

        any_joint = any(p["gates"]["joint_full_cost_and_stability"] for p in receipt["points"])
        all_exact = all(p["gates"]["exact"] for p in receipt["points"])
        receipt["decision"] = {
            "status": (
                "KERNEL_SWEEP_GO_REQUIRES_SEPARATE_COMPILER_AUTHORIZATION"
                if any_joint and all_exact
                else "TERMINAL_NO_GO_NO_PARETO_POINT_MEETS_COST_AND_STABILITY"
            ),
            "all_exact": all_exact,
            "any_joint_gate_pass": any_joint,
            "stop_before_compiler": not any_joint,
            "paid_run_used": False,
            "submission_attempted": False,
        }
    except Exception as exc:
        receipt["decision"] = {
            "status": "INFRA_ERROR",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "stop_before_compiler": True,
        }
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        raise

    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
