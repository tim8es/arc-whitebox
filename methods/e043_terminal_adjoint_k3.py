from __future__ import annotations

import hashlib
import urllib.request

import numpy as np

PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v25.py"
PINNED_BLOB_SHA = "195373a110215256b759d7c172ba8c923c62e5cc"


def suffix_product(transports, n: int):
    out = np.eye(n)
    for transport in transports:
        out = np.asarray(transport) @ out
    return out


def replay_source_dense(a, p, z, zf, transports):
    a_out = np.asarray(a).copy()
    p_out = np.asarray(p).copy()
    z_out = np.asarray(z).copy()
    zf_out = None if zf is None else np.asarray(zf).copy()
    for transport in transports:
        t = np.asarray(transport)
        a_out = t @ a_out
        p_out = t @ p_out
        z_out = t @ z_out
        if zf_out is not None:
            zf_out = t @ zf_out
    return a_out, p_out, z_out, zf_out


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def pinned_raw_url() -> str:
    return f"https://raw.githubusercontent.com/{PINNED_REPO}/{PINNED_COMMIT}/{PINNED_PATH}"


def _replace_exact(source: str, old: str, new: str, key: str, counts: dict[str, int]) -> str:
    count = source.count(old)
    counts[key] = count
    if count != 1:
        raise ValueError(f"E043 patch target {key!r} count={count}, expected 1")
    return source.replace(old, new, 1)


