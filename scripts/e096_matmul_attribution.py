from __future__ import annotations

import collections
import hashlib
import inspect
import json
import linecache
import math
import sys
import types
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
RAW_URL = f"https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/{UPSTREAM_COMMIT}/estimators/estimator_v29.py"
WIDTH = 1024
DEPTH = 16
SEED = 96096
BUDGET = 2**41
E051_FLOPS = 587262754287
TARGET_FLOPS = 0.135 * BUDGET


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load_v29():
    with urllib.request.urlopen(RAW_URL, timeout=60) as r:
        data = r.read()
    observed = blob_sha(data)
    if observed != EXPECTED_BLOB:
        raise RuntimeError(f"blob mismatch {observed} != {EXPECTED_BLOB}")
    source = data.decode("utf-8")
    filename = f"<e096_v29:{EXPECTED_BLOB}>"
    # Seed linecache so inspect/source-line attribution is deterministic for exec'd source.
    lines = source.splitlines(True)
    linecache.cache[filename] = (len(data), None, lines, filename)
    mod = types.ModuleType("e096_v29")
    mod.__file__ = filename
    sys.modules[mod.__name__] = mod
    exec(compile(source, filename, "exec"), mod.__dict__)
    return mod, observed, filename


def make_mlp():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = np.sqrt(2.0 / WIDTH)
    weights = [
        fnp.asarray(rng.normal(0.0, scale, size=(WIDTH, WIDTH)).astype(np.float32), dtype=fnp.float32)
        for _ in range(DEPTH)
    ]
    return SimpleNamespace(width=WIDTH, depth=DEPTH, weights=weights)


def matmul_dims(a, b):
    ash = tuple(int(x) for x in getattr(a, "shape", ()))
    bsh = tuple(int(x) for x in getattr(b, "shape", ()))
    if len(ash) < 2 or len(bsh) < 2:
        return None
    m, k = ash[-2:]
    kb, n = bsh[-2:]
    if k != kb:
        return None
    try:
        batch_shape = np.broadcast_shapes(ash[:-2], bsh[:-2])
    except ValueError:
        return None
    batch = int(math.prod(batch_shape)) if batch_shape else 1
    est = int(batch * m * n * max(1, 2 * k - 1))
    return batch, m, k, n, est


class Profiler:
    def __init__(self, target_filename: str):
        self.target_filename = target_filename
        self.original = fnp.matmul
        self.groups = collections.Counter()
        self.lines = collections.Counter()
        self.calls = 0
        self.total = 0
        self.unattributed = 0

    def wrapped(self, a, b, *args, **kwargs):
        dims = matmul_dims(a, b)
        frame = inspect.currentframe().f_back
        fn = frame.f_code.co_name if frame is not None else "<unknown>"
        lineno = frame.f_lineno if frame is not None else -1
        filename = frame.f_code.co_filename if frame is not None else "<unknown>"
        source = linecache.getline(filename, lineno).strip() if lineno > 0 else ""
        if dims is None:
            batch = m = k = n = est = 0
        else:
            batch, m, k, n, est = dims
        self.calls += 1
        self.total += est
        if filename != self.target_filename:
            self.unattributed += est
        key = (fn, lineno, source, batch, m, k, n)
        self.groups[key] += est
        self.lines[(fn, lineno, source)] += est
        return self.original(a, b, *args, **kwargs)

    def install(self):
        fnp.matmul = self.wrapped

    def restore(self):
        fnp.matmul = self.original


def serialize_counter(counter, limit=None):
    rows = []
    for key, flp in counter.most_common(limit):
        if len(key) == 7:
            fn, line, source, batch, m, k, n = key
            rows.append({"function": fn, "line": line, "source": source, "batch": batch,
                         "m": m, "k": k, "n": n, "estimated_flops": int(flp)})
        else:
            fn, line, source = key
            rows.append({"function": fn, "line": line, "source": source,
                         "estimated_flops": int(flp)})
    return rows


def main():
    out = {"experiment": "E096", "stage": "A", "width": WIDTH, "depth": DEPTH,
           "seed": SEED, "budget": BUDGET, "target_flops": TARGET_FLOPS}
    try:
        mod, observed_blob, filename = load_v29()
        mlp = make_mlp()
        estimator = mod.Estimator()
        estimator.setup(SetupContext(width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
                                     api_version="1", seed=SEED))
        profiler = Profiler(filename)
        profiler.install()
        try:
            with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
                pred = estimator.predict(mlp, BUDGET)
        finally:
            profiler.restore()
        estimator.teardown()
        pred_np = np.asarray(pred)
        measured = int(ctx.flops_used)
        coverage = profiler.total / measured if measured else 0.0
        top_groups = serialize_counter(profiler.groups, 30)
        top_lines = serialize_counter(profiler.lines, 30)
        top3 = sum(r["estimated_flops"] for r in top_lines[:3])
        required_saving = max(0.0, measured - TARGET_FLOPS)
        fraction_top3 = required_saving / top3 if top3 else float("inf")
        out.update({
            "source_blob": observed_blob,
            "predict_flops": measured,
            "utilization": measured / BUDGET,
            "reference_flop_drift_fraction": abs(measured - E051_FLOPS) / E051_FLOPS,
            "finite": bool(np.isfinite(pred_np).all()),
            "matmul_calls": profiler.calls,
            "matmul_estimated_flops": int(profiler.total),
            "matmul_coverage_fraction": coverage,
            "unattributed_matmul_flops": int(profiler.unattributed),
            "top_groups": top_groups,
            "top_lines": top_lines,
            "top3_line_flops": int(top3),
            "top3_fraction_of_predict": top3 / measured if measured else 0.0,
            "required_saving_flops": required_saving,
            "required_fraction_of_top3_if_only_top3_changed": fraction_top3,
        })
        gates = {
            "source_hash": observed_blob == EXPECTED_BLOB,
            "finite": out["finite"],
            "reference_flops": out["reference_flop_drift_fraction"] <= 0.005,
            "matmul_coverage": coverage >= 0.80,
            "nonempty": bool(top_groups) and profiler.total > 0,
            "reconcile": sum(profiler.groups.values()) == profiler.total,
        }
        out["gates"] = gates
        out["valid"] = bool(all(gates.values()))
        out["terminal"] = "VALID_ATTRIBUTION" if out["valid"] else "INVALID_NO-GO"
    except Exception as exc:
        out.update({"error_type": type(exc).__name__, "error": str(exc), "valid": False,
                    "terminal": "INVALID_NO-GO"})

    Path("e096-attribution.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print("E096_ATTRIBUTION_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    if not out.get("valid"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
