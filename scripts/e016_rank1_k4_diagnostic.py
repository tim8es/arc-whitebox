from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench

from methods.e016_rank1_k4 import apply_rank1_mode, build_q, fit_gamma, offdiag_outer

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
LEAN_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/lean/lean_k3_aug.py"
)
EXPECTED_LEAN_BLOB = "8fdaa96fd68f30ce9020e6534626e97ebf71d291"
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
FIT_INDICES = (0, 1, 2, 3)
VALID_INDICES = (4, 5, 6, 7)
SCORED_LAYERS = tuple(range(8, 15))
N = 1024
FLOP_BUDGET = 2**41
E007_RAW = 2.23e-8
E007_UTIL = 0.36666448
E007_ADJUSTED = 8.17e-9
UTIL_GATE = 0.36866448
K4_IMPROVEMENT_GATE = 0.20
RAW_GAIN_GATE = 0.01
WORST_RATIO_GATE = 1.05
RESIDUAL_EXTRA_GATE_S = 0.005
PROXY_REPS = 7
# V25 pre-activation table, including its shipped 0.95 scale.
LAM_BASE = np.asarray(
    [
        4.9895e-03,
        8.0876e-03,
        9.8291e-03,
        1.0549e-02,
        1.0851e-02,
        1.0828e-02,
        1.0589e-02,
        1.0048e-02,
        9.6483e-03,
        9.1720e-03,
        8.7730e-03,
        8.3938e-03,
        8.0555e-03,
        7.6770e-03,
        7.2588e-03,
        7.2588e-03,
    ],
    dtype=np.float64,
) * 0.95
REF_R = np.asarray(
    [
        6.58815e-03,
        8.18414e-03,
        8.53136e-03,
        8.38859e-03,
        8.10153e-03,
        7.74287e-03,
        7.35951e-03,
        6.91093e-03,
        6.55752e-03,
        6.17892e-03,
        5.83953e-03,
        5.56824e-03,
        5.32459e-03,
        5.05165e-03,
        4.77181e-03,
    ],
    dtype=np.float64,
)


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity


def _instrument_source(source: str) -> str:
    sig = '                    age_rank=None, age_eig="exact"):'
    if sig not in source:
        raise RuntimeError("lean signature marker not found")
    source = source.replace(sig, '                    age_rank=None, age_eig="exact", pre_g_hook=None):', 1)
    marker = (
        "            else:\n"
        "                G = W @ G @ W.T\n"
        "                G = 0.5 * (G + G.T)\n"
    )
    if marker not in source:
        raise RuntimeError("dense K4 transport marker not found")
    replacement = marker + (
        "            if pre_g_hook is not None:\n"
        "                G = pre_g_hook(l, G, C)\n"
    )
    return source.replace(marker, replacement, 1)


def _load_lean_module():
    with urllib.request.urlopen(LEAN_URL, timeout=30) as response:  # noqa: S310
        data = response.read()
    blob = _git_blob_sha(data)
    if blob != EXPECTED_LEAN_BLOB:
        raise RuntimeError(f"lean blob mismatch: {blob} != {EXPECTED_LEAN_BLOB}")
    patched = _instrument_source(data.decode("utf-8"))
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    try:
        temp.write(patched)
        temp.close()
        spec = importlib.util.spec_from_file_location("e016_lean_k3_aug", temp.name)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import patched lean module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.torch.set_num_threads(2)
        return module, blob
    finally:
        Path(temp.name).unlink(missing_ok=True)


def _offdiag(a: np.ndarray) -> np.ndarray:
    out = np.asarray(a, dtype=np.float64).copy()
    np.fill_diagonal(out, 0.0)
    return out