def patch_source(source: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    source = _replace_exact(
        source,
        "import math\n\nimport flopscope as flops\n",
        "import math\n\nE043_TERMINAL_ADJOINT_K3 = True\n\nimport flopscope as flops\n",
        "marker",
        counts,
    )

    source = _replace_exact(
        source,
        'NO_CONFINE = _os.environ.get("V21_NO_CONFINE", "0") == "1"  # V21: 1 -> V20 op stream\n',
        "NO_CONFINE = True  # E043: no persistent inherited carrier exists to confine\n",
        "no_confine",
        counts,
    )

    source = _replace_exact(
        source,
        "        rows = []\n\n        w1_prev = None  # wick w(1) of the previous layer, folded into WD\n",
        "        rows = []\n"
        "        # E043: local births and fixed forward transport history; no inherited carrier.\n"
        "        e043_births = []\n"
        "        e043_W_hist = []\n"
        "        e043_w1_hist = []\n"
        "        self._e043_stored_births = 0\n"
        "        self._e043_replayed_births = 0\n"
        "        self._e043_nonterminal_replays = 0\n\n"
        "        w1_prev = None  # wick w(1) of the previous layer, folded into WD\n",
        "state",
        counts,
    )

    source = _replace_exact(
        source,
        "            skip_src = trim and NO_SRC_LAST\n",
        "            skip_src = not last  # E043: inherited K3 is terminal-only\n",
        "skip_src",
        counts,
    )

    source = _replace_exact(
        source,
        "            W = w32.T\n            # ---- linear ----\n",
        "            W = w32.T\n            e043_W_hist.append(W)\n            # ---- linear ----\n",
        "w_history",
        counts,
    )

    replay_block = '''            # E043 terminal adjoint replay: construct exact suffix products once,
            # then replay every stored birth exactly once into the final preactivation.
            if last and e043_births:
                _nb = len(e043_births)
                _suffix = [None] * _nb
                _suffix[_nb - 1] = e043_W_hist[li]
                for _b in range(_nb - 2, -1, -1):
                    _bridge = fnp.reshape(e043_w1_hist[_b + 1], (-1, 1)) * e043_W_hist[_b + 1]
                    _suffix[_b] = _suffix[_b + 1] @ _bridge
                _As, _Ps, _Zs, _Ls, _Zfs = [], [], [], [], []
                for _idx, (_birth_layer, _a, _rr, _lr, _ff) in enumerate(e043_births):
                    _T = _suffix[_idx]
                    _As.append(_T @ _a)
                    _Ps.append(_T)
                    _Zs.append(_T @ _rr)
                    _Ls.append(_lr)
                    if _ff is not None:
                        _Zfs.append(_T @ _ff)
                    self._e043_replayed_births += 1
                A_st = fnp.stack(_As, axis=0)
                P_st = fnp.stack(_Ps, axis=0)
                Z_st = fnp.stack(_Zs, axis=0)
                L_st = fnp.stack(_Ls, axis=0)
                Zf_st = fnp.stack(_Zfs, axis=0) if _Zfs else None
                self._e043_stored_births = _nb

'''
    source = _replace_exact(
        source,
        "            # ---- WK slices ----\n",
        replay_block + "            # ---- WK slices ----\n",
        "terminal_replay",
        counts,
    )

    source = _replace_exact(
        source,
        "            mode = 0 if A_st is None else 1\n",
        "            mode = 0 if not e043_births else 1\n",
        "mode",
        counts,
    )

    old_skip = '''            if mode == 1 and skip_src:
                D3, D21 = fnp.zeros(n, dtype=f32), None
                if regen:
                    WW = W * W
                    dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev
                    g4row = dG * METRIC_C
                    wk4m = wk431 = None
                elif riders:
                    g4row = ((W * W) @ K4_vec) * 0.5 * float(st["wk4_c4"] * metric2)
                    wk4m = None
                else:
                    g4row = ones_n * (K4_sigma * float(st["wk4_c4"] * metric2))
                    wk4m = None
'''
    new_skip = '''            if mode == 1 and skip_src:
                # E043: preserve the pinned local Gaussian/K4 closure, but inherited
                # K3 D3/D21 are zero until the terminal replay.
                D3 = fnp.zeros(n, dtype=f32)
                D21 = fnp.zeros((n, n), dtype=f32)
                if regen:
                    WW = W * W
                    if BETA != 0.0:
                        t_g = WW @ g_prev
                        t_v = var - WW @ var_prev
                        dG0 = t_g + t_v * lam_prev
                        rr = fnp.mean(dG0) / fnp.mean(var)
                        ref = float(REF_R[min(li - 1, len(REF_R) - 1)])
                        lam_prev = lam_prev * fnp.power(fnp.clip(rr / ref, 0.5, 2.0), BETA)
                        dG = t_g + t_v * lam_prev
                    else:
                        dG = WW @ (g_prev - var_prev * lam_prev) + var * lam_prev
                    g4row = dG * METRIC_C
                    g22c = fnp.reshape(dG * (METRIC_C / 6.0), (-1, 1))
                    wk4m = _zero_diag(g22c + g22c.T)
                    wk431 = None if trim else C_off * (0.5 * METRIC_C * lam_prev)
                elif riders:
                    gv = ((W * W) @ K4_vec) * 0.5
                    g4row = gv * float(st["wk4_c4"] * metric2)
                    g22 = gv * float(0.5 * st["wk4_c22"] * metric2)
                    g22c = fnp.reshape(g22, (-1, 1))
                    wk4m = _zero_diag(g22c + g22c.T)
                else:
                    g4v = K4_sigma * float(st["wk4_c4"] * metric2)
                    g22v = K4_sigma * float(st["wk4_c22"] * metric2)
                    g4row = ones_n * g4v
                    wk4m = _zero_diag(ones2 * g22v)
'''
    source = _replace_exact(source, old_skip, new_skip, "local_closure", counts)

    source = _replace_exact(
        source,
        "            w1_prev = w1  # stacks pick up this wick via WD at the next linear\n",
        "            w1_prev = w1  # stacks pick up this wick via WD at the next linear\n"
        "            e043_w1_hist.append(w1)\n",
        "wick_history",
        counts,
    )

    source = _replace_exact(
        source,
        "            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n",
        "            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n"
        "            e043_births.append((li, a_b, Rr_full, Lr_full, Ff_b))\n"
        "            s_list.append(S3c)\n"
        "            e_list.append(e_b)\n"
        "            self._e043_stored_births = len(e043_births)\n"
        "            newborn = None\n",
        "birth_store",
        counts,
    )

    return source, counts


def fetch_and_patch_pinned_source() -> tuple[str, dict]:
    with urllib.request.urlopen(pinned_raw_url(), timeout=30) as response:
        raw = response.read()
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA:
        raise RuntimeError(f"E043 pinned V25 blob mismatch: {blob}")
    patched, counts = patch_source(raw.decode("utf-8"))
    return patched, {"blob_sha": blob, "patch_counts": counts, "url": pinned_raw_url()}
