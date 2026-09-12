"""Patch pinned upstream V25 with an E008 diagnostic-only TensorSketch probe.

The patched estimator is never used for a competition score.  It runs exactly one
public mini MLP and, at layer 14, compares degree-2 TensorSketch reconstructions of
old-source A*P, A*A and P*P against the exact dense products already present in V25.
This is a necessary-condition probe before implementing the full factor-space D21
contraction.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HELPER = r'''

def _e008_count_sketch_rows(X, h, s, m):
    X = _e008_np.asarray(X, dtype=_e008_np.float64)
    out = _e008_np.zeros((X.shape[0], m), dtype=_e008_np.float64)
    for jj in range(X.shape[1]):
        out[:, int(h[jj])] += X[:, jj] * float(s[jj])
    return out


def _e008_maps(r, m):
    # Fixed before data inspection; no seed sweep.
    rng = _e008_np.random.default_rng(20260912 + 1000003 * int(r) + 1009 * int(m))
    h1 = rng.integers(0, m, size=r, dtype=_e008_np.int64)
    h2 = rng.integers(0, m, size=r, dtype=_e008_np.int64)
    s1 = rng.choice(_e008_np.asarray([-1.0, 1.0]), size=r)
    s2 = rng.choice(_e008_np.asarray([-1.0, 1.0]), size=r)
    return h1, h2, s1, s2


def _e008_ts2(X, Y, maps, m):
    h1, h2, s1, s2 = maps
    c1 = _e008_count_sketch_rows(X, h1, s1, m)
    c2 = _e008_count_sketch_rows(Y, h2, s2, m)
    return _e008_np.fft.ifft(
        _e008_np.fft.fft(c1, axis=1) * _e008_np.fft.fft(c2, axis=1),
        axis=1,
    ).real


def _e008_rel(num, den):
    return float(_e008_np.sqrt(num / max(den, 1e-300)))


def _e008_probe_products(A_st, P_st, ka, kb, Qc, U2, FAo, FPo, FA2, FP2):
    import json as _e008_json

    if ka <= 0:
        return
    A_all = _e008_np.asarray(A_st, dtype=_e008_np.float64)
    P_all = _e008_np.asarray(P_st, dtype=_e008_np.float64)
    Q1 = _e008_np.asarray(Qc, dtype=_e008_np.float64)
    Q2 = None
    if kb > 0:
        Q2 = Q1 @ _e008_np.asarray(U2, dtype=_e008_np.float64)

    source_specs = []
    if kb > 0:
        fa2 = _e008_np.asarray(FA2, dtype=_e008_np.float64)
        fp2 = _e008_np.asarray(FP2, dtype=_e008_np.float64)
        for ss in range(int(kb)):
            source_specs.append((ss, Q2, fa2[ss], fp2[ss], "tier2"))
    if ka > kb:
        fao = _e008_np.asarray(FAo, dtype=_e008_np.float64)
        fpo = _e008_np.asarray(FPo, dtype=_e008_np.float64)
        for ss in range(int(kb), int(ka)):
            source_specs.append((ss, Q1, fao[ss - int(kb)], fpo[ss - int(kb)], "tier1"))

    # Verify that the factor coordinates correspond to the exact old dense legs at
    # this point in V25.  If this fails the probe is invalid and must not be read.
    rec_a_num = rec_a_den = rec_p_num = rec_p_den = 0.0
    for ss, basis, fa, fp, _tier in source_specs:
        aa = basis @ fa
        pp = basis @ fp
        rec_a_num += float(_e008_np.sum((aa - A_all[ss]) ** 2))
        rec_a_den += float(_e008_np.sum(A_all[ss] ** 2))
        rec_p_num += float(_e008_np.sum((pp - P_all[ss]) ** 2))
        rec_p_den += float(_e008_np.sum(P_all[ss] ** 2))

    result = {
        "layer": 14,
        "n_old": int(ka),
        "n_tier2": int(kb),
        "factor_reconstruction_rel_rms_A": _e008_rel(rec_a_num, rec_a_den),
        "factor_reconstruction_rel_rms_P": _e008_rel(rec_p_num, rec_p_den),
        "dimensions": {},
    }

    for m in (64, 128, 256, 512):
        sums = {
            "ap_num": 0.0, "ap_den": 0.0,
            "aa_num": 0.0, "aa_den": 0.0,
            "pp_num": 0.0, "pp_den": 0.0,
        }
        max_source = {"ap": 0.0, "aa": 0.0, "pp": 0.0}
        basis_cache = {}
        for ss, basis, fa, fp, tier in source_specs:
            r = int(basis.shape[1])
            key = (tier, r, m)
            if key not in basis_cache:
                maps = _e008_maps(r, m)
                basis_cache[key] = (maps, _e008_ts2(basis, basis, maps, m))
            maps, zq = basis_cache[key]
            z_ap = _e008_ts2(fa.T, fp.T, maps, m)
            z_aa = _e008_ts2(fa.T, fa.T, maps, m)
            z_pp = _e008_ts2(fp.T, fp.T, maps, m)

            ap_hat = zq @ z_ap.T
            aa_hat = zq @ z_aa.T
            pp_hat = zq @ z_pp.T
            a = A_all[ss]
            p = P_all[ss]
            exacts = {
                "ap": a * p,
                "aa": a * a,
                "pp": p * p,
            }
            hats = {"ap": ap_hat, "aa": aa_hat, "pp": pp_hat}
            for name in ("ap", "aa", "pp"):
                err = hats[name] - exacts[name]
                num = float(_e008_np.sum(err * err))
                den = float(_e008_np.sum(exacts[name] * exacts[name]))
                sums[name + "_num"] += num
                sums[name + "_den"] += den
                max_source[name] = max(max_source[name], _e008_rel(num, den))

        result["dimensions"][str(m)] = {
            "AP_rel_rms": _e008_rel(sums["ap_num"], sums["ap_den"]),
            "AA_rel_rms": _e008_rel(sums["aa_num"], sums["aa_den"]),
            "PP_rel_rms": _e008_rel(sums["pp_num"], sums["pp_den"]),
            "AP_max_source_rel_rms": max_source["ap"],
            "AA_max_source_rel_rms": max_source["aa"],
            "PP_max_source_rel_rms": max_source["pp"],
        }

    print("E008_PRODUCT_PROBE_JSON=" + _e008_json.dumps(result, sort_keys=True))
'''


def patch(source: str) -> str:
    import_marker = "import math\n"
    if import_marker not in source:
        raise RuntimeError("V25 import marker not found")
    source = source.replace(import_marker, import_marker + "import numpy as _e008_np\n", 1)

    class_marker = "# ---- embedded coefficient tables (generated by dump_k3_tables2.py) ----\n"
    if class_marker not in source:
        raise RuntimeError("V25 helper insertion marker not found")
    source = source.replace(class_marker, HELPER + "\n\n" + class_marker, 1)

    call_marker = "            # ---- WK slices ----\n"
    call = (
        "            if li == 14 and ka > 0:\n"
        "                _e008_probe_products(A_st, P_st, ka, kb, Qc, U, FAo, FPo, FA2, FP2)\n\n"
    )
    if call_marker not in source:
        raise RuntimeError("V25 probe call marker not found")
    source = source.replace(call_marker, call + call_marker, 1)
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    original = args.source.read_text(encoding="utf-8")
    args.output.write_text(patch(original), encoding="utf-8")


if __name__ == "__main__":
    main()
