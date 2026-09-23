#!/usr/bin/env python3
"""R235 frozen exact fixture for the screened WEIGHTED-ALIAS-GRAM direction.

This fixture is intentionally NOT executed in R235 because the frozen production
upper bound already fails the >=1.0% materiality gate. It is committed so the
screened algebraic identity and flopscope behavior remain reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp

EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
N = 1024
L = 16
AGE_OLD = 4
R_OLD = 384
AGE_OLD2 = 7
R_OLD2 = 224
V25_FLOPS = 806_303_721_965


def git_blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode())
    h.update(data)
    return h.hexdigest()


def production_schedule():
    ka = 0
    kb = 0
    joins = []
    moves = []
    # At layer li, k == li for suite layers after the newborn from the previous
    # layer has been inserted. The final layer skips the join by source code gate.
    for li in range(L):
        last = li == L - 1
        k = li
        ka_t = ka
        if not last:
            ka_t = max(ka, min(k, li - AGE_OLD))
        if ka_t > ka:
            if ka_t != ka + 1:
                raise AssertionError((li, ka, ka_t))
            joins.append(li)

            kb_t = kb
            kb_t = max(kb, min(ka_t - 1, li - AGE_OLD2))
            if kb_t > kb:
                if kb_t != kb + 1:
                    raise AssertionError((li, kb, kb_t))
                moves.append(li)
                kb = kb_t
            ka = ka_t
    return joins, moves


def analytic_bound():
    joins, moves = production_schedule()
    grams = 2 * (len(joins) + len(moves))
    per_gram = R_OLD * R_OLD * (2 * N - 1)
    current = grams * per_gram
    ideal_saving = current // 2
    threshold = 0.01 * V25_FLOPS
    return {
        "joins": joins,
        "moves": moves,
        "eligible_weighted_grams": grams,
        "dense_flops_per_gram": per_gram,
        "current_total_flops": current,
        "ideal_half_price_saving_flops": ideal_saving,
        "relative_saving": ideal_saving / V25_FLOPS,
        "threshold_1pct_flops": threshold,
        "materiality_pass": ideal_saving >= threshold,
    }


def run_fixture(source: Path, out: Path):
    raw = source.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != EXPECTED_V25_BLOB:
        raise SystemExit(f"V25 blob mismatch: {blob}")

    text = raw.decode("utf-8")
    required = [
        'AGE_OLD = int(_os.environ.get("V21_AGE_OLD", "4"))',
        'R_OLD = int(_os.environ.get("V21_R_OLD", "384"))',
        'AGE_OLD2 = int(_os.environ.get("V24_AGE_OLD2", "7"))',
        'R_OLD2 = int(_os.environ.get("V24_R_OLD2", "224"))',
        'Sj = (FAj[0] @ (dAj * FAj[0].T)) + (FPj[0] @ (dPj * FPj[0].T))',
        'S_s = (FA1 @ (dAb * FA1.T)) + (FP1 @ (dPb * FP1.T))',
    ]
    for s in required:
        if s not in text:
            raise AssertionError(f"required source fragment missing: {s}")

    # Tiny deterministic algebraic fixture. Use r=4, n=8 to avoid any estimator
    # execution while preserving the same contraction structure.
    r, n = 4, 8
    F_np = ((np.arange(r * n, dtype=np.float32).reshape(r, n) - 11.0) / 7.0).astype(np.float32)
    d_np = ((np.arange(n, dtype=np.float32) + 1.0) / 9.0).astype(np.float32)

    F = fnp.asarray(F_np)
    d = fnp.asarray(d_np)
    X = F.T

    with flops.BudgetContext(flop_budget=10**8, wall_time_limit_s=10.0, quiet=True) as ctx_b:
        baseline = F @ (d.reshape(-1, 1) * F.T)
    baseline_flops = int(ctx_b.flops_used)

    alias_exception = None
    alias = None
    alias_flops = None
    try:
        with flops.BudgetContext(flop_budget=10**8, wall_time_limit_s=10.0, quiet=True) as ctx_a:
            alias = fnp.einsum("ia,i,ib->ab", X, d, X)
        alias_flops = int(ctx_a.flops_used)
    except Exception as exc:  # preserve exact failure type/message
        alias_exception = {"type": type(exc).__name__, "message": str(exc)}

    bitwise = False if alias is None else bool(np.array_equal(np.asarray(baseline), np.asarray(alias)))
    bound = analytic_bound()

    result = {
        "schema": "arc.whitebox.r235.weighted_alias_gram_fixture.v1",
        "source_git_blob": blob,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "flopscope_version": getattr(flops, "__version__", None),
        "fixture": {
            "r": r,
            "n": n,
            "baseline_flops": baseline_flops,
            "alias_flops": alias_flops,
            "alias_exception": alias_exception,
            "bitwise_equal": bitwise,
        },
        "production_bound": bound,
        "exactness_go": bitwise and alias_exception is None,
        "count_go": alias_flops is not None and alias_flops < baseline_flops,
        "materiality_go": bool(bound["materiality_pass"]),
        "scope": {
            "estimator_executed": False,
            "target_data_used": False,
            "mini100": False,
        },
    }
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    run_fixture(args.source, args.out)


if __name__ == "__main__":
    main()
