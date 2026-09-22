#!/usr/bin/env python3
"""R233 micro-fixture: prove ONEHOT-WICK-ROW-SELECT identity and FLOP delta.

This script never imports or executes the V25 estimator. It statically parses pinned
source constants, reconstructs only _term_prog metadata, and compares the baseline
dense coefficient-matrix transforms with the frozen row-select rewrite.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp

EXPECTED_V25_BLOB = "195373a110215256b759d7c172ba8c923c62e5cc"
EXPECTED_COUNTS = {0: {"d2": 6, "d1": 4}, 1: {"d2": 52, "d1": 14}}
FIXTURE_N = 8


def git_blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode())
    h.update(data)
    return h.hexdigest()


def literal_assignment(tree: ast.AST, name: str):
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise KeyError(name)


def build_term_data(source: str):
    tree = ast.parse(source)
    wick_pairs = literal_assignment(tree, "WICK_PAIRS")
    term_specs = literal_assignment(tree, "TERM_SPECS")
    d2_ips = literal_assignment(tree, "D2_IPS")
    d1_ips = literal_assignment(tree, "D1_IPS")
    mode0_missing = set(literal_assignment(tree, "MODE0_MISSING"))

    # Exact V25 source appends these four wk431 terms after TERM_SPECS is created.
    i = wick_pairs.index
    expected_fragments = [
        "TERM_SPECS[(1, 1)].append(('wk431', 'ones2'",
        "TERM_SPECS[(2, 1)].append(('wk431', 'ones2'",
        "TERM_SPECS[(2, 2)].append(('wk431', 'ones2'",
    ]
    for fragment in expected_fragments:
        if fragment not in source:
            raise AssertionError(f"pinned source append fragment missing: {fragment}")
    term_specs[(1, 1)].append(("wk431", "ones2", i((1, 1)), i((3, 1)), 1.0 / 3.0))
    term_specs[(2, 1)].append(("wk431", "ones2", i((1, 2)), i((3, 1)), 1.0 / 6.0))
    term_specs[(2, 1)].append(("wk431", "ones2", i((3, 2)), i((1, 1)), 1.0 / 6.0))
    term_specs[(2, 2)].append(("wk431", "ones2", i((1, 2)), i((3, 2)), 1.0 / 3.0))

    return wick_pairs, term_specs, d2_ips, d1_ips, mode0_missing


def term_prog(mode, wick_pairs, term_specs, d2_ips, d1_ips, mode0_missing):
    missing = mode0_missing if mode == 0 else set()
    npairs = len(wick_pairs)

    d2 = []
    d1 = []
    for g, ip in enumerate(d2_ips):
        for a, b, wl, wr, coef in term_specs.get(tuple(ip), []):
            if a in missing or b in missing:
                continue
            d2.append((g, a, b, wl, wr, coef))
    for g, ip in enumerate(d1_ips):
        for a, b, wl, wr, coef in term_specs.get(tuple(ip), []):
            if a in missing or b in missing:
                continue
            d1.append((g, a, b, wl, coef))

    sl2 = np.zeros((len(d2), npairs), dtype=np.float32)
    sr2 = np.zeros((len(d2), npairs), dtype=np.float32)
    sl1 = np.zeros((len(d1), npairs), dtype=np.float32)
    for t, (_, _, _, wl, wr, coef) in enumerate(d2):
        sl2[t, wl] = np.float32(coef)
        sr2[t, wr] = np.float32(1.0)
    for t, (_, _, _, wl, coef) in enumerate(d1):
        sl1[t, wl] = np.float32(coef)

    def extract_onehot(mat):
        idx = []
        coef = []
        for row in mat:
            nz = np.flatnonzero(row)
            if len(nz) != 1:
                raise AssertionError(f"row is not one-hot: {row}")
            j = int(nz[0])
            idx.append(j)
            coef.append(float(row[j]))
        return np.asarray(idx, dtype=np.int64), np.asarray(coef, dtype=np.float32)

    sl2_idx, sl2_coef = extract_onehot(sl2)
    sr2_idx, sr2_coef = extract_onehot(sr2)
    sl1_idx, sl1_coef = extract_onehot(sl1)

    if not np.array_equal(sr2_coef, np.ones_like(sr2_coef)):
        raise AssertionError("SR2 coefficients are not all 1")

    return {
        "SL2": sl2,
        "SR2": sr2,
        "SL1": sl1,
        "sl2_idx": sl2_idx,
        "sl2_coef": sl2_coef,
        "sr2_idx": sr2_idx,
        "sl1_idx": sl1_idx,
        "sl1_coef": sl1_coef,
    }


def run_mode(mode: int, p: dict):
    k = p["SL2"].shape[1]
    # Deterministic finite float32 values chosen to exercise signs/fractions.
    wt_np = ((np.arange(k * FIXTURE_N, dtype=np.float32).reshape(k, FIXTURE_N) - 53.0) / 17.0).astype(np.float32)

    WT = fnp.asarray(wt_np)
    SL2 = fnp.asarray(p["SL2"])
    SR2 = fnp.asarray(p["SR2"])
    SL1 = fnp.asarray(p["SL1"])
    i2l = fnp.asarray(p["sl2_idx"])
    i2r = fnp.asarray(p["sr2_idx"])
    i1 = fnp.asarray(p["sl1_idx"])
    c2 = fnp.asarray(p["sl2_coef"].reshape(-1, 1))
    c1 = fnp.asarray(p["sl1_coef"].reshape(-1, 1))

    with flops.BudgetContext(flop_budget=10**9, wall_time_limit_s=10.0, quiet=True) as ctx_b:
        wl2_b = SL2 @ WT
        wr2_b = SR2 @ WT
        wl1_b = SL1 @ WT
    baseline_flops = int(ctx_b.flops_used)

    with flops.BudgetContext(flop_budget=10**9, wall_time_limit_s=10.0, quiet=True) as ctx_c:
        wl2_c = fnp.take(WT, i2l, axis=0) * c2
        wr2_c = fnp.take(WT, i2r, axis=0)
        wl1_c = fnp.take(WT, i1, axis=0) * c1
    candidate_flops = int(ctx_c.flops_used)

    eq = {
        "WL2": bool(np.array_equal(np.asarray(wl2_b), np.asarray(wl2_c))),
        "WR2": bool(np.array_equal(np.asarray(wr2_b), np.asarray(wr2_c))),
        "WL1": bool(np.array_equal(np.asarray(wl1_b), np.asarray(wl1_c))),
    }

    t2 = int(p["SL2"].shape[0])
    t1 = int(p["SL1"].shape[0])
    expected_baseline = (2 * t2 + t1) * FIXTURE_N * (2 * k - 1)
    expected_candidate = (9 * t2 + 5 * t1) * FIXTURE_N

    return {
        "mode": mode,
        "k": k,
        "n": FIXTURE_N,
        "d2_terms": t2,
        "d1_terms": t1,
        "bitwise_equal": eq,
        "baseline_flops": baseline_flops,
        "candidate_flops": candidate_flops,
        "measured_saving": baseline_flops - candidate_flops,
        "expected_baseline_flops": expected_baseline,
        "expected_candidate_flops": expected_candidate,
        "expected_saving": expected_baseline - expected_candidate,
        "cost_exact": baseline_flops == expected_baseline and candidate_flops == expected_candidate,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    raw = args.source.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != EXPECTED_V25_BLOB:
        raise SystemExit(f"V25 blob mismatch: {blob}")

    source = raw.decode("utf-8")
    wick_pairs, term_specs, d2_ips, d1_ips, mode0_missing = build_term_data(source)

    results = []
    for mode in (0, 1):
        p = term_prog(mode, wick_pairs, term_specs, d2_ips, d1_ips, mode0_missing)
        got = {"d2": int(p["SL2"].shape[0]), "d1": int(p["SL1"].shape[0])}
        if got != EXPECTED_COUNTS[mode]:
            raise AssertionError(f"mode {mode} count mismatch: {got}")
        results.append(run_mode(mode, p))

    identity_go = all(all(r["bitwise_equal"].values()) for r in results)
    count_go = all(r["cost_exact"] and r["measured_saving"] > 0 for r in results)

    out = {
        "schema": "arc.whitebox.r233.onehot_wick_fixture.v1",
        "source_git_blob": blob,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "flopscope_version": getattr(flops, "__version__", None),
        "fixture_n": FIXTURE_N,
        "results": results,
        "identity_go": identity_go,
        "count_go": count_go,
        "scope": {
            "estimator_executed": False,
            "mini100": False,
            "target_data_used": False,
        },
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    if not (identity_go and count_go):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
