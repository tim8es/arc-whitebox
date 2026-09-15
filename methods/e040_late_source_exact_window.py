from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import types
import urllib.request

PINNED_REPO = "504aldo/whest-p2-cumulant-k3"
PINNED_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PINNED_PATH = "estimators/estimator_v25.py"
PINNED_BLOB_SHA = "195373a110215256b759d7c172ba8c923c62e5cc"
INSERTION_CUTOFF = 8
BASELINE_UTILIZATION = 0.36666448
PROJECTED_UTILIZATION = BASELINE_UTILIZATION * (0.05 + 0.95 * (36.0 / 120.0))

_TARGET = "            if newborn is not None and not skip_src:\n"
_REPLACEMENT = "            if newborn is not None and not skip_src and li >= 8:\n"


def git_blob_sha(source: bytes) -> str:
    header = f"blob {len(source)}\0".encode("ascii")
    return hashlib.sha1(header + source).hexdigest()


def patch_source(source: str) -> tuple[str, int]:
    count = source.count(_TARGET)
    if count != 1:
        raise ValueError(f"E040 V25 newborn patch target count={count}, expected 1")
    patched = source.replace(_TARGET, _REPLACEMENT, 1)
    return patched, count


def birth_schedule(depth: int = 16) -> tuple[tuple[int, ...], tuple[int, ...]]:
    insertions = tuple(li for li in range(1, depth) if li >= INSERTION_CUTOFF)
    births = tuple(li - 1 for li in insertions)
    return births, insertions


def source_layer_pairs(depth: int = 16) -> int:
    births, _ = birth_schedule(depth)
    return sum((depth - 1) - b for b in births)


def pinned_raw_url() -> str:
    return (
        f"https://raw.githubusercontent.com/{PINNED_REPO}/"
        f"{PINNED_COMMIT}/{PINNED_PATH}"
    )


def fetch_and_patch_pinned_source() -> tuple[str, dict]:
    with urllib.request.urlopen(pinned_raw_url(), timeout=30) as response:
        raw = response.read()
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA:
        raise RuntimeError(f"E040 pinned V25 blob mismatch: {blob}")
    source = raw.decode("utf-8")
    patched, count = patch_source(source)
    return patched, {
        "blob_sha": blob,
        "patch_target_count": count,
        "url": pinned_raw_url(),
    }


def load_patched_module(module_name: str = "_e040_pinned_v25") -> tuple[types.ModuleType, dict]:
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
    return module, provenance
