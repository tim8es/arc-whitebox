from __future__ import annotations

import gc
import hashlib
import json
import math
import types
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import numpy as np
from whestbench import SetupContext

BUDGET = 2**41
WIDTH = 1024
DEPTH = 16
SEED = 94194
SETUP_SEED = 0
TAIL_TOL = 1e-3
TARGET_UNITS = 138.24
NON_SOURCE_UNITS = 37.59
YOUNG_UNITS = 115.61
OLD_UNITS = 106.83

PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v29.py"
PINNED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
OUT = Path("e094-spectrum-probe.json")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def load_exact_v29():
    url = (
        f"https://raw.githubusercontent.com/{PINNED_REPO}/"
        f"{PINNED_COMMIT}/{PINNED_PATH}"
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
    observed = git_blob_sha(raw)
    if observed != PINNED_BLOB:
        raise RuntimeError(f"V29 blob mismatch: {observed}")
    mod = types.ModuleType("e094_exact_v29")
    exec(compile(raw.decode("utf-8"), "<e094_exact_v29>", "exec"), mod.__dict__)
    return mod, observed


def synthetic_mlp():
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = 1.0 / math.sqrt(WIDTH)
    weights = [
        rng.normal(0.0, scale, size=(WIDTH, WIDTH)).astype(np.float32)
        for _ in range(DEPTH)
    ]
    return SimpleNamespace(width=WIDTH, depth=DEPTH, weights=weights)


def setup_estimator(estimator) -> None:
    estimator.setup(
        SetupContext(
            width=WIDTH,
            depth=DEPTH,
            flop_budget=BUDGET,
            api_version="1",
            seed=SETUP_SEED,
        )
    )


def run_exact(estimator, mlp):
    setup_estimator(estimator)
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        pred = estimator.predict(mlp, BUDGET)
    estimator.teardown()
    return np.asarray(pred).copy(), int(ctx.flops_used)


def pair_gram(x: np.ndarray, y: np.ndarray, chunk: int = 65536) -> np.ndarray:
    xa = np.asarray(x, dtype=np.float32)
    ya = np.asarray(y, dtype=np.float32)
    if xa.shape != ya.shape or xa.ndim != 3:
        raise ValueError(f"expected paired stacks (S,n,n), got {xa.shape} and {ya.shape}")
    s = xa.shape[0]
    xf = xa.reshape(s, -1)
    yf = ya.reshape(s, -1)
    g = np.zeros((s, s), dtype=np.float64)
    for lo in range(0, xf.shape[1], chunk):
        hi = min(lo + chunk, xf.shape[1])
        xc = xf[:, lo:hi].astype(np.float64, copy=False)
        yc = yf[:, lo:hi].astype(np.float64, copy=False)
        g += xc @ xc.T
        g += yc @ yc.T
    return 0.5 * (g + g.T)


def spectrum_summary(g: np.ndarray, lo: int, hi: int) -> dict[str, object]:
    sub = np.asarray(g[lo:hi, lo:hi], dtype=np.float64)
    eig = np.linalg.eigvalsh(sub)
    eig = np.maximum(eig, 0.0)[::-1]
    total = float(np.sum(eig))
    if not np.isfinite(total) or total <= 0.0:
        raise FloatingPointError("invalid source-axis Gram energy")
    rel_tail = []
    rank_needed = len(eig)
    for r in range(1, len(eig) + 1):
        tail = float(np.sum(eig[r:]))
        err = math.sqrt(max(tail, 0.0) / total)
        rel_tail.append(err)
        if err <= TAIL_TOL and rank_needed == len(eig):
            rank_needed = r
    singular = np.sqrt(eig)
    lead = float(singular[0])
    return {
        "count": int(len(eig)),
        "rank_needed_at_tail_tol": int(rank_needed),
        "relative_tail_by_rank": [float(v) for v in rel_tail],
        "singular_value_ratios": [float(v / lead) for v in singular],
        "gram_trace": total,
    }


def main() -> None:
    mod, observed_blob = load_exact_v29()
    mlp = synthetic_mlp()

    base_est = mod.Estimator()
    baseline_pred, baseline_flops = run_exact(base_est, mlp)
    baseline_finite = bool(np.isfinite(baseline_pred).all())
    del base_est
    gc.collect()

    capture: dict[str, object] = {}
    inst_est = mod.Estimator()
    original_dslices = inst_est._dslices

    def wrapped_dslices(*args, **kwargs):
        a_st = args[0]
        p_st = args[1]
        bufs = args[11]
        need_d21 = bool(kwargs.get("need_d21", True))
        ka = int(kwargs.get("ka", 0))
        k = int(a_st.shape[0])

        should_capture = need_d21 and k == 14
        if should_capture:
            if capture:
                raise RuntimeError("spectrum capture condition hit more than once")
            right_gram = pair_gram(a_st, p_st)
        else:
            right_gram = None

        result = original_dslices(*args, **kwargs)

        if should_capture:
            lap = np.asarray(bufs["lap"])
            if lap.ndim != 4 or lap.shape[0] < k or lap.shape[1] != 2:
                raise RuntimeError(f"unexpected lap buffer shape {lap.shape}")
            left_gram = pair_gram(lap[:k, 0], lap[:k, 1])
            capture.update(
                {
                    "k": k,
                    "ka": ka,
                    "kb": int(kwargs.get("kb", 0)),
                    "right_gram": right_gram,
                    "left_gram": left_gram,
                }
            )
        return result

    inst_est._dslices = wrapped_dslices
    instrumented_pred, instrumented_flops = run_exact(inst_est, mlp)
    instrumented_finite = bool(np.isfinite(instrumented_pred).all())

    if not capture:
        raise RuntimeError("frozen source-spectrum capture condition was never reached")

    k = int(capture["k"])
    ka = int(capture["ka"])
    young_count = k - ka
    old_count = ka
    if young_count <= 0 or old_count <= 0:
        raise RuntimeError(f"invalid frozen group sizes old={old_count}, young={young_count}")

    right_g = np.asarray(capture["right_gram"], dtype=np.float64)
    left_g = np.asarray(capture["left_gram"], dtype=np.float64)
    old_right = spectrum_summary(right_g, 0, ka)
    old_left = spectrum_summary(left_g, 0, ka)
    young_right = spectrum_summary(right_g, ka, k)
    young_left = spectrum_summary(left_g, ka, k)

    rank_old = max(
        int(old_right["rank_needed_at_tail_tol"]),
        int(old_left["rank_needed_at_tail_tol"]),
    )
    rank_young = max(
        int(young_right["rank_needed_at_tail_tol"]),
        int(young_left["rank_needed_at_tail_tol"]),
    )
    fo = rank_old / old_count
    fy = rank_young / young_count
    projected_units = NON_SOURCE_UNITS + YOUNG_UNITS * fy + OLD_UNITS * fo

    prediction_equal = bool(np.array_equal(baseline_pred, instrumented_pred))
    prediction_max_abs = float(np.max(np.abs(
        baseline_pred.astype(np.float64) - instrumented_pred.astype(np.float64)
    )))
    flops_equal = baseline_flops == instrumented_flops

    gates = {
        "upstream_blob_verified": observed_blob == PINNED_BLOB,
        "finite": baseline_finite and instrumented_finite,
        "prediction_bitwise_identical": prediction_equal,
        "prediction_flops_identical": flops_equal,
        "capture_exactly_once": True,
        "expected_group_geometry": (
            k == 14 and ka == 10 and old_count == 10 and young_count == 4
        ),
        "projected_units_le_138_24": projected_units <= TARGET_UNITS,
    }

    decision = (
        "SPECTRUM_FEASIBILITY_GO_ONLY"
        if all(gates.values())
        else "TERMINAL_E094_NO_GO"
    )

    result = {
        "schema": "arc.whitebox.e094.spectrum_probe.v1",
        "experiment": "E094",
        "upstream_blob": observed_blob,
        "synthetic": {
            "width": WIDTH,
            "depth": DEPTH,
            "seed": SEED,
            "setup_seed": SETUP_SEED,
            "targets_read": False,
        },
        "prediction_identity": {
            "baseline_finite": baseline_finite,
            "instrumented_finite": instrumented_finite,
            "bitwise_equal": prediction_equal,
            "max_abs": prediction_max_abs,
            "baseline_flops": baseline_flops,
            "instrumented_flops": instrumented_flops,
        },
        "capture": {
            "k": k,
            "ka": ka,
            "kb": int(capture["kb"]),
            "old_count": old_count,
            "young_count": young_count,
        },
        "tail_tolerance": TAIL_TOL,
        "spectra": {
            "old_right_AP": old_right,
            "old_left_LALP": old_left,
            "young_right_AP": young_right,
            "young_left_LALP": young_left,
        },
        "required_ranks": {
            "old": rank_old,
            "young": rank_young,
            "old_remaining_fraction": fo,
            "young_remaining_fraction": fy,
        },
        "cost_projection": {
            "non_source_units": NON_SOURCE_UNITS,
            "young_source_units": YOUNG_UNITS,
            "old_source_units": OLD_UNITS,
            "projected_units": projected_units,
            "target_units": TARGET_UNITS,
            "projected_utilization": projected_units / 1024.0,
        },
        "gates": gates,
        "decision": decision,
        "scientific_go": False,
        "scope": {
            "public": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E094_SPECTRUM_PROBE=" + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