def _lambda_for_pre_layer(layer: int, dg: np.ndarray, var: np.ndarray) -> float:
    if layer <= 0:
        return 0.0
    idx = min(layer - 1, len(REF_R) - 1)
    mean_var = float(np.mean(var, dtype=np.float64))
    rr = float(np.mean(dg, dtype=np.float64)) / mean_var
    scale = float(np.clip(rr / REF_R[idx], 0.5, 2.0))
    return float(LAM_BASE[min(layer - 1, len(LAM_BASE) - 1)] * scale)


def _relative_rms(pred: np.ndarray, truth: np.ndarray) -> float:
    truth64 = np.asarray(truth, dtype=np.float64)
    pred64 = np.asarray(pred, dtype=np.float64)
    denom = float(np.sqrt(np.mean(truth64 * truth64)))
    if denom == 0.0:
        return 0.0 if np.array_equal(pred64, truth64) else float("inf")
    return float(np.sqrt(np.mean((pred64 - truth64) ** 2)) / denom)


def _row(ds, index: int):
    row = ds[index]
    weights = np.asarray(row["weights"], dtype=np.float64).reshape(16, N, N)
    gt = np.asarray(row["final_means"], dtype=np.float64).reshape(N)
    return weights, gt


@dataclass
class FitAccumulator:
    samples: dict[int, list]

    def __call__(self, layer, g, c):
        if layer not in SCORED_LAYERS:
            return g
        g_np = np.asarray(g.detach().cpu().numpy(), dtype=np.float64)
        c_np = np.asarray(c.detach().cpu().numpy(), dtype=np.float64)
        dg = np.diag(g_np).copy()
        var = np.diag(c_np).copy()
        c_off = _offdiag(c_np)
        teacher = _offdiag(g_np)
        lam = _lambda_for_pre_layer(layer, dg, var)
        self.samples[layer].append((teacher, c_off, dg, var, lam))
        return g


@dataclass
class StructuralValidator:
    gamma: dict[int, float]
    rows: list[dict]
    deterministic: bool = True

    def __call__(self, layer, g, c):
        if layer not in SCORED_LAYERS:
            return g
        g_np = np.asarray(g.detach().cpu().numpy(), dtype=np.float64)
        c_np = np.asarray(c.detach().cpu().numpy(), dtype=np.float64)
        dg = np.diag(g_np).copy()
        var = np.diag(c_np).copy()
        c_off = _offdiag(c_np)
        truth = _offdiag(g_np)
        lam = _lambda_for_pre_layer(layer, dg, var)
        baseline = lam * c_off
        candidate = apply_rank1_mode(c_off, dg, var, lam=lam, gamma=self.gamma[layer])
        candidate2 = apply_rank1_mode(c_off, dg, var, lam=lam, gamma=self.gamma[layer])
        self.deterministic = self.deterministic and np.array_equal(candidate, candidate2)
        base_err = _relative_rms(baseline, truth)
        cand_err = _relative_rms(candidate, truth)
        self.rows.append(
            {
                "layer": int(layer),
                "baseline_relative_rms": base_err,
                "candidate_relative_rms": cand_err,
                "ratio": cand_err / base_err if base_err > 0 else float("inf"),
                "lambda": lam,
            }
        )
        return g


class ReplayClosure:
    def __init__(self, module, gamma: dict[int, float] | None):
        self.module = module
        self.gamma = gamma or {}
        self.finite = True

    def __call__(self, layer, g, c):
        if layer <= 0:
            return g
        g_np = np.asarray(g.detach().cpu().numpy(), dtype=np.float64)
        c_np = np.asarray(c.detach().cpu().numpy(), dtype=np.float64)
        dg = np.diag(g_np).copy()
        var = np.diag(c_np).copy()
        c_off = _offdiag(c_np)
        lam = _lambda_for_pre_layer(layer, dg, var)
        gamma = float(self.gamma.get(layer, 0.0))
        off = apply_rank1_mode(c_off, dg, var, lam=lam, gamma=gamma)
        closed = off
        np.fill_diagonal(closed, dg)
        self.finite = self.finite and bool(np.all(np.isfinite(closed)))
        return self.module.torch.as_tensor(closed, dtype=g.dtype)


