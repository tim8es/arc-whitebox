from __future__ import annotations

import hashlib
import os
import sys
import types
import urllib.request

CHECKPOINTS = (7, 11, 15)
PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v25.py"
PINNED_BLOB_SHA = "195373a110215256b759d7c172ba8c923c62e5cc"
PROJECTED_UTILIZATION = 0.1228326008

_IMPORT_ANCHOR = "from whestbench.domain import MLP\n"
_NO_CONFINE_LINE = (
    'NO_CONFINE = _os.environ.get("V21_NO_CONFINE", "0") == "1"  # V21: 1 -> V20 op stream\n'
)
_STATE_ANCHOR = "        w1_prev = None  # wick w(1) of the previous layer, folded into WD\n"
_SKIP_SRC_LINE = "            skip_src = trim and NO_SRC_LAST\n"
_SOURCE_START = "            # Source stacks evolve by W @ diag(w1_prev); the newborn (added after\n"
_SOURCE_END = "            # ---- WK slices ----\n"
_MODE_LINE = "            mode = 0 if A_st is None else 1\n"
_SKIP_DSLICE_LINE = "                D3, D21 = fnp.zeros(n, dtype=f32), None\n"
_BIRTH_FB_LINE = "            if rfb > 0 and mode == 1:\n"
_W1_PREV_LINE = "            w1_prev = w1  # stacks pick up this wick via WD at the next linear\n"
_NEWBORN_LINE = "            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n"


def checkpoint_live_counts(depth: int) -> tuple[int, ...]:
    if depth <= max(CHECKPOINTS):
        raise ValueError("E044 requires all frozen checkpoints to exist")
    return tuple(int(c) for c in CHECKPOINTS)


def checkpoint_source_uses(depth: int) -> int:
    return sum(checkpoint_live_counts(depth))


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def pinned_raw_url() -> str:
    return (
        f"https://raw.githubusercontent.com/{PINNED_REPO}/"
        f"{PINNED_COMMIT}/{PINNED_PATH}"
    )


def _weight_t(weights, layer: int):
    return weights[layer].T


def compose_segment_operator(xp, weights, w1_hist, start_checkpoint: int, checkpoint: int):
    if checkpoint <= start_checkpoint:
        raise ValueError("checkpoint must be after previous checkpoint")
    out = None
    for layer in range(start_checkpoint + 1, checkpoint + 1):
        w = _weight_t(weights, layer)
        wd = w * xp.reshape(w1_hist[layer - 1], (1, -1))
        out = wd if out is None else wd @ out
    return out


def compose_newborn_operator(xp, weights, w1_hist, birth: int, checkpoint: int):
    if not (0 <= birth < checkpoint):
        raise ValueError("birth must precede checkpoint")
    out = _weight_t(weights, checkpoint)
    for layer in range(checkpoint - 1, birth, -1):
        out = (out * xp.reshape(w1_hist[layer], (1, -1))) @ _weight_t(weights, layer)
    return out


