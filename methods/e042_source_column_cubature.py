from __future__ import annotations

import hashlib
import urllib.request

import numpy as np

PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v25.py"
PINNED_BLOB_SHA = "195373a110215256b759d7c172ba8c923c62e5cc"
Q_SUITE = 320
BIRTH_OFFSET = 73


def _bit_reverse(value: int, bits: int) -> int:
    out = 0
    for _ in range(bits):
        out = (out << 1) | (value & 1)
        value >>= 1
    return out


def source_nodes(n: int, birth: int) -> np.ndarray:
    if n <= 0:
        raise ValueError("n must be positive")
    q = min(Q_SUITE, n)
    if n == 1024:
        nodes = [(_bit_reverse(k, 10) + BIRTH_OFFSET * int(birth)) % 1024 for k in range(q)]
    elif q == n:
        shift = (BIRTH_OFFSET * int(birth)) % n
        nodes = [((k + shift) % n) for k in range(n)]
    else:
        # Shape-generic non-suite fallback. Suite science uses only the branch above.
        nodes = [(k * n) // q for k in range(q)]
    arr = np.asarray(nodes, dtype=np.int64)
    if len(np.unique(arr)) != q:
        raise RuntimeError("E042 node generator produced duplicate nodes")
    return arr


def quadrature_weight(n: int) -> float:
    return float(n) / float(len(source_nodes(n, 0)))


def cubature_gram(a, p, v, cols, omega: float):
    a = np.asarray(a)
    p = np.asarray(p)
    v = np.asarray(v)
    cols = np.asarray(cols, dtype=np.int64)
    return float(omega) * ((a[:, cols] * p[:, cols] * v[cols][None, :]) @ a[:, cols].T)


def transport_selected_columns(weights, a, cols):
    x = np.asarray(a)[:, np.asarray(cols, dtype=np.int64)]
    for w in weights:
        x = np.asarray(w) @ x
    return x


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def pinned_raw_url() -> str:
    return f"https://raw.githubusercontent.com/{PINNED_REPO}/{PINNED_COMMIT}/{PINNED_PATH}"


def _replace_exact(source: str, old: str, new: str, key: str, counts: dict[str, int]) -> str:
    count = source.count(old)
    counts[key] = count
    if count != 1:
        raise ValueError(f"E042 patch target {key!r} count={count}, expected 1")
    return source.replace(old, new, 1)


def patch_source(source: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    import_anchor = "import math\n\nimport flopscope as flops\n"
    injected = '''import math\n\nE042_SOURCE_COLUMN_CUBATURE = True\nE042_Q_SUITE = 320\nE042_BIRTH_OFFSET = 73\n\ndef _e042_bitrev(value, bits):\n    out = 0\n    for _ in range(bits):\n        out = (out << 1) | (value & 1)\n        value >>= 1\n    return out\n\ndef _e042_nodes(n, birth):\n    q = min(E042_Q_SUITE, n)\n    if n == 1024:\n        return [(_e042_bitrev(k, 10) + E042_BIRTH_OFFSET * int(birth)) % 1024 for k in range(q)]\n    if q == n:\n        shift = (E042_BIRTH_OFFSET * int(birth)) % n\n        return [((k + shift) % n) for k in range(n)]\n    return [(k * n) // q for k in range(q)]\n\nimport flopscope as flops\n'''
    source = _replace_exact(source, import_anchor, injected, "constants", counts)

    no_confine = 'NO_CONFINE = _os.environ.get("V21_NO_CONFINE", "0") == "1"  # V21: 1 -> V20 op stream\n'
    source = _replace_exact(
        source,
        no_confine,
        "NO_CONFINE = True  # E042: native row-space confinement is disabled\n",
        "no_confine",
        counts,
    )

    source = _replace_exact(
        source,
        "        n = mlp.width\n        f32 = fnp.float32\n",
        "        n = mlp.width\n        qcol = min(E042_Q_SUITE, n)\n        f32 = fnp.float32\n",
        "predict_qcol",
        counts,
    )

    # There are exactly two source-carrier pools: dslice scratch and A/P ping-pong legs.
    pool_old = 'fnp.empty((L - 1, n, n), dtype=f32)'
    pool_count = source.count(pool_old)
    counts["carrier_pools"] = pool_count
    if pool_count != 2:
        raise ValueError(f"E042 carrier pool count={pool_count}, expected 2")
    source = source.replace(pool_old, 'fnp.empty((L - 1, n, qcol), dtype=f32)')

    source = _replace_exact(
        source,
        "                a_b, Rr, Lr, s_b, e_b, Ff = newborn\n",
        "                a_b, Rr, Lr, s_b, e_b, Ff, cols_b = newborn\n",
        "newborn_unpack",
        counts,
    )
    source = _replace_exact(
        source,
        '                fnp.copyto(legs["P0"][k], W)\n',
        '                fnp.copyto(legs["P0"][k], W[:, cols_b])\n',
        "newborn_p_columns",
        counts,
    )
    source = _replace_exact(
        source,
        "                l_n = fnp.reshape(Lr, (1, n, Lr.shape[1]))\n",
        "                l_n = fnp.reshape(Lr, (1, qcol, Lr.shape[1]))\n",
        "newborn_l_shape",
        counts,
    )

    source = _replace_exact(
        source,
        "            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n",
        "            cols_b = _e042_nodes(n, li)\n"
        "            newborn = (a_b[:, cols_b], Rr_full, Lr_full[cols_b],\n"
        "                       S3c[cols_b], e_b[cols_b], Ff_b, cols_b)\n",
        "newborn_slice",
        counts,
    )
    source = _replace_exact(
        source,
        "                r1n = fnp.reshape(R1T_b, (1, n, rfb))\n                r2n = fnp.reshape(R2T_b, (1, n, rfb))\n",
        "                r1n = fnp.reshape(R1T_b[cols_b], (1, qcol, rfb))\n"
        "                r2n = fnp.reshape(R2T_b[cols_b], (1, qcol, rfb))\n",
        "feedback_right_columns",
        counts,
    )

    source = _replace_exact(source, "            w2b_list.append(w2)\n", "            w2b_list.append(w2[cols_b])\n", "w2_columns", counts)
    source = _replace_exact(
        source,
        "            dA_list.append(9.0 + w2 * w2 + 9.0 * e_b * e_b)\n",
        "            dA_list.append((9.0 + w2 * w2 + 9.0 * e_b * e_b)[cols_b])\n",
        "dA_columns",
        counts,
    )
    source = _replace_exact(source, "            dP_list.append(1.0 + S3c * S3c)\n", "            dP_list.append((1.0 + S3c * S3c)[cols_b])\n", "dP_columns", counts)
    source = _replace_exact(source, "            c1_list.append(c1_b)\n", "            c1_list.append(c1_b[cols_b])\n", "c1_columns", counts)
    source = _replace_exact(source, "            c2_list.append(dgw)\n", "            c2_list.append(dgw[cols_b])\n", "c2_columns", counts)
    source = _replace_exact(source, "            y_list.append(y_b)\n", "            y_list.append(y_b[cols_b])\n", "y_columns", counts)

    source = _replace_exact(
        source,
        "        k = len(w2b_list)\n        W2B = fnp.reshape(fnp.stack(w2b_list, axis=0), (k, 1, n))\n        Sb = fnp.reshape(fnp.stack(s_list, axis=0), (k, 1, n))\n        Eb = fnp.reshape(fnp.stack(e_list, axis=0), (k, 1, n))\n",
        "        k = len(w2b_list)\n        qcol = A_st.shape[2]\n        e042_omega = float(n) / float(qcol)\n"
        "        W2B = fnp.reshape(fnp.stack(w2b_list, axis=0), (k, 1, qcol))\n"
        "        Sb = fnp.reshape(fnp.stack(s_list, axis=0), (k, 1, qcol))\n"
        "        Eb = fnp.reshape(fnp.stack(e_list, axis=0), (k, 1, qcol))\n",
        "dslice_column_shape",
        counts,
    )
    source = _replace_exact(
        source,
        "        fnp.multiply(P_st, fnp.reshape(C2, (k, 1, n)), out=MP)\n"
        "        fnp.multiply(A_st, fnp.reshape(C1, (k, 1, n)), out=T)\n",
        "        fnp.multiply(P_st, fnp.reshape(C2, (k, 1, qcol)), out=MP)\n"
        "        fnp.multiply(A_st, fnp.reshape(C1, (k, 1, qcol)), out=T)\n",
        "feed_column_shape",
        counts,
    )
    source = _replace_exact(
        source,
        "        if not need_d21:\n            return D3, None\n",
        "        if not need_d21:\n            return D3 * e042_omega, None\n",
        "d3_weight",
        counts,
    )
    source = _replace_exact(
        source,
        "        return D3, _zero_diag(D21)\n",
        "        return D3 * e042_omega, _zero_diag(D21 * e042_omega)\n",
        "d21_weight",
        counts,
    )

    return source, counts


def fetch_and_patch_pinned_source() -> tuple[str, dict]:
    with urllib.request.urlopen(pinned_raw_url(), timeout=30) as response:
        raw = response.read()
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA:
        raise RuntimeError(f"E042 pinned V25 blob mismatch: {blob}")
    patched, counts = patch_source(raw.decode("utf-8"))
    return patched, {"blob_sha": blob, "patch_counts": counts, "url": pinned_raw_url()}
