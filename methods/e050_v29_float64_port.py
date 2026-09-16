from __future__ import annotations

import hashlib
import types
from dataclasses import dataclass, field
from typing import Any

import numpy as np

UPSTREAM_REPO = "504aldo/whest-p2-cumulant-k3"
UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
UPSTREAM_PATH = "estimators/estimator_v29.py"
UPSTREAM_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
UPSTREAM_RAW = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    f"{UPSTREAM_COMMIT}/{UPSTREAM_PATH}"
)
BUDGET = 2**41
WIDTH = 32
DEPTH = 8
SEED = 50050


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify_upstream_bytes(data: bytes) -> None:
    got = git_blob_sha1(data)
    if got != UPSTREAM_BLOB:
        raise AssertionError(f"upstream blob mismatch: {got} != {UPSTREAM_BLOB}")


def mechanical_float64_source(source: str) -> str:
    marker = "f32 = fnp.float32"
    count = source.count(marker)
    if count != 2:
        raise AssertionError(f"expected exactly two working-dtype sites, found {count}")
    out = source.replace(marker, "f32 = fnp.float64")
    if out.count("f32 = fnp.float64") != 2:
        raise AssertionError("mechanical dtype replacement failed")
    # Reversibility proves there was no second algorithmic text edit.
    if out.replace("f32 = fnp.float64", marker) != source:
        raise AssertionError("float64 port is not a pure reversible dtype transform")
    return out


@dataclass
class TraceRecorder:
    label: str
    records: list[dict[str, Any]] = field(default_factory=list)
    first_nonfinite: dict[str, Any] | None = None
    scan_flops: int = 0

    def capture(self, layer: int, name: str, value: Any) -> None:
        if value is None:
            self.records.append({"layer": int(layer), "name": name, "value": None, "finite": True})
            return
        arr = np.asarray(value).copy()
        self.scan_flops += int(arr.size)
        finite = bool(np.isfinite(arr).all())
        rec = {"layer": int(layer), "name": name, "value": arr, "finite": finite}
        self.records.append(rec)
        if not finite and self.first_nonfinite is None:
            bad = np.argwhere(~np.isfinite(arr))
            rec0 = {"layer": int(layer), "name": name, "shape": list(arr.shape)}
            if bad.size:
                idx = tuple(int(x) for x in bad[0])
                rec0["index"] = list(idx)
                rec0["value"] = repr(arr[idx])
            self.first_nonfinite = rec0


def _inject_once(source: str, needle: str, replacement: str) -> str:
    count = source.count(needle)
    if count != 1:
        raise AssertionError(f"trace anchor count {count}, expected 1: {needle[:80]!r}")
    return source.replace(needle, replacement, 1)