def reconstruct_checkpoint(
    xp,
    weights,
    w1_hist,
    birth_records,
    *,
    checkpoint: int,
    previous_checkpoint: int,
    previous_state,
):
    """Reconstruct all K3 source legs at one frozen checkpoint.

    Birth records are V25 tuples `(a_b, Rr, Lr, s_b, e_b, Ff)`.  Existing
    checkpoint-state sources share one exact composed WD segment operator.  Births
    since the previous checkpoint are replayed with raw-W first and WD thereafter.
    """
    k = len(birth_records)
    if k != checkpoint:
        raise ValueError(f"E044 checkpoint {checkpoint} expected {checkpoint} births, got {k}")
    if k == 0:
        raise ValueError("E044 checkpoint replay requires at least one birth")

    n = int(birth_records[0][0].shape[0])
    dtype = birth_records[0][0].dtype
    rz = int(birth_records[0][1].shape[1])
    A = xp.empty((k, n, n), dtype=dtype)
    P = xp.empty((k, n, n), dtype=dtype)
    Z = xp.empty((k, n, rz), dtype=dtype)
    L = xp.empty((k, n, rz), dtype=dtype)
    has_zf = birth_records[0][5] is not None
    rzf = int(birth_records[0][5].shape[1]) if has_zf else 0
    Zf = xp.empty((k, n, rzf), dtype=dtype) if has_zf else None

    old_k = 0 if previous_state is None else int(previous_state["A"].shape[0])
    if previous_state is None:
        if previous_checkpoint != -1:
            raise ValueError("missing previous state")
    else:
        expected_old = previous_checkpoint
        if old_k != expected_old:
            raise ValueError(
                f"E044 previous checkpoint {previous_checkpoint} expected {expected_old} sources, got {old_k}"
            )
        if tuple(previous_state["births"]) != tuple(range(old_k)):
            raise ValueError("E044 previous state lost source identity")

    if old_k:
        seg = compose_segment_operator(xp, weights, w1_hist, previous_checkpoint, checkpoint)
        segb = xp.reshape(seg, (1, n, n))
        xp.copyto(A[:old_k], xp.matmul(segb, previous_state["A"]))
        xp.copyto(P[:old_k], xp.matmul(segb, previous_state["P"]))
        xp.copyto(Z[:old_k], xp.matmul(segb, previous_state["Z"]))
        xp.copyto(L[:old_k], previous_state["L"])
        if has_zf:
            if previous_state["Zf"] is None:
                raise ValueError("E044 previous state lost Zf")
            xp.copyto(Zf[:old_k], xp.matmul(segb, previous_state["Zf"]))

    # Build all newborn replay operators in one backward recursion.  The newest
    # pending birth uses raw W_checkpoint.  Each older birth prepends exactly one
    # additional D(w1) and raw W, so this costs one dense matrix product per step.
    op = _weight_t(weights, checkpoint)
    for birth in range(checkpoint - 1, old_k - 1, -1):
        if birth < checkpoint - 1:
            layer = birth + 1
            op = (op * xp.reshape(w1_hist[layer], (1, -1))) @ _weight_t(weights, layer)
        a_b, rr, lr, _s_b, _e_b, ff = birth_records[birth]
        xp.copyto(P[birth], op)
        xp.copyto(A[birth], op @ a_b)
        xp.copyto(Z[birth], op @ rr)
        xp.copyto(L[birth], lr)
        if has_zf:
            if ff is None:
                raise ValueError("E044 mixed Zf birth cardinality")
            xp.copyto(Zf[birth], op @ ff)

    state = {
        "A": A,
        "P": P,
        "Z": Z,
        "L": L,
        "Zf": Zf,
        "births": tuple(range(k)),
    }
    widths = [A.shape[0], P.shape[0], Z.shape[0], L.shape[0]]
    if Zf is not None:
        widths.append(Zf.shape[0])
    if len(set(widths)) != 1:
        raise RuntimeError(f"E044 replay cardinality mismatch: {widths}")
    return state


