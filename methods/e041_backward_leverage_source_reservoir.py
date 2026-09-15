from __future__ import annotations

import hashlib
import os
import sys
import types
import urllib.request

PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v25.py"
PINNED_BLOB_SHA = "195373a110215256b759d7c172ba8c923c62e5cc"
CAPACITY = 41
BASELINE_UTILIZATION = 0.36666448
PROJECTED_UTILIZATION = BASELINE_UTILIZATION * (0.05 + 0.95 * CAPACITY / 120.0)

_NO_CONFINE_LINE = (
    'NO_CONFINE = _os.environ.get("V21_NO_CONFINE", "0") == "1"  # V21: 1 -> V20 op stream\n'
)
_KEEP_LINE = (
    'E041_KEEP_BIRTHS = tuple(int(x) for x in _os.environ.get("E041_KEEP_BIRTHS", "").split(",") if x)\n'
)
_NEWBORN_BLOCK = (
    '            newborn = (a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n'
    '            if rfb > 0:\n'
)
_NEWBORN_REPLACEMENT = (
    '            newborn = ((a_b, Rr_full, Lr_full, S3c, e_b, Ff_b)\n'
    '                       if li in E041_KEEP_BIRTHS else None)\n'
    '            if rfb > 0 and li in E041_KEEP_BIRTHS:\n'
)
_APPEND_LINES = (
    'w2b_list.append(w2)',
    'dA_list.append(9.0 + w2 * w2 + 9.0 * e_b * e_b)',
    'dP_list.append(1.0 + S3c * S3c)',
    'c1_list.append(c1_b)',
    'c2_list.append(dgw)',
    'y_list.append(y_b)',
)


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def pinned_raw_url() -> str:
    return (
        f"https://raw.githubusercontent.com/{PINNED_REPO}/"
        f"{PINNED_COMMIT}/{PINNED_PATH}"
    )


def walsh_probes(xp, n: int):
    if n < 4 or n & (n - 1):
        raise ValueError("E041 Walsh probes require a power-of-two width >=4")
    cols = []
    for i in range(n):
        b0 = -1.0 if (i & 1) else 1.0
        b1 = -1.0 if (i & 2) else 1.0
        cols.append((1.0, b0, b1, b0 * b1))
    return xp.asarray(cols, dtype=xp.float64)


def backward_leverage_scores(xp, weights, probes):
    if len(weights) < 2:
        raise ValueError("E041 requires at least two layers")
    g = probes
    scores = [None] * (len(weights) - 1)
    for birth in range(len(weights) - 2, -1, -1):
        g = (weights[birth + 1] @ g) * 0.5
        scores[birth] = xp.mean(xp.sum(g * g, axis=0))
    return xp.stack(scores, axis=0)


def source_pair_cost(births) -> int:
    return sum(15 - int(b) for b in births)


def select_births_knapsack(scores, capacity: int = CAPACITY) -> tuple[int, ...]:
    if len(scores) != 15:
        raise ValueError(f"E041 expected 15 birth scores, got {len(scores)}")
    # state[cost] = (value, lexicographically smallest birth tuple for that value)
    states: dict[int, tuple[float, tuple[int, ...]]] = {0: (0.0, ())}
    for birth, raw_value in enumerate(scores):
        value = float(raw_value)
        cost = 15 - birth
        nxt = dict(states)
        for used, (old_value, old_tuple) in states.items():
            new_cost = used + cost
            if new_cost > capacity:
                continue
            cand = (old_value + value, old_tuple + (birth,))
            prior = nxt.get(new_cost)
            if prior is None or cand[0] > prior[0] or (
                cand[0] == prior[0] and cand[1] < prior[1]
            ):
                nxt[new_cost] = cand
        states = nxt
    best_value = -1.0
    best_tuple: tuple[int, ...] | None = None
    for _, (value, births) in states.items():
        if value > best_value or (
            value == best_value and (best_tuple is None or births < best_tuple)
        ):
            best_value = value
            best_tuple = births
    if best_tuple is None:
        raise RuntimeError("E041 knapsack produced no state")
    return best_tuple


def patch_source(source: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    counts["no_confine_anchor"] = source.count(_NO_CONFINE_LINE)
    if counts["no_confine_anchor"] != 1:
        raise ValueError(
            f"E041 no-confine anchor count={counts['no_confine_anchor']}, expected 1"
        )
    source = source.replace(_NO_CONFINE_LINE, _NO_CONFINE_LINE + _KEEP_LINE, 1)

    counts["newborn_block"] = source.count(_NEWBORN_BLOCK)
    if counts["newborn_block"] != 1:
        raise ValueError(
            f"E041 newborn block count={counts['newborn_block']}, expected 1"
        )
    source = source.replace(_NEWBORN_BLOCK, _NEWBORN_REPLACEMENT, 1)

    for append in _APPEND_LINES:
        key = append.split(".append", 1)[0]
        old = f"            {append}\n"
        new = f"            if li in E041_KEEP_BIRTHS: {append}\n"
        counts[key] = source.count(old)
        if counts[key] != 1:
            raise ValueError(f"E041 {key} append count={counts[key]}, expected 1")
        source = source.replace(old, new, 1)

    return source, counts


def fetch_and_patch_pinned_source() -> tuple[str, dict]:
    with urllib.request.urlopen(pinned_raw_url(), timeout=30) as response:
        raw = response.read()
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA:
        raise RuntimeError(f"E041 pinned V25 blob mismatch: {blob}")
    patched, counts = patch_source(raw.decode("utf-8"))
    return patched, {"blob_sha": blob, "patch_counts": counts, "url": pinned_raw_url()}


def load_patched_module(
    keep_births: tuple[int, ...], module_name: str = "_e041_pinned_v25"
) -> tuple[types.ModuleType, dict]:
    patched, provenance = fetch_and_patch_pinned_source()
    old_no_confine = os.environ.get("V21_NO_CONFINE")
    old_keep = os.environ.get("E041_KEEP_BIRTHS")
    os.environ["V21_NO_CONFINE"] = "1"
    os.environ["E041_KEEP_BIRTHS"] = ",".join(str(x) for x in keep_births)
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
        if old_keep is None:
            os.environ.pop("E041_KEEP_BIRTHS", None)
        else:
            os.environ["E041_KEEP_BIRTHS"] = old_keep
    provenance["no_confine_frozen"] = bool(getattr(module, "NO_CONFINE", False))
    provenance["keep_births_frozen"] = tuple(getattr(module, "E041_KEEP_BIRTHS", ()))
    return module, provenance
