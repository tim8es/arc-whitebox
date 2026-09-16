from __future__ import annotations

import hashlib
import importlib.util
import types
import urllib.request

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
RAW_URL = f"https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/{UPSTREAM_COMMIT}/estimators/estimator_v29.py"
WIDTH = 1024
DEPTH = 16
AGE_OLD2 = 6
R_OLD2 = 256


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def fetch_exact_source() -> bytes:
    with urllib.request.urlopen(RAW_URL, timeout=30) as response:
        data = response.read()
    observed = git_blob_sha1(data)
    if observed != EXPECTED_BLOB:
        raise RuntimeError(f"unexpected upstream blob {observed}")
    return data


def _load_module(data: bytes, name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_loader(name, loader=None)
    if spec is None:
        raise RuntimeError("failed to create module spec")
    mod = importlib.util.module_from_spec(spec)
    code = compile(data, f"<{name}:{EXPECTED_BLOB}>", "exec")
    exec(code, mod.__dict__)
    return mod


def load_v29() -> tuple[types.ModuleType, bytes]:
    data = fetch_exact_source()
    return _load_module(data, "e053_exact_v29"), data


def load_e053() -> tuple[types.ModuleType, bytes]:
    base, data = load_v29()

    class Estimator(base.Estimator):
        pass

    Estimator.AGE_OLD2 = AGE_OLD2
    Estimator.R_OLD2 = R_OLD2
    mod = types.ModuleType("e053_age6_r256")
    mod.Estimator = Estimator
    return mod, data


def frozen_delta() -> dict[str, int]:
    return {"AGE_OLD2": AGE_OLD2, "R_OLD2": R_OLD2}