def _run_lean(module, weights, statics, hook, *, teacher: bool):
    kwargs = dict(k4_aug=True, pre_g_hook=hook)
    if not teacher:
        # Frozen memoryless-K4 replay lane from F68: the expensive K211 production is absent.
        kwargs["aug_no_k211"] = True
    return module.lean_k3_predict(weights, statics=statics, **kwargs).detach().cpu().numpy()


def _measure_proxy_once(seed: int):
    rng = np.random.default_rng(seed)
    w = fnp.asarray(rng.standard_normal((N, N), dtype=np.float32))
    q = fnp.asarray(rng.standard_normal(N, dtype=np.float32))
    tmp = fnp.empty(N, dtype=fnp.float32)
    acc = fnp.empty(N, dtype=fnp.float32)
    with flops.BudgetContext(flop_budget=10_000_000_000, wall_time_limit_s=30.0) as ctx:
        # Conservative production proxy: four dense vector transports per active layer.
        for _ in SCORED_LAYERS:
            fnp.matmul(w, q, out=tmp)
            fnp.multiply(tmp, 0.5, out=acc)
            fnp.matmul(w, acc, out=tmp)
            fnp.add(tmp, q, out=acc)
            fnp.matmul(w, acc, out=tmp)
            fnp.multiply(tmp, 0.25, out=acc)
            fnp.matmul(w, acc, out=tmp)
    return int(ctx.flops_used), float(ctx.residual_wall_time_s)


def _measure_proxy():
    _measure_proxy_once(1600)
    rows = [_measure_proxy_once(1610 + i) for i in range(PROXY_REPS)]
    return {
        "extra_flops": rows[0][0],
        "residual_s_all": [x[1] for x in rows],
        "residual_s_median": statistics.median(x[1] for x in rows),
    }