def instrument_source(source: str, recorder_symbol: str = "_E050_RECORDER") -> str:
    # Pure observations at frozen V29 state boundaries. Captures never feed back.
    source = _inject_once(
        source,
        "            mu = W @ mu\n            C_pre = None",
        f"            mu = W @ mu\n            {recorder_symbol}.capture(li, 'mu', mu)\n            C_pre = None",
    )
    source = _inject_once(
        source,
        "            mode = 0 if A_st is None else 1\n",
        f"            {recorder_symbol}.capture(li, 'var', var)\n"
        f"            {recorder_symbol}.capture(li, 'A_st', A_st)\n"
        f"            {recorder_symbol}.capture(li, 'P_st', P_st)\n"
        f"            {recorder_symbol}.capture(li, 'Z_st', Z_st)\n"
        "            mode = 0 if A_st is None else 1\n",
    )
    source = _inject_once(
        source,
        "                if regen:\n                    # F68: exact transported diagonal of the regenerated core",
        f"                {recorder_symbol}.capture(li, 'D3', D3)\n"
        f"                {recorder_symbol}.capture(li, 'D21', D21)\n"
        "                if regen:\n                    # F68: exact transported diagonal of the regenerated core",
    )
    source = _inject_once(
        source,
        "                        dG = t_g + t_v * lam_prev                 # var == diag(C_pre)\n",
        "                        dG = t_g + t_v * lam_prev                 # var == diag(C_pre)\n"
        f"                        {recorder_symbol}.capture(li, 'dG', dG)\n",
    )
    source = _inject_once(
        source,
        "                    dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev  # var == diag(C_pre)\n",
        "                    dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev  # var == diag(C_pre)\n"
        f"                    {recorder_symbol}.capture(li, 'dG', dG)\n",
    )
    source = _inject_once(
        source,
        "            alpha = mu / sigma\n",
        f"            alpha = mu / sigma\n            {recorder_symbol}.capture(li, 'alpha', alpha)\n",
    )
    source = _inject_once(
        source,
        "            W_all = ((APOW @ C1) * phic + (APOW @ C2) * Phic) * (SB @ SELC)\n",
        "            W_all = ((APOW @ C1) * phic + (APOW @ C2) * Phic) * (SB @ SELC)\n"
        f"            {recorder_symbol}.capture(li, 'W_all', W_all)\n",
    )
    source = _inject_once(
        source,
        "                PK2 = fnp.einsum(\"tij,ti,tj,tg->gij\", ABstack, WL2, WR2, fpm[\"IND2\"])\n",
        "                PK2 = fnp.einsum(\"tij,ti,tj,tg->gij\", ABstack, WL2, WR2, fpm[\"IND2\"])\n"
        f"                {recorder_symbol}.capture(li, 'PK2', PK2)\n",
    )
    source = _inject_once(
        source,
        "            PK1 = fnp.einsum(\"ti,ti,tg->gi\", B1stack, WL1, fpm[\"IND1\"])\n",
        "            PK1 = fnp.einsum(\"ti,ti,tg->gi\", B1stack, WL1, fpm[\"IND1\"])\n"
        f"            {recorder_symbol}.capture(li, 'PK1', PK1)\n",
    )
    source = _inject_once(
        source,
        "            K2v, K3v, K4v = K[(2,)], K[(3,)], K[(4,)]\n",
        "            K2v, K3v, K4v = K[(2,)], K[(3,)], K[(4,)]\n"
        f"            {recorder_symbol}.capture(li, 'K2', K2v)\n"
        f"            {recorder_symbol}.capture(li, 'K11', K11)\n",
    )
    source = _inject_once(
        source,
        "            C = flops.as_symmetric(C, symmetry=(0, 1))\n",
        f"            {recorder_symbol}.capture(li, 'C', C)\n"
        "            C = flops.as_symmetric(C, symmetry=(0, 1))\n",
    )
    source = _inject_once(
        source,
        "        return fnp.stack(rows, axis=0)\n",
        f"        _e050_out = fnp.stack(rows, axis=0)\n"
        f"        {recorder_symbol}.capture(L, 'final_output', _e050_out)\n"
        "        return _e050_out\n",
    )
    return source


def build_module(source: str, name: str, recorder: TraceRecorder) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__dict__["_E050_RECORDER"] = recorder
    exec(compile(source, f"<{name}>", "exec"), module.__dict__)
    return module


def compare_arrays(a: np.ndarray, b: np.ndarray) -> tuple[float, float, int]:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if aa.shape != bb.shape:
        return float("inf"), float("inf"), 0
    diff = aa - bb
    max_abs = float(np.max(np.abs(diff))) if diff.size else 0.0
    denom = np.maximum(np.abs(aa), np.abs(bb))
    denom = np.maximum(denom, np.finfo(np.float64).tiny)
    rel_rms = float(np.sqrt(np.mean((diff / denom) ** 2))) if diff.size else 0.0
    # Conservative arithmetic count for diff, abs/max, denom maxes, division, square, mean, sqrt.
    flops = int(diff.size * 8 + 1)
    return max_abs, rel_rms, flops
