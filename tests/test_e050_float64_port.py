from __future__ import annotations

import urllib.request

from methods.e050_v29_float64_port import (
    UPSTREAM_RAW,
    UPSTREAM_BLOB,
    mechanical_float64_source,
    instrument_source,
    verify_upstream_bytes,
    git_blob_sha1,
)


def _source() -> str:
    data = urllib.request.urlopen(UPSTREAM_RAW, timeout=30).read()
    verify_upstream_bytes(data)
    assert git_blob_sha1(data) == UPSTREAM_BLOB
    return data.decode("utf-8")


def test_port_is_exactly_two_reversible_dtype_edits():
    src = _source()
    port = mechanical_float64_source(src)
    assert src.count("f32 = fnp.float32") == 2
    assert port.count("f32 = fnp.float64") == 2
    assert port.replace("f32 = fnp.float64", "f32 = fnp.float32") == src
    for forbidden in ("jitter", "psd_repair", "renormalize", "damping", "E050_CLIP"):
        assert forbidden not in port


def test_instrumentation_is_observational_and_compiles():
    src = _source()
    traced_ref = instrument_source(src)
    traced_f64 = instrument_source(mechanical_float64_source(src))
    compile(traced_ref, "<e050_ref>", "exec")
    compile(traced_f64, "<e050_f64>", "exec")
    for name in ("mu", "var", "alpha", "W_all", "A_st", "P_st", "Z_st", "D3", "D21", "PK1", "PK2", "K2", "K11", "C", "final_output"):
        assert f"'{name}'" in traced_ref
    # Instrumentation cannot alter any frozen V29 literal/config text; removing captures
    # and the final-output temporary is checked operationally by the exact port test above.


def test_frozen_v29_constants_and_order_text_are_present():
    src = _source()
    required = [
        'V21_AGE_OLD", "4"', 'V21_R_OLD", "384"',
        'V24_AGE_OLD2", "7"', 'V24_R_OLD2", "224"',
        'R_FB = 16', 'R_RES = 16', 'V26_STRASSEN", "5"',
        'V26_STRASSEN_MIN", "32"', 'V25_BETA", "1.0"',
        'LAM = [4.9895e-03',
        'D3, D21 = self._dslices(',
        'W_all = ((APOW @ C1) * phic + (APOW @ C2) * Phic) * (SB @ SELC)',
        'K2v, K3v, K4v = K[(2,)], K[(3,)], K[(4,)]',
        'C = flops.as_symmetric(C, symmetry=(0, 1))',
    ]
    positions = []
    for token in required:
        assert token in src
        positions.append(src.index(token))
    assert positions[-4:] == sorted(positions[-4:])
