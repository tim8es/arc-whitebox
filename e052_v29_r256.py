from __future__ import annotations

import hashlib
import sys
import types
import urllib.request

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
UPSTREAM_RAW_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    + UPSTREAM_COMMIT
    + "/estimators/estimator_v29.py"
)
ORIGINAL = '    R_OLD2 = int(_os.environ.get("V24_R_OLD2", "224"))'
PATCHED = '    R_OLD2 = int(_os.environ.get("V24_R_OLD2", "256"))'


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def fetch_exact_source() -> bytes:
    with urllib.request.urlopen(UPSTREAM_RAW_URL, timeout=60) as response:
        data = response.read()
    observed = git_blob_sha1(data)
    if observed != EXPECTED_BLOB:
        raise RuntimeError(f"V29 blob mismatch: {observed} != {EXPECTED_BLOB}")
    return data


def _load(source: str, module_name: str) -> types.ModuleType:
    mod = types.ModuleType(module_name)
    mod.__file__ = f"<{module_name}>"
    sys.modules[module_name] = mod
    exec(compile(source, mod.__file__, "exec"), mod.__dict__)
    return mod


def load_v29(module_name: str = "e052_v29_baseline") -> tuple[types.ModuleType, bytes]:
    data = fetch_exact_source()
    return _load(data.decode("utf-8"), module_name), data


def load_e052(module_name: str = "e052_v29_r256") -> tuple[types.ModuleType, bytes]:
    data = fetch_exact_source()
    source = data.decode("utf-8")
    if source.count(ORIGINAL) != 1:
        raise RuntimeError("frozen R_OLD2 source line not unique")
    patched = source.replace(ORIGINAL, PATCHED, 1)
    if patched.count(PATCHED) != 1 or patched.count(ORIGINAL) != 0:
        raise RuntimeError("mechanical R_OLD2 patch failed")
    return _load(patched, module_name), data