def patch_source(source: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    for key, anchor in (
        ("import_anchor", _IMPORT_ANCHOR),
        ("no_confine", _NO_CONFINE_LINE),
        ("state_anchor", _STATE_ANCHOR),
        ("skip_src", _SKIP_SRC_LINE),
        ("mode", _MODE_LINE),
        ("skip_dslice", _SKIP_DSLICE_LINE),
        ("birth_fb", _BIRTH_FB_LINE),
        ("w1_prev", _W1_PREV_LINE),
        ("newborn", _NEWBORN_LINE),
    ):
        counts[key] = source.count(anchor)
        if counts[key] != 1:
            raise ValueError(f"E044 {key} target count={counts[key]}, expected 1")

    counts["source_start"] = source.count(_SOURCE_START)
    counts["source_end"] = source.count(_SOURCE_END)
    if counts["source_start"] != 1 or counts["source_end"] != 1:
        raise ValueError("E044 source block markers are not unique")

    source = source.replace(
        _IMPORT_ANCHOR,
        _IMPORT_ANCHOR
        + "from methods.e044_fixed_checkpoint_k3_replay import reconstruct_checkpoint\n",
        1,
    )
    source = source.replace(
        _NO_CONFINE_LINE,
        _NO_CONFINE_LINE + "E044_CHECKPOINTS = (7, 11, 15)\n",
        1,
    )
    source = source.replace(
        _STATE_ANCHOR,
        _STATE_ANCHOR
        + "        e044_birth_records = []\n"
        + "        e044_w1_hist = []\n"
        + "        e044_checkpoint_layer = -1\n",
        1,
    )
    source = source.replace(_SKIP_SRC_LINE, "            skip_src = li not in E044_CHECKPOINTS\n", 1)

    start = source.index(_SOURCE_START)
    end = source.index(_SOURCE_END, start)
    replacement = (
        "            # E044: temporally sparse exact inherited-K3 replay.\n"
        "            if li in E044_CHECKPOINTS and e044_birth_records:\n"
        "                prev_state = None if A_st is None else {\n"
        "                    'A': A_st, 'P': P_st, 'Z': Z_st, 'L': L_st,\n"
        "                    'Zf': Zf_st, 'births': tuple(range(A_st.shape[0])),\n"
        "                }\n"
        "                replay = reconstruct_checkpoint(\n"
        "                    fnp, mlp.weights, e044_w1_hist, e044_birth_records,\n"
        "                    checkpoint=li, previous_checkpoint=e044_checkpoint_layer,\n"
        "                    previous_state=prev_state,\n"
        "                )\n"
        "                A_st, P_st = replay['A'], replay['P']\n"
        "                Z_st, L_st, Zf_st = replay['Z'], replay['L'], replay['Zf']\n"
        "                e044_checkpoint_layer = li\n"
        "                k = A_st.shape[0]\n"
        "            else:\n"
        "                k = 0 if A_st is None else A_st.shape[0]\n"
    )
    source = source[:start] + replacement + source[end:]

    source = source.replace(
        _MODE_LINE,
        "            mode = 0 if not e044_birth_records else 1\n",
        1,
    )
    source = source.replace(
        _SKIP_DSLICE_LINE,
        "                D3 = fnp.zeros(n, dtype=f32)\n"
        "                D21 = None if trim else fnp.zeros((n, n), dtype=f32)\n",
        1,
    )
    source = source.replace(
        _BIRTH_FB_LINE,
        "            if rfb > 0 and mode == 1 and not skip_src:\n",
        1,
    )
    source = source.replace(
        _W1_PREV_LINE,
        _W1_PREV_LINE + "            e044_w1_hist.append(w1)\n",
        1,
    )
    source = source.replace(
        _NEWBORN_LINE,
        _NEWBORN_LINE
        + "            e044_birth_records.append(newborn)\n"
        + "            s_list.append(S3c)\n"
        + "            e_list.append(e_b)\n"
        + "            newborn = None\n",
        1,
    )
    return source, counts


def fetch_and_patch_pinned_source() -> tuple[str, dict]:
    with urllib.request.urlopen(pinned_raw_url(), timeout=30) as response:
        raw = response.read()
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA:
        raise RuntimeError(f"E044 pinned V25 blob mismatch: {blob}")
    patched, counts = patch_source(raw.decode("utf-8"))
    return patched, {"blob_sha": blob, "patch_counts": counts, "url": pinned_raw_url()}


def load_patched_module(module_name: str = "_e044_pinned_v25") -> tuple[types.ModuleType, dict]:
    patched, provenance = fetch_and_patch_pinned_source()
    old_no_confine = os.environ.get("V21_NO_CONFINE")
    os.environ["V21_NO_CONFINE"] = "1"
    try:
        module = types.ModuleType(module_name)
        module.__file__ = f"<{module_name}>"
        sys.modules[module_name] = module
        exec(compile(patched, module.__file__, "exec"), module.__dict__)
    finally:
        if old_no_confine is None:
            os.environ.pop("V21_NO_CONFINE", None)
        else:
            os.environ["V21_NO_CONFINE"] = old_no_confine
    provenance["no_confine_frozen"] = bool(getattr(module, "NO_CONFINE", False))
    provenance["checkpoints_frozen"] = tuple(getattr(module, "E044_CHECKPOINTS", ()))
    return module, provenance