def main() -> int:
    t0 = time.perf_counter()
    module, blob = _load_lean_module()
    ds = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
    statics = module.build_static_coefs(N)

    fit_samples = {layer: [] for layer in SCORED_LAYERS}
    fit_meta = []
    for index in FIT_INDICES:
        weights, _ = _row(ds, index)
        hook = FitAccumulator(fit_samples)
        start = time.perf_counter()
        pred = _run_lean(module, weights, statics, hook, teacher=True)
        fit_meta.append(
            {"index": index, "finite": bool(np.all(np.isfinite(pred))), "wall_s": time.perf_counter() - start}
        )

    gamma = {layer: fit_gamma(fit_samples[layer]) for layer in SCORED_LAYERS}
    gamma_repeat = {layer: fit_gamma(fit_samples[layer]) for layer in SCORED_LAYERS}
    fit_deterministic = all(gamma[layer] == gamma_repeat[layer] for layer in SCORED_LAYERS)

    structural_rows = []
    structural_meta = []
    for index in VALID_INDICES:
        weights, _ = _row(ds, index)
        hook = StructuralValidator(gamma, [])
        start = time.perf_counter()
        pred = _run_lean(module, weights, statics, hook, teacher=True)
        for row in hook.rows:
            row["index"] = index
            structural_rows.append(row)
        structural_meta.append(
            {
                "index": index,
                "finite": bool(np.all(np.isfinite(pred))),
                "deterministic": hook.deterministic,
                "wall_s": time.perf_counter() - start,
            }
        )

    baseline_mses = []
    candidate_mses = []
    replay_meta = []
    for index in VALID_INDICES:
        weights, gt = _row(ds, index)
        base_hook = ReplayClosure(module, None)
        cand_hook = ReplayClosure(module, gamma)
        start = time.perf_counter()
        baseline = _run_lean(module, weights, statics, base_hook, teacher=False)
        base_wall = time.perf_counter() - start
        start = time.perf_counter()
        candidate = _run_lean(module, weights, statics, cand_hook, teacher=False)
        cand_wall = time.perf_counter() - start
        base_mse = float(np.mean((baseline[-1] - gt) ** 2))
        cand_mse = float(np.mean((candidate[-1] - gt) ** 2))
        baseline_mses.append(base_mse)
        candidate_mses.append(cand_mse)
        replay_meta.append(
            {
                "index": index,
                "baseline_mse": base_mse,
                "candidate_mse": cand_mse,
                "baseline_wall_s": base_wall,
                "candidate_wall_s": cand_wall,
                "finite": bool(base_hook.finite and cand_hook.finite and np.all(np.isfinite(candidate))),
            }
        )

    base_core_mean = float(np.mean([r["baseline_relative_rms"] for r in structural_rows]))
    cand_core_mean = float(np.mean([r["candidate_relative_rms"] for r in structural_rows]))
    core_improvement = 1.0 - cand_core_mean / base_core_mean
    worst_ratio = float(max(r["ratio"] for r in structural_rows))
    baseline_mse = float(np.mean(baseline_mses))
    candidate_mse = float(np.mean(candidate_mses))
    raw_ratio = candidate_mse / baseline_mse
    raw_gain = 1.0 - raw_ratio

    proxy = _measure_proxy()
    projected_util = E007_UTIL + proxy["extra_flops"] / FLOP_BUDGET
    projected_raw = E007_RAW * raw_ratio
    projected_adjusted = projected_raw * projected_util
    extra_state_bytes = 3 * N * 4  # q, transported-q, one existing thin-vector slot

    gates = {
        "k4_core_improvement": core_improvement >= K4_IMPROVEMENT_GATE,
        "worst_structural_regression": worst_ratio <= WORST_RATIO_GATE,
        "end_to_end_raw_gain": raw_gain >= RAW_GAIN_GATE,
        "projected_adjusted": projected_adjusted < E007_ADJUSTED,
        "projected_utilization": projected_util <= UTIL_GATE,
        "shared_layer_coefficients_only": len(gamma) == 7,
        "deterministic": fit_deterministic and all(x["deterministic"] for x in structural_meta),
        "finite": all(x["finite"] for x in fit_meta + structural_meta + replay_meta)
        and all(np.isfinite(list(gamma.values()))),
        "residual_resource": proxy["residual_s_median"] <= RESIDUAL_EXTRA_GATE_S
        and extra_state_bytes <= 3 * N * 4,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    result = {
        "experiment": "E016",
        "decision": decision,
        "scope": "public dev 0-3 fit, 4-7 frozen validation; no official scorer/holdout",
        "upstream_commit": UPSTREAM_COMMIT,
        "lean_blob": blob,
        "fit_indices": list(FIT_INDICES),
        "validation_indices": list(VALID_INDICES),
        "scored_layers": list(SCORED_LAYERS),
        "gamma_by_layer": {str(k): v for k, v in gamma.items()},
        "fit_meta": fit_meta,
        "structural_meta": structural_meta,
        "structural_rows": structural_rows,
        "baseline_k4_core_mean_relative_rms": base_core_mean,
        "candidate_k4_core_mean_relative_rms": cand_core_mean,
        "k4_core_relative_rms_improvement": core_improvement,
        "worst_candidate_to_baseline_core_error_ratio": worst_ratio,
        "replay": replay_meta,
        "baseline_validation_final_mse": baseline_mse,
        "candidate_validation_final_mse": candidate_mse,
        "validation_raw_mse_ratio": raw_ratio,
        "validation_raw_mse_gain": raw_gain,
        "proxy": proxy,
        "extra_state_bytes": extra_state_bytes,
        "projected_total_utilization": projected_util,
        "projected_raw_from_e007": projected_raw,
        "projected_adjusted_from_e007": projected_adjusted,
        "gates": gates,
        "wall_s_total": time.perf_counter() - t0,
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    print(f"DECISION={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
